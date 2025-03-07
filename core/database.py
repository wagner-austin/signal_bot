"""
core/database.py - SQLite database integration for persistent storage.
Contains functions to store volunteer assignments, event details, and command logs.
"""

import sqlite3
from sqlite3 import Connection
from typing import Dict, Any, Optional

DB_NAME = "bot_data.db"

def get_connection() -> Connection:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """
    Initialize the database, creating tables if they do not exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Volunteers (
        phone TEXT PRIMARY KEY,
        name TEXT,
        skills TEXT,
        available INTEGER,
        current_role TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS CommandLogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT,
        command TEXT,
        args TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def get_all_volunteers() -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all volunteer records from the database.
    
    Returns:
        Dict[str, Dict[str, Any]]: A dictionary of volunteer records keyed by phone number.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Volunteers")
    rows = cursor.fetchall()
    conn.close()
    volunteers = {}
    for row in rows:
        volunteers[row["phone"]] = {
            "name": row["name"],
            "skills": row["skills"].split(",") if row["skills"] else [],
            "available": bool(row["available"]),
            "current_role": row["current_role"]
        }
    return volunteers

def get_volunteer_record(phone: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single volunteer record by phone number.
    
    Args:
        phone (str): The volunteer's phone number.
    
    Returns:
        Optional[Dict[str, Any]]: The volunteer record or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Volunteers WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "name": row["name"],
            "skills": row["skills"].split(",") if row["skills"] else [],
            "available": bool(row["available"]),
            "current_role": row["current_role"]
        }
    return None

def add_volunteer_record(phone: str, display_name: str, skills: list, available: bool, current_role: Optional[str]) -> None:
    """
    Add a new volunteer record to the database.
    
    Args:
        phone (str): The volunteer's phone number.
        display_name (str): The volunteer's display name.
        skills (list): List of skills.
        available (bool): Availability status.
        current_role (Optional[str]): Current assigned role.
    """
    skills_str = ",".join(skills)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO Volunteers (phone, name, skills, available, current_role) VALUES (?, ?, ?, ?, ?)",
                   (phone, display_name, skills_str, int(available), current_role))
    conn.commit()
    conn.close()

def update_volunteer_record(phone: str, display_name: str, skills: list, available: bool, current_role: Optional[str]) -> None:
    """
    Update an existing volunteer record in the database.
    
    Args:
        phone (str): The volunteer's phone number.
        display_name (str): The volunteer's display name.
        skills (list): List of skills.
        available (bool): Availability status.
        current_role (Optional[str]): Current assigned role.
    """
    skills_str = ",".join(skills)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE Volunteers 
    SET name = ?, skills = ?, available = ?, current_role = ?
    WHERE phone = ?
    """, (display_name, skills_str, int(available), current_role, phone))
    conn.commit()
    conn.close()

def log_command(sender: str, command: str, args: str) -> None:
    """
    Log a command execution to the database.
    
    Args:
        sender (str): The sender's identifier.
        command (str): The command executed.
        args (str): The arguments passed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO CommandLogs (sender, command, args)
    VALUES (?, ?, ?)
    """, (sender, command, args))
    conn.commit()
    conn.close()

# End of core/database.py