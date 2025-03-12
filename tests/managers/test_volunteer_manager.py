#!/usr/bin/env python
"""
tests/managers/test_volunteer_manager.py - Tests for aggregated volunteer management functionalities.
Verifies that operations like register_volunteer, check_in, deletion, status retrieval, and role management work correctly.
Now includes concurrency testing for multiple register_volunteer calls on the same phone number,
and a new test for list_all_volunteers() to ensure unified volunteer data retrieval.
"""

import pytest
import concurrent.futures
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.database.volunteers import get_volunteer_record
from managers.volunteer.volunteer_operations import register_volunteer

@pytest.mark.parametrize(
    "phone, name, skills, expected_substring",
    [
        ("+10000000001", "John Doe", ["Public Speaking"], "John Doe"),
        ("+10000000002", "Jane Smith", ["Greeter"], "Jane Smith"),
        ("+10000000003", "Alice Johnson", ["Logistics Oversight"], "Alice Johnson"),
    ]
)
def test_register_volunteer_and_status(phone, name, skills, expected_substring):
    """
    Test registering volunteers and verifying their status.
    Uses parametrization for different phone/name/skills combos.
    """
    result = VOLUNTEER_MANAGER.register_volunteer(phone, name, skills)
    assert "registered" in result.lower() or "updated" in result.lower()
    status = VOLUNTEER_MANAGER.volunteer_status()
    assert expected_substring in status

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+10000000002", "Jane Smith", ["Greeter"]),
        ("+10000000008", "Tom Tester", ["AnySkill"]),
    ]
)
def test_check_in(phone, name, skills):
    """
    Test checking in a volunteer with multiple scenarios.
    """
    VOLUNTEER_MANAGER.register_volunteer(phone, name, skills)
    result = VOLUNTEER_MANAGER.check_in(phone)
    assert "checked in" in result.lower()

@pytest.mark.parametrize(
    "phone, name, skills",
    [
        ("+10000000003", "Alice Johnson", ["Logistics Oversight"]),
        ("+10000000009", "Another Person", ["SomeSkill"]),
    ]
)
def test_delete_volunteer(phone, name, skills):
    """
    Test deleting volunteers using parametrization for multiple phone/name combos.
    """
    VOLUNTEER_MANAGER.register_volunteer(phone, name, skills)
    result = VOLUNTEER_MANAGER.delete_volunteer(phone)
    assert "deleted" in result.lower()
    record = get_volunteer_record(phone)
    assert record is None

@pytest.mark.parametrize(
    "phone, name, skills, is_available, role",
    [
        ("+10000000004", "Test Volunteer", ["SkillX"], False, "Tester"),
        ("+10000000010", "Another Volunteer", ["SkillA", "SkillB"], True, "Coordinator"),
    ]
)
def test_register_volunteer_with_availability_and_role(phone, name, skills, is_available, role):
    """
    Tests that register_volunteer correctly handles availability and role for different volunteers.
    """
    # Create a new volunteer with the specified availability and role
    result_create = VOLUNTEER_MANAGER.register_volunteer(phone, name, skills, is_available, role)
    assert "registered" in result_create.lower()

    record = get_volunteer_record(phone)
    assert record is not None
    assert record["name"] == name
    for skl in skills:
        assert skl in record["skills"]
    assert record["available"] == is_available
    assert record["current_role"] == role

    # Update the volunteer with an additional skill, to ensure union behavior
    new_skill = ["ExtraSkill"]
    result_update = VOLUNTEER_MANAGER.register_volunteer(phone, name + " Updated", new_skill, not is_available, role)
    # Expect an update message (the message should indicate the volunteer was updated).
    assert "updated" in result_update.lower()

    updated_record = get_volunteer_record(phone)
    assert updated_record is not None
    assert updated_record["name"] == name + " Updated"
    # Since we union the old and new skills:
    for skl in (skills + new_skill):
        assert skl in updated_record["skills"]
    # Invert the availability
    assert updated_record["available"] == (not is_available)
    # Role remains the same
    assert updated_record["current_role"] == role

def test_concurrent_register_volunteer_same_user():
    """
    Test concurrent register_volunteer calls using the same phone number, with different names and skills.
    Verifies that the final record merges all skills (union) and ends with whichever name
    was last, ensuring no partial merges or errors under concurrency.
    """
    phone = "+10000000042"

    # If volunteer exists, remove them
    existing = get_volunteer_record(phone)
    if existing:
        VOLUNTEER_MANAGER.delete_volunteer(phone)

    concurrency_data = [
        ("ConcurrentOne", ["SkillA"]),
        ("ConcurrentTwo", ["SkillB", "SkillC"]),
        ("ConcurrentThree", ["SkillB", "SkillX"]),
        ("ConcurrentFour", ["SkillA", "SkillD"]),
        ("ConcurrentFive", ["SkillZ"]),
    ]

    def register_task(name, skills):
        return VOLUNTEER_MANAGER.register_volunteer(phone, name, skills, True, None)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(concurrency_data)) as executor:
        futures = [
            executor.submit(register_task, name, skills)
            for (name, skills) in concurrency_data
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    for res in results:
        # Should all say "registered" or "updated"
        assert any(word in res.lower() for word in ["registered", "updated", "volunteer"])

    final_record = get_volunteer_record(phone)
    assert final_record is not None, "Expected a final volunteer record after concurrency register_volunteer."

    # final name is whichever thread finished last
    possible_names = {cd[0] for cd in concurrency_data}
    assert final_record["name"] in possible_names, (
        f"Final name '{final_record['name']}' must be among: {possible_names}"
    )

    # The final skills is the union of all skill sets
    merged_skills = set()
    for _, skill_list in concurrency_data:
        merged_skills.update(skill_list)
    for skl in merged_skills:
        assert skl in final_record["skills"], (
            f"Final record lacks skill '{skl}' from concurrency data set."
        )

def test_list_volunteers_method():
    """
    Test that VOLUNTEER_MANAGER.list_all_volunteers() returns a dictionary mapping phone numbers to volunteer data.
    """
    phone = "+7777777777"
    # Register a volunteer.
    result = VOLUNTEER_MANAGER.register_volunteer(phone, "List Test Volunteer", ["SkillX"], True, None)
    assert "registered" in result.lower() or "updated" in result.lower()
    volunteers = VOLUNTEER_MANAGER.list_all_volunteers()
    assert phone in volunteers
    assert volunteers[phone]["name"] == "List Test Volunteer"

# End of tests/managers/test_volunteer_manager.py