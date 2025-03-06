"""
manager.py
------------------
Unified plugin manager module that handles registration, loading, and reloading of plugins.
It skips non-plugin files and abstracts common loading logic into a helper function.
"""

import os
import sys
import importlib.util
import importlib
from typing import Callable, Any, Optional, Dict
from types import ModuleType

# Registry to hold command plugins.
plugin_registry: Dict[str, Callable[..., Any]] = {}

def plugin(command: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to register a function as a command plugin.
    
    Args:
        command (str): The command name to register.
        
    Returns:
        Callable: A decorator that registers the plugin function.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        plugin_registry[command.lower()] = func
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

def _load_module(module_name: str, file_path: str) -> Optional[ModuleType]:
    """
    Helper function to load a module given its module name and file path.
    
    Args:
        module_name (str): The name of the module.
        file_path (str): The file path to the module.
        
    Returns:
        Optional[ModuleType]: The loaded module object if successful, else None.
        
    Raises:
        Exception: If the module fails to load.
    """
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def _load_plugins_from_dir(reload: bool = False) -> None:
    """
    Helper function to load or reload all plugin modules from the plugins directory,
    skipping non-plugin files such as __init__.py.
    
    Args:
        reload (bool): If True, reloads modules already imported; otherwise, imports modules.
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))
    plugins_dir = os.path.join(base_dir, 'plugins')
    if not os.path.isdir(plugins_dir):
        return
    for filename in os.listdir(plugins_dir):
        # Skip non-plugin files
        if not filename.endswith('.py') or filename == '__init__.py':
            continue
        module_name = "plugins." + filename[:-3]
        file_path = os.path.join(plugins_dir, filename)
        if reload and module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
        else:
            _load_module(module_name, file_path)

def load_plugins() -> None:
    """
    Automatically import all plugin modules in the 'plugins' directory,
    skipping non-plugin files.
    
    Returns:
        None
    """
    _load_plugins_from_dir(reload=False)

def reload_plugins() -> None:
    """
    Reload all plugin modules dynamically by clearing the plugin registry
    and re-importing all plugin modules, skipping non-plugin files.
    
    Returns:
        None
    """
    clear_plugins()
    _load_plugins_from_dir(reload=True)

# End of plugins/manager.py