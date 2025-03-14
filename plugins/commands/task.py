#!/usr/bin/env python
"""
plugins/commands/task.py - Task command plugins.
Manages shared to-do items with the universal format_task function.
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
from core.exceptions import ResourceError, VolunteerError
from managers.task_manager import create_task, list_all_tasks, assign_task, close_task
from core.plugin_usage import USAGE_TASK_ADD, USAGE_TASK_LIST, USAGE_TASK_ASSIGN, USAGE_TASK_CLOSE
from plugins.commands.formatters import format_task

logger = logging.getLogger(__name__)

@plugin('task', canonical='task')
def task_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    task - Manage shared to-do tasks.
    
    Subcommands:
      add <description>       : Add a new task.
      list                    : List all tasks.
      assign <task_id> <name> : Assign a task.
      close <task_id>         : Close a task.
    
    USAGE:
      Add: {USAGE_TASK_ADD}
      List: {USAGE_TASK_LIST}
      Assign: {USAGE_TASK_ASSIGN}
      Close: {USAGE_TASK_CLOSE}
    """
    try:
        parsed_main = parse_plugin_arguments(args, mode='positional')
        tokens = parsed_main["tokens"]
        if not tokens:
            raise PluginArgError(f"{USAGE_TASK_ADD}\n{USAGE_TASK_LIST}\n{USAGE_TASK_ASSIGN}\n{USAGE_TASK_CLOSE}")

        subcommand = tokens[0].lower()
        rest = tokens[1:] if len(tokens) > 1 else []

        if subcommand == "add":
            if not rest:
                raise PluginArgError(USAGE_TASK_ADD)
            validated = validate_model({"description": " ".join(rest)}, TaskAddModel, USAGE_TASK_ADD)
            task_id = create_task(sender, validated.description)
            return f"Task added with ID {task_id}."

        elif subcommand == "list":
            tasks = list_all_tasks()
            if not tasks:
                return "No tasks found."
            return "\n".join(format_task(t) for t in tasks)

        elif subcommand == "assign":
            if len(rest) < 2:
                raise PluginArgError(USAGE_TASK_ASSIGN)
            data = {"task_id": rest[0], "volunteer_display_name": " ".join(rest[1:])}
            validated = validate_model(data, TaskAssignModel, USAGE_TASK_ASSIGN)
            assign_task(validated.task_id, validated.volunteer_display_name)
            return f"Task {validated.task_id} assigned to {validated.volunteer_display_name}."

        elif subcommand == "close":
            if not rest:
                raise PluginArgError(USAGE_TASK_CLOSE)
            data = {"task_id": rest[0]}
            validated = validate_model(data, TaskCloseModel, USAGE_TASK_CLOSE)
            close_task(validated.task_id)
            return f"Task {validated.task_id} has been closed."

        else:
            raise PluginArgError(f"{USAGE_TASK_ADD}\n{USAGE_TASK_LIST}\n{USAGE_TASK_ASSIGN}\n{USAGE_TASK_CLOSE}")

    except PluginArgError as e:
        logger.warning(f"task_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"task_command domain error: {e}", exc_info=True)
        error_msg = str(e)
        if ":" in error_msg:
            error_msg = error_msg.split(":", 1)[1].strip()
        return f"An error occurred: {error_msg}"
    except Exception as e:
        logger.error(f"task_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in task_command."

# End of plugins/commands/task.py