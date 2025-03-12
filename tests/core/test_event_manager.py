#!/usr/bin/env python
"""
tests/core/test_event_manager.py --- Test for core/event_manager.py.
Verifies event CRUD and speaker management functions using the event manager functions.
"""

import pytest
import logging
from core.event_manager import (
    create_event, update_event, list_events, get_event,
    delete_event, assign_speaker, list_speakers, remove_speaker
)

def test_create_and_get_event(caplog):
    with caplog.at_level(logging.INFO):
        event_id = create_event("Unit Test Event", "2025-03-09", "2-4PM", "Test Venue", "Test Description")
    assert event_id > 0
    event = get_event(event_id)
    assert event is not None
    assert event.get("title") == "Unit Test Event"

    # Confirm we logged an info-level message about event creation
    assert any("Event created with ID" in rec.message for rec in caplog.records), (
        "Expected an info-level log indicating event was created."
    )

def test_update_event():
    event_id = create_event("Old Event", "2025-03-09", "2-4PM", "Test Venue", "Old Description")
    update_event(event_id, title="Updated Event", description="Updated Description")
    event = get_event(event_id)
    assert event.get("title") == "Updated Event"
    assert event.get("description") == "Updated Description"

def test_list_and_delete_event():
    event_id = create_event("Event to Delete", "2025-03-09", "2-4PM", "Test Venue", "Description")
    events = list_events()
    assert any(e.get("event_id") == event_id for e in events)
    delete_event(event_id)
    assert get_event(event_id) is None

def test_assign_list_remove_speaker():
    event_id = create_event("Event with Speakers", "2025-03-09", "2-4PM", "Test Venue", "Description")
    assign_speaker(event_id, "Speaker One", "Topic A")
    assign_speaker(event_id, "Speaker Two", "Topic B")
    speakers = list_speakers(event_id)
    names = [s.get("speaker_name") for s in speakers]
    assert "Speaker One" in names and "Speaker Two" in names
    remove_speaker(event_id, "Speaker One")
    speakers_after = list_speakers(event_id)
    names_after = [s.get("speaker_name") for s in speakers_after]
    assert "Speaker One" not in names_after
    delete_event(event_id)

# End of tests/core/test_event_manager.py