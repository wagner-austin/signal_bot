#!/usr/bin/env python
"""
managers/volunteer_skills_manager.py
------------------------------------
Manages skill-related logic for volunteers, including listing available skills,
finding volunteers with certain skill(s), auto-assigning volunteers based on skills,
and unifying duplicates while preserving earliest-typed forms.
"""

import logging
from typing import Optional
from db.volunteers import get_all_volunteers, get_volunteer_record, update_volunteer_record
from core.exceptions import VolunteerError
from core.transaction import atomic_transaction
from managers.volunteer_manager import normalize_name

logger = logging.getLogger(__name__)

AVAILABLE_SKILLS = [
    "Event Coordination",
    "Volunteer Management",
    "Logistics Oversight",
    "Public Speaking",
    "Press Communication",
    "Volunteer Recruitment",
    "Crowd Management",
    "Peacekeeping",
    "Greeter",
    "Chant Leading",
    "General Event Support"
]


def unify_skills_preserving_earliest(skills: list) -> list:
    """
    Merge duplicate skill entries by ignoring case, but preserve the earliest typed case.
    
    Args:
        skills (list): A list of raw skill strings (possibly repeated, mixed-case).
        
    Returns:
        list: The merged list of skills, each in the earliest typed case.
    """
    seen_lower = set()
    result = []
    for s in skills:
        stripped = s.strip()
        lower = stripped.lower()
        if lower not in seen_lower:
            seen_lower.add(lower)
            result.append(stripped)
    return result


class VolunteerSkillsManager:
    """
    VolunteerSkillsManager - Handles volunteer skill logic, searching, and auto-assignment.
    """

    def get_all_skills(self):
        """
        Retrieve the list of available skills from AVAILABLE_SKILLS.
        """
        return AVAILABLE_SKILLS

    def find_available_volunteer(self, skill: str) -> Optional[str]:
        """
        Finds the first available volunteer with the specified skill (case-insensitive)
        who has no assigned role.
        """
        all_vols = get_all_volunteers()
        for phone, data in all_vols.items():
            vskills = [s.lower() for s in data.get("skills", [])]
            if skill.lower() in vskills and data.get("available") and data.get("current_role") is None:
                return normalize_name(data.get("name", phone), phone)
        return None

    def assign_volunteer(self, skill: str, role: str) -> Optional[str]:
        """
        Finds the first volunteer with a given skill who is available
        and has no current role, then assigns them the provided role.
        Returns the volunteer's normalized name if assigned, else None.
        """
        volunteers = get_all_volunteers()
        target_phone = None
        for phone, data in volunteers.items():
            if any(skill.lower() == s.lower() for s in data.get("skills", [])) \
               and data.get("available") \
               and data.get("current_role") is None:
                target_phone = phone
                break

        if target_phone:
            try:
                with atomic_transaction() as conn:
                    rec = get_volunteer_record(target_phone, conn=conn)
                    if rec:
                        merged_skills = rec.get("skills", [])
                        update_volunteer_record(
                            target_phone,
                            rec["name"],
                            merged_skills,
                            rec["available"],
                            role,
                            conn=conn
                        )
                        return normalize_name(rec["name"], target_phone)
            except Exception:
                return None
        return None


SKILLS_MANAGER = VolunteerSkillsManager()

# End of managers/volunteer_skills_manager.py