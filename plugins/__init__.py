"""
__init__.py
-----------
Plugin definitions for the Signal bot.
Each plugin is registered via the @plugin decorator from the unified plugins/manager.
This module exports the public plugin commands for use in the bot.
"""

from plugins.manager import plugin  # Updated import from unified plugins/manager
from managers.volunteer_manager import VOLUNTEER_MANAGER

@plugin('assign')
def assign_command(args, sender, state_machine, msg_timestamp=None):
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
def test_command(args, sender, state_machine, msg_timestamp=None):
    """
    Plugin command for testing.
    Expected format: "test" or "@bot test"
    Responds with "yes".
    """
    return "yes"

@plugin('shutdown')
def shutdown_command(args, sender, state_machine, msg_timestamp=None):
    """
    Plugin command to shut down the bot gracefully.
    Expected format: "@bot shutdown"
    """
    state_machine.shutdown()
    return "Bot is shutting down."
