"""
plugins/commands/logs.py - Logs command plugin.
Subcommands:
  default : List all command logs.
USAGE: Logs command does not require additional arguments.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.logs_manager import list_all_logs
from plugins.commands.formatters import format_log

logger = logging.getLogger(__name__)

@plugin('logs', canonical='logs')
def logs_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/logs.py - Logs command plugin.
    Subcommands:
      default : List all command logs.
    USAGE: Logs command does not require additional arguments.
    """
    if args.strip() and args.strip().lower() != "default":
        return "Unknown subcommand. USAGE: Logs command does not require additional arguments."
    try:
        logs = list_all_logs()
        if not logs:
            return "No command logs found."
        formatted = [format_log(log) for log in logs]
        return "\n".join(formatted)
    except Exception as e:
        logger.exception("Error in logs_command")
        return "An internal error occurred in logs_command."

# End of plugins/commands/logs.py