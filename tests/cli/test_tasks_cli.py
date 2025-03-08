#!/usr/bin/env python
"""
tests/cli/test_tasks_cli.py - Tests for task-related CLI commands.
Verifies that tasks can be listed via the CLI.
"""

from tests.cli.cli_test_helpers import run_cli_command
from tests.test_helpers import insert_record

def test_list_tasks():
    # Insert a task record manually using helper.
    insert_record(
        "INSERT INTO Tasks (description, created_by, status) VALUES (?, ?, ?)",
        ("Test Task", "+4444444444", "open")
    )

    output = run_cli_command(["list-tasks"])
    assert "Test Task" in output
    # Since no volunteer exists for +4444444444, created_by_name should be "Unknown".
    assert "Unknown" in output

# End of tests/cli/test_tasks_cli.py