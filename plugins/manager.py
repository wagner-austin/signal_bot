"""
plugins/manager.py - Unified plugin manager with alias support.
Handles registration, loading, and retrieval of plugins using canonical names and alias mapping.
"""

import sys
import importlib
import pkgutil
from typing import Callable, Any, Optional, Dict, List, Union

# Registry: key = canonical command, value = dict with function, aliases, and help_visible flag.
plugin_registry: Dict[str, Dict[str, Any]] = {}
# Alias mapping: key = alias (lowercase), value = canonical command.
alias_mapping: Dict[str, str] = {}

def plugin(commands: Union[str, List[str]], canonical: Optional[str] = None, help_visible: bool = True) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to register a function as a command plugin with one or more aliases.
    Optionally specify a canonical name that will be used in help listings.
    """
    if isinstance(commands, str):
        commands = [commands]
    if canonical is None:
        canonical = commands[0].lower()
    else:
        canonical = canonical.lower()
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        nonlocal commands
        # Register canonical command with its aliases and help visibility.
        plugin_registry[canonical] = {
            "function": func,
            "aliases": [cmd.lower() for cmd in commands],
            "help_visible": help_visible
        }
        # Map each alias to the canonical command.
        for cmd in commands:
            alias_mapping[cmd.lower()] = canonical
        return func
    return decorator

def get_plugin(command: str) -> Optional[Callable[..., Any]]:
    """
    Retrieve the plugin function for a given command by looking up the alias mapping.
    """
    canonical = alias_mapping.get(command.lower())
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