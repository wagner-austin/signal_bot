"""
plugins/commands/speaker.py - Speaker command plugins.
Subcommands:
  add speaker    : default - Add a speaker to an event.
  remove speaker : default - Remove a speaker from an event.
USAGE: See respective USAGE constants in core/plugin_usage.
"""

import logging
from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError
from managers.event_manager import list_all_events, assign_speaker, remove_speaker
from core.plugin_usage import USAGE_ADD_SPEAKER, USAGE_REMOVE_SPEAKER

logger = logging.getLogger(__name__)

@plugin('add speaker', canonical='add speaker')
def add_speaker_command(args: str, sender: str, state_machine: BotStateMachine,
                        msg_timestamp: Optional[int] = None) -> str:
    """
    plugins/commands/speaker.py - Add speaker command.
    Subcommands:
      default : Add a speaker to an event.
    USAGE: {USAGE_ADD_SPEAKER}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_ADD_SPEAKER}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        parts = parse_plugin_arguments(new_args, mode='kv')["kv"]
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
    plugins/commands/speaker.py - Remove speaker command.
    Subcommands:
      default : Remove a speaker from an event.
    USAGE: {USAGE_REMOVE_SPEAKER}
    """
    tokens = args.strip().split(None, 1)
    if not tokens:
        tokens = ["default"]
    if tokens[0].lower() != "default":
        return f"Unknown subcommand. USAGE: {USAGE_REMOVE_SPEAKER}"
    new_args = tokens[1] if len(tokens) > 1 else ""
    try:
        parts = parse_plugin_arguments(new_args, mode='kv')["kv"]
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

# End of plugins/commands/speaker.py