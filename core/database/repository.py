#!/usr/bin/env python
"""
core/database/repository.py --- Data Access Layer repository classes.
Provides a BaseRepository with common CRUD operations and specific repository classes for various tables.
Now includes an 'external_connection' option to avoid closing external DB connections prematurely.
"""

from core.database.connection import get_connection

class BaseRepository:
    def __init__(self, table_name: str, primary_key: str = "id",
                 connection_provider=get_connection,
                 external_connection: bool = False):
        """
        Initialize the base repository.

        Args:
            table_name (str): The database table name.
            primary_key (str): Name of the primary key column.
            connection_provider: Function returning a DB connection.
            external_connection (bool): If True, do not close the connection
                                        after each operation. The caller
                                        controls the connection lifecycle.
        """
        self.table_name = table_name
        self.primary_key = primary_key
        self.connection_provider = connection_provider
        self.external_connection = external_connection

    def _maybe_close(self, conn):
        """
        _maybe_close - Close the connection only if external_connection=False.
        """
        if not self.external_connection:
            conn.close()

    def create(self, data: dict, replace: bool = False) -> int:
        """
        create - Insert a record into the table. If replace=True, use INSERT OR REPLACE.

        Args:
            data (dict): Column -> Value
            replace (bool): Whether to use INSERT OR REPLACE.

        Returns:
            int: The last inserted row id.
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
        self._maybe_close(conn)
        return last_id

    def get_by_id(self, id_value):
        """
        Retrieve a record by its primary key.
        """
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, (id_value,))
        row = cursor.fetchone()
        self._maybe_close(conn)
        return dict(row) if row else None

    def update(self, id_value, data: dict) -> None:
        """
        update - Update a record identified by its primary key.

        Args:
            id_value: The PK value.
            data (dict): Column -> Value to update.
        """
        fields = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {self.table_name} SET {fields} WHERE {self.primary_key} = ?"
        params = tuple(data.values()) + (id_value,)
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        self._maybe_close(conn)

    def delete(self, id_value) -> None:
        """
        delete - Delete a record by its primary key.
        """
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, (id_value,))
        conn.commit()
        self._maybe_close(conn)

    def list_all(self, filters: dict = None, order_by: str = None) -> list:
        """
        list_all - Return records from the table, optionally filtered and ordered.

        Args:
            filters (dict): Column -> Value
            order_by (str): ORDER BY clause.

        Returns:
            list of dict: The records.
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
        self._maybe_close(conn)
        return [dict(row) for row in rows] if rows else []

    def delete_by_conditions(self, conditions: dict) -> None:
        """
        delete_by_conditions - Delete records matching a set of conditions.

        Args:
            conditions (dict): Column -> Value
        """
        cond_str = " AND ".join([f"{key} = ?" for key in conditions.keys()])
        query = f"DELETE FROM {self.table_name} WHERE {cond_str}"
        params = tuple(conditions.values())
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        self._maybe_close(conn)


# Specific repository classes

class VolunteerRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("Volunteers", primary_key="phone",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class DeletedVolunteerRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("DeletedVolunteers", primary_key="phone",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class ResourceRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("Resources", primary_key="id",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class DonationRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("Donations", primary_key="id",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class EventRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("Events", primary_key="event_id",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class EventSpeakerRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("EventSpeakers", primary_key="id",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class TaskRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("Tasks", primary_key="task_id",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class CommandLogRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("CommandLogs", primary_key="id",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

# End of core/database/repository.py