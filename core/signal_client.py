"""
core/signal_client.py
--------------------
Encapsulates functions to interact with signal-cli for sending and receiving messages.
Improved error handling and asynchronous subprocess handling, and robust message parsing.
"""

import asyncio
import re
import logging
from types import SimpleNamespace
from typing import List, Optional
from core.config import BOT_NUMBER, SIGNAL_CLI_COMMAND
from managers.message_handler import handle_message
from core.message_parser import parse_message

class SignalCLIError(Exception):
    """
    Custom exception for errors encountered when executing signal-cli commands.
    """
    pass

async def async_run_signal_cli(args: List[str]) -> SimpleNamespace:
    """
    Asynchronously run signal-cli with given arguments, catching and logging any errors.

    Args:
        args (List[str]): List of command-line arguments for signal-cli.

    Returns:
        SimpleNamespace: An object with attributes stdout, stderr, returncode, and args.

    Raises:
        SignalCLIError: If an error occurs while running the signal-cli command.
    """
    full_args = [SIGNAL_CLI_COMMAND, '-u', BOT_NUMBER] + args
    try:
        process = await asyncio.create_subprocess_exec(
            *full_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=30)
        except asyncio.TimeoutError:
            process.kill()
            await process.communicate()
            raise SignalCLIError("signal-cli command timed out.")
        
        stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
        stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""
        
        if process.returncode != 0:
            logging.error(f"Signal-cli command failed: {full_args} with return code {process.returncode}. Stderr: {stderr}")
            raise SignalCLIError(f"Command {full_args} failed with return code {process.returncode}. Stderr: {stderr}")
        
        return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=process.returncode, args=full_args)
    except Exception as e:
        logging.error(f"Unexpected error while running signal-cli: {e}")
        raise SignalCLIError(f"Unexpected error: {e}") from e

async def send_message(to_number: str, message: str, group_id: Optional[str] = None) -> None:
    """
    Asynchronously send a message using signal-cli. If group_id is provided, send to the group chat.

    Args:
        to_number (str): The recipient's phone number.
        message (str): The message to send.
        group_id (Optional[str]): The group ID if sending to a group chat.
    """
    if group_id:
        args = ['send', '-g', group_id, '-m', message]
        logging.info(f"Sent to group {group_id}: {message}")
    else:
        args = ['send', to_number, '-m', message]
        logging.info(f"Sent to {to_number}: {message}")
    await async_run_signal_cli(args)

async def receive_messages() -> List[str]:
    """
    Asynchronously retrieve incoming messages using signal-cli with improved delimiter parsing.

    Returns:
        List[str]: A list of raw message strings.
    """
    result = await async_run_signal_cli(['receive'])
    if result and result.stdout:
        # Use regex to robustly extract all envelope blocks.
        messages = re.findall(r'(Envelope.*?)(?=Envelope|$)', result.stdout, flags=re.DOTALL)
        return messages
    return []

async def process_incoming() -> None:
    """
    Asynchronously process each incoming message, dispatch commands, and send responses.
    Skips system messages (e.g. typing notifications, receipts) which lack a 'Body:'.
    Modified to use the dedicated message parser and asynchronous subprocess handling.
    """
    messages = await receive_messages()
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
            await send_message(sender, response, group_id=group_id)

# End of core/signal_client.py