#!/usr/bin/env python
"""
core/serialization_utils.py - Serialization utilities.
Provides functions for serializing and deserializing lists (e.g., skills) to and from comma-separated strings.
"""

def serialize_list(items: list) -> str:
    """
    Convert a list of strings into a comma-separated string.
    
    Args:
        items (list): List of strings.
        
    Returns:
        str: Comma-separated string.
    """
    return ",".join(items)

def deserialize_list(serialized: str) -> list:
    """
    Convert a comma-separated string into a list of strings.
    
    Args:
        serialized (str): Comma-separated string.
        
    Returns:
        list: List of strings.
    """
    if not serialized:
        return []
    return [item.strip() for item in serialized.split(",") if item.strip()]

# End of core/serialization_utils.py