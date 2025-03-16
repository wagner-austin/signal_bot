# File: plugins/commands/delete.py
"""
plugins/commands/delete.py
---------
Summary: 'delete' plugin command. Initiates or continues the volunteer deletion flow.
usage: @bot delete
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from plugins.messages import DELETION_PROMPT, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin(['delete', 'del', 'stop', 'unsubscribe', 'remove', 'opt out'], canonical='delete', help_visible=False)
class DeletePlugin(BasePlugin):
    """
    Start or continue the volunteer deletion flow.

    Usage:
      @bot delete
    """
    def __init__(self):
        super().__init__(
            "delete",
            help_text="Start or continue volunteer deletion flow.\n\nUsage:\n  @bot delete"
        )
        self.logger = logging.getLogger(__name__)

    def run_command(self, args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
        usage = "Usage: @bot delete"
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
                unknown_subcmd_msg="Unknown subcommand. See usage: " + usage
            )
        except PluginArgError as e:
            self.logger.error(f"Argument parsing error in delete command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in delete command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_default(self, rest: List[str], sender: str) -> str:
        user_input = " ".join(rest)
        active_flow = flow_state_api.get_active_flow(sender)
        if not active_flow:
            flow_state_api.start_flow(sender, "volunteer_deletion")
            if not user_input.strip():
                return DELETION_PROMPT
        return flow_state_api.handle_flow_input(sender, user_input)

# End of plugins/commands/delete.py