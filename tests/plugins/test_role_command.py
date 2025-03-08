#!/usr/bin/env python
"""
tests/plugins/test_role_command.py - Unit tests for role command plugin.
Tests the functionalities of listing roles, setting, switching, and unassigning volunteer roles.
"""

import pytest
from core.state import BotStateMachine
from managers.volunteer.volunteer_operations import sign_up
from managers.volunteer.volunteer_roles import get_volunteer_record
from plugins.commands.role import role_command

# Helper function to simulate calling the role command.
def call_role_command(command_args, sender, state_machine):
    # role_command takes args, sender, state_machine, and msg_timestamp.
    return role_command(command_args, sender, state_machine, msg_timestamp=123)

@pytest.fixture
def state_machine():
    return BotStateMachine()

def test_role_list_command(state_machine):
    # Test "role list" command: it should list recognized roles.
    response = call_role_command("list", "+70000000010", state_machine)
    # Expect response to contain at least one of the recognized role keywords.
    assert "greeter" in response.lower() or "speaker coordinator" in response.lower()

def test_role_set_command_success(state_machine):
    # Test "role set greeter" command with valid skills.
    sender = "+70000000011"
    # Register a volunteer with the required skills for "greeter": "communication", "interpersonal"
    sign_up(sender, "Role Tester", ["communication", "interpersonal"], True, None)
    response = call_role_command("set greeter", sender, state_machine)
    assert "preferred role has been set to 'greeter'" in response.lower()
    record = get_volunteer_record(sender)
    assert record is not None
    assert record.get("preferred_role") == "greeter"

def test_role_set_command_failure(state_machine):
    # Test "role set emcee" command with missing required skills.
    sender = "+70000000012"
    # Register a volunteer without the required skills for "emcee" (needs "public speaking", "communication")
    sign_up(sender, "Role Tester 2", ["interpersonal"], True, None)
    response = call_role_command("set emcee", sender, state_machine)
    # Expect an error message about missing necessary skills.
    assert "do not have the necessary skills" in response.lower()
    record = get_volunteer_record(sender)
    # The preferred role should remain unset.
    assert record is not None
    assert record.get("preferred_role") is None

def test_role_switch_command_success(state_machine):
    # Test "role switch" command for a volunteer who already has a role.
    sender = "+70000000013"
    # Register a volunteer with skills for both "greeter" and "emcee"
    sign_up(sender, "Role Tester 3", ["communication", "interpersonal", "public speaking"], True, "greeter")
    response = call_role_command("switch emcee", sender, state_machine)
    # Expect a message indicating a successful role switch.
    assert "switching from 'greeter' to 'emcee'" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") == "emcee"

def test_role_unassign_command(state_machine):
    # Test "role unassign" command to clear the volunteer's role.
    sender = "+70000000014"
    # Register a volunteer with a role.
    sign_up(sender, "Role Tester 4", ["communication", "interpersonal"], True, "greeter")
    response = call_role_command("unassign", sender, state_machine)
    assert "preferred role has been cleared" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") is None

# End of tests/plugins/test_role_command.py