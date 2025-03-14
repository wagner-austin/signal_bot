"""
tests/core/test_database_logs.py - Tests for command logs database operations.
Verifies that log_command writes a log entry to the CommandLogs table.
"""

from db.logs import log_command
from db.connection import get_connection

def test_log_command():
    sender = "+1111111111"
    command = "test"
    args = "arg1 arg2"
    log_command(sender, command, args)
    # Verify that a log record was created.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sender, command, args FROM CommandLogs WHERE sender = ?", (sender,))
    row = cursor.fetchone()
    conn.close()
    assert row is not None
    assert row["sender"] == sender
    assert row["command"] == command
    assert row["args"] == args

# End of tests/core/test_database_logs.py