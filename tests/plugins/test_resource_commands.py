#!/usr/bin/env python
"""
tests/plugins/test_resource_commands.py - Tests for the resource command plugin.
Verifies that resource_command correctly handles usage, add, list, and remove subcommands,
including edge/negative cases.
"""

import re
import pytest
from plugins.commands.resource import resource_command
from core.state import BotStateMachine
from core.database.resources import list_resources
from core.plugin_usage import USAGE_RESOURCE

def test_resource_no_args_shows_usage():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("", sender, state_machine, msg_timestamp=123)
    assert "usage:" in response.lower() and "resource add" in response.lower()

def test_resource_add_command():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree",
                                sender, state_machine, msg_timestamp=123)
    assert "Resource added with ID" in response
    resources = list_resources("Linktree")
    assert any("OfficialLinktree" in res["title"] for res in resources)

def test_resource_list_command_with_category():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree",
                     sender, state_machine, msg_timestamp=123)
    response = resource_command("list Linktree", sender, state_machine, msg_timestamp=123)
    assert "id" in response.lower() and "linktree" in response.lower() and "officiallinktree" in response.lower()

def test_resource_list_command_all():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree",
                     sender, state_machine, msg_timestamp=123)
    resource_command("add Flyers https://example.com/flyer Flyer1",
                     sender, state_machine, msg_timestamp=123)
    response = resource_command("list", sender, state_machine, msg_timestamp=123)
    assert "officiallinktree" in response.lower() and "flyer1" in response.lower()

def test_resource_remove_command():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    add_response = resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree",
                                    sender, state_machine, msg_timestamp=123)
    import re
    match = re.search(r"Resource added with ID (\d+)", add_response)
    assert match, "No resource ID found in add output"
    resource_id = match.group(1)
    remove_response = resource_command(f"remove {resource_id}", sender, state_machine, msg_timestamp=123)
    assert f"Resource with ID {resource_id} removed" in remove_response
    list_output = resource_command("list Linktree", sender, state_machine, msg_timestamp=123)
    assert resource_id not in list_output

def test_resource_add_missing_category():
    state_machine = BotStateMachine()
    sender = "+10000000001"
    response = resource_command("add  https://example.com", sender, state_machine, msg_timestamp=123)
    assert "category is required" in response.lower()

def test_resource_add_missing_url():
    state_machine = BotStateMachine()
    sender = "+10000000002"
    response = resource_command("add Flyers", sender, state_machine, msg_timestamp=123)
    assert "url is required" in response.lower()

def test_resource_unknown_subcommand():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("foo", sender, state_machine, msg_timestamp=123)
    assert USAGE_RESOURCE.lower() in response.lower()

# End of tests/plugins/test_resource_commands.py