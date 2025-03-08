#!/usr/bin/env python
"""
volunteers.py --- Volunteer-related database operations.
Provides functions to manage volunteer records using the repository pattern.
This module now uses consistent role fields by updating and retrieving the 'preferred_role' column.
Changes:
 - Use unify_skills_preserving_earliest to unify duplicates ignoring case but preserve earliest typed case.
 - Added external_connection logic to avoid closing shared connections prematurely.
"""

from typing import Dict, Any, Optional, List
from core.database.repository import VolunteerRepository, DeletedVolunteerRepository
from core.serialization_utils import (
    serialize_list,
    deserialize_list,
    unify_skills_preserving_earliest
)
from core.database.connection import get_connection

# Aliases for convenience
serialize_skills = serialize_list
deserialize_skills = deserialize_list
parse_skills = deserialize_list  # for backwards compatibility


def get_all_volunteers(conn=None) -> Dict[str, Dict[str, Any]]:
    """
    get_all_volunteers - Retrieve all volunteers in the database.

    Args:
        conn: Optional existing DB connection for transactional usage.

    Returns:
        A dict mapping phone -> volunteer record data.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
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


def get_volunteer_record(phone: str, conn=None) -> Optional[Dict[str, Any]]:
    """
    get_volunteer_record - Retrieve a single volunteer record by phone.

    Args:
        phone (str): Volunteer phone number.
        conn: Optional DB connection for transactional usage.

    Returns:
        A dict of volunteer data if found, else None.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
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


def add_volunteer_record(phone: str, display_name: str, skills: list,
                         available: bool, current_role: Optional[str],
                         preferred_role: Optional[str] = None, conn=None) -> None:
    """
    add_volunteer_record - Create or replace a volunteer record in the Volunteers table.

    Args:
        phone (str): Volunteer phone
        display_name (str): Volunteer name
        skills (list): List of skill strings
        available (bool): Availability status
        current_role (Optional[str]): Current volunteer role
        preferred_role (Optional[str]): Preferred volunteer role
        conn: Optional DB connection for a transaction
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    merged_skills = unify_skills_preserving_earliest(skills)
    skills_str = serialize_skills(merged_skills)
    data = {
        "phone": phone,
        "name": display_name,
        "skills": skills_str,
        "available": int(available),
        "current_role": current_role,
        "preferred_role": preferred_role
    }
    repo.create(data, replace=True)


def update_volunteer_record(phone: str, display_name: str, skills: list,
                            available: bool, current_role: Optional[str], conn=None) -> None:
    """
    update_volunteer_record - Update an existing volunteer record.

    Args:
        phone (str): Volunteer phone
        display_name (str): Updated name
        skills (list): Merged list of skill strings
        available (bool): Availability status
        current_role (Optional[str]): Current role
        conn: Optional DB connection for a transaction
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    merged_skills = unify_skills_preserving_earliest(skills)
    skills_str = serialize_skills(merged_skills)
    data = {
        "name": display_name,
        "skills": skills_str,
        "available": int(available),
        "current_role": current_role,
        "preferred_role": current_role
    }
    repo.update(phone, data)


def delete_volunteer_record(phone: str, conn=None) -> None:
    """
    delete_volunteer_record - Delete a volunteer by phone from the Volunteers table.
    """
    repo = VolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    repo.delete(phone)


def add_deleted_volunteer_record(phone: str, name: str, skills: list, available: bool,
                                 current_role: Optional[str], preferred_role: Optional[str] = None, conn=None) -> None:
    """
    add_deleted_volunteer_record - Insert a record into DeletedVolunteers.
    """
    repo = DeletedVolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    merged_skills = unify_skills_preserving_earliest(skills)
    skills_str = serialize_skills(merged_skills)
    data = {
        "phone": phone,
        "name": name,
        "skills": skills_str,
        "available": int(available),
        "current_role": current_role,
        "preferred_role": preferred_role
    }
    repo.create(data, replace=True)


def remove_deleted_volunteer_record(phone: str, conn=None) -> None:
    """
    remove_deleted_volunteer_record - Remove a record from DeletedVolunteers by phone.
    """
    repo = DeletedVolunteerRepository(
        connection_provider=lambda: conn or get_connection(),
        external_connection=bool(conn)
    )
    repo.delete(phone)

# End of core/database/volunteers.py