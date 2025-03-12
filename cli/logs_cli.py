#!/usr/bin/env python
"""
cli/logs_cli.py --- CLI tool for viewing command logs.
Now calls list_all_logs from the manager.
Streamlined to a one-liner "list" command.
"""

from cli.formatters import format_log
from cli.common import print_results
from managers.logs_manager import list_all_logs

def list_logs_cli():
    """
    list_logs_cli - List all command logs (one-liner).
    """
    print_results(list_all_logs(), format_log, "No command logs found.")

# End of cli/logs_cli.py