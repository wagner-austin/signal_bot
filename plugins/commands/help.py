#!/usr/bin/env python
"""
plugins/commands/help.py - Help command plugin.
Provides a concise help listing for available commands based on help_visible flag.
Usage: "@bot help"
"""

from typing import Optional
from plugins.manager import plugin, get_all_plugins
from core.state import BotStateMachine
import logging

logger = logging.getLogger(__name__)

@plugin('help', canonical='help')
def help_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    help - Provides a concise list of available commands.
    Only commands with help_visible=True are displayed.
    Usage: "@bot help"
    """
    try:
        plugins_info = get_all_plugins()
        lines = []
        # Automatically include plugins marked as help_visible.
        for canonical, info in sorted(plugins_info.items()):
            if info.get("help_visible", True):
                func = info["function"]
                doc_line = (func.__doc__ or "No description").strip().splitlines()[0]
                lines.append(f"@bot {canonical} - {doc_line}")
        return "\n\n".join(lines)
    except Exception as e:
        logger.error(f"help_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in help_command."

# End of plugins/commands/help.py