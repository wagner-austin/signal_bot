"""
core/event_manager.py - Event Manager for handling event CRUD operations and speaker assignments using repository pattern.
Provides functions for creating, updating, listing, retrieving, and deleting events, as well as assigning,
listing, and removing speakers from events.
"""

from typing import List, Dict, Any, Optional
from core.database.repository import EventRepository, EventSpeakerRepository

def create_event(title: str, date: str, time: str, location: str, description: str) -> int:
    repo = EventRepository()
    data = {
        "title": title,
        "date": date,
        "time": time,
        "location": location,
        "description": description
    }
    return repo.create(data)

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

# End of core/event_manager.py