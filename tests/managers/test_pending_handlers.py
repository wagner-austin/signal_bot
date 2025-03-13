#!/usr/bin/env python
"""
tests/managers/test_pending_handlers.py - Tests for interactive pending action handlers.
Verifies deletion, registration, and event creation flows, including partial instructions when input is incomplete.
"""

import logging
import pytest
import concurrent.futures
from managers.message.pending_handlers import (
    DeletionPendingHandler, RegistrationPendingHandler, EventCreationPendingHandler
)
from parsers.message_parser import ParsedMessage
from core.messages import (
    DELETION_CONFIRM, ALREADY_REGISTERED,
    DELETION_PROMPT, EDIT_PROMPT, EDIT_CANCELED, EDIT_CANCELED_WITH_NAME
)
from managers.pending_actions import PENDING_ACTIONS
from core.plugin_usage import USAGE_REGISTER_PARTIAL, USAGE_PLAN_EVENT_PARTIAL
from core.database import get_volunteer_record

logger = logging.getLogger(__name__)

# Create a dummy volunteer manager with minimal functionality.
class DummyVolunteerManager:
    def delete_volunteer(self, sender):
        return "Volunteer deleted."
    def sign_up(self, sender, name, skills, available=True, current_role=None):
        return f"Volunteer registered as {name}."
    def register_volunteer(self, sender, name, skills, available=True, current_role=None):
        return f"Volunteer registered as {name}."

def create_parsed_message(body, sender="+70000000001"):
    return ParsedMessage(
        sender=sender,
        body=body,
        timestamp=123,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command=None,
        args=None
    )

def test_deletion_pending_handler_confirm():
    PENDING_ACTIONS.set_deletion("+70000000001", "initial")
    handler = DeletionPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("yes", "+70000000001")
    response = handler.process_deletion_response(parsed, "+70000000001")
    # Verify that the deletion confirmation now uses DELETION_CONFIRM
    assert response == DELETION_CONFIRM

def test_deletion_pending_handler_cancel():
    PENDING_ACTIONS.set_deletion("+70000000002", "initial")
    handler = DeletionPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("no", "+70000000002")
    response = handler.process_deletion_response(parsed, "+70000000002")
    assert "cancel" in response.lower() or "registered" in response.lower()

def test_registration_pending_handler_skip():
    PENDING_ACTIONS.set_registration("+70000000003", "register")
    handler = RegistrationPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("skip", "+70000000003")
    response = handler.process_registration_response(parsed, "+70000000003")
    assert "anonymous" in response.lower()

def test_registration_pending_handler_change_name():
    PENDING_ACTIONS.set_registration("+70000000004", "edit")
    handler = RegistrationPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("New Name", "+70000000004")
    response = handler.process_registration_response(parsed, "+70000000004")
    assert "new name" in response.lower()

def test_registration_pending_handler_partial():
    PENDING_ACTIONS.set_registration("+70000000005", "register")
    handler = RegistrationPendingHandler(PENDING_ACTIONS, DummyVolunteerManager())
    parsed = create_parsed_message("John", "+70000000005")  # Incomplete: only one word
    response = handler.process_registration_response(parsed, "+70000000005")
    assert USAGE_REGISTER_PARTIAL.lower() in response.lower()

def test_event_creation_pending_handler_cancel():
    PENDING_ACTIONS.set_event_creation("+70000000006")
    handler = EventCreationPendingHandler(PENDING_ACTIONS)
    parsed = create_parsed_message("cancel", "+70000000006")
    response = handler.process_event_creation_response(parsed, "+70000000006")
    assert "cancelled" in response.lower()

def test_event_creation_pending_handler_missing_fields():
    PENDING_ACTIONS.set_event_creation("+70000000007")
    handler = EventCreationPendingHandler(PENDING_ACTIONS)
    # Provide only Title and Date; missing Time, Location, Description
    parsed = create_parsed_message("Title: Incomplete, Date: 2025-12-31", "+70000000007")
    response = handler.process_event_creation_response(parsed, "+70000000007")
    assert "missing" in response.lower() and USAGE_PLAN_EVENT_PARTIAL.lower() in response.lower()

# End of tests/managers/test_pending_handlers.py