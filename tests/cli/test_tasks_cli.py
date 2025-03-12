#!/usr/bin/env python
"""
tests/cli/test_tasks_cli.py - Tests for task-related CLI commands.
Verifies that tasks can be listed via the CLI by using task_manager.add_task for creation
and then calling the CLI command which delegates to task_manager.list_all_tasks().
"""

from tests.cli.cli_test_helpers import run_cli_command
from managers.task_manager import add_task

def test_list_tasks():
    # Use the task manager API to add a task.
    created_by = "+4444444444"
    description = "Test Task"
    task_id = add_task(created_by, description)
    
    output = run_cli_command(["list-tasks"])["stdout"]
    assert "Test Task" in output
    # Since no volunteer record exists for +4444444444, created_by_name should be "Unknown".
    assert "Unknown" in output

# End of tests/cli/test_tasks_cli.py