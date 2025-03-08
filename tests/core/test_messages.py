#!/usr/bin/env python
"""
tests/core/test_messages.py - Tests for core/messages.
Verifies that key message constants are defined and non-empty.
"""
import core.messages as messages

def test_registration_prompt():
    assert messages.REGISTRATION_PROMPT and isinstance(messages.REGISTRATION_PROMPT, str)

def test_already_registered():
    formatted = messages.ALREADY_REGISTERED.format(name="Test")
    assert "Test" in formatted

def test_edit_prompt():
    formatted = messages.EDIT_PROMPT.format(name="Test")
    assert "Test" in formatted

def test_deletion_prompts():
    assert messages.DELETION_PROMPT
    assert messages.DELETION_CONFIRM_PROMPT
    assert messages.DELETION_CANCELED

def test_feedback_usage():
    assert "Usage:" in messages.FEEDBACK_USAGE

def test_new_volunteer_registered():
    formatted = messages.NEW_VOLUNTEER_REGISTERED.format(name="Test")
    assert "Test" in formatted

# End of tests/core/test_messages.py