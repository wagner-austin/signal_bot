"""
managers/message_manager.py
---------------------------
Aggregated message manager facade.
Now prioritizes flow processing (if active) before checking plugin commands,
ensuring only one dispatch path is used per message.
"""

from typing import Any, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from parsers.message_parser import ParsedMessage

from core.state import BotStateMachine
from managers.message.message_dispatcher import dispatch_message
from core.api.flow_state_api import get_active_flow
from plugins.manager import get_plugin
import logging

logger = logging.getLogger(__name__)

class MessageManager:
    """
    MessageManager - Aggregated facade for message processing.
    """

    def __init__(self, state_machine: Optional[BotStateMachine] = None) -> None:
        from core.state import BotStateMachine
        self.state_machine = state_machine if state_machine else BotStateMachine()

    def process_message(
        self,
        parsed: "ParsedMessage",
        sender: str,
        volunteer_manager: Any,
        msg_timestamp: Optional[int] = None
    ) -> str:
        """
        Process the incoming message by first checking if the user has an active flow.
        If so, route the message to that flow. Otherwise, dispatch to the recognized plugin command.
        Returns a single string response (or an empty string if no response).
        """
        # 1) Check if user is in an active flow
        active_flow = get_active_flow(sender)
        if active_flow:
            from managers.flow_manager import FlowManager
            fm = FlowManager()
            return fm.handle_flow_input(sender, parsed.body or "")

        # 2) If not in a flow, check for a plugin command
        command = parsed.command
        if command:
            plugin_func = get_plugin(command)
            if plugin_func:
                return dispatch_message(
                    parsed,
                    sender,
                    self.state_machine,
                    volunteer_manager,
                    msg_timestamp=msg_timestamp
                )

        # 3) Return empty if neither a flow nor a plugin command applies
        return ""

# End of managers/message_manager.py