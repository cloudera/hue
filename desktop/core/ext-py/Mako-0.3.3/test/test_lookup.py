from mako.template import Template
from mako import lookup, exceptions
from util import flatten_result, result_lines
import unittest

from test import TemplateTest, template_base, module_base

tl = lookup.TemplateLookup(directories=[template_base])
class LookupTest(unittest.TestCase):
    def test_basic(self):
        t = tl.get_template('index.html')
        assert result_lines(t.render()) == [
            "this is index"
        ]
    def test_subdir(self):
        t = tl.get_template('/subdir/index.html')
        assert result_lines(t.render()) == [
            "this is sub index",
            "this is include 2"

        ]

        assert tl.get_template('/subdir/index.html').module_id \
                            == '_subdir_index_html'
    
    def test_updir(self):
        t = tl.get_template('/subdir/foo/../bar/../index.html')
        assert result_lines(t.render()) == [
            "this is sub index",
            "this is include 2"

        ]
    
    def test_directory_lookup(self):
        """test that hitting an existent directory still raises
        LookupError."""
        
        self.assertRaises(exceptions.TopLevelLookupException,
            tl.get_template, "/subdir"
        )
        
    def test_no_lookup(self):
        t = Template("hi <%include file='foo.html'/>")
        try:
            t.render()
            assert False
        except exceptions.TemplateLookupException, e:
            assert str(e) == \
                "Template 'memory:%s' has no TemplateLookup associated" % \
                hex(id(t))
            
    def test_uri_adjust(self):
        tl = lookup.TemplateLookup(directories=['/foo/bar'])
        assert tl.filename_to_uri('/foo/bar/etc/lala/index.html') == \
                        '/etc/lala/index.html'

        tl = lookup.TemplateLookup(directories=['./foo/bar'])
        assert tl.filename_to_uri('./foo/bar/etc/index.html') == \
                        '/etc/index.html'
    
    def test_uri_cache(self):
        """test that the _uri_cache dictionary is available"""
        tl._uri_cache[('foo', 'bar')] = '/some/path'
        assert tl._uri_cache[('foo', 'bar')] == '/some/path'
        
