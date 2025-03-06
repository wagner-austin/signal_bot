"""
managers/message_handler.py
------------------
Handles incoming messages and dispatches commands using the plugin manager.
Now supports:
  1) "@bot <command> <arguments>"
  2) "<command> <arguments>"
for every plugin command.
"""

import re
from typing import Tuple, Optional
from managers.plugin_manager import get_plugin

def parse_command(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Determine the intended command and arguments from the message.
    
    Args:
        message (str): The incoming message text.
        
    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the command and its arguments.
        Returns (None, None) if the message is empty or command cannot be parsed.
    """
    message = message.strip()

    # If message starts with "@bot ", parse the next token as the command
    if re.match(r'^@bot\s', message, re.IGNORECASE):
        parts = message.split(None, 2)  # split on whitespace
        # parts[0] = '@bot', parts[1] = command, parts[2] = the rest (if any)
        if len(parts) >= 2:
            command = parts[1].lower()
            args = parts[2] if len(parts) > 2 else ""
            return command, args
        else:
            return None, None

    # Otherwise, parse the first word as the command
    parts = message.split(None, 1)
    if not parts:
        return None, None

    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
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
            # Run the plugin function
            response = plugin_func(args, sender, msg_timestamp=msg_timestamp)
            return response
        else:
            return f"Command '{command}' not recognized."
    return ""

# End of managers/message_handler.py