"""
tests/managers/test_volunteer_manager.py – Tests for volunteer management functionalities.
Verifies that operations like sign_up, check_in, delete_volunteer, and volunteer_status work correctly.
"""

import pytest
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.database import get_volunteer_record, get_connection

def test_volunteer_status_empty():
    # Initially, no volunteer exists.
    status = VOLUNTEER_MANAGER.volunteer_status()
    assert status == ""

def test_sign_up_and_status():
    phone = "+10000000001"
    name = "John Doe"
    result = VOLUNTEER_MANAGER.sign_up(phone, name, ["Public Speaking"])
    assert "registered" in result.lower() or "updated" in result.lower()
    status = VOLUNTEER_MANAGER.volunteer_status()
    assert "John Doe" in status
    assert "Available" in status
    assert "Current Role: None" in status

def test_check_in():
    phone = "+10000000002"
    name = "Jane Smith"
    VOLUNTEER_MANAGER.sign_up(phone, name, ["Greeter"])
    result = VOLUNTEER_MANAGER.check_in(phone)
    assert "checked in" in result.lower()

def test_delete_volunteer():
    phone = "+10000000003"
    name = "Alice Johnson"
    VOLUNTEER_MANAGER.sign_up(phone, name, ["Logistics Oversight"])
    result = VOLUNTEER_MANAGER.delete_volunteer(phone)
    assert "deleted" in result.lower()
    record = get_volunteer_record(phone)
    assert record is None

# End of tests/managers/test_volunteer_manager.py