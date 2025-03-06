"""
signal_client.py
--------------------
Encapsulates functions to interact with signal-cli for sending and receiving messages.
Improved asynchronous handling with asyncio subprocess and robust message delimiter parsing.
Now supports sending direct replies by quoting the original command message in group chats only.
"""

import asyncio
import re
import logging
from typing import List, Optional
from core.config import BOT_NUMBER, SIGNAL_CLI_COMMAND
from managers.message_handler import handle_message
from parsers.message_parser import parse_message

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
        except asyncio.TimeoutError as te:
            proc.kill()
            await proc.communicate()
            logger.exception(f"Signal CLI command timed out. Args: {full_args}")
            raise SignalCLIError(f"Signal CLI command timed out. Args: {full_args}") from te
        
        if proc.returncode != 0:
            error_output = stderr.decode().strip() if stderr else ""
            logger.error(f"Signal-cli command failed: {full_args} with return code {proc.returncode}. Error: {error_output}")
            raise SignalCLIError(f"Signal-cli command failed with return code {proc.returncode}. Args: {full_args}")
        
        return stdout.decode() if stdout else ""
    except OSError as ose:
        logger.exception(f"OS error while running async signal-cli with args {full_args}: {ose}")
        raise SignalCLIError(f"OS error while running signal-cli: {ose}") from ose
    except Exception as e:
        logger.exception(f"Unexpected error while running async signal-cli with args {full_args}: {e}")
        raise SignalCLIError(f"Unexpected error: {e}") from e

async def send_message(
    to_number: str,
    message: str,
    group_id: Optional[str] = None,
    reply_quote_author: Optional[str] = None,
    reply_quote_timestamp: Optional[str] = None,
    reply_quote_message: Optional[str] = None
) -> None:
    """
    Asynchronously send a message using signal-cli.
    
    For group chats, the message will include the original command text as a direct reply.
    For individual chats, the message will be sent without the original command text.
    
    Args:
        to_number (str): The recipient's phone number.
        message (str): The message to send.
        group_id (Optional[str]): The group ID if sending to a group chat.
        reply_quote_author (Optional[str]): The author of the original message to quote.
        reply_quote_timestamp (Optional[str]): The timestamp of the original message.
        reply_quote_message (Optional[str]): The text of the original message.
    """
    if group_id:
        args = ['send', '-g', group_id]
    else:
        args = ['send', to_number]
    
    # For group chats, include direct reply quoting flags if available.
    if group_id and reply_quote_author and reply_quote_timestamp and reply_quote_message:
        args.extend([
            '--quote-author', reply_quote_author,
            '--quote-timestamp', reply_quote_timestamp,
            '--quote-message', reply_quote_message
        ])
    
    args.extend(['-m', message])
    
    if group_id:
        logger.info(f"Sent to group {group_id}: {message} (replying to message by {reply_quote_author})")
    else:
        logger.info(f"Sent to {to_number}: {message} (no direct reply quoting for individual chat)")
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
    For group chats, sends the response as a direct reply using the original command message's details.
    For individual chats, sends the response without direct reply quoting.
    """
    messages = await receive_messages()
    for message in messages:
        logger.info(f"Processing message:\n{message}\n")
        
        parsed = parse_message(message)
        sender = parsed.get('sender')
        body = parsed.get('body')
        msg_timestamp = parsed.get('timestamp')
        group_id = parsed.get('group_id')
        # For direct reply, use the original command's message details if available.
        quote_timestamp = str(parsed.get('message_timestamp') or msg_timestamp) if msg_timestamp else None
        quote_author = sender  # The command's sender becomes the quoted author.
        quote_message = body  # The body of the command message.
        
        if not sender or not body:
            continue
        
        response = handle_message(body, sender, msg_timestamp=msg_timestamp)
        if response:
            await send_message(
                sender,
                response,
                group_id=group_id,
                reply_quote_author=quote_author,
                reply_quote_timestamp=quote_timestamp,
                reply_quote_message=quote_message
            )

# End of core/signal_client.py