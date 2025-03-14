#!/usr/bin/env python
"""
tests/managers/test_user_states_manager.py
------------------------------------------
Tests for user state management with multi-flow approach.
Verifies create_flow, pause_flow, resume_flow, and legacy get_flow_state,
clear_flow_state for backward compatibility.
"""

import pytest
from managers.user_states_manager import (
    create_flow,
    get_flow_state,
    clear_flow_state,
    pause_flow,
    resume_flow,
    get_flow_data,
    set_flow_data,
    list_flows
)

PHONE = "+1234567890"

@pytest.fixture(autouse=True)
def cleanup_user_state():
    """
    Cleanup flow state after each test.
    """
    yield
    clear_flow_state(PHONE)  # ensures no active flow remains

def test_create_and_get_flow_state():
    """
    Ensures create_flow sets the active flow, and get_flow_state reflects that.
    """
    clear_flow_state(PHONE)
    create_flow(PHONE, "registration")
    assert get_flow_state(PHONE) == "registration"

def test_clear_flow_state():
    """
    Verifies that clear_flow_state sets the active flow to empty.
    """
    create_flow(PHONE, "edit")
    assert get_flow_state(PHONE) == "edit"
    clear_flow_state(PHONE)
    assert get_flow_state(PHONE) == ""

def test_pause_flow():
    """
    Tests that pausing an active flow resets get_flow_state() to empty.
    """
    create_flow(PHONE, "registration")
    assert get_flow_state(PHONE) == "registration"
    pause_flow(PHONE, "registration")
    assert get_flow_state(PHONE) == "", "Expected no active flow after pause."

def test_resume_flow():
    """
    Resume a previously created flow so it becomes active again.
    """
    create_flow(PHONE, "registration")
    pause_flow(PHONE, "registration")
    # flow is still in 'flows', but not active
    resume_flow(PHONE, "registration")
    assert get_flow_state(PHONE) == "registration"

def test_set_flow_data_and_retrieve():
    """
    Validate that we can store data in the flow's data dict and retrieve it.
    """
    create_flow(PHONE, "deletion", initial_data={"confirmed": False})
    set_flow_data(PHONE, "deletion", "reason", "testing")
    data = get_flow_data(PHONE, "deletion")
    assert data["reason"] == "testing"
    assert data["confirmed"] == False, "Expected the initial_data to still be present."

def test_list_flows_multiple():
    """
    Create multiple flows and check the listing.
    """
    create_flow(PHONE, "flow1")
    create_flow(PHONE, "flow2")
    flows_info = list_flows(PHONE)
    assert flows_info["active_flow"] == "flow2", "Latest created flow is active."
    assert "flow1" in flows_info["flows"], "Flow1 should be tracked."
    assert "flow2" in flows_info["flows"], "Flow2 should be tracked."

# End of tests/managers/test_user_states_manager.py