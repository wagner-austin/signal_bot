#!/usr/bin/env python
"""
tests/plugins/test_role_command.py - Tests for the role command plugin.
Verifies listing roles, setting, switching, unassigning operations, and CLI exception handling.
"""

import pytest
from core.state import BotStateMachine
from managers.volunteer.volunteer_operations import register_volunteer
from managers.volunteer.volunteer_roles import get_volunteer_record
from plugins.commands.role import role_command

def call_role_command(command_args, sender, state_machine):
    return role_command(command_args, sender, state_machine, msg_timestamp=123)

def test_role_no_args_shows_recognized_roles():
    """
    Calling role command with no arguments should list recognized roles.
    """
    state_machine = BotStateMachine()
    response = call_role_command("", "+70000000010", state_machine)
    assert "recognized roles:" in response.lower()

def test_role_bogus_subcommand_shows_usage():
    """
    An invalid subcommand returns a usage-like message about valid subcommands.
    """
    state_machine = BotStateMachine()
    response = call_role_command("bogus", "+70000000011", state_machine)
    assert "invalid subcommand for role" in response.lower()

def test_role_list_command():
    """
    Tests listing roles explicitly with 'list'.
    """
    state_machine = BotStateMachine()
    response = call_role_command("list", "+70000000010", state_machine)
    assert "recognized roles:" in response.lower()

def test_role_set_command_success():
    """
    Tests setting a recognized role if the volunteer has the needed skills.
    """
    sender = "+70000000011"
    register_volunteer(sender, "Role Tester", ["communication", "interpersonal"], True, None)
    state_machine = BotStateMachine()
    response = call_role_command("set greeter", sender, state_machine)
    assert "preferred role has been set to 'greeter'" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") == "greeter"

def test_role_switch_command_success():
    """
    Tests switching from one role to another if volunteer has the required skills.
    """
    sender = "+70000000013"
    register_volunteer(sender, "Role Tester 3", ["communication", "interpersonal", "public speaking"], True, "greeter")
    state_machine = BotStateMachine()
    response = call_role_command("switch emcee", sender, state_machine)
    assert "switching from 'greeter' to 'emcee'" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") == "emcee"

def test_role_unassign_command():
    """
    Tests unassigning a role entirely.
    """
    sender = "+70000000014"
    register_volunteer(sender, "Role Tester 4", ["communication", "interpersonal"], True, "greeter")
    state_machine = BotStateMachine()
    response = call_role_command("unassign", sender, state_machine)
    assert "cleared" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") is None

def test_role_command_handles_manager_exception(monkeypatch):
    """
    Tests that the role command catches a manager exception and returns a consistent error message.
    """
    from core.exceptions import VolunteerError
    from core.state import BotStateMachine
    def fake_assign_role(sender, role):
         raise VolunteerError("Simulated role assignment failure")
    monkeypatch.setattr("managers.volunteer_manager.VOLUNTEER_MANAGER.assign_role", fake_assign_role)
    response = call_role_command("set greeter", "+70000000015", BotStateMachine())
    assert "an error occurred: simulated role assignment failure" in response.lower()

# End of tests/plugins/test_role_command.py