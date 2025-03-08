#!/usr/bin/env python
"""
test_role_command.py
--------------------
Tests the role command plugin for normal role operations: listing roles, successful set/switch/unassign.
Negative/edge cases are now in test_plugin_negatives.py.
"""

import pytest
from core.state import BotStateMachine
from managers.volunteer.volunteer_operations import sign_up
from managers.volunteer.volunteer_roles import get_volunteer_record
from plugins.commands.role import role_command

def call_role_command(command_args, sender, state_machine):
    return role_command(command_args, sender, state_machine, msg_timestamp=123)

@pytest.fixture
def state_machine():
    return BotStateMachine()

def test_role_list_command(state_machine):
    response = call_role_command("list", "+70000000010", state_machine)
    assert "greeter" in response.lower() or "speaker coordinator" in response.lower()

def test_role_set_command_success(state_machine):
    sender = "+70000000011"
    # Register volunteer with required skills for "greeter": communication + interpersonal
    sign_up(sender, "Role Tester", ["communication", "interpersonal"], True, None)
    response = call_role_command("set greeter", sender, state_machine)
    assert "preferred role has been set to 'greeter'" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") == "greeter"

def test_role_switch_command_success(state_machine):
    sender = "+70000000013"
    # Register a volunteer with enough skills for both greeter + emcee
    sign_up(sender, "Role Tester 3", ["communication", "interpersonal", "public speaking"], True, "greeter")
    response = call_role_command("switch emcee", sender, state_machine)
    assert "switching from 'greeter' to 'emcee'" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") == "emcee"

def test_role_unassign_command(state_machine):
    sender = "+70000000014"
    sign_up(sender, "Role Tester 4", ["communication", "interpersonal"], True, "greeter")
    response = call_role_command("unassign", sender, state_machine)
    assert "cleared" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") is None

# End of tests/plugins/commands/test_role_command.py