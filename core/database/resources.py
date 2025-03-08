#!/usr/bin/env python
"""
core/database/resources.py - Database operations for resource links using repository pattern.
Provides functions to add, list, and remove resource records.
"""

from core.database.repository import ResourceRepository

def add_resource(category: str, url: str, title: str = "") -> int:
    repo = ResourceRepository()
    data = {
        "category": category,
        "title": title,
        "url": url
    }
    return repo.create(data)

def list_resources(category: str = None):
    repo = ResourceRepository()
    if category:
        return repo.list_all(filters={"category": category})
    else:
        return repo.list_all()

def remove_resource(resource_id: int) -> None:
    repo = ResourceRepository()
    repo.delete(resource_id)

# End of core/database/resources.py