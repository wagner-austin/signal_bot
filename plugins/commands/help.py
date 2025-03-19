#!/usr/bin/env python
"""
plugins/commands/help.py - Help command plugin.
Lists available commands using centralized help metadata.
Usage:
  @bot help
"""

import logging
from typing import Optional, List
from plugins.manager import plugin, get_all_plugins, disabled_plugins
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from plugins.messages import HELP_UNKNOWN_SUBCOMMAND, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin('help', canonical='help')
class HelpPlugin(BasePlugin):
    """
    Help command plugin.
    Lists available commands.
    Usage:
      @bot help
    """
    def __init__(self):
        super().__init__("help", help_text="List available commands.\n\nUsage:\n  @bot help")
        self.logger = logging.getLogger(__name__)
        self.subcommands = {
            "default": self._default_subcmd
        }

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        if args.strip() and args.strip().lower() != "default":
            return HELP_UNKNOWN_SUBCOMMAND
        try:
            return handle_subcommands(
                args,
                subcommands=self.subcommands,
                usage_msg="Usage: @bot help",
                default_subcommand="default"
            )
        except PluginArgError as e:
            self.logger.error(f"Argument parsing error in help command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            self.logger.error(f"Unexpected error in help command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _default_subcmd(self, rest: List[str]) -> str:
        try:
            plugins_info = get_all_plugins()
            lines = []
            for canonical, info in sorted(plugins_info.items()):
                # Retrieve help text from centralized registry field "help_text"
                help_text = info.get("help_text", "No description")
                if canonical in disabled_plugins:
                    lines.append(f"@bot {canonical} (disabled) - {help_text}")
                else:
                    if info.get("help_visible", True):
                        lines.append(f"@bot {canonical} - {help_text}")
            return "\n\n".join(lines)
        except Exception as e:
            logger.error(f"Unexpected error in help command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/help.py