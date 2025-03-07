"""
tests/managers/test_pending_actions.py - Tests for the PendingActions class.
Ensures that pending registration and deletion states are properly managed.
"""

import pytest
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

# End of tests/managers/test_pending_actions.py