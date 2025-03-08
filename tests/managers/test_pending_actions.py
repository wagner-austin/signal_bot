#!/usr/bin/env python
"""
tests/managers/test_pending_actions.py
--------------------------------------
Tests for the PendingActions class.
Ensures that pending registration, deletion, and event creation states
are properly managed, including concurrent access using thread pools.

NEW/CHANGED:
  - Added test_concurrent_edit_registration to simulate multiple threads
    setting an 'edit' registration for the same user concurrently.
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

def test_set_and_get_event_creation(pending_actions):
    sender = "+1234567899"
    # Initially, no event creation is pending
    assert not pending_actions.has_event_creation(sender)
    pending_actions.set_event_creation(sender)
    assert pending_actions.has_event_creation(sender)

def test_clear_event_creation(pending_actions):
    sender = "+1111111111"
    pending_actions.set_event_creation(sender)
    assert pending_actions.has_event_creation(sender)
    pending_actions.clear_event_creation(sender)
    assert not pending_actions.has_event_creation(sender)

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

def concurrent_set_event_creation(pending_actions, sender):
    pending_actions.set_event_creation(sender)
    return pending_actions.has_event_creation(sender)

def test_concurrent_event_creation_set(pending_actions):
    """
    Test concurrency for setting event creation states.
    """
    sender = "+5555555555"
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(concurrent_set_event_creation, pending_actions, sender) for _ in range(4)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    # All results should be True after setting event creation.
    for res in results:
        assert res is True
    assert pending_actions.has_event_creation(sender)

def concurrent_clear_event_creation(pending_actions, sender):
    pending_actions.clear_event_creation(sender)
    return pending_actions.has_event_creation(sender)

def test_concurrent_event_creation_clear(pending_actions):
    """
    Test concurrency for clearing event creation states.
    """
    sender = "+5555555556"
    pending_actions.set_event_creation(sender)
    assert pending_actions.has_event_creation(sender)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(concurrent_clear_event_creation, pending_actions, sender) for _ in range(4)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    # All results should be False after clearing event creation.
    for res in results:
        assert res is False
    assert not pending_actions.has_event_creation(sender)


# -----------------------------------------------------------------
# NEW TEST: Concurrent "edit" registrations for the same user
# -----------------------------------------------------------------

def test_concurrent_edit_registration(pending_actions):
    """
    Tests that multiple threads trying to set an 'edit' registration for the same sender
    do not produce any race conditions or partial states.
    """
    sender = "+9999999998"
    modes = ["edit1", "edit2", "edit3", "edit4"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(concurrent_set_registration, pending_actions, sender, mode) for mode in modes]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # Ensure each concurrency call returns one of the modes
    for result in results:
        assert result in modes

    # The final registration mode for the sender must be one of the 'editN'.
    final_mode = pending_actions.get_registration(sender)
    assert final_mode in modes

# End of tests/managers/test_pending_actions.py