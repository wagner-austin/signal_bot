"""
message_parser.py
-------------------------
Provides message parsing utilities that combine envelope parsing and command extraction.
Utilizes functions from envelope_parser.py for extracting envelope details and also extracts command and arguments.
"""

from typing import Optional, Dict, Any, Tuple
from parsers.envelope_parser import (
    parse_sender,
    parse_body,
    parse_timestamp,
    parse_group_info,
    parse_reply_id,
    parse_message_timestamp
)
import re

def parse_command_from_body(body: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract the command and its arguments from the message body.
    
    Parameters:
        body (Optional[str]): The text body of the message.
        
    Returns:
        Tuple[Optional[str], Optional[str]]: A tuple containing the command in lowercase and its arguments,
                                               or (None, None) if parsing fails.
    """
    if not body:
        return None, None

    # Normalize whitespace.
    message = " ".join(body.strip().split())
    
    # Check if the message starts with the '@bot' prefix.
    if message.lower().startswith("@bot"):
        parts = message.split(" ", 2)
        if len(parts) < 2 or not parts[1].strip():
            return None, None
        command = parts[1].strip().lower()
        args = parts[2].strip() if len(parts) == 3 else ""
        return command, args

    # Otherwise, assume the first word is the command.
    parts = message.split(" ", 1)
    command = parts[0].strip().lower()
    args = parts[1].strip() if len(parts) == 2 else ""
    if not command:
        return None, None
    return command, args

def parse_message(message: str) -> Dict[str, Optional[Any]]:
    """
    Parse the incoming message and return a dictionary with details.
    
    The returned dictionary contains:
      - 'sender': The sender's phone number.
      - 'body': The text body of the message.
      - 'timestamp': The general timestamp of the message.
      - 'group_id': The group ID if available.
      - 'reply_to': The reply message ID if available from a quoted block.
      - 'message_timestamp': The original command's message timestamp.
      - 'command': The extracted command from the message body.
      - 'args': The arguments for the command, if any.
    
    Parameters:
        message (str): The full incoming message text.
    
    Returns:
        Dict[str, Optional[Any]]: A dictionary containing message details.
    """
    sender = parse_sender(message)
    body = parse_body(message)
    timestamp = parse_timestamp(message)
    group_id = parse_group_info(message)
    reply_to = parse_reply_id(message)
    message_timestamp = parse_message_timestamp(message)
    command, args = parse_command_from_body(body)
    return {
        'sender': sender,
        'body': body,
        'timestamp': timestamp,
        'group_id': group_id,
        'reply_to': reply_to,
        'message_timestamp': message_timestamp,
        'command': command,
        'args': args
    }

# End of parsers/message_parser.py