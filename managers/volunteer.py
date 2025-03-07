"""
managers/volunteer.py - Manages volunteer data and registration.
Uses the SQLite database as the single source of truth for volunteer data.
Provides functions for volunteer status, check-in, sign-up, assignment, deletion, and skill tracking.
This module modifies global state in the database and is used by other managers.
"""

import logging
from typing import Optional, List
from core.database import (
    get_all_volunteers, get_volunteer_record, add_volunteer_record,
    update_volunteer_record, delete_volunteer_record, add_deleted_volunteer_record,
    remove_deleted_volunteer_record
)
from core.skill_config import AVAILABLE_SKILLS

logger = logging.getLogger(__name__)

def normalize_name(name: str, fallback: str) -> str:
    """
    normalize_name - Normalizes a volunteer's name.
    Returns "Anonymous" if the name equals the fallback (typically the phone number).
    """
    return name if name != fallback else "Anonymous"

class VolunteerManager:
    def __init__(self) -> None:
        """
        VolunteerManager - Initializes the volunteer manager.
        No in-memory cache is maintained; all operations use the database.
        """
        pass

    def find_available_volunteer(self, skill: str) -> Optional[str]:
        """
        find_available_volunteer - Finds the first available volunteer with the specified skill.
        
        Args:
            skill (str): The required skill.
        Returns:
            Optional[str]: The volunteer's name if found; otherwise, None.
        """
        volunteers = get_all_volunteers()
        for phone, data in volunteers.items():
            if skill in data.get("skills", []) and data.get("available") and data.get("current_role") is None:
                return normalize_name(data.get("name", phone), phone)
        logger.warning(f"No available volunteer found with skill '{skill}'.")
        return None

    def assign_volunteer(self, skill: str, role: str) -> Optional[str]:
        """
        assign_volunteer - Assigns a volunteer with the given skill to a role.
        
        Args:
            skill (str): The required skill.
            role (str): The role to assign.
        Returns:
            Optional[str]: The volunteer's name if assignment is successful; otherwise, None.
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
                return normalize_name(record["name"], target_phone)
        return None

    def volunteer_status(self) -> str:
        """
        volunteer_status - Retrieves and formats the current volunteer status from the database.
        
        Returns:
            str: A list of volunteer statuses (one line per volunteer).
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
        check_in - Checks in a volunteer, marking them as available.
        
        Args:
            phone (str): The volunteer's phone number.
        Returns:
            str: A confirmation or error message.
        Side Effects:
            Updates the volunteer's availability in the database.
        """
        record = get_volunteer_record(phone)
        if record:
            update_volunteer_record(phone, record["name"], record.get("skills", []), True, record.get("current_role"))
            return f"Volunteer '{normalize_name(record['name'], phone)}' has been checked in and is now available."
        return "Volunteer not found."

    def sign_up(self, phone: str, name: str, skills: List[str]) -> str:
        """
        sign_up - Registers a new volunteer or updates an existing one.
        
        Args:
            phone (str): The volunteer's phone number.
            name (str): The volunteer's full name.
            skills (List[str]): A list of skills.
        Returns:
            str: A confirmation message.
        Side Effects:
            Inserts or updates the volunteer record in the database and may remove a record from DeletedVolunteers.
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
            remove_deleted_volunteer_record(phone)
            final_name = "Anonymous" if name.lower() == "skip" or name.strip() == "" else name
            final_name = normalize_name(final_name, phone)
            add_volunteer_record(phone, final_name, skills, True, None)
            return f"New volunteer '{final_name}' registered"

    def delete_volunteer(self, phone: str) -> str:
        """
        delete_volunteer - Deletes a volunteer's registration.
        
        Args:
            phone (str): The volunteer's phone number.
        Returns:
            str: A confirmation message.
        Side Effects:
            Moves the volunteer record to DeletedVolunteers and removes it from active registrations.
        """
        record = get_volunteer_record(phone)
        if not record:
            return "You are not registered."
        add_deleted_volunteer_record(phone, record["name"], record.get("skills", []), record["available"], record.get("current_role"))
        delete_volunteer_record(phone)
        return "Your registration has been deleted. Thank you."

    def get_all_skills(self) -> List[str]:
        """
        get_all_skills - Retrieves the unified list of available skills.
        
        Returns:
            List[str]: A list of skills from the centralized configuration.
        """
        return AVAILABLE_SKILLS

# Global instance for volunteer management
VOLUNTEER_MANAGER = VolunteerManager()

# End of managers/volunteer.py