#!/usr/bin/env python
"""
tests/managers/test_volunteer_manager.py - Tests for aggregated volunteer management functionalities.
Verifies that operations like sign‑up, check‑in, deletion, status retrieval, and role management work correctly.
"""

import pytest
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.database import get_volunteer_record

@pytest.mark.parametrize(
    "phone, name, skills, expected_substring",
    [
        ("+10000000001", "John Doe", ["Public Speaking"], "John Doe"),
        ("+10000000002", "Jane Smith", ["Greeter"], "Jane Smith"),
        ("+10000000003", "Alice Johnson", ["Logistics Oversight"], "Alice Johnson"),
    ]
)
def test_sign_up_and_status(phone, name, skills, expected_substring):
    result = VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    assert "registered" in result.lower() or "updated" in result.lower()
    status = VOLUNTEER_MANAGER.volunteer_status()
    assert expected_substring in status

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+10000000002", "Jane Smith", ["Greeter"]),
    ]
)
def test_check_in(phone, name, skills):
    VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    result = VOLUNTEER_MANAGER.check_in(phone)
    assert "checked in" in result.lower()

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+10000000003", "Alice Johnson", ["Logistics Oversight"]),
    ]
)
def test_delete_volunteer(phone, name, skills):
    VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    result = VOLUNTEER_MANAGER.delete_volunteer(phone)
    assert "deleted" in result.lower()
    record = get_volunteer_record(phone)
    assert record is None

def test_sign_up_with_availability_and_role():
    """
    tests/managers/test_volunteer_manager.py - test_sign_up_with_availability_and_role
    Tests that sign_up correctly creates a volunteer with specified availability and role,
    and then updates the record when called again.
    """
    phone = "+10000000004"
    # Create a new volunteer with available=False and role "Tester"
    result_create = VOLUNTEER_MANAGER.sign_up(phone, "Test Volunteer", ["SkillX"], False, "Tester")
    assert "registered" in result_create.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == "Test Volunteer"
    assert "SkillX" in record["skills"]
    assert record["available"] is False
    assert record["current_role"] == "Tester"
    
    # Update the volunteer with different details.
    result_update = VOLUNTEER_MANAGER.sign_up(phone, "Test Volunteer Updated", ["SkillY"], True, "Coordinator")
    assert "updated" in result_update.lower()
    updated_record = get_volunteer_record(phone)
    assert updated_record is not None
    assert updated_record["name"] == "Test Volunteer Updated"
    # Expect that skills include both SkillX and SkillY (union behavior).
    assert "SkillX" in updated_record["skills"]
    assert "SkillY" in updated_record["skills"]
    assert updated_record["available"] is True
    assert updated_record["current_role"] == "Coordinator"

# End of tests/managers/test_volunteer_manager.py