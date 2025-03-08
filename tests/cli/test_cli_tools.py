#!/usr/bin/env python
"""
tests/cli/test_cli_tools.py - Tests for the CLI Tools Aggregated Facade.
Verifies that all CLI commands (volunteers, events, logs, resources, tasks, etc.) work as expected.
"""

import sys
import io
from core.database.connection import get_connection
from core.database.helpers import execute_sql

def run_cli_command(command_args):
    """
    run_cli_command - Helper function to simulate command-line invocation of cli_tools.py.
    
    Args:
        command_args (list): List of command arguments.
    
    Returns:
        str: Captured output from running the command.
    """
    original_argv = sys.argv
    original_stdout = sys.stdout
    try:
        sys.argv = ["cli_tools.py"] + command_args
        captured_output = io.StringIO()
        sys.stdout = captured_output
        from cli_tools import main as cli_main
        try:
            cli_main()
        except SystemExit:
            pass
        return captured_output.getvalue()
    finally:
        sys.argv = original_argv
        sys.stdout = original_stdout

def test_add_and_list_volunteer():
    # Ensure no volunteers initially.
    output = run_cli_command(["list-volunteers"])
    assert "No volunteers found." in output

    # Add a volunteer.
    add_output = run_cli_command([
        "add-volunteer",
        "--phone", "+1111111111",
        "--name", "John Doe",
        "--skills", "Python,SQL",
        "--available", "1",
        "--role", "Coordinator"
    ])
    assert "Volunteer 'John Doe' added" in add_output

    # List volunteers and verify.
    list_output = run_cli_command(["list-volunteers"])
    assert "John Doe" in list_output
    # Phone numbers are visible via CLI.
    assert "+1111111111" in list_output

def test_list_deleted_volunteers():
    # Insert a deleted volunteer record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO DeletedVolunteers (phone, name, skills, available, current_role) VALUES (?, ?, ?, ?, ?)",
        ("+2222222222", "Deleted Volunteer", "SkillA,SkillB", 0, "")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-deleted-volunteers"])
    assert "Deleted Volunteer" in output
    assert "+2222222222" in output

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

def test_list_logs():
    # Insert a command log record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO CommandLogs (sender, command, args) VALUES (?, ?, ?)",
        ("+3333333333", "test", "arg1 arg2")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-logs"])
    assert "test" in output
    assert "+3333333333" in output

def test_list_resources_and_add_remove_resource():
    # Ensure no resources initially.
    output = run_cli_command(["list-resources"])
    assert "No resources found." in output

    # Add a resource using CLI.
    add_output = run_cli_command([
        "add-resource",
        "--category", "Linktree",
        "--url", "https://linktr.ee/50501oc",
        "--title", "Official Linktree"
    ])
    assert "Resource added with ID" in add_output

    # List resources and verify.
    list_output = run_cli_command(["list-resources"])
    assert "Official Linktree" in list_output

    # Extract resource ID from the add_output.
    parts = add_output.strip().split()
    resource_id = parts[-1].strip(".")
    
    # Remove the resource.
    remove_output = run_cli_command([
        "remove-resource",
        "--id", resource_id
    ])
    assert f"Resource with ID {resource_id} removed" in remove_output

    # Verify resource no longer appears.
    list_output_after = run_cli_command(["list-resources"])
    assert "Official Linktree" not in list_output_after

def test_list_tasks():
    # Insert a task record manually.
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Tasks (description, created_by, status) VALUES (?, ?, ?)",
        ("Test Task", "+4444444444", "open")
    )
    conn.commit()
    conn.close()

    output = run_cli_command(["list-tasks"])
    assert "Test Task" in output
    # Since no volunteer exists for +4444444444, created_by_name should be "Unknown".
    assert "Unknown" in output

# End of tests/cli/test_cli_tools.py