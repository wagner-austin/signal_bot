#!/usr/bin/env python
"""
tests/core/test_task_manager.py - Tests for the Task Manager module.
Verifies that tasks can be added, listed, assigned, and closed.
"""

from core.task_manager import add_task, list_tasks, assign_task, close_task
from core.database.connection import get_connection

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
    # Since no volunteer record exists for created_by, the created_by_name should be "Unknown"
    assert task["created_by_name"] == "Unknown"

def test_assign_and_close_task(monkeypatch):
    # Add a volunteer record so that assignment works
    from core.database.volunteers import add_volunteer_record
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

# End of tests/core/test_task_manager.py