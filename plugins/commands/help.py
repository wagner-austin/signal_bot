"""
plugins/commands/help.py - Help command plugins for the Signal bot.
Provides commands to display available commands and detailed help.
"""

from typing import Optional
import difflib
from plugins.manager import plugin, get_all_plugins
from core.state import BotStateMachine

@plugin('help')
def help_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    help - Provides a concise list of available commands.
    Usage: "@bot help"
    """
    commands = get_all_plugins()
    excluded_commands = {"assign", "test", "shutdown", "test all"}
    lines = []
    for cmd, func in sorted(commands.items()):
        if cmd in excluded_commands:
            continue
        doc_line = func.__doc__.strip().splitlines()[0] if func.__doc__ else "No description"
        lines.append(f"@bot {cmd} - {doc_line}")
    return "\n\n".join(lines)

@plugin('more help')
def more_help_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    more help - Provides detailed information for available commands.
    Usage: "@bot more help"
    """
    commands = get_all_plugins()
    excluded_commands = {"assign", "test", "shutdown", "test all"}
    lines = []
    for cmd, func in sorted(commands.items()):
        if cmd in excluded_commands:
            continue
        doc = func.__doc__.strip() if func.__doc__ else "No detailed help available."
        lines.append(f"@bot {cmd}\n{doc}")
    return "\n\n".join(lines)

# End of plugins/commands/help.py