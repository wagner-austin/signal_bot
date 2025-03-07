"""
managers/volunteer_manager.py - Manages volunteer data and registration.
Uses the SQLite database as the single source of truth for all volunteer data.
Provides functions for volunteer status, check-in, sign-up, assignment, deletion, and skill tracking.
Encapsulates pending registration and deletion actions within the PendingActions manager.
"""

import logging
from typing import Optional, Dict, Any, List
from core.database import (
    get_all_volunteers, get_volunteer_record, add_volunteer_record,
    update_volunteer_record, delete_volunteer_record, add_deleted_volunteer_record,
    remove_deleted_volunteer_record
)

logger = logging.getLogger(__name__)

def normalize_name(name: str, fallback: str) -> str:
    """
    Normalize the volunteer's name.
    If the name is equal to the fallback (typically the phone number), return "Anonymous".
    Otherwise, return the original name.
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
        If a deleted record exists for the phone, it is removed.
        
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
            # If the user exists in the trash, remove that record.
            remove_deleted_volunteer_record(phone)
            final_name = "Anonymous" if name.lower() == "skip" or name.strip() == "" else name
            final_name = normalize_name(final_name, phone)
            add_volunteer_record(phone, final_name, skills, True, None)
            return f"New volunteer '{final_name}' registered"

    def delete_volunteer(self, phone: str) -> str:
        """
        Delete the volunteer registration.
        Stores the deleted record in the trash area and removes it from active registrations.
        
        Args:
            phone (str): The volunteer's phone number.
        Returns:
            str: Confirmation message.
        """
        record = get_volunteer_record(phone)
        if not record:
            return "You are not registered."
        # Store record in trash
        add_deleted_volunteer_record(phone, record["name"], record.get("skills", []), record["available"], record.get("current_role"))
        # Remove from active registrations
        delete_volunteer_record(phone)
        return "Your registration has been deleted. Thank you."

    def get_all_skills(self) -> List[str]:
        """
        Retrieve the unified list of available skills.
        
        Returns:
            List[str]: The list of skills from the centralized skill configuration.
        """
        from core.skill_config import AVAILABLE_SKILLS
        return AVAILABLE_SKILLS

class PendingActions:
    """
    PendingActions - Encapsulates pending registration and deletion actions.
    Manages in-memory state for pending registration/edit and deletion processes.
    """
    def __init__(self) -> None:
        self._registrations: Dict[str, str] = {}
        self._deletions: Dict[str, str] = {}

    # Registration methods
    def set_registration(self, sender: str, mode: str) -> None:
        self._registrations[sender] = mode

    def get_registration(self, sender: str) -> Optional[str]:
        return self._registrations.get(sender)

    def has_registration(self, sender: str) -> bool:
        return sender in self._registrations

    def clear_registration(self, sender: str) -> None:
        self._registrations.pop(sender, None)

    # Deletion methods
    def set_deletion(self, sender: str, mode: str) -> None:
        self._deletions[sender] = mode

    def get_deletion(self, sender: str) -> Optional[str]:
        return self._deletions.get(sender)

    def has_deletion(self, sender: str) -> bool:
        return sender in self._deletions

    def clear_deletion(self, sender: str) -> None:
        self._deletions.pop(sender, None)

# Expose a single instance for volunteer management.
VOLUNTEER_MANAGER = VolunteerManager()
# Global instance for pending actions.
PENDING_ACTIONS = PendingActions()

# End of managers/volunteer_manager.py