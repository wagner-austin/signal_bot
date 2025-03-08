#!/usr/bin/env python
"""
managers/volunteer/volunteer_operations.py --- Volunteer operations.
Provides functions for volunteer registration, check‑in, and deletion.
Uses a centralized sign up method for consistent volunteer creation.
Changes:
 - Added an info-level log message upon successful volunteer deletion.
"""

import logging
from typing import List, Optional
from core.database import (
    get_volunteer_record, add_volunteer_record, update_volunteer_record,
    delete_volunteer_record, add_deleted_volunteer_record, remove_deleted_volunteer_record
)
from core.messages import NEW_VOLUNTEER_REGISTERED, VOLUNTEER_UPDATED, VOLUNTEER_DELETED, VOLUNTEER_CHECKED_IN
from managers.volunteer.volunteer_common import normalize_name
from core.skill_config import AVAILABLE_SKILLS

logger = logging.getLogger(__name__)

def sign_up(phone: str, name: str, skills: List[str], available: bool = True, current_role: Optional[str] = None) -> str:
    """
    sign_up - Registers a new volunteer or updates an existing one using a centralized method.
    
    Args:
        phone (str): Volunteer phone number.
        name (str): Volunteer full name.
        skills (List[str]): List of skills.
        available (bool): Availability status; defaults to True.
        current_role (Optional[str]): Role provided during registration.
                                      If omitted or empty, no role is assigned.
    
    Returns:
        str: Confirmation message.
    """
    record = get_volunteer_record(phone)
    if record:
        updated_name = record["name"] if name.lower() == "skip" else name
        current_skills = set(record.get("skills", []))
        updated_skills = list(current_skills.union(skills))
        updated_name = normalize_name(updated_name, phone)
        # Update current_role if provided; otherwise keep existing.
        new_role = current_role if current_role is not None and current_role.strip() != "" else record.get("current_role")
        update_volunteer_record(phone, updated_name, updated_skills, available, new_role)
        return VOLUNTEER_UPDATED.format(name=updated_name)
    else:
        remove_deleted_volunteer_record(phone)
        final_name = "Anonymous" if name.lower() == "skip" or name.strip() == "" else name
        final_name = normalize_name(final_name, phone)
        # Only assign role if a non-empty role string is provided.
        role_to_set = current_role.strip() if current_role and current_role.strip() != "" else None
        add_volunteer_record(phone, final_name, skills, available, role_to_set, role_to_set)
        return NEW_VOLUNTEER_REGISTERED.format(name=final_name)

def delete_volunteer(phone: str) -> str:
    """
    delete_volunteer - Deletes a volunteer's registration.
    
    Args:
        phone (str): Volunteer phone number.
    
    Returns:
        str: Confirmation message.
    """
    record = get_volunteer_record(phone)
    if not record:
        return "You are not registered."
    add_deleted_volunteer_record(phone, record["name"], record.get("skills", []), record["available"], record.get("current_role"))
    delete_volunteer_record(phone)
    logger.info(f"Volunteer record for {phone} has been deleted from the system.")
    return VOLUNTEER_DELETED

def check_in(phone: str) -> str:
    """
    check_in - Marks a volunteer as available.
    
    Args:
        phone (str): Volunteer phone number.
    
    Returns:
        str: Confirmation message.
    """
    record = get_volunteer_record(phone)
    if record:
        update_volunteer_record(phone, record["name"], record.get("skills", []), True, record.get("current_role"))
        return VOLUNTEER_CHECKED_IN.format(name=normalize_name(record['name'], phone))
    return "Volunteer not found."

# End of managers/volunteer/volunteer_operations.py