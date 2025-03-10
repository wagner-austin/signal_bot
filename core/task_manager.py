#!/usr/bin/env python
"""
core/task_manager.py --- Task Manager for shared to-do items using repository pattern.
Provides functions to add, list, assign, and close tasks.

Concurrency Note:
    The `assign_task` function uses a simple last-write-wins approach when multiple
    concurrent assignments happen to the same task. The final DB state reflects the
    assignment from whichever thread completes last. If you need finer-grained control,
    consider using transactions or row-level locking.

Name Matching Note:
    The volunteer's name comparison in `assign_task` is case-insensitive.
    If the DB has 'John Doe', you can assign with 'john doe' or 'JOHN DOE' etc.
"""

from typing import List, Dict, Optional
from core.database.repository import TaskRepository
from core.database.helpers import execute_sql
from core.database.connection import get_connection
from managers.volunteer.volunteer_common import normalize_name

def add_task(created_by: str, description: str) -> int:
    repo = TaskRepository()
    data = {
        "description": description,
        "created_by": created_by
    }
    return repo.create(data)

def list_tasks() -> List[Dict]:
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

def assign_task(task_id: int, volunteer_display_name: str) -> Optional[str]:
    """
    assign_task - Assigns the given task to the volunteer identified by volunteer_display_name
    (matching is case-insensitive). If the volunteer is not found, returns an error message;
    otherwise returns None.
    """
    query = "SELECT phone FROM Volunteers WHERE lower(name)=? LIMIT 1"
    result = execute_sql(query, (volunteer_display_name.lower(),), fetchone=True)
    if not result:
        return f"Volunteer with name '{volunteer_display_name}' not found."
    volunteer_phone = result["phone"]
    update_query = "UPDATE Tasks SET assigned_to = ? WHERE task_id = ?"
    execute_sql(update_query, (volunteer_phone, task_id), commit=True)
    return None

def close_task(task_id: int) -> bool:
    update_query = "UPDATE Tasks SET status = 'closed' WHERE task_id = ?"
    execute_sql(update_query, (task_id,), commit=True)
    return True

# End of core/task_manager.py