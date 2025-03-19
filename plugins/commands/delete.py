#!/usr/bin/env python
"""
plugins/commands/delete.py
--------------------------
Summary: 'delete' plugin command. Initiates or continues volunteer deletion flow.
Usage:
  @bot delete
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

@plugin(["delete", "del", "stop", "unsubscribe", "remove", "opt out"], canonical="delete", help_visible=True, required_role=REGISTERED)
class DeletePlugin(BasePlugin):
    """
    Start or continue the volunteer deletion flow.

    Usage:
      @bot delete
    """
    def __init__(self):
        super().__init__(
            "delete",
            help_text="Delete your registration."
        )
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
            flow_state_api.start_flow(sender, "volunteer_deletion")
        try:
            return flow_state_api.handle_flow_input(sender, user_input)
        except Exception as e:
            logger.error(f"Unexpected error in delete command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/delete.py