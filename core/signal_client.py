"""
core/signal_client.py
--------------------
Encapsulates functions to interact with signal-cli for sending and receiving messages.
Modified to use a dedicated message parser module for regex extraction.
"""

import subprocess
import re
import time
from core.config import BOT_NUMBER
from managers.message_handler import handle_message
from core.message_parser import parse_message  # Newly added import

def run_signal_cli(args):
    """Run signal-cli with given arguments."""
    full_args = ['signal-cli.bat', '-u', BOT_NUMBER] + args
    result = subprocess.run(full_args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result

def send_message(to_number, message, group_id=None):
    """Send a message using signal-cli. If group_id is provided, send to the group chat."""
    if group_id:
        args = ['send', '-g', group_id, '-m', message]
        print(f"Sent to group {group_id}: {message}")
    else:
        args = ['send', to_number, '-m', message]
        print(f"Sent to {to_number}: {message}")
    run_signal_cli(args)

def receive_messages():
    """Retrieve incoming messages using signal-cli."""
    result = run_signal_cli(['receive'])
    if result.stdout:
        messages = result.stdout.strip().split('\nEnvelope')
        return messages
    return []

def process_incoming():
    """
    Process each incoming message, dispatch commands, and send responses.
    Skips system messages (e.g. typing notifications, receipts) which lack a 'Body:'.
    Modified to use the dedicated message parser.
    """
    messages = receive_messages()
    for message in messages:
        print(f"Processing message:\n{message}\n")
        
        # Use the new message parser to extract details.
        parsed = parse_message(message)
        sender = parsed.get('sender')
        body = parsed.get('body')
        msg_timestamp = parsed.get('timestamp')
        group_id = parsed.get('group_id')

        # Skip if required fields are missing.
        if not sender or not body:
            continue

        # Process the message using the existing handler.
        response = handle_message(body, sender, msg_timestamp=msg_timestamp)
        if response:
            send_message(sender, response, group_id=group_id)
