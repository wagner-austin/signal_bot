"""
core/database/volunteers.py - Volunteer-related database operations.
Provides functions to manage volunteer records, including adding, updating, retrieving, and deleting volunteers,
using a context manager for connection handling.
"""

from typing import Dict, Any, Optional, List
from .connection import db_connection

def parse_skills(skills_str: Optional[str]) -> List[str]:
    """
    Parse a comma-separated skills string into a list of trimmed skill names.
    
    Args:
        skills_str (Optional[str]): The string containing skills separated by commas.
    
    Returns:
        List[str]: A list of individual skill names.
    """
    if not skills_str:
        return []
    return [skill.strip() for skill in skills_str.split(",") if skill.strip()]

def get_all_volunteers() -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all volunteer records from the database.
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary of volunteer records keyed by phone number.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Volunteers")
        rows = cursor.fetchall()
    volunteers = {}
    for row in rows:
        volunteers[row["phone"]] = {
            "name": row["name"],
            "skills": parse_skills(row["skills"]),
            "available": bool(row["available"]),
            "current_role": row["current_role"]
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
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Volunteers WHERE phone = ?", (phone,))
        row = cursor.fetchone()
    if row:
        return {
            "name": row["name"],
            "skills": parse_skills(row["skills"]),
            "available": bool(row["available"]),
            "current_role": row["current_role"]
        }
    return None

def add_volunteer_record(phone: str, display_name: str, skills: list, available: bool, current_role: Optional[str]) -> None:
    """
    Add a new volunteer record to the database.
    
    Args:
        phone (str): The volunteer's phone number.
        display_name (str): The volunteer's display name.
        skills (list): List of skills.
        available (bool): Availability status.
        current_role (Optional[str]): Current assigned role.
    """
    skills_str = ",".join(skills)
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO Volunteers (phone, name, skills, available, current_role) VALUES (?, ?, ?, ?, ?)",
                       (phone, display_name, skills_str, int(available), current_role))
        conn.commit()

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
    skills_str = ",".join(skills)
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE Volunteers 
        SET name = ?, skills = ?, available = ?, current_role = ?
        WHERE phone = ?
        """, (display_name, skills_str, int(available), current_role, phone))
        conn.commit()

def delete_volunteer_record(phone: str) -> None:
    """
    Delete a volunteer record from the Volunteers table.
    
    Args:
        phone (str): The volunteer's phone number.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Volunteers WHERE phone = ?", (phone,))
        conn.commit()

def add_deleted_volunteer_record(phone: str, name: str, skills: list, available: bool, current_role: Optional[str]) -> None:
    """
    Add a volunteer record to the DeletedVolunteers (trash) table.
    
    Args:
        phone (str): The volunteer's phone number.
        name (str): The volunteer's name.
        skills (list): List of skills.
        available (bool): Availability status.
        current_role (Optional[str]): Current assigned role.
    """
    skills_str = ",".join(skills)
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO DeletedVolunteers (phone, name, skills, available, current_role) VALUES (?, ?, ?, ?, ?)",
                       (phone, name, skills_str, int(available), current_role))
        conn.commit()

def remove_deleted_volunteer_record(phone: str) -> None:
    """
    Remove a volunteer record from the DeletedVolunteers table.
    
    Args:
        phone (str): The volunteer's phone number.
    """
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DeletedVolunteers WHERE phone = ?", (phone,))
        conn.commit()

# End of core/database/volunteers.py