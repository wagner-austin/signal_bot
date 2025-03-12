#!/usr/bin/env python
"""
tests/managers/test_logs_manager.py --- Tests for the logs manager.
Verifies that logs_manager.list_all_logs() returns a list of command log records.
"""

from managers.logs_manager import list_all_logs
from core.database.connection import get_connection

def test_logs_manager_list_logs():
    # Clear the CommandLogs table.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CommandLogs")
    conn.commit()
    conn.close()

    # Insert a log record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO CommandLogs (sender, command, args) VALUES (?, ?, ?)",
                   ("+1234567890", "test_command", "arg1 arg2"))
    conn.commit()
    conn.close()

    logs = list_all_logs()
    # Verify that logs is a list containing our test log.
    assert isinstance(logs, list)
    assert any("test_command" in log.get("command", "") for log in logs)

# End of tests/managers/test_logs_manager.py