"""
signal_cli_runner.py
---------------------
Module for running signal-cli commands asynchronously with unified error handling.
"""

import asyncio
import logging
from typing import List
from core.config import SIGNAL_CLI_COMMAND, BOT_NUMBER

logger = logging.getLogger(__name__)

class SignalCLIError(Exception):
    """
    Custom exception for errors encountered when executing signal-cli commands.
    """
    pass

def _log_and_raise(error_msg: str, exception: Exception, full_args: List[str]) -> None:
    """
    Helper function to log an error message and raise a SignalCLIError.
    
    Args:
        error_msg (str): The error message to log.
        exception (Exception): The caught exception.
        full_args (List[str]): The full list of command-line arguments used.
    """
    full_msg = f"{error_msg} Args: {full_args}. Exception: {exception}"
    logger.exception(full_msg)
    raise SignalCLIError(full_msg) from exception

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
            _log_and_raise("Signal CLI command timed out.", te, full_args)
        
        if proc.returncode != 0:
            error_output = stderr.decode().strip() if stderr else ""
            _log_and_raise(f"Signal-cli command failed with return code {proc.returncode}. Error: {error_output}", Exception("Nonzero return code"), full_args)
        
        return stdout.decode() if stdout else ""
    except OSError as ose:
        _log_and_raise("OS error while running async signal-cli", ose, full_args)
    except Exception as e:
        _log_and_raise("Unexpected error while running async signal-cli", e, full_args)

# End of core/signal_cli_runner.py