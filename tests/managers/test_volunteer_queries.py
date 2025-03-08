#!/usr/bin/env python
"""
tests/managers/test_volunteer_queries.py - Tests for volunteer queries.
Verifies volunteer_status, find_available_volunteer, and get_all_skills functionalities.
"""
from managers.volunteer.volunteer_queries import volunteer_status, find_available_volunteer, get_all_skills
from core.database.volunteers import add_volunteer_record

def test_volunteer_status():
    # Add a volunteer record for testing status.
    phone = "+50000000001"
    add_volunteer_record(phone, "Status Volunteer", ["SkillStatus"], True, None)
    status = volunteer_status()
    assert "Status Volunteer" in status

def test_find_available_volunteer():
    phone = "+50000000002"
    add_volunteer_record(phone, "Available Volunteer", ["UniqueSkill"], True, None)
    name = find_available_volunteer("UniqueSkill")
    assert name == "Available Volunteer"

def test_get_all_skills():
    skills = get_all_skills()
    assert isinstance(skills, list)
    assert len(skills) > 0

# End of tests/managers/test_volunteer_queries.py