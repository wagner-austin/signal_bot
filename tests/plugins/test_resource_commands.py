#!/usr/bin/env python
"""
tests/plugins/test_resource_commands.py - Tests for resource command plugin.
Verifies adding and listing resources.
"""

import pytest
from plugins.commands.resource import resource_command
from core.state import BotStateMachine

def test_resource_list_command_all():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    resource_command("add Linktree https://linktr.ee/50501oc OfficialLinktree", sender, state_machine, msg_timestamp=123)
    resource_command("add Flyers https://example.com/flyer Flyer1", sender, state_machine, msg_timestamp=123)
    response = resource_command("list", sender, state_machine, msg_timestamp=123)
    assert "officiallinktree" in response.lower() and "flyer1" in response.lower()

def test_resource_list_no_resources():
    state_machine = BotStateMachine()
    sender = "+10000000000"
    response = resource_command("list", sender, state_machine, msg_timestamp=123)
    assert "no resources found" in response.lower()

# End of tests/plugins/test_resource_commands.py