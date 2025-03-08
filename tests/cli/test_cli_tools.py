#!/usr/bin/env python
"""
tests/cli/test_cli_tools.py - Tests for the CLI Tools.
Verifies that new commands for listing deleted volunteers, event speakers, and tasks work as expected.
"""

import sys
import io
from core.database.connection import get_connection

def run_cli_command(command_args):
    # Backup original sys.argv and stdout
    original_argv = sys.argv
    original_stdout = sys.stdout
    try:
        sys.argv = ["cli_tools.py"] + command_args
        captured_output = io.StringIO()
        sys.stdout = captured_output
        # Import here to ensure our modified sys.argv is used
        from cli_tools import main as cli_main
        try:
            cli_main()
        except SystemExit:
            pass
        return captured_output.getvalue()
    finally:
        sys.argv = original_argv
        sys.stdout = original_stdout

def test_list_deleted_volunteers_cli():
    # Insert a deleted volunteer record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO DeletedVolunteers (phone, name, skills, available, current_role) VALUES (?, ?, ?, ?, ?)",
        ("+3333333333", "Deleted Volunteer", "Skill1,Skill2", 0, "")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-deleted-volunteers"])
    assert "Deleted Volunteer" in output
    # CLI Tools are allowed to display phone numbers.
    assert "+3333333333" in output

def test_list_event_speakers_cli():
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

def test_list_tasks_cli():
    # Insert a task record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Tasks (description, created_by, assigned_to, status) VALUES (?, ?, ?, ?)",
        ("Test Task", "+4444444444", None, "open")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-tasks"])
    assert "Test Task" in output
    # Since no volunteer record exists for +4444444444, created_by_name should be "Unknown".
    assert "Unknown" in output

# End of tests/cli/test_cli_tools.py