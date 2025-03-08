"""
managers/message_handler.py - Handles incoming messages and dispatches commands.
Separates pending flows (registration, deletion, and event creation) from normal command processing.
"""

import logging
import difflib
from typing import Optional
from plugins.manager import get_plugin, get_all_plugins
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage
from core.messages import (
    DELETION_CONFIRM_PROMPT, ALREADY_REGISTERED, DELETION_CANCELED,
    EDIT_PROMPT, EDIT_CANCELED, EDIT_CANCELED_WITH_NAME
)
from core.constants import SKIP_VALUES

logger = logging.getLogger(__name__)

def _get_confirmation_message(sender: str, registered_format: str, default_message: str) -> str:
    """
    _get_confirmation_message - Fetches the volunteer record and generates a confirmation message.
    
    Args:
        sender (str): The sender's phone number.
        registered_format (str): Format string expecting a 'name' parameter.
        default_message (str): Default message if no record is found.
        
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
    """
    def __init__(self, pending_actions, volunteer_manager) -> None:
        self.pending_actions = pending_actions
        self.volunteer_manager = volunteer_manager

    def process_deletion_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        """
        Processes a deletion response using pending deletion state.
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
    """
    def __init__(self, pending_actions, volunteer_manager) -> None:
        self.pending_actions = pending_actions
        self.volunteer_manager = volunteer_manager

    def process_registration_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        """
        Processes a registration or edit response using the pending registration state.
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

class EventCreationPendingHandler:
    """
    EventCreationPendingHandler - Handles pending event creation responses.
    
    If a sender is in a pending event creation state, processes the reply to either create
    the event or cancel the process.
    """
    def __init__(self, pending_actions) -> None:
        self.pending_actions = pending_actions

    def process_event_creation_response(self, parsed: ParsedMessage, sender: str) -> Optional[str]:
        """
        Processes a pending event creation response.
        
        Returns:
            str: Confirmation message if event is created or cancellation message.
        """
        from core.event_manager import create_event
        if not self.pending_actions.has_event_creation(sender):
            return None
        user_input = parsed.body.strip() if parsed.body else ""
        if user_input.lower() in SKIP_VALUES:
            self.pending_actions.clear_event_creation(sender)
            return "Event creation cancelled."
        try:
            parts = {}
            for part in user_input.split(","):
                key, value = part.split(":", 1)
                parts[key.strip().lower()] = value.strip()
            required_fields = ["title", "date", "time", "location", "description"]
            if not all(field in parts for field in required_fields):
                self.pending_actions.clear_event_creation(sender)
                return "Missing one or more required fields. Event creation cancelled."
            event_id = create_event(parts["title"], parts["date"], parts["time"], parts["location"], parts["description"])
            self.pending_actions.clear_event_creation(sender)
            return f"Event '{parts['title']}' created successfully with ID {event_id}."
        except Exception as e:
            self.pending_actions.clear_event_creation(sender)
            return f"Error parsing event details: {str(e)}"

def handle_message(parsed: ParsedMessage, sender: str, state_machine: BotStateMachine, pending_actions, volunteer_manager, msg_timestamp: Optional[int] = None) -> str:
    """
    Processes an incoming message, handling pending responses and executing the appropriate plugin command.
    """
    # Only process pending responses for private chats
    if parsed.group_id is None:
        # Handle pending event creation first
        event_response = EventCreationPendingHandler(pending_actions).process_event_creation_response(parsed, sender)
        if event_response is not None:
            return event_response
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
            matches = difflib.get_close_matches(command, available_commands, n=1, cutoff=0.75)
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