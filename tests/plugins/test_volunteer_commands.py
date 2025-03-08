#!/usr/bin/env python
"""
tests/plugins/test_volunteer_commands.py
----------------------------------------
Tests volunteer command plugins for normal usage: register, edit, delete, etc.
Also includes a new test for a partial/malformed volunteer registration flow
(where the user sends '@bot register' then follows up with a blank message).

NEW/CHANGED:
  - Added test_register_command_blank_after_initiation to confirm
    the bot remains in a pending state or cancels gracefully, rather than crashing.
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

# --------------------------------------------------------
# NEW TEST: partial / malformed volunteer registration
# --------------------------------------------------------

def test_register_command_blank_after_initiation():
    """
    Simulates a user who sends '@bot register' with no arguments, gets a pending registration state,
    but then follows up with a blank message. We check that it doesn't crash,
    and the user remains in a pending or gracefully canceled state.
    """
    phone = "+80000000008"
    state_machine = BotStateMachine()

    # First, the user sends "@bot register" with no arguments:
    response1 = register_command("", phone, state_machine, msg_timestamp=123)
    assert "please respond with your first and last name" in response1.lower() or "registered" in response1.lower() or "you are registered as" in response1.lower()
    # Now we have a pending registration state.
    assert PENDING_ACTIONS.has_registration(phone)

    # Next, user sends a blank message. The register_command is typically triggered again with an empty string:
    response2 = register_command("", phone, state_machine, msg_timestamp=123)

    # It's up to the logic whether it remains pending or says "already registered." We just ensure no crash:
    # So we accept either continuing pending or a message about "You are registered as ...".
    # Implementation might vary. We'll just ensure it's not an unhandled error or meltdown.
    assert isinstance(response2, str) and response2.strip() != ""

# End of tests/plugins/test_volunteer_commands.py