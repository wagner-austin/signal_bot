"""
volunteer_manager.py - Manages volunteer data and registration.
Uses the SQLite database as the single source of truth for all volunteer data.
Provides functions for volunteer status, check-in, sign-up, assignment, and skill tracking.
"""

import logging
from typing import Optional, Dict, Any, List
from core.database import get_all_volunteers, get_volunteer_record, add_volunteer_record, update_volunteer_record

logger = logging.getLogger(__name__)

def normalize_name(name: str, fallback: str) -> str:
    """
    Normalize the volunteer's name.
    If the name is equal to the fallback (typically the phone number), return "Anonymous".
    Otherwise, return the original name.
    
    Args:
        name (str): The original name.
        fallback (str): The fallback value, usually the phone number.
    
    Returns:
        str: The normalized name.
    """
    return name if name != fallback else "Anonymous"

class VolunteerManager:
    def __init__(self) -> None:
        """
        Initializes the VolunteerManager.
        No in-memory cache is maintained; all operations use the database.
        """
        pass

    def find_available_volunteer(self, skill: str) -> Optional[str]:
        """
        Find the first available volunteer with the specified skill.
        
        Args:
            skill (str): The required skill.
        Returns:
            Optional[str]: The volunteer's name if found, else None.
        """
        volunteers = get_all_volunteers()
        for phone, data in volunteers.items():
            if skill in data.get("skills", []) and data.get("available") and data.get("current_role") is None:
                name = normalize_name(data.get("name", phone), phone)
                return name
        logger.warning(f"[find_available_volunteer] No available volunteer found with skill '{skill}'.")
        return None

    def assign_volunteer(self, skill: str, role: str) -> Optional[str]:
        """
        Assign a volunteer with the given skill to a role.
        
        Args:
            skill (str): The required skill.
            role (str): The role to assign.
        Returns:
            Optional[str]: The volunteer's name if assignment is successful, else None.
        """
        volunteers = get_all_volunteers()
        target_phone = None
        for phone, data in volunteers.items():
            if skill in data.get("skills", []) and data.get("available") and data.get("current_role") is None:
                target_phone = phone
                break
        if target_phone:
            record = get_volunteer_record(target_phone)
            if record:
                update_volunteer_record(
                    target_phone,
                    record["name"],
                    record.get("skills", []),
                    record["available"],
                    role
                )
                name = normalize_name(record["name"], target_phone)
                return name
        return None

    def volunteer_status(self) -> str:
        """
        Retrieve and format the current volunteer status from the database.
        
        Returns:
            str: Volunteer statuses formatted as one line per volunteer.
        """
        volunteers = get_all_volunteers()
        status_lines = []
        for phone, data in volunteers.items():
            name = normalize_name(data.get("name", phone), phone)
            availability = "Available" if data.get("available") else "Not Available"
            role = data.get("current_role") if data.get("current_role") else "None"
            status_lines.append(f"{name}: {availability}, Current Role: {role}")
        return "\n".join(status_lines)

    def check_in(self, phone: str) -> str:
        """
        Check in a volunteer (by phone), marking them as available.
        
        Args:
            phone (str): The volunteer's phone number.
        Returns:
            str: Confirmation or error message.
        """
        record = get_volunteer_record(phone)
        if record:
            update_volunteer_record(phone, record["name"], record.get("skills", []), True, record.get("current_role"))
            name = normalize_name(record["name"], phone)
            return f"Volunteer '{name}' has been checked in and is now available."
        return "Volunteer not found."

    def sign_up(self, phone: str, name: str, skills: List[str]) -> str:
        """
        Register a new volunteer or update an existing one.
        Writes changes directly to the database.
        
        Args:
            phone (str): The volunteer's phone number.
            name (str): The volunteer's full name.
            skills (List[str]): A list of skills.
        Returns:
            str: Confirmation message.
        """
        record = get_volunteer_record(phone)
        if record:
            updated_name = record["name"] if name.lower() == "skip" else name
            current_skills = set(record.get("skills", []))
            updated_skills = list(current_skills.union(skills))
            updated_name = normalize_name(updated_name, phone)
            update_volunteer_record(phone, updated_name, updated_skills, True, record.get("current_role"))
            return f"Volunteer '{updated_name}' updated"
        else:
            final_name = "Anonymous" if name.lower() == "skip" or name.strip() == "" else name
            final_name = normalize_name(final_name, phone)
            add_volunteer_record(phone, final_name, skills, True, None)
            return f"New volunteer '{final_name}' registered"

# Expose a single instance for volunteer management.
VOLUNTEER_MANAGER = VolunteerManager()
# Global dictionary to track pending registrations (or updates) by sender's phone.
PENDING_REGISTRATIONS: Dict[str, bool] = {}

# End of managers/volunteer_manager.py
