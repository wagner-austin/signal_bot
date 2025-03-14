#!/usr/bin/env python
"""
plugins/commands/volunteer.py
-----------------------------
Volunteer command plugins for registration, editing, deletion, and other volunteer actions.
All multi-step flows for registration and deletion are delegated to FlowManager. 
No partial checks for name or confirmation remain here.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER
from parsers.argument_parser import parse_plugin_arguments
from parsers.plugin_arg_parser import PluginArgError, VolunteerFindModel, VolunteerAddSkillsModel, validate_model
import logging
from core.exceptions import ResourceError, VolunteerError
from core.plugin_usage import (
    USAGE_VOLUNTEER_STATUS, USAGE_REGISTER,
    USAGE_EDIT, USAGE_DELETE, USAGE_SKILLS, USAGE_FIND, USAGE_ADD_SKILLS
)
from managers.user_states_manager import get_active_flow
from db.volunteers import get_volunteer_record
from managers.volunteer_skills_manager import AVAILABLE_SKILLS
from plugins.commands.formatters import format_deleted_volunteer, format_volunteer
from managers.flow_manager import FlowManager

# For the no-args registration test
from core.messages import REGISTRATION_WELCOME

logger = logging.getLogger(__name__)
FLOW_MANAGER = FlowManager()

@plugin('volunteer status', canonical='volunteer status')
def volunteer_status_command(args: str, sender: str, state_machine: BotStateMachine,
                             msg_timestamp: Optional[int] = None) -> str:
    """
    volunteer status
    ---------------
    Subcommands:
      default : Display volunteer status for all volunteers (no multi-step flow).
    USAGE: {USAGE_VOLUNTEER_STATUS}
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    if subcmd != "default":
        return f"Unknown subcommand. USAGE: {USAGE_VOLUNTEER_STATUS}"

    if get_active_flow(sender):
        return "You have an active multi-step flow. Please finish or cancel it first."

    try:
        all_vols = VOLUNTEER_MANAGER.list_all_volunteers_list()
        if not all_vols:
            return "No volunteers found."
        return "\n".join(format_volunteer(v) for v in all_vols)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"volunteer_status_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"volunteer_status_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in volunteer_status_command."

@plugin('check in', canonical='check in')
def check_in_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    check in
    --------
    Subcommands:
      default : Mark volunteer as available (no flow).
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    if subcmd != "default":
        # Include "usage" in the response so test_subcommand_consistency passes
        return "Unknown subcommand. USAGE: check in does not require additional arguments."

    if get_active_flow(sender):
        return "You're in a multi-step flow. Please finish or cancel that flow first."

    try:
        return VOLUNTEER_MANAGER.check_in(sender)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"check_in_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"check_in_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in check_in_command."

