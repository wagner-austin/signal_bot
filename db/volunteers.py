#!/usr/bin/env python
"""
db/volunteers.py
----------------
Volunteer-related database operations using a repository pattern.
Removes domain logic (unify_skills_preserving_earliest) to avoid circular imports.
"""

from typing import Dict, Any, Optional, List
from db.repository import VolunteerRepository, DeletedVolunteerRepository
# Removed circular import to managers.volunteer_skills_manager
from core.serialization_utils import (
    serialize_list,
    deserialize_list
)
from db.connection import get_connection


def get_all_volunteers(conn=None) -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all volunteers from the Volunteers table, returning phone->record mapping.
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
    The manager layer is responsible for unifying skills before calling this function.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    data = {
        "phone": phone,
        "name": display_name,
        "skills": serialize_list(skills),
        "available": int(available),
        "current_role": current_role,
        "preferred_role": preferred_role
    }
    repo.create(data, replace=True)


def update_volunteer_record(phone: str, display_name: str, skills: list,
                            available: bool, current_role: Optional[str],
                            preferred_role: Optional[str] = None, conn=None) -> None:
    """
    update_volunteer_record - Update an existing volunteer record, including an optional preferred_role.
    The manager layer is responsible for unifying skills before calling this function.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    data = {
        "name": display_name,
        "skills": serialize_list(skills),
        "available": int(available),
        "current_role": current_role,
        "preferred_role": preferred_role
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
    The manager layer is responsible for unifying skills before calling this function.
    """
    repo = DeletedVolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    data = {
        "phone": phone,
        "name": name,
        "skills": serialize_list(skills),
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