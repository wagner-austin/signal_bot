"""
managers/message_handler.py
------------------
Handles incoming messages and dispatches commands using the plugin manager.
Supports:
  1) "@bot <command> <arguments>"
  2) "<command> <arguments>"
Handles extra whitespace and ambiguous input robustly.
"""

import re
import logging
from typing import Tuple, Optional
from managers.plugin_manager import get_plugin

def parse_command(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Determine the intended command and arguments from the message.
    
    This function supports two formats:
      1) "@bot <command> <args>"
      2) "<command> <args>"
    
    It normalizes whitespace, validates that a command is present, and
    returns a tuple of (command, args) or (None, None) if parsing fails.
    
    Args:
        message (str): The incoming message text.
        
    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the command and its arguments.
        Returns (None, None) if the message is empty or the command cannot be parsed.
    """
    # Remove leading/trailing whitespace and collapse multiple spaces into one.
    message = " ".join(message.strip().split())
    if not message:
        return None, None

    # Check if the message starts with the '@bot' prefix.
    if message.lower().startswith("@bot"):
        parts = message.split(" ", 2)
        # Validate that there is a command after '@bot'
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
    Process a message, execute the corresponding plugin command (if it exists),
    and return the plugin's response.
    
    Args:
        message (str): The incoming message text.
        sender (str): The sender's identifier (e.g., phone number).
        msg_timestamp (Optional[int]): The timestamp of the message.
        
    Returns:
        str: The response from the executed plugin command, or an error message if the command is not recognized.
    """
    command, args = parse_command(message)
    if command:
        plugin_func = get_plugin(command)
        if plugin_func:
            try:
                # Run the plugin function
                response = plugin_func(args, sender, msg_timestamp=msg_timestamp)
                return response
            except Exception as e:
                logging.exception(f"Error executing plugin for command '{command}': {e}")
                return f"An error occurred while processing the command '{command}'."
        else:
            return f"Command '{command}' not recognized."
    return ""

# End of managers/message_handler.py