"""
plugins/commands/event.py - Event command plugins.
Provides commands related to events such as event summary, speakers, and event planning.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine

@plugin('event', canonical='event')
def event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    event - Shows a summary of the next event.
    Usage: "@bot event"
    """
    from core.event_config import EVENT_DETAILS
    event = EVENT_DETAILS.get("upcoming_event", {})
    if not event:
        return "No upcoming event information available."
    return (
        f"{event.get('title', 'Next Event')}\n\n"
        f"Date: {event.get('date', 'Unknown Date')}\n"
        f"Time: {event.get('time', 'Unknown Time')}\n"
        f"Location: {event.get('location', 'Unknown Location')}\n\n"
        f"{event.get('description', 'No description')}"
    )

@plugin('speakers', canonical='speakers')
def speakers_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    speakers - Returns upcoming speakers for the next event or for a specified event.
    Usage: "@bot speakers" or "@bot speakers <event name>"
    """
    if args.strip():
        event_name = args.strip()
        return (
            f"Upcoming Speakers for '{event_name}':\n\n"
            "1. Laura Oatman, Indivisible - 3 min\n"
            "2. Cathey Ryder, HB/OC Huddle and Protect HB - 3 min\n"
            "3. Additional speakers to be announced."
        )
    else:
        return (
            "Upcoming Speakers for the Next Event (Sunday 3/9):\n\n"
            "Emcee: Daniel (starts at 2:30pm)\n"
            "Speaker 1: Laura Oatman, Indivisible - 3 min\n"
            "Speaker 2: Cathey Ryder, HB/OC Huddle and Protect HB - 3 min\n"
            "More speakers will be announced shortly."
        )

@plugin('plan event', canonical='plan event')
def plan_event_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    plan event - Walks you through creating an event.
    Usage: "@bot plan event"
    """
    return (
        "Plan Event:\n\n"
        "To create a new event, please provide the following details:\n"
        "- Title\n"
        "- Date (e.g., Sunday 3/9)\n"
        "- Time (e.g., 2-4PM)\n"
        "- Location\n"
        "- Description\n\n"
        "Please reply with your event details in the following format:\n"
        "'Title: <title>, Date: <date>, Time: <time>, Location: <location>, Description: <description>'"
    )

# End of plugins/commands/event.py