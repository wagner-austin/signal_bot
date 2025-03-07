"""
tests/plugins/test_commands.py - Tests for plugin command functionalities.
Verifies that registered command plugins return valid responses,
including tests for system, event, and help commands.
"""

import pytest
from plugins.manager import get_all_plugins
from plugins.commands.system import plugin_test_command, shutdown_command, assign_command
from core.state import BotStateMachine

@pytest.mark.asyncio
async def test_all_plugin_commands():
    state_machine = BotStateMachine()
    plugins = get_all_plugins()
    # Commands allowed to return an empty response (e.g., volunteer status when no data exists)
    allowed_empty = {"volunteer status"}
    for command, entry in plugins.items():
        args = ""
        # Extract the actual function from the plugin entry dictionary.
        func = entry["function"]
        result = func(args, "+dummy", state_machine, msg_timestamp=123)
        if hasattr(result, "__await__"):
            result = await result
        # If the command is allowed to return an empty response, skip the check.
        if command in allowed_empty:
            continue
        assert isinstance(result, str) and result.strip(), f"Plugin '{command}' returned empty response"

def test_plugin_test_command():
    state_machine = BotStateMachine()
    result = plugin_test_command("", "+111", state_machine, msg_timestamp=123)
    assert result.strip() == "yes"

def test_assign_command():
    state_machine = BotStateMachine()
    result = assign_command("Event Coordination", "+111", state_machine, msg_timestamp=123)
    # The assign command returns a message with either an assignment or a "not available" message.
    assert "assigned to" in result or "No available volunteer" in result

def test_shutdown_command():
    state_machine = BotStateMachine()
    result = shutdown_command("", "+111", state_machine, msg_timestamp=123)
    assert result.strip() == "Bot is shutting down."
    assert not state_machine.should_continue()

def test_event_command():
    from plugins.commands.event import event_command
    from core.event_config import EVENT_DETAILS
    state_machine = BotStateMachine()
    result = event_command("", "+dummy", state_machine, msg_timestamp=123)
    assert EVENT_DETAILS["upcoming_event"]["title"] in result

def test_help_commands():
    from plugins.commands.help import help_command
    state_machine = BotStateMachine()
    result_help = help_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "@bot" in result_help

# End of tests/plugins/test_commands.py