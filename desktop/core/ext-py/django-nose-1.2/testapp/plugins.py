from nose.plugins import Plugin


plugin_began = False

class SanityCheckPlugin(Plugin):
    enabled = True

    def options(self, parser, env):
        """Register commandline options."""

    def configure(self, options, conf):
        """Configure plugin."""

    def begin(self):
        global plugin_began
        plugin_began = True
