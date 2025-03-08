#!/usr/bin/env python
"""
core/database/volunteers.py - Volunteer-related database operations.
Provides functions to manage volunteer records, including adding, updating, retrieving, and deleting volunteers,
and handles conversion of skills lists to comma-separated strings.
Now also stores and retrieves the preferred_role field.
"""

from typing import Dict, Any, Optional, List
from .helpers import execute_sql

def serialize_skills(skills: List[str]) -> str:
    """
    serialize_skills - Converts a list of skills into a comma-separated string.
    
    Args:
        skills (List[str]): The list of skills.
        
    Returns:
        str: A comma-separated string of skills.
    """
    return ",".join(skills)

def deserialize_skills(skills_str: Optional[str]) -> List[str]:
    """
    deserialize_skills - Converts a comma-separated skills string into a list of trimmed skill names.
    
    Args:
        skills_str (Optional[str]): The string containing skills separated by commas.
    
    Returns:
        List[str]: A list of individual skill names.
    """
    if not skills_str:
        return []
    return [skill.strip() for skill in skills_str.split(",") if skill.strip()]

# For backwards compatibility
parse_skills = deserialize_skills

def get_all_volunteers() -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all volunteer records from the database.
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary of volunteer records keyed by phone number.
    """
    rows = execute_sql("SELECT * FROM Volunteers", fetchall=True)
    volunteers = {}
    for row in rows:
        preferred_role = row["preferred_role"] if "preferred_role" in row.keys() else None
        volunteers[row["phone"]] = {
            "name": row["name"],
            "skills": deserialize_skills(row["skills"]),
            "available": bool(row["available"]),
            "current_role": row["current_role"],
            "preferred_role": preferred_role
        }
    return volunteers

def get_volunteer_record(phone: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single volunteer record by phone number.
    
    Args:
        phone (str): The volunteer's phone number.
    
    Returns:
        Optional[Dict[str, Any]]: The volunteer record or None if not found.
    """
    row = execute_sql("SELECT * FROM Volunteers WHERE phone = ?", (phone,), fetchone=True)
    if row:
        preferred_role = row["preferred_role"] if "preferred_role" in row.keys() else None
        return {
            "name": row["name"],
            "skills": deserialize_skills(row["skills"]),
            "available": bool(row["available"]),
            "current_role": row["current_role"],
            "preferred_role": preferred_role
        }
    return None

def add_volunteer_record(phone: str, display_name: str, skills: list, available: bool, current_role: Optional[str], preferred_role: Optional[str] = None) -> None:
    """
    Add a new volunteer record to the database.
    
    Args:
        phone (str): The volunteer's phone number.
        display_name (str): The volunteer's display name.
        skills (list): List of skills.
        available (bool): Availability status.
        current_role (Optional[str]): Current assigned role.
        preferred_role (Optional[str]): Preferred role.
    """
    skills_str = serialize_skills(skills)
    execute_sql(
        "INSERT OR REPLACE INTO Volunteers (phone, name, skills, available, current_role, preferred_role) VALUES (?, ?, ?, ?, ?, ?)",
        (phone, display_name, skills_str, int(available), current_role, preferred_role),
        commit=True
    )

def update_volunteer_record(phone: str, display_name: str, skills: list, available: bool, current_role: Optional[str]) -> None:
    """
    Update an existing volunteer record in the database.
    
    Args:
        phone (str): The volunteer's phone number.
        display_name (str): The volunteer's display name.
        skills (list): List of skills.
        available (bool): Availability status.
        current_role (Optional[str]): Current assigned role.
    """
    skills_str = serialize_skills(skills)
    execute_sql(
        """
        UPDATE Volunteers 
        SET name = ?, skills = ?, available = ?, current_role = ?
        WHERE phone = ?
        """,
        (display_name, skills_str, int(available), current_role, phone),
        commit=True
    )

def delete_volunteer_record(phone: str) -> None:
    """
    Delete a volunteer record from the Volunteers table.
    
    Args:
        phone (str): The volunteer's phone number.
    """
    execute_sql("DELETE FROM Volunteers WHERE phone = ?", (phone,), commit=True)

def add_deleted_volunteer_record(phone: str, name: str, skills: list, available: bool, current_role: Optional[str], preferred_role: Optional[str] = None) -> None:
    """
    Add a volunteer record to the DeletedVolunteers (trash) table.
    
    Args:
        phone (str): The volunteer's phone number.
        name (str): The volunteer's name.
        skills (list): List of skills.
        available (bool): Availability status.
        current_role (Optional[str]): Current assigned role.
        preferred_role (Optional[str]): Preferred role.
    """
    skills_str = serialize_skills(skills)
    execute_sql(
        "INSERT OR REPLACE INTO DeletedVolunteers (phone, name, skills, available, current_role, preferred_role) VALUES (?, ?, ?, ?, ?, ?)",
        (phone, name, skills_str, int(available), current_role, preferred_role),
        commit=True
    )

def remove_deleted_volunteer_record(phone: str) -> None:
    """
    Remove a volunteer record from the DeletedVolunteers table.
    
    Args:
        phone (str): The volunteer's phone number.
    """
    execute_sql("DELETE FROM DeletedVolunteers WHERE phone = ?", (phone,), commit=True)

# End of core/database/volunteers.py