#!/usr/bin/env python
"""
test_plugin_negatives.py
------------------------
Centralized negative/edge-case tests for various plugin commands:
- event command: partial/invalid fields
- task command: missing volunteer name, invalid numeric inputs
- donate command: invalid donation amounts, usage instructions
- role command: failing skill checks
- etc.
"""

import pytest
from core.state import BotStateMachine
from plugins.commands.event import plan_event_command, edit_event_command, remove_event_command
from plugins.commands.task import task_command
from plugins.commands.donate import donate_command
from plugins.commands.role import role_command
from managers.volunteer.volunteer_operations import sign_up
from managers.volunteer.volunteer_roles import get_volunteer_record

####################################
# EVENT COMMAND NEGATIVES
####################################

@pytest.fixture
def state_machine():
    return BotStateMachine()

def test_event_command_no_args(state_machine):
    response = plan_event_command("", "+dummy", state_machine)
    assert "Plan Event:" in response

def test_event_command_cancel(state_machine):
    response = plan_event_command("cancel", "+dummy", state_machine)
    assert "Event creation cancelled." in response

def test_event_command_missing_fields(state_machine):
    response = plan_event_command("Title:Test, Date:2025-12-31", "+dummy", state_machine)
    assert "Missing one or more required fields" in response

def test_event_command_edit_no_args(state_machine):
    response = edit_event_command("", "+dummy", state_machine)
    assert "Usage: @bot edit event" in response

def test_event_command_edit_no_eventid(state_machine):
    response = edit_event_command("title: newtitle", "+dummy", state_machine)
    assert "EventID is required" in response

def test_event_command_edit_invalid_eventid(state_machine):
    response = edit_event_command("EventID: abc, title: newtitle", "+dummy", state_machine)
    assert "Invalid EventID provided." in response

def test_event_command_edit_non_existent(state_machine):
    response = edit_event_command("EventID: 9999, title: NonExistent", "+dummy", state_machine)
    assert "No event found with ID 9999 to edit." in response

def test_event_command_remove_no_args(state_machine):
    response = remove_event_command("", "+dummy", state_machine)
    assert "Usage: @bot remove event" in response

def test_event_command_remove_invalid_id(state_machine):
    response = remove_event_command("EventID: abc", "+dummy", state_machine)
    assert "Invalid EventID provided." in response

def test_event_command_remove_non_existent(state_machine):
    response = remove_event_command("EventID: 9999", "+dummy", state_machine)
    assert "No event found with ID 9999." in response

def test_event_command_remove_title_non_existent(state_machine):
    response = remove_event_command("Title: Unknown Title", "+dummy", state_machine)
    assert "No event found with title 'Unknown Title'." in response


####################################
# TASK COMMAND NEGATIVES
####################################

def test_task_command_assign_invalid(state_machine):
    response = task_command("assign 999 UnknownVolunteer", "+dummy", state_machine, msg_timestamp=123)
    assert "not found" in response.lower() or "volunteer with name" in response.lower()

def test_task_command_close_invalid(state_machine):
    response = task_command("close abc", "+dummy", state_machine, msg_timestamp=123)
    assert "invalid task_id" in response.lower()

def test_task_command_add_no_description(state_machine):
    response = task_command("add", "+dummy", state_machine, msg_timestamp=123)
    assert "Usage: @bot task add <description>" in response

def test_task_command_assign_no_name(state_machine):
    response = task_command("assign 123", "+dummy", state_machine, msg_timestamp=123)
    assert "Usage: @bot task assign <task_id> <volunteer_display_name>" in response

def test_task_command_assign_non_existent_volunteer(state_machine):
    response = task_command("assign 10 FakeVolunteer", "+dummy", state_machine, msg_timestamp=123)
    assert "volunteer with name 'fakevolunteer' not found" in response.lower()


####################################
# DONATE COMMAND NEGATIVES
####################################

def test_donate_command_invalid_amount(state_machine):
    sender = "+4040404040"
    args = "abc Invalid amount test"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Invalid donation amount" in response

def test_donate_command_usage_instructions(state_machine):
    sender = "+5050505050"
    args = ""
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "Usage:" in response


####################################
# ROLE COMMAND NEGATIVES
####################################

def call_role_command(args, sender, sm):
    return role_command(args, sender, sm, msg_timestamp=123)

def test_role_command_set_failure(state_machine):
    sender = "+70000000012"
    # Register volunteer without required skills for "emcee" (needs public speaking, communication)
    sign_up(sender, "Role Tester 2", ["interpersonal"], True, None)
    response = call_role_command("set emcee", sender, state_machine)
    assert "do not have the necessary skills" in response.lower()
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") is None

# End of tests/plugins/test_plugin_negatives.py