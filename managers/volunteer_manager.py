#!/usr/bin/env python
"""
managers/volunteer_manager.py - Core volunteer management for volunteers (registration, deletion, check-in).
Bridges code for role/skill logic so older tests still pass.
"""

import logging
from typing import Optional, List, Dict, Any

from core.exceptions import VolunteerError
from db.volunteers import (
    get_all_volunteers,
    get_volunteer_record,
    add_volunteer_record,
    update_volunteer_record,
    delete_volunteer_record,
    add_deleted_volunteer_record,
    remove_deleted_volunteer_record
)
from core.transaction import atomic_transaction
from core.concurrency import per_phone_lock
from core.validators import validate_phone_number
from managers.utils import normalize_name
from managers.volunteer_role_manager import ROLE_MANAGER, ROLE_SKILL_REQUIREMENTS
from managers.volunteer_skills_manager import (
    unify_skills_preserving_earliest,
    SKILLS_MANAGER
)

logger = logging.getLogger(__name__)

class VolunteerManager:
    """
    VolunteerManager - Orchestrates volunteer operations (register, delete, check_in, etc.)
    and integrates role/skill assignment from subordinate managers.
    """

    def register_volunteer(self, phone: str, name: str, skills: List[str],
                           available: bool = True, current_role: Optional[str] = None) -> str:
        validate_phone_number(phone)

        if not isinstance(available, bool):
            try:
                available = bool(int(available))
            except (ValueError, TypeError):
                raise VolunteerError("Available must be 0 or 1.")

        from db.volunteers import get_volunteer_record as gv_record
        with per_phone_lock(phone):
            with atomic_transaction(exclusive=True) as conn:
                remove_deleted_volunteer_record(phone, conn=conn)

                record = gv_record(phone, conn=conn)
                if record:
                    # If "skip", become "Anonymous"
                    updated_name = "Anonymous" if name.lower() == "skip" else name
                    existing_skills = record["skills"]
                    merged_skills = set(existing_skills).union(s.strip() for s in skills)
                    updated_name = normalize_name(updated_name, phone)
                    new_role = (current_role.strip() if current_role and current_role.strip()
                                else record["current_role"])

                    merged_skills_list = unify_skills_preserving_earliest(list(merged_skills))
                    update_volunteer_record(
                        phone, updated_name, merged_skills_list, available, new_role, record.get("preferred_role"),
                        conn=conn
                    )
                    logger.info(f"Volunteer {phone} updated: name='{updated_name}', skills={merged_skills_list}, "
                                f"available={available}, role='{new_role}'")
                    from core.messages import VOLUNTEER_UPDATED
                    return VOLUNTEER_UPDATED.format(name=updated_name)
                else:
                    final_name = "Anonymous" if name.lower() == "skip" or not name.strip() else name
                    final_name = normalize_name(final_name, phone)
                    role_to_set = (current_role.strip() if current_role and current_role.strip() else None)
                    merged_skills_list = unify_skills_preserving_earliest(skills)

                    add_volunteer_record(
                        phone, final_name, merged_skills_list, available, role_to_set, role_to_set, conn=conn
                    )
                    logger.info(f"New volunteer {phone} registered: name='{final_name}', skills={merged_skills_list}, "
                                f"available={available}, role='{role_to_set}'")
                    from core.messages import NEW_VOLUNTEER_REGISTERED
                    return NEW_VOLUNTEER_REGISTERED.format(name=final_name)

    def delete_volunteer(self, phone: str) -> str:
        record = get_volunteer_record(phone)
        if not record:
            raise VolunteerError("You are not registered.")
        skills = unify_skills_preserving_earliest(record["skills"])
        add_deleted_volunteer_record(
            phone,
            record["name"],
            skills,
            record["available"],
            record["current_role"],
            record.get("preferred_role")
        )
        delete_volunteer_record(phone)
        logger.info(f"Volunteer {phone} record deleted from the system.")
        from core.messages import VOLUNTEER_DELETED
        return VOLUNTEER_DELETED

    def check_in(self, phone: str) -> str:
        record = get_volunteer_record(phone)
        if record:
            merged = unify_skills_preserving_earliest(record["skills"])
            update_volunteer_record(
                phone,
                record["name"],
                merged,
                True,
                record["current_role"],
                record.get("preferred_role")
            )
            logger.info(f"Volunteer {phone} checked in.")
            from core.messages import VOLUNTEER_CHECKED_IN
            return VOLUNTEER_CHECKED_IN.format(name=normalize_name(record['name'], phone))
        raise VolunteerError("Volunteer not found.")

    def volunteer_status(self) -> str:
        all_vols = get_all_volunteers()
        lines = []
        for phone, data in all_vols.items():
            name = normalize_name(data.get("name", phone), phone)
            availability = "Available" if data.get("available") else "Not Available"
            current_role = data.get("current_role") or "None"
            preferred_role = data.get("preferred_role") or "None"
            lines.append(f"{name}: {availability}, Assigned Role: {current_role}, Preferred Role: {preferred_role}")
        return "\n".join(lines)

    def list_all_volunteers(self) -> Dict[str, Dict[str, Any]]:
        return get_all_volunteers()

    def list_all_volunteers_list(self) -> List[Dict[str, Any]]:
        volunteers_dict = self.list_all_volunteers()
        result = []
        for phone, data in volunteers_dict.items():
            row = {
                "phone": phone,
                "name": data.get("name"),
                "skills": data.get("skills", []),
                "available": data.get("available"),
                "current_role": data.get("current_role"),
                "preferred_role": data.get("preferred_role")
            }
            result.append(row)
        return result

    def list_deleted_volunteers(self) -> List[Dict[str, Any]]:
        from db.repository import execute_sql
        query = "SELECT * FROM DeletedVolunteers ORDER BY deleted_at DESC"
        return execute_sql(query, fetchall=True)

    # Bridge to role manager
    def list_roles(self) -> List[str]:
        return ROLE_MANAGER.list_roles()

    def assign_role(self, phone: str, role: str) -> str:
        return ROLE_MANAGER.assign_role(phone, role)

    def switch_role(self, phone: str, role: str) -> str:
        return ROLE_MANAGER.switch_role(phone, role)

    def unassign_role(self, phone: str) -> str:
        return ROLE_MANAGER.unassign_role(phone)

    # Bridge to skill manager
    def assign_volunteer(self, skill: str, role: str) -> Optional[str]:
        return SKILLS_MANAGER.assign_volunteer(skill, role)

    def add_skills(self, phone: str, new_skills: List[str]) -> str:
        """
        add_skills - Preserves existing volunteer name and merges new skills.
        Raises VolunteerError if volunteer does not exist.
        """
        validate_phone_number(phone)
        with per_phone_lock(phone):
            with atomic_transaction(exclusive=True) as conn:
                record = get_volunteer_record(phone, conn=conn)
                if not record:
                    raise VolunteerError("Volunteer not found.")
                merged = unify_skills_preserving_earliest(record["skills"] + new_skills)
                update_volunteer_record(
                    phone,
                    record["name"],
                    merged,
                    record["available"],
                    record["current_role"],
                    record.get("preferred_role"),
                    conn=conn
                )
        return f"Skills updated for {record['name']}"

