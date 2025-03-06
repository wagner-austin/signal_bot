"""
managers/message_handler.py
---------------------------
Handles incoming messages and dispatches commands using the unified plugins/manager.
Now only responds to recognized commands and implements fuzzy matching to catch typos.
"""

import logging
import difflib
from typing import Optional
from plugins.manager import get_plugin, get_all_plugins
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage

logger = logging.getLogger(__name__)

def handle_message(parsed: ParsedMessage, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Process an incoming message and execute the corresponding plugin command if available.
    
    This function extracts the command and arguments from the ParsedMessage,
    attempts an exact lookup, and if not found uses fuzzy matching to catch typos.
    If no recognized command is found, it returns an empty string (no response).
    
    Args:
        parsed (ParsedMessage): The parsed message details.
        sender (str): The identifier of the sender (e.g., phone number).
        state_machine (BotStateMachine): The bot's state machine instance.
        msg_timestamp (Optional[int]): The timestamp of the message, if available.
        
    Returns:
        str: The response from the executed plugin command, an error message if execution fails,
             or an empty string if no recognized command is found.
    """
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
                # Command not recognized; do not respond.
                return ""
        try:
            response = plugin_func(args, sender, state_machine, msg_timestamp=msg_timestamp)
            return response
        except (ValueError, TypeError, AttributeError) as e:
            logger.exception(f"[handle_message] Error executing plugin for command '{command}' with args '{args}' from sender '{sender}': {e}")
            return f"An error occurred while processing the command '{command}': {e}"
    return ""

# End of managers/message_handler.py