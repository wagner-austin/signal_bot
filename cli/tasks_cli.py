#!/usr/bin/env python
"""
cli/tasks_cli.py - CLI tool for task-related operations.
Retrieves task data using business logic and uses a dedicated formatter to present tasks.
"""

from core.task_manager import list_tasks
from cli.formatters import format_task
from cli.common import print_results

def list_tasks_cli():
    """
    list_tasks_cli - List all tasks.
    Uses a formatter to display tasks consistently.
    """
    tasks = list_tasks()
    print_results(tasks, format_task, "No tasks found.")

# End of cli/tasks_cli.py