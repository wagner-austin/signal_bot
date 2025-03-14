#!/usr/bin/env python
"""
managers/task_manager.py --- Task Manager for shared to-do items.
Provides functions for creating, listing, assigning, and closing tasks with proper logging.
Exceptions from business logic propagate to the CLI/plugin layer.
"""

from typing import List, Dict
from db.repository import execute_sql
from core.transaction import atomic_transaction
from managers.volunteer_manager import normalize_name
from core.exceptions import VolunteerError
import logging

logger = logging.getLogger(__name__)

def create_task(created_by: str, description: str) -> int:
    """
    create_task - Create a new task in the database.
    """
    from db.repository import TaskRepository  # Local import to avoid circular references
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
    _fetch_tasks - Internal helper to query the Task table for all tasks.
    """
    query = """
    SELECT t.task_id, t.description, t.status, t.created_at,
           t.created_by,
           v1.name as created_by_name,
           t.assigned_to,
           v2.name as assigned_to_name
    FROM Tasks t
    LEFT JOIN Volunteers v1 ON t.created_by = v1.phone
    LEFT JOIN Volunteers v2 ON t.assigned_to = v2.phone
    ORDER BY t.created_at DESC
    """
    rows = execute_sql(query, fetchall=True)
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
    update_query = "UPDATE Tasks SET status = 'closed' WHERE task_id = ?"
    execute_sql(update_query, (task_id,), commit=True)
    logger.info(f"Task {task_id} marked as closed.")
    return True

from db.repository import TaskRepository

# End of managers/task_manager.py