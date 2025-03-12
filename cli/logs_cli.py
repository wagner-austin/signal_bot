#!/usr/bin/env python
"""
logs_cli.py - CLI tool for viewing command logs.
Provides a one-liner 'list' command that delegates to logs_manager.
"""

from cli.formatters import format_log
from cli.common import print_results
from managers.logs_manager import list_all_logs

def list_logs_cli():
    """
    list_logs_cli - List all command logs by calling managers.logs_manager.list_all_logs().
    """
    print_results(list_all_logs(), format_log, "No command logs found.")

# End of cli/logs_cli.py