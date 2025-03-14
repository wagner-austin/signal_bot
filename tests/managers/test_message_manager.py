#!/usr/bin/env python
"""
tests/managers/test_message_manager.py --- Tests for the MessageManager facade.
Verifies that process_message correctly delegates to the message dispatcher.
Note: The GETTING_STARTED message is now sent separately via process_incoming.
"""
import pytest
from managers.message_manager import MessageManager
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage
from core.messages import GETTING_STARTED

# Register dummy plugin for the "dummy" command.
@pytest.fixture(autouse=True)
def register_dummy_command_plugin(monkeypatch):
    from plugins.manager import plugin_registry, alias_mapping
    alias_mapping["dummy"] = "dummy"
    plugin_registry["dummy"] = {
         "function": lambda args, sender, state_machine, msg_timestamp=None: "dummy response",
         "aliases": ["dummy"],
         "help_visible": True
    }
    yield
    alias_mapping.pop("dummy", None)
    plugin_registry.pop("dummy", None)

def make_dummy_parsed_message() -> ParsedMessage:
    """
    make_dummy_parsed_message --- Creates a dummy ParsedMessage with command "dummy" and no arguments.
    
    Returns:
        ParsedMessage: A dummy message object.
    """
    from parsers.message_parser import ParsedMessage
    return ParsedMessage(
        sender="+1111111111",
        body="@bot dummy",
        timestamp=123,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command="dummy",
        args=""
    )

def test_message_manager_process_message():
    """
    Test that MessageManager.process_message dispatches the dummy command correctly.
    The response should be "dummy response".
    """
    from managers.message_manager import MessageManager
    state_machine = BotStateMachine()
    message_manager = MessageManager(state_machine)
    parsed = make_dummy_parsed_message()
    volunteer_manager = DummyVolunteerManager()
    response = message_manager.process_message(parsed, parsed.sender, volunteer_manager, msg_timestamp=123)
    expected_response = "dummy response"
    assert response == expected_response

class DummyVolunteerManager:
    def register_volunteer(self, sender: str, name: str, skills: list):
        return f"registered {name}"
    def volunteer_status(self):
        return "status ok"

# End of tests/managers/test_message_manager.py