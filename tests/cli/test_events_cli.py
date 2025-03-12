#!/usr/bin/env python
"""
tests/cli/test_events_cli.py --- Tests for event-related CLI commands.
Verifies event listing and event speaker functionalities by using the core/event_manager functions.
"""

from tests.cli.cli_test_helpers import run_cli_command
from core.event_manager import create_event, assign_speaker

def test_list_events():
    """
    Create an event using create_event() and verify that the CLI 'list-events' command displays it.
    """
    # Create an event via the event manager.
    create_event("Test Event", "2025-03-09", "2-4PM", "Test Location", "Test Description")
    output = run_cli_command(["list-events"])["stdout"]
    assert "Test Event" in output
    assert "2025-03-09" in output

def test_list_event_speakers():
    """
    Create an event and add a speaker via assign_speaker(), then verify that the CLI 'list-event-speakers'
    command displays the speaker details.
    """
    event_id = create_event("Speaker Event", "2025-03-10", "3-5PM", "Conference Hall", "Event with speakers")
    assign_speaker(event_id, "Speaker One", "Topic A")
    output = run_cli_command(["list-event-speakers"])["stdout"]
    assert "Speaker One" in output
    assert "Topic A" in output

# End of tests/cli/test_events_cli.py