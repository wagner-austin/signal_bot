"""
plugins/commands/volunteer.py - Volunteer-related command plugins for the Signal bot.
Includes commands such as volunteer status, check in, feedback, register, edit, delete, and skills.
Utilizes PendingActions to manage interactive registration and deletion flows.
"""

from typing import Optional
from plugins.manager import plugin, get_all_plugins
from core.state import BotStateMachine
from core.database import get_volunteer_record
from managers.volunteer import VOLUNTEER_MANAGER
from managers.pending_actions import PENDING_ACTIONS

@plugin('volunteer status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    volunteer status - Display the current status of all volunteers.
    """
    return VOLUNTEER_MANAGER.volunteer_status()

@plugin('check in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    check in - Check in a volunteer.
    Expected format: "@bot check in" (the sender is assumed to be the volunteer).
    """
    return VOLUNTEER_MANAGER.check_in(sender)

@plugin('feedback')
def feedback_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    feedback - Submit feedback or report issues.
    Expected format: "@bot feedback <Your feedback or report>"
    """
    feedback_text = args.strip()
    if not feedback_text:
        return "Usage: @bot feedback <Your feedback or report>"
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Feedback from {sender}: {feedback_text}")
    return "Thank you for your feedback. It has been logged for review."

@plugin('register')
def register_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    register - Interactive volunteer registration command.
    Handles registration in two steps:
      1. If invoked as "@bot register" without arguments:
         - If the sender is not registered, prompt:
           "Welcome! Please respond with your first and last name to get registered. Or \"skip\" to remain anonymous."
         - If the sender is already registered, reply:
           "You are registered as \"<Existing Name>\". Use command \"@bot edit\" to edit your name."
      2. If invoked with arguments, registers the volunteer,
         returning "New volunteer '<Name>' registered".
    """
    if args.strip():
        name = args.strip()
        record = get_volunteer_record(sender)
        if record:
            return f"You are registered as \"{record['name']}\". Use command \"@bot edit\" to edit your name."
        else:
            return VOLUNTEER_MANAGER.sign_up(sender, name, [])
    else:
        record = get_volunteer_record(sender)
        if record:
            return f"You are registered as \"{record['name']}\". Use command \"@bot edit\" to edit your name."
        else:
            PENDING_ACTIONS.set_registration(sender, "register")
            return "Welcome! Please respond with your first and last name to get registered. Or 'skip' to remain anonymous."

@plugin('edit')
@plugin('change my name please')
@plugin('change my name to')
@plugin('change my name')
@plugin('change name')
@plugin('can you change my name please')
@plugin('can you change my name to')
@plugin('can you change my name')
@plugin('can i change my name to')
@plugin('can i change my name')
@plugin('not my name')
@plugin("that's not my name")
@plugin('wrong name')
@plugin('i mispelled')
def edit_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    edit (aliases: change name, not my name, that's not my name, wrong name, i mispelled) - Edit your registered name.
    Usage:
      - If invoked without arguments:
          For new users: interpreted as register, initiating the registration process.
          For existing users: reply "You are registered as '<Existing Name>'. Type a new name or type 'skip' to cancel editing."
      - If invoked with arguments, updates the volunteer's name immediately.
    """
    record = get_volunteer_record(sender)
    if not record:
        # Treat as registration for new users.
        PENDING_ACTIONS.set_registration(sender, "register")
        return "Welcome! Please respond with your first and last name to get registered. Or \"skip\" to remain anonymous."
    if not args.strip():
        # For existing users, prompt for editing.
        PENDING_ACTIONS.set_registration(sender, "edit")
        return f"You are registered as \"{record['name']}\". Type a new name or type \"skip\" to cancel editing."
    # If arguments provided, update immediately.
    return VOLUNTEER_MANAGER.sign_up(sender, args.strip(), [])

@plugin('delete')
@plugin('del')
@plugin('stop')
@plugin('unsubscribe')
@plugin('remove')
@plugin('opt out')
def delete_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    delete/del/stop/unsubscribe/remove/opt out - Delete your registration.
    Usage:
      - When invoked as "@bot delete" (or any alias) without arguments, the bot asks:
          "Would you like to delete your registration? Yes or No"
      - Subsequent responses are processed interactively:
          If affirmative, the bot then prompts: "Please respond with 'DELETE' to delete your account."
          If the user responds with "DELETE", the registration is deleted (and stored in trash).
          Otherwise, deletion is cancelled and the current registration is maintained.
    """
    if not args.strip():
        PENDING_ACTIONS.set_deletion(sender, "initial")
        return "Would you like to delete your registration? Yes or No"
    PENDING_ACTIONS.set_deletion(sender, "initial")
    return "Would you like to delete your registration? Yes or No?"

@plugin('skills')
def skills_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    skills - Display current skills and list available skills for addition.
    For existing users: Shows their registered skills (formatted as a bullet list) and a list of relevant available skills.
    For new users: Acts as a registration command.
    Usage: "@bot skills"
    """
    from core.database import get_volunteer_record
    from core.skill_config import AVAILABLE_SKILLS
    record = get_volunteer_record(sender)
    if not record:
        # Not registered; treat as registration.
        PENDING_ACTIONS.set_registration(sender, "register")
        return "Welcome! Please respond with your first and last name to get registered. Or 'skip' to remain anonymous."
    else:
        current_skills = record.get("skills", [])
        if current_skills:
            current_skills_formatted = "\n".join([f" - {skill}" for skill in current_skills])
        else:
            current_skills_formatted = " - None"
        available_skills_formatted = "\n".join([f" - {skill}" for skill in AVAILABLE_SKILLS])
        name = record.get("name", "Anonymous")
        message = f"{name} currently has skills:\n{current_skills_formatted}\n\n"
        message += "Here is a list of relevant skills you can add to your profile:\n" + available_skills_formatted
        return message

# End of plugins/commands/volunteer.py