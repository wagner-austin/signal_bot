#!/usr/bin/env python
"""
tests/cli/test_logs_cli.py - Tests for logs-related CLI commands.
Verifies that command logs can be listed via the CLI.
"""

from tests.cli.cli_test_helpers import run_cli_command
from tests.test_helpers import insert_record

def test_list_logs():
    # Insert a command log record manually using helper.
    insert_record(
        "INSERT INTO CommandLogs (sender, command, args) VALUES (?, ?, ?)",
        ("+3333333333", "test", "arg1 arg2")
    )

    output = run_cli_command(["list-logs"])
    assert "test" in output
    assert "+3333333333" in output

# End of tests/cli/test_logs_cli.py