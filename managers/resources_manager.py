#!/usr/bin/env python
"""
managers/resources_manager.py --- Resources Manager.
Provides a unified interface for resource-related operations including listing resources.
"""

from core.database.resources import list_resources

def list_all_resources(category: str = None):
    """
    list_all_resources - Retrieve resource records.
    
    Args:
        category (str, optional): Filter resources by category if provided.
    
    Returns:
        list: A list of resource records.
    """
    return list_resources(category)
    
# End of managers/resources_manager.py