#!/usr/bin/env python
"""
plugins/commands/check_in.py - Check-in command plugin. Marks a volunteer as available.
Usage:
  @bot check in
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.exceptions import VolunteerError
from plugins.messages import FLOW_BUSY_MESSAGE, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin('check in', canonical='check in')
class CheckInPlugin(BasePlugin):
    """
    Mark volunteer as available.
    Usage:
      @bot check in
    """
    def __init__(self):
        super().__init__(
            "check in",
            help_text="Mark volunteer as available.\n\nUsage:\n  @bot check in"
        )
        self.logger = logging.getLogger(__name__)

    def run_command(self, args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
        usage = "Usage: @bot check in"
        subcommands = {"default": lambda rest: self._sub_default(rest, sender)}
        try:
            return handle_subcommands(
                args,
                subcommands=subcommands,
                usage_msg=usage,
                unknown_subcmd_msg="Unknown subcommand. See usage: " + usage,
                default_subcommand="default"
            )
        except PluginArgError as e:
            self.logger.error(f"Argument parsing error in check in command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            self.logger.error(f"Unexpected error in check in command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_default(self, rest: List[str], sender: str) -> str:
        active_flow = flow_state_api.get_active_flow(sender)
        if active_flow:
            return FLOW_BUSY_MESSAGE
        try:
            return VOLUNTEER_MANAGER.check_in(sender)
        except VolunteerError as e:
            logger.error(f"Check in command domain error: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in check in command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/check_in.py