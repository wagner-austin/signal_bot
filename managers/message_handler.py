"""
message_handler.py
---------------------------
Handles incoming messages and dispatches commands using the unified plugins/manager.
Extracts the command and its arguments from the parsed message dictionary.
"""

import logging
from typing import Optional
from plugins.manager import get_plugin  # Updated import from unified plugins/manager

logger = logging.getLogger(__name__)

def handle_message(parsed: dict, sender: str, state_machine, msg_timestamp: Optional[int] = None) -> str:
    """
    Process an incoming message and execute the corresponding plugin command if available.
    
    This function extracts the command and arguments from the parsed message dictionary,
    retrieves the appropriate plugin function, and executes it.
    
    Parameters:
        parsed (dict): The parsed message details, including 'command' and 'args'.
        sender (str): The identifier of the sender (e.g., phone number).
        state_machine: The BotStateMachine instance for dependency injection.
        msg_timestamp (Optional[int]): The timestamp of the message, if available.
        
    Returns:
        str:
            - The response from the executed plugin command,
            - An error message if command execution fails,
            - Or an empty string if no valid command is identified.
    """
    command = parsed.get('command')
    args = parsed.get('args')
    if command:
        plugin_func = get_plugin(command)
        if plugin_func:
            try:
                response = plugin_func(args, sender, state_machine, msg_timestamp=msg_timestamp)
                return response
            except Exception as e:
                logger.exception(
                    f"Error executing plugin for command '{command}' with args '{args}' "
                    f"from sender '{sender}': {e}"
                )
                return f"An error occurred while processing the command '{command}'."
        else:
            return f"Command '{command}' not recognized."
    return ""

# End of managers/message_handler.py