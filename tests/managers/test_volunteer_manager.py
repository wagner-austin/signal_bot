"""
tests/managers/test_volunteer_manager.py - Tests for volunteer manager functionalities.
This module tests sign-up, status, check-in, and deletion of volunteer records using a temporary test database.
"""

import pytest
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.database import get_volunteer_record, get_connection

@pytest.fixture(autouse=True)
def clear_volunteers():
    """
    Clears the Volunteers table before each test.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Volunteers")
    conn.commit()
    conn.close()
    yield
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Volunteers")
    conn.commit()
    conn.close()

def test_volunteer_status_empty():
    # Initially, no volunteer exists.
    status = VOLUNTEER_MANAGER.volunteer_status()
    # Expect an empty string when no volunteers are registered.
    assert status == ""

def test_sign_up_and_status():
    # Sign up a new volunteer.
    phone = "+10000000001"
    name = "John Doe"
    result = VOLUNTEER_MANAGER.sign_up(phone, name, ["Public Speaking"])
    assert "registered" in result.lower() or "updated" in result.lower()
    
    # Check volunteer status should now list the volunteer.
    status = VOLUNTEER_MANAGER.volunteer_status()
    # The status should contain the volunteer's name, availability, and current role.
    assert "John Doe" in status
    assert "Available" in status
    assert "Current Role: None" in status

def test_check_in():
    phone = "+10000000002"
    name = "Jane Smith"
    # First, sign up a volunteer.
    VOLUNTEER_MANAGER.sign_up(phone, name, ["Greeter"])
    # Now, check in the volunteer.
    result = VOLUNTEER_MANAGER.check_in(phone)
    assert "checked in" in result.lower()

def test_delete_volunteer():
    phone = "+10000000003"
    name = "Alice Johnson"
    # Sign up volunteer.
    VOLUNTEER_MANAGER.sign_up(phone, name, ["Logistics Oversight"])
    # Delete volunteer.
    result = VOLUNTEER_MANAGER.delete_volunteer(phone)
    assert "deleted" in result.lower()
    # Ensure the volunteer record is no longer active.
    record = get_volunteer_record(phone)
    assert record is None

# End of tests/managers/test_volunteer_manager.py
