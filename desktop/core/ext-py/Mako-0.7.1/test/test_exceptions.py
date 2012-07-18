# -*- coding: utf-8 -*-
import sys
import unittest

from mako import exceptions, util
from mako.template import Template
from mako.lookup import TemplateLookup
from util import result_lines
from test import template_base, module_base, TemplateTest
from test import requires_pygments_14, requires_no_pygments

class ExceptionsTest(TemplateTest):
    def test_html_error_template(self):
        """test the html_error_template"""
        code = """
% i = 0
"""
        try:
            template = Template(code)
            template.render_unicode()
            assert False
        except exceptions.CompileException, ce:
            html_error = exceptions.html_error_template().render_unicode()
            assert ("CompileException: Fragment &#39;i = 0&#39; is not "
                    "a partial control statement at line: 2 char: 1") in html_error
            assert '<style>' in html_error
            html_error_stripped = html_error.strip()
            assert html_error_stripped.startswith('<html>')
            assert html_error_stripped.endswith('</html>')

            not_full = exceptions.html_error_template().\
                                    render_unicode(full=False)
            assert '<html>' not in not_full
            assert '<style>' in not_full

            no_css = exceptions.html_error_template().\
                                    render_unicode(css=False)
            assert '<style>' not in no_css
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")

    def test_text_error_template(self):
        code = """
% i = 0
"""
        try:
            template = Template(code)
            template.render_unicode()
            assert False
        except exceptions.CompileException, ce:
            text_error = exceptions.text_error_template().render_unicode()
            assert 'Traceback (most recent call last):' in text_error
            assert ("CompileException: Fragment 'i = 0' is not a partial "
                    "control statement") in text_error

    @requires_pygments_14
    def test_utf8_html_error_template_pygments(self):
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
            if util.py3k:
                assert ("CompileException: Fragment &#39;if 2 == 2: /an "
                    "error&#39; is not a partial control statement "
                    "at line: 2 char: 1").encode(sys.getdefaultencoding(), 'htmlentityreplace') in \
                    html_error
            else:
                assert ("CompileException: Fragment &#39;if 2 == 2: /an "
                        "error&#39; is not a partial control statement "
                        "at line: 2 char: 1") in \
                        html_error
 
            if util.py3k:
                assert u"".encode(sys.getdefaultencoding(),
                                        'htmlentityreplace') in html_error
            else:
                assert u'<pre>3</pre></div></td><td class="code">'\
                        '<div class="syntax-highlighted"><pre><span '\
                        'class="cp">${</span><span class="s">u&#39;'\
                        '&#x43F;&#x440;&#x438;&#x432;&#x435;&#x442;'\
                        '&#39;</span><span class="cp">}</span>'.encode(
                                sys.getdefaultencoding(),
                                'htmlentityreplace') in html_error
        else:
            assert False, ("This function should trigger a CompileException, "
                           "but didn't")

    @requires_no_pygments
    def test_utf8_html_error_template_no_pygments(self):
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
            if util.py3k:
                assert ("CompileException: Fragment &#39;if 2 == 2: /an "
                    "error&#39; is not a partial control statement "
                    "at line: 2 char: 1").encode(sys.getdefaultencoding(), 'htmlentityreplace') in \
                    html_error
            else:
                assert ("CompileException: Fragment &#39;if 2 == 2: /an "
                        "error&#39; is not a partial control statement "
                        "at line: 2 char: 1") in \
                        html_error
 
            if util.py3k:
                assert u"${&#39;привет&#39;}".encode(sys.getdefaultencoding(),
                                        'htmlentityreplace') in html_error
            else:
                assert u"${u&#39;привет&#39;}".encode(sys.getdefaultencoding(),
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
            assert "RuntimeError: test" in str(html_error)
 
    def test_py_utf8_html_error_template(self):
        try:
            foo = u'日本'
            raise RuntimeError('test')
        except:
            html_error = exceptions.html_error_template().render()
            if util.py3k:
                assert 'RuntimeError: test' in html_error.decode('utf-8')
                assert u"foo = &#39;日本&#39;" in html_error.decode('utf-8')
            else:
                assert 'RuntimeError: test' in html_error
                assert "foo = u&#39;&#x65E5;&#x672C;&#39;" in html_error

    def test_py_unicode_error_html_error_template(self):
        try:
            raise RuntimeError(u'日本')
        except:
            html_error = exceptions.html_error_template().render()
            assert u"RuntimeError: 日本".encode('ascii', 'ignore') in html_error

    @requires_pygments_14
    def test_format_exceptions_pygments(self):
        l = TemplateLookup(format_exceptions=True)

        l.put_string("foo.html", """
<%inherit file="base.html"/>
${foobar}
        """)

        l.put_string("base.html", """
        ${self.body()}
        """)

        assert '<div class="sourceline"><table class="syntax-highlightedtable">'\
                '<tr><td class="linenos"><div class="linenodiv"><pre>3</pre>'\
                '</div></td><td class="code"><div class="syntax-highlighted">'\
                '<pre><span class="err">$</span><span class="p">{</span>'\
                '<span class="n">foobar</span><span class="p">}</span>' in \
            result_lines(l.get_template("foo.html").render_unicode())

    @requires_no_pygments
    def test_format_exceptions_no_pygments(self):
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
 
    @requires_pygments_14
    def test_utf8_format_exceptions_pygments(self):
        """test that htmlentityreplace formatting is applied to 
           exceptions reported with format_exceptions=True"""
 
        l = TemplateLookup(format_exceptions=True)
        if util.py3k:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${'привет' + foobar}""")
        else:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${u'привет' + foobar}""")

        if util.py3k:
            assert '<table class="error syntax-highlightedtable"><tr><td '\
                    'class="linenos"><div class="linenodiv"><pre>2</pre>'\
                    '</div></td><td class="code"><div class="error '\
                    'syntax-highlighted"><pre><span class="cp">${</span>'\
                    '<span class="s">&#39;привет&#39;</span> <span class="o">+</span> '\
                    '<span class="n">foobar</span><span class="cp">}</span>'\
                    '<span class="x"></span>' in \
                result_lines(l.get_template("foo.html").render().decode('utf-8'))
        else:
            assert '<table class="error syntax-highlightedtable"><tr><td '\
                    'class="linenos"><div class="linenodiv"><pre>2</pre>'\
                    '</div></td><td class="code"><div class="error '\
                    'syntax-highlighted"><pre><span class="cp">${</span>'\
                    '<span class="s">u&#39;&#x43F;&#x440;&#x438;&#x432;'\
                    '&#x435;&#x442;&#39;</span> <span class="o">+</span> '\
                    '<span class="n">foobar</span><span class="cp">}</span>'\
                    '<span class="x"></span>' in \
                result_lines(l.get_template("foo.html").render().decode('utf-8'))

    @requires_no_pygments
    def test_utf8_format_exceptions_no_pygments(self):
        """test that htmlentityreplace formatting is applied to 
           exceptions reported with format_exceptions=True"""
 
        l = TemplateLookup(format_exceptions=True)
        if util.py3k:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${'привет' + foobar}""")
        else:
            l.put_string("foo.html", """# -*- coding: utf-8 -*-\n${u'привет' + foobar}""")

        if util.py3k:
            assert u'<div class="sourceline">${&#39;привет&#39; + foobar}</div>'\
                in result_lines(l.get_template("foo.html").render().decode('utf-8'))
        else:
            assert '${u&#39;&#x43F;&#x440;&#x438;&#x432;&#x435;'\
                   '&#x442;&#39; + foobar}' in \
                result_lines(l.get_template("foo.html").render().decode('utf-8'))
 
 
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
        assert "".join(reversed(");93#&rab;93#&(oof")) in html_error

    def test_tback_no_trace(self):
        try:
            t = self._file_template("runtimeerr.html")
            t.render()
        except:
            t, v, tback = sys.exc_info()

        if not util.py3k:
            # blow away tracebaack info
            sys.exc_clear()
 
        # and don't even send what we have.
        html_error = exceptions.html_error_template().\
                    render_unicode(error=v, traceback=None)
        assert "local variable &#39;y&#39; referenced before assignment" in html_error
