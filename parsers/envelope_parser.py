"""
envelope_parser.py
---------------------
Provides envelope parsing utilities using regex extraction.
Handles extraction of sender, body, timestamp, group info, reply ID, and message timestamp from incoming messages.
"""

import re
from typing import Optional

# Regex patterns for envelope parsing.
SENDER_PATTERN: str = r'\s*from:\s*(?:["“]?.+?["”]?\s+)?(\+\d{1,15})'
BODY_PATTERN: str = r'Body:\s*(.+)'
TIMESTAMP_PATTERN: str = r'Timestamp:\s*(\d+)'
GROUP_INFO_PATTERN: str = r'Id:\s*([^\n]+)'
REPLY_PATTERN: str = r'Quote:.*?Id:\s*([^\n]+)'
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

# End of parsers/envelope_parser.py