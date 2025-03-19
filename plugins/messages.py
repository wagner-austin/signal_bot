"""
plugins/messages.py
-------------------
Brief summary: Centralized user-facing message constants for the Signal bot.
No usage (not a plugin).
"""

# Registration Messages
REGISTRATION_WELCOME = (
    "Please provide your first and last name or type 'skip' to remain anonymous."
)
REGISTRATION_COMPLETED_ANONYMOUS = (
    "Registration completed. You are now 'Anonymous'."
)
ALREADY_REGISTERED_WITH_INSTRUCTIONS = (
    'You are already registered as "{name}". '
    "Use @bot edit to change your name or @bot delete to remove your profile."
)

# New Volunteer or Update
NEW_VOLUNTEER_REGISTERED = 'New volunteer "{name}" has been registered.'
VOLUNTEER_UPDATED = 'Volunteer "{name}" updated.'

# Edit Messages
EDIT_PROMPT = "Starting edit flow. Provide your new name or 'skip' to cancel."
EDIT_CANCELED = "Editing cancelled."
EDIT_CANCELED_WITH_NAME = 'Editing cancelled. You remain "{name}".'
EDIT_NOT_REGISTERED = (
    "You are not registered, starting registration flow.\n"
    "Please provide your full name or type 'skip' for anonymous."
)

# Deletion Messages
DELETION_PROMPT = "Starting deletion flow. Type 'yes' to confirm or anything else to cancel."
DELETION_CANCELED = "Deletion cancelled."
NOTHING_TO_DELETE = "You are not currently registered; nothing to delete."
DELETION_CONFIRM = "Type 'delete' to confirm removing your registration."
DELETION_CONFIRM_PROFILE = "Type 'delete' to confirm removing your profile."
VOLUNTEER_DELETED = "Your registration has been deleted. Thank you."

# Flow Busy Message
FLOW_BUSY_MESSAGE = (
    "You have an active multi-step flow. Please finish or cancel it before issuing new commands."
)

# Check-in Message
VOLUNTEER_CHECKED_IN = "Volunteer has been checked in and is now available."

# Plugin/System Messages
BOT_SHUTDOWN = "Bot is shutting down."

# Info Messages
INFO_USAGE = "Usage: @bot info"
INFO_TEXT = (
    "50501 OC Grassroots Movement is dedicated to upholding the Constitution "
    "and ending executive overreach.\n\n"
    "We empower citizens to reclaim democracy and hold power accountable "
    "through peaceful, visible, and sustained engagement."
)

# Plugin management
HELP_UNKNOWN_SUBCOMMAND = "Unknown subcommand. Usage: @bot help"

# Template Plugin Messages
TEMPLATE_FLOW_STARTED = "Template flow 'template_flow' started."
TEMPLATE_FLOW_PAUSED = "Template flow 'template_flow' paused."
TEMPLATE_FLOW_RESUMED = "Template flow 'template_flow' resumed."
TEMPLATE_NO_FLOW_TO_RESUME = "No template flow to resume. Please start one first."

# Volunteer Status Messages
NO_VOLUNTEERS_FOUND = "No volunteers found."
VOLUNTEER_STATUS_TEMPLATE = "Name: {name}\nAvailable: {available}\n----------------------------------------"

# Flow Management Messages
FLOW_SWITCH_USAGE = "Usage: @bot flow switch <flow_name>"
FLOW_SWITCH_SUCCESS = "Switched to flow '{flow_name}'."
FLOW_PAUSE_NO_ACTIVE = "No active flow to pause."
FLOW_PAUSE_SUCCESS = "Paused flow '{flow_name}'."
FLOW_CREATE_USAGE = "Usage: @bot flow create <flow_name>"
FLOW_CREATE_SUCCESS = "Flow '{flow_name}' created and set active."

# Volunteer Error Messages
VOLUNTEER_NOT_FOUND = "Volunteer not found."
VOLUNTEER_NOT_REGISTERED = "You are not registered."
INVALID_AVAILABILITY_FORMAT = "Available must be 0 or 1."

# Internal error message
INTERNAL_ERROR = "An internal error occurred. Please try again later."

# Additional 'getting started' message used by process_incoming
GETTING_STARTED = (
    "Welcome to the 50501 OC bot! You can type '@bot help' to see available commands."
)

# **New** constant for deleted volunteers
NO_DELETED_VOLUNTEERS_FOUND = "No deleted volunteers found."

# End of plugins/messages.py