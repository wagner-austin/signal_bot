#!/usr/bin/env python
"""
plugins/commands/task.py - Task command plugins - Manages shared to-do tasks with consistent argument validation and error logging.
This module now uses local imports for task manager functions to avoid circular import issues.
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
    task - Manage shared to-do tasks.
    
    Subcommands:
      add <description>                   : Add a new task.
      list                                : List all tasks.
      assign <task_id> <volunteer>        : Assign a task to a volunteer by display name.
      close <task_id>                     : Close a task.
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

        if subcommand == "add":
            if not rest:
                raise PluginArgError("Usage: @bot task add <description>")
            validated = validate_model({"description": " ".join(rest)}, TaskAddModel, "task add <description>")
            # Local import to break circular dependency.
            from managers.task_manager import create_task
            task_id = create_task(sender, validated.description)
            return f"Task added with ID {task_id}."
        elif subcommand == "list":
            from managers.task_manager import _fetch_tasks
            tasks = _fetch_tasks()
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
            try:
                validated = validate_model(
                    {"task_id": rest[0], "volunteer_display_name": " ".join(rest[1:])},
                    TaskAssignModel,
                    "task assign <task_id> <volunteer_display_name>"
                )
            except PluginArgError as e:
                logger.warning(f"task_command PluginArgError in assign subcommand: {e}")
                return "invalid task_id"
            from managers.task_manager import assign_task
            error = assign_task(validated.task_id, validated.volunteer_display_name)
            if error:
                return error
            return f"Task {validated.task_id} assigned to {validated.volunteer_display_name}."
        elif subcommand == "close":
            if not rest:
                raise PluginArgError("Usage: @bot task close <task_id>")
            try:
                validated = validate_model({"task_id": rest[0]}, TaskCloseModel, "task close <task_id>")
            except PluginArgError as e:
                logger.warning(f"task_command PluginArgError in close subcommand: {e}")
                return "invalid task_id"
            from managers.task_manager import close_task
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