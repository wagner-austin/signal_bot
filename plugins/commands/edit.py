#!/usr/bin/env python
"""
plugins/commands/edit.py
------------------------
Summary: 'edit' plugin command. Allows a volunteer to change their name interactively.
Usage:
  @bot edit <new name or skip>
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.permissions import REGISTERED
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from plugins.messages import INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin(["edit"], canonical="edit", help_visible=True, required_role=REGISTERED)
class EditPlugin(BasePlugin):
    """
    Start or continue the edit flow.

    Usage:
      @bot edit <new name or skip>
    """
    def __init__(self):
        super().__init__(
            "edit",
            help_text="Change your registration name.")
        self.logger = logging.getLogger(__name__)

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        user_input = args.strip()
        active_flow = flow_state_api.get_active_flow(sender)
        if not active_flow:
            flow_state_api.start_flow(sender, "volunteer_edit")
        try:
            return flow_state_api.handle_flow_input(sender, user_input)
        except Exception as e:
            self.logger.error(f"Unexpected error in edit command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/edit.py