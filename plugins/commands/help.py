"""
plugins/commands/help.py - Help command plugins.
Provides a concise help listing for available commands without showing aliases.
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
        lines.append(f"@bot {canonical} - {doc_line}")
    return "\n\n".join(lines)

# End of plugins/commands/help.py