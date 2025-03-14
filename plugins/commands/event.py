"""
plugins/commands/event.py - Event command plugins.
Subcommands for each command:
  event           : default - List upcoming events.
  plan event      : default - Create a new event.
  edit event      : default - Update an existing event.
  remove event    : default - Delete an existing event.
  event speakers  : default - List all event speakers.
USAGE: See respective USAGE constants in core/plugin_usage.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from parsers.plugin_arg_parser import PluginArgError, validate_model
from managers.event_manager import (
    list_all_events,
    create_event,
    update_event,
    delete_event,
    get_event,
    list_all_event_speakers
)
from core.plugin_usage import (
    USAGE_PLAN_EVENT, USAGE_PLAN_EVENT_PARTIAL,
    USAGE_EDIT_EVENT, USAGE_REMOVE_EVENT
)
from plugins.commands.formatters import format_event, format_event_speaker

logger = logging.getLogger(__name__)

@plugin('event', canonical='event')
def event_command(args: str, sender: str, state_machine: BotStateMachine,
                  msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/event.py - Event listing command.
    Subcommands:
      default : List upcoming events.
    USAGE: @bot event
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: @bot event"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        events = list_all_events()
        if not events:
            return "No upcoming events found."
        return "\n".join(format_event(e) for e in events)
    except Exception as e:
        logger.error(f"event_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in event_command."

@plugin('plan event', canonical='plan event')
def plan_event_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/event.py - Event planning command.
    Subcommands:
      default : Create a new event.
    USAGE: {USAGE_PLAN_EVENT}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_PLAN_EVENT}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    if not new_args.strip():
        return f"Usage: {USAGE_PLAN_EVENT}"
    if new_args.strip().lower() in {"skip", "cancel"}:
        return "Event creation cancelled."
    parts = {}
    for chunk in new_args.split(","):
        chunk = chunk.strip()
        if ":" not in chunk or not chunk:
            return f"Usage: {USAGE_PLAN_EVENT}"
        k, v = chunk.split(":", 1)
        parts[k.strip().lower()] = v.strip()
    required_fields = ["title", "date", "time", "location", "description"]
    missing = [f for f in required_fields if f not in parts]
    if missing:
        return f"Missing required fields: {', '.join(missing)}. {USAGE_PLAN_EVENT_PARTIAL}"
    from parsers.plugin_arg_parser import PlanEventModel
    data = {
        "title": parts["title"],
        "date": parts["date"],
        "time": parts["time"],
        "location": parts["location"],
        "description": parts["description"],
    }
    validated = validate_model(data, PlanEventModel, USAGE_PLAN_EVENT)
    ev_id = create_event(
        validated.title,
        validated.date,
        validated.time,
        validated.location,
        validated.description
    )
    return f"Event '{validated.title}' created successfully with ID {ev_id}."

@plugin('edit event', canonical='edit event')
def edit_event_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/event.py - Event editing command.
    Subcommands:
      default : Update an existing event.
    USAGE: {USAGE_EDIT_EVENT}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_EDIT_EVENT}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    if not new_args.strip():
        return f"Usage: {USAGE_EDIT_EVENT}"
    parts = {}
    for chunk in new_args.split(","):
        chunk = chunk.strip()
        if ":" not in chunk or not chunk:
            return f"Usage: {USAGE_EDIT_EVENT}"
        k, v = chunk.split(":", 1)
        parts[k.strip().lower()] = v.strip()
    if "eventid" not in parts:
        return "EventID is required for updating an event."
    from parsers.plugin_arg_parser import EditEventModel
    data = {
        "event_id": parts["eventid"],
        "title": parts.get("title"),
        "date": parts.get("date"),
        "time": parts.get("time"),
        "location": parts.get("location"),
        "description": parts.get("description"),
    }
    validated = validate_model(data, EditEventModel, USAGE_EDIT_EVENT)
    existing = get_event(validated.event_id)
    if not existing:
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

@plugin('remove event', canonical='remove event')
def remove_event_command(args: str, sender: str, state_machine: BotStateMachine,
                         msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/event.py - Event removal command.
    Subcommands:
      default : Delete an existing event.
    USAGE: {USAGE_REMOVE_EVENT}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_REMOVE_EVENT}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    if not new_args.strip():
        return f"Usage: {USAGE_REMOVE_EVENT}"
    parts = {}
    for chunk in new_args.split(","):
        chunk = chunk.strip()
        if ":" not in chunk or not chunk:
            return f"Usage: {USAGE_REMOVE_EVENT}"
        k, v = chunk.split(":", 1)
        parts[k.strip().lower()] = v.strip()
    from parsers.plugin_arg_parser import RemoveEventByIdModel, RemoveEventByTitleModel
    if "eventid" in parts:
        data = {"event_id": parts["eventid"]}
        validated = validate_model(data, RemoveEventByIdModel, USAGE_REMOVE_EVENT)
        existing = get_event(validated.event_id)
        if not existing:
            return f"No event found with ID {validated.event_id}."
        delete_event(validated.event_id)
        return f"Event with ID {validated.event_id} removed successfully."
    elif "title" in parts:
        data = {"title": parts["title"]}
        validated = validate_model(data, RemoveEventByTitleModel, USAGE_REMOVE_EVENT)
        evs = list_all_events()
        found_id = None
        for ev in evs:
            if ev.get("title", "").lower() == validated.title.lower():
                found_id = ev.get("event_id")
                break
        if not found_id:
            return f"No event found with title '{validated.title}'."
        delete_event(found_id)
        return f"Event with ID {found_id} removed successfully."
    else:
        return f"Usage: {USAGE_REMOVE_EVENT}"

@plugin('event speakers', canonical='event speakers')
def event_speakers_command(args: str, sender: str, state_machine: BotStateMachine,
                           msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/event.py - Event speakers listing command.
    Subcommands:
      default : List all event speakers.
    USAGE: @bot event speakers
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return "Unknown subcommand. USAGE: @bot event speakers"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        speakers = list_all_event_speakers()
        if not speakers:
            return "No event speakers found."
        return "\n".join(format_event_speaker(sp) for sp in speakers)
    except Exception as e:
        logger.error(f"event_speakers_command error: {e}", exc_info=True)
        return "An internal error occurred in event_speakers_command."

# End of plugins/commands/event.py