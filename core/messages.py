#!/usr/bin/env python
"""
core/messages.py - Constants for user-facing messages.
This module centralizes all text strings used in responses for the Signal bot,
facilitating future updates and localization.
"""

# Registration Messages
REGISTRATION_WELCOME = "Starting registration flow. To register, please provide your full name or type 'skip' to remain anonymous."
ALREADY_REGISTERED = "You are registered as \"{name}\". Use command \"@bot edit\" to edit your name."

# Edit Messages
EDIT_PROMPT = "You are registered as \"{name}\". Type a new name or type \"skip\" to cancel editing."
EDIT_CANCELED = "Editing cancelled."
EDIT_CANCELED_WITH_NAME = "Editing cancelled. You remain registered as \"{name}\"."

# Deletion Messages
DELETION_PROMPT = "Would you like to delete your registration? Yes or No"
DELETION_CONFIRM = "Are you sure you want to delete your profile? Type 'DELETE' to remove your registration."
DELETION_CANCELED = "Deletion cancelled."
VOLUNTEER_DELETED = "Your registration has been deleted. Thank you."

# Other Messages
FEEDBACK_USAGE = "Usage: @bot feedback <Your feedback or report>"
NEW_VOLUNTEER_REGISTERED = "New volunteer '{name}' registered"
VOLUNTEER_UPDATED = "Volunteer '{name}' updated"
VOLUNTEER_CHECKED_IN = "Volunteer '{name}' has been checked in and is now available."

# Getting Started Message for New Users
GETTING_STARTED = "Hi! I don't recognize you yet. Try @bot register or type 'help' for instructions."

# End of core/messages.py