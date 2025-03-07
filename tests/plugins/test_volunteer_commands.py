"""
tests/plugins/test_volunteer_commands.py - Tests for volunteer command plugins.
Verifies that volunteer registration, modification, and new commands (find, add skills) work correctly.
"""

import pytest
from plugins.commands.volunteer import register_command, delete_command, find_command, add_skills_command
from core.state import BotStateMachine
from core.database import get_volunteer_record, get_all_volunteers
from core.database.volunteers import add_volunteer_record

def test_register_command_new_user():
    phone = "+20000000001"
    state_machine = BotStateMachine()
    response = register_command("Alice Smith", phone, state_machine, msg_timestamp=123)
    assert "registered" in response.lower()
    record = get_volunteer_record(phone)
    assert record is not None
    assert record.get("name").lower() == "alice smith"

def test_register_command_existing_user():
    phone = "+20000000003"
    state_machine = BotStateMachine()
    response = register_command("Alice Smith", phone, state_machine, msg_timestamp=123)
    assert "registered" in response.lower()
    response2 = register_command("", phone, state_machine, msg_timestamp=123)
    assert "you are registered as" in response2.lower()

def test_delete_command():
    phone = "+20000000004"
    state_machine = BotStateMachine()
    register_command("Bob Brown", phone, state_machine, msg_timestamp=123)
    response = delete_command("", phone, state_machine, msg_timestamp=123)
    assert "delete your registration" in response.lower()

def test_find_command():
    # Add two volunteer records with different skills.
    phone1 = "+30000000001"
    add_volunteer_record(phone1, "Volunteer One", ["skillA", "skillB"], True, None)
    phone2 = "+30000000002"
    add_volunteer_record(phone2, "Volunteer Two", ["skillB", "skillC"], True, None)
    response = find_command("skillB", "+dummy", None, msg_timestamp=123)
    assert "Volunteer One" in response and "Volunteer Two" in response
    response = find_command("skillC", "+dummy", None, msg_timestamp=123)
    assert "Volunteer Two" in response and "Volunteer One" not in response

def test_add_skills_command():
    phone = "+30000000003"
    add_volunteer_record(phone, "Volunteer Three", ["skillX"], True, None)
    response = add_skills_command("skillY, skillZ", phone, None, msg_timestamp=123)
    record = get_volunteer_record(phone)
    skills = record.get("skills", [])
    assert "skillX" in skills and "skillY" in skills and "skillZ" in skills

# End of tests/plugins/test_volunteer_commands.py