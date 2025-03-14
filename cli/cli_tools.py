#!/usr/bin/env python
"""
cli/cli_tools.py - Aggregated CLI Tools Facade, now unified with plugin commands.

CHANGES:
 - Added a new "task" subparser with sub-subcommands (add, assign, close).
 - That aligns with the test calls: ["task", "add", "..."], ["task", "assign", "..."], etc.
 - No other changes beyond what's needed for the task tests.
"""

import argparse
import logging
import sys
from core.logger_setup import setup_logging
from core.exceptions import VolunteerError, ResourceError
from core.state import BotStateMachine

logger = logging.getLogger(__name__)

# A simple BotStateMachine instance for CLI usage
CLI_STATE_MACHINE = BotStateMachine()

def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified CLI Tools for plugin-based commands.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Volunteers
    sp_list_vols = subparsers.add_parser("list-volunteers", help="List all volunteers")
    
    sp_add_vol = subparsers.add_parser("add-volunteer", help="Add/register a volunteer")
    sp_add_vol.add_argument("--phone", required=True, help="Volunteer phone number (E.164 format)")
    sp_add_vol.add_argument("--name", required=True, help="Volunteer name")
    sp_add_vol.add_argument("--skills", default="", help="Comma-separated list of skills")
    sp_add_vol.add_argument("--available", default="1", help="Availability: '1' for available, '0' for not available")
    sp_add_vol.add_argument("--role", default="", help="Set volunteer's current role if desired")

    subparsers.add_parser("list-deleted-volunteers", help="List deleted volunteers")

    # Events
    subparsers.add_parser("list-events", help="List all events")
    subparsers.add_parser("list-event-speakers", help="List all event speakers")

    # Logs
    subparsers.add_parser("list-logs", help="List all command logs")

    # Resources
    subparsers.add_parser("list-resources", help="List all resources")
    sp_add_res = subparsers.add_parser("add-resource", help="Add a resource")
    sp_add_res.add_argument("--category", required=True, help="Resource category")
    sp_add_res.add_argument("--url", required=True, help="URL of the resource")
    sp_add_res.add_argument("--title", default="", help="Optional resource title")

    sp_remove_res = subparsers.add_parser("remove-resource", help="Remove a resource by ID")
    sp_remove_res.add_argument("--id", type=int, required=True, help="Resource ID")

    # Tasks
    subparsers.add_parser("list-tasks", help="List all tasks")

    # NEW: a "task" command that has sub-subcommands add/assign/close
    sp_task = subparsers.add_parser("task", help="Task subcommands: add, assign, close")
    sp_task_sub = sp_task.add_subparsers(dest="task_subcommand", help="Task subcommand")

    # sub-subcommand: add
    sp_task_add = sp_task_sub.add_parser("add", help="Add a new task")
    sp_task_add.add_argument("description", nargs="+", help="Task description")

    # sub-subcommand: assign
    sp_task_assign = sp_task_sub.add_parser("assign", help="Assign an existing task to a volunteer by name")
    sp_task_assign.add_argument("task_id", help="Task ID (integer)")
    sp_task_assign.add_argument("volunteer_name", nargs="+", help="Volunteer name")

    # sub-subcommand: close
    sp_task_close = sp_task_sub.add_parser("close", help="Close an existing task by ID")
    sp_task_close.add_argument("task_id", help="Task ID (integer)")

    return parser

def _dispatch_subcommand(args: argparse.Namespace, parser: argparse.ArgumentParser):
    from plugins.commands.volunteer import (
        volunteer_status_command,
        register_command,
        check_in_command,
        add_skills_command,
    )
    from plugins.commands.role import role_command
    from plugins.commands.volunteer import deleted_volunteers_command
    from plugins.commands.event import event_command, event_speakers_command
    from plugins.commands.logs import logs_command
    from plugins.commands.resource import resource_command
    from plugins.commands.task import task_command

    command = args.command
    if not command:
        parser.print_help()
        return

    # Volunteers
    if command == "list-volunteers":
        result = volunteer_status_command("", "cli", CLI_STATE_MACHINE)
        print(result)

    elif command == "add-volunteer":
        phone = args.phone
        name = args.name
        skills = [s.strip() for s in args.skills.split(",")] if args.skills else []
        available = args.available  # "0" or "1"
        role = args.role.strip()

        # 1) Register volunteer
        reg_result = register_command(name, phone, CLI_STATE_MACHINE)
        print(reg_result)

        # 2) If any skills were provided, add them
        if skills:
            skill_args = ",".join(skills)
            skill_result = add_skills_command(skill_args, phone, CLI_STATE_MACHINE)
            print(skill_result)

        # 3) Validate availability
        if available != "1" and available != "0":
            print("Error: available must be 0 or 1.")
            return
        if available == "1":
            ci_result = check_in_command("", phone, CLI_STATE_MACHINE)
            print(ci_result)

        # 4) If role is given, set it
        if role:
            role_args = f"set {role}"
            role_result = role_command(role_args, phone, CLI_STATE_MACHINE)
            print(role_result)

    elif command == "list-deleted-volunteers":
        result = deleted_volunteers_command("", "cli", CLI_STATE_MACHINE)
        print(result)

    # Events
    elif command == "list-events":
        result = event_command("", "cli", CLI_STATE_MACHINE)
        print(result)

    elif command == "list-event-speakers":
        result = event_speakers_command("", "cli", CLI_STATE_MACHINE)
        print(result)

    # Logs
    elif command == "list-logs":
        result = logs_command("", "cli", CLI_STATE_MACHINE)
        print(result)

    # Resources
    elif command == "list-resources":
        result = resource_command("list", "cli", CLI_STATE_MACHINE)
        print(result)

    elif command == "add-resource":
        category = args.category
        url = args.url
        title = args.title
        combined_args = f"add {category} {url} {title}".strip()
        result = resource_command(combined_args, "cli", CLI_STATE_MACHINE)
        print(result)

    elif command == "remove-resource":
        resource_id = args.id
        combined_args = f"remove {resource_id}"
        result = resource_command(combined_args, "cli", CLI_STATE_MACHINE)
        print(result)

    # Tasks
    elif command == "list-tasks":
        result = task_command("list", "cli", CLI_STATE_MACHINE)
        print(result)

    elif command == "task":
        # sub-subcommand
        if not args.task_subcommand:
            # no sub-subcommand => print usage
            parser.print_help()
            return

        if args.task_subcommand == "add":
            description_str = " ".join(args.description)
            # e.g., "task add some desc" => pass "add some desc"
            cmd_args = f"add {description_str}"
            result = task_command(cmd_args, "cli", CLI_STATE_MACHINE)
            print(result)

        elif args.task_subcommand == "assign":
            # e.g., task assign <task_id> <volunteer name...>
            volunteer_name_str = " ".join(args.volunteer_name)
            cmd_args = f"assign {args.task_id} {volunteer_name_str}"
            result = task_command(cmd_args, "cli", CLI_STATE_MACHINE)
            print(result)

        elif args.task_subcommand == "close":
            cmd_args = f"close {args.task_id}"
            result = task_command(cmd_args, "cli", CLI_STATE_MACHINE)
            print(result)
        else:
            parser.print_help()

    else:
        parser.print_help()

def main():
    setup_logging()
    parser = create_arg_parser()
    args = parser.parse_args()
    try:
        _dispatch_subcommand(args, parser)
    except (VolunteerError, ResourceError) as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

# End of cli/cli_tools.py