"""
managers/message_handler.py - Handles incoming messages and dispatches commands.
Also processes interactive registration responses using a dedicated function.
"""

import logging
import difflib
from typing import Optional
from plugins.manager import get_plugin, get_all_plugins
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage

logger = logging.getLogger(__name__)

def process_registration_response(parsed: ParsedMessage, sender: str) -> Optional[str]:
    """
    Process a registration response for a pending registration.
    
    If the sender is in a pending registration state and sends a response,
    interpret the response as the full name for registration.
    
    Allowed skip responses (case-insensitive): "skip", "no", "quit", "no thank you",
    "unsubscribe", "q", "help", "stop", or empty input. In these cases, register as "Anonymous".
    
    Args:
        parsed (ParsedMessage): The parsed message.
        sender (str): The sender's identifier.
        
    Returns:
        Optional[str]: The registration confirmation message if processed, otherwise None.
    """
    from managers.volunteer_manager import PENDING_REGISTRATIONS, VOLUNTEER_MANAGER
    if sender not in PENDING_REGISTRATIONS:
        return None
    name_input = parsed.body.strip() if parsed.body else ""
    skip_values = {"skip", "no", "quit", "no thank you", "unsubscribe", "q", "help", "stop", ""}
    if name_input.lower() in skip_values:
        final_name = "Anonymous"
    else:
        final_name = name_input
    confirmation = VOLUNTEER_MANAGER.sign_up(sender, final_name, [])
    del PENDING_REGISTRATIONS[sender]
    return confirmation

def handle_message(parsed: ParsedMessage, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Process an incoming message and execute the corresponding plugin command if available.
    Additionally, if a sender is in a pending registration state (private message), the registration
    response is handled in a dedicated function.
    
    Args:
        parsed (ParsedMessage): The parsed message details.
        sender (str): The sender's identifier.
        state_machine (BotStateMachine): The bot's state machine instance.
        msg_timestamp (Optional[int]): The message timestamp.
        
    Returns:
        str: The response from the executed plugin command, registration confirmation,
             an error message if execution fails, or an empty string if no recognized command is found.
    """
    # Process pending registration responses for private messages
    if parsed.group_id is None:
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
            matches = difflib.get_close_matches(command, available_commands, n=1, cutoff=0.7)
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
