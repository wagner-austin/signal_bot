"""
volunteer_manager.py
--------------------
Handles volunteer management including assigning volunteers to roles.
"""

VOLUNTEERS = {
    'Jen': {'skills': ['Event Coordination', 'Volunteer Management', 'Logistics Oversight'], 'available': True, 'current_role': None},
    'Daniel': {'skills': ['Public Speaking', 'Press Communication'], 'available': True, 'current_role': None},
    'Julie': {'skills': ['Volunteer Recruitment', 'Event Coordination'], 'available': True, 'current_role': None},
    'Dawn': {'skills': ['Crowd Management', 'Peacekeeping'], 'available': True, 'current_role': None},
    'Austin': {'skills': ['Crowd Management', 'Volunteer Assistance'], 'available': True, 'current_role': None},
    'Raquel': {'skills': ['Greeter'], 'available': True, 'current_role': None},
    'Spence': {'skills': ['Chant Leading'], 'available': True, 'current_role': None},
    'Lynda Young': {'skills': ['General Event Support'], 'available': True, 'current_role': None}
}

def find_available_volunteer(skill: str):
    """Find the first available volunteer with the specified skill."""
    for name, data in VOLUNTEERS.items():
        if skill in data['skills'] and data['available'] and data['current_role'] is None:
            return name
    return None

def assign_volunteer(skill: str, role: str):
    """Assign a volunteer with the specified skill to a role."""
    volunteer = find_available_volunteer(skill)
    if volunteer:
        VOLUNTEERS[volunteer]['current_role'] = role
        return volunteer
    return None
