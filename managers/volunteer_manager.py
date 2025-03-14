#!/usr/bin/env python
"""
volunteer_manager.py
--------------------
Aggregated volunteer management with common utilities, operations, queries, and role handling.
Contains code merged from volunteer_common.py, volunteer_operations.py, volunteer_queries.py, and volunteer_roles.py.
Retains as much original code as possible.
"""

import logging
from typing import Optional, List, Dict, Any
from core.exceptions import VolunteerError, ResourceError
from db.volunteers import (
    get_all_volunteers,
    get_volunteer_record,
    update_volunteer_record,
    add_volunteer_record,
    delete_volunteer_record,
    add_deleted_volunteer_record,
    remove_deleted_volunteer_record,
)
from core.transaction import atomic_transaction
from core.concurrency import per_phone_lock
from core.validators import validate_phone_number
from core.serialization_utils import (
    unify_skills_preserving_earliest,
    serialize_list,
    deserialize_list,
)

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# volunteer_common.py (merged)
# --------------------------------------------------------------------
def normalize_name(name: str, fallback: str) -> str:
    """
    normalize_name - Normalizes a volunteer's name.
    Returns "Anonymous" if the name equals the fallback or if the name appears to be a phone number.

    Args:
        name (str): The volunteer's registered name.
        fallback (str): The fallback identifier (typically the volunteer's phone number).

    Returns:
        str: A safe display name that does not reveal any phone numbers.
    """
    import re
    if name == fallback or re.fullmatch(r'\+?\d+', name):
        return "Anonymous"
    return name

# --------------------------------------------------------------------
# volunteer_operations.py (merged)
# --------------------------------------------------------------------
def register_volunteer(phone: str, name: str, skills: List[str],
                       available: bool = True, current_role: Optional[str] = None) -> str:
    """
    register_volunteer - Creates/updates a volunteer in an atomic transaction.
    Raises VolunteerError for invalid input or unexpected errors.
    """
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
                updated_name = record["name"] if name.lower() == "skip" else name
                merged_skills = set(record["skills"]).union(set(sk.strip() for sk in skills))
                updated_name = normalize_name(updated_name, phone)
                new_role = current_role.strip() if current_role and current_role.strip() else record["current_role"]

                merged_skills_list = unify_skills_preserving_earliest(list(merged_skills))
                skills_str = serialize_list(merged_skills_list)

                data = {
                    "name": updated_name,
                    "skills": skills_str,
                    "available": int(available),
                    "current_role": new_role,
                    "preferred_role": new_role,
                }
                update_volunteer_record(phone, data["name"], merged_skills_list, available, new_role, conn=conn)
                logger.info(f"Volunteer {phone} updated: name='{updated_name}', skills={merged_skills_list}, "
                            f"available={available}, role='{new_role}'")
                from core.messages import VOLUNTEER_UPDATED
                return VOLUNTEER_UPDATED.format(name=updated_name)
            else:
                final_name = "Anonymous" if name.lower() == "skip" or not name.strip() else name
                final_name = normalize_name(final_name, phone)
                role_to_set = current_role.strip() if current_role and current_role.strip() else None
                merged_skills_list = unify_skills_preserving_earliest(skills)

                add_volunteer_record(
                    phone, final_name, merged_skills_list, available, role_to_set, role_to_set, conn=conn
                )
                logger.info(f"New volunteer {phone} registered: name='{final_name}', skills={merged_skills_list}, "
                            f"available={available}, role='{role_to_set}'")
                from core.messages import NEW_VOLUNTEER_REGISTERED
                return NEW_VOLUNTEER_REGISTERED.format(name=final_name)

def delete_volunteer(phone: str) -> str:
    """
    delete_volunteer - Deletes a volunteer's registration.
    """
    record = get_volunteer_record(phone)
    if not record:
        raise VolunteerError("You are not registered.")

    add_deleted_volunteer_record(
        phone,
        record["name"],
        record["skills"],
        record["available"],
        record["current_role"],
        record.get("preferred_role")
    )
    delete_volunteer_record(phone)
    logger.info(f"Volunteer {phone} record deleted from the system.")
    from core.messages import VOLUNTEER_DELETED
    return VOLUNTEER_DELETED

def check_in(phone: str) -> str:
    """
    check_in - Marks a volunteer as available.
    """
    record = get_volunteer_record(phone)
    if record:
        update_volunteer_record(phone, record["name"], record["skills"], True, record["current_role"])
        logger.info(f"Volunteer {phone} checked in.")
        from core.messages import VOLUNTEER_CHECKED_IN
        return VOLUNTEER_CHECKED_IN.format(name=normalize_name(record['name'], phone))
    raise VolunteerError("Volunteer not found.")

# --------------------------------------------------------------------
# volunteer_queries.py (merged)
# --------------------------------------------------------------------
def volunteer_status() -> str:
    """
    volunteer_status - Retrieves and formats current volunteer status.

    Returns:
        str: Status information for each volunteer.
    """
    all_vols = get_all_volunteers()
    lines = []
    for phone, data in all_vols.items():
        name = normalize_name(data.get("name", phone), phone)
        availability = "Available" if data.get("available") else "Not Available"
        current_role = data.get("current_role") or "None"
        preferred_role = data.get("preferred_role") or "None"
        lines.append(f"{name}: {availability}, Assigned Role: {current_role}, Preferred Role: {preferred_role}")
    return "\n".join(lines)

