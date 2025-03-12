#!/usr/bin/env python
"""
tasks_cli.py - CLI tool for task-related operations.
Delegates listing to managers.task_manager with a simple one-liner function.
"""

from managers.task_manager import list_all_tasks
from cli.formatters import format_task
from cli.common import print_results

def list_tasks_cli():
    """
    list_tasks_cli - List all tasks by calling managers.task_manager.list_all_tasks().
    """
    print_results(list_all_tasks(), format_task, "No tasks found.")

# End of cli/tasks_cli.py