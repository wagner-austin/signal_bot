#!/usr/bin/env python
"""
plugins/commands/event.py - Event command plugins for creating and managing events.
Handles planning, editing, and removing events, as well as listing speakers.
Returns informative messages based on command outcomes.
"""

import logging
from typing import Optional, Dict, Any
from plugins.manager import plugin
from core.state import BotStateMachine
from parsers.argument_parser import parse_plugin_arguments
from core.event_manager import (
    list_events, create_event, update_event, delete_event, get_event, list_speakers
)

logger = logging.getLogger(__name__)

@plugin('event', canonical='event')
def event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    event - List all upcoming events.

    Parameters:
        args (str): Unused; no arguments required.
        sender (str): Sender's phone number.
        state_machine (BotStateMachine): The bot's state machine.
        msg_timestamp (Optional[int]): Optional timestamp of the message.

    Returns:
        str: A formatted list of upcoming events or a message if none are found.
    """
    events = list_events()
    if not events:
        return "No upcoming events found."
    response = "Upcoming Events:\n"
    for event in events:
        response += f"ID {event.get('event_id')}: {event.get('title')} on {event.get('date')} at {event.get('time')} - {event.get('location')}\n"
    return response.strip()

@plugin('plan event', canonical='plan event')
def plan_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    plan event - Create a new event either interactively or immediately.

    If args are empty, returns interactive instructions.
    Otherwise, expects comma-separated key:value pairs with required fields.
    """
    if not args.strip():
        return (
            "Plan Event:\n\n"
            "Please reply with event details in the following format:\n"
            "Title: <title>, Date: <date>, Time: <time>, Location: <location>, Description: <description>\n"
            "Or reply with 'skip' to cancel event creation."
        )
    if args.strip().lower() in {"skip", "cancel"}:
        return "Event creation cancelled."
    try:
        details: Dict[str, Any] = parse_plugin_arguments(args, mode='kv')["kv"]
        required = ["title", "date", "time", "location", "description"]
        if not all(field in details for field in required):
            return "Missing one or more required fields. Event creation cancelled."
        event_id: int = create_event(
            details["title"],
            details["date"],
            details["time"],
            details["location"],
            details["description"]
        )
        return f"Event '{details['title']}' created successfully with ID {event_id}."
    except Exception as e:
        logger.exception("Error parsing event details in plan_event_command.")
        return "An internal error occurred while creating the event. Please try again later."

@plugin('edit event', canonical='edit event')
def edit_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    edit event - Update an existing event.
    Expects comma-separated key:value pairs, including "EventID: <id>".
    """
    if not args.strip():
        return "Usage: @bot edit event EventID: <id>, <key>:<value>, [<key>:<value>, ...]"
    try:
        details: Dict[str, Any] = parse_plugin_arguments(args, mode='kv')["kv"]
    except Exception as e:
        return f"Error parsing event details: {str(e)}"

    event_id: Optional[int] = None
    update_fields: Dict[str, Any] = {}
    for key, value in details.items():
        if key == "eventid":
            try:
                event_id = int(value)
            except ValueError:
                return "Invalid EventID provided."
        else:
            update_fields[key] = value

    if event_id is None:
        return "EventID is required for updating an event."
    existing_event = get_event(event_id)
    if not existing_event:
        return f"No event found with ID {event_id} to edit."
    if not update_fields:
        return "No update fields provided."

    update_event(event_id, **update_fields)
    return f"Event with ID {event_id} updated successfully."

@plugin('remove event', canonical='remove event')
def remove_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    remove event - Delete an existing event.
    Accepts comma-separated key:value pairs with either:
      - EventID: <id>
      - Title: <event title>
    """
    if not args.strip():
        return "Usage: @bot remove event EventID: <id> or Title: <event title>"
    try:
        details: Dict[str, Any] = parse_plugin_arguments(args, mode='kv')["kv"]
    except Exception as e:
        return f"Error parsing event details: {str(e)}"

    event_id: Optional[int] = None
    if "eventid" in details:
        try:
            event_id = int(details["eventid"])
        except ValueError:
            return "Invalid EventID provided."
    elif "title" in details:
        events = list_events()
        for ev in events:
            if ev.get("title", "").lower() == details["title"].lower():
                event_id = ev.get("event_id")
                break
        if event_id is None:
            return f"No event found with title '{details['title']}'."
    else:
        return "Please provide either EventID or Title to remove an event."

    if event_id is not None:
        existing = get_event(event_id)
        if not existing:
            return f"No event found with ID {event_id}."
        delete_event(event_id)
        return f"Event with ID {event_id} removed successfully."
    return "No valid event identifier provided."

@plugin('speakers', canonical='speakers')
def speakers_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    speakers - List speakers for an event.
    If args is empty, lists speakers for the latest event.
    If args is an event title, lists speakers for that event.
    """
    event_found: Optional[Dict[str, Any]] = None
    if args.strip():
        events = list_events()
        for ev in events:
            if ev.get("title", "").lower() == args.strip().lower():
                event_found = ev
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