#!/usr/bin/env python
"""
File: managers/task_manager.py
------------------------------
Task Manager for shared to-do items.
Provides functions for creating, listing, assigning, and closing tasks with proper logging.
Exceptions from business logic propagate to the CLI/plugin layer.

CHANGES:
 - Replaced direct execute_sql in _fetch_tasks() with TaskRepository.list_tasks_detailed().
"""

from typing import List, Dict
from db.repository import TaskRepository
from core.transaction import atomic_transaction
from managers.volunteer_manager import normalize_name
from core.exceptions import VolunteerError
import logging

logger = logging.getLogger(__name__)

def create_task(created_by: str, description: str) -> int:
    """
    create_task - Create a new task in the database.
    """
    repo = TaskRepository()
    data = {
        "description": description,
        "created_by": created_by
    }
    task_id = repo.create(data)
    logger.info(f"Task created with ID {task_id} by {created_by}.")
    return task_id

def _fetch_tasks() -> List[Dict]:
    """
    _fetch_tasks - Internal helper to query the Task table, joined with Volunteers.
    Now uses TaskRepository.list_tasks_detailed().
    """
    repo = TaskRepository()
    rows = repo.list_tasks_detailed()
    tasks = []
    if rows:
        for row in rows:
            created_by_name = normalize_name(row["created_by_name"], row["created_by"]) if row["created_by_name"] else "Unknown"
            assigned_to_name = normalize_name(row["assigned_to_name"], row["assigned_to"]) if row["assigned_to_name"] else "Unassigned"
            tasks.append({
                "task_id": row["task_id"],
                "description": row["description"],
                "status": row["status"],
                "created_at": row["created_at"],
                "created_by_name": created_by_name,
                "assigned_to_name": assigned_to_name
            })
    return tasks

def list_all_tasks() -> List[Dict]:
    """
    list_all_tasks - Retrieve all tasks from the database.
    """
    return _fetch_tasks()

def assign_task(task_id: int, volunteer_display_name: str) -> None:
    """
    assign_task - Assigns a task to a volunteer based on the volunteer's display name.
    Raises VolunteerError if the volunteer is not found.
    """
    from db.connection import get_connection
    with atomic_transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT phone FROM Volunteers WHERE lower(name)=? LIMIT 1", (volunteer_display_name.lower(),))
        result = cursor.fetchone()
        if not result:
            raise VolunteerError(f"Volunteer with name '{volunteer_display_name}' not found.")
        volunteer_phone = result["phone"]
        cursor.execute("UPDATE Tasks SET assigned_to = ? WHERE task_id = ?", (volunteer_phone, task_id))
        logger.info(f"Task {task_id} assigned to volunteer '{volunteer_display_name}' (phone: {volunteer_phone}).")

def close_task(task_id: int) -> bool:
    """
    close_task - Mark a task as closed in the database.
    """
    repo = TaskRepository()
    repo.update(task_id, {"status": "closed"})
    logger.info(f"Task {task_id} marked as closed.")
    return True

# End of managers/task_manager.py