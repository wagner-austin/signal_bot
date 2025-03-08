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
    """
    Test signing up volunteers and verifying their status.
    Uses parametrization for different phone/name/skills combos.
    """
    result = VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    assert "registered" in result.lower() or "updated" in result.lower()
    status = VOLUNTEER_MANAGER.volunteer_status()
    assert expected_substring in status


@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+10000000002", "Jane Smith", ["Greeter"]),
        ("+10000000008", "Tom Tester", ["AnySkill"]),
    ]
)
def test_check_in(phone, name, skills):
    """
    Test checking in a volunteer with multiple scenarios.
    """
    VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    result = VOLUNTEER_MANAGER.check_in(phone)
    assert "checked in" in result.lower()


@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+10000000003", "Alice Johnson", ["Logistics Oversight"]),
        ("+10000000009", "Another Person", ["SomeSkill"]),
    ]
)
def test_delete_volunteer(phone, name, skills):
    """
    Test deleting volunteers using parametrization for multiple phone/name combos.
    """
    VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    result = VOLUNTEER_MANAGER.delete_volunteer(phone)
    assert "deleted" in result.lower()
    record = get_volunteer_record(phone)
    assert record is None


@pytest.mark.parametrize(
    "phone, volunteer_name, skill_list, is_available, role",
    [
        ("+10000000004", "Test Volunteer", ["SkillX"], False, "Tester"),
        ("+10000000010", "Another Volunteer", ["SkillA", "SkillB"], True, "Coordinator"),
    ]
)
def test_sign_up_with_availability_and_role(phone, volunteer_name, skill_list, is_available, role):
    """
    Tests that sign_up correctly handles availability and role for different volunteers.
    """
    # Create a new volunteer with the specified availability and role
    result_create = VOLUNTEER_MANAGER.sign_up(phone, volunteer_name, skill_list, is_available, role)
    assert "registered" in result_create.lower()

    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == volunteer_name
    for skl in skill_list:
        assert skl in record["skills"]
    assert record["available"] == is_available
    assert record["current_role"] == role

    # Update the volunteer with an additional skill, to ensure union behavior
    new_skill = ["ExtraSkill"]
    result_update = VOLUNTEER_MANAGER.sign_up(phone, volunteer_name + " Updated", new_skill, not is_available, role)
    # Expect an update message (the message should indicate the volunteer was updated).
    assert "updated" in result_update.lower()

    updated_record = get_volunteer_record(phone)
    assert updated_record is not None
    assert updated_record["name"] == volunteer_name + " Updated"
    # Check that old and new skills are present (union).
    for skl in (skill_list + new_skill):
        assert skl in updated_record["skills"]
    # Invert the availability (since we toggled).
    assert updated_record["available"] == (not is_available)
    # Role remains the same
    assert updated_record["current_role"] == role

# End of tests/managers/test_volunteer_manager.py