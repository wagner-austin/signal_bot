"""
plugins/manager.py - Unified plugin manager with alias support.
Handles registration, loading, and retrieval of plugins using centralized and standardized alias definitions.
Now includes enhanced error handling for import-time exceptions and optional concurrent module loading.
"""

import sys
import importlib
import pkgutil
import logging
from typing import Callable, Any, Optional, Dict, List, Union

# Setup logger for the module
logger = logging.getLogger(__name__)

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

def import_module_safe(module_name: str) -> None:
    """
    Attempt to import or reload a module safely.
    If the module is already in sys.modules, it is reloaded.
    Exceptions during import are caught and logged, allowing the process to continue.
    """
    try:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            logger.info(f"Reloaded module '{module_name}'.")
        else:
            importlib.import_module(module_name)
            logger.info(f"Imported module '{module_name}'.")
    except Exception as e:
        logger.error(f"Failed to import module '{module_name}': {e}", exc_info=True)

def load_plugins(concurrent: bool = False) -> None:
    """
    Automatically import (or reload) all plugin modules in the 'plugins.commands'
    package to register all plugins.
    
    If an import fails, the error is logged and the process continues with other modules.
    Optionally, modules can be imported concurrently by setting concurrent=True.
    
    Parameters:
        concurrent (bool): If True, import modules concurrently using a thread pool.
    """
    import plugins.commands  # Ensure the package is imported.
    module_infos = list(pkgutil.walk_packages(plugins.commands.__path__, plugins.commands.__name__ + "."))
    module_names = {module_info.name for module_info in module_infos}
    
    if concurrent:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(import_module_safe, module_name): module_name for module_name in module_names}
            for future in as_completed(futures):
                module_name = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Unexpected error importing module '{module_name}': {e}", exc_info=True)
    else:
        for module_name in module_names:
            import_module_safe(module_name)

def reload_plugins(concurrent: bool = False) -> None:
    """
    Reload all plugin modules dynamically by clearing the plugin registry and re-importing modules.
    
    Parameters:
        concurrent (bool): If True, modules are reloaded concurrently.
    """
    clear_plugins()
    load_plugins(concurrent=concurrent)

# End of plugins/manager.py