#!/usr/bin/env python
"""
tests/managers/test_volunteer_common.py - Tests for volunteer common utilities.
Verifies that the normalize_name function hides phone numbers from user-facing outputs.
"""

import pytest
from managers.volunteer.volunteer_common import normalize_name

def test_normalize_name_same_as_fallback():
    # If the name is exactly the same as the fallback phone, return "Anonymous".
    phone = "+5555555555"
    assert normalize_name(phone, phone) == "Anonymous"

def test_normalize_name_phone_pattern():
    # If the provided name matches a phone number pattern even if not equal to fallback, return "Anonymous".
    fallback = "+1234567890"
    assert normalize_name("+5555555555", fallback) == "Anonymous"

def test_normalize_name_valid_name():
    phone = "+5555555555"
    name = "John Doe"
    assert normalize_name(name, phone) == "John Doe"

# End of tests/managers/test_volunteer_common.py