def find_available_volunteer(skill: str) -> Optional[str]:
    """
    find_available_volunteer - Finds the first available volunteer with the specified skill (case-insensitive).
    """
    all_vols = get_all_volunteers()
    for phone, data in all_vols.items():
        vskills = [s.lower() for s in data.get("skills", [])]
        if skill.lower() in vskills and data.get("available") and data.get("current_role") is None:
            return normalize_name(data.get("name", phone), phone)
    return None

def get_all_skills() -> List[str]:
    """
    get_all_skills - Retrieves the list of available skills from configuration.
    """
    from core.skill_config import AVAILABLE_SKILLS
    return AVAILABLE_SKILLS

# --------------------------------------------------------------------
# volunteer_roles.py (merged)
# --------------------------------------------------------------------
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

def list_roles() -> List[str]:
    """
    list_roles - Returns a list of recognized roles with their required skills.
    """
    roles_info = []
    for role in RECOGNIZED_ROLES:
        req_skills = ROLE_SKILL_REQUIREMENTS.get(role.lower(), [])
        roles_info.append(f"{role} (requires: {', '.join(req_skills) if req_skills else 'None'})")
    return roles_info

def update_volunteer_role(phone: str, role: Optional[str]) -> None:
    """
    update_volunteer_role - Updates the volunteer's preferred role in the database.
    """
    from db.repository import execute_sql
    execute_sql("UPDATE Volunteers SET preferred_role = ? WHERE phone = ?", (role, phone), commit=True)
    logger.debug(f"Volunteer {phone} updated preferred_role to {role}.")

def assign_role(phone: str, role: str) -> str:
    """
    assign_role - Assigns a preferred role to a volunteer after validating required skills.
    Raises VolunteerError for invalid role, unregistered volunteer, or insufficient skills.
    """
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
        raise VolunteerError(f"You do not have the necessary skills for the role '{role}'. "
                             f"Required: {', '.join(required)}. "
                             f"Your skills: {', '.join(volunteer_skills) if volunteer_skills else 'None'}.")
    update_volunteer_role(phone, role)
    logger.info(f"Volunteer {phone} assigned role '{role}'.")
    return f"Your preferred role has been set to '{role}'."

def switch_role(phone: str, role: str) -> str:
    """
    switch_role - Switches the volunteer's current role to a new role.
    Raises VolunteerError if the volunteer is not registered or if role assignment fails.
    """
    record = get_volunteer_record(phone)
    if not record:
        raise VolunteerError("You are not registered.")
    current = record.get("preferred_role")
    message = f"Switching from '{current}' to '{role}'. " if current else "Setting role to "
    confirmation = assign_role(phone, role)
    logger.info(f"Volunteer {phone} switched role from '{current}' to '{role}'.")
    return message + confirmation

def unassign_role(phone: str) -> str:
    """
    unassign_role - Clears the volunteer's preferred role.
    Raises VolunteerError if the volunteer is not registered.
    """
    record = get_volunteer_record(phone)
    if not record:
        raise VolunteerError("You are not registered.")
    update_volunteer_role(phone, None)
    logger.info(f"Volunteer {phone} unassigned their role.")
    return "Your preferred role has been cleared."

# --------------------------------------------------------------------
# Original volunteer_manager.py (merged logic)
# --------------------------------------------------------------------
class VolunteerManager:
    """
    VolunteerManager - Orchestrates volunteer operations, queries, roles, etc.
    """

    # Operations
    def register_volunteer(self, phone: str, name: str, skills: List[str],
                           available: bool = True, current_role: Optional[str] = None) -> str:
        return register_volunteer(phone, name, skills, available, current_role)

    def delete_volunteer(self, phone: str) -> str:
        return delete_volunteer(phone)

    def check_in(self, phone: str) -> str:
        return check_in(phone)

    # Queries
    def volunteer_status(self) -> str:
        return volunteer_status()

    def find_available_volunteer(self, skill: str) -> Optional[str]:
        return find_available_volunteer(skill)

    def get_all_skills(self) -> List[str]:
        return get_all_skills()

    def list_all_volunteers(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all volunteers in the database as a dict: {phone: volunteer_data}.
        """
        return get_all_volunteers()

    def list_all_volunteers_list(self) -> List[Dict[str, Any]]:
        """
        Retrieve all volunteers as a list of dictionaries for CLI usage.
        """
        volunteers_dict = self.list_all_volunteers()
        result = []
        for phone, data in volunteers_dict.items():
            row = {
                "phone": phone,
                "name": data.get("name"),
                "skills": data.get("skills", []),
                "available": data.get("available"),
                "current_role": data.get("current_role"),
            }
            result.append(row)
        return result

    # Role management
    def list_roles(self) -> List[str]:
        return list_roles()

    def assign_role(self, phone: str, role: str) -> str:
        return assign_role(phone, role)

    def switch_role(self, phone: str, role: str) -> str:
        return switch_role(phone, role)

    def unassign_role(self, phone: str) -> str:
        return unassign_role(phone)

    # Auto-assignment logic
    def assign_volunteer(self, skill: str, role: str) -> Optional[str]:
        """
        assign_volunteer - Finds the first volunteer with a given skill who is available
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

    def list_deleted_volunteers(self) -> List[Dict[str, Any]]:
        """
        list_deleted_volunteers - Retrieves all deleted volunteer records from DeletedVolunteers table.
        """
        from db.repository import execute_sql
        query = "SELECT * FROM DeletedVolunteers ORDER BY deleted_at DESC"
        return execute_sql(query, fetchall=True)


# Singleton instance for convenience
VOLUNTEER_MANAGER = VolunteerManager()

# End of managers/volunteer_manager.py