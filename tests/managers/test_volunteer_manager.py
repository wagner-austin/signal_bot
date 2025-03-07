"""
tests/managers/test_volunteer_manager.py - Tests for volunteer management functionalities.
Verifies that operations like sign‑up, check‑in, deletion, and status retrieval work correctly using parameterized tests.
"""

import pytest
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.database import get_volunteer_record

@pytest.mark.parametrize(
    "phone, name, skills, expected_substring",
    [
        ("+10000000001", "John Doe", ["Public Speaking"], "John Doe"),
        ("+10000000002", "Jane Smith", ["Greeter"], "Jane Smith"),
        ("+10000000003", "Alice Johnson", ["Logistics Oversight"], "Alice Johnson"),
    ]
)
def test_sign_up_and_status(phone, name, skills, expected_substring):
    result = VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    assert "registered" in result.lower() or "updated" in result.lower()
    status = VOLUNTEER_MANAGER.volunteer_status()
    assert expected_substring in status

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+10000000002", "Jane Smith", ["Greeter"]),
    ]
)
def test_check_in(phone, name, skills):
    VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    result = VOLUNTEER_MANAGER.check_in(phone)
    assert "checked in" in result.lower()

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+10000000003", "Alice Johnson", ["Logistics Oversight"]),
    ]
)
def test_delete_volunteer(phone, name, skills):
    VOLUNTEER_MANAGER.sign_up(phone, name, skills)
    result = VOLUNTEER_MANAGER.delete_volunteer(phone)
    assert "deleted" in result.lower()
    record = get_volunteer_record(phone)
    assert record is None

def test_volunteer_status_empty():
    # If no volunteer exists, volunteer_status should return an empty string.
    status = VOLUNTEER_MANAGER.volunteer_status()
    assert status == ""

# End of tests/managers/test_volunteer_manager.py