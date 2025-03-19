#!/usr/bin/env python
"""
plugins/commands/help.py
------------------------
Summary: Help command plugin. Lists available commands.
Usage:
  @bot help
"""

import logging
from typing import Optional
from plugins.manager import plugin, get_all_plugins, disabled_plugins
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from plugins.messages import HELP_UNKNOWN_SUBCOMMAND, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin(["help"], canonical="help")
class HelpPlugin(BasePlugin):
    """
    Help command plugin.
    Lists available commands.

    Usage:
      @bot help
    """
    def __init__(self):
        super().__init__(
            "help",
            help_text="List available commands.\n\nUsage:\n  @bot help"
        )
        self.logger = logging.getLogger(__name__)

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = "Usage: @bot help"
        user_input = args.strip()

        # If there's extraneous user input, show usage
        if user_input:
            return usage

        try:
            plugins_info = get_all_plugins()
            lines = []
            for canonical, info in sorted(plugins_info.items()):
                help_text = info.get("help_text", "No description")
                if canonical in disabled_plugins:
                    lines.append(f"@bot {canonical} (disabled) - {help_text}")
                else:
                    if info.get("help_visible", True):
                        lines.append(f"@bot {canonical} - {help_text}")
            return "\n\n".join(lines)
        except Exception as e:
            self.logger.error(f"Unexpected error in help command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/help.py