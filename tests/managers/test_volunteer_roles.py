#!/usr/bin/env python
"""
tests/managers/test_volunteer_roles.py - Tests for volunteer role management.
Verifies list_roles, assign_role, switch_role, and unassign_role functionalities.
"""
from managers.volunteer.volunteer_roles import list_roles, assign_role, switch_role, unassign_role
from core.database.volunteers import add_volunteer_record, get_volunteer_record

def test_list_roles():
    roles = list_roles()
    assert isinstance(roles, list)
    assert len(roles) > 0

def test_assign_and_switch_and_unassign_role():
    phone = "+60000000001"
    # Create a volunteer with no preferred role.
    add_volunteer_record(phone, "Role Volunteer", ["communication", "interpersonal"], True, None)
    # Try to assign a recognized role that requires communication and interpersonal skills, e.g., "greeter"
    response_assign = assign_role(phone, "greeter")
    assert "preferred role has been set" in response_assign.lower()
    record = get_volunteer_record(phone)
    assert record["preferred_role"] == "greeter"
    # Switch role to another valid role, e.g., "emcee" (expected to fail if skills are insufficient)
    response_switch = switch_role(phone, "emcee")
    assert "do not have the necessary skills" in response_switch.lower()
    # Unassign role
    response_unassign = unassign_role(phone)
    assert "cleared" in response_unassign.lower()
    record = get_volunteer_record(phone)
    assert record["preferred_role"] is None

# End of tests/managers/test_volunteer_roles.py