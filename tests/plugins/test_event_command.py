#!/usr/bin/env python
"""
tests/plugins/test_event_command.py - Verifies normal 'event' command plugin functionalities.
Ensures successful event planning and also tests partial event creation (interactive flow) for missing fields.
"""

import pytest
from plugins.commands.event import plan_event_command, edit_event_command, remove_event_command
from core.state import BotStateMachine
from managers.event_manager import list_all_events, get_event
from core.plugin_usage import USAGE_PLAN_EVENT_PARTIAL

@pytest.fixture
def state_machine():
    return BotStateMachine()

def test_plan_event_success(state_machine):
    # Provide all required fields
    response = plan_event_command(
        "Title: My Event, Date: 2025-12-31, Time: 2PM, Location: Park, Description: Having Fun",
        "+dummy",
        state_machine
    )
    assert "created successfully with ID" in response

def test_plan_event_partial(state_machine):
    # Provide incomplete event data: missing time, location, and description
    response = plan_event_command(
        "Title: Partial Event, Date: 2025-12-31",
        "+dummy",
        state_machine
    )
    # Expect a message indicating missing required fields along with the partial usage prompt.
    assert "missing required fields" in response.lower() or USAGE_PLAN_EVENT_PARTIAL.lower() in response.lower()

# End of tests/plugins/test_event_command.py