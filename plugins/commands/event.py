"""
plugins/commands/event.py - Event command plugins for the Signal bot.
Includes commands like event and event info.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER

@plugin('event')
def event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    event - Shows a summary of the next event.
    Usage: "@bot event"
    """
    from core.event_config import EVENT_DETAILS
    event = EVENT_DETAILS.get("upcoming_event", {})
    if not event:
        return "No upcoming event information available."
    summary = (
        f"{event.get('title', 'Next Event')}\n\n"
        f"{event.get('date', 'Unknown Date')} "
        f"from {event.get('time', 'Unknown Time')}.\n\n"
        f"{event.get('description', 'No description')}\n\n"
        f"{event.get('location', 'Unknown Location')}"
    )
    return summary

@plugin('event info')
def event_info_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    event info - Provides detailed information on the next event.
    Usage: "@bot event info"
    """
    from core.event_config import EVENT_DETAILS
    event = EVENT_DETAILS.get("upcoming_event", {})
    if not event:
        return "No upcoming event information available."
    details = (
        f"Title: {event.get('title', 'Next Event')}\n"
        f"Date: {event.get('date', 'Unknown')}\n"
        f"Time: {event.get('time', 'Unknown')}\n"
        f"Location: {event.get('location', 'Unknown')}\n"
        f"Description: {event.get('description', 'No description')}\n"
        "Volunteer Roles:"
    )
    for role, person in event.get("volunteer_roles", {}).items():
        details += f"\n  - {role.capitalize()}: {person}"
    return details

# End of plugins/commands/event.py
