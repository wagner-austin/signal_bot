#!/usr/bin/env python
"""
tests/plugins/test_task_command.py - Tests for the task command plugin.
Verifies normal operations and CLI exception handling for task commands.
"""

from plugins.commands.task import task_command
from core.state import BotStateMachine
import pytest

def test_task_add_command():
    state_machine = BotStateMachine()
    response = task_command("add Test task for plugin", "+dummy", state_machine, msg_timestamp=123)
    assert "task added with id" in response.lower()

def test_task_list_command():
    state_machine = BotStateMachine()
    response = task_command("list", "+dummy", state_machine, msg_timestamp=123)
    assert "no tasks found" in response.lower() or "tasks:" in response.lower()

def test_task_unknown_subcommand():
    """
    Test that an unrecognized subcommand returns an appropriate error message.
    """
    state_machine = BotStateMachine()
    response = task_command("foo", "+dummy", state_machine, msg_timestamp=123)
    assert "invalid subcommand for task" in response.lower()

def test_task_command_assign_handles_exception(monkeypatch):
    """
    Tests that the task command catches a manager exception and returns a user-friendly error message.
    """
    from core.exceptions import VolunteerError
    from core.state import BotStateMachine
    def fake_assign_task(task_id, volunteer_display_name):
         raise VolunteerError("Simulated task assignment failure")
    monkeypatch.setattr("managers.task_manager.assign_task", fake_assign_task)
    response = task_command("assign 10 SomeVolunteer", "+dummy", BotStateMachine(), msg_timestamp=123)
    assert "an error occurred: simulated task assignment failure" in response.lower()

# End of tests/plugins/test_task_command.py