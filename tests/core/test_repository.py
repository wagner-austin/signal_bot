#!/usr/bin/env python
"""
File: tests/core/test_repository.py
-----------------------------------
Tests for the Data Access Layer repository classes.
This module verifies that the common CRUD operations provided by the BaseRepository
and its subclasses (ResourceRepository, DonationRepository, EventRepository, and EventSpeakerRepository)
work as expected. Also includes coverage for StatsRepository usage.
"""

import os
import shutil
import pytest
from db.repository import (
    ResourceRepository,
    DonationRepository,
    EventRepository,
    EventSpeakerRepository,
    StatsRepository
)
from db.resources import list_resources
from db.donations import add_donation
from db.connection import get_connection

# Ensure a clean backup of the database state for repository tests
@pytest.fixture(autouse=True)
def clear_tables():
    conn = get_connection()
    cursor = conn.cursor()
    # Clear tables used in our repository tests.
    tables = ["Resources", "Donations", "Events", "EventSpeakers", "Volunteers", "CommandLogs"]
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
    yield
    conn = get_connection()
    cursor = conn.cursor()
    for table in tables:
        cursor.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()

def test_resource_repository_crud():
    repo = ResourceRepository()
    # Create a resource record.
    data = {"category": "Linktree", "title": "Official Linktree", "url": "https://linktr.ee/50501oc"}
    resource_id = repo.create(data)
    # Verify a valid id is returned.
    assert resource_id > 0

    # Retrieve the record.
    record = repo.get_by_id(resource_id)
    assert record is not None
    assert record["title"] == "Official Linktree"

    # Update the record.
    repo.update(resource_id, {"title": "Updated Linktree"})
    updated_record = repo.get_by_id(resource_id)
    assert updated_record["title"] == "Updated Linktree"

    # List all records with filter.
    records = repo.list_all(filters={"category": "Linktree"})
    assert any(r["id"] == resource_id for r in records)

    # Delete the record.
    repo.delete(resource_id)
    deleted = repo.get_by_id(resource_id)
    assert deleted is None

def test_donation_repository_crud():
    repo = DonationRepository()
    # Create a donation record.
    data = {
        "phone": "+9999999999",
        "amount": 50.0,
        "donation_type": "cash",
        "description": "Test cash donation"
    }
    donation_id = repo.create(data)
    # Verify valid id.
    assert donation_id > 0

    # Retrieve the donation.
    record = repo.get_by_id(donation_id)
    assert record is not None
    assert record["amount"] == 50.0

    # Update the donation.
    repo.update(donation_id, {"description": "Updated donation"})
    updated = repo.get_by_id(donation_id)
    assert "Updated donation" in updated["description"]

    # Delete by conditions.
    repo.delete(donation_id)
    assert repo.get_by_id(donation_id) is None

def test_event_repository_crud():
    repo = EventRepository()
    # Create an event.
    data = {
        "title": "Test Event",
        "date": "2025-03-09",
        "time": "2-4PM",
        "location": "Test Location",
        "description": "Test Description"
    }
    event_id = repo.create(data)
    assert event_id > 0

    # Retrieve event.
    event = repo.get_by_id(event_id)
    assert event is not None
    assert event["title"] == "Test Event"

    # Update event.
    repo.update(event_id, {"title": "Updated Test Event"})
    updated_event = repo.get_by_id(event_id)
    assert updated_event["title"] == "Updated Test Event"

    # List events ordered by created_at (should contain our event).
    events = repo.list_all(order_by="created_at DESC")
    assert any(e["event_id"] == event_id for e in events)

    # Delete event.
    repo.delete(event_id)
    assert repo.get_by_id(event_id) is None

def test_event_speaker_repository_delete_by_conditions():
    repo = EventSpeakerRepository()
    # Create two speaker records for the same event.
    data1 = {"event_id": 1, "speaker_name": "Speaker One", "speaker_topic": "Topic A"}
    data2 = {"event_id": 1, "speaker_name": "Speaker Two", "speaker_topic": "Topic B"}
    id1 = repo.create(data1)
    id2 = repo.create(data2)
    assert id1 > 0 and id2 > 0

    # Verify both exist.
    speakers = repo.list_all(filters={"event_id": 1})
    assert len(speakers) >= 2

    # Delete speaker with name "Speaker One" using delete_by_conditions.
    repo.delete_by_conditions({"event_id": 1, "speaker_name": "Speaker One"})
    speakers_after = repo.list_all(filters={"event_id": 1})
    names = [s["speaker_name"] for s in speakers_after]
    assert "Speaker One" not in names
    assert "Speaker Two" in names

def test_stats_repository_usage():
    """
    Tests the StatsRepository functionality by verifying table names, row counts, and schema version logic.
    """
    from db.repository import StatsRepository
    from db.connection import get_connection

    # Insert some records in Volunteers, CommandLogs
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Volunteers (phone, name, skills, available, current_role) VALUES (?, ?, ?, ?, ?)",
                   ("+10000000001", "StatTest Volunteer", "SkillTest", 1, None))
    cursor.execute("INSERT INTO CommandLogs (sender, command, args) VALUES (?, ?, ?)",
                   ("+9999999999", "test_cmd", "arg1"))
    conn.commit()
    conn.close()

    stats_repo = StatsRepository()
    table_names = stats_repo.get_table_names()

    # Confirm table_names is a list
    assert isinstance(table_names, list), "Expected a list of table names."

    # The row count for Volunteers should reflect 1 inserted row if it's not excluded
    if "Volunteers" in table_names:
        row_count = stats_repo.get_row_count("Volunteers")
        assert row_count == 1, f"Expected 1 row in Volunteers, got {row_count}."

    # Check schema version - it may be None if no table or any int >= 0 if we have versioning
    schema_version = stats_repo.get_schema_version()
    # We allow any nonnegative integer or None
    allowed = (schema_version is None) or (schema_version >= 0)
    assert allowed, f"Unexpected schema version: {schema_version}"

# End of tests/core/test_repository.py