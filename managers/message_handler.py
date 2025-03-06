"""
managers/message_handler.py
---------------------------
Handles incoming messages and dispatches commands using the unified plugins/manager.
Supports two command formats:
  1) "@bot <command> <arguments>"
  2) "<command> <arguments>"
Handles extra whitespace and ambiguous input robustly.
"""

import re
import logging
from typing import Tuple, Optional
from plugins.manager import get_plugin  # Updated import from unified plugins/manager

logger = logging.getLogger(__name__)

def parse_command(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse the incoming message to determine the command and its arguments.

    This function supports two formats:
      1) "@bot <command> <args>"
      2) "<command> <args>"
    
    It normalizes whitespace, validates that a command is present,
    and returns a tuple of (command, args) or (None, None) if parsing fails.

    Parameters:
        message (str): The incoming message text.
        
    Returns:
        Tuple[Optional[str], Optional[str]]:
            - First element: The command in lowercase, or None if not found.
            - Second element: The arguments string (possibly empty), or None if not found.
    """
    # Remove leading/trailing whitespace and collapse multiple spaces into one.
    message = " ".join(message.strip().split())
    if not message:
        return None, None

    # Check if the message starts with the '@bot' prefix.
    if message.lower().startswith("@bot"):
        parts = message.split(" ", 2)
        if len(parts) < 2 or not parts[1].strip():
            return None, None
        command = parts[1].strip().lower()
        args = parts[2].strip() if len(parts) == 3 else ""
        return command, args

    # Otherwise, assume the first word is the command.
    parts = message.split(" ", 1)
    command = parts[0].strip().lower()
    args = parts[1].strip() if len(parts) == 2 else ""
    if not command:
        return None, None
    return command, args

def handle_message(message: str, sender: str, msg_timestamp: Optional[int] = None) -> str:
    """
    Process an incoming message and execute the corresponding plugin command if available.

    The function extracts the command and arguments from the message using `parse_command`
    and retrieves the appropriate plugin function. If the plugin exists, it is executed,
    and its response is returned. If no valid command is found or an error occurs,
    an error message or an empty string is returned.

    Parameters:
        message (str): The incoming message text.
        sender (str): The identifier of the sender (e.g., phone number).
        msg_timestamp (Optional[int]): The timestamp of the message, if available.
        
    Returns:
        str:
            - The response from the executed plugin command,
            - An error message if command execution fails,
            - Or an empty string if no valid command is identified.
    """
    command, args = parse_command(message)
    if command:
        plugin_func = get_plugin(command)
        if plugin_func:
            try:
                response = plugin_func(args, sender, msg_timestamp=msg_timestamp)
                return response
            except Exception as e:
                logger.exception(
                    f"Error executing plugin for command '{command}' with args '{args}' "
                    f"from sender '{sender}' and message '{message}': {e}"
                )
                return f"An error occurred while processing the command '{command}'."
        else:
            return f"Command '{command}' not recognized."
    return ""

# End of managers/message_handler.py
