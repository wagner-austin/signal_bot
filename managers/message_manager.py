#!/usr/bin/env python
"""
managers/message_manager.py
---------------------------
Aggregated message manager facade.
Provides a unified interface for processing incoming messages by delegating to the message dispatcher.

CHANGES:
 - Now includes logic that checks if a user is in the "deletion" flow at the start of process_message()
   and automatically routes the user's raw message to the "delete" plugin if so.
"""

from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from parsers.message_parser import ParsedMessage

from core.state import BotStateMachine
from managers.message.message_dispatcher import dispatch_message
from managers.user_states_manager import get_flow_state  # <-- ADDED import to check user flow state

class MessageManager:
    """
    MessageManager - Aggregated facade for message processing.
    """
    def __init__(self, state_machine: Optional[BotStateMachine] = None) -> None:
        """
        Initializes the MessageManager.

        Parameters:
            state_machine (Optional[BotStateMachine]): The bot's state machine; if None, a new instance is created.
        """
        from core.state import BotStateMachine
        self.state_machine: BotStateMachine = state_machine if state_machine is not None else BotStateMachine()

    def process_message(self, parsed: "ParsedMessage", sender: str,
                        volunteer_manager: Any,
                        msg_timestamp: Optional[int] = None) -> str:
        """
        process_message - Processes an incoming message by dispatching it to the appropriate handler.
        
        1. Checks if the user is in "deletion" or "deletion_confirm" flow.
           If so, forcibly set parsed.command = "delete", parsed.args = parsed.body.
        2. Otherwise, dispatch normally based on parsed.command and parsed.args.
        
        Parameters:
            parsed (ParsedMessage): The parsed message object.
            sender (str): Sender's phone number.
            volunteer_manager (Any): Volunteer manager instance.
            msg_timestamp (Optional[int]): Optional message timestamp.
        
        Returns:
            str: The response message.
        """
        flow_state = get_flow_state(sender)
        if flow_state in {"deletion", "deletion_confirm"}:
            # If in deletion flow, override command so that a plain "yes"/"delete" message
            # is handled by the delete plugin automatically.
            parsed.command = "delete"
            parsed.args = parsed.body

        response = dispatch_message(parsed, sender, self.state_machine, volunteer_manager, msg_timestamp=msg_timestamp)
        return response

# End of managers/message_manager.py