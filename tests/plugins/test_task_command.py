#!/usr/bin/env python
"""
tests/plugins/test_task_command.py - Tests for the task command plugin.
Verifies normal operations and exception handling for task commands.
"""

from plugins.commands.task import task_command
from core.state import BotStateMachine
import pytest
from core.plugin_usage import USAGE_TASK_ADD, USAGE_TASK_LIST, USAGE_TASK_ASSIGN, USAGE_TASK_CLOSE

def test_task_add_command():
    state_machine = BotStateMachine()
    response = task_command("add Test task for plugin", "+dummy", state_machine, msg_timestamp=123)
    assert "task added with id" in response.lower()

def test_task_list_command():
    state_machine = BotStateMachine()
    response = task_command("list", "+dummy", state_machine, msg_timestamp=123)
    assert "no tasks found" in response.lower() or "tasks:" in response.lower()

def test_task_unknown_subcommand():
    state_machine = BotStateMachine()
    response = task_command("foo", "+dummy", state_machine, msg_timestamp=123)
    # Expect usage text containing all task command usages.
    for usage in [USAGE_TASK_ADD, USAGE_TASK_LIST, USAGE_TASK_ASSIGN, USAGE_TASK_CLOSE]:
        assert usage.lower() in response.lower()

def test_task_command_assign_handles_exception(monkeypatch):
    from core.exceptions import VolunteerError
    def fake_assign_task(task_id, volunteer_display_name):
         raise VolunteerError("Simulated task assignment failure")
    monkeypatch.setattr("managers.task_manager.assign_task", fake_assign_task)
    response = task_command("assign 10 SomeVolunteer", "+dummy", BotStateMachine(), msg_timestamp=123)
    # Check that response contains "volunteer with name" and "not found"
    assert "volunteer with name" in response.lower() and "not found" in response.lower()

def test_task_command_close_invalid():
    response = task_command("close abc", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "validation error for taskclosemodel" in response.lower()

# End of tests/plugins/test_task_command.py