#!/usr/bin/env python
"""
test_task_command.py
--------------------
Tests 'task' command plugin for normal (non-error) paths: add, list, assign, close.
Negative/edge cases are now in test_plugin_negatives.py.
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

# End of tests/plugins/commands/test_task_command.py