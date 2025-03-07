"""
managers/message_handler.py - Handles incoming messages and dispatches commands.
Also processes interactive registration, edit, and deletion responses using dedicated functions.
"""

import logging
import difflib
from typing import Optional
from plugins.manager import get_plugin, get_all_plugins
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage

logger = logging.getLogger(__name__)

def process_deletion_response(parsed: ParsedMessage, sender: str) -> Optional[str]:
    """
    Process a deletion response for a pending deletion.
    
    The deletion process has two stages:
      - "initial": expecting a response "Yes" or "No" to the prompt.
      - "confirm": expecting the exact text "DELETE" to finalize deletion.
    
    Args:
        parsed (ParsedMessage): The parsed message.
        sender (str): The sender's identifier.
        
    Returns:
        Optional[str]: The deletion confirmation or cancellation message if processed, otherwise None.
    """
    from managers.volunteer_manager import PENDING_DELETIONS, VOLUNTEER_MANAGER
    from core.database import get_volunteer_record
    if sender not in PENDING_DELETIONS:
        return None
    state = PENDING_DELETIONS[sender]  # "initial" or "confirm"
    user_input = parsed.body.strip().lower() if parsed.body else ""
    if state == "initial":
        if user_input in {"yes", "y", "yea", "sure"}:
            PENDING_DELETIONS[sender] = "confirm"
            return 'Please respond with "DELETE" to delete your account.'
        else:
            record = get_volunteer_record(sender)
            confirmation = f"Thank you. You are registered as \"{record['name']}\"." if record else "Deletion cancelled."
            del PENDING_DELETIONS[sender]
            return confirmation
    elif state == "confirm":
        if parsed.body.strip() == "DELETE":
            confirmation = VOLUNTEER_MANAGER.delete_volunteer(sender)
            del PENDING_DELETIONS[sender]
            return confirmation
        else:
            record = get_volunteer_record(sender)
            confirmation = f"Thank you. You are registered as \"{record['name']}\"." if record else "Deletion cancelled."
            del PENDING_DELETIONS[sender]
            return confirmation
    return None

def process_registration_response(parsed: ParsedMessage, sender: str) -> Optional[str]:
    """
    Process a registration or edit response for a pending registration/edit.
    
    If the sender is in a pending registration state and sends a response,
    interpret the response as the full name for registration or name editing.
    
    For pending registration:
      - Allowed skip responses (case-insensitive): "skip", "no", "quit", "no thank you",
        "unsubscribe", "q", "help", "stop", or empty input will register as "Anonymous".
    
    For pending edit:
      - Allowed skip responses will cancel editing without updating the name.
    
    Args:
        parsed (ParsedMessage): The parsed message.
        sender (str): The sender's identifier.
        
    Returns:
        Optional[str]: The confirmation message if processed, otherwise None.
    """
    from managers.volunteer_manager import PENDING_REGISTRATIONS, VOLUNTEER_MANAGER
    from core.database import get_volunteer_record
    if sender not in PENDING_REGISTRATIONS:
        return None
    mode = PENDING_REGISTRATIONS[sender]  # mode can be "register" or "edit"
    name_input = parsed.body.strip() if parsed.body else ""
    skip_values = {"skip", "s", "no", "n", "quit", "q", "no thank you", "unsubscribe", "help", "stop", "cancel", ""}
    if mode == "edit" and name_input.lower() in skip_values:
        record = get_volunteer_record(sender)
        confirmation = f"Editing cancelled. You remain registered as \"{record['name']}\"." if record else "Editing cancelled."
    elif mode == "register" and name_input.lower() in skip_values:
        final_name = "Anonymous"
        confirmation = VOLUNTEER_MANAGER.sign_up(sender, final_name, [])
    else:
        final_name = name_input
        confirmation = VOLUNTEER_MANAGER.sign_up(sender, final_name, [])
    del PENDING_REGISTRATIONS[sender]
    return confirmation

def handle_message(parsed: ParsedMessage, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Process an incoming message and execute the corresponding plugin command if available.
    Additionally, if a sender is in a pending deletion or registration/edit state (private message),
    the respective response is handled in a dedicated function.
    
    Args:
        parsed (ParsedMessage): The parsed message details.
        sender (str): The sender's identifier.
        state_machine (BotStateMachine): The bot's state machine instance.
        msg_timestamp (Optional[int]): The message timestamp.
        
    Returns:
        str: The response from the executed plugin command, deletion or registration/edit confirmation,
             an error message if execution fails, or an empty string if no recognized command is found.
    """
    # Process pending deletion responses first for private messages.
    if parsed.group_id is None:
        del_response = process_deletion_response(parsed, sender)
        if del_response is not None:
            return del_response
        # Process pending registration/edit responses.
        reg_response = process_registration_response(parsed, sender)
        if reg_response is not None:
            return reg_response

    command = parsed.command
    args = parsed.args
    if command:
        plugin_func = get_plugin(command)
        if not plugin_func:
            # Use fuzzy matching to find a close match for the command.
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
