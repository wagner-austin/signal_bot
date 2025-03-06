"""
core/message_parser.py
----------------------
Module for parsing incoming messages using regex extraction.
Centralizes common regex patterns for consistency.
"""

import re
from typing import Optional, Dict, Any

# Matches lines starting with "from:" possibly including a quoted sender name,
# then captures an E.164 formatted phone number (a '+' followed by 1 to 15 digits).
SENDER_PATTERN: str = r'\s*from:\s*(?:["“]?.+?["”]?\s+)?(\+\d{1,15})'

# Matches "Body:" followed by any characters capturing the message text.
BODY_PATTERN: str = r'Body:\s*(.+)'

# Matches "Timestamp:" followed by one or more digits (the message timestamp).
TIMESTAMP_PATTERN: str = r'Timestamp:\s*(\d+)'

# Matches "Id:" followed by any characters (non-newline) capturing the group ID.
GROUP_INFO_PATTERN: str = r'Id:\s*([^\n]+)'

def parse_sender(message: str) -> Optional[str]:
    """
    Extract and return the sender phone number from the message.

    Args:
        message (str): The incoming message string.
        
    Returns:
        Optional[str]: The sender's phone number in E.164 format if found, otherwise None.
    """
    match = re.search(SENDER_PATTERN, message, re.IGNORECASE)
    return match.group(1) if match else None

def parse_body(message: str) -> Optional[str]:
    """
    Extract and return the message body.

    Args:
        message (str): The incoming message string.
        
    Returns:
        Optional[str]: The message body if found, otherwise None.
    """
    match = re.search(BODY_PATTERN, message)
    return match.group(1).strip() if match else None

def parse_timestamp(message: str) -> Optional[int]:
    """
    Extract and return the message timestamp as an integer.

    Args:
        message (str): The incoming message string.
        
    Returns:
        Optional[int]: The message timestamp if found, otherwise None.
    """
    match = re.search(TIMESTAMP_PATTERN, message)
    return int(match.group(1)) if match else None

def parse_group_info(message: str) -> Optional[str]:
    """
    Extract and return the group ID if available.

    Args:
        message (str): The incoming message string.
        
    Returns:
        Optional[str]: The group ID if found, otherwise None.
    """
    if "Group info:" in message:
        match = re.search(GROUP_INFO_PATTERN, message)
        return match.group(1).strip() if match else None
    return None

def parse_message(message: str) -> Dict[str, Optional[Any]]:
    """
    Parse the incoming message and return a dictionary with details.

    Args:
        message (str): The full incoming message text.
        
    Returns:
        Dict[str, Optional[Any]]: A dictionary containing:
            - 'sender': The sender's phone number (str) or None.
            - 'body': The text body of the message (str) or None.
            - 'timestamp': The message timestamp (int) or None.
            - 'group_id': The group ID (str) if the message is from a group, else None.
    """
    return {
        'sender': parse_sender(message),
        'body': parse_body(message),
        'timestamp': parse_timestamp(message),
        'group_id': parse_group_info(message)
    }

# End of core/message_parser.py