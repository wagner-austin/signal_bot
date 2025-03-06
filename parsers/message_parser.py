"""
parsers/message_parser.py
-------------------------
Provides message parsing utilities that combine envelope parsing and command extraction.
Enhances input validation by sanitizing and validating commands.
Uses a dedicated module for command extraction to simplify modifications.
Returns a structured ParsedMessage dataclass.
"""

from typing import Optional
from dataclasses import dataclass
from parsers.envelope_parser import (
    parse_sender,
    parse_body,
    parse_timestamp,
    parse_group_info,
    parse_reply_id,
    parse_message_timestamp
)
from parsers.command_extractor import parse_command_from_body  # Import command extraction logic

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
    
    # Determine if this is a group message (group_id is present).
    is_group = group_id is not None
    command, args = parse_command_from_body(body, is_group=is_group)
    
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