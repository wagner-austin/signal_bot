#!/usr/bin/env python
"""
tests/plugins/test_task_command.py ---
Comprehensive tests for the 'task' command plugin, including edge cases.
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
    # Since no volunteer exists, expect an error or "Volunteer with name 'UnknownVolunteer' not found."
    assert "not found" in response.lower() or "volunteer with name" in response.lower()

def test_task_close_invalid():
    state_machine = BotStateMachine()
    response = task_command("close abc", "+dummy", state_machine, msg_timestamp=123)
    assert "invalid task_id" in response.lower()

# -------------------------------
# New Edge Case Tests
# -------------------------------

def test_task_add_no_description():
    """
    Verify that running '@bot task add' with no description yields usage or an error message.
    """
    state_machine = BotStateMachine()
    response = task_command("add", "+dummy", state_machine, msg_timestamp=123)
    assert "Usage: @bot task add <description>" in response

def test_task_assign_no_name():
    """
    Verify that running '@bot task assign <task_id>' with no volunteer name
    yields the usage message or an error.
    """
    state_machine = BotStateMachine()
    # Only an ID, no volunteer name.
    response = task_command("assign 123", "+dummy", state_machine, msg_timestamp=123)
    assert "Usage: @bot task assign <task_id> <volunteer_display_name>" in response

def test_task_assign_non_existent_volunteer():
    """
    Verify that assigning a task to a volunteer name who doesn't exist returns
    the relevant volunteer-not-found error message.
    """
    state_machine = BotStateMachine()
    # 'FakeVolunteer' does not exist in the DB.
    response = task_command("assign 10 FakeVolunteer", "+dummy", state_machine, msg_timestamp=123)
    # The plugin calls `assign_task` which returns "Volunteer with name 'xxx' not found."
    assert "volunteer with name 'fakevolunteer' not found" in response.lower()

# End of tests/plugins/test_task_command.py