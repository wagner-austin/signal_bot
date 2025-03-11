#!/usr/bin/env python
"""
plugins/commands/volunteer.py --- Volunteer-related command plugins.
Ensures add_skills_command checks if args are empty before checking registration,
using the unified validate_model for consistent argument validation.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.database.volunteers import get_volunteer_record
from managers.volunteer_manager import VOLUNTEER_MANAGER
from managers.pending_actions import PENDING_ACTIONS
from core.messages import (
    REGISTRATION_PROMPT, ALREADY_REGISTERED, EDIT_PROMPT, DELETION_PROMPT
)
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import (
    PluginArgError,
    VolunteerFindModel,
    VolunteerAddSkillsModel,
    validate_model
)
from pydantic import ValidationError

@plugin('volunteer status', canonical='volunteer status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine,
                             msg_timestamp: Optional[int] = None) -> str:
    """ volunteer status - Display the current status of all volunteers. """
    return VOLUNTEER_MANAGER.volunteer_status()

@plugin('check in', canonical='check in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """ check in - Check in a volunteer (the sender). """
    return VOLUNTEER_MANAGER.check_in(sender)

@plugin('register', canonical='register')
def register_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    register - Interactive volunteer registration command.
    If invoked with arguments, directly registers. Else sets pending registration.
    """
    record = get_volunteer_record(sender)
    if args.strip():
        if record:
            return ALREADY_REGISTERED.format(name=record['name'])
        else:
            return VOLUNTEER_MANAGER.sign_up(sender, args.strip(), [])
    else:
        if record:
            return ALREADY_REGISTERED.format(name=record['name'])
        else:
            PENDING_ACTIONS.set_registration(sender, "register")
            return REGISTRATION_PROMPT

@plugin(
    [
        'edit','change my name please','change my name to','change my name',
        'can you change my name please','can you change my name to','can you change my name',
        'can i change my name to','can i change my name','not my name',"that's not my name",
        'wrong name','i mispelled'
    ],
    canonical='edit',
    help_visible=False
)
def edit_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    edit - Edit your registered name.
    If no arguments are provided, initiates an interactive edit; else updates name.
    """
    record = get_volunteer_record(sender)
    if not record:
        PENDING_ACTIONS.set_registration(sender, "register")
        return REGISTRATION_PROMPT
    if not args.strip():
        PENDING_ACTIONS.set_registration(sender, "edit")
        return EDIT_PROMPT.format(name=record['name'])
    return VOLUNTEER_MANAGER.sign_up(sender, args.strip(), [])

@plugin(['delete','del','stop','unsubscribe','remove','opt out'], canonical='delete', help_visible=False)
def delete_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    delete - Delete your registration. Without arguments, asks for deletion confirmation.
    """
    if not args.strip():
        PENDING_ACTIONS.set_deletion(sender, "initial")
        return DELETION_PROMPT
    PENDING_ACTIONS.set_deletion(sender, "initial")
    return DELETION_PROMPT

@plugin('skills', canonical='skills')
def skills_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    skills - Display your current skills and list available skills for addition.
    If not registered, initiates registration.
    """
    from core.database import get_volunteer_record
    from core.skill_config import AVAILABLE_SKILLS
    record = get_volunteer_record(sender)
    if not record:
        PENDING_ACTIONS.set_registration(sender, "register")
        return REGISTRATION_PROMPT
    else:
        current_skills = record.get("skills", [])
        if current_skills:
            current_skills_formatted = "\n".join([f" - {skill}" for skill in current_skills])
        else:
            current_skills_formatted = " - None"
        available_skills_formatted = "\n".join([f" - {skill}" for skill in AVAILABLE_SKILLS])
        name = record.get("name", "Anonymous")
        message = f"{name} currently has skills:\n{current_skills_formatted}\n\n"
        message += "Here is a list of relevant skills you can add:\n" + available_skills_formatted
        return message

@plugin('find', canonical='find')
def find_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    find - Finds volunteers with the specified skill(s).
    Usage: "@bot find <skill1> <skill2> ..."
    """
    from core.database import get_all_volunteers
    try:
        raw_tokens = args.split()
        if not raw_tokens:
            return "Usage: @bot find <skill1> <skill2> ..."
        data = {"skills": [s.lower() for s in raw_tokens]}
        validated = validate_model(data, VolunteerFindModel, "find <skill1> <skill2> ...")
        volunteers = get_all_volunteers()
        matching_volunteers = []
        for phone, data in volunteers.items():
            volunteer_skills = [s.lower() for s in data.get("skills", [])]
            if all(req in volunteer_skills for req in validated.skills):
                matching_volunteers.append(data.get("name", phone))
        if matching_volunteers:
            return "Volunteers with specified skills: " + ", ".join(matching_volunteers)
        else:
            return "No volunteers found with the specified skills."
    except PluginArgError as e:
        return str(e)

@plugin('add skills', canonical='add skills')
def add_skills_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    add skills - Adds skills to your profile.
    Usage: "@bot add skills <skill1>, <skill2>, ..."
    """
    if not args.strip():
        return "Usage: @bot add skills <skill1>, <skill2>, ..."
    from core.database import get_volunteer_record
    record = get_volunteer_record(sender)
    if not record:
        return "You are not registered. Please register first."
    raw_tokens = [t.strip() for t in args.split(",") if t.strip()]
    if not raw_tokens:
        return "Usage: @bot add skills <skill1>, <skill2>, ..."
    data = {"skills": raw_tokens}
    validated = validate_model(data, VolunteerAddSkillsModel, "add skills <skill1>, <skill2>, ...")
    return VOLUNTEER_MANAGER.sign_up(sender, "skip", validated.skills)

# End of plugins/commands/volunteer.py