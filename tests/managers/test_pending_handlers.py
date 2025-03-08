#!/usr/bin/env python
"""
tests/managers/test_pending_handlers.py
---------------------------------------
Tests for pending action handlers, including concurrency checks for event creation.
"""

import logging
import pytest
import concurrent.futures
from managers.message.pending_handlers import (
    DeletionPendingHandler, RegistrationPendingHandler, EventCreationPendingHandler
)
from parsers.message_parser import ParsedMessage
from core.messages import (DELETION_CONFIRM_PROMPT, ALREADY_REGISTERED,
                           DELETION_CANCELED, EDIT_PROMPT, EDIT_CANCELED, EDIT_CANCELED_WITH_NAME)
from managers.pending_actions import PENDING_ACTIONS

logger = logging.getLogger(__name__)

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
    assert "registered as Anonymous" in response

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

def _create_dummy_event(handler, sender: str, body: str):
    """Helper function for concurrency test."""
    parsed = ParsedMessage(
        sender=sender,
        body=body,
        timestamp=123,
        group_id=None,
        reply_to=None,
        message_timestamp=None,
        command=None,
        args=None
    )
    return handler.process_event_creation_response(parsed, sender)

def test_concurrent_event_creation_handler():
    """
    Tests concurrency for EventCreationPendingHandler by simulating multiple
    users concurrently sending partial or invalid event details.
    Ensures no data corruption or unhandled exceptions occur.
    """
    # Prepare the handler
    handler = EventCreationPendingHandler(PENDING_ACTIONS)

    # We'll simulate 5 different users, some providing valid data, some partial, some 'cancel'.
    test_data = {
        "+userA": "Title: A, Date: 2025-10-10, Time: 10AM, Location: Park, Description: Fun day",
        "+userB": "cancel",
        "+userC": "Title: MissingFields, Time: 10AM",  # incomplete
        "+userD": "skip",  # also a cancellation
        "+userE": "Title: E, Date: 2025-11-11, Time: 2PM, Location: Beach, Description: Cleanup"
    }

    # First, mark each user as having event creation pending:
    for sender in test_data.keys():
        PENDING_ACTIONS.set_event_creation(sender)

    results = {}
    # Now run them concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(test_data)) as executor:
        future_to_sender = {
            executor.submit(_create_dummy_event, handler, sender, body): sender
            for sender, body in test_data.items()
        }
        for future in concurrent.futures.as_completed(future_to_sender):
            s = future_to_sender[future]
            try:
                results[s] = future.result()
            except Exception as e:
                results[s] = str(e)

    # Verify each result is either cancellation, success, or partial fields message.
    for sender, response in results.items():
        if sender in ["+userB", "+userD"]:
            # Both provided "cancel" or "skip"
            assert "cancel" in response.lower()
        elif sender == "+userC":
            # Incomplete fields
            assert "missing one or more required fields" in response.lower()
        else:
            # Should be success with event creation
            # The message is something like "Event 'A' created successfully with ID 7."
            # When lowercased, it's "event 'a' created successfully with id 7."
            assert "created successfully with id" in response.lower() or "cancelled" in response.lower()

# End of tests/managers/test_pending_handlers.py