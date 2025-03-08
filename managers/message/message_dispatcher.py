#!/usr/bin/env python
"""
managers/message/message_dispatcher.py - Dispatches incoming messages to appropriate handlers or plugins.
Contains the function to process a message and route it accordingly.
"""

import logging
import difflib
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from parsers.message_parser import ParsedMessage

from core.state import BotStateMachine
from plugins.manager import get_plugin, get_all_plugins

logger = logging.getLogger(__name__)

def dispatch_message(parsed: "ParsedMessage", sender: str, state_machine: BotStateMachine,
                     pending_actions: any, volunteer_manager: any,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    dispatch_message - Processes an incoming message by first handling pending actions
    (for private chats) and then dispatching commands via registered plugins.

    Parameters:
        parsed (ParsedMessage): The parsed incoming message.
        sender (str): Sender's phone number.
        state_machine (BotStateMachine): The current state machine instance.
        pending_actions (any): Global pending actions object.
        volunteer_manager (any): Volunteer manager instance.
        msg_timestamp (Optional[int]): Optional message timestamp.

    Returns:
        str: The response message.
    """
    if parsed.group_id is None:
        from managers.message.pending_handlers import EventCreationPendingHandler, DeletionPendingHandler, RegistrationPendingHandler
        event_response = EventCreationPendingHandler(pending_actions).process_event_creation_response(parsed, sender)
        if event_response is not None:
            return event_response
        deletion_response = DeletionPendingHandler(pending_actions, volunteer_manager).process_deletion_response(parsed, sender)
        if deletion_response is not None:
            return deletion_response
        registration_response = RegistrationPendingHandler(pending_actions, volunteer_manager).process_registration_response(parsed, sender)
        if registration_response is not None:
            return registration_response

    command: Optional[str] = parsed.command
    args: Optional[str] = parsed.args
    if command:
        plugin_func = get_plugin(command)
        if not plugin_func:
            available_commands = list(get_all_plugins().keys())
            matches = difflib.get_close_matches(command, available_commands, n=1, cutoff=0.75)
            if matches:
                plugin_func = get_plugin(matches[0])
                logger.info(f"Fuzzy matching: '{command}' interpreted as '{matches[0]}'")
            else:
                return ""
        try:
            response = plugin_func(args, sender, state_machine, msg_timestamp=msg_timestamp)
            return response
        except Exception as e:
            logger.exception(f"Error executing plugin for command '{command}' with args '{args}' from sender '{sender}': {e}")
            return "An internal error occurred while processing your command. Please try again later."
    return ""

# End of managers/message/message_dispatcher.py