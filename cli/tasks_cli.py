#!/usr/bin/env python
"""
cli/tasks_cli.py - CLI tool for task-related operations.
Provides a function to list all tasks from the Tasks table.
"""

from core.task_manager import list_tasks

def list_tasks_cli():
    """
    list_tasks_cli - List all tasks.
    Displays task ID, description, status, creation time, and volunteer names (normalized).
    """
    tasks = list_tasks()
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print(f"Task ID: {task['task_id']}")
        print(f"Description: {task['description']}")
        print(f"Status: {task['status']}")
        print(f"Created At: {task['created_at']}")
        print(f"Created By: {task['created_by_name']}")
        print(f"Assigned To: {task['assigned_to_name']}")
        print("-" * 40)

# End of cli/tasks_cli.py