#!/usr/bin/env python
"""
tests/managers/test_user_states_manager.py --- Tests for user state management.
Verifies that set_flow_state, get_flow_state, and clear_flow_state work correctly.
"""
import pytest
from managers.user_states_manager import set_flow_state, get_flow_state, clear_flow_state

@pytest.fixture(autouse=True)
def cleanup_user_state():
    yield
    phone = "+1234567890"
    clear_flow_state(phone)

def test_set_and_get_flow_state():
    phone = "+1234567890"
    clear_flow_state(phone)
    set_flow_state(phone, "registration")
    state = get_flow_state(phone)
    assert state == "registration", f"Expected 'registration', got '{state}'"

def test_clear_flow_state():
    phone = "+1234567890"
    set_flow_state(phone, "edit")
    state = get_flow_state(phone)
    assert state == "edit", f"Expected 'edit', got '{state}'"
    clear_flow_state(phone)
    state_after = get_flow_state(phone)
    assert state_after == "", f"Expected empty state after clear, got '{state_after}'"

def test_multiple_flow_state_updates():
    phone = "+1234567890"
    clear_flow_state(phone)
    set_flow_state(phone, "registration")
    state = get_flow_state(phone)
    assert state == "registration"
    set_flow_state(phone, "deletion")
    state2 = get_flow_state(phone)
    assert state2 == "deletion", f"Expected 'deletion', got '{state2}'"
    set_flow_state(phone, "deletion")
    state3 = get_flow_state(phone)
    assert state3 == "deletion"

# End of tests/managers/test_user_states_manager.py