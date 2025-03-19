#!/usr/bin/env python
"""
plugins/commands/info.py
------------------------
Summary: Info command plugin. Displays bot information.
Usage:
  @bot info
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from plugins.messages import INFO_USAGE, INFO_TEXT, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin(["info"], canonical="info")
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

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = INFO_USAGE
        user_input = args.strip()

        # If there's extraneous user input, show usage
        if user_input:
            return usage

        try:
            return INFO_TEXT
        except Exception as e:
            self.logger.error(f"Unexpected error in info command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/info.py