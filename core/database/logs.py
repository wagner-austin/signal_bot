#!/usr/bin/env python
"""
core/database/logs.py - Command logs database operations using repository pattern.
Provides functions to log command executions.
"""

from core.database.repository import CommandLogRepository

def log_command(sender: str, command: str, args: str) -> None:
    repo = CommandLogRepository()
    data = {
        "sender": sender,
        "command": command,
        "args": args
    }
    repo.create(data)

# End of core/database/logs.py