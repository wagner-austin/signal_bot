#!/usr/bin/env python
"""
plugins/commands/volunteer.py - Volunteer command plugins.
Handles volunteer registration, editing, deletion, skill updates, and more.
Centralizes exception handling to convert domain errors to user-friendly messages.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from core.messages import (
    REGISTRATION_PROMPT, ALREADY_REGISTERED, EDIT_PROMPT,
    DELETION_PROMPT
)
from managers.volunteer_manager import VOLUNTEER_MANAGER
from managers.pending_actions import PENDING_ACTIONS
from core.constants import SKIP_VALUES
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import (
    PluginArgError,
    VolunteerFindModel,
    VolunteerAddSkillsModel,
    validate_model
)
import logging
from core.exceptions import ResourceError, VolunteerError

logger = logging.getLogger(__name__)

@plugin('volunteer status', canonical='volunteer status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine,
                             msg_timestamp: Optional[int] = None) -> str:
    """
    volunteer status - Display the current volunteer status.
    """
    try:
        return VOLUNTEER_MANAGER.volunteer_status()
    except (ResourceError, VolunteerError) as e:
        logger.error(f"volunteer_status_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e)}"
    except Exception as e:
        logger.error(f"volunteer_status_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in volunteer_status_command."

@plugin('check in', canonical='check in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    check in - Marks a volunteer as available.
    """
    try:
        return VOLUNTEER_MANAGER.check_in(sender)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"check_in_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e)}"
    except Exception as e:
        logger.error(f"check_in_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in check_in_command."

@plugin('register', canonical='register')
def register_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    register - Interactive volunteer registration command.
    """
    try:
        record = VOLUNTEER_MANAGER.list_all_volunteers().get(sender)
        if args.strip():
            if record:
                return ALREADY_REGISTERED.format(name=record['name'])
            else:
                return VOLUNTEER_MANAGER.register_volunteer(sender, args.strip(), [])
        else:
            if record:
                return ALREADY_REGISTERED.format(name=record['name'])
            else:
                PENDING_ACTIONS.set_registration(sender, "register")
                return REGISTRATION_PROMPT
    except (ResourceError, VolunteerError) as e:
        logger.error(f"register_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e)}"
    except Exception as e:
        logger.error(f"register_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in register_command."

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
    """
    try:
        record = VOLUNTEER_MANAGER.list_all_volunteers().get(sender)
        if not record:
            PENDING_ACTIONS.set_registration(sender, "register")
            return REGISTRATION_PROMPT
        if not args.strip():
            PENDING_ACTIONS.set_registration(sender, "edit")
            return EDIT_PROMPT.format(name=record['name'])
        return VOLUNTEER_MANAGER.register_volunteer(sender, args.strip(), [])
    except (ResourceError, VolunteerError) as e:
        logger.error(f"edit_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e)}"
    except Exception as e:
        logger.error(f"edit_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in edit_command."

@plugin(['delete','del','stop','unsubscribe','remove','opt out'], canonical='delete', help_visible=False)
def delete_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    delete - Initiates volunteer deletion flow.
    """
    try:
        if not args.strip():
            PENDING_ACTIONS.set_deletion(sender, "initial")
            return DELETION_PROMPT
        PENDING_ACTIONS.set_deletion(sender, "initial")
        return DELETION_PROMPT
    except (ResourceError, VolunteerError) as e:
        logger.error(f"delete_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e)}"
    except Exception as e:
        logger.error(f"delete_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in delete_command."

@plugin('skills', canonical='skills')
def skills_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    skills - Display your current skills.
    """
    try:
        from core.database import get_volunteer_record
        from core.skill_config import AVAILABLE_SKILLS
        record = get_volunteer_record(sender)
        if not record:
            PENDING_ACTIONS.set_registration(sender, "register")
            return REGISTRATION_PROMPT
        else:
            current_skills = record.get("skills", [])
            current_skills_formatted = "\n".join([f" - {skill}" for skill in current_skills]) if current_skills else " - None"
            available_skills_formatted = "\n".join([f" - {skill}" for skill in AVAILABLE_SKILLS])
            name = record.get("name", "Anonymous")
            message = f"{name} currently has skills:\n{current_skills_formatted}\n\n"
            message += "Here is a list of relevant skills you can add:\n" + available_skills_formatted
            return message
    except (ResourceError, VolunteerError) as e:
        logger.error(f"skills_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e)}"
    except Exception as e:
        logger.error(f"skills_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in skills_command."

@plugin('find', canonical='find')
def find_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    find - Finds volunteers with specified skill(s).
    """
    try:
        from core.database import get_all_volunteers
        raw_tokens = args.split()
        if not raw_tokens:
            raise PluginArgError("Usage: @bot find <skill1> <skill2> ...")
        data = {"skills": [s.lower() for s in raw_tokens]}
        validated = validate_model(data, VolunteerFindModel, "find <skill1> <skill2> ...")
        volunteers = get_all_volunteers()
        matching_volunteers = []
        for phone, data_v in volunteers.items():
            volunteer_skills = [s.lower() for s in data_v.get("skills", [])]
            if all(req in volunteer_skills for req in validated.skills):
                matching_volunteers.append(data_v.get("name", phone))
        if matching_volunteers:
            return "Volunteers with specified skills: " + ", ".join(matching_volunteers)
        else:
            return "No volunteers found with the specified skills."
    except PluginArgError as e:
        logger.warning(f"find_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"find_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e)}"
    except Exception as e:
        logger.error(f"find_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in find_command."

@plugin('add skills', canonical='add skills')
def add_skills_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    add skills - Adds skills to your profile.
    """
    try:
        if not args.strip():
            raise PluginArgError("Usage: @bot add skills <skill1>, <skill2>, ...")
        from core.database import get_volunteer_record
        record = get_volunteer_record(sender)
        if not record:
            return "You are not registered. Please register first."
        raw_tokens = [t.strip() for t in args.split(",") if t.strip()]
        if not raw_tokens:
            raise PluginArgError("Usage: @bot add skills <skill1>, <skill2>, ...")
        data = {"skills": raw_tokens}
        validated = validate_model(data, VolunteerAddSkillsModel, "add skills <skill1>, <skill2>, ...")
        return VOLUNTEER_MANAGER.register_volunteer(sender, "skip", validated.skills)
    except PluginArgError as e:
        logger.warning(f"add_skills_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"add_skills_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e)}"
    except Exception as e:
        logger.error(f"add_skills_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in add_skills_command."

# End of plugins/commands/volunteer.py