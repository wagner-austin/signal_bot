#!/usr/bin/env python
"""
tests/managers/test_base_pending_handler.py - Unit tests for BasePendingHandler.
Tests the functionality of has_pending, get_pending, and clear_pending methods.
"""

import pytest
from managers.message.base_pending_handler import BasePendingHandler

class DummyPendingHandler(BasePendingHandler):
    def __init__(self):
        # For testing, we define simple functions using an internal dict.
        self.state = {}
        super().__init__(self, self.has, self.get, self.clear)

    def has(self, sender: str) -> bool:
        return sender in self.state

    def get(self, sender: str):
        return self.state.get(sender)

    def clear(self, sender: str) -> None:
        if sender in self.state:
            del self.state[sender]

    def set(self, sender: str, value):
        self.state[sender] = value

def test_base_pending_handler_methods():
    handler = DummyPendingHandler()
    sender = "+1234567890"
    
    # Initially, no pending state.
    assert not handler.has_pending(sender)
    assert handler.get_pending(sender) is None
    
    # Set a pending state.
    handler.set(sender, "test_state")
    assert handler.has_pending(sender)
    assert handler.get_pending(sender) == "test_state"
    
    # Clear pending state.
    handler.clear_pending(sender)
    assert not handler.has_pending(sender)
    assert handler.get_pending(sender) is None

# End tests/managers/test_base_pending_handler.py