#!/usr/bin/env python
"""
cli/tasks_cli.py --- CLI tool for task-related operations.
Delegates logic to task_manager, which now has create_task, list_all_tasks, etc.
Streamlined to a one-liner "list" command.
"""

from managers.task_manager import list_all_tasks
from cli.formatters import format_task
from cli.common import print_results

def list_tasks_cli():
    """
    list_tasks_cli - List all tasks (one-liner).
    """
    print_results(list_all_tasks(), format_task, "No tasks found.")

# End of cli/tasks_cli.py