#!/usr/bin/env python
"""
tests/cli/test_cli_tools.py - Tests for cli_tools.py
----------------------------------------------------
Verifies command-line interface dispatch, including negative/edge case scenarios:
 - Missing required arguments
 - Invalid values (like non-integer or negative IDs)
 - Partial near-match commands
 - Missing subcommand and near-correct subcommands (typos)
"""

from tests.cli.cli_test_helpers import run_cli_command
import re

def test_cli_list_volunteers_no_volunteers():
    output = run_cli_command(["list-volunteers"])["stdout"]
    assert "No volunteers found." in output

def test_cli_add_volunteer_and_list():
    add_output = run_cli_command([
        "add-volunteer",
        "--phone", "+1111111111",
        "--name", "CLI Test Volunteer",
        "--skills", "Testing,CLI",
        "--available", "1",
        "--role", "Tester"
    ])["stdout"]
    list_output = run_cli_command(["list-volunteers"])["stdout"]
    assert "CLI Test Volunteer" in list_output

def test_cli_list_events_no_events():
    output = run_cli_command(["list-events"])["stdout"]
    assert "No events found." in output or "No upcoming events found." in output

def test_cli_list_logs_no_logs():
    output = run_cli_command(["list-logs"])["stdout"]
    assert "No command logs found." in output

def test_cli_list_resources_no_resources():
    output = run_cli_command(["list-resources"])["stdout"]
    assert "No resources found." in output

def test_cli_list_tasks_no_tasks():
    output = run_cli_command(["list-tasks"])["stdout"]
    assert "No tasks found." in output

def test_cli_unknown_command():
    """
    Test that calling cli_tools.py with an unknown command prints usage or help text.
    """
    output_data = run_cli_command(["foobar"])
    stdout = output_data["stdout"]
    stderr = output_data["stderr"]
    # Expect the CLI to print usage instructions
    assert "usage:" in stdout.lower() or "usage:" in stderr.lower()

def test_cli_add_volunteer_missing_phone():
    """
    Verify usage/help is displayed when --phone is missing (argparse enforced).
    """
    output_data = run_cli_command([
        "add-volunteer",
        "--name", "NoPhone"
    ])
    stderr = output_data["stderr"].lower()
    assert "usage:" in stderr
    assert "the following arguments are required: --phone" in stderr

def test_cli_add_volunteer_missing_name():
    """
    Verify usage/help is displayed when --name is missing (argparse enforced).
    """
    output_data = run_cli_command([
        "add-volunteer",
        "--phone", "+9999999999"
    ])
    stderr = output_data["stderr"].lower()
    assert "usage:" in stderr
    assert "the following arguments are required: --name" in stderr

def test_cli_add_volunteer_invalid_available():
    """
    Check that invalid availability (not 0 or 1) prints an error.
    """
    output_data = run_cli_command([
        "add-volunteer",
        "--phone", "+2222222222",
        "--name", "BadAvail",
        "--skills", "None",
        "--available", "xyz"  # invalid
    ])
    stdout = output_data["stdout"].lower()
    stderr = output_data["stderr"].lower()
    # Manager now prints "error: available must be 0 or 1."
    expected_substr = "error: available must be 0 or 1"
    assert expected_substr in stdout or expected_substr in stderr

def test_cli_partial_known_command():
    """
    Test that a partial near-match command like 'list-volunteerz' also shows usage.
    """
    output_data = run_cli_command(["list-volunteerz"])
    stdout = output_data["stdout"].lower()
    stderr = output_data["stderr"].lower()
    assert "usage:" in stdout or "usage:" in stderr

def test_cli_no_subcommand():
    """
    Verify that calling cli_tools.py without any subcommand prints top-level help.
    """
    output_data = run_cli_command([])
    stdout = output_data["stdout"].lower()
    stderr = output_data["stderr"].lower()
    # Expect help text with usage information if no subcommand is provided.
    assert "usage:" in stdout or "usage:" in stderr

def test_cli_almost_correct_subcommand():
    """
    Verify that calling an almost-correct subcommand, e.g. list-eventz, prints usage help.
    """
    output_data = run_cli_command(["list-eventz"])
    stdout = output_data["stdout"].lower()
    stderr = output_data["stderr"].lower()
    assert "usage:" in stdout or "usage:" in stderr

# -----------------------
# NEW TESTS FOR COVERAGE
# -----------------------

def test_cli_add_volunteer_invalid_phone():
    """
    Test that passing an invalid phone format results in an error message from the manager.
    We expect to see 'invalid phone number format' in stdout or stderr.
    """
    output_data = run_cli_command([
        "add-volunteer",
        "--phone", "ABCD1234",  # invalid phone format
        "--name", "Wrong Phone",
        "--skills", "CLI",
        "--available", "1"
    ])
    stdout = output_data["stdout"].lower()
    stderr = output_data["stderr"].lower()
    # Manager should raise VolunteerError about phone format
    assert "invalid phone number format" in stdout or "invalid phone number format" in stderr

def test_cli_list_deleted_volunteers_no_results():
    """
    Test that calling list-deleted-volunteers prints 'No deleted volunteers found.' if none exist.
    """
    output = run_cli_command(["list-deleted-volunteers"])["stdout"].lower()
    assert "no deleted volunteers found" in output

def test_cli_list_deleted_volunteers_partial():
    """
    Test a partial near-match command like 'list-deleted-volunteerse' also shows usage help.
    """
    output_data = run_cli_command(["list-deleted-volunteerse"])
    stdout = output_data["stdout"].lower()
    stderr = output_data["stderr"].lower()
    assert "usage:" in stdout or "usage:" in stderr

# End of tests/cli/test_cli_tools.py