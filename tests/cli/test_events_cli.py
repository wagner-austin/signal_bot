#!/usr/bin/env python
"""
tests/cli/test_events_cli.py - Tests for event-related CLI commands.
Verifies event listing and event speakers functionalities using robust output extraction.
"""

from tests.cli.cli_test_helpers import run_cli_command
from tests.test_helpers import insert_record

def test_list_events():
    # Insert an event record manually using helper.
    insert_record(
        "INSERT INTO Events (title, date, time, location, description) VALUES (?, ?, ?, ?, ?)",
        ("Test Event", "2025-03-09", "2-4PM", "Test Location", "Test Description")
    )

    output = run_cli_command(["list-events"])["stdout"]
    assert "Test Event" in output
    assert "2025-03-09" in output

def test_list_event_speakers():
    # Insert an event speaker record manually using helper.
    insert_record(
        "INSERT INTO EventSpeakers (event_id, speaker_name, speaker_topic) VALUES (?, ?, ?)",
        (1, "Speaker One", "Topic A")
    )

    output = run_cli_command(["list-event-speakers"])["stdout"]
    assert "Speaker One" in output
    assert "Topic A" in output

# End of tests/cli/test_events_cli.py