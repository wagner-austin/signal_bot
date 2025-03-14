#!/usr/bin/env python
"""
managers/message_manager.py
---------------------------
Aggregated message manager facade.
Provides a unified interface for processing incoming messages by delegating to the message dispatcher.

CHANGES:
 - If no recognized command is found, auto-dispatch to the user's active_flow (if any).
 - Minimal changes otherwise, preserving existing logic and docstrings.
"""

from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from parsers.message_parser import ParsedMessage

from core.state import BotStateMachine
from managers.message.message_dispatcher import dispatch_message
from managers.user_states_manager import get_active_flow, list_flows  # new usage
from plugins.manager import get_plugin, get_all_plugins

class MessageManager:
    """
    MessageManager - Aggregated facade for message processing.
    """
    def __init__(self, state_machine: Optional[BotStateMachine] = None) -> None:
        from core.state import BotStateMachine
        self.state_machine: BotStateMachine = state_machine if state_machine is not None else BotStateMachine()

    def process_message(self, parsed: "ParsedMessage", sender: str,
                        volunteer_manager: Any,
                        msg_timestamp: Optional[int] = None) -> str:
        """
        process_message - Processes an incoming message by dispatching it to the appropriate handler.

        1. If parsed.command is recognized, we dispatch to that plugin as usual.
        2. If no recognized command is found, we check if there's an active_flow for this user.
           If so, hand the raw text to that flow for handling.
        3. Otherwise, do default or no-op.

        Returns:
            str: The response message.
        """
        # Attempt normal plugin dispatch
        command = parsed.command
        if command:
            # Check if there's a plugin for that command
            plugin_func = get_plugin(command)
            if plugin_func:
                return dispatch_message(parsed, sender, self.state_machine, volunteer_manager, msg_timestamp=msg_timestamp)
            # If command is not found, we fall through to check active flow
            # but let's do a blank response or something
            # We'll keep consistent with the existing approach
            # so let's do an empty return after checking flows
        # If we reach here, no recognized plugin or no command at all
        active_flow = get_active_flow(sender)
        if active_flow:
            # Let the user’s active flow handle the text
            # We can invoke a centralized flow handler function
            # We'll do that inline for now:
            return self._handle_active_flow(sender, active_flow, parsed.body)
        else:
            # No active flow and no recognized command
            return ""

    def _handle_active_flow(self, phone: str, flow_name: str, raw_text: str) -> str:
        """
        _handle_active_flow - Minimal stub that routes the user's input
        to the appropriate flow logic. In a real system you'd have
        flow-specific handlers or a registry of flows.

        For demonstration, we simply show "Flow <flow_name> step logic not implemented."
        """
        # Here you would do something like:
        #   if flow_name == "registration": handle_registration_step(phone, raw_text)
        #   elif flow_name == "delete_flow": handle_delete_step(phone, raw_text)
        #   else: ...
        # We'll just return a placeholder:
        return f"Flow '{flow_name}' is active. You said: {raw_text}. (Flow logic not implemented here.)"

# End of managers/message_manager.py