VOLUNTEER_MANAGER = VolunteerManager()

def register_volunteer(phone, name, skills, available=True, current_role=None):
    return VOLUNTEER_MANAGER.register_volunteer(phone, name, skills, available, current_role)

def delete_volunteer(phone):
    return VOLUNTEER_MANAGER.delete_volunteer(phone)

def check_in(phone):
    return VOLUNTEER_MANAGER.check_in(phone)

def volunteer_status():
    return VOLUNTEER_MANAGER.volunteer_status()

def find_available_volunteer(skill: str):
    return SKILLS_MANAGER.find_available_volunteer(skill)

def get_all_skills():
    return SKILLS_MANAGER.get_all_skills()

def list_roles():
    return VOLUNTEER_MANAGER.list_roles()

def assign_role(phone: str, role: str):
    return VOLUNTEER_MANAGER.assign_role(phone, role)

def switch_role(phone: str, role: str):
    return VOLUNTEER_MANAGER.switch_role(phone, role)

def unassign_role(phone: str):
    return VOLUNTEER_MANAGER.unassign_role(phone)

from .volunteer_role_manager import ROLE_SKILL_REQUIREMENTS
ROLE_SKILL_REQUIREMENTS = ROLE_SKILL_REQUIREMENTS

# End of managers/volunteer_manager.py