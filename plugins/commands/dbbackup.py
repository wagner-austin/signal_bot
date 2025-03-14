"""
plugins/commands/dbbackup.py - Database backup command plugin.
Subcommands:
  create               : Create a new backup snapshot.
  list                 : List all backup snapshots.
  restore <filename>   : Restore the database from a specified backup file.
USAGE: {USAGE_DBBACKUP}

CHANGES:
 - Now uses the new 'handle_subcommands' function to avoid repeated token parsing.
"""

from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from db.backup import create_backup, list_backups, restore_backup
from parsers.plugin_arg_parser import PluginArgError
import logging
from core.plugin_usage import USAGE_DBBACKUP
from plugins.commands.subcommand_dispatcher import handle_subcommands

logger = logging.getLogger(__name__)

@plugin('dbbackup', canonical='dbbackup')
def dbbackup_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/dbbackup.py - Database backup command plugin.
    Subcommands:
      create               : Create a new backup snapshot.
      list                 : List all backup snapshots.
      restore <filename>   : Restore the database from a specified backup file.
    USAGE: {USAGE_DBBACKUP}
    """
    try:
        def sub_create(rest: List[str]) -> str:
            backup_path = create_backup()
            return f"Backup created: {backup_path}"

        def sub_list(rest: List[str]) -> str:
            backups = list_backups()
            if not backups:
                return "No backups found."
            return "Available Backups:\n" + "\n".join(backups)

        def sub_restore(rest: List[str]) -> str:
            if not rest:
                raise PluginArgError(USAGE_DBBACKUP)
            filename = rest[0]
            success = restore_backup(filename)
            if success:
                return f"Database restored from backup: {filename}"
            else:
                return f"Backup file '{filename}' not found."

        subcommands = {
            "create": sub_create,
            "list": sub_list,
            "restore": sub_restore
        }

        return handle_subcommands(
            args,
            subcommands,
            usage_msg=USAGE_DBBACKUP,
            unknown_subcmd_msg="Unknown subcommand"
        )

    except PluginArgError as e:
        logger.warning(f"dbbackup_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"dbbackup_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in dbbackup_command."

# End of plugins/commands/dbbackup.py