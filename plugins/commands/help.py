"""
plugins/commands/help.py - Help command plugins.
Provides concise and detailed help listings for available commands, showing only canonical names.
"""

from typing import Optional
from plugins.manager import plugin, get_all_plugins
from core.state import BotStateMachine

@plugin(commands=['help'], canonical='help')
def help_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    help - Provides a concise list of available commands.
    Usage: "@bot help"
    """
    plugins_info = get_all_plugins()
    lines = []
    for canonical, info in sorted(plugins_info.items()):
        if not info.get("help_visible", True):
            continue
        func = info["function"]
        # Use only the first line of the docstring as a summary.
        doc_line = func.__doc__.strip().splitlines()[0] if func.__doc__ else "No description"
        # Optionally list extra aliases if they differ from the canonical name.
        aliases = info["aliases"]
        extra_aliases = [alias for alias in aliases if alias != canonical]
        alias_str = f" (aliases: {', '.join(extra_aliases)})" if extra_aliases else ""
        lines.append(f"@bot {canonical}{alias_str} - {doc_line}")
    return "\n\n".join(lines)

@plugin(commands=['more help'], canonical='more help')
def more_help_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    more help - Provides detailed information for available commands.
    Usage: "@bot more help"
    """
    plugins_info = get_all_plugins()
    lines = []
    for canonical, info in sorted(plugins_info.items()):
        if not info.get("help_visible", True):
            continue
        func = info["function"]
        doc = func.__doc__.strip() if func.__doc__ else "No detailed help available."
        extra_aliases = [alias for alias in info["aliases"] if alias != canonical]
        alias_str = f" (aliases: {', '.join(extra_aliases)})" if extra_aliases else ""
        lines.append(f"@bot {canonical}{alias_str}\n{doc}")
    return "\n\n".join(lines)

# End of plugins/commands/help.py