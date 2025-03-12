#!/usr/bin/env python
"""
managers/resources_manager.py --- Resources Manager.
Provides a unified interface for resource-related operations including listing, adding, and removing resources.
Now includes all business logic and validations previously in the CLI.
"""

from core.database.resources import add_resource, list_resources, remove_resource
from core.exceptions import ResourceError

def list_all_resources(category: str = None):
    """
    list_all_resources - Retrieve resource records.
    
    Args:
        category (str, optional): Filter resources by category if provided.
    
    Returns:
        list: A list of resource records.
    """
    return list_resources(category)

def add_new_resource(category: str, url: str, title: str = "") -> int:
    """
    add_new_resource - Add a new resource record with validations.
    
    Raises:
        ResourceError: If URL does not start with 'http'.
    """
    if not url.startswith("http"):
        error_msg = f"URL must start with 'http'. Provided: {url}"
        raise ResourceError(error_msg)
    resource_id = add_resource(category, url, title)
    return resource_id

def remove_resource_by_id(resource_id: int) -> None:
    """
    remove_resource_by_id - Remove a resource record by its ID, with validations.
    
    Raises:
        ResourceError: If the provided resource_id is not a positive integer.
    """
    if resource_id <= 0:
        error_msg = f"Resource ID must be a positive integer. Provided: {resource_id}"
        raise ResourceError(error_msg)
    remove_resource(resource_id)

# End of managers/resources_manager.py