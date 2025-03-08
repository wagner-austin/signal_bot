"""
core/event_manager.py - Event Manager for handling event CRUD operations and speaker assignments.
Provides functions for creating, updating, listing, retrieving, and deleting events, as well as assigning,
listing, and removing speakers from events.
"""

from typing import List, Dict, Any, Optional
from core.database.helpers import execute_sql

def create_event(title: str, date: str, time: str, location: str, description: str) -> int:
    """
    Create a new event and return its event_id.
    
    Args:
        title (str): The title of the event.
        date (str): The date of the event.
        time (str): The time of the event.
        location (str): The location of the event.
        description (str): A description of the event.
        
    Returns:
        int: The event_id of the newly created event.
    """
    query = """
    INSERT INTO Events (title, date, time, location, description)
    VALUES (?, ?, ?, ?, ?)
    """
    execute_sql(query, (title, date, time, location, description), commit=True)
    result = execute_sql("SELECT last_insert_rowid() as event_id", fetchone=True)
    return result["event_id"] if result else -1

def update_event(event_id: int, **kwargs) -> None:
    """
    Update an existing event with the given fields.
    
    Acceptable keys: title, date, time, location, description.
    
    Args:
        event_id (int): The unique identifier for the event.
        **kwargs: Field names and values to update.
    """
    fields = []
    values = []
    for key in ['title', 'date', 'time', 'location', 'description']:
        if key in kwargs:
            fields.append(f"{key} = ?")
            values.append(kwargs[key])
    if not fields:
        return
    values.append(event_id)
    query = f"UPDATE Events SET {', '.join(fields)} WHERE event_id = ?"
    execute_sql(query, tuple(values), commit=True)

def list_events() -> List[Dict[str, Any]]:
    """
    Retrieve and return a list of all events.
    
    Returns:
        List[dict]: A list of events as dictionaries.
    """
    query = "SELECT * FROM Events ORDER BY created_at DESC"
    rows = execute_sql(query, fetchall=True)
    return [dict(row) for row in rows] if rows else []

def get_event(event_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single event by event_id.
    
    Args:
        event_id (int): The unique identifier for the event.
        
    Returns:
        dict or None: The event details as a dictionary, or None if not found.
    """
    query = "SELECT * FROM Events WHERE event_id = ?"
    row = execute_sql(query, (event_id,), fetchone=True)
    return dict(row) if row else None

def delete_event(event_id: int) -> None:
    """
    Delete an event by event_id.
    
    Args:
        event_id (int): The unique identifier for the event.
    """
    query = "DELETE FROM Events WHERE event_id = ?"
    execute_sql(query, (event_id,), commit=True)

def assign_speaker(event_id: int, speaker_name: str, speaker_topic: str) -> None:
    """
    Assign a speaker to an event.
    
    Args:
        event_id (int): The unique identifier for the event.
        speaker_name (str): The name of the speaker.
        speaker_topic (str): The topic the speaker will cover.
    """
    query = """
    INSERT INTO EventSpeakers (event_id, speaker_name, speaker_topic)
    VALUES (?, ?, ?)
    """
    execute_sql(query, (event_id, speaker_name, speaker_topic), commit=True)

def list_speakers(event_id: int) -> List[Dict[str, Any]]:
    """
    List all speakers assigned to a given event.
    
    Args:
        event_id (int): The unique identifier for the event.
        
    Returns:
        List[dict]: A list of speakers with their details.
    """
    query = "SELECT * FROM EventSpeakers WHERE event_id = ? ORDER BY created_at ASC"
    rows = execute_sql(query, (event_id,), fetchall=True)
    return [dict(row) for row in rows] if rows else []

def remove_speaker(event_id: int, speaker_name: str) -> None:
    """
    Remove a speaker from an event.
    
    Args:
        event_id (int): The unique identifier for the event.
        speaker_name (str): The name of the speaker to remove.
    """
    query = "DELETE FROM EventSpeakers WHERE event_id = ? AND speaker_name = ?"
    execute_sql(query, (event_id, speaker_name), commit=True)

# End of core/event_manager.py