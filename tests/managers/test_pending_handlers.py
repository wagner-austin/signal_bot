#!/usr/bin/env python
"""
tests/managers/test_pending_handlers.py - Tests for pending action handlers.
Verifies deletion, registration, and event creation pending handler responses.
"""
import pytest
from managers.message.pending_handlers import DeletionPendingHandler, RegistrationPendingHandler, EventCreationPendingHandler
from parsers.message_parser import ParsedMessage
from core.messages import DELETION_CONFIRM_PROMPT, ALREADY_REGISTERED, DELETION_CANCELED, EDIT_PROMPT, EDIT_CANCELED_WITH_NAME
from managers.pending_actions import PENDING_ACTIONS

# Create a dummy volunteer manager with minimal functionality.
class DummyVolunteerManager:
    def delete_volunteer(self, sender):
        return "Volunteer deleted."
    def sign_up(self, sender, name, skills, available=True, current_role=None):
        return f"Volunteer registered as {name}."

def create_parsed_message(body):
    return ParsedMessage(
        sender="+70000000001",
        body=body,
        timestamp=123,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command=None,
        args=None
    )

def test_deletion_pending_handler_confirm():
    # Set initial deletion state.
    PENDING_ACTIONS.set_deletion("+70000000001", "initial")
    handler = DeletionPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("yes")
    response = handler.process_deletion_response(parsed, "+70000000001")
    assert response == DELETION_CONFIRM_PROMPT

def test_deletion_pending_handler_cancel():
    PENDING_ACTIONS.set_deletion("+70000000002", "initial")
    handler = DeletionPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("no")
    response = handler.process_deletion_response(parsed, "+70000000002")
    # Should return deletion canceled or already registered message.
    assert "cancel" in response.lower() or "registered" in response.lower()

def test_registration_pending_handler_skip():
    # Test registration with skip input.
    PENDING_ACTIONS.set_registration("+70000000003", "register")
    handler = RegistrationPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("skip")
    response = handler.process_registration_response(parsed, "+70000000003")
    assert "registered as" in response.lower()

def test_registration_pending_handler_change_name():
    # Test edit registration with a valid name.
    PENDING_ACTIONS.set_registration("+70000000004", "edit")
    handler = RegistrationPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("New Name")
    response = handler.process_registration_response(parsed, "+70000000004")
    assert "registered as New Name" in response

def test_event_creation_pending_handler_cancel():
    # Test event creation cancellation.
    PENDING_ACTIONS.set_event_creation("+70000000005")
    handler = EventCreationPendingHandler(PENDING_ACTIONS)
    parsed = create_parsed_message("cancel")
    response = handler.process_event_creation_response(parsed, "+70000000005")
    assert "cancelled" in response.lower()

# End of tests/managers/test_pending_handlers.py