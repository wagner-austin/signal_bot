"""
managers/volunteer_role_manager.py
----------------------------------
Manages volunteer roles, recognized role list, skill requirements,
and assigning/unassigning roles. Imports only the needed DB methods and
utility functions directly (no circular references).
"""

import logging
from typing import Optional
from core.exceptions import VolunteerError
from db.volunteers import get_volunteer_record, update_volunteer_record
from managers.utils import normalize_name

logger = logging.getLogger(__name__)

RECOGNIZED_ROLES = [
    "greeter",
    "speaker coordinator",
    "table staff",
    "photographer",
    "medic",
    "emcee",
    "peacekeeper",
    "chant leader"
]

ROLE_SKILL_REQUIREMENTS = {
    "greeter": ["communication", "interpersonal"],
    "speaker coordinator": ["organizational", "communication"],
    "table staff": ["organization"],
    "photographer": ["photography"],
    "medic": ["first aid"],
    "emcee": ["public speaking", "communication"],
    "peacekeeper": ["conflict resolution"],
    "chant leader": ["leadership", "communication"]
}


class VolunteerRoleManager:
    """
    VolunteerRoleManager - Handles domain logic for volunteer roles,
    including recognized roles, skill validation, and assignment.
    """

    def list_roles(self):
        roles_info = []
        for role in RECOGNIZED_ROLES:
            req_skills = ROLE_SKILL_REQUIREMENTS.get(role.lower(), [])
            roles_info.append(f"{role} (requires: {', '.join(req_skills) if req_skills else 'None'})")
        return roles_info

    def update_volunteer_role(self, phone: str, role: Optional[str]) -> None:
        """
        update_volunteer_role - Directly updates the volunteer's preferred_role.
        Retrieves the existing record and updates with the correct name, skills, availability, etc.
        """
        record = get_volunteer_record(phone)
        if not record:
            return
        update_volunteer_record(
            phone,
            record["name"],
            record["skills"],
            record["available"],
            record["current_role"],
            role
        )

    def assign_role(self, phone: str, role: str) -> str:
        role_lower = role.lower()
        valid_roles = [r.lower() for r in RECOGNIZED_ROLES]
        if role_lower not in valid_roles:
            raise VolunteerError(f"Role '{role}' is not recognized.")

        record = get_volunteer_record(phone)
        if not record:
            raise VolunteerError("You are not registered.")

        volunteer_skills = set(s.lower() for s in record.get("skills", []))
        required = set(ROLE_SKILL_REQUIREMENTS.get(role_lower, []))
        if not required.issubset(volunteer_skills):
            raise VolunteerError(
                f"You do not have the necessary skills for the role '{role}'. "
                f"Required: {', '.join(required)}. Your skills: {', '.join(volunteer_skills) or 'None'}."
            )

        self.update_volunteer_role(phone, role)
        logger.info(f"Volunteer {phone} assigned role '{role}'.")
        return f"Your preferred role has been set to '{role}'."

    def switch_role(self, phone: str, role: str) -> str:
        record = get_volunteer_record(phone)
        if not record:
            raise VolunteerError("You are not registered.")
        current = record.get("preferred_role")
        message = f"Switching from '{current}' to '{role}'. " if current else "Setting role to "
        confirmation = self.assign_role(phone, role)
        logger.info(f"Volunteer {phone} switched role from '{current}' to '{role}'.")
        return message + confirmation

    def unassign_role(self, phone: str) -> str:
        record = get_volunteer_record(phone)
        if not record:
            raise VolunteerError("You are not registered.")
        self.update_volunteer_role(phone, None)
        logger.info(f"Volunteer {phone} unassigned their role.")
        return "Your preferred role has been cleared."


ROLE_MANAGER = VolunteerRoleManager()

# End of managers/volunteer_role_manager.py