#!/usr/bin/env python
"""
File: db/repository.py
----------------------
Unified repository code with helpers, plus specific repositories for domain tables.
Now includes EventRepository, EventSpeakerRepository, TaskRepository, UserStatesRepository, and StatsRepository.
"""

import sqlite3
import logging
from typing import Optional, Dict, Any, List
from db.connection import get_connection  # to open DB

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# execute_sql Helper
# ---------------------------------------------------------------------
def execute_sql(query: str, params: tuple = (), commit: bool = False,
                fetchone: bool = False, fetchall: bool = False):
    """
    execute_sql - Execute a SQL query with optional commit/fetch.

    Args:
        query (str): The SQL to execute.
        params (tuple): Parameters for placeholders.
        commit (bool): Whether to commit after execute.
        fetchone (bool): Return a single row.
        fetchall (bool): Return all rows.

    Returns:
        The fetched row(s) if fetch flags are set, else None.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            result = None
        if commit:
            conn.commit()
        return result
    except sqlite3.Error as e:
        logger.error(f"SQL error in execute_sql: {e} | Query: {query}")
        raise
    finally:
        if conn:
            conn.close()

def log_command(sender: str, command: str, args: str) -> None:
    """
    log_command - Insert a row into the CommandLogs table.
    """
    data = {
        "sender": sender,
        "command": command,
        "args": args
    }
    repo = CommandLogRepository()
    repo.create(data)

# ---------------------------------------------------------------------
# Base Repository
# ---------------------------------------------------------------------
class BaseRepository:
    def __init__(self, table_name: str, primary_key: str = "id",
                 connection_provider=get_connection, external_connection: bool = False):
        self.table_name = table_name
        self.primary_key = primary_key
        self.connection_provider = connection_provider
        self.external_connection = external_connection

    def _maybe_close(self, conn):
        if not self.external_connection:
            conn.close()

    def create(self, data: dict, replace: bool = False) -> int:
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
        query = f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?"
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, (id_value,))
        row = cursor.fetchone()
        self._maybe_close(conn)
        return row

    def update(self, id_value, data: dict) -> None:
        fields = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {self.table_name} SET {fields} WHERE {self.primary_key} = ?"
        params = tuple(data.values()) + (id_value,)
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        self._maybe_close(conn)

    def delete(self, id_value) -> None:
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, (id_value,))
        conn.commit()
        self._maybe_close(conn)

    def list_all(self, filters: dict = None, order_by: str = None) -> list:
        query = f"SELECT * FROM {self.table_name}"
        params = ()
        if filters:
            conditions = " AND ".join([f"{k} = ?" for k in filters.keys()])
            query += f" WHERE {conditions}"
            params = tuple(filters.values())
        if order_by:
            query += f" ORDER BY {order_by}"
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        self._maybe_close(conn)
        return rows or []

    def delete_by_conditions(self, conditions: dict) -> None:
        cond_str = " AND ".join([f"{key} = ?" for key in conditions.keys()])
        query = f"DELETE FROM {self.table_name} WHERE {cond_str}"
        params = tuple(conditions.values())
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        self._maybe_close(conn)

# ---------------------------------------------------------------------
# Existing Specific Repositories
# ---------------------------------------------------------------------
class DonationRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("Donations", primary_key="id",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class ResourceRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("Resources", primary_key="id",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

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

class CommandLogRepository(BaseRepository):
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("CommandLogs", primary_key="id",
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

    def list_tasks_detailed(self) -> list:
        """
        list_tasks_detailed - Returns tasks joined with Volunteers to get created_by_name
        and assigned_to_name. Replaces the direct JOIN in managers/task_manager.
        """
        query = """
        SELECT t.task_id, t.description, t.status, t.created_at,
               t.created_by,
               v1.name as created_by_name,
               t.assigned_to,
               v2.name as assigned_to_name
        FROM Tasks t
        LEFT JOIN Volunteers v1 ON t.created_by = v1.phone
        LEFT JOIN Volunteers v2 ON t.assigned_to = v2.phone
        ORDER BY t.created_at DESC
        """
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        self._maybe_close(conn)
        return rows

# ---------------------------------------------------------------------
# NEW Repositories
# ---------------------------------------------------------------------

class UserStatesRepository(BaseRepository):
    """
    UserStatesRepository - Manages read/write of the UserStates table, keyed by phone.
    The 'flow_state' column stores the JSON state.
    """
    def __init__(self, connection_provider=get_connection, external_connection=False):
        super().__init__("UserStates", primary_key="phone",
                         connection_provider=connection_provider,
                         external_connection=external_connection)

class StatsRepository:
    """
    StatsRepository - Provides methods for gathering table stats and schema version,
    instead of direct execute_sql usage in db/stats.py.
    """
    def __init__(self, connection_provider=get_connection):
        self.connection_provider = connection_provider

    def get_table_names(self) -> List[str]:
        """
        Return a list of table names excluding system tables to match
        the logic used in get_database_stats. 
        """
        exclude = {"sqlite_sequence", "SchemaVersion", "CommandLogs"}
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [row["name"] for row in cursor.fetchall()]
        conn.close()
        return [t for t in all_tables if t not in exclude]

    def get_row_count(self, table_name: str) -> int:
        """
        Return row count for the given table or raise an exception on error.
        """
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
        row = cursor.fetchone()
        conn.close()
        return row["count"] if row else 0

    def get_schema_version(self) -> Optional[int]:
        """
        Return the current schema version from SchemaVersion, or None if missing.
        """
        conn = self.connection_provider()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SchemaVersion'")
        exists = cursor.fetchone()
        if not exists:
            conn.close()
            return None
        cursor.execute("SELECT version FROM SchemaVersion")
        row = cursor.fetchone()
        conn.close()
        return row["version"] if row else None

# End of db/repository.py