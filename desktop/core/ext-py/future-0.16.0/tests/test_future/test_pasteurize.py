# -*- coding: utf-8 -*-
"""
This module contains snippets of Python 3 code (invalid Python 2) and
tests for whether they can be passed to ``pasteurize`` and
immediately run under both Python 2 and Python 3.
"""

from __future__ import print_function, absolute_import

import pprint
from subprocess import Popen, PIPE
import tempfile
import os

from future.tests.base import CodeHandler, unittest, skip26


class TestPasteurize(CodeHandler):
    """
    After running ``pasteurize``, these Python 3 code snippets should run
    on both Py3 and Py2.
    """

    def setUp(self):
        # For tests that need a text file:
        _, self.textfilename = tempfile.mkstemp(text=True)
        super(TestPasteurize, self).setUp()

    def tearDown(self):
        os.unlink(self.textfilename)

    @skip26    # Python 2.6's lib2to3 causes the "from builtins import
               # range" line to be stuck at the bottom of the module!
    def test_range_slice(self):
        """
        After running ``pasteurize``, this Python 3 code should run
        quickly on both Py3 and Py2 without a MemoryError
        """
        code = '''
        for i in range(10**8)[:10]:
            pass
        '''
        self.unchanged(code, from3=True)

    def test_print(self):
        """
        This Python 3-only code is a SyntaxError on Py2 without the
        print_function import from __future__.
        """
        code = '''
        import sys
        print('Hello', file=sys.stderr)
        '''
        self.unchanged(code, from3=True)

    def test_division(self):
        """
        True division should not be screwed up by conversion from 3 to both
        """
        code = '''
        x = 3 / 2
        assert x == 1.5
        '''
        self.unchanged(code, from3=True)

    # TODO: write / fix the raise_ fixer so that it uses the raise_ function
    @unittest.expectedFailure
    def test_exception_indentation(self):
        """
        As of v0.11.2, pasteurize broke the indentation of ``raise`` statements
        using with_traceback. Test for this.
        """
        before = '''
        import sys
        if True:
            try:
                'string' + 1
            except TypeError:
                ty, va, tb = sys.exc_info()
                raise TypeError("can't do that!").with_traceback(tb)
        '''
        after = '''
        import sys
        from future.utils import raise_with_traceback
        if True:
            try:
                'string' + 1
            except TypeError:
                ty, va, tb = sys.exc_info()
                raise_with_traceback(TypeError("can't do that!"), tb)
        '''
        self.convert_check(before, after, from3=True)

    # TODO: fix and test this test
    @unittest.expectedFailure
    def test_urllib_request(self):
        """
        Example Python 3 code using the new urllib.request module.
        
        Does the ``pasteurize`` script handle this?
        """
        before = """
            import pprint
            import urllib.request

            URL = 'http://pypi.python.org/pypi/{}/json'
            package = 'future'
            
            r = urllib.request.urlopen(URL.format(package))
            pprint.pprint(r.read())
        """
        after = """
            import pprint
            import future.standard_library.urllib.request as urllib_request

            URL = 'http://pypi.python.org/pypi/{}/json'
            package = 'future'
            
            r = urllib_request.urlopen(URL.format(package))
            pprint.pprint(r.read())
        """

        self.convert_check(before, after, from3=True)

    def test_urllib_refactor2(self):
        before = """
        import urllib.request, urllib.parse

        f = urllib.request.urlopen(url, timeout=15)
        filename = urllib.parse.urlparse(url)[2].split('/')[-1]
        """

        after = """
        from future.standard_library.urllib import request as urllib_request
        from future.standard_library.urllib import parse as urllib_parse

        f = urllib_request.urlopen(url, timeout=15)
        filename = urllib_parse.urlparse(url)[2].split('/')[-1]
        """

    def test_correct_exit_status(self):
        """
        Issue #119: futurize and pasteurize were not exiting with the correct
        status code. This is because the status code returned from
        libfuturize.main.main() etc. was a ``newint``, which sys.exit() always
        translates into 1!
        """
        from libpasteurize.main import main
        # Try pasteurizing this test script:
        retcode = main([self.textfilename])
        self.assertTrue(isinstance(retcode, int))   # i.e. Py2 builtin int

 
class TestFuturizeAnnotations(CodeHandler):
    @unittest.expectedFailure
    def test_return_annotations_alone(self):
        before = "def foo() -> 'bar': pass"
        after = """
        def foo(): pass
        foo.__annotations__ = {'return': 'bar'}
        """
        self.convert_check(before, after, from3=True)

        b = """
        def foo() -> "bar":
            print "baz"
            print "what's next, again?"
        """
        a = """
        def foo():
            print "baz"
            print "what's next, again?"
        """
        self.convert_check(b, a, from3=True)

    @unittest.expectedFailure
    def test_single_param_annotations(self):
        b = "def foo(bar:'baz'): pass"
        a = """
        def foo(bar): pass
        foo.__annotations__ = {'bar': 'baz'}
        """
        self.convert_check(b, a, from3=True)

        b = """
        def foo(bar:"baz"="spam"):
            print("what's next, again?")
            print("whatever.")
        """
        a = """
        def foo(bar="spam"):
            print("what's next, again?")
            print("whatever.")
        foo.__annotations__ = {'bar': 'baz'}
        """
        self.convert_check(b, a, from3=True)

    def test_multiple_param_annotations(self):
        b = "def foo(bar:'spam'=False, baz:'eggs'=True, ham:False='spaghetti'): pass"
        a = "def foo(bar=False, baz=True, ham='spaghetti'): pass"
        self.convert_check(b, a, from3=True)

        b = """
        def foo(bar:"spam"=False, baz:"eggs"=True, ham:False="spam"):
            print("this is filler, just doing a suite")
            print("suites require multiple lines.")
        """
        a = """
        def foo(bar=False, baz=True, ham="spam"):
            print("this is filler, just doing a suite")
            print("suites require multiple lines.")
        """
        self.convert_check(b, a, from3=True)

    def test_mixed_annotations(self):
        b = "def foo(bar=False, baz:'eggs'=True, ham:False='spaghetti') -> 'zombies': pass"
        a = "def foo(bar=False, baz=True, ham='spaghetti'): pass"
        self.convert_check(b, a, from3=True)

        b = """
        def foo(bar:"spam"=False, baz=True, ham:False="spam") -> 'air':
            print("this is filler, just doing a suite")
            print("suites require multiple lines.")
        """
        a = """
        def foo(bar=False, baz=True, ham="spam"):
            print("this is filler, just doing a suite")
            print("suites require multiple lines.")
        """
        self.convert_check(b, a, from3=True)

        b = "def foo(bar) -> 'brains': pass"
        a = "def foo(bar): pass"
        self.convert_check(b, a, from3=True)

    def test_functions_unchanged(self):
        s = "def foo(): pass"
        self.unchanged(s, from3=True)

        s = """
        def foo():
            pass
            pass
        """
        self.unchanged(s, from3=True)

        s = """
        def foo(bar='baz'):
            pass
            pass
        """
        self.unchanged(s, from3=True)
        

if __name__ == '__main__':
    unittest.main()
