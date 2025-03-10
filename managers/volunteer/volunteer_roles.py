#!/usr/bin/env python
"""
managers/volunteer/volunteer_roles.py - Volunteer role management.
Provides functions to list, assign, switch, and unassign volunteer roles.
Handles validation of required skills for each role.
"""

from typing import List, Optional
from core.database import get_volunteer_record
from core.database.helpers import execute_sql
from managers.volunteer.volunteer_common import normalize_name

# Recognized roles and their required skills.
RECOGNIZED_ROLES = [
    "greeter",
    "speaker coordinator",
    "table staff",
    "photographer",
    "medic",
    "emcee",
    "peacekeeper",
    "chant leader"
]

ROLE_SKILL_REQUIREMENTS = {
    "greeter": ["communication", "interpersonal"],
    "speaker coordinator": ["organizational", "communication"],
    "table staff": ["organization"],
    "photographer": ["photography"],
    "medic": ["first aid"],
    "emcee": ["public speaking", "communication"],
    "peacekeeper": ["conflict resolution"],
    "chant leader": ["leadership", "communication"]
}

def list_roles() -> List[str]:
    """
    list_roles - Returns a list of recognized roles with their required skills.
    
    Returns:
        List[str]: List of roles and required skills.
    """
    roles_info = []
    for role in RECOGNIZED_ROLES:
        req_skills = ROLE_SKILL_REQUIREMENTS.get(role.lower(), [])
        roles_info.append(f"{role} (requires: {', '.join(req_skills) if req_skills else 'None'})")
    return roles_info

def update_volunteer_role(phone: str, role: Optional[str]) -> None:
    """
    update_volunteer_role - Updates the volunteer's preferred role in the database.
    
    Args:
        phone (str): Volunteer phone number.
        role (Optional[str]): New role to set; None to clear.
    """
    execute_sql("UPDATE Volunteers SET preferred_role = ? WHERE phone = ?", (role, phone), commit=True)

def assign_role(phone: str, role: str) -> str:
    """
    assign_role - Assigns a preferred role to a volunteer after validating required skills.
    
    Args:
        phone (str): Volunteer phone number.
        role (str): Role to assign.
    
    Returns:
        str: Confirmation or error message.
    """
    role_lower = role.lower()
    valid_roles = [r.lower() for r in RECOGNIZED_ROLES]
    if role_lower not in valid_roles:
        return f"Role '{role}' is not recognized. Use '@bot role list' to see available roles."
    record = get_volunteer_record(phone)
    if not record:
        return "You are not registered."
    volunteer_skills = set(skill.lower() for skill in record.get("skills", []))
    required_skills = set(ROLE_SKILL_REQUIREMENTS.get(role_lower, []))
    if not required_skills.issubset(volunteer_skills):
        return (f"You do not have the necessary skills for the role '{role}'. "
                f"Required: {', '.join(required_skills)}. "
                f"Your skills: {', '.join(volunteer_skills) if volunteer_skills else 'None'}.")
    update_volunteer_role(phone, role)
    return f"Your preferred role has been set to '{role}'."

def switch_role(phone: str, role: str) -> str:
    record = get_volunteer_record(phone)
    if not record:
        return "You are not registered."
    current = record.get("preferred_role")
    message = ""
    if current:
        message = f"Switching from '{current}' to '{role}'. "
    else:
        message = "Setting role to "
    result = assign_role(phone, role)
    if "do not have the necessary skills" in result:
        return result
    return message + result

def unassign_role(phone: str) -> str:
    record = get_volunteer_record(phone)
    if not record:
        return "You are not registered."
    # Always update role to None, regardless of current value.
    update_volunteer_role(phone, None)
    return "Your preferred role has been cleared."

# End of managers/volunteer/volunteer_roles.py
