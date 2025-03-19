#!/usr/bin/env python
"""
plugins/commands/template.py - Template plugin for new command development.
Demonstrates usage of concurrency, DB API, and multi-step flows.
Usage:
  @bot template start
  @bot template pause
  @bot template resume
"""

import logging
from typing import Optional, List
from plugins.manager import plugin
from core.permissions import ADMIN
from plugins.abstract import BasePlugin
from core.state import BotStateMachine

from core.api.concurrency_api import per_phone_lock_api, atomic_transaction_api
from core.api.db_api import fetch_one, execute_query
from core.api.flow_state_api import start_flow, pause_flow, resume_flow, get_active_flow
from plugins.messages import INTERNAL_ERROR, TEMPLATE_FLOW_STARTED, TEMPLATE_FLOW_PAUSED, TEMPLATE_FLOW_RESUMED, TEMPLATE_NO_FLOW_TO_RESUME

logger = logging.getLogger(__name__)

@plugin(commands=["template"], canonical="template", required_role=ADMIN)
class TemplatePlugin(BasePlugin):
    """
    Template plugin for new command development.
    Demonstrates concurrency, DB usage, and multi-step flows.
    Usage:
      @bot template <start|pause|resume>
    """
    def __init__(self):
        super().__init__(
            "template",
            help_text="A sample plugin demonstrating concurrency, DB usage, and multi-step flows."
        )
        self.logger = logging.getLogger(__name__)
        self.subcommands = {
            "start": self._sub_start,
            "pause": self._sub_pause,
            "resume": self._sub_resume,
        }

    def run_command(
        self,
        args: str,
        sender: str,
        state_machine: BotStateMachine,
        msg_timestamp: Optional[int] = None
    ) -> str:
        from plugins.commands.subcommand_dispatcher import handle_subcommands
        usage = "Usage: @bot template <start|pause|resume>"
        try:
            return handle_subcommands(
                args,
                self.subcommands,
                usage_msg=usage,
                unknown_subcmd_msg="Unknown subcommand. See usage: " + usage,
                default_subcommand="default"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error in template command: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_start(self, rest: List[str]) -> str:
        """
        Start a new multi-step flow.
        Demonstrates a simple DB insert and concurrency lock usage.
        """
        try:
            with per_phone_lock_api(self._sender):
                with atomic_transaction_api(exclusive=False) as conn:
                    execute_query(
                        "INSERT OR IGNORE INTO UserStates (phone, flow_state) VALUES (?, '{}')",
                        (self._sender,),
                        commit=True
                    )
            start_flow(self._sender, "template_flow")
            return TEMPLATE_FLOW_STARTED
        except Exception as e:
            self.logger.error(f"Error in template start subcommand: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_pause(self, rest: List[str]) -> str:
        """
        Pause the 'template_flow'.
        """
        try:
            pause_flow(self._sender, "template_flow")
            return TEMPLATE_FLOW_PAUSED
        except Exception as e:
            self.logger.error(f"Error in template pause subcommand: {e}", exc_info=True)
            return INTERNAL_ERROR

    def _sub_resume(self, rest: List[str]) -> str:
        """
        Resume the 'template_flow'.
        """
        try:
            resume_flow(self._sender, "template_flow")
            active = get_active_flow(self._sender)
            if active == "template_flow":
                return TEMPLATE_FLOW_RESUMED
            return TEMPLATE_NO_FLOW_TO_RESUME
        except Exception as e:
            self.logger.error(f"Error in template resume subcommand: {e}", exc_info=True)
            return INTERNAL_ERROR

    @property
    def _sender(self) -> str:
        import inspect
        for frame_info in inspect.stack():
            if frame_info.function == "run_command":
                return frame_info.frame.f_locals.get("sender", "Unknown")
        return "Unknown"

# End of plugins/commands/template.py