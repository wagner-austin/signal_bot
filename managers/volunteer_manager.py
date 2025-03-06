"""
managers/volunteer_manager.py
--------------------
Encapsulates volunteer management by wrapping volunteer data in a VolunteerManager class.
"""

class VolunteerManager:
    def __init__(self):
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

    def find_available_volunteer(self, skill: str) -> str:
        """Find the first available volunteer with the specified skill."""
        for name, data in self.volunteers.items():
            if skill in data['skills'] and data['available'] and data['current_role'] is None:
                return name
        return None

    def assign_volunteer(self, skill: str, role: str) -> str:
        """Assign a volunteer with the specified skill to a role."""
        volunteer = self.find_available_volunteer(skill)
        if volunteer:
            self.volunteers[volunteer]['current_role'] = role
            return volunteer
        return None

# Module-level instance for volunteer management.
VOLUNTEER_MANAGER = VolunteerManager()

def find_available_volunteer(skill: str) -> str:
    """Module-level function to find an available volunteer using the VOLUNTEER_MANAGER instance."""
    return VOLUNTEER_MANAGER.find_available_volunteer(skill)

def assign_volunteer(skill: str, role: str) -> str:
    """Module-level function to assign a volunteer using the VOLUNTEER_MANAGER instance."""
    return VOLUNTEER_MANAGER.assign_volunteer(skill, role)

# End of managers/volunteer_manager.py