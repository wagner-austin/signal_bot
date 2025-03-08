#!/usr/bin/env python
"""
plugins/commands/speaker.py - Speaker command plugins.
Provides commands to add or remove a speaker from an event.
Usage:
  "@bot add speaker [Event: <event title>,] Name: <speaker name>, Topic: <speaker topic>"
  "@bot remove speaker [Event: <event title>,] Name: <speaker name>"
If "Event:" is omitted, the latest event is used.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine

@plugin('add speaker', canonical='add speaker')
def add_speaker_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    add speaker - Adds a speaker to an event.
    
    Usage:
      "@bot add speaker Event: <event title>, Name: <speaker name>, Topic: <speaker topic>"
    If "Event:" is omitted, the latest event is used.
    
    Returns a confirmation message on success or an error message on failure.
    """
    from core.event_manager import list_events, assign_speaker
    try:
        parts = {}
        for part in args.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                parts[key.strip().lower()] = value.strip()
        event_id = None
        if "event" in parts:
            event_title = parts["event"]
            events = list_events()
            for event in events:
                if event.get("title", "").lower() == event_title.lower():
                    event_id = event.get("event_id")
                    break
            if event_id is None:
                return f"No event found with title '{event_title}'."
        else:
            events = list_events()
            if not events:
                return "No upcoming events found to assign a speaker."
            event_id = events[0].get("event_id")
        
        if "name" not in parts or "topic" not in parts:
            return "Missing required fields. Please provide both 'Name' and 'Topic'."
        
        speaker_name = parts["name"]
        speaker_topic = parts["topic"]
        assign_speaker(event_id, speaker_name, speaker_topic)
        return f"Speaker '{speaker_name}' with topic '{speaker_topic}' assigned to event ID {event_id} successfully."
    except Exception as e:
        return f"Error processing command: {str(e)}"

@plugin('remove speaker', canonical='remove speaker')
def remove_speaker_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    remove speaker - Removes a speaker from an event.
    
    Usage:
      "@bot remove speaker Event: <event title>, Name: <speaker name>"
    If "Event:" is omitted, the latest event is used.
    
    Returns a confirmation message on success or an error message on failure.
    """
    from core.event_manager import list_events, remove_speaker
    try:
        parts = {}
        for part in args.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                parts[key.strip().lower()] = value.strip()
        event_id = None
        if "event" in parts:
            event_title = parts["event"]
            events = list_events()
            for event in events:
                if event.get("title", "").lower() == event_title.lower():
                    event_id = event.get("event_id")
                    break
            if event_id is None:
                return f"No event found with title '{event_title}'."
        else:
            events = list_events()
            if not events:
                return "No upcoming events found."
            event_id = events[0].get("event_id")
        
        if "name" not in parts:
            return "Missing required field 'Name'. Please provide the speaker's name to remove."
        
        speaker_name = parts["name"]
        remove_speaker(event_id, speaker_name)
        return f"Speaker '{speaker_name}' removed from event ID {event_id} successfully."
    except Exception as e:
        return f"Error processing command: {str(e)}"

# End of plugins/commands/speaker.py