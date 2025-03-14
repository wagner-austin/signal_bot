#!/usr/bin/env python
"""
tests/plugins/test_role_command.py - Tests for the role command plugin.
Verifies listing roles, setting, switching, unassigning, and exception handling.
"""

import pytest
from core.state import BotStateMachine
from managers.volunteer_manager import register_volunteer
from db.volunteers import get_volunteer_record
from plugins.commands.role import role_command
from core.plugin_usage import USAGE_ROLE

def call_role_command(command_args, sender, state_machine):
    return role_command(command_args, sender, state_machine, msg_timestamp=123)

def test_role_no_args_shows_recognized_roles():
    state_machine = BotStateMachine()
    response = call_role_command("", "+70000000010", state_machine)
    assert "recognized roles:" in response.lower()

def test_role_bogus_subcommand_shows_usage():
    state_machine = BotStateMachine()
    response = call_role_command("bogus", "+70000000011", state_machine)
    assert USAGE_ROLE.lower() in response.lower()

def test_role_list_command():
    state_machine = BotStateMachine()
    response = call_role_command("list", "+70000000010", state_machine)
    assert "recognized roles:" in response.lower()

def test_role_set_command_success():
    sender = "+70000000011"
    register_volunteer(sender, "Role Tester", ["communication", "interpersonal"], True, None)
    state_machine = BotStateMachine()
    response = call_role_command("set greeter", sender, state_machine)
    assert "preferred role has been set" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") == "greeter"

def test_role_switch_command_success():
    sender = "+70000000013"
    register_volunteer(sender, "Role Tester 3", ["communication", "interpersonal", "public speaking"], True, "greeter")
    state_machine = BotStateMachine()
    response = call_role_command("switch emcee", sender, state_machine)
    assert "switching from" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") == "emcee"

def test_role_unassign_command():
    sender = "+70000000014"
    register_volunteer(sender, "Role Tester 4", ["communication", "interpersonal"], True, "greeter")
    state_machine = BotStateMachine()
    response = call_role_command("unassign", sender, state_machine)
    assert "cleared" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") is None

def test_role_command_handles_manager_exception(monkeypatch):
    from core.exceptions import VolunteerError
    def fake_assign_role(sender, role):
         raise VolunteerError("Simulated role assignment failure")
    monkeypatch.setattr("managers.volunteer_manager.VOLUNTEER_MANAGER.assign_role", fake_assign_role)
    response = call_role_command("set greeter", "+70000000015", BotStateMachine())
    assert "simulated role assignment failure" in response.lower()

# End of tests/plugins/test_role_command.py