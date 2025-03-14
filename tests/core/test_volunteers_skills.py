#!/usr/bin/env python
"""
tests/core/test_volunteers_skills.py - Tests for skill conversion functions in core/database/volunteers.py.
Ensures that skills are properly serialized to a comma-separated string and deserialized back to a list.
Changes:
 - Updated test_duplicate_skills_unified to confirm we unify duplicates ignoring case but preserve earliest typed form.
 - Removed db_connection fixture usage (it was nonexistent).
"""

import pytest
from core.serialization_utils import serialize_list, deserialize_list
from db.volunteers import (
    add_volunteer_record,
    get_volunteer_record,
    delete_volunteer_record
)
from managers.volunteer_manager import register_volunteer


def test_serialize_list_empty():
    assert serialize_list([]) == ""

def test_serialize_list_multiple():
    items = ["a", "b", "c"]
    result = serialize_list(items)
    # Expect a comma-separated string without extra spaces.
    assert result == "a,b,c"

def test_deserialize_list_empty():
    assert deserialize_list("") == []
    assert deserialize_list(None) == []

def test_deserialize_list_multiple():
    serialized = "a,b,c"
    result = deserialize_list(serialized)
    assert result == ["a", "b", "c"]

def test_serialize_then_deserialize():
    items = ["item1", "item2", "item3"]
    serialized = serialize_list(items)
    deserialized = deserialize_list(serialized)
    assert deserialized == items

# ---------------------------------------------------------------------
# UPDATED TEST: unify duplicates ignoring case, but keep earliest typed form
# ---------------------------------------------------------------------
def test_duplicate_skills_unified():
    """
    Provide a list with duplicates or repeated skill strings in different cases
    to confirm we unify them ignoring case, preserving the earliest typed case.
    """
    phone = "+88888888888"
    # Clean up if that volunteer record exists
    delete_volunteer_record(phone)

    # Repeated skill strings: "Python", "python", "PYTHON", " python "
    # plus duplicates "sql", "SQL"
    skill_list = ["Python", "python", "PYTHON", " python ", "sql", "SQL", "SQL"]

    register_volunteer(phone, "DupSkillTester", skill_list, True, None)
    record = get_volunteer_record(phone)
    assert record is not None

    final_skills = record["skills"]
    # We should see exactly 2 unique skills, "Python" and "sql"
    # because "Python" was the earliest form for that skill
    # and "sql" was earliest for the second skill.
    assert len(final_skills) == 2
    assert "Python" in final_skills
    assert "sql" in final_skills

    # Cleanup
    delete_volunteer_record(phone)

# End of tests/core/test_volunteers_skills.py