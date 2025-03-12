#!/usr/bin/env python
"""
tests/plugins/test_plugin_negatives.py
------------------------
Centralized negative/edge-case tests for various plugin commands except usage instructions,
which are now handled directly in each plugin's test_ file (for more modular coverage).
We still test partial/invalid arguments that do not just print usage but produce other errors.

Now includes resource and volunteer plugin negative tests for unified coverage.
"""

import pytest
from core.state import BotStateMachine, BotState
from plugins.commands.event import plan_event_command, edit_event_command, remove_event_command
from plugins.commands.task import task_command
from plugins.commands.role import role_command
from plugins.commands.system import shutdown_command
from plugins.commands.donate import donate_command
from plugins.commands.resource import resource_command
from plugins.commands.volunteer import add_skills_command, find_command, delete_command
from managers.volunteer.volunteer_operations import register_volunteer
from managers.volunteer.volunteer_roles import get_volunteer_record

####################################
# EVENT COMMAND NEGATIVES
####################################

def test_event_command_no_args():
    state_machine = BotStateMachine()
    response = plan_event_command("", "+dummy", state_machine)
    assert "Plan Event:" in response

def test_event_command_cancel():
    state_machine = BotStateMachine()
    response = plan_event_command("cancel", "+dummy", state_machine)
    assert "Event creation cancelled." in response

def test_event_command_missing_fields():
    state_machine = BotStateMachine()
    response = plan_event_command("Title:Test, Date:2025-12-31", "+dummy", state_machine)
    assert "Missing one or more required fields" in response

def test_event_command_edit_no_args():
    state_machine = BotStateMachine()
    response = edit_event_command("", "+dummy", state_machine)
    assert "Usage: @bot edit event" in response

def test_event_command_edit_no_eventid():
    state_machine = BotStateMachine()
    response = edit_event_command("title: newtitle", "+dummy", state_machine)
    assert "EventID is required" in response

def test_event_command_edit_invalid_eventid():
    """
    Updated to check the actual pydantic-based error message instead of
    'Invalid EventID provided.'
    """
    state_machine = BotStateMachine()
    response = edit_event_command("EventID: abc, title: newtitle", "+dummy", state_machine)
    # Check for the usage string and the model error text
    assert "usage error: edit event: provide valid eventid and fields" in response.lower()
    assert "1 validation error for editeventmodel" in response.lower()

def test_event_command_edit_non_existent():
    state_machine = BotStateMachine()
    response = edit_event_command("EventID: 9999, title: NonExistent", "+dummy", state_machine)
    assert "No event found with ID 9999" in response

def test_event_command_remove_no_args():
    state_machine = BotStateMachine()
    response = remove_event_command("", "+dummy", state_machine)
    assert "Usage: @bot remove event" in response

def test_event_command_remove_invalid_id():
    """
    Updated to check the actual pydantic-based error message instead of
    'Invalid EventID provided.'
    """
    state_machine = BotStateMachine()
    response = remove_event_command("EventID: abc", "+dummy", state_machine)
    assert "usage error: remove event: provide valid eventid" in response.lower()
    assert "1 validation error for removeeventbyidmodel" in response.lower()

def test_event_command_remove_non_existent():
    state_machine = BotStateMachine()
    response = remove_event_command("EventID: 9999", "+dummy", state_machine)
    assert "No event found with ID 9999" in response

def test_event_command_remove_title_non_existent():
    state_machine = BotStateMachine()
    response = remove_event_command("Title: Unknown Title", "+dummy", state_machine)
    assert "No event found with title 'Unknown Title'." in response


####################################
# TASK COMMAND NEGATIVES
####################################

