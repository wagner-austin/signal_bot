#!/usr/bin/env python
"""
tests/cli/test_cli_tools.py – Test for cli_tools.py: Verify command-line interface dispatch.
Also tests unknown commands for usage/help output, including edge cases and invalid flags.
"""

from tests.cli.cli_test_helpers import run_cli_command

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

# -------------------------------
# New Negative / Edge Case Tests
# -------------------------------

def test_cli_add_volunteer_missing_phone():
    """
    Verify usage/help is displayed when --phone is missing (argparse enforced).
    """
    output_data = run_cli_command([
        "add-volunteer",
        "--name", "NoPhone"
    ])
    stderr = output_data["stderr"].lower()
    # Argparse error typically prints to stderr
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

    # We expect our custom error message or usage to appear
    # The code in cli_tools.py catches ValueError and prints the message.
    assert "error parsing --available value:" in stdout or "error parsing --available value:" in stderr

# End of tests/cli/test_cli_tools.py