"""
core/signal_cli_runner.py
-------------------------
Module for running signal-cli commands asynchronously with unified error handling.
Introduces a helper function to consolidate subprocess execution and error logging.
"""

import asyncio
import logging
from typing import List, Tuple
from core.config import SIGNAL_CLI_COMMAND, BOT_NUMBER

logger = logging.getLogger(__name__)

class SignalCLIError(Exception):
    """
    Custom exception for errors encountered when executing signal-cli commands.
    """
    pass

def _log_and_raise(func_name: str, error_msg: str, exception: Exception, full_args: List[str]) -> None:
    """
    Helper function to log an error message with context and raise a SignalCLIError.
    
    Args:
        func_name (str): The name of the function where the error occurred.
        error_msg (str): The error message to log.
        exception (Exception): The caught exception.
        full_args (List[str]): The full list of command-line arguments used.
    
    Raises:
        SignalCLIError: Always raised with the full contextual error message.
    """
    full_msg = f"[{func_name}] {error_msg} | Args: {full_args} | Exception: {exception}"
    logger.exception(full_msg)
    raise SignalCLIError(full_msg) from exception

async def _run_subprocess(full_args: List[str], timeout: int = 30) -> Tuple[bytes, bytes, int]:
    """
    Helper function to run a subprocess with unified error handling.
    
    Args:
        full_args (List[str]): The full list of command-line arguments.
        timeout (int): Timeout in seconds for process execution.
    
    Returns:
        Tuple[bytes, bytes, int]: A tuple containing stdout, stderr, and the return code.
    
    Raises:
        SignalCLIError: If any error occurs during subprocess execution.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            *full_args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except asyncio.TimeoutError as te:
            proc.kill()
            await proc.communicate()
            _log_and_raise("_run_subprocess", "Timed out waiting for process", te, full_args)
        return stdout, stderr, proc.returncode
    except OSError as ose:
        _log_and_raise("_run_subprocess", "OS error encountered", ose, full_args)
    except Exception as e:
        _log_and_raise("_run_subprocess", "Unexpected error encountered", e, full_args)

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
    stdout, stderr, returncode = await _run_subprocess(full_args, timeout=30)
    if returncode != 0:
        error_output = stderr.decode().strip() if stderr else ""
        _log_and_raise("async_run_signal_cli", f"Nonzero return code {returncode}. Error output: {error_output}", Exception("Nonzero return code"), full_args)
    return stdout.decode() if stdout else ""

# End of core/signal_cli_runner.py