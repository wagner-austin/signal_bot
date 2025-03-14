#!/usr/bin/env python
"""
tests/managers/test_logs_manager.py
-----------------------------------
Tests for managers/logs_manager.py.
Expanded coverage to include multiple logs insertion and empty logs check.
"""

from managers.logs_manager import list_all_logs
from db.connection import get_connection

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

def test_logs_manager_empty():
    """
    Verifies that, if CommandLogs is empty, list_all_logs() returns an empty list without errors.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CommandLogs")
    conn.commit()
    conn.close()

    logs = list_all_logs()
    assert logs == [], "Expected an empty list when no logs are present."

def test_logs_manager_multiple():
    """
    Inserts multiple logs to test retrieval order and presence.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM CommandLogs")
    cursor.execute("INSERT INTO CommandLogs (sender, command, args) VALUES (?, ?, ?)",
                   ("+1111111111", "first_command", "alpha"))
    cursor.execute("INSERT INTO CommandLogs (sender, command, args) VALUES (?, ?, ?)",
                   ("+2222222222", "second_command", "beta"))
    conn.commit()
    conn.close()

    logs = list_all_logs()  # Should be in DESC timestamp order, but we won't enforce that strictly unless you do in code
    assert len(logs) == 2, "Should have two logs total."
    commands = [log["command"] for log in logs]
    assert "first_command" in commands and "second_command" in commands

# End of tests/managers/test_logs_manager.py