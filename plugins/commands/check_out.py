#!/usr/bin/env python
"""
plugins/commands/check_out.py
-----------------------------
Summary: Mark volunteer as unavailable (checked out).
Usage:
  @bot check out
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from core.api.volunteer_api import check_out
from core.exceptions import VolunteerError
from plugins.messages import FLOW_BUSY_MESSAGE, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin(["check out"], canonical="check out")
class CheckOutPlugin(BasePlugin):
    """
    Mark volunteer as unavailable (checked out).
    Usage:
      @bot check out
    """
    def __init__(self):
        super().__init__(
            "check out",
            help_text="Mark volunteer as unavailable (checked out).\n\nUsage:\n  @bot check out"
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
            return check_out(sender)
        except VolunteerError as e:
            logger.error(f"Check out command domain error: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in check out command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/check_out.py