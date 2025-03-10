#!/usr/bin/env python
"""
tests/cli/test_resources_cli.py - Tests for resource-related CLI commands.
Verifies resource addition, listing, and removal functionalities using robust extraction
of resource IDs via regular expressions.
"""

import re
from tests.cli.cli_test_helpers import run_cli_command

def test_list_resources_and_add_remove_resource():
    # Ensure no resources initially.
    output = run_cli_command(["list-resources"])["stdout"]
    assert "No resources found." in output

    # Add a resource using CLI.
    add_output = run_cli_command([
        "add-resource",
        "--category", "Linktree",
        "--url", "https://linktr.ee/50501oc",
        "--title", "Official Linktree"
    ])["stdout"]
    assert "Resource added with ID" in add_output

    # List resources and verify.
    list_output = run_cli_command(["list-resources"])["stdout"]
    assert "Official Linktree" in list_output

    # Extract resource ID from the add_output using regex.
    match = re.search(r"Resource added with ID (\d+)", add_output)
    assert match is not None, "Resource ID not found in add_output"
    resource_id = match.group(1)

    # Remove the resource.
    remove_output = run_cli_command([
        "remove-resource",
        "--id", resource_id
    ])["stdout"]
    assert f"Resource with ID {resource_id} removed" in remove_output

    # Verify resource no longer appears.
    list_output_after = run_cli_command(["list-resources"])["stdout"]
    assert "Official Linktree" not in list_output_after

# End of tests/cli/test_resources_cli.py