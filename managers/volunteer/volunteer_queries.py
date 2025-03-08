#!/usr/bin/env python
"""
managers/volunteer/volunteer_queries.py - Volunteer query functions.
Provides functions to retrieve volunteer status, search for available volunteers,
and list available skills.
"""

from typing import Optional, List
from core.database import get_all_volunteers
from managers.volunteer.volunteer_common import normalize_name

def volunteer_status() -> str:
    """
    volunteer_status - Retrieves and formats current volunteer status.
    
    Returns:
        str: Status information for each volunteer.
    """
    volunteers = get_all_volunteers()
    status_lines = []
    for phone, data in volunteers.items():
        name = normalize_name(data.get("name", phone), phone)
        availability = "Available" if data.get("available") else "Not Available"
        current_role = data.get("current_role") if data.get("current_role") else "None"
        preferred_role = data.get("preferred_role") if data.get("preferred_role") else "None"
        status_lines.append(f"{name}: {availability}, Assigned Role: {current_role}, Preferred Role: {preferred_role}")
    return "\n".join(status_lines)

def find_available_volunteer(skill: str) -> Optional[str]:
    """
    find_available_volunteer - Finds the first available volunteer with the specified skill.
    
    Args:
        skill (str): The required skill.
    
    Returns:
        Optional[str]: Volunteer name if available, else None.
    """
    volunteers = get_all_volunteers()
    for phone, data in volunteers.items():
        if skill in data.get("skills", []) and data.get("available") and data.get("current_role") is None:
            return normalize_name(data.get("name", phone), phone)
    return None

def get_all_skills() -> List[str]:
    """
    get_all_skills - Retrieves the list of available skills from configuration.
    
    Returns:
        List[str]: List of skills.
    """
    from core.skill_config import AVAILABLE_SKILLS
    return AVAILABLE_SKILLS

# End of managers/volunteer/volunteer_queries.py