"""
managers/volunteer_manager.py
--------------------
Encapsulates volunteer management by wrapping volunteer data in a VolunteerManager class.
Provides logging for volunteer assignments and for cases where no volunteer is found.
"""

import logging
from typing import Optional

class VolunteerManager:
    def __init__(self) -> None:
        self.volunteers = {
            'Jen': {'skills': ['Event Coordination', 'Volunteer Management', 'Logistics Oversight'], 'available': True, 'current_role': None},
            'Daniel': {'skills': ['Public Speaking', 'Press Communication'], 'available': True, 'current_role': None},
            'Julie': {'skills': ['Volunteer Recruitment', 'Event Coordination'], 'available': True, 'current_role': None},
            'Dawn': {'skills': ['Crowd Management', 'Peacekeeping'], 'available': True, 'current_role': None},
            'Austin': {'skills': ['Crowd Management', 'Volunteer Assistance'], 'available': True, 'current_role': None},
            'Raquel': {'skills': ['Greeter'], 'available': True, 'current_role': None},
            'Spence': {'skills': ['Chant Leading'], 'available': True, 'current_role': None},
            'Lynda Young': {'skills': ['General Event Support'], 'available': True, 'current_role': None}
        }

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
                logging.info(f"Volunteer '{name}' found with skill '{skill}'.")
                return name
        logging.warning(f"No available volunteer found with skill '{skill}'.")
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
            logging.info(f"Volunteer '{volunteer}' assigned to role '{role}'.")
            return volunteer
        logging.warning(f"Failed to assign volunteer for skill '{skill}' to role '{role}'.")
        return None

# Expose a single instance for volunteer management.
VOLUNTEER_MANAGER = VolunteerManager()

# End of managers/volunteer_manager.py