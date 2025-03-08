#!/usr/bin/env python
"""
tests/cli/test_logs_cli.py - Tests for logs-related CLI commands.
Verifies that command logs can be listed via the CLI.
"""

from core.database.connection import get_connection
from tests.cli.cli_test_helpers import run_cli_command

def test_list_logs():
    # Insert a command log record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO CommandLogs (sender, command, args) VALUES (?, ?, ?)",
        ("+3333333333", "test", "arg1 arg2")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-logs"])
    assert "test" in output
    assert "+3333333333" in output

# End of tests/cli/test_logs_cli.py