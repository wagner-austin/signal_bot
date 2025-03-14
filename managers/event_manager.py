#!/usr/bin/env python
"""
event_manager.py
----------------
Event Manager for handling event CRUD operations and speaker assignments.
Ensures Row objects are converted to dictionaries so tests can do .get().
"""

from typing import List, Dict, Any, Optional
import logging
from db.repository import EventRepository, EventSpeakerRepository

logger = logging.getLogger(__name__)

def create_event(title: str, date: str, time: str, location: str, description: str) -> int:
    repo = EventRepository()
    data = {
        "title": title,
        "date": date,
        "time": time,
        "location": location,
        "description": description
    }
    new_id = repo.create(data)
    logger.info(f"Event created with ID {new_id}, Title: '{title}'")
    return new_id

def update_event(event_id: int, **kwargs) -> None:
    repo = EventRepository()
    repo.update(event_id, kwargs)

def list_all_events() -> List[Dict[str, Any]]:
    """
    list_all_events - Return all events in descending order by created_at
                      as a list of dictionaries.
    """
    repo = EventRepository()
    rows = repo.list_all(order_by="created_at DESC")
    events = []
    for row in rows:
        events.append({
            "event_id": row["event_id"],
            "title": row["title"],
            "date": row["date"],
            "time": row["time"],
            "location": row["location"],
            "description": row["description"],
            "created_at": row["created_at"]
        })
    return events

def get_event(event_id: int) -> Optional[Dict[str, Any]]:
    """
    get_event - Retrieve a single event as a dictionary, or None if not found.
    """
    repo = EventRepository()
    row = repo.get_by_id(event_id)
    if row:
        return {
            "event_id": row["event_id"],
            "title": row["title"],
            "date": row["date"],
            "time": row["time"],
            "location": row["location"],
            "description": row["description"],
            "created_at": row["created_at"]
        }
    return None

def delete_event(event_id: int) -> None:
    repo = EventRepository()
    repo.delete(event_id)

def assign_speaker(event_id: int, speaker_name: str, speaker_topic: str) -> None:
    repo = EventSpeakerRepository()
    data = {
        "event_id": event_id,
        "speaker_name": speaker_name,
        "speaker_topic": speaker_topic
    }
    repo.create(data)

def list_speakers(event_id: int) -> List[Dict[str, Any]]:
    """
    list_speakers - Return all speakers for a given event as a list of dictionaries.
    """
    repo = EventSpeakerRepository()
    rows = repo.list_all(filters={"event_id": event_id}, order_by="created_at ASC")
    speakers = []
    for row in rows:
        speakers.append({
            "id": row["id"],
            "event_id": row["event_id"],
            "speaker_name": row["speaker_name"],
            "speaker_topic": row["speaker_topic"],
            "created_at": row["created_at"]
        })
    return speakers

def remove_speaker(event_id: int, speaker_name: str) -> None:
    repo = EventSpeakerRepository()
    repo.delete_by_conditions({"event_id": event_id, "speaker_name": speaker_name})

def list_all_event_speakers() -> List[Dict[str, Any]]:
    """
    list_all_event_speakers - Return all event speakers as a list of dictionaries.
    """
    repo = EventSpeakerRepository()
    rows = repo.list_all(order_by="created_at DESC")
    speakers = []
    for row in rows:
        speakers.append({
            "id": row["id"],
            "event_id": row["event_id"],
            "speaker_name": row["speaker_name"],
            "speaker_topic": row["speaker_topic"],
            "created_at": row["created_at"]
        })
    return speakers

# End of event_manager.py