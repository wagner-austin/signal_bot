#!/usr/bin/env python
"""
plugins/commands/shutdown.py - Shutdown command plugin. Shuts down the bot.
Usage:
  @bot shutdown
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from plugins.messages import BOT_SHUTDOWN, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin(['shutdown', 'shut down'], canonical='shutdown')

class ShutdownPlugin(BasePlugin):
    """
    Shut down the bot.
    Usage:
      @bot shutdown
    """
    def __init__(self):
        super().__init__(
            "shutdown",
            help_text="Shut down the bot.\n\nUsage:\n  @bot shutdown"
        )
        self.logger = logging.getLogger(__name__)
        self.subcommands = {"default": self._default_subcmd}
        self.state_machine: Optional[BotStateMachine] = None

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        self.state_machine = state_machine
        usage = "Usage: @bot shutdown"
        try:
            return handle_subcommands(
                args,
                subcommands=self.subcommands,
                usage_msg=usage,
                unknown_subcmd_msg="Unknown subcommand. See usage: " + usage,
                default_subcommand="default"
            )
        except PluginArgError as e:
            self.logger.error(f"Argument parsing error in shutdown command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            self.logger.error(f"Unexpected error in shutdown command: {e}", exc_info=True)
            return INTERNAL_ERROR
    
    def _default_subcmd(self, rest: List[str]) -> str:
        if rest:
            return "Usage: @bot shutdown"
        if self.state_machine:
            self.state_machine.shutdown()
        return BOT_SHUTDOWN

# End of plugins/commands/shutdown.py