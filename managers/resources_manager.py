#!/usr/bin/env python
"""
managers/resources_manager.py --- Resources Manager.
Provides a unified interface for resource-related operations including listing, creating, and deleting resources.
All validation and DB logic reside here.
"""

from core.database.resources import add_resource, list_resources, remove_resource
from core.exceptions import ResourceError

def list_all_resources(category: str = None):
    """
    list_all_resources - Retrieve resource records from the database.

    Args:
        category (str, optional): Filter resources by category if provided.

    Returns:
        list: A list of resource records.
    """
    return list_resources(category)

def create_resource(category: str, url: str, title: str = "") -> int:
    """
    create_resource - Add a new resource record with validation.

    Raises:
        ResourceError: If URL does not start with 'http'.
    """
    if not url.startswith("http"):
        raise ResourceError(f"URL must start with 'http'. Provided: {url}")
    return add_resource(category, url, title)

def delete_resource(resource_id: int) -> None:
    """
    delete_resource - Remove a resource record by its ID, with validation.

    Raises:
        ResourceError: If the provided resource_id is not a positive integer.
    """
    if resource_id <= 0:
        raise ResourceError(f"Resource ID must be a positive integer. Provided: {resource_id}")
    remove_resource(resource_id)

# End of managers/resources_manager.py