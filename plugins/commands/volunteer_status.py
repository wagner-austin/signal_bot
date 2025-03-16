#!/usr/bin/env python
"""
plugins/commands/volunteer_status.py - Volunteer status command plugin. Displays volunteer status without showing phone numbers.
Usage:
  @bot volunteer status
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from managers.volunteer_manager import VOLUNTEER_MANAGER
from plugins.messages import FLOW_BUSY_MESSAGE, NO_VOLUNTEERS_FOUND, VOLUNTEER_STATUS_TEMPLATE, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin('volunteer status', canonical='volunteer status')
class VolunteerStatusPlugin(BasePlugin):
    """
    Show volunteer status for all volunteers without displaying phone numbers.
    Usage:
      @bot volunteer status
    """
    def __init__(self):
        super().__init__(
            "volunteer status",
            help_text="Show volunteer status (name & availability) for all volunteers without showing phone numbers.\n\nUsage:\n  @bot volunteer status"
        )
        self.logger = logging.getLogger(__name__)
    
    def run_command(self, args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
        usage = "Usage: @bot volunteer status"
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
            self.logger.error(f"Argument parsing error in volunteer status command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in volunteer status command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_default(self, rest: List[str], sender: str) -> str:
        active_flow = flow_state_api.get_active_flow(sender)
        if active_flow:
            return FLOW_BUSY_MESSAGE
        try:
            all_vols = VOLUNTEER_MANAGER.list_all_volunteers_list()
            if not all_vols:
                return NO_VOLUNTEERS_FOUND
            # Format each volunteer's info without exposing phone numbers.
            formatted = []
            for v in all_vols:
                name = v.get("name", "Unknown")
                available = "Available" if v.get("available") else "Not Available"
                formatted.append(VOLUNTEER_STATUS_TEMPLATE.format(name=name, available=available))
            return "\n".join(formatted)
        except Exception as e:
            logger.error(f"Unexpected error in volunteer status command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/volunteer_status.py