"""
tests/core/test_database_volunteers.py - Tests for volunteer database operations.
Verifies functions for adding, updating, retrieving, and deleting volunteer records using parameterized tests.
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

@pytest.mark.parametrize(
    "operation, phone, init_name, init_skills, new_name, new_skills, available, current_role, expected_name, expected_skills, expected_available, expected_role",
    [
        # Test adding a volunteer record.
        (
            "add",
            "+1234567890",
            "Test Volunteer", ["Skill1", "Skill2"],
            "Test Volunteer", ["Skill1", "Skill2"],
            True, None,
            "Test Volunteer", ["Skill1", "Skill2"],
            True, None
        ),
        # Test updating a volunteer record.
        (
            "update",
            "+1234567891",
            "Initial Name", ["SkillA"],
            "Updated Name", ["SkillB"],
            False, "RoleX",
            "Updated Name", ["SkillB"],
            False, "RoleX"
        ),
    ]
)
def test_volunteer_operations(
    operation, phone, init_name, init_skills, new_name, new_skills,
    available, current_role, expected_name, expected_skills, expected_available, expected_role
):
    if operation == "add":
        add_volunteer_record(phone, init_name, init_skills, True, None)
    elif operation == "update":
        add_volunteer_record(phone, init_name, init_skills, True, None)
        update_volunteer_record(phone, new_name, new_skills, available, current_role)
    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == expected_name
    # Check that each expected skill is present.
    for skill in expected_skills:
        assert skill in record["skills"]
    if operation == "update":
        assert record["available"] is expected_available
        assert record["current_role"] == expected_role

@pytest.mark.parametrize(
    "operation, phone, name, skills",
    [
        ("delete", "+1234567892", "Delete Volunteer", ["SkillDel"]),
        ("deleted_record", "+1234567893", "Deleted Volunteer", ["SkillX"]),
    ]
)
def test_volunteer_deletion(operation, phone, name, skills):
    add_volunteer_record(phone, name, skills, True, None)
    if operation == "deleted_record":
        add_deleted_volunteer_record(phone, name, skills, True, None)
    delete_volunteer_record(phone)
    record_active = get_volunteer_record(phone)
    assert record_active is None
    if operation == "deleted_record":
        remove_deleted_volunteer_record(phone)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DeletedVolunteers WHERE phone = ?", (phone,))
        row = cursor.fetchone()
        conn.close()
        assert row is None

# End of tests/core/test_database_volunteers.py