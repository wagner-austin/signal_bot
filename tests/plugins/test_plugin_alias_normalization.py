"""
tests/plugins/test_plugin_alias_normalization.py - Tests for plugin alias normalization.
Verifies that duplicate aliases (even with different formatting) raise an error and that aliases are normalized.
"""

import pytest
from plugins.manager import plugin, clear_plugins

def test_duplicate_alias_error():
    clear_plugins()

    @plugin(commands=["TestAlias", "alias2"], canonical="test")
    def plugin_one(args, sender, state_machine, msg_timestamp=None):
        return "one"

    with pytest.raises(ValueError) as excinfo:
        @plugin(commands=[" testalias "], canonical="another_test")
        def plugin_two(args, sender, state_machine, msg_timestamp=None):
            return "two"
    assert "Duplicate alias detected" in str(excinfo.value)

# End of tests/plugins/test_plugin_alias_normalization.py