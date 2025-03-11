#!/usr/bin/env python
"""
plugins/commands/event.py --- Event command plugins for creating and managing events.
Handles invalid integer parsing by returning custom error messages to match negative tests.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from parsers.plugin_arg_parser import (
    PluginArgError,
    PlanEventModel,
    EditEventModel,
    RemoveEventByIdModel,
    RemoveEventByTitleModel,
    validate_model
)
from pydantic import ValidationError
from parsers.argument_parser import parse_plugin_arguments
from core.event_manager import (
    list_events, create_event, update_event, delete_event, get_event
)

logger = logging.getLogger(__name__)

@plugin('event', canonical='event')
def event_command(args: str, sender: str, state_machine: BotStateMachine,
                  msg_timestamp: Optional[int] = None) -> str:
    """
    event - List all upcoming events. No arguments required.
    """
    try:
        events = list_events()
        if not events:
            return "No upcoming events found."
        response = "Upcoming Events:\n"
        for event in events:
            response += (
                f"ID {event.get('event_id')}: {event.get('title')} on {event.get('date')} "
                f"at {event.get('time')} - {event.get('location')}\n"
            )
        return response.strip()
    except PluginArgError as e:
        return str(e)

@plugin('plan event', canonical='plan event')
def plan_event_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    plan event - Create a new event using comma-separated key:value pairs.
    If args are empty, returns interactive instructions.
    If args are 'skip'/'cancel', cancels creation.
    """
    try:
        lowered = args.strip().lower()
        if not lowered:
            raise PluginArgError(
                "Plan Event:\n\n"
                "Please reply with event details in the format:\n"
                "Title: <title>, Date: <date>, Time: <time>, Location: <loc>, Description: <desc>\n"
                "Or 'skip' to cancel."
            )

        if lowered in {"skip", "cancel"}:
            return "Event creation cancelled."

        parts = {}
        for chunk in args.split(","):
            chunk = chunk.strip()
            if ":" not in chunk:
                raise PluginArgError("Missing one or more required fields. Event creation cancelled.")
            k, v = chunk.split(":", 1)
            parts[k.strip().lower()] = v.strip()

        try:
            data = {
                "title": parts["title"],
                "date": parts["date"],
                "time": parts["time"],
                "location": parts["location"],
                "description": parts["description"],
            }
        except KeyError:
            return "Missing one or more required fields. Event creation cancelled."

        validated = validate_model(data, PlanEventModel, "plan event: Title, Date, Time, Location, Description required")
        event_id = create_event(
            validated.title,
            validated.date,
            validated.time,
            validated.location,
            validated.description
        )
        return f"Event '{validated.title}' created successfully with ID {event_id}."
    except PluginArgError as e:
        return str(e)
    except Exception as e:
        logger.exception("Error parsing event details in plan_event_command.")
        return "An internal error occurred while creating the event. Please try again later."

@plugin('edit event', canonical='edit event')
def edit_event_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    edit event - Update an existing event, must include "EventID: <id>" in comma-separated kv pairs.
    """
    try:
        if not args.strip():
            raise PluginArgError("Usage: @bot edit event EventID: <id>, <key>:<value>, ...")

        parts = {}
        for chunk in args.split(","):
            chunk = chunk.strip()
            if ":" not in chunk:
                raise PluginArgError("Invalid format. Use key:value pairs separated by commas.")
            k, v = chunk.split(":", 1)
            parts[k.strip().lower()] = v.strip()

        if "eventid" not in parts:
            raise PluginArgError("EventID is required for updating an event.")

        data = {
            "event_id": parts["eventid"],
            "title": parts.get("title"),
            "date": parts.get("date"),
            "time": parts.get("time"),
            "location": parts.get("location"),
            "description": parts.get("description"),
        }

        try:
            validated = validate_model(data, EditEventModel, "edit event: provide valid EventID and fields")
        except PluginArgError:
            return "Invalid EventID provided."

        existing_event = get_event(validated.event_id)
        if not existing_event:
            return f"No event found with ID {validated.event_id} to edit."

        update_fields = {}
        if validated.title is not None:
            update_fields["title"] = validated.title
        if validated.date is not None:
            update_fields["date"] = validated.date
        if validated.time is not None:
            update_fields["time"] = validated.time
        if validated.location is not None:
            update_fields["location"] = validated.location
        if validated.description is not None:
            update_fields["description"] = validated.description

        if not update_fields:
            return "No update fields provided."

        update_event(validated.event_id, **update_fields)
        return f"Event with ID {validated.event_id} updated successfully."
    except PluginArgError as e:
        return str(e)

@plugin('remove event', canonical='remove event')
def remove_event_command(args: str, sender: str, state_machine: BotStateMachine,
                         msg_timestamp: Optional[int] = None) -> str:
    """
    remove event - Delete an existing event.
    Usage: "EventID: <id>" or "Title: <event title>" in comma-separated kv pairs.
    """
    try:
        if not args.strip():
            raise PluginArgError("Usage: @bot remove event EventID: <id> or Title: <event title>")

        parts = {}
        for chunk in args.split(","):
            chunk = chunk.strip()
            if ":" not in chunk:
                raise PluginArgError("Invalid format. Use key:value pairs separated by commas.")
            k, v = chunk.split(":", 1)
            parts[k.strip().lower()] = v.strip()

        if "eventid" in parts:
            data = {"event_id": parts["eventid"]}
            try:
                validated = validate_model(data, RemoveEventByIdModel, "remove event: provide valid EventID")
            except PluginArgError:
                return "Invalid EventID provided."

            existing = get_event(validated.event_id)
            if not existing:
                return f"No event found with ID {validated.event_id}."
            delete_event(validated.event_id)
            return f"Event with ID {validated.event_id} removed successfully."
        elif "title" in parts:
            data = {"title": parts["title"]}
            validated = validate_model(data, RemoveEventByTitleModel, "remove event: provide a title")
            events = list_events()
            found_id = None
            for ev in events:
                if ev.get("title", "").lower() == validated.title.lower():
                    found_id = ev.get("event_id")
                    break
            if not found_id:
                return f"No event found with title '{validated.title}'."
            delete_event(found_id)
            return f"Event with ID {found_id} removed successfully."
        else:
            raise PluginArgError("Please provide either EventID or Title to remove an event.")
    except PluginArgError as e:
        return str(e)

# End of plugins/commands/event.py