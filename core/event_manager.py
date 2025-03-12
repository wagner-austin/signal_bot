#!/usr/bin/env python
"""
core/event_manager.py --- Event Manager for handling event CRUD operations and speaker assignments.
Provides functions for creating, updating, listing, retrieving, and deleting events, as well as assigning,
listing, and removing speakers from events.
"""

from typing import List, Dict, Any, Optional
import logging
from core.database.repository import EventRepository, EventSpeakerRepository

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

def list_events() -> List[Dict[str, Any]]:
    repo = EventRepository()
    return repo.list_all(order_by="created_at DESC")

def get_event(event_id: int) -> Optional[Dict[str, Any]]:
    repo = EventRepository()
    row = repo.get_by_id(event_id)
    return row if row else None

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
    repo = EventSpeakerRepository()
    return repo.list_all(filters={"event_id": event_id}, order_by="created_at ASC")

def remove_speaker(event_id: int, speaker_name: str) -> None:
    repo = EventSpeakerRepository()
    repo.delete_by_conditions({"event_id": event_id, "speaker_name": speaker_name})

def list_all_event_speakers() -> List[Dict[str, Any]]:
    """
    list_all_event_speakers - List all event speaker records without filtering by event.
    
    Returns:
        List[Dict[str, Any]]: A list of all event speaker records ordered by created_at descending.
    """
    repo = EventSpeakerRepository()
    return repo.list_all(order_by="created_at DESC")

# End of core/event_manager.py