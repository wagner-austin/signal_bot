"""
plugins/commands/deleted_volunteers.py
--------------------------------------
Summary: List deleted volunteer records.
Usage:
  @bot deleted volunteers
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.permissions import OWNER  
from core.state import BotStateMachine
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from core.api.volunteer_api import list_deleted_volunteers
from plugins.commands.formatters import format_deleted_volunteer
from plugins.messages import FLOW_BUSY_MESSAGE, NO_DELETED_VOLUNTEERS_FOUND, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin("deleted volunteers", canonical="deleted volunteers", required_role=OWNER)
class DeletedVolunteersPlugin(BasePlugin):
    """
    List deleted volunteer records.

    Usage:
      @bot deleted volunteers
    """
    def __init__(self):
        super().__init__(
            "deleted volunteers",
            help_text="List deleted volunteer records."
        )
        self.logger = logging.getLogger(__name__)

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = "Usage: @bot deleted volunteers"
        user_input = args.strip()

        # If there's extraneous user input, optionally show usage
        if user_input:
            return usage

        active_flow = flow_state_api.get_active_flow(sender)
        if active_flow:
            return FLOW_BUSY_MESSAGE

        try:
            recs = list_deleted_volunteers()
            if not recs:
                return NO_DELETED_VOLUNTEERS_FOUND
            return "\n".join(format_deleted_volunteer(r) for r in recs)
        except Exception as e:
            logger.error(f"Error in deleted volunteers command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/deleted_volunteers.py