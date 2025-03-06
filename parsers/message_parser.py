"""
parsers/message_parser.py
-------------------------
Provides message parsing utilities that combine envelope parsing and command extraction.
Enhances input validation by sanitizing and validating commands.
Returns a structured ParsedMessage dataclass.
"""

from typing import Optional, Tuple
from dataclasses import dataclass
from parsers.envelope_parser import (
    parse_sender,
    parse_body,
    parse_timestamp,
    parse_group_info,
    parse_reply_id,
    parse_message_timestamp
)
import re

@dataclass
class ParsedMessage:
    sender: Optional[str]
    body: Optional[str]
    timestamp: Optional[int]
    group_id: Optional[str]
    reply_to: Optional[str]
    message_timestamp: Optional[str]
    command: Optional[str]
    args: Optional[str]

def _validate_command(command: str) -> bool:
    """
    Validate that the command consists only of allowed characters: lowercase letters, digits, and underscores.
    """
    return re.match(r'^[a-z0-9_]+$', command) is not None

def _parse_atbot_command(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse command and arguments from a message starting with '@bot'.
    
    Args:
        message (str): The normalized message string.
    
    Returns:
        Tuple[Optional[str], Optional[str]]: The command and arguments.
    """
    parts = message.split(" ", 2)
    if len(parts) < 2 or not parts[1].strip():
        return None, None
    command = parts[1].strip().lower()
    if not _validate_command(command):
        return None, None
    args = parts[2].strip() if len(parts) == 3 else ""
    return command, args

def _parse_default_command(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse command and arguments from a message without '@bot' prefix.
    
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

def parse_command_from_body(body: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the command and its arguments from the message body.
    
    Args:
        body (Optional[str]): The text body of the message.
        
    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the command in lowercase and its arguments,
                                               or (None, None) if parsing fails.
    """
    if not body:
        return None, None

    # Normalize whitespace.
    message = " ".join(body.strip().split())
    
    if message.lower().startswith("@bot"):
        return _parse_atbot_command(message)
    else:
        return _parse_default_command(message)

def parse_message(message: str) -> ParsedMessage:
    """
    Parse the incoming message and return a ParsedMessage dataclass with details.
    
    The returned ParsedMessage contains:
      - sender: The sender's phone number.
      - body: The text body of the message.
      - timestamp: The general timestamp of the message.
      - group_id: The group ID if available.
      - reply_to: The reply message ID if available from a quoted block.
      - message_timestamp: The original command's message timestamp.
      - command: The extracted command from the message body.
      - args: The arguments for the command, if any.
    
    Args:
        message (str): The full incoming message text.
    
    Returns:
        ParsedMessage: A dataclass instance with parsed message attributes.
    """
    sender = parse_sender(message)
    body = parse_body(message)
    timestamp = parse_timestamp(message)
    group_id = parse_group_info(message)
    reply_to = parse_reply_id(message)
    message_timestamp = parse_message_timestamp(message)
    command, args = parse_command_from_body(body)
    
    return ParsedMessage(
        sender=sender,
        body=body,
        timestamp=timestamp,
        group_id=group_id,
        reply_to=reply_to,
        message_timestamp=message_timestamp,
        command=command,
        args=args
    )

# End of parsers/message_parser.py
