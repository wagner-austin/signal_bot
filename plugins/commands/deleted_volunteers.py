#!/usr/bin/env python
"""
plugins/commands/deleted_volunteers.py - Deleted volunteers command plugin. Lists records of deleted volunteers.
Usage:
  @bot deleted volunteers
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from managers.volunteer_manager import VOLUNTEER_MANAGER
from plugins.commands.formatters import format_deleted_volunteer
from plugins.messages import FLOW_BUSY_MESSAGE, NO_DELETED_VOLUNTEERS_FOUND, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin('deleted volunteers', canonical='deleted volunteers')
class DeletedVolunteersPlugin(BasePlugin):
    """
    List deleted volunteer records.
    Usage:
      @bot deleted volunteers
    """
    def __init__(self):
        super().__init__(
            "deleted volunteers",
            help_text="List deleted volunteer records.\n\nUsage:\n  @bot deleted volunteers"
        )
        self.logger = logging.getLogger(__name__)

    def run_command(self, args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
        usage = "Usage: @bot deleted volunteers"
        tokens = args.strip().split(None, 1)
        subcmd = tokens[0].lower() if tokens else "default"
        if subcmd != "default":
            return "Unknown subcommand. See usage: " + usage
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
            self.logger.error(f"Argument parsing error in deleted volunteers command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in deleted volunteers command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_default(self, rest: List[str], sender: str) -> str:
        active_flow = flow_state_api.get_active_flow(sender)
        if active_flow:
            return FLOW_BUSY_MESSAGE
        try:
            recs = VOLUNTEER_MANAGER.list_deleted_volunteers()
            if not recs:
                return NO_DELETED_VOLUNTEERS_FOUND
            return "\n".join(format_deleted_volunteer(r) for r in recs)
        except Exception as e:
            logger.error(f"Error in deleted volunteers command: {e}", exc_info=True)
            return INTERNAL_ERROR

# End of plugins/commands/deleted_volunteers.py