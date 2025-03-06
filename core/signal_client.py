"""
core/signal_client.py
---------------------
Encapsulates functions to interact with signal-cli for sending and receiving messages.
Improved asynchronous handling by refactoring message processing into smaller helper functions.
"""

import asyncio
import re
import logging
from typing import List, Optional, Tuple
from core.signal_cli_runner import async_run_signal_cli, SignalCLIError
from managers.message_handler import handle_message
from parsers.message_parser import parse_message, ParsedMessage

logger = logging.getLogger(__name__)

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

def _get_quote_details(parsed: ParsedMessage) -> Tuple[Optional[str], str, str]:
    """
    Extract quoting details from a parsed message.
    
    Args:
        parsed (ParsedMessage): The parsed message.
    
    Returns:
        Tuple containing:
         - quote_timestamp: Original command's timestamp (as string), if available.
         - quote_author: The sender's identifier.
         - quote_message: The message body.
    """
    msg_timestamp = parsed.timestamp
    quote_timestamp = str(parsed.message_timestamp or msg_timestamp) if msg_timestamp else None
    quote_author = parsed.sender
    quote_message = parsed.body
    return quote_timestamp, quote_author, quote_message

async def _dispatch_message(response: str, parsed: ParsedMessage, quote_details: Tuple[Optional[str], str, str]) -> None:
    """
    Dispatch the response message by calling send_message with appropriate quoting details.
    
    Args:
        response (str): The response message to send.
        parsed (ParsedMessage): The parsed incoming message.
        quote_details (Tuple): A tuple containing quote_timestamp, quote_author, and quote_message.
    """
    await send_message(
        parsed.sender,
        response,
        group_id=parsed.group_id,
        reply_quote_author=quote_details[1],
        reply_quote_timestamp=quote_details[0],
        reply_quote_message=quote_details[2]
    )

async def process_incoming(state_machine) -> int:
    """
    Asynchronously process each incoming message, dispatch commands, and send responses.
    
    This function uses helper functions to handle quoting and message dispatching, improving readability.
    Returns the count of processed messages to help adjust the polling interval.
    
    Args:
        state_machine: Instance of BotStateMachine for dependency injection.
    
    Returns:
        int: Number of processed messages.
    """
    messages = await receive_messages()
    processed_count = 0
    for message in messages:
        logger.info(f"Processing message:\n{message}\n")
        
        parsed = parse_message(message)
        if not parsed.sender or not parsed.body:
            continue
        
        processed_count += 1
        quote_details = _get_quote_details(parsed)
        response = handle_message(parsed, parsed.sender, state_machine, msg_timestamp=parsed.timestamp)
        if response:
            await _dispatch_message(response, parsed, quote_details)
    return processed_count

# End of core/signal_client.py