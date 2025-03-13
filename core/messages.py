"""
core/messages.py - Constants for user-facing messages.
This module centralizes all text strings used in responses for the Signal bot,
facilitating future updates and localization.
"""

REGISTRATION_PROMPT = "Welcome! Please respond with your first and last name to get registered. Or 'skip' to remain anonymous."
ALREADY_REGISTERED = "You are registered as \"{name}\". Use command \"@bot edit\" to edit your name."
EDIT_PROMPT = "You are registered as \"{name}\". Type a new name or type \"skip\" to cancel editing."
DELETION_PROMPT = "Would you like to delete your registration? Yes or No"
DELETION_CONFIRM_PROMPT = "Please respond with \"DELETE\" to delete your account."
DELETION_CANCELED = "Deletion cancelled."
EDIT_CANCELED = "Editing cancelled."
EDIT_CANCELED_WITH_NAME = "Editing cancelled. You remain registered as \"{name}\"."
FEEDBACK_USAGE = "Usage: @bot feedback <Your feedback or report>"
NEW_VOLUNTEER_REGISTERED = "New volunteer '{name}' registered"
VOLUNTEER_UPDATED = "Volunteer '{name}' updated"
VOLUNTEER_DELETED = "Your registration has been deleted. Thank you."
VOLUNTEER_CHECKED_IN = "Volunteer '{name}' has been checked in and is now available."

# New unified interactive prompts
REGISTRATION_WELCOME = "Welcome! To register, reply with your full name. Or type 'skip' to remain anonymous."
DELETION_CONFIRM = "Are you sure you want to delete your profile? Type 'YES' to confirm."
GETTING_STARTED = "Hi! I don’t recognize you yet. Try @bot register or type 'help' for instructions."

# End of core/messages.py