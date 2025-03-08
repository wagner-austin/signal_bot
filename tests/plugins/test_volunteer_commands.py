#!/usr/bin/env python
"""
test_volunteer_commands.py
--------------------------
Tests volunteer command plugins for normal usage: register, edit, delete, etc.
Negative or edge-case volunteer tests are either in their own specific modules or covered
in test_plugin_negatives.py if more severe. 
"""

import pytest
from plugins.commands.volunteer import (
    register_command,
    edit_command,
    delete_command,
    skills_command,
    find_command,
    add_skills_command
)
from core.state import BotStateMachine
from core.database.volunteers import get_volunteer_record

def test_volunteer_register_new():
    phone = "+80000000001"
    state_machine = BotStateMachine()
    response = register_command("Test User", phone, state_machine, msg_timestamp=123)
    assert "registered" in response.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    assert record.get("name").lower() == "test user"

def test_volunteer_register_existing():
    phone = "+80000000002"
    state_machine = BotStateMachine()
    register_command("Existing User", phone, state_machine, msg_timestamp=123)
    response = register_command("Any Name", phone, state_machine, msg_timestamp=123)
    # This is a normal "already registered" path, not a fatal error.
    assert "you are registered as" in response.lower()

def test_volunteer_edit_command_interactive():
    phone = "+80000000003"
    state_machine = BotStateMachine()
    register_command("Initial Name", phone, state_machine, msg_timestamp=123)
    response = edit_command("", phone, state_machine, msg_timestamp=123)
    assert "edit" in response.lower()

def test_volunteer_delete_command():
    phone = "+80000000004"
    state_machine = BotStateMachine()
    register_command("Delete Me", phone, state_machine, msg_timestamp=123)
    response = delete_command("", phone, state_machine, msg_timestamp=123)
    assert "delete your registration" in response.lower()

def test_volunteer_skills_command():
    phone = "+80000000005"
    state_machine = BotStateMachine()
    register_command("Skill User", phone, state_machine, msg_timestamp=123)
    response = skills_command("", phone, state_machine, msg_timestamp=123)
    assert "currently has skills" in response.lower()

def test_volunteer_find_command():
    phone = "+80000000006"
    register_command("Find Me", phone, BotStateMachine(), msg_timestamp=123)
    response = find_command("find", "+dummy", BotStateMachine(), msg_timestamp=123)
    # Usually just returns a string describing no volunteers match, or a list. 
    assert isinstance(response, str)

def test_volunteer_add_skills_command():
    phone = "+80000000007"
    register_command("Skill Adder", phone, BotStateMachine(), msg_timestamp=123)
    response = add_skills_command("Python, Testing", phone, BotStateMachine(), msg_timestamp=123)
    assert "registered" in response.lower() or "updated" in response.lower()

# End of tests/plugins/commands/test_volunteer_commands.py