"""
managers/message/message_dispatcher.py --- Dispatches incoming messages to appropriate plugins.
Handles PluginArgError uniformly and detects if a plugin is disabled.
"""

import logging
import difflib
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from parsers.message_parser import ParsedMessage

from core.state import BotStateMachine
from plugins.manager import get_plugin, get_all_plugins, disabled_plugins
from parsers.plugin_arg_parser import PluginArgError

logger = logging.getLogger(__name__)

def dispatch_message(parsed: "ParsedMessage", sender: str, state_machine: BotStateMachine,
                     volunteer_manager: any,
                     msg_timestamp: Optional[int] = None, logger: Optional[logging.Logger] = None) -> str:
    """
    dispatch_message - Processes an incoming message by dispatching commands to plugins.
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    command: Optional[str] = parsed.command
    args: Optional[str] = parsed.args

    if command:
        plugin_func = get_plugin(command)
        if not plugin_func:
            # Attempt fuzzy matching
            available_commands = list(get_all_plugins().keys())
            matches = difflib.get_close_matches(command, available_commands, n=1, cutoff=0.75)
            if matches:
                matched_cmd = matches[0]
                if matched_cmd in disabled_plugins:
                    return f"Plugin '{matched_cmd}' is currently disabled."
                plugin_func = get_all_plugins()[matched_cmd]["function"]
                logger.info(f"Fuzzy matching: '{command}' -> '{matches[0]}'")
            else:
                return ""

        if plugin_func:
            try:
                # Always call with the correct arguments
                response = plugin_func(args or "", sender, state_machine, msg_timestamp=msg_timestamp)
                # If the plugin is disabled, it returns None
                if response is None:
                    return f"Plugin '{command}' is currently disabled."
                if not isinstance(response, str):
                    logger.warning(f"Plugin '{command}' returned non-string or None. Returning empty string.")
                    response = ""
                return response
            except PluginArgError as pae:
                logger.error(f"Argument parsing error for command '{command}': {pae}")
                return str(pae)
            except Exception as e:
                logger.exception(
                    f"Error executing plugin for command '{command}' with args '{args}' "
                    f"from sender '{sender}': {e}"
                )
                return "An internal error occurred while processing your command."
        return ""

    return ""

# End of managers/message/message_dispatcher.py