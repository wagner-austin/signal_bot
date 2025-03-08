#!/usr/bin/env python
"""
tests/cli/test_tasks_cli.py - Tests for task-related CLI commands.
Verifies that tasks can be listed via the CLI.
"""

from core.database.connection import get_connection
from tests.cli.cli_test_helpers import run_cli_command

def test_list_tasks():
    # Insert a task record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Tasks (description, created_by, status) VALUES (?, ?, ?)",
        ("Test Task", "+4444444444", "open")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-tasks"])
    assert "Test Task" in output
    # Since no volunteer exists for +4444444444, created_by_name should be "Unknown".
    assert "Unknown" in output

# End of tests/cli/test_tasks_cli.py