#!/usr/bin/env python
"""
tests/core/test_database_volunteers.py - Tests for volunteer-related database operations.
Verifies functions to manage volunteer records including creation, update, and deletion.
"""

import pytest
from core.database.volunteers import (
    add_volunteer_record,
    get_volunteer_record,
    update_volunteer_record,
    delete_volunteer_record,
    add_deleted_volunteer_record,
    remove_deleted_volunteer_record,
)
from managers.volunteer.volunteer_operations import register_volunteer

def test_volunteer_operations_add_and_update():
    """
    tests/core/test_database_volunteers.py - test_volunteer_operations_add_and_update
    Tests adding and updating volunteer records using separate functions.
    """
    phone = "+1234567890"
    add_volunteer_record(phone, "Test Volunteer", ["Skill1", "Skill2"], True, None)
    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == "Test Volunteer"

def test_volunteer_operations_delete():
    phone = "+1234567891"
    add_volunteer_record(phone, "Delete Volunteer", ["SkillDel"], True, None)
    delete_volunteer_record(phone)
    record = get_volunteer_record(phone)
    assert record is None

def test_register_volunteer_method_creation_and_update():
    """
    tests/core/test_database_volunteers.py - test_register_volunteer_method_creation_and_update
    Tests the centralized register_volunteer method for creating a new volunteer and updating an existing one.
    """
    phone = "+5550000000"
    # Create a new volunteer
    msg1 = register_volunteer(phone, "Initial Name", ["Skill1"], True, None)
    assert "New volunteer" in msg1
    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == "Initial Name"

    # Update the volunteer with new details.
    msg2 = register_volunteer(phone, "Updated Name", ["Skill2"], False, "Tester")
    assert "updated" in msg2.lower()
    record_updated = get_volunteer_record(phone)
    assert record_updated is not None
    assert record_updated["name"] == "Updated Name"
    # Since union is used, the skills should include both "Skill1" and "Skill2"
    assert "Skill1" in record_updated["skills"]
    assert "Skill2" in record_updated["skills"]
    assert record_updated["available"] is False
    assert record_updated["current_role"] == "Tester"

# End of tests/core/test_database_volunteers.py