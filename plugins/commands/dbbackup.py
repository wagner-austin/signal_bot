#!/usr/bin/env python
"""
plugins/commands/dbbackup.py - Database backup command plugin.
Provides subcommands to create, list, and restore database backups.
Usage:
  "@bot dbbackup create"      - Creates a new backup snapshot.
  "@bot dbbackup list"        - Lists all backup files.
  "@bot dbbackup restore <filename>" - Restores the database from the specified backup.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.backup import create_backup, list_backups, restore_backup

@plugin('dbbackup', canonical='dbbackup')
def dbbackup_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    dbbackup - Manage database backups.
    
    Subcommands:
      create               : Create a new backup snapshot.
      list                 : List all backup snapshots.
      restore <filename>   : Restore the database from a specified backup file.
    
    Usage Examples:
      "@bot dbbackup create"
      "@bot dbbackup list"
      "@bot dbbackup restore backup_20250307_153000.db"
    """
    args = args.strip().split()
    if not args:
        return ("Usage:\n  dbbackup create\n  dbbackup list\n  dbbackup restore <filename>")
    
    subcommand = args[0].lower()
    
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
        if len(args) < 2:
            return "Usage: dbbackup restore <filename>"
        filename = args[1]
        success = restore_backup(filename)
        if success:
            return f"Database restored from backup: {filename}"
        else:
            return f"Backup file '{filename}' not found."
    else:
        return ("Invalid subcommand.\nUsage:\n  dbbackup create\n  dbbackup list\n  dbbackup restore <filename>")

# End of plugins/commands/dbbackup.py