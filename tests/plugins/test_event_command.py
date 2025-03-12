#!/usr/bin/env python
"""
test_event_command.py
---------------------
Verifies normal 'event' command plugin functionalities, such as successful event planning.
Negative/edge cases are now in test_plugin_negatives.py.
"""

import pytest
from plugins.commands.event import plan_event_command, edit_event_command, remove_event_command
from core.state import BotStateMachine
from managers.event_manager import list_all_events, get_event

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

# End of tests/plugins/commands/test_event_command.py