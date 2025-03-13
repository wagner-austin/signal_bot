#!/usr/bin/env python
"""
core/plugin_usage.py - Centralized usage strings for plugin commands.
Defines short usage snippets for all commands including interactive (multi-step) flows.
"""

USAGE_DBBACKUP = (
    "Usage:\n"
    "  dbbackup create\n"
    "  dbbackup list\n"
    "  dbbackup restore <filename>"
)

USAGE_DBSTATS = "Usage: @bot dbstats"

USAGE_DONATE = (
    "Usage:\n"
    "  @bot donate <amount> <description>\n"
    "  @bot donate in-kind <description>\n"
    "  @bot donate register <method> [<description>]"
)

USAGE_PLAN_EVENT = (
    "Usage:\n"
    "  plan event Title: <title>, Date: <date>, Time: <time>, Location: <loc>, Description: <desc>\n"
    "  Or type 'skip' to cancel."
)

USAGE_PLAN_EVENT_PARTIAL = (
    "Incomplete event details. Please provide missing fields (e.g., location: MyLocation, date: YYYY-MM-DD) to continue."
)

USAGE_EDIT_EVENT = "Usage: @bot edit event EventID: <id>, <key>:<value>, ..."

USAGE_REMOVE_EVENT = "Usage: @bot remove event EventID: <id> or Title: <event title>"

USAGE_HELP = "Usage: @bot help"

USAGE_WEEKLY_UPDATE = "Usage: @bot weekly update"

USAGE_POLITICAL = "Usage: @bot political"

USAGE_RESOURCE = (
    "Usage:\n"
    "  @bot resource add <category> <url> [title?]\n"
    "  @bot resource list [<category>]\n"
    "  @bot resource remove <resource_id>"
)

USAGE_ASSIGN = "Usage: @bot assign <Skill Name>"

USAGE_TEST = "Usage: @bot test"

USAGE_SHUTDOWN = "Usage: @bot shutdown"

USAGE_INFO = "Usage: @bot info"

USAGE_WEEKLY_UPDATE_SYSTEM = "Usage: @bot weekly update"

USAGE_THEME_SYSTEM = "Usage: @bot theme"

USAGE_ROLE = (
    "Usage:\n"
    "  @bot role list\n"
    "  @bot role set <role>\n"
    "  @bot role switch <role>\n"
    "  @bot role unassign"
)

USAGE_ROLE_SET = "Usage: @bot role set <role>"

USAGE_ROLE_SWITCH = "Usage: @bot role switch <role>"

USAGE_ADD_SPEAKER = "Usage: @bot add speaker [Event: <title>,] Name: <speaker name>, Topic: <speaker topic>"

USAGE_REMOVE_SPEAKER = "Usage: @bot remove speaker [Event: <title>,] Name: <speaker name>"

USAGE_TASK_ADD = "Usage: @bot task add <description>"

USAGE_TASK_LIST = "Usage: @bot task list"

USAGE_TASK_ASSIGN = "Usage: @bot task assign <task_id> <volunteer_display_name>"

USAGE_TASK_CLOSE = "Usage: @bot task close <task_id>"

USAGE_THEME = "Usage: @bot theme"

USAGE_PLAN_THEME = "Usage: @bot plan theme"

USAGE_VOLUNTEER_STATUS = "Usage: @bot volunteer status"

USAGE_REGISTER = "Usage: @bot register <your full name> (or leave blank to be prompted)"

USAGE_REGISTER_PARTIAL = (
    "Incomplete registration. Please provide your full name (first and last) or type 'skip' to remain anonymous."
)

USAGE_EDIT = "Usage: @bot edit <new name> (or type 'skip' to cancel editing)"

USAGE_DELETE = "Usage: @bot delete (follow prompts to confirm deletion)"

USAGE_SKILLS = "Usage: @bot skills"

USAGE_FIND = "Usage: @bot find <skill1> <skill2> ..."

USAGE_ADD_SKILLS = "Usage: @bot add skills <skill1>, <skill2>, ..."

# End of core/plugin_usage.py