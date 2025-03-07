"""
tests/managers/test_message_handler.py - Tests for the message handler's pending state integration.
Verifies that PendingStateHandler correctly processes deletion and registration responses.
Uses dummy volunteer manager functions to simulate database operations.
"""

import pytest
from managers.message_handler import PendingStateHandler
from managers.pending_actions import PendingActions
from parsers.message_parser import ParsedMessage

# Create a dummy volunteer manager to simulate volunteer actions.
class DummyVolunteerManager:
    def delete_volunteer(self, sender: str) -> str:
        return f"Deleted volunteer {sender}"

    def sign_up(self, sender: str, name: str, skills: list) -> str:
        return f"Registered volunteer {name}"

def make_parsed_message(body: str, group_id: str = None) -> ParsedMessage:
    """
    Helper function to create a dummy ParsedMessage.
    """
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
    """
    Provides a fresh instance of PendingStateHandler with a dummy volunteer manager.
    """
    pending_actions = PendingActions()
    volunteer_manager = DummyVolunteerManager()
    return PendingStateHandler(pending_actions, volunteer_manager)

def test_process_deletion_response_initial_yes(pending_state_handler):
    """
    Test that a deletion response in the "initial" state with an affirmative response
    updates the state and returns the expected prompt.
    """
    handler = pending_state_handler
    sender = "+1234567890"
    handler.pending_actions.set_deletion(sender, "initial")
    parsed = make_parsed_message("Yes")
    response = handler.process_deletion_response(parsed, sender)
    assert "please respond with" in response.lower()
    # Ensure state is updated to "confirm"
    assert handler.pending_actions.get_deletion(sender) == "confirm"

def test_process_deletion_response_confirm_delete(pending_state_handler):
    """
    Test that a deletion response in the "confirm" state with 'DELETE' input
    triggers deletion and clears the pending state.
    """
    handler = pending_state_handler
    sender = "+1234567890"
    handler.pending_actions.set_deletion(sender, "confirm")
    parsed = make_parsed_message("DELETE")
    response = handler.process_deletion_response(parsed, sender)
    assert "deleted volunteer" in response.lower()
    # Ensure deletion state is cleared.
    assert not handler.pending_actions.has_deletion(sender)

def test_process_registration_response_register_skip(pending_state_handler):
    """
    Test that a registration response in the "register" state with a skip input
    registers the user as "Anonymous" and clears the pending state.
    """
    handler = pending_state_handler
    sender = "+1234567890"
    handler.pending_actions.set_registration(sender, "register")
    parsed = make_parsed_message("skip")
    response = handler.process_registration_response(parsed, sender)
    assert "registered volunteer anonymous" in response.lower()
    assert not handler.pending_actions.has_registration(sender)

def test_process_registration_response_edit_with_name(pending_state_handler):
    """
    Test that a registration (edit) response with a valid name registers the new name
    and clears the pending state.
    """
    handler = pending_state_handler
    sender = "+1234567890"
    handler.pending_actions.set_registration(sender, "edit")
    parsed = make_parsed_message("New Name")
    response = handler.process_registration_response(parsed, sender)
    assert "registered volunteer new name" in response.lower()
    assert not handler.pending_actions.has_registration(sender)

# End of tests/managers/test_message_handler.py