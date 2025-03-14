#!/usr/bin/env python
"""
tests/managers/test_event_manager.py
------------------------------------
Tests for managers/event_manager.py.
Expands coverage by adding partial update checks, negative speaker removal, and a helper fixture for event creation.
"""

import pytest
import logging
from managers.event_manager import (
    create_event, update_event, list_all_events, get_event,
    delete_event, assign_speaker, list_speakers, remove_speaker
)

@pytest.fixture
def create_test_event():
    """
    create_test_event - Fixture that creates a single event and returns its ID for re-use in tests.
    """
    def _create(title="Fixture Event", date="2025-03-09", time="2-4PM",
                location="Test Venue", description="Default Description"):
        return create_event(title, date, time, location, description)
    return _create

def test_create_and_get_event(caplog, create_test_event):
    with caplog.at_level(logging.INFO):
        event_id = create_test_event(title="Unit Test Event", description="Test Description")
    assert event_id > 0
    event = get_event(event_id)
    assert event is not None
    assert event.get("title") == "Unit Test Event"

    # Confirm we logged an info-level message about event creation
    assert any("Event created with ID" in rec.message for rec in caplog.records), (
        "Expected an info-level log indicating event was created."
    )

def test_update_event(create_test_event):
    event_id = create_test_event(title="Old Event", description="Old Description")
    update_event(event_id, title="Updated Event", description="Updated Description")
    event = get_event(event_id)
    assert event.get("title") == "Updated Event"
    assert event.get("description") == "Updated Description"

def test_partial_update_event(create_test_event):
    """
    Tests updating only a single field (location) to ensure partial updates work properly.
    """
    event_id = create_test_event(title="Partial Update Event", location="Initial Venue")
    update_event(event_id, location="New Venue")
    event = get_event(event_id)
    assert event.get("title") == "Partial Update Event"
    assert event.get("location") == "New Venue"

def test_list_and_delete_event(create_test_event):
    event_id = create_test_event(title="Event to Delete")
    events = list_all_events()
    assert any(e.get("event_id") == event_id for e in events)
    delete_event(event_id)
    assert get_event(event_id) is None

def test_assign_list_remove_speaker(create_test_event):
    event_id = create_test_event(title="Event with Speakers")
    assign_speaker(event_id, "Speaker One", "Topic A")
    assign_speaker(event_id, "Speaker Two", "Topic B")
    speakers = list_speakers(event_id)
    names = [s.get("speaker_name") for s in speakers]
    assert "Speaker One" in names and "Speaker Two" in names
    remove_speaker(event_id, "Speaker One")
    speakers_after = list_speakers(event_id)
    names_after = [s.get("speaker_name") for s in speakers_after]
    assert "Speaker One" not in names_after

def test_remove_missing_speaker(create_test_event):
    """
    Attempts to remove a speaker who does not exist on the event.
    Ensures it does not break or raise unexpected errors.
    """
    event_id = create_test_event(title="Event for Missing Speaker")
    # There's no "Ghost Speaker" assigned, so removing them should be a no-op.
    remove_speaker(event_id, "Ghost Speaker")
    speakers_after = list_speakers(event_id)
    # Confirm we didn't add or break anything
    assert len(speakers_after) == 0

# End of tests/managers/test_event_manager.py