#!/usr/bin/env python
"""
tests/cli/test_cli_tools.py – Test for cli_tools.py: Verify command-line interface dispatch.
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

# End of tests/cli/test_cli_tools.py