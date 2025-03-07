"""
managers/message_handler.py - Handles incoming messages and dispatches commands.
Refactored into separate handlers for registration/edit and deletion flows.
"""

import logging
import difflib
from typing import Optional
from plugins.manager import get_plugin, get_all_plugins
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage
from core.messages import (
    DELETION_CONFIRM_PROMPT, ALREADY_REGISTERED, DELETION_CANCELED,
    EDIT_CANCELED, EDIT_CANCELED_WITH_NAME
)
from core.constants import SKIP_VALUES  # Consolidated constant

logger = logging.getLogger(__name__)

def _get_confirmation_message(sender: str, registered_format: str, default_message: str) -> str:
    """
    _get_confirmation_message - Helper function to fetch the volunteer record and generate a confirmation message.
    
    Args:
        sender (str): The sender's phone number.
        registered_format (str): A format string expecting a 'name' parameter.
        default_message (str): A default message if no volunteer record is found.
        
    Returns:
        str: The formatted confirmation message.
    """
    from core.database import get_volunteer_record
    record = get_volunteer_record(sender)
    if record:
        return registered_format.format(name=record['name'])
    else:
        return default_message

class DeletionPendingHandler:
    """
    DeletionPendingHandler - Handles pending deletion responses.
    
    Separates deletion flow from registration logic for clarity and easier testing.
    """
    def __init__(self, pending_actions, volunteer_manager) -> None:
        self.pending_actions = pending_actions
        self.volunteer_manager = volunteer_manager

    def process_deletion_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        """
        process_deletion_response - Processes a deletion response using the pending deletion state.
        
        Args:
            parsed (ParsedMessage): The parsed message.
            sender (str): The sender's identifier.
        Returns:
            Optional[str]: The deletion confirmation or cancellation message if processed.
        """
        if not self.pending_actions.has_deletion(sender):
            return None
        state = self.pending_actions.get_deletion(sender)
        user_input = parsed.body.strip().lower() if parsed.body else ""
        if state == "initial":
            if user_input in {"yes", "y", "yea", "sure"}:
                self.pending_actions.set_deletion(sender, "confirm")
                return DELETION_CONFIRM_PROMPT
            else:
                confirmation = _get_confirmation_message(sender, ALREADY_REGISTERED, DELETION_CANCELED)
                self.pending_actions.clear_deletion(sender)
                return confirmation
        elif state == "confirm":
            if parsed.body.strip() == "DELETE":
                confirmation = self.volunteer_manager.delete_volunteer(sender)
                self.pending_actions.clear_deletion(sender)
                return confirmation
            else:
                confirmation = _get_confirmation_message(sender, ALREADY_REGISTERED, DELETION_CANCELED)
                self.pending_actions.clear_deletion(sender)
                return confirmation
        return None

class RegistrationPendingHandler:
    """
    RegistrationPendingHandler - Handles pending registration/edit responses.
    
    Splits out registration and edit flow from deletion, making logic more modular.
    """
    def __init__(self, pending_actions, volunteer_manager) -> None:
        self.pending_actions = pending_actions
        self.volunteer_manager = volunteer_manager

    def process_registration_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        """
        process_registration_response - Processes a registration or edit response using the pending registration state.
        
        Args:
            parsed (ParsedMessage): The parsed message.
            sender (str): The sender's identifier.
        Returns:
            Optional[str]: The confirmation message if processed.
        """
        if not self.pending_actions.has_registration(sender):
            return None
        mode = self.pending_actions.get_registration(sender)
        name_input = parsed.body.strip() if parsed.body else ""
        if mode == "edit" and name_input.lower() in SKIP_VALUES:
            confirmation = _get_confirmation_message(sender, EDIT_CANCELED_WITH_NAME, EDIT_CANCELED)
        elif mode == "register" and name_input.lower() in SKIP_VALUES:
            final_name = "Anonymous"
            confirmation = self.volunteer_manager.sign_up(sender, final_name, [])
        else:
            final_name = name_input
            confirmation = self.volunteer_manager.sign_up(sender, final_name, [])
        self.pending_actions.clear_registration(sender)
        return confirmation

def handle_message(parsed: ParsedMessage, sender: str, state_machine: BotStateMachine, pending_actions, volunteer_manager, msg_timestamp: Optional[int] = None) -> str:
    """
    handle_message - Processes an incoming message and executes the corresponding plugin command if available.
    
    Additionally, if a sender is in a pending deletion or registration/edit state (private message),
    the respective response is handled via the separated PendingStateHandlers.
    
    Args:
        parsed (ParsedMessage): The parsed message details.
        sender (str): The sender's identifier.
        state_machine (BotStateMachine): The bot's state machine instance.
        pending_actions: Instance managing pending actions.
        volunteer_manager: Instance managing volunteer operations.
        msg_timestamp (Optional[int]): The message timestamp.
    Returns:
        str: The response from the executed plugin command, or a pending state response.
    """
    # Only process pending responses for private chats
    if parsed.group_id is None:
        deletion_response = DeletionPendingHandler(pending_actions, volunteer_manager).process_deletion_response(parsed, sender)
        if deletion_response is not None:
            return deletion_response
        registration_response = RegistrationPendingHandler(pending_actions, volunteer_manager).process_registration_response(parsed, sender)
        if registration_response is not None:
            return registration_response

    command = parsed.command
    args = parsed.args
    if command:
        plugin_func = get_plugin(command)
        if not plugin_func:
            available_commands = list(get_all_plugins().keys())
            matches = difflib.get_close_matches(command, available_commands, n=1, cutoff=0.8)
            if matches:
                plugin_func = get_plugin(matches[0])
                logger.info(f"Fuzzy matching: '{command}' interpreted as '{matches[0]}'")
            else:
                return ""
        try:
            response = plugin_func(args, sender, state_machine, msg_timestamp=msg_timestamp)
            return response
        except (ValueError, TypeError, AttributeError) as e:
            logger.exception(f"[handle_message] Error executing plugin for command '{command}' with args '{args}' from sender '{sender}': {e}")
            return f"An error occurred while processing the command '{command}': {e}"
    return ""
    
# End of managers/message_handler.py
