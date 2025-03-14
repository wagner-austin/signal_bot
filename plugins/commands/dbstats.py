#!/usr/bin/env python
"""
plugins/commands/dbstats.py - Database statistics command plugin.
Provides a command to display current database statistics.
Usage: "@bot dbstats" (See USAGE_DBSTATS in core/plugin_usage.py)
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from db.stats import get_database_stats
from db.backup import list_backups
from datetime import datetime
from core.plugin_usage import USAGE_DBSTATS

@plugin('dbstats', canonical='dbstats')
def dbstats_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    dbstats - Display current database statistics.
    
    USAGE: {USAGE_DBSTATS}
    
    Returns:
        A formatted string showing the current schema version, table row counts,
        and the timestamp of the most recent backup.
    """
    stats = get_database_stats()
    response_lines = []
    response_lines.append("Database Statistics:")
    response_lines.append(f"Schema Version: {stats.get('schema_version')}")
    response_lines.append("Table Row Counts:")
    for table, count in stats["tables"].items():
        response_lines.append(f" - {table}: {count}")
    
    backups = list_backups()
    if backups:
        last_backup = backups[-1]
        try:
            timestamp_str = last_backup[len("backup_"):-len(".db")]
            dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            formatted_timestamp = last_backup
    else:
        formatted_timestamp = "None"
    
    response_lines.append("")
    response_lines.append(f"Last Backup: {formatted_timestamp}")
    return "\n".join(response_lines)

# End of plugins/commands/dbstats.py