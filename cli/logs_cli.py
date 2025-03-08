#!/usr/bin/env python
"""
cli/logs_cli.py - CLI tool for viewing command logs.
Provides a function to list all command logs from the database.
"""

from core.database.helpers import execute_sql

def list_logs_cli():
    """
    list_logs_cli - List all command logs.
    Displays log ID, sender, command, arguments, and timestamp.
    """
    query = "SELECT * FROM CommandLogs ORDER BY timestamp DESC"
    rows = execute_sql(query, fetchall=True)
    if not rows:
        print("No command logs found.")
        return
    for row in rows:
        print(f"ID: {row['id']}")
        print(f"Sender: {row['sender']}")
        print(f"Command: {row['command']}")
        print(f"Args: {row['args']}")
        print(f"Timestamp: {row['timestamp']}")
        print("-" * 40)

# End of cli/logs_cli.py