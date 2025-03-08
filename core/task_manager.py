#!/usr/bin/env python
"""
core/task_manager.py - Task Manager for shared to-do items.
Provides functions to add, list, assign, and close tasks.
"""

from typing import List, Dict, Optional
from core.database.helpers import execute_sql
from core.database.connection import get_connection
from managers.volunteer.volunteer_common import normalize_name  # Import normalization for consistent volunteer display

def add_task(created_by: str, description: str) -> int:
    """
    add_task - Add a new task to the Tasks table.
    
    Args:
        created_by (str): The phone number of the volunteer creating the task.
        description (str): The task description.
        
    Returns:
        int: The task_id of the newly created task.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Tasks (description, created_by) VALUES (?, ?)",
        (description, created_by)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def list_tasks() -> List[Dict]:
    """
    list_tasks - List all tasks with joined volunteer display names for created_by and assigned_to.
    
    Returns:
        List[Dict]: A list of tasks with keys: task_id, description, status, created_at,
                    created_by_name, assigned_to_name.
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

def assign_task(task_id: int, volunteer_display_name: str) -> Optional[str]:
    """
    assign_task - Assign a task to a volunteer by display name.
    Performs a case-insensitive search in the Volunteers table.
    
    Args:
        task_id (int): The ID of the task to assign.
        volunteer_display_name (str): The display name of the volunteer to assign.
        
    Returns:
        Optional[str]: An error message if assignment fails, otherwise None.
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
    """
    close_task - Close a task by updating its status to 'closed'.
    
    Args:
        task_id (int): The ID of the task to close.
        
    Returns:
        bool: True if the task was updated, False otherwise.
    """
    update_query = "UPDATE Tasks SET status = 'closed' WHERE task_id = ?"
    execute_sql(update_query, (task_id,), commit=True)
    return True

# End of core/task_manager.py