from mako.template import Template
import unittest
import os
from mako.compat import py3k, py26, py25
from mako.util import function_named
import re
from mako.cache import CacheImpl, register_plugin
from nose import SkipTest
import sys

template_base = os.path.join(os.path.dirname(__file__), 'templates')
module_base = os.path.join(template_base, 'modules')

class TemplateTest(unittest.TestCase):

    def _file_template(self, filename, **kw):
        filepath = self._file_path(filename)
        return Template(uri=filename, filename=filepath,
                            module_directory=module_base, **kw)

    def _file_path(self, filename):
        name, ext = os.path.splitext(filename)

        if py3k:
            py3k_path = os.path.join(template_base, name + "_py3k" + ext)
            if os.path.exists(py3k_path):
                return py3k_path

        return os.path.join(template_base, filename)

    def _do_file_test(self, filename, expected, filters=None,
                        unicode_=True, template_args=None, **kw):
        t1 = self._file_template(filename, **kw)
        self._do_test(t1, expected, filters=filters,
                        unicode_=unicode_, template_args=template_args)

    def _do_memory_test(self, source, expected, filters=None,
                        unicode_=True, template_args=None, **kw):
        t1 = Template(text=source, **kw)
        self._do_test(t1, expected, filters=filters,
                        unicode_=unicode_, template_args=template_args)

    def _do_test(self, template, expected, filters=None, template_args=None,
                                unicode_=True):
        if template_args is None:
            template_args = {}
        if unicode_:
            output = template.render_unicode(**template_args)
        else:
            output = template.render(**template_args)

        if filters:
            output = filters(output)
        eq_(output, expected)

def eq_(a, b, msg=None):
    """Assert a == b, with repr messaging on failure."""
    assert a == b, msg or "%r != %r" % (a, b)

def teardown():
    import shutil
    shutil.rmtree(module_base, True)

def assert_raises(except_cls, callable_, *args, **kw):
    try:
        callable_(*args, **kw)
        success = False
    except except_cls:
        success = True

    # assert outside the block so it works for AssertionError too !
    assert success, "Callable did not raise an exception"

def assert_raises_message(except_cls, msg, callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
        assert False, "Callable did not raise an exception"
    except except_cls:
        e = sys.exc_info()[1]
        assert re.search(msg, str(e)), "%r !~ %s" % (msg, e)
        print(str(e))

def skip_if(predicate, reason=None):
    """Skip a test if predicate is true."""
    reason = reason or predicate.__name__

    def decorate(fn):
        fn_name = fn.__name__
        def maybe(*args, **kw):
            if predicate():
                msg = "'%s' skipped: %s" % (
                    fn_name, reason)
                raise SkipTest(msg)
            else:
                return fn(*args, **kw)
        return function_named(maybe, fn_name)
    return decorate

def requires_python_2(fn):
    return skip_if(lambda: py3k, "Requires Python 2.xx")(fn)

def requires_python_26_or_greater(fn):
    return skip_if(lambda: not py26, "Requires Python 2.6 or greater")(fn)

def requires_python_25_or_greater(fn):
    return skip_if(lambda: not py25, "Requires Python 2.5 or greater")(fn)

def requires_pygments_14(fn):
    try:
        import pygments
        version = pygments.__version__
    except:
        version = "0"
    return skip_if(lambda: version < "1.4")(fn)

def requires_no_pygments_exceptions(fn):
    def go(*arg, **kw):
        from mako import exceptions
        exceptions._install_fallback()
        try:
            return fn(*arg, **kw)
        finally:
            exceptions._install_highlighting()
    return function_named(go, fn.__name__)

class PlainCacheImpl(CacheImpl):
    """Simple memory cache impl so that tests which
    use caching can run without beaker.  """

    def __init__(self, cache):
        self.cache = cache
        self.data = {}

    def get_or_create(self, key, creation_function, **kw):
        if key in self.data:
            return self.data[key]
        else:
            self.data[key] = data = creation_function(**kw)
            return data

    def put(self, key, value, **kw):
        self.data[key] = value

    def get(self, key, **kw):
        return self.data[key]

    def invalidate(self, key, **kw):
        del self.data[key]

register_plugin("plain", __name__, "PlainCacheImpl")
