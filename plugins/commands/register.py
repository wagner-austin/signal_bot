#!/usr/bin/env python
"""
plugins/commands/register.py
----------------------------
Summary: Start or continue the volunteer registration flow.
Usage:
  @bot register <optional name>
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.permissions import EVERYONE
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from core.api.volunteer_api import get_volunteer_record
from plugins.messages import (
    REGISTRATION_WELCOME,
    ALREADY_REGISTERED_WITH_INSTRUCTIONS,
    INTERNAL_ERROR
)

logger = logging.getLogger(__name__)

@plugin(["register"], canonical="register", required_role=EVERYONE)
class RegisterPlugin(BasePlugin):
    """
    Start or continue the registration flow.

    Usage:
      @bot register <optional name>
    """
    def __init__(self):
        super().__init__(
            "register",
            help_text="Start or continue registration flow.\n\nUsage:\n  @bot register [optional name]"
        )
        self.logger = logging.getLogger(__name__)

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        record = get_volunteer_record(sender)
        if record is not None:
            return ALREADY_REGISTERED_WITH_INSTRUCTIONS.format(name=record.get("name", "Unknown"))

        user_input = args.strip()
        active_flow = flow_state_api.get_active_flow(sender)
        if not active_flow:
            flow_state_api.start_flow(sender, "volunteer_registration")
            if not user_input:
                return REGISTRATION_WELCOME

        try:
            return flow_state_api.handle_flow_input(sender, user_input)
        except Exception as e:
            logger.error(f"Unexpected error in register command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/register.py