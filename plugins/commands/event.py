#!/usr/bin/env python
"""
plugins/commands/event.py - Event command plugins.
Refactored to use core/event_manager for event CRUD operations.
Provides commands for listing events, creating (plan), updating (edit), deleting (remove), 
and managing speakers.
Usage examples:
  "@bot event"                           - List upcoming events.
  "@bot plan event Title: <title>, Date: <date>, Time: <time>, Location: <location>, Description: <description>"
                                         - Create a new event.
  "@bot edit event EventID: <id>, <key>:<value>, [<key>:<value>, ...]"
                                         - Update an existing event.
  "@bot remove event EventID: <id>"
                                         - Delete an event.
  "@bot speakers" or "@bot speakers <event title>"
                                         - List speakers for an event.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine

@plugin('event', canonical='event')
def event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int]=None) -> str:
    """
    event - Lists all upcoming events.
    
    Usage: "@bot event"
    """
    from core.event_manager import list_events
    events = list_events()
    if not events:
        return "No upcoming events found."
    response = "Upcoming Events:\n"
    for event in events:
        response += f"ID {event.get('event_id')}: {event.get('title')} on {event.get('date')} at {event.get('time')} - {event.get('location')}\n"
    return response.strip()

@plugin('plan event', canonical='plan event')
def plan_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int]=None) -> str:
    """
    plan event - Creates a new event interactively or immediately.
    
    Usage:
      "@bot plan event" 
         - Returns instructions for event creation.
      "@bot plan event Title: <title>, Date: <date>, Time: <time>, Location: <location>, Description: <description>" 
         - Creates the event immediately.
      If the reply is "skip" or "cancel", the creation is aborted.
    """
    if not args.strip():
        return ("Plan Event:\n\n"
                "Please reply with event details in the following format:\n"
                "Title: <title>, Date: <date>, Time: <time>, Location: <location>, Description: <description>\n"
                "Or reply with 'skip' to cancel event creation.")
    if args.strip().lower() in {"skip", "cancel"}:
        return "Event creation cancelled."
    details = {}
    try:
        parts = [part.strip() for part in args.split(",")]
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                details[key.strip().lower()] = value.strip()
        required = ["title", "date", "time", "location", "description"]
        if not all(field in details for field in required):
            return "Missing one or more required fields. Required fields: Title, Date, Time, Location, Description."
        from core.event_manager import create_event
        event_id = create_event(details["title"], details["date"], details["time"], details["location"], details["description"])
        return f"Event '{details['title']}' created successfully with ID {event_id}."
    except Exception as e:
        return f"Error parsing event details: {str(e)}"

@plugin('edit event', canonical='edit event')
def edit_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int]=None) -> str:
    """
    edit event - Updates an existing event.
    
    Usage: "@bot edit event EventID: <id>, <key>:<value>, [<key>:<value>, ...]"
    Only provided fields will be updated.
    """
    if not args.strip():
        return "Usage: @bot edit event EventID: <id>, <key>:<value>, [<key>:<value>, ...]"
    details = {}
    try:
        parts = [part.strip() for part in args.split(",")]
        event_id = None
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key == "eventid":
                    try:
                        event_id = int(value)
                    except ValueError:
                        return "Invalid EventID provided."
                else:
                    details[key] = value
        if event_id is None:
            return "EventID is required for updating an event."
        if not details:
            return "No update fields provided."
        from core.event_manager import update_event
        update_event(event_id, **details)
        return f"Event with ID {event_id} updated successfully."
    except Exception as e:
        return f"Error updating event: {str(e)}"

@plugin('remove event', canonical='remove event')
def remove_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int]=None) -> str:
    """
    remove event - Deletes an existing event.
    
    Usage: "@bot remove event EventID: <id>" or "@bot remove event Title: <event title>"
    """
    if not args.strip():
        return "Usage: @bot remove event EventID: <id> or Title: <event title>"
    try:
        details = {}
        parts = [part.strip() for part in args.split(",")]
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                details[key.strip().lower()] = value.strip()
        event_id = None
        if "eventid" in details:
            try:
                event_id = int(details["eventid"])
            except ValueError:
                return "Invalid EventID provided."
        elif "title" in details:
            from core.event_manager import list_events
            events = list_events()
            for event in events:
                if event.get("title", "").lower() == details["title"].lower():
                    event_id = event.get("event_id")
                    break
            if event_id is None:
                return f"No event found with title '{details['title']}'."
        else:
            return "Please provide either EventID or Title to remove an event."
        from core.event_manager import delete_event
        delete_event(event_id)
        return f"Event with ID {event_id} removed successfully."
    except Exception as e:
        return f"Error removing event: {str(e)}"

@plugin('speakers', canonical='speakers')
def speakers_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int]=None) -> str:
    """
    speakers - Lists speakers for an event.
    
    Usage:
      "@bot speakers" to list speakers for the latest event, or 
      "@bot speakers <event title>" to list speakers for a specific event.
    """
    from core.event_manager import list_events, list_speakers
    event_found = None
    if args.strip():
        events = list_events()
        for event in events:
            if event.get("title", "").lower() == args.strip().lower():
                event_found = event
                break
        if event_found is None:
            return f"No event found with title '{args.strip()}'."
    else:
        events = list_events()
        if not events:
            return "No upcoming events found."
        event_found = events[0]
    speakers = list_speakers(event_found.get("event_id"))
    if not speakers:
        return f"No speakers assigned for event '{event_found.get('title')}'."
    response = f"Speakers for event '{event_found.get('title')}':\n"
    for sp in speakers:
        response += f"{sp.get('speaker_name')} – {sp.get('speaker_topic')}\n"
    return response.strip()

# End of plugins/commands/event.py
