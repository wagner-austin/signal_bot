"""
core/message_parser.py
----------------------
Module for parsing incoming messages using regex extraction.
Centralizes common regex patterns for consistency.
"""

import re

# Define common regex patterns as constants
SENDER_PATTERN = r'\s*from:\s*(?:["“]?.+?["”]?\s+)?(\+\d+)'
BODY_PATTERN = r'Body:\s*(.+)'
TIMESTAMP_PATTERN = r'Timestamp:\s*(\d+)'
GROUP_INFO_PATTERN = r'Id:\s*([^\n]+)'

def parse_sender(message: str) -> str:
    """Extract and return the sender phone number from the message, or None if not found."""
    match = re.search(SENDER_PATTERN, message, re.IGNORECASE)
    return match.group(1) if match else None

def parse_body(message: str) -> str:
    """Extract and return the message body, or None if not found."""
    match = re.search(BODY_PATTERN, message)
    return match.group(1).strip() if match else None

def parse_timestamp(message: str) -> int:
    """Extract and return the message timestamp as an integer, or None if not found."""
    match = re.search(TIMESTAMP_PATTERN, message)
    return int(match.group(1)) if match else None

def parse_group_info(message: str) -> str:
    """Extract and return the group ID if available, else return None."""
    if "Group info:" in message:
        match = re.search(GROUP_INFO_PATTERN, message)
        return match.group(1).strip() if match else None
    return None

def parse_message(message: str) -> dict:
    """
    Parse the incoming message and return a dictionary with the following keys:
      - sender: The sender's phone number (str) or None.
      - body: The text body of the message (str) or None.
      - timestamp: The message timestamp (int) or None.
      - group_id: The group ID (str) if the message is from a group, else None.
    """
    return {
        'sender': parse_sender(message),
        'body': parse_body(message),
        'timestamp': parse_timestamp(message),
        'group_id': parse_group_info(message)
    }

# End of message_parser.py