@plugin('register', canonical='register')
def register_command(args: str, sender: str, state_machine: BotStateMachine,
                     msg_timestamp: Optional[int] = None) -> str:
    """
    register
    --------
    Subcommands:
      default : Start or continue registration flow.
    USAGE: {USAGE_REGISTER}
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    user_input = tokens[1] if len(tokens) > 1 else ""

    if subcmd != "default":
        return f"Unknown subcommand. USAGE: {USAGE_REGISTER}"

    try:
        active_flow = get_active_flow(sender)
        if not active_flow:
            FLOW_MANAGER.start_flow(sender, FLOW_MANAGER.REGISTRATION_FLOW)
            # If user provided no input => show welcome
            if not user_input.strip():
                return REGISTRATION_WELCOME
        return FLOW_MANAGER.handle_flow_input(sender, user_input)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"register_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
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
    edit
    ----
    Subcommands:
      default : Start or continue the edit flow.
    USAGE: {USAGE_EDIT}
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    user_input = tokens[1] if len(tokens) > 1 else ""

    if subcmd != "default":
        # We must include "usage" for test_subcommand_consistency
        return f"Unknown subcommand. USAGE: {USAGE_EDIT}"

    try:
        active_flow = get_active_flow(sender)
        if not active_flow:
            FLOW_MANAGER.start_flow(sender, FLOW_MANAGER.EDIT_FLOW)
            if not user_input.strip():
                # The test expects "starting edit flow." or a prompt
                return "Starting edit flow. Please provide your new name or type 'skip' to cancel."
        return FLOW_MANAGER.handle_flow_input(sender, user_input)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"edit_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"edit_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in edit_command."

@plugin(['delete','del','stop','unsubscribe','remove','opt out'], canonical='delete', help_visible=False)
def delete_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    delete
    ------
    Subcommands:
      default : Start or continue the volunteer deletion flow.
    USAGE: {USAGE_DELETE}
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    user_input = tokens[1] if len(tokens) > 1 else ""

    if subcmd != "default":
        return f"Unknown subcommand. USAGE: {USAGE_DELETE}"

    try:
        active_flow = get_active_flow(sender)
        if not active_flow:
            FLOW_MANAGER.start_flow(sender, FLOW_MANAGER.DELETION_FLOW)
            if not user_input.strip():
                return "Starting deletion flow. Type 'yes' to confirm or anything else to cancel."
        return FLOW_MANAGER.handle_flow_input(sender, user_input)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"delete_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"delete_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in delete_command."

@plugin('skills', canonical='skills')
def skills_command(args: str, sender: str, state_machine: BotStateMachine,
                   msg_timestamp: Optional[int] = None) -> str:
    """
    skills
    ------
    Subcommands:
      default : Show or reference volunteer skills. Blocks if user in multi-step flow.
    USAGE: {USAGE_SKILLS}
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    if subcmd != "default":
        return f"Unknown subcommand. USAGE: {USAGE_SKILLS}"

    if get_active_flow(sender):
        return "You have an active multi-step flow. Please finish or cancel it first."

    try:
        record = get_volunteer_record(sender)
        if not record:
            return "You are not registered. Try '@bot register' to create a profile first."
        current_skills = record.get("skills", [])
        skill_lines = "\n".join(f" - {s}" for s in current_skills) if current_skills else " - None"
        all_skills = "\n".join(f" - {s}" for s in AVAILABLE_SKILLS)
        name = record.get("name", "Anonymous")

        return (
            f"{name} currently has skills:\n{skill_lines}\n\n"
            "Here is a list of relevant skills you can add:\n" + all_skills
        )
    except (ResourceError, VolunteerError) as e:
        logger.error(f"skills_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"skills_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in skills_command."

@plugin('find', canonical='find')
def find_command(args: str, sender: str, state_machine: BotStateMachine,
                 msg_timestamp: Optional[int] = None) -> str:
    """
    find
    ----
    Subcommands:
      default : Find volunteers by listed skills.
    USAGE: {USAGE_FIND}
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    leftover = tokens[1].strip() if len(tokens) > 1 else ""

    if subcmd != "default":
        return f"Unknown subcommand. USAGE: {USAGE_FIND}"
    if not leftover:
        return f"Usage: {USAGE_FIND}"

    try:
        data = {"skills": [s.lower() for s in leftover.split()]}
        validated = validate_model(data, VolunteerFindModel, USAGE_FIND)

        from db.volunteers import get_all_volunteers
        volunteers = get_all_volunteers()
        matching = []
        for phone, vol_data in volunteers.items():
            vskills = [s.lower() for s in vol_data.get("skills", [])]
            if all(req in vskills for req in validated.skills):
                matching.append(vol_data.get("name", phone))

        if matching:
            return "Volunteers with specified skills: " + ", ".join(matching)
        return "No volunteers found with the specified skills."
    except PluginArgError as e:
        logger.warning(f"find_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"find_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"find_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in find_command."

@plugin('add skills', canonical='add skills')
def add_skills_command(args: str, sender: str, state_machine: BotStateMachine,
                       msg_timestamp: Optional[int] = None) -> str:
    """
    add skills
    ----------
    Subcommands:
      default : Add skills to your volunteer profile.
    USAGE: {USAGE_ADD_SKILLS}
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    leftover = tokens[1].strip() if len(tokens) > 1 else ""

    if subcmd != "default":
        return f"Unknown subcommand. USAGE: {USAGE_ADD_SKILLS}"

    # Return usage if empty leftover so test_plugin_negatives can pass
    if not leftover:
        return f"Usage: {USAGE_ADD_SKILLS}"

    if get_active_flow(sender):
        return "You have an active multi-step flow. Please finish or cancel it first."

    try:
        record = get_volunteer_record(sender)
        if not record:
            return "You are not registered. Please register first."

        raw_tokens = [t.strip() for t in leftover.split(",") if t.strip()]
        if not raw_tokens:
            raise PluginArgError(USAGE_ADD_SKILLS)

        data = {"skills": raw_tokens}
        validated = validate_model(data, VolunteerAddSkillsModel, USAGE_ADD_SKILLS)
        return VOLUNTEER_MANAGER.register_volunteer(
            sender, record['name'], validated.skills,
            available=record['available'],
            current_role=record['current_role']
        )
    except PluginArgError as e:
        logger.warning(f"add_skills_command PluginArgError: {e}")
        return str(e)
    except (ResourceError, VolunteerError) as e:
        logger.error(f"add_skills_command domain error: {e}", exc_info=True)
        return f"An error occurred: {str(e).split(':',1)[-1].strip()}"
    except Exception as e:
        logger.error(f"add_skills_command unexpected error: {e}", exc_info=True)
        return "An internal error occurred in add_skills_command."

@plugin('deleted volunteers', canonical='deleted volunteers')
def deleted_volunteers_command(args: str, sender: str, state_machine: BotStateMachine,
                               msg_timestamp: Optional[int] = None) -> str:
    """
    deleted volunteers
    ------------------
    Subcommands:
      default : List deleted volunteer records.
    """
    tokens = args.strip().split(None, 1)
    subcmd = tokens[0].lower() if tokens else "default"
    if subcmd != "default":
        return "Unknown subcommand. USAGE: deleted volunteers command does not require additional arguments."

    if get_active_flow(sender):
        return "You have an active multi-step flow. Please finish or cancel it first."

    try:
        recs = VOLUNTEER_MANAGER.list_deleted_volunteers()
        if not recs:
            return "No deleted volunteers found."
        return "\n".join(format_deleted_volunteer(r) for r in recs)
    except Exception as e:
        logger.error(f"deleted_volunteers_command error: {e}", exc_info=True)
        return "An internal error occurred in deleted_volunteers_command."

# End of plugins/commands/volunteer.py