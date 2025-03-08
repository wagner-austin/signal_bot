#!/usr/bin/env python
"""
tests/cli/test_resources_cli.py - Tests for resource-related CLI commands.
Verifies resource addition, listing, and removal functionalities.
"""

from tests.cli.cli_test_helpers import run_cli_command

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

# End of tests/cli/test_resources_cli.py