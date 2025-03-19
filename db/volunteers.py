#!/usr/bin/env python
"""
db/volunteers.py
----------------
Volunteer-related database operations using a repository pattern.
Removes domain logic (unify_skills_preserving_earliest) to avoid circular imports.

Now uses only a single 'role' column; references to 'current_role' or 'preferred_role'
are removed. Retains 'skills' and availability logic as before.

Focuses on modular, unified, consistent code that facilitates future updates.
"""

from typing import Dict, Any, Optional, List
from db.repository import VolunteerRepository, DeletedVolunteerRepository
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
            "role": row["role"]
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
            "role": row["role"]
        }
    return None


def add_volunteer_record(phone: str,
                         display_name: str,
                         skills: list,
                         available: bool,
                         role: Optional[str] = 'registered',
                         conn=None) -> None:
    """
    Create/replace a volunteer record in the Volunteers table with a single role field.
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
        "role": role
    }
    repo.create(data, replace=True)


def update_volunteer_record(phone: str,
                            display_name: str,
                            skills: list,
                            available: bool,
                            role: str,
                            conn=None) -> None:
    """
    update_volunteer_record - Update an existing volunteer record, including the single 'role'.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    data = {
        "name": display_name,
        "skills": serialize_list(skills),
        "available": int(available),
        "role": role
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


def add_deleted_volunteer_record(phone: str,
                                 name: str,
                                 skills: list,
                                 available: bool,
                                 role: str,
                                 conn=None) -> None:
    """
    Insert a record into DeletedVolunteers using a single 'role' column.
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
        "role": role
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