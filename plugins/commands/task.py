#!/usr/bin/env python
"""
plugins/commands/task.py - Task command plugins.
Provides commands to add, list, assign, and close tasks.
Usage:
  "@bot task add <description>"
  "@bot task list"
  "@bot task assign <task_id> <volunteer_display_name>"
  "@bot task close <task_id>"
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.task_manager import add_task, list_tasks, assign_task, close_task
from parsers.argument_parser import parse_plugin_arguments

@plugin('task', canonical='task')
def task_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    task - Manage shared to-do tasks.
    
    Subcommands:
      add <description>                : Add a new task.
      list                             : List all tasks.
      assign <task_id> <volunteer>       : Assign a task to a volunteer by display name.
      close <task_id>                  : Close a task.
    
    Usage examples:
      "@bot task add Need 5 new signs"
      "@bot task list"
      "@bot task assign 3 John Doe"
      "@bot task close 3"
    """
    parsed = parse_plugin_arguments(args, mode='positional')
    tokens = parsed["tokens"]
    if not tokens:
        return ("Usage:\n"
                "  @bot task add <description>\n"
                "  @bot task list\n"
                "  @bot task assign <task_id> <volunteer_display_name>\n"
                "  @bot task close <task_id>")
    
    subcommand = tokens[0].lower()
    rest = " ".join(tokens[1:]) if len(tokens) > 1 else ""
    
    if subcommand == "add":
        if not rest:
            return "Usage: @bot task add <description>"
        task_id = add_task(sender, rest)
        return f"Task added with ID {task_id}."
    
    elif subcommand == "list":
        tasks = list_tasks()
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
        parsed_assign = parse_plugin_arguments(rest, mode='positional', maxsplit=1)
        assign_parts = parsed_assign["tokens"]
        if len(assign_parts) < 2:
            return "Usage: @bot task assign <task_id> <volunteer_display_name>"
        try:
            task_id = int(assign_parts[0])
        except ValueError:
            return "Invalid task_id. It should be a number."
        volunteer_name = assign_parts[1].strip()
        error = assign_task(task_id, volunteer_name)
        if error:
            return error
        return f"Task {task_id} assigned to {volunteer_name}."
    
    elif subcommand == "close":
        if not rest:
            return "Usage: @bot task close <task_id>"
        try:
            task_id = int(rest.strip())
        except ValueError:
            return "Invalid task_id. It should be a number."
        close_task(task_id)
        return f"Task {task_id} has been closed."
    
    else:
        return "Invalid subcommand for task. Use add, list, assign, or close."

# End of plugins/commands/task.py