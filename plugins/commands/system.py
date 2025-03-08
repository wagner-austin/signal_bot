#!/usr/bin/env python
"""
plugins/commands/system.py - System command plugins.
Provides system-level commands such as assign, test, shutdown, info,
weekly update, theme, plan theme, and status.
"""

from typing import Optional
from plugins.manager import plugin
from core.state import BotStateMachine
from managers.volunteer_manager import VOLUNTEER_MANAGER
from core.metrics import get_uptime, messages_sent

@plugin('assign', canonical='assign')
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

@plugin('test', canonical='test')
def plugin_test_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    test - Test command for verifying bot response.
    Expected format: "@bot test"
    """
    return "yes"

@plugin('shutdown', canonical='shutdown')
def shutdown_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    shutdown - Shut down the bot gracefully.
    Expected format: "@bot shutdown"
    """
    state_machine.shutdown()
    return "Bot is shutting down."

@plugin('info', canonical='info')
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

@plugin('weekly update', canonical='weekly update')
def weekly_update_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    weekly update - Provides a summary of Trump's actions and Democrat advances this week.
    Usage: "@bot weekly update"
    """
    return (
        "Weekly Update:\n\n"
        "Trump Actions:\n"
        "- Held multiple rallies and press conferences.\n"
        "- Continued controversial executive orders.\n\n"
        "Democrat Advances:\n"
        "- Pushed forward key legislation on voting rights and healthcare.\n"
        "- Gained momentum in local and state elections.\n\n"
        "Overall, it was a week of stark contrasts between executive actions and legislative progress."
    )

@plugin('theme', canonical='theme')
def theme_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    theme - Displays the important theme for this week.
    Usage: "@bot theme"
    """
    return (
        "This Week's Theme:\n\n"
        "General - Focusing on grassroots organization, community empowerment, and challenging executive overreach.\n"
        "Key Message: Visibility, Unity, and Resistance."
    )

@plugin('plan theme', canonical='plan theme')
def plan_theme_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    plan theme - Walks you through adding the theme for this week.
    Usage: "@bot plan theme"
    """
    return (
        "Plan Theme:\n\n"
        "To set this week's theme, please reply with a message in the following format:\n"
        "'Theme: <your theme description>'\n\n"
        "For example: 'Theme: Community Resilience and Unity'."
    )

@plugin('status', canonical='status')
def status_command(args: str, sender: str, state_machine: BotStateMachine, msg_timestamp: Optional[int] = None) -> str:
    """
    status - Displays system status including messages per hour, total messages sent, uptime, and overall system status.
    Usage: "@bot status"
    """
    uptime_seconds = get_uptime()
    uptime_hours = uptime_seconds / 3600 if uptime_seconds > 0 else 0
    mph = messages_sent if uptime_hours < 1 else messages_sent / uptime_hours
    return (
        f"Status:\n"
        f"Messages sent: {messages_sent}\n"
        f"Uptime: {uptime_seconds:.0f} seconds (~{uptime_hours:.2f} hours)\n"
        f"Messages per hour: {mph:.2f}\n"
        f"System: operational."
    )

# End of plugins/commands/system.py