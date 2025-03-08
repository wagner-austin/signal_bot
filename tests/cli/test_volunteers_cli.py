#!/usr/bin/env python
"""
tests/cli/test_volunteers_cli.py - Tests for volunteer-related CLI commands.
Verifies volunteer addition, listing, and deletion functionalities.
"""

from tests.cli.cli_test_helpers import run_cli_command
from tests.test_helpers import insert_record

def test_add_and_list_volunteer():
    # Ensure no volunteers initially.
    output = run_cli_command(["list-volunteers"])["stdout"]
    assert "No volunteers found." in output

    # Add a volunteer.
    add_output = run_cli_command([
        "add-volunteer",
        "--phone", "+1111111111",
        "--name", "John Doe",
        "--skills", "Python,SQL",
        "--available", "1",
        "--role", "Coordinator"
    ])["stdout"]
    assert "Volunteer 'John Doe' added" in add_output

    # List volunteers and verify.
    list_output = run_cli_command(["list-volunteers"])["stdout"]
    assert "John Doe" in list_output
    # Phone numbers are visible via CLI.
    assert "+1111111111" in list_output

def test_list_deleted_volunteers():
    # Insert a deleted volunteer record manually using helper.
    insert_record(
        "INSERT INTO DeletedVolunteers (phone, name, skills, available, current_role) VALUES (?, ?, ?, ?, ?)",
        ("+2222222222", "Deleted Volunteer", "SkillA,SkillB", 0, "")
    )

    output = run_cli_command(["list-deleted-volunteers"])["stdout"]
    assert "Deleted Volunteer" in output
    assert "+2222222222" in output

# End of tests/cli/test_volunteers_cli.py