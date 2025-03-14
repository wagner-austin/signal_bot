#!/usr/bin/env python
"""
db/resources.py
------------
Database operations for resource links, using a repository pattern.
(Moved from core/database/resources.py)
"""

from db.repository import ResourceRepository

def add_resource(category: str, url: str, title: str = "") -> int:
    """
    add_resource - Insert a resource record into the Resources table.

    Args:
        category (str): Resource category.
        url (str): URL of the resource.
        title (str, optional): Optional title for the resource.

    Returns:
        int: The new resource's row ID.
    """
    repo = ResourceRepository()
    data = {
        "category": category,
        "title": title,
        "url": url
    }
    return repo.create(data)

def list_resources(category: str = None) -> list:
    """
    list_resources - Retrieve resource records, optionally filtered by category.
    """
    repo = ResourceRepository()
    if category:
        return repo.list_all(filters={"category": category})
    else:
        return repo.list_all()

def remove_resource(resource_id: int) -> None:
    """
    remove_resource - Delete a resource record by its ID.
    """
    repo = ResourceRepository()
    repo.delete(resource_id)

# End of db/resources.py