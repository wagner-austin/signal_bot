#!/usr/bin/env python
"""
managers/logs_manager.py --- Logs Manager for retrieving command logs.
Renamed list_logs -> list_all_logs for naming consistency.
"""

from core.database.repository import CommandLogRepository

def list_all_logs() -> list:
    """
    list_all_logs - Retrieve all command log records.
    """
    repo = CommandLogRepository()
    return repo.list_all(order_by="timestamp DESC")

# End of managers/logs_manager.py