#!/usr/bin/env python
"""
tests/managers/test_volunteer_operations.py - Tests for volunteer operations.
Verifies register_volunteer, delete_volunteer, check_in, and registration without role functionalities.
Now updated to assert raised VolunteerError for invalid operations.
"""

import pytest
import logging
from managers.volunteer.volunteer_operations import register_volunteer, delete_volunteer, check_in
from core.database.volunteers import get_volunteer_record
from core.exceptions import VolunteerError  # New import for error handling

@pytest.mark.parametrize(
    "phone, name, skills, available, current_role",
    [
        ("+40000000001", "Test Volunteer Ops A", ["Skill1"], True, "Tester"),
        ("+40000000002", "Test Volunteer Ops B", ["Skill2", "Skill3"], False, None),
    ]
)
def test_register_volunteer_creates_volunteer(phone, name, skills, available, current_role):
    """
    Test that register_volunteer creates volunteers with multiple sets of parameters.
    """
    # Ensure volunteer isn't already registered
    record = get_volunteer_record(phone)
    if record:
        delete_volunteer(phone)

    msg = register_volunteer(phone, name, skills, available, current_role)
    assert "registered" in msg.lower()

    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == name
    # Check skill presence
    for s in skills:
        assert s in record["skills"]
    assert record["available"] == available
    assert record["current_role"] == current_role

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+40000000010", "To Be Deleted1", ["SkillDel"]),
        ("+40000000011", "To Be Deleted2", ["SkillX", "SkillY"]),
    ]
)
def test_delete_volunteer(phone, name, skills, caplog):
    """
    Test deleting volunteers using parametrization for multiple phone/name combos.
    Added caplog usage to ensure volunteer deletion logs an info message.
    """
    register_volunteer(phone, name, skills)
    with caplog.at_level(logging.INFO):
        msg = delete_volunteer(phone)
    assert "deleted" in msg.lower()
    record = get_volunteer_record(phone)
    assert record is None

    # Verify we logged an info-level message about deletion
    assert any("deleted from the system" in rec.message for rec in caplog.records), (
        "Expected an info-level log indicating volunteer record was deleted."
    )

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+40000000003", "CheckIn Volunteer A", ["SkillCheck"]),
        ("+40000000004", "CheckIn Volunteer B", ["SkillA"]),
    ]
)
def test_check_in_volunteer(phone, name, skills):
    """
    Test checking in volunteers using multiple test sets.
    """
    register_volunteer(phone, name, skills, False, None)
    msg = check_in(phone)
    assert "checked in" in msg.lower()
    record = get_volunteer_record(phone)
    assert record["available"] is True

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+40000000005", "EmptyRole A", ["SkillA"]),
        ("+40000000006", "EmptyRole B", ["SkillB", "SkillC"]),
    ]
)
def test_register_volunteer_with_empty_role(phone, name, skills):
    """
    Test that an empty role string leads to no assigned preferred_role for volunteers.
    """
    msg = register_volunteer(phone, name, skills, True, "")
    assert "registered" in msg.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    # Verify that current_role/preferred_role is None when an empty role is provided.
    assert record.get("current_role") is None

@pytest.mark.parametrize(
    "invalid_phone",
    [
        "",               # empty
        "abc",            # not numeric
        "+1 234567",      # space in middle
        "+1234567890123456",  # 16 digits (beyond the 15 max)
        "123456"          # 6 digits (less than the 7 required)
    ]
)
def test_register_volunteer_invalid_phone(invalid_phone):
    """
    Test that register_volunteer raises VolunteerError if phone is invalid or empty.
    """
    name = "Invalid Phone"
    skills = ["SkillX"]
    with pytest.raises(VolunteerError, match="Invalid phone number format"):
        register_volunteer(invalid_phone, name, skills, True, None)

@pytest.mark.parametrize(
    "phone",
    [
        ("+40000000007"),
        ("+40000000008"),
    ]
)
def test_delete_unregistered_volunteer(phone):
    """
    Confirm that attempting to delete an unregistered volunteer raises VolunteerError.
    """
    with pytest.raises(VolunteerError, match="not registered"):
        delete_volunteer(phone)

# End of tests/managers/test_volunteer_operations.py