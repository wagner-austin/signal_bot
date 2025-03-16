#!/usr/bin/env python
"""
plugins/commands/info.py - Info command plugin. Displays bot information.
Usage:
  @bot info
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from plugins.messages import INFO_USAGE, INFO_TEXT, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin('info', canonical='info')
class InfoPlugin(BasePlugin):
    """
    Display bot information.
    Usage:
      @bot info
    """
    def __init__(self):
        super().__init__(
            "info",
            help_text="Display bot information.\n\nUsage:\n  @bot info"
        )
        self.logger = logging.getLogger(__name__)
        self.subcommands = {"default": self._sub_default}

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        try:
            return handle_subcommands(
                args,
                subcommands=self.subcommands,
                usage_msg=INFO_USAGE,
                unknown_subcmd_msg="Unknown subcommand. See usage: " + INFO_USAGE,
                default_subcommand="default"
            )
        except PluginArgError as e:
            self.logger.error(f"Argument parsing error in info command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            self.logger.error(f"Unexpected error in info command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_default(self, rest: List[str]) -> str:
        if rest:
            return INFO_USAGE
        return INFO_TEXT

# End of plugins/commands/info.py