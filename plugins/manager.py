"""
plugins/manager.py - Unified plugin manager with alias support.
Handles registration, loading, and retrieval of plugins using centralized and standardized alias definitions.
"""

import sys
import importlib
import pkgutil
from typing import Callable, Any, Optional, Dict, List, Union

# Registry: key = canonical command, value = dict with function, aliases, and help_visible flag.
plugin_registry: Dict[str, Dict[str, Any]] = {}
# Alias mapping: key = alias (normalized), value = canonical command.
alias_mapping: Dict[str, str] = {}

def normalize_alias(alias: str) -> str:
    """
    Normalize an alias to a standardized format: lowercased and stripped.
    """
    return alias.strip().lower()

def plugin(commands: Union[str, List[str]], canonical: Optional[str] = None, help_visible: bool = True) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to register a function as a command plugin with one or more aliases.
    Optionally specify a canonical name that will be used in help listings.
    """
    if isinstance(commands, str):
        commands = [commands]
    
    normalized_commands = [normalize_alias(cmd) for cmd in commands]
    
    if canonical is None:
        canonical = normalized_commands[0]
    else:
        canonical = normalize_alias(canonical)
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Register canonical command with its aliases and help visibility.
        plugin_registry[canonical] = {
            "function": func,
            "aliases": normalized_commands,
            "help_visible": help_visible
        }
        # Map each alias to the canonical command.
        for alias in normalized_commands:
            if alias in alias_mapping and alias_mapping[alias] != canonical:
                raise ValueError(f"Duplicate alias detected: '{alias}' is already assigned to '{alias_mapping[alias]}'.")
            alias_mapping[alias] = canonical
        return func
    return decorator

def get_plugin(command: str) -> Optional[Callable[..., Any]]:
    """
    Retrieve the plugin function for a given command by looking up the alias mapping.
    """
    canonical = alias_mapping.get(normalize_alias(command))
    if canonical:
        entry = plugin_registry.get(canonical)
        if entry:
            return entry["function"]
    return None

def get_all_plugins() -> Dict[str, Dict[str, Any]]:
    """
    Return all registered plugins as a dictionary keyed by canonical command names.
    """
    return plugin_registry

def clear_plugins() -> None:
    """
    Clear all registered plugins and alias mappings.
    """
    plugin_registry.clear()
    alias_mapping.clear()

def load_plugins() -> None:
    """
    Automatically import (or reload) all plugin modules in the 'plugins.commands'
    package to register all plugins.
    """
    import plugins.commands  # Ensure the package is imported.
    module_names = {module_info.name for module_info in pkgutil.walk_packages(plugins.commands.__path__, plugins.commands.__name__ + ".")}
    for module_name in module_names:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

def reload_plugins() -> None:
    """
    Reload all plugin modules dynamically by clearing the plugin registry and re-importing modules.
    """
    clear_plugins()
    load_plugins()

# End of plugins/manager.py