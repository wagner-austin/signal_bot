#!/usr/bin/env python
"""
core/signal_cli_runner.py - Asynchronous runner for signal-cli commands with standardized error handling.
Provides functions to run signal-cli commands via subprocess, wrapping errors in a unified SignalCLIError.
"""

import asyncio
import logging
import re
from typing import List, Tuple, Optional
from core.config import SIGNAL_CLI_COMMAND, BOT_NUMBER
from core.constants import ALLOWED_CLI_FLAGS, DANGEROUS_PATTERN  # For any legacy usage
from core.validators import validate_cli_args, CLIValidationError  # Imported validation utilities

logger = logging.getLogger(__name__)

class SignalCLIError(Exception):
    """
    Custom exception for errors encountered when executing signal-cli commands.
    """
    pass

def _log_and_raise(func_name: str, error_msg: str, exception: Exception, full_args: List[str]) -> None:
    """
    core/signal_cli_runner.py - _log_and_raise: Logs an error message with context and raises a SignalCLIError with a standardized prefix.
    """
    full_msg = f"[{func_name}] SignalCLIError: {error_msg} | Args: {full_args} | Exception: {exception}"
    logger.exception(full_msg)
    raise SignalCLIError(full_msg) from exception

def async_error_handler(func):
    """
    async_error_handler - Decorator to standardize error handling in asynchronous subprocess calls.
    Catches exceptions, logs standardized error messages, and raises SignalCLIError.
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            full_args = args[0] if args else []
            _log_and_raise(func.__name__, "Async subprocess error", e, full_args)
    return wrapper

@async_error_handler
async def _run_subprocess(full_args: List[str], timeout: int = 30, input_data: Optional[str] = None) -> Tuple[bytes, bytes, int]:
    """
    _run_subprocess - Executes a subprocess command asynchronously.
    Uses the provided full_args and optional input_data (for STDIN) with a specified timeout.
    In case of timeout, kills the process and logs the error.
    
    Returns:
        Tuple[bytes, bytes, int]: stdout, stderr, and the return code.
    """
    proc = await asyncio.create_subprocess_exec(
        *full_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE if input_data is not None else None
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=input_data.encode() if input_data else None),
            timeout=timeout
        )
    except asyncio.TimeoutError as te:
        proc.kill()
        await proc.communicate()
        _log_and_raise("_run_subprocess", "Timed out waiting for process", te, full_args)
    return stdout, stderr, proc.returncode

async def async_run_signal_cli(args: List[str], stdin_input: Optional[str] = None) -> str:
    """
    async_run_signal_cli - Asynchronously run signal-cli with the given arguments.
    Validates allowed flags, constructs the full command, and returns the standard output.
    
    Args:
        args (List[str]): Command-line arguments.
        stdin_input (Optional[str]): Input text for STDIN (used with --message-from-stdin).
    
    Returns:
        str: The standard output from the signal-cli command.
        
    Raises:
        SignalCLIError: If an error occurs while running the signal-cli command.
    """
    try:
        validate_cli_args(args)
    except CLIValidationError as e:
        raise SignalCLIError(str(e))
    
    full_args = [SIGNAL_CLI_COMMAND, '-u', BOT_NUMBER] + args
    stdout, stderr, returncode = await _run_subprocess(full_args, timeout=30, input_data=stdin_input)
    if returncode != 0:
        error_output = stderr.decode().strip() if stderr else ""
        _log_and_raise("async_run_signal_cli", f"Nonzero return code {returncode}. Error output: {error_output}", Exception("Nonzero return code"), full_args)
    return stdout.decode() if stdout else ""

# End of core/signal_cli_runner.py