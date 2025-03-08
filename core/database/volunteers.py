#!/usr/bin/env python
"""
core/database/volunteers.py - Volunteer-related database operations.
Provides functions to manage volunteer records using the repository pattern.
This module now uses consistent role fields by updating and retrieving the 'preferred_role' column.
"""

from typing import Dict, Any, Optional, List
from core.database.repository import VolunteerRepository, DeletedVolunteerRepository
from core.serialization_utils import serialize_list, deserialize_list

# Aliases for skills serialization utilities
serialize_skills = serialize_list
deserialize_skills = deserialize_list
# For backwards compatibility
parse_skills = deserialize_list

def get_all_volunteers() -> Dict[str, Dict[str, Any]]:
    repo = VolunteerRepository()
    rows = repo.list_all()
    volunteers = {}
    for row in rows:
        preferred_role = row.get("preferred_role")
        volunteers[row["phone"]] = {
            "name": row.get("name"),
            "skills": deserialize_skills(row.get("skills", "")),
            "available": bool(row.get("available")),
            "current_role": row.get("current_role"),
            "preferred_role": preferred_role
        }
    return volunteers

def get_volunteer_record(phone: str) -> Optional[Dict[str, Any]]:
    repo = VolunteerRepository()
    row = repo.get_by_id(phone)
    if row:
        return {
            "name": row.get("name"),
            "skills": deserialize_skills(row.get("skills", "")),
            "available": bool(row.get("available")),
            "current_role": row.get("current_role"),
            "preferred_role": row.get("preferred_role")
        }
    return None

def add_volunteer_record(phone: str, display_name: str, skills: list, available: bool, current_role: Optional[str], preferred_role: Optional[str] = None) -> None:
    repo = VolunteerRepository()
    skills_str = serialize_skills(skills)
    data = {
        "phone": phone,
        "name": display_name,
        "skills": skills_str,
        "available": int(available),
        "current_role": current_role,
        "preferred_role": preferred_role
    }
    repo.create(data, replace=True)

def update_volunteer_record(phone: str, display_name: str, skills: list, available: bool, current_role: Optional[str]) -> None:
    repo = VolunteerRepository()
    skills_str = serialize_skills(skills)
    data = {
        "name": display_name,
        "skills": skills_str,
        "available": int(available),
        "current_role": current_role,
        "preferred_role": current_role  # Update preferred_role along with current_role for consistency
    }
    repo.update(phone, data)

def delete_volunteer_record(phone: str) -> None:
    repo = VolunteerRepository()
    repo.delete(phone)

def add_deleted_volunteer_record(phone: str, name: str, skills: list, available: bool, current_role: Optional[str], preferred_role: Optional[str] = None) -> None:
    repo = DeletedVolunteerRepository()
    skills_str = serialize_skills(skills)
    data = {
        "phone": phone,
        "name": name,
        "skills": skills_str,
        "available": int(available),
        "current_role": current_role,
        "preferred_role": preferred_role
    }
    repo.create(data, replace=True)

def remove_deleted_volunteer_record(phone: str) -> None:
    repo = DeletedVolunteerRepository()
    repo.delete(phone)

# End of core/database/volunteers.py