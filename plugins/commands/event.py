"""
plugins/commands/event.py - Event command plugins.
Provides commands related to events such as event summary, speaker listing, event planning, editing, and removal.
All event data is managed via the database using the event_manager module.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.constants import SKIP_VALUES
from managers.pending_actions import PENDING_ACTIONS

@plugin('event', canonical='event')
def event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    event - Shows a summary of the most recent event from the database.
    
    Usage: 
      "@bot event"
      
    Retrieves the latest event details from the database and returns the title, date,
    time, location, and description.
    """
    from core.event_manager import list_events
    events = list_events()
    if not events:
        return "No upcoming events found."
    latest_event = events[0]
    return (
        f"{latest_event.get('title', 'Next Event')}\n\n"
        f"Date: {latest_event.get('date', 'Unknown Date')}\n"
        f"Time: {latest_event.get('time', 'Unknown Time')}\n"
        f"Location: {latest_event.get('location', 'Unknown Location')}\n\n"
        f"{latest_event.get('description', 'No description')}"
    )

@plugin('speakers', canonical='speakers')
def speakers_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    speakers - Lists speakers assigned to an event.
    
    Usage: 
      "@bot speakers" to list speakers for the most recent event, or 
      "@bot speakers <event title>" to list speakers for a specific event.
      
    Retrieves event data from the database and lists all speakers associated with that event.
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
    speakers = list_speakers(event_found["event_id"])
    if not speakers:
        return f"No speakers assigned for event '{event_found.get('title', 'Event')}'."
    response = f"Speakers for event '{event_found.get('title')}'\n\n"
    for sp in speakers:
        response += f"{sp.get('speaker_name')} – {sp.get('speaker_topic')}\n"
    return response

@plugin('plan event', canonical='plan event')
def plan_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    plan event - Creates a new event using database-backed data.
    
    Usage:
      "@bot plan event" 
         - Sets an interactive pending state and returns instructions to the user.
      "@bot plan event Title: <title>, Date: <date>, Time: <time>, Location: <location>, Description: <description>" 
         - Immediately parses the provided details and creates the event.
      
    Allows cancellation by replying with any skip keyword (e.g., "skip", "cancel").
    """
    from core.event_manager import create_event
    if not args.strip():
        # Set pending event creation state and instruct user.
        PENDING_ACTIONS.set_event_creation(sender)
        return (
            "Plan Event:\n\n"
            "Please reply with event details in the following format:\n"
            "Title: <title>, Date: <date>, Time: <time>, Location: <location>, Description: <description>\n"
            "Or reply with 'skip' to cancel event creation."
        )
    if args.strip().lower() in SKIP_VALUES:
        return "Event creation cancelled."
    try:
        parts = {}
        for part in args.split(","):
            key, value = part.split(":", 1)
            parts[key.strip().lower()] = value.strip()
        required_fields = ["title", "date", "time", "location", "description"]
        if not all(field in parts for field in required_fields):
            return "Missing one or more required fields. Please provide Title, Date, Time, Location, and Description."
        event_id = create_event(parts["title"], parts["date"], parts["time"], parts["location"], parts["description"])
        return f"Event '{parts['title']}' created successfully with ID {event_id}."
    except Exception as e:
        return f"Error parsing event details: {str(e)}"

@plugin('edit event', canonical='edit event')
def edit_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    edit event - Edits an existing event.
    
    Usage:
      "@bot edit event EventID: <id>, [Title: <new title>, Date: <new date>, Time: <new time>, Location: <new location>, Description: <new description>]"
      
    If EventID is not provided, the latest event is used.
    Only provided fields will be updated.
    """
    from core.event_manager import update_event, list_events
    try:
        parts = {}
        for part in args.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                parts[key.strip().lower()] = value.strip()
        event_id = None
        if "eventid" in parts:
            try:
                event_id = int(parts["eventid"])
            except ValueError:
                return "Invalid EventID provided."
        else:
            events = list_events()
            if not events:
                return "No events found to edit."
            event_id = events[0].get("event_id")
        parts.pop("eventid", None)
        if not parts:
            return "No update fields provided."
        update_event(event_id, **parts)
        return f"Event with ID {event_id} updated successfully."
    except Exception as e:
        return f"Error editing event: {str(e)}"

@plugin('remove event', canonical='remove event')
def remove_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    remove event - Removes an existing event.
    
    Usage:
      "@bot remove event EventID: <id>" or
      "@bot remove event Title: <event title>"
      
    If EventID is not provided, the event is looked up by title.
    """
    from core.event_manager import delete_event, list_events
    try:
        parts = {}
        for part in args.split(","):
            if ":" in part:
                key, value = part.split(":", 1)
                parts[key.strip().lower()] = value.strip()
        event_id = None
        if "eventid" in parts:
            try:
                event_id = int(parts["eventid"])
            except ValueError:
                return "Invalid EventID provided."
        elif "title" in parts:
            events = list_events()
            for event in events:
                if event.get("title", "").lower() == parts["title"].lower():
                    event_id = event.get("event_id")
                    break
            if event_id is None:
                return f"No event found with title '{parts['title']}'."
        else:
            return "Please provide either EventID or Title to remove an event."
        delete_event(event_id)
        return f"Event with ID {event_id} removed successfully."
    except Exception as e:
        return f"Error removing event: {str(e)}"

# End of plugins/commands/event.py