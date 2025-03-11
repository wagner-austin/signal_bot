#!/usr/bin/env python
"""
parsers/plugin_arg_parser.py - Unified plugin argument parser.
Provides a centralized function for parsing plugin command arguments using Pydantic models.
Defines a custom PluginArgError exception for uniform error handling.
"""

try:
    from pydantic import BaseModel, ValidationError
except ModuleNotFoundError:
    # Minimal fallback implementations if pydantic is not installed.
    class BaseModel:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
        @classmethod
        def parse_obj(cls, obj):
            return cls(**obj)
    class ValidationError(Exception):
        pass

class PluginArgError(Exception):
    """Custom exception raised when plugin argument parsing fails."""
    pass

def parse_plugin_args(raw_args: str, model: type[BaseModel]) -> BaseModel:
    """
    Parses raw plugin arguments into a typed Pydantic model.

    Args:
        raw_args (str): The raw argument string.
        model (type[BaseModel]): The Pydantic model class to parse the arguments.

    Returns:
        An instance of the provided Pydantic model.

    Raises:
        PluginArgError: If argument parsing fails.
    """
    try:
        arg_dict = {}
        if raw_args.strip():
            pairs = [pair.strip() for pair in raw_args.split(",") if pair.strip()]
            for pair in pairs:
                if ":" not in pair:
                    raise PluginArgError(f"Argument '{pair}' is not a valid key:value pair.")
                key, value = pair.split(":", 1)
                arg_dict[key.strip()] = value.strip()
        return model.parse_obj(arg_dict)
    except ValidationError as ve:
        raise PluginArgError(str(ve))

# End of parsers/plugin_arg_parser.py