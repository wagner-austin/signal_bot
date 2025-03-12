#!/usr/bin/env python
"""
managers/logs_manager.py --- Logs Manager for retrieving command logs.
Provides a unified interface for retrieving log data from the CommandLogs table.
"""

from core.database.repository import CommandLogRepository

def list_logs() -> list:
    """
    list_logs - Retrieve all command log records.
    
    Returns:
        list: A list of command log records ordered by timestamp descending.
    """
    repo = CommandLogRepository()
    return repo.list_all(order_by="timestamp DESC")
    
# End of managers/logs_manager.py