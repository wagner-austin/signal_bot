"""
parsers/command_extractor.py
----------------------------
Module dedicated to extracting commands and their arguments from a message body.
Contains functions for command validation, prefix stripping, and splitting.
"""

import re
from typing import Optional, Tuple

def _validate_command(command: str) -> bool:
    """
    Validate that the command consists only of allowed characters: lowercase letters, digits, and underscores.
    """
    return re.match(r'^[a-z0-9_]+$', command) is not None

def _parse_default_command(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse command and arguments from a message without any prefix.

    Args:
        message (str): The normalized message string.

    Returns:
        Tuple[Optional[str], Optional[str]]: The command and arguments.
    """
    parts = message.split(" ", 1)
    command = parts[0].strip().lower()
    if not _validate_command(command):
        return None, None
    args = parts[1].strip() if len(parts) == 2 else ""
    return command, args

def parse_command_from_body(body: Optional[str], is_group: bool = False) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the command and its arguments from the message body, taking into account whether
    the message is from a group chat or a private chat.

    In a group chat (is_group=True), the message must start with one of the allowed prefixes.
    In a private chat (is_group=False), the prefix is optional.

    Allowed prefixes (case-insensitive):
      - "@bot"
      - "@50501oc bot"

    Additionally, if the message begins with an object replacement character (U+FFFC),
    it is replaced with "@50501oc bot".

    Args:
        body (Optional[str]): The text body of the message.
        is_group (bool): True if the message is from a group chat, False if private.

    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the command in lowercase and its arguments,
                                               or (None, None) if parsing fails.
    """
    if not body:
        return None, None

    # Normalize whitespace.
    message = " ".join(body.strip().split())

    # If message starts with the object replacement character, replace it with "@50501oc bot"
    if message and message[0] == "\uFFFC":
        message = "@50501oc bot" + message[1:]
        message = message.strip()

    allowed_prefixes = ["@bot", "@50501oc bot"]

    if is_group:
        # In group chats, require one of the allowed prefixes.
        found_prefix = None
        for prefix in allowed_prefixes:
            if message.lower().startswith(prefix):
                found_prefix = prefix
                break
        if found_prefix:
            message = message[len(found_prefix):].strip()
            return _parse_default_command(message)
        else:
            return None, None
    else:
        # In private chats, the prefix is optional.
        for prefix in allowed_prefixes:
            if message.lower().startswith(prefix):
                message = message[len(prefix):].strip()
                break
        return _parse_default_command(message)

# End of parsers/command_extractor.py