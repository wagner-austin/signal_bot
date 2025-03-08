"""
tests/plugins/test_commands.py - Tests for plugin command functionalities.
Verifies that registered system, event, speaker, and volunteer command plugins return valid responses.
Includes tests for weekly update, theme, plan theme, status, event, speakers, plan event,
edit event, remove event, add speaker, and remove speaker.
"""

import pytest
from plugins.manager import get_all_plugins
from plugins.commands.system import (
    plugin_test_command, shutdown_command, assign_command,
    weekly_update_command, theme_command, plan_theme_command, status_command
)
from plugins.commands.event import (
    event_command, speakers_command, plan_event_command, 
    edit_event_command, remove_event_command
)
from plugins.commands.speaker import (
    add_speaker_command, remove_speaker_command
)
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
    state_machine = BotStateMachine()
    result = status_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "Status:" in result
    assert "Messages sent:" in result
    assert "Uptime:" in result
    assert "Messages per hour:" in result
    assert "System: operational" in result

def test_event_command():
    state_machine = BotStateMachine()
    # If no event exists, event_command may return "No upcoming events found."
    result = event_command("", "+dummy", state_machine, msg_timestamp=123)
    assert isinstance(result, str)

def test_speakers_command():
    state_machine = BotStateMachine()
    # When no event exists, speakers_command should indicate so.
    result = speakers_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "No upcoming events found" in result or "No speakers assigned" in result
    # Create an event and test speakers command for that specific event.
    details = "Title: Some Event, Date: 2025-03-09, Time: 2-4PM, Location: Test Location, Description: Test Description."
    plan_response = plan_event_command(details, "+dummy", state_machine, msg_timestamp=123)
    result_event = speakers_command("Some Event", "+dummy", state_machine, msg_timestamp=123)
    assert "No speakers assigned" in result_event

def test_plan_event_command():
    state_machine = BotStateMachine()
    # Test interactive plan event (empty args should return instructions)
    response_interactive = plan_event_command("", "+dummy", state_machine, msg_timestamp=123)
    assert "Plan Event:" in response_interactive
    assert "Please reply with event details" in response_interactive
    # Test immediate event creation
    details = "Title: Test Event, Date: 2025-03-09, Time: 2-4PM, Location: 123 Main St, Description: This is a test event."
    response_immediate = plan_event_command(details, "+dummy", state_machine, msg_timestamp=123)
    assert "created successfully" in response_immediate.lower()
    # Test cancellation via skip
    response_skip = plan_event_command("skip", "+dummy", state_machine, msg_timestamp=123)
    assert "cancelled" in response_skip.lower()

def test_edit_event_command():
    state_machine = BotStateMachine()
    # Create an event first
    details = "Title: Original Event, Date: 2025-03-09, Time: 2-4PM, Location: 123 Main St, Description: Original description."
    plan_response = plan_event_command(details, "+dummy", state_machine, msg_timestamp=123)
    # Edit the event: update title only (assume EventID is 1 in test environment)
    edit_details = "EventID: 1, Title: Edited Event"
    edit_response = edit_event_command(edit_details, "+dummy", state_machine, msg_timestamp=123)
    assert "updated successfully" in edit_response.lower()

def test_remove_event_command():
    state_machine = BotStateMachine()
    # Create an event to be removed.
    details = "Title: Removable Event, Date: 2025-03-09, Time: 2-4PM, Location: 123 Main St, Description: To be removed."
    plan_response = plan_event_command(details, "+dummy", state_machine, msg_timestamp=123)
    remove_details = "EventID: 1"
    remove_response = remove_event_command(remove_details, "+dummy", state_machine, msg_timestamp=123)
    assert "removed successfully" in remove_response.lower()

def test_add_speaker_command():
    state_machine = BotStateMachine()
    # Create an event for speaker assignment.
    details = "Title: Event With Speaker, Date: 2025-03-09, Time: 2-4PM, Location: 123 Main St, Description: Has speakers."
    plan_response = plan_event_command(details, "+dummy", state_machine, msg_timestamp=123)
    add_speaker_details = "Name: Alice, Topic: Keynote Speech"
    add_speaker_response = add_speaker_command(add_speaker_details, "+dummy", state_machine, msg_timestamp=123)
    assert "assigned" in add_speaker_response.lower()

def test_remove_speaker_command():
    state_machine = BotStateMachine()
    # Create an event and add a speaker.
    details = "Title: Event With Speaker, Date: 2025-03-09, Time: 2-4PM, Location: 123 Main St, Description: Has speakers."
    plan_response = plan_event_command(details, "+dummy", state_machine, msg_timestamp=123)
    add_speaker_details = "Name: Bob, Topic: Panel Discussion"
    add_speaker_response = add_speaker_command(add_speaker_details, "+dummy", state_machine, msg_timestamp=123)
    remove_speaker_details = "Name: Bob"
    remove_speaker_response = remove_speaker_command(remove_speaker_details, "+dummy", state_machine, msg_timestamp=123)
    assert "removed from event" in remove_speaker_response.lower()

# End of tests/plugins/test_commands.py