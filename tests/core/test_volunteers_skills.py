#!/usr/bin/env python
"""
tests/core/test_volunteers_skills.py - Tests for skill conversion functions in core/database/volunteers.py.
Ensures that skills are properly serialized to a comma-separated string and deserialized back to a list.
"""

import pytest
from core.database.volunteers import serialize_skills, deserialize_skills

def test_serialize_skills_empty():
    assert serialize_skills([]) == ""

def test_serialize_skills_multiple():
    skills = ["Public Speaking", "Logistics", "  Volunteer Management "]
    # Expect that skills are joined by commas without extra whitespace.
    expected = "Public Speaking,Logistics,  Volunteer Management "
    assert serialize_skills(skills) == expected

def test_deserialize_skills_empty():
    assert deserialize_skills("") == []
    assert deserialize_skills(None) == []

def test_deserialize_skills_multiple():
    skills_str = "Public Speaking, Logistics ,Volunteer Management"
    expected = ["Public Speaking", "Logistics", "Volunteer Management"]
    assert deserialize_skills(skills_str) == expected

def test_serialize_then_deserialize():
    skills = ["Skill1", "Skill2", "Skill3"]
    serialized = serialize_skills(skills)
    deserialized = deserialize_skills(serialized)
    assert deserialized == skills

# -------------------------------
# Additional Negative / Boundary Tests
# -------------------------------

def test_deserialize_list_special_characters():
    """
    Verifies that skills containing special characters are preserved without error.
    """
    serialized = "Skill!, ???, 123$%^,   Spaces   "
    result = deserialize_skills(serialized)
    # We expect them preserved exactly (trimming only outer whitespace on each token).
    # So "   Spaces   " becomes "Spaces" as typical.
    assert result == ["Skill!", "???", "123$%^", "Spaces"]

# End of tests/core/test_volunteers_skills.py