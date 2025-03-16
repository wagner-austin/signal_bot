#!/usr/bin/env python
"""
managers/volunteer_manager.py - Core volunteer management for registration, deletion, check_in, status, etc.
All skill and role code has been removed, preserving only name, phone, and availability.
"""

import logging
from typing import Optional, List, Dict, Any

from core.exceptions import VolunteerError
from core.validators import validate_phone_number
from managers.utils import normalize_name
from plugins.messages import (
    NEW_VOLUNTEER_REGISTERED,
    VOLUNTEER_UPDATED,
    VOLUNTEER_DELETED,
    VOLUNTEER_CHECKED_IN,
    VOLUNTEER_NOT_FOUND,
    VOLUNTEER_NOT_REGISTERED,
    INVALID_AVAILABILITY_FORMAT
)
from core.api.concurrency_api import per_phone_lock_api, atomic_transaction_api
from core.api import db_api

logger = logging.getLogger(__name__)

class VolunteerManager:
    """
    VolunteerManager - Handles volunteer registration, deletion, check_in, and status.
    Skill and role references have been removed.
    """

    def register_volunteer(self,
                           phone: str,
                           name: str,
                           available: bool = True) -> str:
        """
        Register or update a volunteer record, storing just phone, name, and availability.
        """
        validate_phone_number(phone)
        if not isinstance(available, bool):
            try:
                available = bool(int(available))
            except (ValueError, TypeError):
                raise VolunteerError(INVALID_AVAILABILITY_FORMAT)

        with per_phone_lock_api(phone):
            with atomic_transaction_api(exclusive=True) as conn:
                # Remove from DeletedVolunteers if present
                self._remove_deleted_volunteer_record(conn, phone)

                existing = self._get_volunteer_record(conn, phone)
                if existing:
                    # Update existing
                    self._update_volunteer_record(conn, phone, name, available)
                    logger.info(
                        f"Volunteer {phone} updated: name='{name}', available={available}"
                    )
                    return VOLUNTEER_UPDATED.format(name=normalize_name(name, phone))
                else:
                    # Create new
                    self._add_volunteer_record(conn, phone, name, available)
                    logger.info(
                        f"New volunteer {phone} registered: name='{name}', available={available}"
                    )
                    return NEW_VOLUNTEER_REGISTERED.format(name=normalize_name(name, phone))

    def delete_volunteer(self, phone: str) -> str:
        """
        Delete a volunteer by phone, archiving them in DeletedVolunteers.
        """
        with per_phone_lock_api(phone):
            existing = self.get_volunteer_record(phone)
            if not existing:
                raise VolunteerError(VOLUNTEER_NOT_REGISTERED)
            with atomic_transaction_api() as conn:
                self._add_deleted_volunteer_record(
                    conn,
                    phone,
                    existing["name"],
                    existing["available"]
                )
                self._delete_volunteer_record(conn, phone)

            logger.info(f"Volunteer {phone} record deleted from the system.")
            return VOLUNTEER_DELETED

    def check_in(self, phone: str) -> str:
        """
        Mark an existing volunteer as available (true).
        """
        with per_phone_lock_api(phone):
            existing = self.get_volunteer_record(phone)
            if existing:
                with atomic_transaction_api() as conn:
                    self._update_volunteer_record(conn, phone, existing["name"], True)
                logger.info(f"Volunteer {phone} checked in (now available).")
                return VOLUNTEER_CHECKED_IN.format(name=normalize_name(existing['name'], phone))
            raise VolunteerError(VOLUNTEER_NOT_FOUND)

    def volunteer_status(self) -> str:
        """
        Return a string summarizing all volunteers' availability (excluding skills/roles).
        """
        all_vols = self._get_all_volunteers()
        lines = []
        for phone, data in all_vols.items():
            name = normalize_name(data.get("name", phone), phone)
            availability = "Available" if data.get("available") else "Not Available"
            lines.append(f"{name}: {availability}")
        return "\n".join(lines)

    def list_all_volunteers(self) -> Dict[str, Dict[str, Any]]:
        """
        Return a dictionary phone -> volunteer data (no skill/role).
        """
        return self._get_all_volunteers()

    def list_all_volunteers_list(self) -> List[Dict[str, Any]]:
        """
        Return a list of volunteer dictionaries.
        """
        volunteers_dict = self._get_all_volunteers()
        result = []
        for phone, data in volunteers_dict.items():
            row = {
                "phone": phone,
                "name": data.get("name"),
                "available": data.get("available")
            }
            result.append(row)
        return result

    def list_deleted_volunteers(self) -> List[Dict[str, Any]]:
        """
        Return all records from DeletedVolunteers in descending order by deleted_at.
        """
        query = "SELECT * FROM DeletedVolunteers ORDER BY deleted_at DESC"
        rows = db_api.fetch_all(query)
        return rows

    def get_volunteer_record(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        Return a single volunteer record or None if not found.
        """
        return self._get_volunteer_record(None, phone)

    # -----------------------------
    # Internal Helper Methods
    # -----------------------------
    def _get_volunteer_record(self, conn, phone: str) -> Optional[Dict[str, Any]]:
        query = """
            SELECT phone, name, available
            FROM Volunteers
            WHERE phone = ?
        """
        if conn:
            row = conn.execute(query, (phone,)).fetchone()
            if row:
                return {
                    "name": row["name"],
                    "available": bool(row["available"])
                }
            return None
        else:
            row = db_api.fetch_one(query, (phone,))
            if not row:
                return None
            return {
                "name": row["name"],
                "available": bool(row["available"])
            }

    def _delete_volunteer_record(self, conn, phone: str) -> None:
        query = "DELETE FROM Volunteers WHERE phone = ?"
        conn.execute(query, (phone,))

    def _add_volunteer_record(self,
                              conn,
                              phone: str,
                              display_name: str,
                              available: bool):
        query = """
            INSERT OR REPLACE INTO Volunteers
            (phone, name, available)
            VALUES (?, ?, ?)
        """
        conn.execute(query, (phone, display_name, int(available)))

    def _update_volunteer_record(self,
                                 conn,
                                 phone: str,
                                 display_name: str,
                                 available: bool):
        query = """
            UPDATE Volunteers
            SET name = ?,
                available = ?
            WHERE phone = ?
        """
        conn.execute(query, (display_name, int(available), phone))

    def _add_deleted_volunteer_record(self,
                                      conn,
                                      phone: str,
                                      name: str,
                                      available: bool):
        query = """
            INSERT OR REPLACE INTO DeletedVolunteers
            (phone, name, available)
            VALUES (?, ?, ?)
        """
        conn.execute(query, (phone, name, int(available)))

    def _remove_deleted_volunteer_record(self, conn, phone: str):
        query = "DELETE FROM DeletedVolunteers WHERE phone = ?"
        conn.execute(query, (phone,))

    def _get_all_volunteers(self) -> Dict[str, Dict[str, Any]]:
        """
        Return phone -> {record_data} for all volunteers (only name, available).
        """
        query = "SELECT phone, name, available FROM Volunteers"
        rows = db_api.fetch_all(query)
        output = {}
        for r in rows:
            phone = r["phone"]
            output[phone] = {
                "name": r["name"],
                "available": bool(r["available"])
            }
        return output


VOLUNTEER_MANAGER = VolunteerManager()

def register_volunteer(phone, name, available=True):
    return VOLUNTEER_MANAGER.register_volunteer(phone, name, available)

def delete_volunteer(phone):
    return VOLUNTEER_MANAGER.delete_volunteer(phone)

def check_in(phone):
    return VOLUNTEER_MANAGER.check_in(phone)

def volunteer_status():
    return VOLUNTEER_MANAGER.volunteer_status()

# End of managers/volunteer_manager.py