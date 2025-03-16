# File: plugins/commands/edit.py
"""
plugins/commands/edit.py
-------
Summary: 'edit' plugin command. Allows a volunteer to change their name interactively.
usage: @bot edit <new name or skip>
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from plugins.messages import EDIT_PROMPT, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin(
    ['edit', 'change my name please', 'change my name to', 'change my name',
     'can you change my name please', 'can you change my name to', 'can you change my name',
     'can i change my name to', 'can i change my name', 'not my name', "that's not my name",
     'wrong name', 'i mispelled'],
    canonical='edit',
    help_visible=False
)
class EditPlugin(BasePlugin):
    """
    Start or continue the edit flow.

    Usage:
      @bot edit <new name or skip>
    """
    def __init__(self):
        super().__init__(
            "edit",
            help_text="Start or continue edit flow.\n\nUsage:\n  @bot edit <new name or skip>"
        )
        self.logger = logging.getLogger(__name__)

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        usage = "Usage: @bot edit <new name or skip>"
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
            self.logger.error(f"Argument parsing error in edit command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in edit command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_default(self, rest: List[str], sender: str) -> str:
        user_input = " ".join(rest)
        active_flow = flow_state_api.get_active_flow(sender)
        if not active_flow:
            flow_state_api.start_flow(sender, "volunteer_edit")
            if not user_input.strip():
                return EDIT_PROMPT
        return flow_state_api.handle_flow_input(sender, user_input)

# End of plugins/commands/edit.py