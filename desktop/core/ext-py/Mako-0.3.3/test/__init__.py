from mako.template import Template
import unittest, os
from mako.util import function_named, py3k

from nose import SkipTest


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
    
    def _do_test(self, template, expected, filters=None, template_args=None, unicode_=True):
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
