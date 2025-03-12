#!/usr/bin/env python
"""
cli/tasks_cli.py --- CLI tool for task-related operations.
Retrieves task data using business logic and uses a dedicated formatter to present tasks.
Delegates task retrieval to the task manager.
"""

from managers.task_manager import list_all_tasks
from cli.formatters import format_task
from cli.common import print_results

def list_tasks_cli():
    """
    list_tasks_cli - List all tasks.
    Uses task_manager.list_all_tasks to retrieve tasks and a formatter for consistent display.
    """
    tasks = list_all_tasks()
    print_results(tasks, format_task, "No tasks found.")

# End of cli/tasks_cli.py