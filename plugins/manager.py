"""
plugins/manager.py - Unified plugin manager.
Handles registration, loading, and reloading of plugins.
Supports registering multiple aliases in one decorator.
Uses pkgutil.iter_modules to discover plugins within the package.
"""

import sys
import importlib
import pkgutil
from typing import Callable, Any, Optional, Dict, List, Union
from types import ModuleType

# Registry to hold command plugins.
plugin_registry: Dict[str, Callable[..., Any]] = {}

def plugin(commands: Union[str, List[str]]) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to register a function as a command plugin with one or more aliases.
    
    Args:
        commands (Union[str, List[str]]): A command name or a list of command aliases.
        
    Returns:
        Callable: A decorator that registers the plugin function.
        
    Raises:
        ValueError: If a plugin for any of the given commands is already registered.
    """
    if isinstance(commands, str):
        commands = [commands]
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        for command in commands:
            key = command.lower()
            if key in plugin_registry:
                raise ValueError(f"Duplicate registration for '{command}'")
            plugin_registry[key] = func
        return func
    return decorator

def get_plugin(command: str) -> Optional[Callable[..., Any]]:
    """
    Retrieve a plugin function by command.
    
    Args:
        command (str): The command name.
        
    Returns:
        Optional[Callable]: The plugin function if found, else None.
    """
    return plugin_registry.get(command.lower())

def get_all_plugins() -> Dict[str, Callable[..., Any]]:
    """
    Return all registered plugins.
    
    Returns:
        Dict[str, Callable]: Dictionary containing all registered plugins.
    """
    return plugin_registry

def clear_plugins() -> None:
    """
    Clear all registered plugins to facilitate dynamic reloading.
    """
    plugin_registry.clear()

def _load_plugins_from_pkg(reload: bool = False) -> None:
    """
    Helper function to load or reload all plugin modules from the plugins package using pkgutil.iter_modules.
    
    Args:
        reload (bool): If True, reloads modules already imported; otherwise, imports modules.
    """
    import plugins  # Ensure the plugins package is imported.
    for finder, name, ispkg in pkgutil.iter_modules(plugins.__path__):
        module_name = f"plugins.{name}"
        if reload and module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            importlib.import_module(module_name)

def load_plugins() -> None:
    """
    Automatically import all plugin modules in the 'plugins' package.
    
    Returns:
        None
    """
    _load_plugins_from_pkg(reload=False)

def reload_plugins() -> None:
    """
    Reload all plugin modules dynamically by clearing the plugin registry
    and re-importing all plugin modules.
    
    Returns:
        None
    """
    clear_plugins()
    _load_plugins_from_pkg(reload=True)

# End of plugins/manager.py
