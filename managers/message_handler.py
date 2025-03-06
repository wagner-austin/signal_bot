"""
message_handler.py
---------------------------
Handles incoming messages and dispatches commands using the unified plugins/manager.
Extracts the command and its arguments from the parsed message dictionary.
"""

import logging
from typing import Optional, Dict, Any
from plugins.manager import get_plugin
from core.state import BotStateMachine

logger = logging.getLogger(__name__)

def handle_message(parsed: Dict[str, Any], sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Process an incoming message and execute the corresponding plugin command if available.
    
    This function extracts the command and arguments from the parsed message dictionary,
    retrieves the appropriate plugin function, and executes it.
    
    Args:
        parsed (Dict[str, Any]): The parsed message details. Expected keys include:
            - 'command': Optional[str] - The extracted command in lowercase.
            - 'args': Optional[str] - The command arguments.
        sender (str): The identifier of the sender (e.g., phone number).
        state_machine (BotStateMachine): The bot's state machine instance.
        msg_timestamp (Optional[int]): The timestamp of the message, if available.
        
    Returns:
        str: The response from the executed plugin command, an error message if execution fails,
             or an empty string if no valid command is identified.
             
    Raises:
        Exception: Any exception raised by the plugin function is caught and logged.
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
                logger.exception(f"[handle_message] Error executing plugin for command '{command}' with args '{args}' from sender '{sender}': {e}")
                return f"An error occurred while processing the command '{command}'."
        else:
            return f"Command '{command}' not recognized."
    return ""

# End of managers/message_handler.py