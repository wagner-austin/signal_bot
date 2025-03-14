#!/usr/bin/env python
"""
resources_manager.py
--------------------
Manages resource logic. Now references db/resources instead of db.resources.
"""

import logging
from core.exceptions import ResourceError
from db.resources import add_resource, list_resources, remove_resource

logger = logging.getLogger(__name__)

def list_all_resources(category: str = None):
    """
    Return resource records (optionally filtered by category).
    """
    return list_resources(category)

def create_resource(category: str, url: str, title: str = "") -> int:
    """
    create_resource - Add a new resource record to the DB.
    Raises ResourceError if invalid (e.g., URL doesn't start with 'http').
    """
    if not url.startswith("http"):
        raise ResourceError(f"URL must start with 'http'. Provided: {url}")
    resource_id = add_resource(category, url, title)
    logger.info(f"Resource created: ID {resource_id}, category: {category}, title: {title}")
    return resource_id

def delete_resource(resource_id: int) -> None:
    """
    delete_resource - Remove a resource record by its ID.
    Raises ResourceError if the ID is invalid (<= 0).
    """
    if resource_id <= 0:
        raise ResourceError(f"Resource ID must be a positive integer. Provided: {resource_id}")
    remove_resource(resource_id)
    logger.info(f"Resource with ID {resource_id} deleted.")

# End of managers/resources_manager.py