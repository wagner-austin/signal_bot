"""
volunteer_manager.py - Encapsulates volunteer management by wrapping volunteer data in a VolunteerManager class.
Loads volunteer data from a separate configuration file and provides logging for volunteer assignments.
Also includes functions to check volunteer status, check in, and sign up new volunteers.
"""

import logging
from typing import Optional, Dict, Any, List
from core.volunteer_config import VOLUNTEER_DATA

logger = logging.getLogger(__name__)

class VolunteerManager:
    def __init__(self) -> None:
        """
        Initializes the VolunteerManager with volunteer data loaded from the configuration file.
        """
        # Use a copy of the data to avoid modifying the original configuration.
        self.volunteers: Dict[str, Dict[str, Any]] = {k: v.copy() for k, v in VOLUNTEER_DATA.items()}

    def find_available_volunteer(self, skill: str) -> Optional[str]:
        """
        Find the first available volunteer with the specified skill.
        
        Args:
            skill (str): The required skill for the volunteer.
            
        Returns:
            Optional[str]: The name of the available volunteer, or None if no volunteer is available.
        """
        for name, data in self.volunteers.items():
            if skill in data['skills'] and data['available'] and data['current_role'] is None:
                logger.info(f"[find_available_volunteer] Volunteer '{name}' found with skill '{skill}'.")
                return name
        logger.warning(f"[find_available_volunteer] No available volunteer found with skill '{skill}'.")
        return None

    def assign_volunteer(self, skill: str, role: str) -> Optional[str]:
        """
        Assign a volunteer with the specified skill to a role.
        
        Args:
            skill (str): The required skill for the volunteer.
            role (str): The role to assign to the volunteer.
            
        Returns:
            Optional[str]: The name of the assigned volunteer, or None if no volunteer is available.
        """
        volunteer = self.find_available_volunteer(skill)
        if volunteer:
            self.volunteers[volunteer]['current_role'] = role
            logger.info(f"[assign_volunteer] Volunteer '{volunteer}' assigned to role '{role}'.")
            return volunteer
        logger.warning(f"[assign_volunteer] Failed to assign volunteer for skill '{skill}' to role '{role}'.")
        return None

    def volunteer_status(self) -> str:
        """
        Get the status of all volunteers.
        
        Returns:
            str: A formatted string listing each volunteer's name, availability, and current role.
        """
        status_lines = []
        for name, data in self.volunteers.items():
            availability = "Available" if data.get("available") else "Not Available"
            role = data.get("current_role") if data.get("current_role") else "None"
            status_lines.append(f"{name}: {availability}, Current Role: {role}")
        return "\n".join(status_lines)

    def check_in(self, name: str) -> str:
        """
        Check in a volunteer, marking them as available.
        
        Args:
            name (str): The name of the volunteer.
            
        Returns:
            str: A confirmation message or error message if the volunteer is not found.
        """
        if name in self.volunteers:
            self.volunteers[name]["available"] = True
            logger.info(f"[check_in] Volunteer '{name}' checked in and marked as available.")
            return f"Volunteer '{name}' has been checked in and is now available."
        else:
            logger.warning(f"[check_in] Volunteer '{name}' not found.")
            return f"Volunteer '{name}' not found."

    def sign_up(self, name: str, skills: List[str]) -> str:
        """
        Sign up a new volunteer or update an existing volunteer's skills.
        
        Args:
            name (str): The name of the volunteer.
            skills (List[str]): A list of skills for the volunteer.
            
        Returns:
            str: A confirmation message indicating the sign-up status.
        """
        if name in self.volunteers:
            # Update existing volunteer's skills by adding new ones (if not already present)
            current_skills = set(self.volunteers[name].get("skills", []))
            updated_skills = current_skills.union(skills)
            self.volunteers[name]["skills"] = list(updated_skills)
            self.volunteers[name]["available"] = True
            logger.info(f"[sign_up] Volunteer '{name}' updated with skills {updated_skills}.")
            return f"Volunteer '{name}' updated with skills: {', '.join(updated_skills)}."
        else:
            # Add new volunteer
            self.volunteers[name] = {
                "skills": skills,
                "available": True,
                "current_role": None
            }
            logger.info(f"[sign_up] New volunteer '{name}' signed up with skills {skills}.")
            return f"New volunteer '{name}' signed up with skills: {', '.join(skills)}."

# Expose a single instance for volunteer management.
VOLUNTEER_MANAGER = VolunteerManager()

# End of managers/volunteer_manager.py