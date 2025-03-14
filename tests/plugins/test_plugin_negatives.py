# tests/plugins/test_plugin_negatives.py
"""
tests/plugins/test_plugin_negatives.py
------------------------
Centralized negative/edge-case tests for various plugin commands.
Tests partial/invalid arguments and ensures error messages include usage prompts from centralized constants.
"""

import pytest
from core.state import BotStateMachine
from plugins.commands.event import plan_event_command, remove_event_command
from plugins.commands.task import task_command
from plugins.commands.role import role_command
from plugins.commands.system import shutdown_command
from plugins.commands.donate import donate_command
from plugins.commands.resource import resource_command
from plugins.commands.volunteer import add_skills_command, find_command, delete_command
from core.plugin_usage import (
    USAGE_PLAN_EVENT, USAGE_PLAN_EVENT_PARTIAL, USAGE_REMOVE_EVENT,
    USAGE_TASK_ADD, USAGE_TASK_LIST, USAGE_TASK_ASSIGN, USAGE_TASK_CLOSE,
    USAGE_DONATE, USAGE_ROLE, USAGE_SHUTDOWN, USAGE_RESOURCE,
    USAGE_ADD_SKILLS, USAGE_FIND
)

def test_event_command_no_args():
    state_machine = BotStateMachine()
    response = plan_event_command("", "+dummy", state_machine)
    # Expect usage message from USAGE_PLAN_EVENT
    assert USAGE_PLAN_EVENT.lower() in response.lower()

def test_event_command_remove_no_args():
    state_machine = BotStateMachine()
    response = remove_event_command("", "+dummy", state_machine)
    assert USAGE_REMOVE_EVENT.lower() in response.lower()

def test_task_command_add_no_description():
    response = task_command("add", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert USAGE_TASK_ADD.lower() in response.lower()

def test_task_command_assign_no_name():
    response = task_command("assign 123", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert USAGE_TASK_ASSIGN.lower() in response.lower()

def test_task_command_assign_non_existent_volunteer():
    response = task_command("assign 10 FakeVolunteer", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "volunteer with name" in response.lower() and "not found" in response.lower()

def test_task_command_close_invalid():
    response = task_command("close abc", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "validation error for taskclosemodel" in response.lower()

def test_donate_command_invalid_amount():
    sender = "+4040404040"
    args = "abc Invalid amount test"
    response = donate_command(args, sender, BotStateMachine(), msg_timestamp=123)
    assert USAGE_DONATE.lower() in response.lower()

def test_donate_negative_amount():
    state_machine = BotStateMachine()
    sender = "+4040404041"
    args = "-100 Malicious donation"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "donation logged with id" in response.lower()

def test_donate_extremely_large_amount():
    state_machine = BotStateMachine()
    sender = "+4040404042"
    args = "1e12 Extremely large donation"
    response = donate_command(args, sender, state_machine, msg_timestamp=123)
    assert "donation logged with id" in response.lower()

def test_role_command_set_failure():
    sender = "+70000000012"
    from managers.volunteer_manager import register_volunteer
    register_volunteer(sender, "Role Tester 2", ["interpersonal"], True, None)
    state_machine = BotStateMachine()
    response = role_command("set emcee", sender, state_machine, msg_timestamp=123)
    assert "do not have the necessary skills" in response.lower()

def test_shutdown_command_with_extra_args():
    state_machine = BotStateMachine()
    response = shutdown_command("somethingInvalid", "+dummy", state_machine, msg_timestamp=123)
    assert USAGE_SHUTDOWN.lower() in response.lower()

def test_resource_command_remove_bad_id():
    response = resource_command("remove abc", "+dummy", BotStateMachine())
    assert "resource id must be a positive integer" in response.lower() or "error" in response.lower()

def test_resource_command_remove_zero_id():
    response = resource_command("remove 0", "+dummy", BotStateMachine())
    assert "resource id must be a positive integer" in response.lower() or "error" in response.lower()

def test_resource_command_add_missing_url():
    response = resource_command("add Flyers", "+dummy", BotStateMachine())
    assert "url is required" in response.lower() or "error" in response.lower()

def test_resource_command_add_missing_category():
    response = resource_command("add http://example.com", "+dummy", BotStateMachine())
    assert "category is required" in response.lower() or "error" in response.lower()

def test_resource_unknown_subcommand():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("foo", sender, state_machine, msg_timestamp=123)
    assert USAGE_RESOURCE.lower() in response.lower()

def test_add_skills_command_no_skills():
    response = add_skills_command("", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert USAGE_ADD_SKILLS.lower() in response.lower()

def test_find_command_no_skills():
    response = find_command("", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert USAGE_FIND.lower() in response.lower()

def test_delete_command_with_extra_args():
    response = delete_command("extra stuff", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert ("delete your registration" in response.lower()
            or "deletion" in response.lower()
            or "nothing to delete" in response.lower())

# End of tests/plugins/test_plugin_negatives.py