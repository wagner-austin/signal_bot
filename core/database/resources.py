#!/usr/bin/env python
"""
core/database/resources.py - Database operations for resource links.
Provides functions to add, list, and remove resource records.
"""

from .helpers import execute_sql
from .connection import db_connection

def add_resource(category: str, url: str, title: str = "") -> int:
    """
    Add a new resource record to the database and return its ID.
    
    Args:
        category (str): The category of the resource (e.g., "Flyers", "Videos", "Sign Ideas").
        url (str): The URL of the resource.
        title (str, optional): The title or description of the resource.
        
    Returns:
        int: The ID of the newly added resource.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Resources (category, title, url) VALUES (?, ?, ?)", (category, title, url))
        conn.commit()
        resource_id = cursor.lastrowid
    return resource_id

def list_resources(category: str = None):
    """
    List resource records from the database.
    
    Args:
        category (str, optional): If provided, filter resources by this category.
        
    Returns:
        list: A list of resource records (as sqlite3.Row objects) or an empty list.
    """
    if category:
        query = "SELECT * FROM Resources WHERE category = ? ORDER BY created_at DESC"
        rows = execute_sql(query, (category,), fetchall=True)
    else:
        query = "SELECT * FROM Resources ORDER BY created_at DESC"
        rows = execute_sql(query, fetchall=True)
    return rows if rows else []

def remove_resource(resource_id: int) -> None:
    """
    Remove a resource record from the database by its ID.
    
    Args:
        resource_id (int): The ID of the resource to remove.
    """
    query = "DELETE FROM Resources WHERE id = ?"
    execute_sql(query, (resource_id,), commit=True)

# End of core/database/resources.py