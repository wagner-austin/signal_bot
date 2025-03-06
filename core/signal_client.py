"""
core/signal_client.py
--------------------
Encapsulates functions to interact with signal-cli for sending and receiving messages.
Improved asynchronous handling with asyncio subprocess and robust message delimiter parsing.
Also uses a centralized logger for consistent logging.
"""

import asyncio
import re
import logging
from typing import List, Optional
from core.config import BOT_NUMBER, SIGNAL_CLI_COMMAND
from managers.message_handler import handle_message
from core.message_parser import parse_message

logger = logging.getLogger(__name__)

class SignalCLIError(Exception):
    """
    Custom exception for errors encountered when executing signal-cli commands.
    """
    pass

async def async_run_signal_cli(args: List[str]) -> str:
    """
    Asynchronously run signal-cli with given arguments.
    
    Args:
        args (List[str]): List of command-line arguments for signal-cli.
    
    Returns:
        str: The standard output from the signal-cli command.
        
    Raises:
        SignalCLIError: If an error occurs while running the signal-cli command.
    """
    full_args = [SIGNAL_CLI_COMMAND, '-u', BOT_NUMBER] + args
    try:
        proc = await asyncio.create_subprocess_exec(
            *full_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            raise SignalCLIError(f"Signal CLI command timed out. Args: {full_args}")
        
        if proc.returncode != 0:
            error_output = stderr.decode().strip() if stderr else ""
            logger.error(f"Signal-cli command failed: {full_args} with return code {proc.returncode}. Error: {error_output}")
            raise SignalCLIError(f"Signal-cli command failed with return code {proc.returncode}. Args: {full_args}")
        
        return stdout.decode() if stdout else ""
    except Exception as e:
        logger.error(f"Unexpected error while running async signal-cli with args {full_args}: {e}")
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
        logger.info(f"Sent to group {group_id}: {message}")
    else:
        args = ['send', to_number, '-m', message]
        logger.info(f"Sent to {to_number}: {message}")
    await async_run_signal_cli(args)

async def receive_messages() -> List[str]:
    """
    Asynchronously retrieve incoming messages using signal-cli.
    
    Returns:
        List[str]: A list of raw message strings.
    """
    output = await async_run_signal_cli(['receive'])
    if output:
        # Use regex splitting with a lookahead to capture each envelope robustly.
        messages = re.split(r'\n(?=Envelope)', output.strip())
        return messages
    return []

async def process_incoming() -> None:
    """
    Asynchronously process each incoming message, dispatch commands, and send responses.
    Skips system messages (e.g. typing notifications, receipts) which lack a 'Body:'.
    Modified to use the dedicated message parser.
    """
    messages = await receive_messages()
    for message in messages:
        logger.info(f"Processing message:\n{message}\n")
        
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