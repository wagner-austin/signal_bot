"""
tests/core/test_database_volunteers.py – Tests for volunteer database operations.
Verifies functions for adding, updating, retrieving, and deleting volunteer records.
"""

import pytest
from core.database.volunteers import (
    add_volunteer_record,
    get_volunteer_record,
    update_volunteer_record,
    delete_volunteer_record,
    add_deleted_volunteer_record,
    remove_deleted_volunteer_record,
)
from core.database.connection import get_connection

def test_add_and_get_volunteer():
    phone = "+1234567890"
    name = "Test Volunteer"
    skills = ["Skill1", "Skill2"]
    add_volunteer_record(phone, name, skills, True, None)
    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == name
    assert "Skill1" in record["skills"]

def test_update_volunteer():
    phone = "+1234567891"
    name = "Initial Name"
    skills = ["SkillA"]
    add_volunteer_record(phone, name, skills, True, None)
    update_volunteer_record(phone, "Updated Name", ["SkillB"], False, "RoleX")
    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == "Updated Name"
    assert "SkillB" in record["skills"]
    assert record["available"] is False
    assert record["current_role"] == "RoleX"

def test_delete_volunteer():
    phone = "+1234567892"
    name = "Delete Volunteer"
    skills = ["SkillDel"]
    add_volunteer_record(phone, name, skills, True, None)
    delete_volunteer_record(phone)
    record = get_volunteer_record(phone)
    assert record is None

def test_deleted_volunteer_record_handling():
    phone = "+1234567893"
    name = "Deleted Volunteer"
    skills = ["SkillX"]
    add_volunteer_record(phone, name, skills, True, None)
    add_deleted_volunteer_record(phone, name, skills, True, None)
    delete_volunteer_record(phone)
    record_active = get_volunteer_record(phone)
    assert record_active is None
    remove_deleted_volunteer_record(phone)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM DeletedVolunteers WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    assert row is None

# End of tests/core/test_database_volunteers.py