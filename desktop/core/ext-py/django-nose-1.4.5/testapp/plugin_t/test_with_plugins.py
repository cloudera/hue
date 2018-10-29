"""Test loading of additional plugins."""
from nose.tools import eq_


def test_one():
    """Test that the test plugin was initialized."""
    from testapp import plugins
    eq_(plugins.plugin_began, True)
