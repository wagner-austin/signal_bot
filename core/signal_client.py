"""
core/signal_client.py
--------------------
Encapsulates functions to interact with signal-cli for sending and receiving messages.
Improved error handling in subprocess calls.
"""

import subprocess
import re
import time
import logging
from core.config import BOT_NUMBER, SIGNAL_CLI_COMMAND
from managers.message_handler import handle_message
from core.message_parser import parse_message

def run_signal_cli(args):
    """Run signal-cli with given arguments, catching and logging any errors."""
    full_args = [SIGNAL_CLI_COMMAND, '-u', BOT_NUMBER] + args
    try:
        result = subprocess.run(full_args, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Signal-cli command failed: {e.cmd} with return code {e.returncode}. Output: {e.output}")
        return e
    except Exception as e:
        logging.error(f"Unexpected error while running signal-cli: {e}")
        return None

def send_message(to_number, message, group_id=None):
    """Send a message using signal-cli. If group_id is provided, send to the group chat."""
    if group_id:
        args = ['send', '-g', group_id, '-m', message]
        logging.info(f"Sent to group {group_id}: {message}")
    else:
        args = ['send', to_number, '-m', message]
        logging.info(f"Sent to {to_number}: {message}")
    run_signal_cli(args)

def receive_messages():
    """Retrieve incoming messages using signal-cli."""
    result = run_signal_cli(['receive'])
    if result and result.stdout:
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
        logging.info(f"Processing message:\n{message}\n")
        
        # Use the message parser to extract details.
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

# End of core/signal_client.py