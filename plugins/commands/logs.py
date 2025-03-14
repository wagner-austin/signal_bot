#!/usr/bin/env python
"""
plugins/commands/logs.py - Logs command plugin.
Displays logs using the universal format_log function.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.logs_manager import list_all_logs
from plugins.commands.formatters import format_log

logger = logging.getLogger(__name__)

@plugin('logs', canonical='logs')
def logs_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    logs - Lists all command logs.
    """
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