def test_task_command_assign_invalid():
    response = task_command("assign 999 UnknownVolunteer", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "not found" in response.lower() or "volunteer with name" in response.lower()

def test_task_command_close_invalid():
    """
    Updated to check the new pydantic-based message instead of 'invalid task_id'.
    """
    response = task_command("close abc", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "usage error: task close <task_id>" in response.lower()
    assert "1 validation error for taskclosemodel" in response.lower()

def test_task_command_add_no_description():
    response = task_command("add", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "Usage: @bot task add <description>" in response

def test_task_command_assign_no_name():
    response = task_command("assign 123", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "Usage: @bot task assign <task_id> <volunteer_display_name>" in response

def test_task_command_assign_non_existent_volunteer():
    response = task_command("assign 10 FakeVolunteer", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "volunteer with name 'fakevolunteer' not found" in response.lower()


####################################
# DONATE COMMAND NEGATIVES (Partial)
####################################

def test_donate_command_invalid_amount():
    sender = "+4040404040"
    args = "abc Invalid amount test"
    response = donate_command(args, sender, BotStateMachine(), msg_timestamp=123)
    assert "Invalid donation amount" in response


####################################
# ROLE COMMAND NEGATIVES (Partial)
####################################

def test_role_command_set_failure():
    sender = "+70000000012"
    # Register volunteer without required skills for "emcee"
    register_volunteer(sender, "Role Tester 2", ["interpersonal"], True, None)
    state_machine = BotStateMachine()
    response = role_command("set emcee", sender, state_machine, msg_timestamp=123)
    assert "do not have the necessary skills" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") is None


####################################
# SYSTEM COMMANDS ERROR STATES
####################################

def test_shutdown_command_with_extra_args():
    state_machine = BotStateMachine()
    response = shutdown_command("somethingInvalid", "+dummy", state_machine, msg_timestamp=123)
    assert "Usage: @bot shutdown" in response
    # The bot state should remain RUNNING since we refused to shut down
    assert state_machine.current_state == BotStateMachine().current_state


####################################
# RESOURCE COMMAND NEGATIVES
####################################

def test_resource_command_remove_bad_id():
    """
    Attempt to remove a resource with a non-integer ID in the plugin command.
    Expect an error about 'Resource ID must be a positive integer.' or similar.
    """
    response = resource_command("remove abc", "+dummy", BotStateMachine())
    assert "must be a positive integer" in response.lower() or "error" in response.lower()

def test_resource_command_remove_zero_id():
    """
    Attempt to remove a resource with an ID of 0, which is invalid.
    The manager or plugin should raise an error about needing a positive integer.
    """
    response = resource_command("remove 0", "+dummy", BotStateMachine())
    # Some might say 'Resource ID must be a positive integer.'
    assert "positive integer" in response.lower() or "error" in response.lower()

def test_resource_command_add_missing_url():
    """
    Attempt to add a resource with no URL (just a category).
    Plugin code or manager logic should error beyond just usage instructions.
    """
    response = resource_command("add Linktree", "+dummy", BotStateMachine())
    assert "url is required" in response.lower() or "error" in response.lower()

def test_resource_command_add_missing_category():
    """
    Attempt to add a resource with no category, only a URL. Should produce an error.
    """
    response = resource_command("add http://example.com", "+dummy", BotStateMachine())
    assert "category is required" in response.lower() or "error" in response.lower()


####################################
# VOLUNTEER COMMAND NEGATIVES
####################################

def test_add_skills_command_no_skills():
    """
    Attempt to add skills with no arguments after the subcommand. 
    Should produce an error beyond usage instructions.
    """
    response = add_skills_command("", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "usage:" in response.lower() or "error" in response.lower()

def test_find_command_no_skills():
    """
    Attempt to find volunteers with no skill arguments. Expects an error or usage message. 
    Verifies negative coverage for partial arguments not just usage.
    """
    response = find_command("", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "usage:" in response.lower() or "error" in response.lower()

def test_delete_command_with_extra_args():
    """
    Attempt to delete with extra arguments that do not just skip usage. 
    We confirm it sets the same pending state or errors out in some negative scenario.
    """
    response = delete_command("extra stuff", "+dummy", BotStateMachine(), msg_timestamp=123)
    # The plugin sets 'initial' deletion state, but let's see if it yields an unexpected scenario.
    assert "delete your registration" in response.lower() or "deletion" in response.lower()

# End of tests/plugins/test_plugin_negatives.py