#!/usr/bin/env python
"""
tests/core/test_messages.py - Tests for core/messages constants.
Verifies that key message constants are defined and non-empty, including new unified interactive prompts.
"""

import plugins.messages as messages

def test_registration_prompt():
    assert messages.REGISTRATION_WELCOME and isinstance(messages.REGISTRATION_WELCOME, str)

def test_already_registered():
    formatted = messages.ALREADY_REGISTERED.format(name="Test")
    assert "Test" in formatted

def test_edit_prompt():
    formatted = messages.EDIT_PROMPT.format(name="Test")
    assert "Test" in formatted

def test_deletion_prompts():
    assert messages.DELETION_PROMPT
    assert messages.DELETION_CANCELED

def test_new_volunteer_registered():
    formatted = messages.NEW_VOLUNTEER_REGISTERED.format(name="Test")
    assert "Test" in formatted

# New tests for unified interactive constants
def test_registration_welcome():
    assert messages.REGISTRATION_WELCOME and isinstance(messages.REGISTRATION_WELCOME, str)
    assert "register" in messages.REGISTRATION_WELCOME.lower()

def test_deletion_confirm():
    assert messages.DELETION_CONFIRM and isinstance(messages.DELETION_CONFIRM, str)
    assert "delete" in messages.DELETION_CONFIRM.lower()

def test_getting_started():
    assert messages.GETTING_STARTED and isinstance(messages.GETTING_STARTED, str)
    assert "help" in messages.GETTING_STARTED.lower()

# End of tests/core/test_messages.py