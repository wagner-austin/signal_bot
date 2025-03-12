#!/usr/bin/env python
"""
cli/logs_cli.py --- CLI tool for viewing command logs.
Retrieves log data via logs_manager and uses a formatter for presentation.
"""

from cli.formatters import format_log
from cli.common import print_results
from managers.logs_manager import list_logs

def list_logs_cli():
    """
    list_logs_cli - List all command logs.
    Retrieves log data via logs_manager and displays formatted output.
    """
    logs = list_logs()
    print_results(logs, format_log, "No command logs found.")

# End of cli/logs_cli.py