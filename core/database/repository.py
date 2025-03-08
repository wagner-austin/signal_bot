#!/usr/bin/env python
"""
core/database/repository.py - Data Access Layer repository classes.
Provides a BaseRepository with common CRUD operations and specific repository classes for various tables.
Dependency injection for the database connection is supported via a connection_provider.
"""

from core.database.connection import get_connection

class BaseRepository:
    def __init__(self, table_name: str, primary_key: str = "id", connection_provider=get_connection):
        self.table_name = table_name
        self.primary_key = primary_key
        self.connection_provider = connection_provider

    def create(self, data: dict, replace: bool = False) -> int:
        """
        Create a new record in the table.
        If replace is True, use INSERT OR REPLACE.
        Returns the last inserted row id.
        """
        operator = "INSERT OR REPLACE" if replace else "INSERT"
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"{operator} INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        params = tuple(data.values())
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def get_by_id(self, id_value) -> dict:
        """
        Retrieve a record by its primary key.
        """
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, (id_value,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update(self, id_value, data: dict) -> None:
        """
        Update a record identified by its primary key.
        """
        fields = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {self.table_name} SET {fields} WHERE {self.primary_key} = ?"
        params = tuple(data.values()) + (id_value,)
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def delete(self, id_value) -> None:
        """
        Delete a record by its primary key.
        """
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, (id_value,))
        conn.commit()
        conn.close()

    def list_all(self, filters: dict = None, order_by: str = None) -> list:
        """
        List all records, optionally filtered and ordered.
        """
        query = f"SELECT * FROM {self.table_name}"
        params = ()
        if filters:
            conditions = " AND ".join([f"{key} = ?" for key in filters.keys()])
            query += " WHERE " + conditions
            params = tuple(filters.values())
        if order_by:
            query += " ORDER BY " + order_by
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows] if rows else []

    def delete_by_conditions(self, conditions: dict) -> None:
        """
        Delete records that match the given conditions.
        """
        cond_str = " AND ".join([f"{key} = ?" for key in conditions.keys()])
        query = f"DELETE FROM {self.table_name} WHERE {cond_str}"
        params = tuple(conditions.values())
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

# Specific repository classes

class VolunteerRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection):
        super().__init__("Volunteers", primary_key="phone", connection_provider=connection_provider)

class DeletedVolunteerRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection):
        super().__init__("DeletedVolunteers", primary_key="phone", connection_provider=connection_provider)

class ResourceRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection):
        super().__init__("Resources", primary_key="id", connection_provider=connection_provider)

class DonationRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection):
        super().__init__("Donations", primary_key="id", connection_provider=connection_provider)

class EventRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection):
        super().__init__("Events", primary_key="event_id", connection_provider=connection_provider)

class EventSpeakerRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection):
        super().__init__("EventSpeakers", primary_key="id", connection_provider=connection_provider)

class TaskRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection):
        super().__init__("Tasks", primary_key="task_id", connection_provider=connection_provider)

class CommandLogRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection):
        super().__init__("CommandLogs", primary_key="id", connection_provider=connection_provider)

# End of core/database/repository.py