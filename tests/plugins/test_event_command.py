#!/usr/bin/env python
"""
tests/plugins/test_event_command.py
-----------------------------------
Verifies partial or invalid inputs for plan_event_command, edit_event_command,
and remove_event_command, including nonexistent IDs and missing fields.
"""

import pytest
from plugins.commands.event import plan_event_command, edit_event_command, remove_event_command
from core.state import BotStateMachine
from core.event_manager import list_events, get_event
from core.database.helpers import execute_sql

@pytest.fixture
def state_machine():
    return BotStateMachine()

def test_plan_event_no_args(state_machine):
    response = plan_event_command("", "+dummy", state_machine)
    assert "Plan Event:" in response

def test_plan_event_cancel(state_machine):
    response = plan_event_command("cancel", "+dummy", state_machine)
    assert "Event creation cancelled." in response

def test_plan_event_missing_fields(state_machine):
    # Missing one or more required fields
    response = plan_event_command("Title:Test, Date:2025-12-31", "+dummy", state_machine)
    assert "Missing one or more required fields" in response

def test_plan_event_success(state_machine):
    # Provide all required fields
    response = plan_event_command(
        "Title: My Event, Date: 2025-12-31, Time: 2PM, Location: Park, Description: Having Fun",
        "+dummy",
        state_machine
    )
    assert "created successfully with ID" in response

def test_edit_event_no_args(state_machine):
    response = edit_event_command("", "+dummy", state_machine)
    assert "Usage: @bot edit event" in response

def test_edit_event_no_eventid(state_machine):
    response = edit_event_command("title: newtitle", "+dummy", state_machine)
    assert "EventID is required" in response

def test_edit_event_invalid_eventid(state_machine):
    response = edit_event_command("EventID: abc, title: newtitle", "+dummy", state_machine)
    assert "Invalid EventID provided." in response

def test_edit_event_non_existent(state_machine):
    # Attempt to edit an event that doesn't exist
    response = edit_event_command("EventID: 9999, title: NonExistent", "+dummy", state_machine)
    assert "No event found with ID 9999 to edit." in response

def test_remove_event_no_args(state_machine):
    response = remove_event_command("", "+dummy", state_machine)
    assert "Usage: @bot remove event" in response

def test_remove_event_invalid_id(state_machine):
    response = remove_event_command("EventID: abc", "+dummy", state_machine)
    assert "Invalid EventID provided." in response

def test_remove_event_non_existent(state_machine):
    # Try removing an event that does not exist
    response = remove_event_command("EventID: 9999", "+dummy", state_machine)
    assert "No event found with ID 9999." in response

def test_remove_event_title_non_existent(state_machine):
    response = remove_event_command("Title: Unknown Title", "+dummy", state_machine)
    assert "No event found with title 'Unknown Title'." in response

# End of tests/plugins/test_event_command.py