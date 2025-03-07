"""
tests/plugins/test_commands.py - Tests for plugin command functionalities.
Verifies that registered system and event command plugins return valid responses,
including tests for weekly update, theme, plan theme, status, speakers, and plan event.
"""

import pytest
from plugins.manager import get_all_plugins
from plugins.commands.system import (
    plugin_test_command, shutdown_command, assign_command,
    weekly_update_command, theme_command, plan_theme_command, status_command
)
from plugins.commands.event import event_command, speakers_command, plan_event_command
from core.state import BotStateMachine

@pytest.mark.asyncio
async def test_all_plugin_commands():
    state_machine = BotStateMachine()
    plugins = get_all_plugins()
    # Commands allowed to return an empty response (e.g., volunteer status when no data exists)
    allowed_empty = {"volunteer status"}
    for command, entry in plugins.items():
        args = ""
        func = entry["function"]
        result = func(args, "+dummy", state_machine, msg_timestamp=123)
        if hasattr(result, "__await__"):
            result = await result
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
    assert "assigned to" in result or "No available volunteer" in result

def test_shutdown_command():
    state_machine = BotStateMachine()
    result = shutdown_command("", "+111", state_machine, msg_timestamp=123)
    assert result.strip() == "Bot is shutting down."
    assert not state_machine.should_continue()

def test_weekly_update_command():
    state_machine = BotStateMachine()
    result = weekly_update_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "Weekly Update:" in result
    assert "Trump Actions:" in result
    assert "Democrat Advances:" in result

def test_theme_command():
    state_machine = BotStateMachine()
    result = theme_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "This Week's Theme:" in result
    assert "Key Message:" in result

def test_plan_theme_command():
    state_machine = BotStateMachine()
    result = plan_theme_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "Plan Theme:" in result
    assert "Theme:" in result

def test_status_command():
    # For status, we assume metrics are already updated.
    state_machine = BotStateMachine()
    result = status_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "Status:" in result
    assert "Messages sent:" in result
    assert "Uptime:" in result
    assert "Messages per hour:" in result
    assert "System: operational" in result

def test_event_command():
    from core.event_config import EVENT_DETAILS
    state_machine = BotStateMachine()
    result = event_command("", "+dummy", state_machine, msg_timestamp=123)
    assert EVENT_DETAILS["upcoming_event"]["title"] in result

def test_speakers_command():
    state_machine = BotStateMachine()
    # Test without event name
    result = speakers_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "Upcoming Speakers for the Next Event" in result
    # Test with an event name
    result_event = speakers_command("Some Event", "+dummy", state_machine, msg_timestamp=123)
    assert "Upcoming Speakers for 'Some Event'" in result_event

def test_plan_event_command():
    state_machine = BotStateMachine()
    result = plan_event_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "Plan Event:" in result
    assert "Title:" in result

# End of tests/plugins/test_commands.py