#!/usr/bin/env python
"""
tests/plugins/test_plugin_negatives.py
------------------------
Centralized negative/edge-case tests for various plugin commands except usage instructions,
which are now handled directly in each plugin's test_ file (for more modular coverage).
We still test partial/invalid arguments that do not just print usage but produce other errors.
"""

import pytest
from core.state import BotStateMachine, BotState
from plugins.commands.event import plan_event_command, edit_event_command, remove_event_command
from plugins.commands.task import task_command
from plugins.commands.role import role_command
from plugins.commands.system import shutdown_command
from plugins.commands.donate import donate_command  # <-- Newly added import
from managers.volunteer.volunteer_operations import sign_up
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
    state_machine = BotStateMachine()
    response = edit_event_command("EventID: abc, title: newtitle", "+dummy", state_machine)
    assert "Invalid EventID provided." in response

def test_event_command_edit_non_existent():
    state_machine = BotStateMachine()
    response = edit_event_command("EventID: 9999, title: NonExistent", "+dummy", state_machine)
    assert "No event found with ID 9999" in response

def test_event_command_remove_no_args():
    state_machine = BotStateMachine()
    response = remove_event_command("", "+dummy", state_machine)
    assert "Usage: @bot remove event" in response

def test_event_command_remove_invalid_id():
    state_machine = BotStateMachine()
    response = remove_event_command("EventID: abc", "+dummy", state_machine)
    assert "Invalid EventID provided." in response

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
    response = task_command("close abc", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "invalid task_id" in response.lower()

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
    sign_up(sender, "Role Tester 2", ["interpersonal"], True, None)
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

# End of tests/plugins/test_plugin_negatives.py