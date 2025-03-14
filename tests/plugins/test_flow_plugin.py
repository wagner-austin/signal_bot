#!/usr/bin/env python
"""
tests/plugins/test_flow_plugin.py
---------------------------------
Tests for the 'flow' plugin commands: list, switch, pause, create.
"""

import pytest
from plugins.commands.flow import flow_command
from managers.user_states_manager import list_flows, get_flow_state

@pytest.fixture
def dummy_sender():
    return "+12223334444"

def test_flow_list_no_flows(dummy_sender):
    """
    If user has no flows, @bot flow list should show none.
    """
    response = flow_command("list", dummy_sender, None)
    assert "Active Flow: None" in response, "No flows yet means no active flow"

def test_flow_create_then_list(dummy_sender):
    """
    After creating a flow, it should become active and appear in flow list.
    """
    flow_command("create testflow", dummy_sender, None)
    response = flow_command("list", dummy_sender, None)
    assert "Active Flow: testflow" in response
    assert "- testflow (step=start" in response, "Default step for create_flow is 'start'"

def test_flow_switch(dummy_sender):
    """
    Create multiple flows, switch among them, verify active_flow changes.
    """
    flow_command("create flowA", dummy_sender, None)
    flow_command("create flowB", dummy_sender, None)
    # flowB is active now
    list_cmd_response = flow_command("list", dummy_sender, None)
    assert "Active Flow: flowB" in list_cmd_response
    # Switch to flowA
    flow_command("switch flowA", dummy_sender, None)
    assert get_flow_state(dummy_sender) == "flowA"

def test_flow_pause(dummy_sender):
    """
    Pause the active flow, check that active_flow is None afterwards.
    """
    flow_command("create testflow", dummy_sender, None)
    assert get_flow_state(dummy_sender) == "testflow"
    flow_command("pause", dummy_sender, None)
    assert get_flow_state(dummy_sender) == "", "Paused flow => no active flow"

def test_flow_pause_specific(dummy_sender):
    """
    Pause a named flow that was active, confirm it's paused.
    """
    flow_command("create myFlow", dummy_sender, None)
    flow_command("pause myFlow", dummy_sender, None)
    assert get_flow_state(dummy_sender) == "", "Should have no active flow after pause"

def test_unknown_subcommand(dummy_sender):
    """
    Passing an unknown subcommand to flow plugin should return an error string.
    """
    response = flow_command("foobar something", dummy_sender, None)
    assert "Unknown subcommand" in response

# End of tests/plugins/test_flow_plugin.py