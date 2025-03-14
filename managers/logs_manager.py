#!/usr/bin/env python
"""
logs_manager.py
---------------
Command logs manager for retrieving logs from the DB as dictionaries.
"""

from db.repository import CommandLogRepository

def list_all_logs() -> list:
    """
    list_all_logs - Retrieve all command log records as a list of dicts.
    """
    repo = CommandLogRepository()
    rows = repo.list_all(order_by="timestamp DESC")
    logs = []
    for row in rows:
        logs.append({
            "id": row["id"],
            "sender": row["sender"],
            "command": row["command"],
            "args": row["args"],
            "timestamp": row["timestamp"]
        })
    return logs

# End of managers/logs_manager.py