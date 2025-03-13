#!/usr/bin/env python
"""
plugins/commands/dbbackup.py - Database backup command plugin.
Provides subcommands to create, list, and restore database backups.
Usage:
  "@bot dbbackup create"
  "@bot dbbackup list"
  "@bot dbbackup restore <filename>"
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.backup import create_backup, list_backups, restore_backup
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError
import logging
from core.plugin_usage import USAGE_DBBACKUP

logger = logging.getLogger(__name__)

@plugin('dbbackup', canonical='dbbackup')
def dbbackup_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    dbbackup - Manage database backups.
    Subcommands:
      create               : Create a new backup snapshot.
      list                 : List all backup snapshots.
      restore <filename>   : Restore the database from a specified backup file.
    """
    try:
        parsed = parse_plugin_arguments(args, mode='positional')
        tokens = parsed["tokens"]
        if not tokens:
            raise PluginArgError(USAGE_DBBACKUP)

        subcommand = tokens[0].lower()

        if subcommand == "create":
            backup_path = create_backup()
            return f"Backup created: {backup_path}"
        elif subcommand == "list":
            backups = list_backups()
            if not backups:
                return "No backups found."
            response = "Available Backups:\n" + "\n".join(backups)
            return response
        elif subcommand == "restore":
            if len(tokens) < 2:
                raise PluginArgError(USAGE_DBBACKUP)
            filename = tokens[1]
            success = restore_backup(filename)
            if success:
                return f"Database restored from backup: {filename}"
            else:
                return f"Backup file '{filename}' not found."
        else:
            raise PluginArgError(USAGE_DBBACKUP)
    except PluginArgError as e:
        logger.warning(f"dbbackup_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"dbbackup_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in dbbackup_command."

# End of plugins/commands/dbbackup.py