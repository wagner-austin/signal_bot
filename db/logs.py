#!/usr/bin/env python
"""
db/logs.py - Command logs database operations using repository pattern.
Provides functions to log command executions.
"""

from db.repository import CommandLogRepository

def log_command(sender: str, command: str, args: str) -> None:
    repo = CommandLogRepository()
    data = {
        "sender": sender,
        "command": command,
        "args": args
    }
    repo.create(data)

# End of db/logs.py