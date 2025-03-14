"""
plugins/commands/task.py - Task management commands.
Manages shared to-do tasks using a unified subcommand dispatcher.
"""

from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
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
def task_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/task.py - Manage shared to-do tasks.
    Subcommands:
      add <description>      : Add a new task.
      list                   : List all tasks.
      assign <task_id> <name>  : Assign a task.
      close <task_id>        : Close a task.
    USAGE:
      Add: {USAGE_TASK_ADD}
      List: {USAGE_TASK_LIST}
      Assign: {USAGE_TASK_ASSIGN}
      Close: {USAGE_TASK_CLOSE}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["list"]  # default to "list"
    allowed = {"add", "list", "assign", "close"}
    if tokens[0].lower() not in allowed:
        return (f"Unknown subcommand. USAGE:\n{USAGE_TASK_ADD}\n{USAGE_TASK_LIST}\n"
                f"{USAGE_TASK_ASSIGN}\n{USAGE_TASK_CLOSE}")
    subcmd = tokens[0].lower()
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        if subcmd == "add":
            if not new_args.strip():
                raise PluginArgError(USAGE_TASK_ADD)
            validated = validate_model({"description": new_args.strip()}, TaskAddModel, USAGE_TASK_ADD)
            task_id = create_task(sender, validated.description)
            return f"Task added with ID {task_id}."
        elif subcmd == "list":
            tasks = list_all_tasks()
            if not tasks:
                return "No tasks found."
            return "\n".join(format_task(t) for t in tasks)
        elif subcmd == "assign":
            parts = new_args.split()
            if len(parts) < 2:
                raise PluginArgError(USAGE_TASK_ASSIGN)
            data = {"task_id": parts[0], "volunteer_display_name": " ".join(parts[1:])}
            validated = validate_model(data, TaskAssignModel, USAGE_TASK_ASSIGN)
            assign_task(validated.task_id, validated.volunteer_display_name)
            return f"Task {validated.task_id} assigned to {validated.volunteer_display_name}."
        elif subcmd == "close":
            parts = new_args.split()
            if not parts:
                raise PluginArgError(USAGE_TASK_CLOSE)
            data = {"task_id": parts[0]}
            validated = validate_model(data, TaskCloseModel, USAGE_TASK_CLOSE)
            close_task(validated.task_id)
            return f"Task {validated.task_id} has been closed."
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