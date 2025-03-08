#!/usr/bin/env python
"""
tests/managers/test_volunteer_operations.py - Tests for volunteer operations.
Verifies sign_up, delete_volunteer, check_in, and registration without role functionalities,
now covered with multiple parametrized inputs.
"""

import pytest
from managers.volunteer.volunteer_operations import sign_up, delete_volunteer, check_in
from core.database.volunteers import get_volunteer_record


@pytest.mark.parametrize(
    "phone, name, skills, available, current_role",
    [
        ("+40000000001", "Test Volunteer Ops A", ["Skill1"], True, "Tester"),
        ("+40000000002", "Test Volunteer Ops B", ["Skill2", "Skill3"], False, None),
    ]
)
def test_sign_up_creates_volunteer(phone, name, skills, available, current_role):
    """
    Tests that sign_up creates volunteers with multiple sets of parameters.
    """
    # Ensure volunteer isn't already registered
    record = get_volunteer_record(phone)
    if record:
        delete_volunteer(phone)

    msg = sign_up(phone, name, skills, available, current_role)
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
def test_delete_volunteer(phone, name, skills):
    """
    Test deleting multiple volunteers in a single parameterized test.
    """
    sign_up(phone, name, skills)
    msg = delete_volunteer(phone)
    assert "deleted" in msg.lower()
    record = get_volunteer_record(phone)
    assert record is None


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
    sign_up(phone, name, skills, False, None)
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
def test_sign_up_with_empty_role(phone, name, skills):
    """
    Test that an empty role string leads to no assigned preferred_role for volunteers.
    """
    msg = sign_up(phone, name, skills, True, "")
    assert "registered" in msg.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    # Verify that current_role/preferred_role is None when an empty role is provided.
    assert record.get("current_role") is None


@pytest.mark.parametrize(
    "phone",
    [
        ("+40000000007"),
        ("+40000000008"),
    ]
)
def test_delete_unregistered_volunteer(phone):
    """
    Confirm that attempting to delete an unregistered volunteer returns a user-friendly message.
    """
    msg = delete_volunteer(phone)
    assert msg == "You are not registered."

# End of tests/managers/test_volunteer_operations.py