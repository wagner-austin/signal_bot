"""
tests/managers/test_message_handler.py - Tests for the message handler's pending state integration.
Verifies that PendingStateHandler correctly processes deletion and registration responses.
Uses dummy volunteer manager functions to simulate database operations.
"""

import pytest
from managers.message_handler import PendingStateHandler
from managers.pending_actions import PENDING_ACTIONS, PendingActions
from parsers.message_parser import ParsedMessage

# Dummy volunteer manager to simulate actions.
class DummyVolunteerManager:
    def delete_volunteer(self, sender: str) -> str:
        return f"Deleted volunteer {sender}"
    def sign_up(self, sender: str, name: str, skills: list) -> str:
        return f"Registered volunteer {name}"

def make_parsed_message(body: str, group_id: str = None) -> ParsedMessage:
    return ParsedMessage(
        sender="+1234567890",
        body=body,
        timestamp=123,
        group_id=group_id,
        reply_to=None,
        message_timestamp=None,
        command=None,
        args=None
    )

@pytest.fixture
def pending_state_handler():
    pending_actions = PendingActions()  # Create a fresh instance for testing.
    volunteer_manager = DummyVolunteerManager()
    return PendingStateHandler(pending_actions, volunteer_manager)

def test_process_deletion_response_initial_yes(pending_state_handler):
    sender = "+1234567890"
    pending_state_handler.pending_actions.set_deletion(sender, "initial")
    parsed = make_parsed_message("Yes")
    response = pending_state_handler.process_deletion_response(parsed, sender)
    assert "please respond with" in response.lower()
    assert pending_state_handler.pending_actions.get_deletion(sender) == "confirm"

def test_process_deletion_response_confirm_delete(pending_state_handler):
    sender = "+1234567890"
    pending_state_handler.pending_actions.set_deletion(sender, "confirm")
    parsed = make_parsed_message("DELETE")
    response = pending_state_handler.process_deletion_response(parsed, sender)
    assert "deleted volunteer" in response.lower()
    assert not pending_state_handler.pending_actions.has_deletion(sender)

def test_process_registration_response_register_skip(pending_state_handler):
    sender = "+1234567890"
    pending_state_handler.pending_actions.set_registration(sender, "register")
    parsed = make_parsed_message("skip")
    response = pending_state_handler.process_registration_response(parsed, sender)
    assert "registered volunteer anonymous" in response.lower()
    assert not pending_state_handler.pending_actions.has_registration(sender)

def test_process_registration_response_edit_with_name(pending_state_handler):
    sender = "+1234567890"
    pending_state_handler.pending_actions.set_registration(sender, "edit")
    parsed = make_parsed_message("New Name")
    response = pending_state_handler.process_registration_response(parsed, sender)
    assert "registered volunteer new name" in response.lower()
    assert not pending_state_handler.pending_actions.has_registration(sender)

# End of tests/managers/test_message_handler.py