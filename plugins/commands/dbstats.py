#!/usr/bin/env python
"""
plugins/commands/dbstats.py - Database statistics command plugin.
Provides a command to display current database statistics including table row counts and the schema version.
Usage: "@bot dbstats"
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.stats import get_database_stats

@plugin('dbstats', canonical='dbstats')
def dbstats_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    dbstats - Display current database statistics.

    Usage: "@bot dbstats"

    Returns:
        A formatted string showing the current schema version and row counts for each table.
    """
    stats = get_database_stats()
    response_lines = []
    response_lines.append("Database Statistics:")
    response_lines.append(f"Schema Version: {stats.get('schema_version')}")
    response_lines.append("Table Row Counts:")
    for table, count in stats["tables"].items():
        response_lines.append(f" - {table}: {count}")
    return "\n".join(response_lines)

# End of plugins/commands/dbstats.py