"""
tests/plugins/test_volunteer_commands.py - Tests for volunteer command plugins.
This module tests commands related to volunteer registration and modification.
"""

import pytest
from plugins.commands.volunteer import register_command, delete_command
from core.state import BotStateMachine
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

def test_register_command_new_user():
    phone = "+20000000001"
    state_machine = BotStateMachine()
    response = register_command("Alice Smith", phone, state_machine, msg_timestamp=123)
    # Should register new volunteer.
    assert "registered" in response.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    assert record.get("name").lower() == "alice smith"

def test_register_command_existing_user():
    phone = "+20000000003"
    state_machine = BotStateMachine()
    # First register the user.
    response = register_command("Alice Smith", phone, state_machine, msg_timestamp=123)
    assert "registered" in response.lower()
    # Attempt to register again.
    response2 = register_command("", phone, state_machine, msg_timestamp=123)
    # Expect response to indicate that the user is already registered.
    assert "you are registered as" in response2.lower()

def test_delete_command():
    phone = "+20000000004"
    state_machine = BotStateMachine()
    # Register the user.
    register_command("Bob Brown", phone, state_machine, msg_timestamp=123)
    response = delete_command("", phone, state_machine, msg_timestamp=123)
    # Check that the initial prompt is correct.
    assert "would you like to delete your registration" in response.lower()

# End of tests/plugins/test_volunteer_commands.py
