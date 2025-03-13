#!/usr/bin/env python
"""
tests/plugins/test_volunteer_commands.py - Tests volunteer command plugins.
Ensures normal usage for register, edit, delete, etc., and verifies that when a volunteer record is missing,
the response directs the user with the proper welcome prompt.
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
from managers.pending_actions import PENDING_ACTIONS
from core.plugin_usage import USAGE_REGISTER_PARTIAL
from core.messages import REGISTRATION_WELCOME, GETTING_STARTED, ALREADY_REGISTERED

def test_volunteer_register_new():
    """
    Tests registering a brand new volunteer with arguments.
    """
    phone = "+80000000001"
    state_machine = BotStateMachine()
    response = register_command("Test User", phone, state_machine, msg_timestamp=123)
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
    register_command("Existing User", phone, state_machine, msg_timestamp=123)
    response = register_command("Any Name", phone, state_machine, msg_timestamp=123)
    # This is a normal "already registered" path.
    assert "you are registered as" in response.lower()

def test_volunteer_register_no_args_shows_welcome():
    """
    Tests that when a new volunteer sends no arguments and no record exists,
    the registration welcome message is returned.
    """
    phone = "+80000000009"
    state_machine = BotStateMachine()
    # Ensure no volunteer record exists for this phone.
    response = register_command("", phone, state_machine, msg_timestamp=123)
    assert REGISTRATION_WELCOME in response

def test_volunteer_edit_command_interactive():
    """
    Tests that editing with no arguments initiates interactive name editing.
    """
    phone = "+80000000003"
    state_machine = BotStateMachine()
    register_command("Initial Name", phone, state_machine, msg_timestamp=123)
    response = edit_command("", phone, state_machine, msg_timestamp=123)
    assert "edit" in response.lower()

def test_volunteer_delete_command():
    """
    Tests volunteer deletion with no arguments -> should set a pending deletion state.
    """
    phone = "+80000000004"
    state_machine = BotStateMachine()
    register_command("Delete Me", phone, state_machine, msg_timestamp=123)
    response = delete_command("", phone, state_machine, msg_timestamp=123)
    assert "delete your registration" in response.lower()

def test_volunteer_skills_command():
    """
    Tests the skills command, which lists current skills and potential additions.
    """
    phone = "+80000000005"
    state_machine = BotStateMachine()
    register_command("Skill User", phone, state_machine, msg_timestamp=123)
    response = skills_command("", phone, state_machine, msg_timestamp=123)
    assert "currently has skills" in response.lower()

def test_volunteer_find_command():
    """
    Tests a normal find scenario. Usually returns no volunteers if none match.
    """
    phone = "+80000000006"
    state_machine = BotStateMachine()
    register_command("Find Me", phone, state_machine, msg_timestamp=123)
    response = find_command("find", "+dummy", state_machine, msg_timestamp=123)
    # Usually just returns no matches or a list. We check that it's a string.
    assert isinstance(response, str)

def test_volunteer_add_skills_command():
    """
    Tests adding skills to an existing volunteer.
    """
    phone = "+80000000007"
    state_machine = BotStateMachine()
    register_command("Skill Adder", phone, state_machine, msg_timestamp=123)
    response = add_skills_command("Python, Testing", phone, state_machine, msg_timestamp=123)
    assert "registered" in response.lower() or "updated" in response.lower()

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
    Tests that providing an incomplete name (e.g., only one word) for registration returns a partial usage prompt.
    """
    phone = "+80000000008"
    state_machine = BotStateMachine()
    response = register_command("John", phone, state_machine, msg_timestamp=123)
    # Expect the response to equal the partial usage prompt for registration.
    assert USAGE_REGISTER_PARTIAL.lower() in response.lower()

# End of tests/plugins/test_volunteer_commands.py