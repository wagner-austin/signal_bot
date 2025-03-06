"""
parsers/message_parser.py
-------------------------
Provides message parsing utilities using regex extraction.
Centralizes common regex patterns for consistency in parsing incoming messages.
"""

import re
from typing import Optional, Dict, Any

# Pattern to match sender information.
SENDER_PATTERN: str = r'\s*from:\s*(?:["“]?.+?["”]?\s+)?(\+\d{1,15})'

# Pattern to match the message body.
BODY_PATTERN: str = r'Body:\s*(.+)'

# Pattern to match the general timestamp.
TIMESTAMP_PATTERN: str = r'Timestamp:\s*(\d+)'

# Pattern to match group information.
GROUP_INFO_PATTERN: str = r'Id:\s*([^\n]+)'

# Pattern to match a quoted reply (if any).
REPLY_PATTERN: str = r'Quote:.*?Id:\s*([^\n]+)'

# New pattern to specifically capture the original command's message timestamp.
MESSAGE_TIMESTAMP_PATTERN: str = r'Message timestamp:\s*(\d+)'

def parse_sender(message: str) -> Optional[str]:
    """
    Extract and return the sender phone number from the message.
    """
    match = re.search(SENDER_PATTERN, message, re.IGNORECASE)
    return match.group(1) if match else None

def parse_body(message: str) -> Optional[str]:
    """
    Extract and return the message body.
    """
    match = re.search(BODY_PATTERN, message)
    return match.group(1).strip() if match else None

def parse_timestamp(message: str) -> Optional[int]:
    """
    Extract and return the general message timestamp as an integer.
    """
    match = re.search(TIMESTAMP_PATTERN, message)
    return int(match.group(1)) if match else None

def parse_group_info(message: str) -> Optional[str]:
    """
    Extract and return the group ID if available.
    """
    if "Group info:" in message:
        match = re.search(GROUP_INFO_PATTERN, message)
        return match.group(1).strip() if match else None
    return None

def parse_reply_id(message: str) -> Optional[str]:
    """
    Extract the reply message ID from a quoted message if present.
    
    Parameters:
        message (str): The full incoming message text.
    
    Returns:
        Optional[str]: The reply message ID if found, otherwise None.
    """
    match = re.search(REPLY_PATTERN, message, re.DOTALL)
    return match.group(1).strip() if match else None

def parse_message_timestamp(message: str) -> Optional[str]:
    """
    Extract the original command's message timestamp from the message if present.
    
    Parameters:
        message (str): The full incoming message text.
    
    Returns:
        Optional[str]: The message timestamp as a string if found, otherwise None.
    """
    match = re.search(MESSAGE_TIMESTAMP_PATTERN, message)
    return match.group(1).strip() if match else None

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
    
    Parameters:
        message (str): The full incoming message text.
    
    Returns:
        Dict[str, Optional[Any]]: A dictionary containing message details.
    """
    return {
        'sender': parse_sender(message),
        'body': parse_body(message),
        'timestamp': parse_timestamp(message),
        'group_id': parse_group_info(message),
        'reply_to': parse_reply_id(message),
        'message_timestamp': parse_message_timestamp(message)
    }

# End of parsers/message_parser.py
