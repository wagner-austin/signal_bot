#!/usr/bin/env python
"""
plugins/commands/volunteer_status.py
------------------------------------
Summary: Show volunteer status for all volunteers without displaying phone numbers.
Usage:
  @bot volunteer status
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from core.api.volunteer_api import list_all_volunteers_list
from plugins.messages import FLOW_BUSY_MESSAGE, NO_VOLUNTEERS_FOUND, VOLUNTEER_STATUS_TEMPLATE, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin("volunteer status", canonical="volunteer status")
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

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = "Usage: @bot volunteer status"
        user_input = args.strip()

        # If there's extraneous user input, optionally show usage
        if user_input:
            return usage

        active_flow = flow_state_api.get_active_flow(sender)
        if active_flow:
            return FLOW_BUSY_MESSAGE

        try:
            all_vols = list_all_volunteers_list()
            if not all_vols:
                return NO_VOLUNTEERS_FOUND

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