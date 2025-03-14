#!/usr/bin/env python
"""
tests/plugins/test_volunteer_commands.py --- Tests volunteer command plugins.
Ensures normal usage for register, edit, delete, etc., and verifies that when a volunteer record is missing,
the response directs the user with the proper welcome prompt or partial name prompt.
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
from db.volunteers import get_volunteer_record
from core.messages import REGISTRATION_WELCOME
from core.plugin_usage import (
    USAGE_REGISTER, USAGE_EDIT, USAGE_DELETE, USAGE_SKILLS,
    USAGE_FIND, USAGE_ADD_SKILLS
)

def test_volunteer_register_new():
    """
    Tests registering a brand new volunteer with arguments.
    """
    phone = "+80000000001"
    state_machine = BotStateMachine()
    response = register_command("default Test User", phone, state_machine, msg_timestamp=123)
    assert "registered" in response.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    assert record.get("name").lower() == "test user"

def test_volunteer_register_existing():
    """
    Tests attempting to register again if the volunteer is already registered.
    """
    phone = "+80000000002"
    state_machine = BotStateMachine()
    register_command("default Existing User", phone, state_machine, msg_timestamp=123)
    response = register_command("default Any Name", phone, state_machine, msg_timestamp=123)
    # "already registered" path from the flow
    assert "you are already registered as" in response.lower()

def test_volunteer_register_no_args_shows_welcome():
    """
    Tests that when a new volunteer sends no arguments and no record exists,
    the registration welcome message is returned.
    """
    phone = "+80000000009"
    state_machine = BotStateMachine()
    response = register_command("default", phone, state_machine, msg_timestamp=123)
    assert REGISTRATION_WELCOME in response

def test_volunteer_edit_command_interactive():
    """
    Tests that editing with no arguments initiates interactive name editing.
    """
    phone = "+80000000003"
    state_machine = BotStateMachine()
    register_command("default Initial Name", phone, state_machine, msg_timestamp=123)
    response = edit_command("default", phone, state_machine, msg_timestamp=123)
    assert "starting edit flow" in response.lower() or "please provide your new name" in response.lower()

def test_volunteer_delete_command():
    """
    Tests volunteer deletion with no arguments -> should set a deletion flow state.
    """
    phone = "+80000000004"
    state_machine = BotStateMachine()
    register_command("default Delete Me", phone, state_machine, msg_timestamp=123)
    response = delete_command("default", phone, state_machine, msg_timestamp=123)
    assert "delete" in response.lower() or "starting deletion flow" in response.lower()

def test_volunteer_skills_command():
    """
    Tests the skills command, which lists current skills and potential additions.
    """
    phone = "+80000000005"
    state_machine = BotStateMachine()
    register_command("default Skill User", phone, state_machine, msg_timestamp=123)
    response = skills_command("default", phone, state_machine, msg_timestamp=123)
    assert "currently has skills" in response.lower()

def test_volunteer_find_command():
    """
    Tests a normal find scenario. Usually returns no volunteers if none match.
    """
    phone = "+80000000006"
    state_machine = BotStateMachine()
    register_command("default Find Me", phone, state_machine, msg_timestamp=123)
    response = find_command("default find", "+dummy", state_machine, msg_timestamp=123)
    assert isinstance(response, str), "Should return a string with either matches or no volunteers found"

def test_volunteer_add_skills_command():
    """
    Tests adding skills to an existing volunteer.
    """
    phone = "+80000000007"
    state_machine = BotStateMachine()
    register_command("default Skill Adder", phone, state_machine, msg_timestamp=123)
    response = add_skills_command("default Python, Testing", phone, state_machine, msg_timestamp=123)
    assert any(keyword in response.lower() for keyword in ["registered", "updated"])

def test_volunteer_find_command_no_args_shows_usage():
    """
    Tests that calling 'find_command' with no arguments returns usage instructions.
    """
    phone = "+80000000006"
    state_machine = BotStateMachine()
    response = find_command("", phone, state_machine, msg_timestamp=123)
    assert "usage:" in response.lower()

def test_volunteer_add_skills_command_no_args_shows_usage():
    """
    Tests that calling 'add_skills_command' with no arguments returns usage instructions.
    """
    phone = "+80000000007"
    state_machine = BotStateMachine()
    response = add_skills_command("", phone, state_machine, msg_timestamp=123)
    assert "usage:" in response.lower()

def test_register_command_partial():
    """
    Tests that providing an incomplete name (e.g., only one word) for registration
    returns the flow's partial name message.
    """
    phone = "+80000000008"
    state_machine = BotStateMachine()
    # "John" => only one word => triggers flow message about needing first/last name
    response = register_command("default John", phone, state_machine, msg_timestamp=123)
    assert "provide your first and last name" in response.lower(), \
        "Expected the flow to prompt for more than one word"

# End of tests/plugins/test_volunteer_commands.py