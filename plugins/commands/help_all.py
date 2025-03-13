#!/usr/bin/env python
"""
plugins/commands/help_all.py - Help all command plugin.
Lists *all* available commands grouped by category.
Usage: "@bot help all"
"""

from typing import Optional
from plugins.manager import plugin, get_all_plugins
from core.state import BotStateMachine
import logging

logger = logging.getLogger(__name__)

@plugin('help all', canonical='help all')
def help_all_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    help all - Lists *all* available commands with grouping by category.
    Usage: "@bot help all"
    """
    plugins_info = get_all_plugins()  # Returns dict {canonical: info}
    groups = {}
    # Group plugins by their category (set in the plugin decorator)
    for canonical, info in plugins_info.items():
        category = info.get("category", "Miscellaneous Commands")
        func = info.get("function")
        doc_line = (func.__doc__ or "No description").strip().splitlines()[0]
        groups.setdefault(category, []).append((canonical, doc_line))
    output_lines = []
    # Sort categories alphabetically and then sort commands within each group
    for category in sorted(groups.keys()):
        output_lines.append(f"{category}:")
        for cmd, desc in sorted(groups[category], key=lambda x: x[0]):
            output_lines.append(f"  @bot {cmd} - {desc}")
        output_lines.append("")  # Blank line between groups
    return "\n".join(output_lines).strip()

# End of plugins/commands/help_all.py