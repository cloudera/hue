"""Additional plugins for testing plugins."""
from nose.plugins import Plugin

plugin_began = False


class SanityCheckPlugin(Plugin):
    """Test plugin that registers that it ran."""

    enabled = True

    def options(self, parser, env):
        """Register commandline options."""

    def configure(self, options, conf):
        """Configure plugin."""

    def begin(self):
        """Flag that the plugin was run."""
        global plugin_began
        plugin_began = True
