#!/usr/bin/env python
"""
plugins/commands/task.py - Task command plugins.
Manages shared to-do items by calling managers.task_manager for add/list/assign/close,
ensuring a single source of truth shared with CLI code.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import (
    PluginArgError,
    TaskAddModel,
    TaskAssignModel,
    TaskCloseModel,
    validate_model
)
import logging

logger = logging.getLogger(__name__)

@plugin('task', canonical='task')
def task_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    task - Manage shared to-do tasks by calling managers.task_manager.
    Subcommands:
      add <description>
      list
      assign <task_id> <volunteer>
      close <task_id>
    
    This plugin is the same 'source of truth' used by the CLI, via managers.task_manager.
    """
    try:
        parsed_main = parse_plugin_arguments(args, mode='positional')
        tokens = parsed_main["tokens"]
        if not tokens:
            raise PluginArgError(
                "Usage:\n"
                "  @bot task add <description>\n"
                "  @bot task list\n"
                "  @bot task assign <task_id> <volunteer_display_name>\n"
                "  @bot task close <task_id>"
            )

        subcommand = tokens[0].lower()
        rest = tokens[1:] if len(tokens) > 1 else []

        # Local import to avoid circular references
        from managers.task_manager import create_task, list_all_tasks, assign_task, close_task

        if subcommand == "add":
            if not rest:
                raise PluginArgError("Usage: @bot task add <description>")
            validated = validate_model({"description": " ".join(rest)}, TaskAddModel, "task add <description>")
            task_id = create_task(sender, validated.description)
            return f"Task added with ID {task_id}."
        elif subcommand == "list":
            tasks = list_all_tasks()
            if not tasks:
                return "No tasks found."
            response_lines = ["Tasks:"]
            for task in tasks:
                response_lines.append(
                    f"ID {task['task_id']}: {task['description']} | Status: {task['status']} | "
                    f"Created by: {task['created_by_name']} | Assigned to: {task['assigned_to_name']}"
                )
            return "\n".join(response_lines)
        elif subcommand == "assign":
            if len(rest) < 2:
                raise PluginArgError("Usage: @bot task assign <task_id> <volunteer_display_name>")
            data = {"task_id": rest[0], "volunteer_display_name": " ".join(rest[1:])}
            validated = validate_model(data, TaskAssignModel, "task assign <task_id> <volunteer_display_name>")
            error = assign_task(validated.task_id, validated.volunteer_display_name)
            if error:
                return error
            return f"Task {validated.task_id} assigned to {validated.volunteer_display_name}."
        elif subcommand == "close":
            if not rest:
                raise PluginArgError("Usage: @bot task close <task_id>")
            data = {"task_id": rest[0]}
            validated = validate_model(data, TaskCloseModel, "task close <task_id>")
            close_task(validated.task_id)
            return f"Task {validated.task_id} has been closed."
        else:
            raise PluginArgError("Invalid subcommand for task. Use add, list, assign, or close.")
    except PluginArgError as e:
        logger.warning(f"task_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"task_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in task_command."

# End of plugins/commands/task.py