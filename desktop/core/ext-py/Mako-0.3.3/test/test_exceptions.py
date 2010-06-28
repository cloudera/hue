# -*- coding: utf-8 -*-
import sys
import unittest

from mako import exceptions, util
from mako.template import Template
from mako.lookup import TemplateLookup
from util import result_lines
from test import template_base, module_base, TemplateTest

class ExceptionsTest(TemplateTest):
    def test_html_error_template(self):
        """test the html_error_template"""
        code = """
% i = 0
"""
        try:
            template = Template(code)
            template.render_unicode()
        except exceptions.CompileException, ce:
            html_error = exceptions.html_error_template().render_unicode()
            assert ("CompileException: Fragment 'i = 0' is not a partial "
                    "control statement") in html_error
            assert '<style>' in html_error
            assert '</style>' in html_error
            html_error_stripped = html_error.strip()
            assert html_error_stripped.startswith('<html>')
            assert html_error_stripped.endswith('</html>')

            not_full = exceptions.html_error_template().\
                                    render_unicode(full=False)
            assert '<html>' not in not_full
            assert '</html>' not in not_full
            assert '<style>' in not_full
            assert '</style>' in not_full

            no_css = exceptions.html_error_template().\
                                    render_unicode(css=False)
            assert '<style>' not in no_css
            assert '</style>' not in no_css
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")

    def test_utf8_html_error_template(self):
        """test the html_error_template with a Template containing utf8
        chars"""
        
        if util.py3k:
            code = """# -*- coding: utf-8 -*-
% if 2 == 2: /an error
${'привет'}
% endif
"""
        else:
            code = """# -*- coding: utf-8 -*-
% if 2 == 2: /an error
${u'привет'}
% endif
"""
        try:
            template = Template(code)
            template.render_unicode()
        except exceptions.CompileException, ce:
            html_error = exceptions.html_error_template().render()
            assert ("CompileException: Fragment 'if 2 == 2: /an "
                    "error' is not a partial control "
                    "statement at line: 2 char: 1") in \
                    html_error.decode('utf-8')
                    
            if util.py3k:
                assert u"3 ${'привет'}".encode(sys.getdefaultencoding(),
                                            'htmlentityreplace') in html_error
            else:
                assert u"3 ${u'привет'}".encode(sys.getdefaultencoding(),
                                            'htmlentityreplace') in html_error
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")
    
    def test_format_closures(self):
        try:
            exec "def foo():"\
                 "    raise RuntimeError('test')"\
                 in locals()
            foo()
        except:
            html_error = exceptions.html_error_template().render()
            assert "RuntimeError: test" in html_error
        
    def test_py_utf8_html_error_template(self):
        try:
            foo = u'日本'
            raise RuntimeError('test')
        except:
            html_error = exceptions.html_error_template().render()
            if util.py3k:
                assert 'RuntimeError: test' in html_error.decode('utf-8')
                assert u"foo = '日本'" in html_error.decode('utf-8')
            else:
                assert 'RuntimeError: test' in html_error
                assert "foo = u'&#x65E5;&#x672C;'" in html_error

    def test_py_unicode_error_html_error_template(self):
        try:
            raise RuntimeError(u'日本')
        except:
            html_error = exceptions.html_error_template().render()
            assert u"RuntimeError: 日本".encode('ascii', 'ignore') in html_error

    def test_format_exceptions(self):
        l = TemplateLookup(format_exceptions=True)

        l.put_string("foo.html", """
<%inherit file="base.html"/>
${foobar}
        """)

        l.put_string("base.html", """
        ${self.body()}
        """)

        assert '<div class="sourceline">${foobar}</div>' in \
                result_lines(l.get_template("foo.html").render_unicode())
    
    def test_utf8_format_exceptions(self):
        """test that htmlentityreplace formatting is applied to 
           exceptions reported with format_exceptions=True"""
        
        l = TemplateLookup(format_exceptions=True)
        if util.py3k:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${'привет' + foobar}""")
        else:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${u'привет' + foobar}""")

        if util.py3k:
            assert u'<div class="sourceline">${\'привет\' + foobar}</div>'\
                in result_lines(l.get_template("foo.html").render().decode('utf-8'))
        else:
            assert '<div class="highlight">2 ${u\'&#x43F;&#x440;'\
                    '&#x438;&#x432;&#x435;&#x442;\' + foobar}</div>' \
                in result_lines(l.get_template("foo.html").render().decode('utf-8'))
        
    
    def test_custom_tback(self):
        try:
            raise RuntimeError("error 1")
            foo('bar')
        except:
            t, v, tback = sys.exc_info()
        
        try:
            raise RuntimeError("error 2")
        except:
            html_error = exceptions.html_error_template().\
                        render_unicode(error=v, traceback=tback)
        
        # obfuscate the text so that this text
        # isn't in the 'wrong' exception
        assert "".join(reversed(")'rab'(oof")) in html_error

    def test_tback_no_trace(self):
        try:
            t = self._file_template("runtimeerr.html")
            t.render()
        except:
            t, v, tback = sys.exc_info()

        # blow away tracebaack info
        sys.exc_clear()
        
        # and don't even send what we have.
        html_error = exceptions.html_error_template().\
                    render_unicode(error=v, traceback=None)
        
        assert "local variable 'y' referenced" in html_error
