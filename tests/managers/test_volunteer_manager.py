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

def test_volunteer_status_empty():
    # If no volunteer exists, volunteer_status should return an empty string.
    status = VOLUNTEER_MANAGER.volunteer_status()
    assert status == ""

# --- New tests for role management ---

def test_assign_role_without_required_skills():
    phone = "+10000000004"
    # Sign up with a skill that doesn't meet "greeter" requirements.
    VOLUNTEER_MANAGER.sign_up(phone, "Test Role", ["some skill"])
    response = VOLUNTEER_MANAGER.assign_role(phone, "greeter")
    assert "do not have the necessary skills" in response.lower()

def test_assign_role_with_required_skills():
    phone = "+10000000005"
    # Sign up with required skills for "greeter": "communication", "interpersonal"
    VOLUNTEER_MANAGER.sign_up(phone, "Test Greeter", ["communication", "interpersonal"])
    response = VOLUNTEER_MANAGER.assign_role(phone, "greeter")
    assert "preferred role has been set" in response.lower()

def test_switch_role():
    phone = "+10000000006"
    # Sign up with skills that satisfy both "greeter" and "speaker coordinator" roles.
    VOLUNTEER_MANAGER.sign_up(phone, "Test Switch", ["communication", "interpersonal", "organizational"])
    # Assign "greeter" first.
    assign_response = VOLUNTEER_MANAGER.assign_role(phone, "greeter")
    # Now switch to "speaker coordinator" which requires "organizational", "communication".
    switch_response = VOLUNTEER_MANAGER.switch_role(phone, "speaker coordinator")
    assert ("switching" in switch_response.lower() or "preferred role has been set" in switch_response.lower())

def test_unassign_role():
    phone = "+10000000007"
    VOLUNTEER_MANAGER.sign_up(phone, "Test Unassign", ["communication", "interpersonal"])
    VOLUNTEER_MANAGER.assign_role(phone, "greeter")
    unassign_response = VOLUNTEER_MANAGER.unassign_role(phone)
    assert "cleared" in unassign_response.lower()

# End of tests/managers/test_volunteer_manager.py