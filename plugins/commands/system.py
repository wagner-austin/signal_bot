"""
plugins/commands/system.py - System command plugins for the Signal bot.
Includes commands like assign, test, shutdown, test all, and info.
"""

from typing import Optional
import difflib
from plugins.manager import plugin, get_all_plugins
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER

@plugin('assign')
def assign_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    assign - Assign a volunteer based on a required skill.
    Expected format: "@bot assign <Skill Name>"
    """
    skill = args.strip()
    if not skill:
        return "Usage: @bot assign <Skill Name>"
    volunteer = VOLUNTEER_MANAGER.assign_volunteer(skill, skill)
    if volunteer:
        return f"{skill} assigned to {volunteer}."
    return f"No available volunteer for {skill}."

@plugin('test')
def test_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    test - Test command for verifying bot response.
    Expected format: "@bot test"
    """
    return "yes"

@plugin('shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    shutdown - Shut down the bot gracefully.
    Expected format: "@bot shutdown"
    """
    state_machine.shutdown()
    return "Bot is shutting down."

@plugin('test all')
async def test_all_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    test all - Run integration tests.
    """
    from tests.test_all import run_tests
    summary = await run_tests()
    return summary

@plugin('info')
def info_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    info - Provides a brief overview of the 50501 OC Grassroots Movement.
    Usage: "@bot info"
    """
    return (
        "50501 OC Grassroots Movement is dedicated to upholding the Constitution and ending executive overreach. \n\n"
        "Our objective is to foster peaceful, visible, and sustained community engagement through nonviolent protest. "
        "We empower citizens to reclaim democracy and hold power accountable, inspiring change through unity and active resistance."
    )

# End of plugins/commands/system.py