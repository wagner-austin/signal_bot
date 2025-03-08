#!/usr/bin/env python
"""
tests/managers/test_volunteer_operations.py - Tests for volunteer operations.
Verifies sign_up, delete_volunteer, check_in, and registration without role functionalities.
"""

import pytest
from managers.volunteer.volunteer_operations import sign_up, delete_volunteer, check_in
from core.database.volunteers import get_volunteer_record

def test_sign_up_creates_volunteer():
    phone = "+40000000001"
    # Ensure the volunteer is not already registered
    record = get_volunteer_record(phone)
    if record:
        delete_volunteer(phone)
    msg = sign_up(phone, "Test Volunteer Ops", ["Skill1"], True, "Tester")
    assert "registered" in msg.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == "Test Volunteer Ops"

def test_delete_volunteer():
    phone = "+40000000002"
    sign_up(phone, "To Be Deleted", ["SkillDel"], True, None)
    msg = delete_volunteer(phone)
    assert "deleted" in msg.lower()
    record = get_volunteer_record(phone)
    assert record is None

def test_check_in_volunteer():
    phone = "+40000000003"
    sign_up(phone, "CheckIn Volunteer", ["SkillCheck"], False, None)
    msg = check_in(phone)
    assert "checked in" in msg.lower()
    record = get_volunteer_record(phone)
    assert record["available"] is True

def test_sign_up_with_empty_role():
    """
    Test that if an empty string is provided as the role,
    the volunteer is registered without any role assigned.
    """
    phone = "+40000000004"
    msg = sign_up(phone, "No Role Volunteer", ["SkillA"], True, "")
    assert "registered" in msg.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    # Verify that preferred_role is None when an empty role is provided.
    assert record.get("preferred_role") is None

# End of tests/managers/test_volunteer_operations.py