#!/usr/bin/env python
"""
tests/managers/test_volunteer_roles.py - Tests for volunteer role management.
Verifies list_roles, assign_role, switch_role, and unassign_role functionalities.
Now also includes coverage for case-insensitive skill matching and a dynamic approach
to ensure all recognized roles can be assigned if the volunteer has the required skills.
"""

import pytest
from managers.volunteer.volunteer_roles import list_roles, assign_role, switch_role, unassign_role, ROLE_SKILL_REQUIREMENTS
from core.database.volunteers import add_volunteer_record, get_volunteer_record

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
    # Create a volunteer with partial skill requirements for a recognized role.
    add_volunteer_record(phone, "Role Volunteer", ["communication", "interpersonal"], True, None)
    # Assign the role "greeter" (requires communication + interpersonal).
    response_assign = assign_role(phone, "greeter")
    # Updated assertion to fully lowercase both sides.
    assert "your preferred role has been set" in response_assign.lower(), (
        f"Expected assignment confirmation in response, got: {response_assign}"
    )

    record = get_volunteer_record(phone)
    assert record["preferred_role"] == "greeter"

    # Switch role to "emcee" (requires public speaking + communication).
    # This should fail because the volunteer lacks "public speaking".
    response_switch = switch_role(phone, "emcee")
    assert "do not have the necessary skills" in response_switch.lower()

    # Now unassign role entirely:
    response_unassign = unassign_role(phone)
    assert "cleared" in response_unassign.lower()
    record = get_volunteer_record(phone)
    assert record["preferred_role"] is None

def test_assign_role_case_insensitive_skills():
    """
    Test that role assignment succeeds even if the volunteer's required skills are in different cases.
    For example, 'Communication' and 'INTERPERSONAL' should match the needed 'communication' + 'interpersonal'.
    """
    phone = "+60000000002"
    # The "greeter" role requires 'communication' and 'interpersonal'.
    # We'll store them in mixed case to verify case-insensitive matching.
    add_volunteer_record(phone, "CaseTest Volunteer", ["Communication", "INTERPERSONAL"], True, None)
    response = assign_role(phone, "greeter")
    assert "your preferred role has been set to 'greeter'." in response.lower()
    record = get_volunteer_record(phone)
    assert record["preferred_role"] == "greeter"

@pytest.mark.parametrize("role, required_skills", list(ROLE_SKILL_REQUIREMENTS.items()))
def test_dynamic_role_assignment(role, required_skills):
    """
    Test that each recognized role in ROLE_SKILL_REQUIREMENTS can be assigned if the volunteer
    has the appropriate skills (in uppercase). Verifies coverage for newly added roles, too.
    """
    phone = f"+600000001{hash(role) % 9999}"
    # Convert required_skills to uppercase to confirm assignment remains case-insensitive.
    uppercased_skills = [skill.upper() for skill in required_skills]
    add_volunteer_record(phone, f"DynamicTest {role}", uppercased_skills, True, None)
    response = assign_role(phone, role)
    # If a role has no required skills, it should trivially succeed. Otherwise it should also succeed.
    assert "your preferred role has been set to" in response.lower(), (
        f"Expected successful assignment for role '{role}', but got: {response}"
    )
    record = get_volunteer_record(phone)
    assert record["preferred_role"] == role, (
        f"Expected assigned role '{role}', got '{record.get('preferred_role')}'"
    )

# End of tests/managers/test_volunteer_roles.py