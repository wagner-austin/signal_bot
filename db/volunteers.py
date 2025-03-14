#!/usr/bin/env python
"""
db/volunteers.py
-------------
Volunteer-related database operations using a repository pattern.
(Moved from core/database/volunteers.py)

Note: Some volunteer logic may now live in managers/volunteer_manager.py,
      but these functions are retained if direct DB access is needed.
"""

from typing import Dict, Any, Optional, List
from db.repository import VolunteerRepository, DeletedVolunteerRepository
from core.serialization_utils import (
    serialize_list,
    deserialize_list,
    unify_skills_preserving_earliest
)
from db.connection import get_connection  # if needed for optional usage

def get_all_volunteers(conn=None) -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all volunteers from the Volunteers table.
    Returns a dict mapping phone -> volunteer record data.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    rows = repo.list_all()
    output = {}
    for row in rows:
        phone = row["phone"]
        output[phone] = {
            "name": row["name"],
            "skills": deserialize_list(row["skills"]),
            "available": bool(row["available"]),
            "current_role": row["current_role"],
            "preferred_role": row["preferred_role"]
        }
    return output

def get_volunteer_record(phone: str, conn=None) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single volunteer record by phone.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    row = repo.get_by_id(phone)
    if row:
        return {
            "name": row["name"],
            "skills": deserialize_list(row["skills"]),
            "available": bool(row["available"]),
            "current_role": row["current_role"],
            "preferred_role": row["preferred_role"]
        }
    return None

def add_volunteer_record(phone: str, display_name: str, skills: list,
                         available: bool, current_role: Optional[str],
                         preferred_role: Optional[str] = None, conn=None) -> None:
    """
    Create/replace a volunteer record in the Volunteers table.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    merged_skills = unify_skills_preserving_earliest(skills)
    data = {
        "phone": phone,
        "name": display_name,
        "skills": serialize_list(merged_skills),
        "available": int(available),
        "current_role": current_role,
        "preferred_role": preferred_role
    }
    repo.create(data, replace=True)

def update_volunteer_record(phone: str, display_name: str, skills: list,
                            available: bool, current_role: Optional[str], conn=None) -> None:
    """
    Update an existing volunteer record.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    merged_skills = unify_skills_preserving_earliest(skills)
    data = {
        "name": display_name,
        "skills": serialize_list(merged_skills),
        "available": int(available),
        "current_role": current_role,
        "preferred_role": current_role
    }
    repo.update(phone, data)

def delete_volunteer_record(phone: str, conn=None) -> None:
    """
    Delete a volunteer by phone from the Volunteers table.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    repo.delete(phone)

def add_deleted_volunteer_record(phone: str, name: str, skills: list, available: bool,
                                 current_role: Optional[str], preferred_role: Optional[str] = None, conn=None) -> None:
    """
    Insert a record into DeletedVolunteers.
    """
    repo = DeletedVolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    merged_skills = unify_skills_preserving_earliest(skills)
    data = {
        "phone": phone,
        "name": name,
        "skills": serialize_list(merged_skills),
        "available": int(available),
        "current_role": current_role,
        "preferred_role": preferred_role
    }
    repo.create(data, replace=True)

def remove_deleted_volunteer_record(phone: str, conn=None) -> None:
    """
    Remove a record from DeletedVolunteers by phone.
    """
    repo = DeletedVolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    repo.delete(phone)

# End of db/volunteers.py