#!/usr/bin/env python
"""
tests/plugins/test_plugin_negatives.py
------------------------
Centralized negative/edge-case tests for various plugin commands.
Tests partial/invalid arguments and ensures error messages include usage prompts from centralized constants.
"""

import pytest
from core.state import BotStateMachine
from plugins.commands.event import plan_event_command, edit_event_command, remove_event_command
from plugins.commands.task import task_command
from plugins.commands.role import role_command
from plugins.commands.system import shutdown_command
from plugins.commands.donate import donate_command
from plugins.commands.resource import resource_command
from plugins.commands.volunteer import add_skills_command, find_command, delete_command
from core.plugin_usage import (
    USAGE_PLAN_EVENT, USAGE_PLAN_EVENT_PARTIAL, USAGE_EDIT_EVENT,
    USAGE_REMOVE_EVENT, USAGE_TASK_CLOSE, USAGE_DONATE, USAGE_RESOURCE, USAGE_ROLE
)

####################################
# EVENT COMMAND NEGATIVES
####################################

def test_event_command_no_args():
    state_machine = BotStateMachine()
    response = plan_event_command("", "+dummy", state_machine)
    # Expect usage message from USAGE_PLAN_EVENT
    assert USAGE_PLAN_EVENT.lower() in response.lower()

def test_event_command_cancel():
    state_machine = BotStateMachine()
    response = plan_event_command("cancel", "+dummy", state_machine)
    assert "cancelled" in response.lower()

def test_event_command_missing_fields():
    state_machine = BotStateMachine()
    response = plan_event_command("Title:Test, Date:2025-12-31", "+dummy", state_machine)
    assert "missing" in response.lower() and USAGE_PLAN_EVENT_PARTIAL.lower() in response.lower()

def test_event_command_edit_no_args():
    state_machine = BotStateMachine()
    response = edit_event_command("", "+dummy", state_machine)
    assert USAGE_EDIT_EVENT.lower() in response.lower()

def test_event_command_edit_no_eventid():
    state_machine = BotStateMachine()
    response = edit_event_command("title: newtitle", "+dummy", state_machine)
    assert "eventid is required" in response.lower()

def test_event_command_edit_invalid_eventid():
    state_machine = BotStateMachine()
    response = edit_event_command("EventID: abc, title: newtitle", "+dummy", state_machine)
    assert "validation error for editeventmodel" in response.lower()

def test_event_command_edit_non_existent():
    state_machine = BotStateMachine()
    response = edit_event_command("EventID: 9999, title: NonExistent", "+dummy", state_machine)
    assert "no event found with id 9999" in response.lower()

def test_event_command_remove_no_args():
    state_machine = BotStateMachine()
    response = remove_event_command("", "+dummy", state_machine)
    assert USAGE_REMOVE_EVENT.lower() in response.lower()

def test_event_command_remove_invalid_id():
    state_machine = BotStateMachine()
    response = remove_event_command("EventID: abc", "+dummy", state_machine)
    assert "validation error for removeeventbyidmodel" in response.lower()

def test_event_command_remove_non_existent():
    state_machine = BotStateMachine()
    response = remove_event_command("EventID: 9999", "+dummy", state_machine)
    assert "no event found with id 9999" in response.lower()

def test_event_command_remove_title_non_existent():
    state_machine = BotStateMachine()
    response = remove_event_command("Title: Unknown Title", "+dummy", state_machine)
    assert "no event found with title 'unknown title'" in response.lower()

####################################
# TASK COMMAND NEGATIVES
####################################

def test_task_command_assign_invalid():
    response = task_command("assign 999 UnknownVolunteer", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "not found" in response.lower() or "volunteer with name" in response.lower()

def test_task_command_close_invalid():
    response = task_command("close abc", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "validation error for taskclosemodel" in response.lower()

def test_task_command_add_no_description():
    response = task_command("add", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "usage:" in response.lower() and "task add" in response.lower()

def test_task_command_assign_no_name():
    response = task_command("assign 123", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "usage:" in response.lower() and "task assign" in response.lower()

def test_task_command_assign_non_existent_volunteer():
    response = task_command("assign 10 FakeVolunteer", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "volunteer with name" in response.lower() and "not found" in response.lower()

####################################
# DONATE COMMAND NEGATIVES (Partial)
####################################

def test_donate_command_invalid_amount():
    sender = "+4040404040"
    args = "abc Invalid amount test"
    response = donate_command(args, sender, BotStateMachine(), msg_timestamp=123)
    # Expect the usage message for donate command
    from core.plugin_usage import USAGE_DONATE
    assert USAGE_DONATE.lower() in response.lower()

####################################
# ROLE COMMAND NEGATIVES (Partial)
####################################

def test_role_command_set_failure():
    sender = "+70000000012"
    # Register volunteer without required skills for "emcee"
    from managers.volunteer.volunteer_operations import register_volunteer
    register_volunteer(sender, "Role Tester 2", ["interpersonal"], True, None)
    state_machine = BotStateMachine()
    response = role_command("set emcee", sender, state_machine, msg_timestamp=123)
    assert "do not have the necessary skills" in response.lower()
    from managers.volunteer.volunteer_roles import get_volunteer_record
    record = get_volunteer_record(sender)
    assert record.get("preferred_role") is None

####################################
# SYSTEM COMMANDS ERROR STATES
####################################

def test_shutdown_command_with_extra_args():
    state_machine = BotStateMachine()
    response = shutdown_command("somethingInvalid", "+dummy", state_machine, msg_timestamp=123)
    assert "usage:" in response.lower() and "shutdown" in response.lower()
    assert state_machine.current_state == BotStateMachine().current_state

####################################
# RESOURCE COMMAND NEGATIVES
####################################

def test_resource_command_remove_bad_id():
    response = resource_command("remove abc", "+dummy", BotStateMachine())
    assert "must be a positive integer" in response.lower() or "error" in response.lower()

def test_resource_command_remove_zero_id():
    response = resource_command("remove 0", "+dummy", BotStateMachine())
    assert "positive integer" in response.lower() or "error" in response.lower()

def test_resource_command_add_missing_url():
    response = resource_command("add Linktree", "+dummy", BotStateMachine())
    assert "url is required" in response.lower() or "error" in response.lower()

def test_resource_command_add_missing_category():
    response = resource_command("add http://example.com", "+dummy", BotStateMachine())
    assert "category is required" in response.lower() or "error" in response.lower()

def test_resource_unknown_subcommand():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("foo", sender, state_machine, msg_timestamp=123)
    from core.plugin_usage import USAGE_RESOURCE
    assert USAGE_RESOURCE.lower() in response.lower()

####################################
# VOLUNTEER COMMAND NEGATIVES
####################################

def test_add_skills_command_no_skills():
    response = add_skills_command("", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "usage:" in response.lower() or "error" in response.lower()

def test_find_command_no_skills():
    response = find_command("", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "usage:" in response.lower() or "error" in response.lower()

def test_delete_command_with_extra_args():
    response = delete_command("extra stuff", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "delete your registration" in response.lower() or "deletion" in response.lower()

# End of tests/plugins/test_plugin_negatives.py