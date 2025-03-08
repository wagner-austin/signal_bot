#!/usr/bin/env python
"""
tests/cli/test_events_cli.py - Tests for event-related CLI commands.
Verifies event listing and event speakers functionalities.
"""

from core.database.connection import get_connection
from tests.cli.cli_test_helpers import run_cli_command

def test_list_events():
    # Insert an event record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Events (title, date, time, location, description) VALUES (?, ?, ?, ?, ?)",
        ("Test Event", "2025-03-09", "2-4PM", "Test Location", "Test Description")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-events"])
    assert "Test Event" in output
    assert "2025-03-09" in output

def test_list_event_speakers():
    # Insert an event speaker record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO EventSpeakers (event_id, speaker_name, speaker_topic) VALUES (?, ?, ?)",
        (1, "Speaker One", "Topic A")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-event-speakers"])
    assert "Speaker One" in output
    assert "Topic A" in output

# End of tests/cli/test_events_cli.py