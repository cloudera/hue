from nose.tools import eq_


def test_one():
    from testapp import plugins
    eq_(plugins.plugin_began, True)
