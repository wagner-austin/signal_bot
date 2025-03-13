#!/usr/bin/env python
"""
tests/managers/test_message_manager.py - Tests for the MessageManager facade.
Verifies that the process_message method correctly delegates to the message dispatcher,
and that a welcome message is included for new senders without a volunteer record.
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
    Creates a dummy ParsedMessage with the command "dummy" and no arguments.
    
    Returns:
        ParsedMessage: A dummy message object.
    """
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

# Dummy implementations for pending actions and volunteer manager.
class DummyPendingActions:
    def has_event_creation(self, sender: str) -> bool:
        return False
    def clear_event_creation(self, sender: str) -> None:
        pass
    def has_deletion(self, sender: str) -> bool:
        return False
    def get_deletion(self, sender: str):
        return None
    def clear_deletion(self, sender: str) -> None:
        pass
    def has_registration(self, sender: str) -> bool:
        return False
    def get_registration(self, sender: str):
        return None
    def clear_registration(self, sender: str) -> None:
        pass

class DummyVolunteerManager:
    def register_volunteer(self, sender: str, name: str, skills: list):
        return f"registered {name}"
    def volunteer_status(self):
        return "status ok"

def test_message_manager_process_message():
    """
    Test that MessageManager.process_message correctly dispatches the dummy command.
    Since the volunteer record is missing, the GETTING_STARTED message should be prepended.
    """
    state_machine = BotStateMachine()
    message_manager = MessageManager(state_machine)
    parsed = make_dummy_parsed_message()
    pending_actions = DummyPendingActions()
    volunteer_manager = DummyVolunteerManager()
    response = message_manager.process_message(parsed, parsed.sender, pending_actions, volunteer_manager, msg_timestamp=123)
    expected_response = GETTING_STARTED + "\n" + "dummy response"
    assert response == expected_response

# End of tests/managers/test_message_manager.py