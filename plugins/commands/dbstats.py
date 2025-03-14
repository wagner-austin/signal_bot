"""
plugins/commands/dbstats.py - Database statistics command plugin.
Subcommands:
  default : Display current database statistics.
USAGE: {USAGE_DBSTATS}
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from db.stats import get_database_stats
from db.backup import list_backups
from datetime import datetime
from core.plugin_usage import USAGE_DBSTATS

logger = logging.getLogger(__name__)

@plugin('dbstats', canonical='dbstats')
def dbstats_command(args: str, sender: str, state_machine: BotStateMachine,
                    msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/dbstats.py - Database statistics command plugin.
    Subcommands:
      default : Display current database statistics.
    USAGE: {USAGE_DBSTATS}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_DBSTATS}"
    new_args = tokens[1] if len(tokens) > 1 else ""
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