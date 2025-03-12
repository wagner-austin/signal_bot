#!/usr/bin/env python
"""
plugins/commands/event.py - Event command plugins.
Leverages managers.event_manager for all event-related CRUD logic,
ensuring a single source of truth shared with CLI code.
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
from managers.event_manager import (
    list_all_events, create_event, update_event, delete_event, get_event
)
from pydantic import ValidationError
from parsers.argument_parser import parse_plugin_arguments

logger = logging.getLogger(__name__)

@plugin('event', canonical='event')
def event_command(args: str, sender: str, state_machine: BotStateMachine,
                  msg_timestamp: Optional[int] = None) -> str:
    """
    event - Lists upcoming events by calling managers.event_manager.list_all_events().
    Also used by CLI subcommands for listing events.
    """
    try:
        events = list_all_events()
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
        logger.warning(f"event_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"event_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in event_command."

@plugin('plan event', canonical='plan event')
def plan_event_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    plan event - Create a new event by calling managers.event_manager.create_event(...).
    Shares the same manager logic as the CLI, ensuring consistent behavior.
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
        logger.warning(f"plan_event_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"plan_event_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in plan_event_command."

@plugin('edit event', canonical='edit event')
def edit_event_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    edit event - Update an existing event by calling managers.event_manager.update_event(...).
    Uses the same manager logic as the CLI subcommand.
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

        validated = validate_model(data, EditEventModel, "edit event: provide valid EventID and fields")
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
        logger.warning(f"edit_event_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"edit_event_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in edit_event_command."

@plugin('remove event', canonical='remove event')
def remove_event_command(args: str, sender: str, state_machine: BotStateMachine,
                         msg_timestamp: Optional[int] = None) -> str:
    """
    remove event - Delete an existing event by calling managers.event_manager.delete_event(...).
    Mirrors the same manager calls used by the CLI.
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
            validated = validate_model(data, RemoveEventByIdModel, "remove event: provide valid EventID")
            existing = get_event(validated.event_id)
            if not existing:
                return f"No event found with ID {validated.event_id}."
            delete_event(validated.event_id)
            return f"Event with ID {validated.event_id} removed successfully."
        elif "title" in parts:
            data = {"title": parts["title"]}
            validated = validate_model(data, RemoveEventByTitleModel, "remove event: provide a title")
            events = list_all_events()
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
        logger.warning(f"remove_event_command PluginArgError: {e}")
        return str(e)
    except Exception as e:
        logger.error(f"remove_event_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in remove_event_command."

# End of plugins/commands/event.py