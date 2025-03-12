#!/usr/bin/env python
"""
managers/volunteer_manager.py - Aggregated volunteer management.
Provides a unified interface for volunteer operations, queries, role management, and volunteer assignment.
Now includes a method to list deleted volunteers, removing direct DB calls from the CLI.
"""

from typing import Optional
from managers.volunteer.volunteer_operations import sign_up, delete_volunteer, check_in
from managers.volunteer.volunteer_queries import volunteer_status, find_available_volunteer, get_all_skills
from managers.volunteer.volunteer_roles import list_roles, assign_role, switch_role, unassign_role
from core.database.volunteers import get_all_volunteers, get_volunteer_record, update_volunteer_record
from managers.volunteer.volunteer_common import normalize_name
from core.transaction import atomic_transaction

class VolunteerManager:
    # Operations
    def sign_up(self, phone: str, name: str, skills: list, available: bool = True, current_role: Optional[str] = None) -> str:
        return sign_up(phone, name, skills, available, current_role)
    
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
    
    def list_volunteers(self) -> dict:
        """
        list_volunteers - Retrieve all volunteer records.
        
        Returns:
            dict: A dictionary mapping phone numbers to volunteer data.
        """
        return get_all_volunteers()
    
    # Role management
    def list_roles(self) -> list:
        return list_roles()
    
    def assign_role(self, phone: str, role: str) -> str:
        return assign_role(phone, role)
    
    def switch_role(self, phone: str, role: str) -> str:
        return switch_role(phone, role)
    
    def unassign_role(self, phone: str) -> str:
        return unassign_role(phone)
    
    # Assignment: automatically assign a volunteer based on required skill.
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