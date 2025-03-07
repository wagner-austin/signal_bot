"""
tests/managers/test_message_handler.py - Tests for the message handler's pending state integration.
Verifies that separate pending state handlers for deletion and registration/edit responses function correctly.
Uses dummy volunteer manager functions to simulate database operations.
"""

import pytest
from managers.message_handler import DeletionPendingHandler, RegistrationPendingHandler
from managers.pending_actions import PendingActions
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
def pending_actions():
    return PendingActions()  # Fresh instance for testing

@pytest.fixture
def volunteer_manager():
    return DummyVolunteerManager()

@pytest.fixture
def deletion_handler(pending_actions, volunteer_manager):
    return DeletionPendingHandler(pending_actions, volunteer_manager)

@pytest.fixture
def registration_handler(pending_actions, volunteer_manager):
    return RegistrationPendingHandler(pending_actions, volunteer_manager)

def test_process_deletion_response_initial_yes(deletion_handler, pending_actions):
    sender = "+1234567890"
    pending_actions.set_deletion(sender, "initial")
    parsed = make_parsed_message("Yes")
    response = deletion_handler.process_deletion_response(parsed, sender)
    # Expect deletion confirmation prompt since state transitions to "confirm"
    assert "please respond with" in response.lower()
    assert pending_actions.get_deletion(sender) == "confirm"

def test_process_deletion_response_confirm_delete(deletion_handler, pending_actions):
    sender = "+1234567890"
    pending_actions.set_deletion(sender, "confirm")
    parsed = make_parsed_message("DELETE")
    response = deletion_handler.process_deletion_response(parsed, sender)
    assert "deleted volunteer" in response.lower()
    assert not pending_actions.has_deletion(sender)

def test_process_registration_response_register_skip(registration_handler, pending_actions):
    sender = "+1234567890"
    pending_actions.set_registration(sender, "register")
    parsed = make_parsed_message("skip")
    response = registration_handler.process_registration_response(parsed, sender)
    # Expect anonymous registration for "skip" input
    assert "registered volunteer anonymous" in response.lower()
    assert not pending_actions.has_registration(sender)

def test_process_registration_response_edit_with_name(registration_handler, pending_actions):
    sender = "+1234567890"
    pending_actions.set_registration(sender, "edit")
    parsed = make_parsed_message("New Name")
    response = registration_handler.process_registration_response(parsed, sender)
    assert "registered volunteer new name" in response.lower()
    assert not pending_actions.has_registration(sender)

# End of tests/managers/test_message_handler.py