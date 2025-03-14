#!/usr/bin/env python
"""
tests/managers/test_volunteer_roles.py - Tests for volunteer role management.
Verifies list_roles, assign_role, switch_role, and unassign_role functionalities.
Also includes tests for case-insensitive matching, dynamic role assignment, and incomplete skill coverage using exception assertions.
"""

import pytest
from managers.volunteer_manager import list_roles, assign_role, switch_role, unassign_role, ROLE_SKILL_REQUIREMENTS
from db.volunteers import add_volunteer_record, get_volunteer_record
from core.exceptions import VolunteerError

def test_list_roles():
    """
    Test that list_roles returns a non-empty list of roles with their required skills.
    """
    roles = list_roles()
    assert isinstance(roles, list)
    assert len(roles) > 0

def test_assign_and_switch_and_unassign_role():
    """
    Test a simple flow of assigning a recognized role, attempting to switch to another,
    and finally unassigning the role.
    """
    phone = "+60000000001"
    # Create a volunteer with the required skills for "greeter"
    add_volunteer_record(phone, "Role Volunteer", ["communication", "interpersonal"], True, None)
    # Assign the role "greeter"
    response_assign = assign_role(phone, "greeter")
    assert "your preferred role has been set" in response_assign.lower()

    record = get_volunteer_record(phone)
    assert record["preferred_role"] == "greeter"

    # Attempt to switch role to "emcee" which requires an additional skill ("public speaking")
    with pytest.raises(VolunteerError, match="do not have the necessary skills"):
        switch_role(phone, "emcee")

    # Now unassign role entirely:
    response_unassign = unassign_role(phone)
    assert "cleared" in response_unassign.lower()
    record = get_volunteer_record(phone)
    assert record["preferred_role"] is None

def test_assign_role_case_insensitive_skills():
    """
    Test that role assignment succeeds even if the volunteer's skills are in different cases.
    """
    phone = "+60000000002"
    add_volunteer_record(phone, "CaseTest Volunteer", ["Communication", "INTERPERSONAL"], True, None)
    response = assign_role(phone, "greeter")
    assert "your preferred role has been set" in response.lower()
    record = get_volunteer_record(phone)
    assert record["preferred_role"] == "greeter"

@pytest.mark.parametrize("role, skills, expect_error", [
    ("greeter", ["communication"], True),  # Incomplete: missing 'interpersonal'
    ("greeter", ["communication", "interpersonal"], False),  # Complete
    ("emcee", ["public speaking"], True),  # Incomplete: missing 'communication'
    ("emcee", ["public speaking", "communication", "extra"], False),  # Complete even with extra skill
])
def test_role_assignment_incomplete_skills(role, skills, expect_error):
    """
    Test that a volunteer with an incomplete skill set for a recognized role raises VolunteerError,
    while a volunteer with all required skills is correctly assigned.
    """
    phone = f"+60000000{abs(hash(role + str(skills))) % 100:02d}"
    add_volunteer_record(phone, "Incomplete Skill Volunteer", skills, True, None)
    if expect_error:
        with pytest.raises(VolunteerError, match="do not have the necessary skills"):
            assign_role(phone, role)
    else:
        response = assign_role(phone, role)
        assert "your preferred role has been set" in response.lower()
        record = get_volunteer_record(phone)
        assert record["preferred_role"] == role

@pytest.mark.parametrize("role, required_skills", list(ROLE_SKILL_REQUIREMENTS.items()))
def test_dynamic_role_assignment(role, required_skills):
    """
    Test that each recognized role can be assigned if the volunteer has the appropriate skills (even in uppercase).
    """
    phone = f"+600000001{abs(hash(role)) % 9999}"
    uppercased_skills = [skill.upper() for skill in required_skills]
    add_volunteer_record(phone, f"DynamicTest {role}", uppercased_skills, True, None)
    response = assign_role(phone, role)
    assert "your preferred role has been set" in response.lower()
    record = get_volunteer_record(phone)
    assert record["preferred_role"] == role

# End of tests/managers/test_volunteer_roles.py