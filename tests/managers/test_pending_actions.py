#!/usr/bin/env python
"""
tests/managers/test_pending_actions.py - Tests for the PendingActions class.
Ensures that pending registration and deletion states are properly managed,
including concurrent access using thread pools to simulate multiple threads.
"""

import pytest
import concurrent.futures
from managers.pending_actions import PendingActions

@pytest.fixture
def pending_actions():
    """
    Provides a fresh instance of PendingActions for each test.
    """
    return PendingActions()

def test_set_and_get_registration(pending_actions):
    sender = "+1234567890"
    mode = "register"
    # Initially, there should be no registration
    assert not pending_actions.has_registration(sender)
    # Set a registration state
    pending_actions.set_registration(sender, mode)
    # Check that registration exists and the mode is correct
    assert pending_actions.has_registration(sender)
    assert pending_actions.get_registration(sender) == mode

def test_clear_registration(pending_actions):
    sender = "+1234567890"
    mode = "edit"
    pending_actions.set_registration(sender, mode)
    # Ensure the registration state is set
    assert pending_actions.has_registration(sender)
    # Clear the registration state
    pending_actions.clear_registration(sender)
    # Confirm the state is cleared
    assert not pending_actions.has_registration(sender)
    assert pending_actions.get_registration(sender) is None

def test_set_and_get_deletion(pending_actions):
    sender = "+1234567890"
    mode = "initial"
    # Initially, there should be no deletion state
    assert not pending_actions.has_deletion(sender)
    # Set a deletion state
    pending_actions.set_deletion(sender, mode)
    # Check that deletion state exists and the mode is correct
    assert pending_actions.has_deletion(sender)
    assert pending_actions.get_deletion(sender) == mode

def test_clear_deletion(pending_actions):
    sender = "+1234567890"
    mode = "confirm"
    pending_actions.set_deletion(sender, mode)
    # Ensure the deletion state is set
    assert pending_actions.has_deletion(sender)
    # Clear the deletion state
    pending_actions.clear_deletion(sender)
    # Confirm the state is cleared
    assert not pending_actions.has_deletion(sender)
    assert pending_actions.get_deletion(sender) is None

# --- Concurrent Tests for Thread Safety ---

def concurrent_set_registration(pending_actions, sender, mode):
    pending_actions.set_registration(sender, mode)
    return pending_actions.get_registration(sender)

def test_concurrent_registration(pending_actions):
    sender = "+9999999999"
    modes = ["mode1", "mode2", "mode3", "mode4", "mode5"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(concurrent_set_registration, pending_actions, sender, mode) for mode in modes]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    # Every result should be one of the allowed modes.
    for result in results:
        assert result in modes
    # Check that the final registration for the sender is one of the modes.
    final_mode = pending_actions.get_registration(sender)
    assert final_mode in modes

def concurrent_clear_registration(pending_actions, sender):
    pending_actions.clear_registration(sender)
    return pending_actions.has_registration(sender)

def test_concurrent_clear_registration(pending_actions):
    sender = "+8888888888"
    pending_actions.set_registration(sender, "initial")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(concurrent_clear_registration, pending_actions, sender) for _ in range(5)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    for result in results:
        assert result is False
    assert pending_actions.get_registration(sender) is None

def concurrent_set_deletion(pending_actions, sender, mode):
    pending_actions.set_deletion(sender, mode)
    return pending_actions.get_deletion(sender)

def test_concurrent_deletion(pending_actions):
    sender = "+7777777777"
    modes = ["init", "confirm", "final"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(concurrent_set_deletion, pending_actions, sender, mode) for mode in modes]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    for result in results:
        assert result in modes
    final_mode = pending_actions.get_deletion(sender)
    assert final_mode in modes

def concurrent_clear_deletion(pending_actions, sender):
    pending_actions.clear_deletion(sender)
    return pending_actions.has_deletion(sender)

def test_concurrent_clear_deletion(pending_actions):
    sender = "+6666666666"
    pending_actions.set_deletion(sender, "init")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(concurrent_clear_deletion, pending_actions, sender) for _ in range(3)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    for result in results:
        assert result is False
    assert pending_actions.get_deletion(sender) is None

# End of tests/managers/test_pending_actions.py