#!/usr/bin/env python
"""
tests/managers/test_task_manager.py - Tests for the Task Manager module.
Verifies that tasks can be added, listed, assigned, and closed.
Also tests concurrency in task assignment to confirm final DB consistency,
and checks that volunteer name matching is case-insensitive.
"""

import concurrent.futures
import pytest
from managers.task_manager import add_task, list_tasks, assign_task, close_task
from core.database.connection import get_connection
from core.database.volunteers import add_volunteer_record, get_volunteer_record

def test_add_and_list_task():
    # Add a new task
    created_by = "+1111111111"
    description = "Need 5 new signs"
    task_id = add_task(created_by, description)
    assert isinstance(task_id, int) and task_id > 0

    tasks = list_tasks()
    # Find task with task_id
    matching = [task for task in tasks if task["task_id"] == task_id]
    assert matching, "Added task should be in list_tasks"
    task = matching[0]
    assert task["description"] == description
    # Since no volunteer record exists for created_by, created_by_name should be "Unknown"
    assert task["created_by_name"] == "Unknown"

def test_assign_and_close_task(monkeypatch):
    # Add a volunteer record so that assignment works
    phone = "+2222222222"
    add_volunteer_record(phone, "Volunteer Test", ["Task Management"], True, None)

    created_by = "+1111111111"
    description = "Need a volunteer for donation table"
    task_id = add_task(created_by, description)

    # Test assignment: assign using volunteer display name "Volunteer Test"
    error = assign_task(task_id, "Volunteer Test")
    assert error is None

    tasks = list_tasks()
    matching = [task for task in tasks if task["task_id"] == task_id]
    assert matching, "Task should be present after assignment"
    task = matching[0]
    # Now the assigned_to_name should be normalized as "Volunteer Test"
    assert task["assigned_to_name"] == "Volunteer Test"

    # Test closing task
    result = close_task(task_id)
    assert result is True
    tasks = list_tasks()
    matching = [task for task in tasks if task["task_id"] == task_id]
    assert matching
    task = matching[0]
    assert task["status"] == "closed"

def test_concurrent_task_assignment():
    """
    Test assigning the same task to different volunteers concurrently to
    see which volunteer ends up assigned. This verifies that we do not crash,
    and the final DB state is valid (last writer wins).
    """
    # Create multiple volunteers
    volunteers = [
        ("+3000000001", "Vol A", ["SkillX"]),
        ("+3000000002", "Vol B", ["SkillY"]),
        ("+3000000003", "Vol C", ["SkillZ"]),
    ]
    for phone, name, skills in volunteers:
        add_volunteer_record(phone, name, skills, True, None)

    # Create a single task
    created_by = "+3000000000"
    description = "Concurrent assignment test"
    task_id = add_task(created_by, description)

    # Attempt to assign concurrently
    def assign_worker(volunteer_name):
        return assign_task(task_id, volunteer_name)

    volunteer_names = [v[1] for v in volunteers]  # ["Vol A", "Vol B", "Vol C"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(volunteer_names)) as executor:
        futures = [executor.submit(assign_worker, name) for name in volunteer_names]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All calls should succeed (no error messages)
    for res in results:
        assert res is None, f"Expected no error, got {res}"

    # Check final DB state - the last update wins
    tasks = list_tasks()
    assigned_task = next((t for t in tasks if t["task_id"] == task_id), None)
    assert assigned_task is not None, "Task should still exist."
    assigned_name = assigned_task["assigned_to_name"]
    # Must be one of Vol A, Vol B, or Vol C
    assert assigned_name in volunteer_names, (
        f"Final assignment is {assigned_name}, expected to be in {volunteer_names}"
    )

def test_assign_task_name_casing():
    """
    Test that volunteer name matching is case-insensitive: if the volunteer is registered as
    'John Doe', assigning with 'john doe', 'JOHN DOE', etc., should succeed.
    """
    phone = "+4000000010"
    volunteer_name_stored = "John Doe"
    add_volunteer_record(phone, volunteer_name_stored, ["AnySkill"], True, None)

    # Create a task
    created_by = "+4000000020"
    description = "Case-insensitive name test"
    task_id = add_task(created_by, description)

    # Try various casing forms
    for name_input in ["john doe", "JOHN DOE", "jOhN dOe"]:
        error = assign_task(task_id, name_input)
        assert error is None, f"Expected no error with volunteer name input: {name_input}"

        # Confirm the DB now has that volunteer assigned
        tasks = list_tasks()
        assigned_task = next((t for t in tasks if t["task_id"] == task_id), None)
        assert assigned_task is not None, "Task should be found."
        assigned_name = assigned_task["assigned_to_name"]
        assert assigned_name == volunteer_name_stored, (
            f"Expected stored name '{volunteer_name_stored}' but got '{assigned_name}'"
        )

def test_list_all_tasks():
    """
    Test that list_all_tasks returns correct data.
    """
    created_by = "+5555555555"
    description = "List All Task Test"
    task_id = add_task(created_by, description)
    from managers.task_manager import list_all_tasks
    tasks = list_all_tasks()
    matching = [task for task in tasks if task["task_id"] == task_id]
    assert matching, "Added task should appear in list_all_tasks"

# End of tests/managers/test_task_manager.py