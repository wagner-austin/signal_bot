#!/usr/bin/env python
"""
managers/volunteer_manager.py - Aggregated volunteer management.
Renamed sign_up -> register_volunteer, list_volunteers -> list_all_volunteers.
Now includes list_all_volunteers_list() returning a list of dicts for CLI usage.
"""

from typing import Optional
from managers.volunteer.volunteer_operations import register_volunteer, delete_volunteer, check_in
from managers.volunteer.volunteer_queries import volunteer_status, find_available_volunteer, get_all_skills
from managers.volunteer.volunteer_roles import list_roles, assign_role, switch_role, unassign_role
from core.database.volunteers import get_all_volunteers, get_volunteer_record, update_volunteer_record
from managers.volunteer.volunteer_common import normalize_name
from core.transaction import atomic_transaction

class VolunteerManager:
    # Operations
    def register_volunteer(self, phone: str, name: str, skills: list,
                           available: bool = True, current_role: Optional[str] = None) -> str:
        return register_volunteer(phone, name, skills, available, current_role)
    
    def delete_volunteer(self, phone: str) -> str:
        return delete_volunteer(phone)
    
    def check_in(self, phone: str) -> str:
        return check_in(phone)
    
    # Queries
    def volunteer_status(self) -> str:
        return volunteer_status()
    
    def find_available_volunteer(self, skill: str):
        return find_available_volunteer(skill)
    
    def get_all_skills(self):
        return get_all_skills()
    
    def list_all_volunteers(self) -> dict:
        """
        list_all_volunteers - Retrieve all volunteer records as a dict {phone: data}.
        """
        return get_all_volunteers()

    def list_all_volunteers_list(self) -> list:
        """
        list_all_volunteers_list - Retrieve all volunteer records as a list of dictionaries,
        for direct consumption by CLI + print_results().
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
    def list_roles(self) -> list:
        return list_roles()
    
    def assign_role(self, phone: str, role: str) -> str:
        return assign_role(phone, role)
    
    def switch_role(self, phone: str, role: str) -> str:
        return switch_role(phone, role)
    
    def unassign_role(self, phone: str) -> str:
        return unassign_role(phone)
    
    # Auto-assignment
    def assign_volunteer(self, skill: str, role: str) -> Optional[str]:
        volunteers = get_all_volunteers()
        target_phone = None
        for phone, data in volunteers.items():
            if any(skill.lower() == s.lower() for s in data.get("skills", [])) \
               and data.get("available") and data.get("current_role") is None:
                target_phone = phone
                break
        if target_phone:
            try:
                with atomic_transaction() as conn:
                    record = get_volunteer_record(target_phone, conn=conn)
                    if record:
                        update_volunteer_record(
                            target_phone,
                            record["name"],
                            record.get("skills", []),
                            record["available"],
                            role,
                            conn=conn
                        )
                        return normalize_name(record["name"], target_phone)
            except Exception:
                return None
        return None

    def list_deleted_volunteers(self) -> list:
        """
        list_deleted_volunteers - Retrieves all deleted volunteer records.
        """
        from core.database.helpers import execute_sql
        query = "SELECT * FROM DeletedVolunteers ORDER BY deleted_at DESC"
        return execute_sql(query, fetchall=True)

VOLUNTEER_MANAGER = VolunteerManager()

# End of managers/volunteer_manager.py