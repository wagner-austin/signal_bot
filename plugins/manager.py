#!/usr/bin/env python
"""
plugins/manager.py - Unified plugin manager with alias support.
Handles registration, loading, and retrieval of plugins, as well as runtime enable/disable functionality.
This module supports both function-based and class-based plugins.
"""

import sys
import inspect
import importlib
import pkgutil
import logging
from typing import Callable, Any, Optional, Dict, List, Union, Set

logger = logging.getLogger(__name__)

# Registry: key = canonical command, value = dict with function, aliases, help_visible, and category.
plugin_registry: Dict[str, Dict[str, Any]] = {}
# Alias mapping: key = alias (normalized), value = canonical command.
alias_mapping: Dict[str, str] = {}
# Track disabled plugins by canonical command name.
disabled_plugins: Set[str] = set()

def normalize_alias(alias: str) -> str:
    """
    Normalize an alias to a standardized format: lowercased and stripped.
    """
    return alias.strip().lower()

def plugin(commands: Union[str, List[str]],
           canonical: Optional[str] = None,
           help_visible: bool = True,
           category: Optional[str] = None) -> Callable[[Any], Any]:
    """
    Decorator to register a function or class as a plugin command with aliases.

    Parameters:
      commands (Union[str, List[str]]): Command aliases.
      canonical (Optional[str]): Primary command name (default is first alias).
      help_visible (bool): If True, command is shown in help listings.
      category (Optional[str]): Command category.

    Usage Example:
      @plugin(['delete', 'remove'], canonical='delete')
      class DeletePlugin(BasePlugin):
          ...
    """
    if isinstance(commands, str):
        commands = [commands]

    normalized_commands = [normalize_alias(cmd) for cmd in commands]

    canonical_name = normalize_alias(canonical) if canonical else normalized_commands[0]

    def decorator(obj: Any) -> Any:
        if inspect.isclass(obj):
            instance = obj()  # Instantiate once

            def plugin_func(args, sender, state_machine, msg_timestamp=None):
                return instance.run_command(args, sender, state_machine, msg_timestamp)

            plugin_registry[canonical_name] = {
                "function": plugin_func,
                "aliases": normalized_commands,
                "help_visible": help_visible,
                "category": category or "Miscellaneous Commands",
            }
        else:
            if not hasattr(obj, "help_text"):
                obj.help_text = ""
            plugin_registry[canonical_name] = {
                "function": obj,
                "aliases": normalized_commands,
                "help_visible": help_visible,
                "category": category or "Miscellaneous Commands",
            }

        # Map all aliases to the canonical command.
        for alias in normalized_commands:
            if alias in alias_mapping and alias_mapping[alias] != canonical_name:
                raise ValueError(f"Duplicate alias '{alias}' already exists for '{alias_mapping[alias]}'.")
            alias_mapping[alias] = canonical_name

        return obj

    return decorator

def get_plugin(command: str) -> Optional[Callable[..., Any]]:
    """
    Retrieve the plugin function for the given command alias.
    Returns None if not found or if the plugin is disabled.
    """
    canonical = alias_mapping.get(normalize_alias(command))
    if not canonical or canonical in disabled_plugins:
        return None
    return plugin_registry.get(canonical, {}).get("function")

def get_all_plugins() -> Dict[str, Dict[str, Any]]:
    """
    Retrieve all registered plugins.
    """
    return plugin_registry

def disable_plugin(canonical_name: str) -> None:
    """
    Disable a plugin by its canonical name.
    """
    disabled_plugins.add(normalize_alias(canonical_name))

def enable_plugin(canonical_name: str) -> None:
    """
    Enable a previously disabled plugin.
    """
    disabled_plugins.discard(normalize_alias(canonical_name))

def clear_plugins() -> None:
    """
    Clear all registered plugins and aliases.
    """
    plugin_registry.clear()
    alias_mapping.clear()
    disabled_plugins.clear()

def import_module_safe(module_name: str) -> None:
    """
    Safely import or reload a module.
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
    Load all plugin modules from 'plugins.commands'.
    """
    import plugins.commands
    module_infos = list(pkgutil.walk_packages(plugins.commands.__path__, plugins.commands.__name__ + "."))
    module_names = {module_info.name for module_info in module_infos}

    def import_module_safe(name):
        try:
            importlib.import_module(name)
            logger.info(f"Imported module '{name}'.")
        except Exception as e:
            logger.error(f"Failed to import module '{name}': {e}", exc_info=True)

    if concurrent:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(import_module_safe, name): name for name in module_names}
            for future in as_completed(futures):
                mname = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Unexpected error importing module '{mname}': {e}", exc_info=True)
    else:
        for mname in module_names:
            import_module_safe(mname)

def reload_plugins(concurrent: bool = False) -> None:
    """
    Clear existing plugins and reload all plugins.
    """
    clear_plugins()
    load_plugins(concurrent=concurrent)

# End of plugins/manager.py