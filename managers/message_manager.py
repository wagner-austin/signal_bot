#!/usr/bin/env python
"""
managers/message_manager.py - Aggregated message manager facade.
Provides a unified interface for processing incoming messages by delegating to the message dispatcher.
"""

from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from parsers.message_parser import ParsedMessage

from core.state import BotStateMachine
from managers.message.message_dispatcher import dispatch_message

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
                        pending_actions: Any, volunteer_manager: Any,
                        msg_timestamp: Optional[int] = None) -> str:
        """
        Processes an incoming message.
        After parsing, if the sender is not recognized (no volunteer record), a welcome message is prepended.

        Parameters:
            parsed (ParsedMessage): The parsed message.
            sender (str): Sender's phone number.
            pending_actions (Any): Global pending actions object.
            volunteer_manager (Any): Volunteer manager instance.
            msg_timestamp (Optional[int]): Optional message timestamp.

        Returns:
            str: The response message.
        """
        from core.database import get_volunteer_record
        from core.messages import GETTING_STARTED
        response = dispatch_message(parsed, sender, self.state_machine, pending_actions, volunteer_manager, msg_timestamp)
        if not get_volunteer_record(sender) and response:
            response = GETTING_STARTED + "\n" + response
        return response

# End of managers/message_manager.py