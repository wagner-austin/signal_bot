#!/usr/bin/env python
"""
plugins/commands/check_in.py
----------------------------
Summary: Mark volunteer as available.
Usage:
  @bot check in
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.permissions import REGISTERED
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from core.api.volunteer_api import check_in
from core.exceptions import VolunteerError
from plugins.messages import FLOW_BUSY_MESSAGE, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin(["check in"], canonical="check in", required_role=REGISTERED)
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

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        _ = args.strip()  # Not used, but standard practice to parse user input

        active_flow = flow_state_api.get_active_flow(sender)
        if active_flow:
            return FLOW_BUSY_MESSAGE

        try:
            return check_in(sender)
        except VolunteerError as e:
            logger.error(f"Check in command domain error: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in check in command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/check_in.py