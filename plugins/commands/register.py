# File: plugins/commands/register.py
"""
plugins/commands/register.py
-----------
Summary: 'register' plugin command. Starts or continues the volunteer registration flow.
usage: @bot register <optional name>
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.state import BotStateMachine
from plugins.commands.subcommand_dispatcher import handle_subcommands, PluginArgError
from plugins.abstract import BasePlugin
from core.api import flow_state_api
from plugins.messages import REGISTRATION_WELCOME, INTERNAL_ERROR

logger = logging.getLogger(__name__)

@plugin('register', canonical='register')
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

    def run_command(self, args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
        usage = "Usage: @bot register <optional name>"
        subcommands = {"default": lambda rest: self._sub_default(rest, sender)}
        from plugins.commands.subcommand_dispatcher import handle_subcommands
        try:
            return handle_subcommands(
                args,
                subcommands=subcommands,
                usage_msg=usage,
                unknown_subcmd_msg="Unknown subcommand. See usage: " + usage,
                default_subcommand="default"
            )
        except PluginArgError as e:
            self.logger.error(f"Argument parsing error in register command: {e}", exc_info=True)
            return str(e)
        except Exception as e:
            logger.error(f"Unexpected error in register command: {e}", exc_info=True)
            return INTERNAL_ERROR
    
    def _sub_default(self, rest: List[str], sender: str) -> str:
        user_input = " ".join(rest)
        active_flow = flow_state_api.get_active_flow(sender)
        if not active_flow:
            flow_state_api.start_flow(sender, "volunteer_registration")
            if not user_input.strip():
                return REGISTRATION_WELCOME
        return flow_state_api.handle_flow_input(sender, user_input)

# End of plugins/commands/register.py