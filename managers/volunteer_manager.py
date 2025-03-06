"""
volunteer_manager.py
--------------------
Encapsulates volunteer management by wrapping volunteer data in a VolunteerManager class.
Loads volunteer data from a separate configuration file.
Provides logging for volunteer assignments and for cases where no volunteer is found.
"""

import logging
from typing import Optional, Dict, Any
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

# Expose a single instance for volunteer management.
VOLUNTEER_MANAGER = VolunteerManager()

# End of managers/volunteer_manager.py