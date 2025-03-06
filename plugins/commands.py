"""
plugins/commands.py - Contains the implementation of command plugins for the Signal bot.
Each command is registered using the @plugin decorator from the unified plugins/manager.
Includes new commands for event information, volunteer status, check-in, sign-up, and feedback.
"""

from typing import Optional
from plugins.manager import plugin
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.state import BotStateMachine

@plugin('assign')
def assign_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to assign a volunteer based on a skill.
    Expected format: "@bot assign <Skill Name>"
    """
    skill = args.strip()
    if not skill:
        return "Usage: @bot assign <Skill Name>"
    volunteer = VOLUNTEER_MANAGER.assign_volunteer(skill, skill)
    if volunteer:
        return f"{skill} assigned to {volunteer}."
    else:
        return f"No available volunteer for {skill}."

@plugin('test')
def test_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command for testing.
    Expected format: "test" or "@bot test"
    Responds with "yes".
    """
    return "yes"

@plugin('shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to shut down the bot gracefully.
    Expected format: "@bot shutdown"
    """
    state_machine.shutdown()
    return "Bot is shutting down."

@plugin('test_all')
async def test_all_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to run all integration tests.
    Invokes tests for message parsing, volunteer assignment, state transitions,
    and simulated message sending. Returns a summary of test results.
    """
    from tests.test_all import run_tests
    summary = await run_tests()
    return summary

@plugin('event_info')
def event_info_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to display details about the upcoming event.
    Fetches event details such as time, location, and volunteer roles.
    """
    from core.event_config import EVENT_DETAILS
    event = EVENT_DETAILS.get("upcoming_event", {})
    if not event:
        return "No upcoming event information available."
    details = (
        f"Event: {event.get('title')}\n"
        f"Date: {event.get('date')}\n"
        f"Time: {event.get('time')}\n"
        f"Location: {event.get('location')}\n"
        f"Description: {event.get('description')}\n"
        f"Volunteer Roles:"
    )
    roles = event.get("volunteer_roles", {})
    for role, person in roles.items():
        details += f"\n - {role.capitalize()}: {person}"
    return details

@plugin('volunteer_status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to display the current status of all volunteers.
    """
    return VOLUNTEER_MANAGER.volunteer_status()

@plugin('check_in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to check in a volunteer, marking them as available.
    Expected format: "@bot check_in <Volunteer Name>"
    """
    volunteer_name = args.strip()
    if not volunteer_name:
        return "Usage: @bot check_in <Volunteer Name>"
    return VOLUNTEER_MANAGER.check_in(volunteer_name)

@plugin('sign_up')
def sign_up_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command to sign up a new volunteer or update an existing volunteer's skills.
    Expected format: "@bot sign_up <Volunteer Name> <Skill1,Skill2,...>"
    """
    parts = args.split()
    if len(parts) < 2:
        return "Usage: @bot sign_up <Volunteer Name> <Skill1,Skill2,...>"
    volunteer_name = parts[0]
    skills_str = " ".join(parts[1:])
    skills = [s.strip() for s in skills_str.split(",") if s.strip()]
    return VOLUNTEER_MANAGER.sign_up(volunteer_name, skills)

@plugin('feedback')
def feedback_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    Plugin command for feedback and reporting.
    Users can report issues or suggest improvements.
    Expected format: "@bot feedback <Your feedback or report>"
    """
    feedback_text = args.strip()
    if not feedback_text:
        return "Usage: @bot feedback <Your feedback or report>"
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Feedback from {sender}: {feedback_text}")
    return "Thank you for your feedback. It has been logged for review."

# End of plugins/commands.py