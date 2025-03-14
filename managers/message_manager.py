"""
managers/message_manager.py
---------------------------
Aggregated message manager facade.
Now defers multi-step flow input handling to FlowManager if no plugin command is recognized.
"""

from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from parsers.message_parser import ParsedMessage

from core.state import BotStateMachine
from managers.message.message_dispatcher import dispatch_message
from managers.user_states_manager import get_active_flow
from plugins.manager import get_plugin
import logging

logger = logging.getLogger(__name__)

# We'll import the new FlowManager instance
# (For a real deployment, you might create a single global or pass it down.)
from managers.flow_manager import FlowManager

FLOW_MANAGER = FlowManager()

class MessageManager:
    """
    MessageManager - Aggregated facade for message processing.
    """

    def __init__(self, state_machine: Optional[BotStateMachine] = None) -> None:
        from core.state import BotStateMachine
        self.state_machine = state_machine if state_machine else BotStateMachine()

    def process_message(self, parsed: "ParsedMessage", sender: str,
                        volunteer_manager: Any,
                        msg_timestamp: Optional[int] = None) -> str:
        """
        process_message - Dispatches recognized plugin commands or passes user input to FlowManager if in a flow.
        """
        command = parsed.command
        if command:
            # Attempt normal plugin dispatch
            plugin_func = get_plugin(command)
            if plugin_func:
                return dispatch_message(parsed, sender, self.state_machine, volunteer_manager,
                                        msg_timestamp=msg_timestamp)
            # No recognized plugin => fall through to flow logic
        # If user is in a flow, pass to FlowManager
        active_flow = get_active_flow(sender)
        if active_flow:
            return FLOW_MANAGER.handle_flow_input(sender, parsed.body or "")
        return ""

# End of managers/message_manager.py