#!/usr/bin/env python
"""
cli/logs_cli.py - CLI tool for viewing command logs.
Retrieves log data from the business logic and uses a formatter for presentation.
"""

from core.database.helpers import execute_sql
from cli.formatters import format_log
from cli.common import print_results

def list_logs_cli():
    """
    list_logs_cli - List all command logs.
    Uses a formatter to display log entries in a consistent format.
    """
    query = "SELECT * FROM CommandLogs ORDER BY timestamp DESC"
    rows = execute_sql(query, fetchall=True)
    print_results(rows, format_log, "No command logs found.")

# End of cli/logs_cli.py