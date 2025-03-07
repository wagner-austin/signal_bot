"""
tests/plugins/test_plugin_discovery.py - Tests for plugin discovery using pkgutil in plugins/manager.py.
Verifies that plugins are correctly discovered, loaded, and reloaded.
"""

import pytest
from plugins import manager

def test_load_plugins_populates_registry():
    # Clear any existing plugins.
    manager.clear_plugins()
    # Load plugins from the plugins package.
    manager.load_plugins()
    plugins_dict = manager.get_all_plugins()
    # We expect that at least one plugin is loaded (assuming there are plugin modules present).
    assert isinstance(plugins_dict, dict)
    assert len(plugins_dict) > 0

def test_reload_plugins_clears_and_reloads():
    # Load plugins initially.
    manager.load_plugins()
    initial_plugins = manager.get_all_plugins().copy()
    # Now reload plugins.
    manager.reload_plugins()
    reloaded_plugins = manager.get_all_plugins()
    # The registry should not be empty after reloading.
    assert len(reloaded_plugins) > 0
    # Although the references might be updated, the keys should remain consistent.
    assert set(initial_plugins.keys()) == set(reloaded_plugins.keys())

# End of tests/plugins/test_plugin_discovery.py