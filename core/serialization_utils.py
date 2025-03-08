#!/usr/bin/env python
"""
core/serialization_utils.py - Serialization utilities.
Provides functions for serializing and deserializing lists (e.g., skills) to and from comma-separated strings.
Changes:
 - Replaced normalize_skill_list with unify_skills_preserving_earliest, which merges duplicates ignoring case but keeps earliest-typed form.
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


def unify_skills_preserving_earliest(skills: list) -> list:
    """
    unify_skills_preserving_earliest - Merge duplicate skill entries by ignoring case,
    but preserve the exact string (including case) from the earliest mention.

    Args:
        skills (list): A list of raw skill strings (possibly repeated, mixed-case).

    Returns:
        list: The merged list of skills, each in the earliest typed case.
    """
    seen_lower = set()
    result = []
    for s in skills:
        stripped = s.strip()
        lower = stripped.lower()
        if lower not in seen_lower:
            seen_lower.add(lower)
            result.append(stripped)
    return result

# End of core/serialization_utils.py