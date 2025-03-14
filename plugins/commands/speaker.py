#!/usr/bin/env python
"""
speaker.py
----------
Speaker command plugins for adding/removing event speakers.
Uses dictionary-based event lookups (avoids .get on sqlite3.Row).
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError
from managers.event_manager import list_all_events, assign_speaker, remove_speaker
import logging
from core.plugin_usage import USAGE_ADD_SPEAKER, USAGE_REMOVE_SPEAKER

logger = logging.getLogger(__name__)

@plugin('add speaker', canonical='add speaker')
def add_speaker_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    add speaker - Adds a speaker to an event.
    If "Event:" is omitted, the latest event is used.

    USAGE: {USAGE_ADD_SPEAKER}
    """
    try:
        parts = parse_plugin_arguments(args, mode='kv')["kv"]
        if "event" in parts:
            event_title = parts["event"]
            events = list_all_events()
            event_id = None
            for event in events:
                if event["title"].lower() == event_title.lower():
                    event_id = event["event_id"]
                    break
            if event_id is None:
                return f"No event found with title '{event_title}'."
        else:
            events = list_all_events()
            if not events:
                return "No upcoming events found to assign a speaker."
            event_id = events[0]["event_id"]

        if "name" not in parts or "topic" not in parts:
            return USAGE_ADD_SPEAKER

        speaker_name = parts["name"]
        speaker_topic = parts["topic"]
        assign_speaker(event_id, speaker_name, speaker_topic)
        return f"Speaker '{speaker_name}' with topic '{speaker_topic}' assigned to event ID {event_id} successfully."
    except (PluginArgError, ValueError) as e:
        logger.warning(f"add_speaker_command PluginArgError: {e}")
        return f"Error parsing speaker details: {str(e)}"
    except Exception as e:
        logger.error(f"add_speaker_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in add_speaker_command."

@plugin('remove speaker', canonical='remove speaker')
def remove_speaker_command(args: str, sender: str, state_machine: BotStateMachine,
                          msg_timestamp: Optional[int] = None) -> str:
    """
    remove speaker - Removes a speaker from an event.
    If "Event:" is omitted, the latest event is used.

    USAGE: {USAGE_REMOVE_SPEAKER}
    """
    try:
        parts = parse_plugin_arguments(args, mode='kv')["kv"]
        if "event" in parts:
            event_title = parts["event"]
            events = list_all_events()
            event_id = None
            for event in events:
                if event["title"].lower() == event_title.lower():
                    event_id = event["event_id"]
                    break
            if event_id is None:
                return f"No event found with title '{event_title}'."
        else:
            events = list_all_events()
            if not events:
                return "No upcoming events found."
            event_id = events[0]["event_id"]

        if "name" not in parts:
            return USAGE_REMOVE_SPEAKER

        speaker_name = parts["name"]
        remove_speaker(event_id, speaker_name)
        return f"Speaker '{speaker_name}' removed from event ID {event_id} successfully."
    except (PluginArgError, ValueError) as e:
        logger.warning(f"remove_speaker_command PluginArgError: {e}")
        return f"Error parsing speaker details: {str(e)}"
    except Exception as e:
        logger.error(f"remove_speaker_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in remove_speaker_command."

# End of speaker.py