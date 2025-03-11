#!/usr/bin/env python
"""
plugins/commands/help.py - Help command plugin - Provides a concise help listing for a select set of available commands.
"""

from typing import Optional
from plugins.manager import plugin, get_all_plugins
from core.state import BotStateMachine
import logging

logger = logging.getLogger(__name__)

# Whitelist of canonical commands to display in help.
ALLOWED_HELP_COMMANDS = {
    "info",
    "weekly update",
    "register",
    "event",
    "help",
}

@plugin('help', canonical='help')
def help_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    help - Provides a concise list of available commands.
    Usage: "@bot help"
    """
    try:
        plugins_info = get_all_plugins()
        lines = []
        for canonical, info in sorted(plugins_info.items()):
            if canonical not in ALLOWED_HELP_COMMANDS:
                continue
            func = info["function"]
            doc_line = func.__doc__.strip().splitlines()[0] if func.__doc__ else "No description"
            lines.append(f"@bot {canonical} - {doc_line}")
        return "\n\n".join(lines)
    except Exception as e:
        logger.error(f"help_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in help_command."

# End of plugins/commands/help.py