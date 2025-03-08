#!/usr/bin/env python
"""
cli/logs_cli.py - CLI tool for viewing command logs.
Retrieves log data from the business logic and uses a formatter for presentation.
"""

from core.database.helpers import execute_sql
from cli.formatters import format_log

def list_logs_cli():
    """
    list_logs_cli - List all command logs.
    Uses a formatter to display log entries in a consistent format.
    """
    query = "SELECT * FROM CommandLogs ORDER BY timestamp DESC"
    rows = execute_sql(query, fetchall=True)
    if not rows:
        print("No command logs found.")
        return
    for row in rows:
        output = format_log(row)
        print(output)

# End of cli/logs_cli.py