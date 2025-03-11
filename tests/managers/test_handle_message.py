#!/usr/bin/env python
"""
tests/managers/test_handle_message.py - Tests for the message dispatch functionality.
Verifies that fuzzy matching correctly handles near-miss command inputs and that mixed
group commands with extra trailing text are correctly parsed.
"""
import pytest
from managers.message.message_dispatcher import dispatch_message as handle_message
from core.state import BotStateMachine
from parsers.message_parser import ParsedMessage, parse_message
from managers.pending_actions import PendingActions
from managers.volunteer_manager import VOLUNTEER_MANAGER

# Helper function to create a full envelope message for parsing.
def make_envelope_message(body: str, sender: str = "+1234567890", group_id: str = None) -> ParsedMessage:
    envelope = f"from: {sender}\nBody: {body}\nTimestamp: 123\n"
    if group_id:
        envelope += f"Group info: {group_id}\n"
    return parse_message(envelope)

# Fixture to register a dummy plugin for "volunteer status" command.
@pytest.fixture
def volunteer_status_plugin(monkeypatch):
    from plugins.manager import plugin_registry, alias_mapping
    alias_mapping["volunteer status"] = "volunteer status"
    def dummy_volunteer_status(args, sender, state_machine, msg_timestamp=None):
         return f"status: {args}"
    plugin_registry["volunteer status"] = {
        "function": dummy_volunteer_status,
        "aliases": ["volunteer status"],
        "help_visible": True
    }
    yield
    alias_mapping.pop("volunteer status", None)
    plugin_registry.pop("volunteer status", None)

# Fixture to register a dummy plugin for "dummy" command.
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

def test_handle_message_fuzzy_matching(dummy_plugin):
    """
    Test that a near-miss command ("tset") is fuzzy-matched correctly.
    """
    parsed = make_envelope_message("@bot tset", sender="+111")
    state_machine = BotStateMachine()
    pending_actions = PendingActions()
    response = handle_message(parsed, "+111", state_machine, pending_actions, VOLUNTEER_MANAGER, msg_timestamp=123)
    assert response == "yes"

def test_group_command_with_extra_text(volunteer_status_plugin):
    """
    Test that a group message with extra trailing text after the recognized plugin command
    correctly extracts the command "volunteer status" and arguments "extra nonsense".
    """
    parsed = make_envelope_message("@bot volunteer status extra nonsense", sender="+1111111111", group_id="group123")
    state_machine = BotStateMachine()
    pending_actions = PendingActions()
    # Dummy volunteer manager for dependency injection.
    class DummyVolunteerManager:
         def delete_volunteer(self, sender):
             return "deleted"
         def sign_up(self, sender, name, skills):
             return f"registered {name}"
    dummy_vol_manager = DummyVolunteerManager()
    
    response = handle_message(parsed, parsed.sender, state_machine, pending_actions, dummy_vol_manager, msg_timestamp=123)
    
    # Verify that the command and args were extracted correctly.
    assert parsed.command == "volunteer status"
    assert parsed.args == "extra nonsense"
    # Verify that the dummy plugin processed the extra text as arguments.
    assert response == "status: extra nonsense"

def test_message_manager_process_message():
    """
    Test that MessageManager.process_message correctly dispatches the dummy command.
    """
    from managers.message_manager import MessageManager
    state_machine = BotStateMachine()
    message_manager = MessageManager(state_machine)
    parsed = make_envelope_message("@bot dummy", sender="+1111111111")
    pending_actions = DummyPendingActions()
    volunteer_manager = DummyVolunteerManager()
    response = message_manager.process_message(parsed, parsed.sender, pending_actions, volunteer_manager, msg_timestamp=123)
    assert response == "dummy response"

# --- Dummy Classes for Testing ---
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
    def delete_volunteer(self, sender: str) -> str:
        return "deleted"
    def sign_up(self, sender: str, name: str, skills: list) -> str:
        return "dummy response"

# End of tests/managers/test_handle_message.py