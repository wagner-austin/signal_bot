#!/usr/bin/env python
"""
tests/plugins/test_task_command.py - Tests for task command plugin.
Verifies subcommands: add, list, assign, and close.
"""
from plugins.commands.task import task_command
from core.state import BotStateMachine

def test_task_add_command():
    state_machine = BotStateMachine()
    response = task_command("add Test task for plugin", "+dummy", state_machine, msg_timestamp=123)
    assert "Task added with ID" in response

def test_task_list_command():
    state_machine = BotStateMachine()
    response = task_command("list", "+dummy", state_machine, msg_timestamp=123)
    # It might be "No tasks found" if none exist.
    assert "No tasks found" in response or "Tasks:" in response

def test_task_assign_invalid():
    state_machine = BotStateMachine()
    response = task_command("assign 999 UnknownVolunteer", "+dummy", state_machine, msg_timestamp=123)
    # Since no volunteer exists, expect error message.
    assert "not found" in response.lower() or "invalid" in response.lower()

def test_task_close_invalid():
    state_machine = BotStateMachine()
    response = task_command("close abc", "+dummy", state_machine, msg_timestamp=123)
    assert "invalid task_id" in response.lower()

# End of tests/plugins/test_task_command.py