"""
Tests for the future.standard_library module
"""

from __future__ import absolute_import, print_function
from future import standard_library
from future import utils
from future.tests.base import unittest, CodeHandler, expectedFailurePY2

import sys
import tempfile
import os
import copy
import textwrap
from subprocess import CalledProcessError


class TestStandardLibraryReorganization(CodeHandler):

    def setUp(self):
        self.interpreter = sys.executable
        standard_library.install_aliases()
        super(TestStandardLibraryReorganization, self).setUp()

    def tearDown(self):
        # standard_library.remove_hooks()
        pass

    def test_can_import_several(self):
        """
        This test failed in v0.12-pre if e.g.
        future/standard_library/email/header.py contained:

            from future import standard_library
            standard_library.remove_hooks()
        """

        import future.moves.urllib.parse as urllib_parse
        import future.moves.urllib.request as urllib_request

        import http.server
        for m in [urllib_parse, urllib_request, http.server]:
            self.assertTrue(m is not None)

    def test_is_py2_stdlib_module(self):
        """
        Tests whether the internal is_py2_stdlib_module function (called by the
        sys.modules scrubbing functions) is reliable.
        """
        externalmodules = [standard_library, utils]
        self.assertTrue(not any([standard_library.is_py2_stdlib_module(module)
                             for module in externalmodules]))

        py2modules = [sys, tempfile, copy, textwrap]
        if utils.PY2:
            # Debugging:
            for module in py2modules:
                if hasattr(module, '__file__'):
                    print(module.__file__, file=sys.stderr)
            self.assertTrue(all([standard_library.is_py2_stdlib_module(module)
                                 for module in py2modules]))
        else:
            self.assertTrue(
                    not any ([standard_library.is_py2_stdlib_module(module)
                              for module in py2modules]))

    # @unittest.skip("No longer relevant")
    # def test_all_modules_identical(self):
    #     """
    #     Tests whether all of the old imports in RENAMES are accessible
    #     under their new names.
    #     """
    #     for (oldname, newname) in standard_library.RENAMES.items():
    #         if newname == 'winreg' and sys.platform not in ['win32', 'win64']:
    #             continue
    #         if newname in standard_library.REPLACED_MODULES:
    #             # Skip this check for e.g. the stdlib's ``test`` module,
    #             # which we have replaced completely.
    #             continue
    #         oldmod = __import__(oldname)
    #         newmod = __import__(newname)
    #         if '.' not in oldname:
    #             self.assertEqual(oldmod, newmod)

    @expectedFailurePY2
    def test_suspend_hooks(self):
        """
        Code like the try/except block here appears in Pyflakes v0.6.1. This
        method tests whether suspend_hooks() works as advertised.
        """
        example_PY2_check = False
        with standard_library.suspend_hooks():
            # An example of fragile import code that we don't want to break:
            try:
                import builtins
            except ImportError:
                example_PY2_check = True
        if utils.PY2:
            self.assertTrue(example_PY2_check)
        else:
            self.assertFalse(example_PY2_check)
        # The import should succeed again now:
        import builtins

    @expectedFailurePY2
    def test_disable_hooks(self):
        """
        Tests the old (deprecated) names. These deprecated aliases should be
        removed by version 1.0
        """
        example_PY2_check = False

        standard_library.enable_hooks()   # deprecated name
        old_meta_path = copy.copy(sys.meta_path)

        standard_library.disable_hooks()
        standard_library.scrub_future_sys_modules()
        if utils.PY2:
            self.assertTrue(len(old_meta_path) == len(sys.meta_path) + 1)
        else:
            self.assertTrue(len(old_meta_path) == len(sys.meta_path))

        # An example of fragile import code that we don't want to break:
        try:
            import builtins
        except ImportError:
            example_PY2_check = True
        if utils.PY2:
            self.assertTrue(example_PY2_check)
        else:
            self.assertFalse(example_PY2_check)

        standard_library.install_hooks()

        # Imports should succeed again now:
        import builtins
        import html
        if utils.PY2:
            self.assertTrue(standard_library.detect_hooks())
            self.assertTrue(len(old_meta_path) == len(sys.meta_path))

    @expectedFailurePY2
    def test_remove_hooks2(self):
        """
        As above, but with the new names
        """
        example_PY2_check = False

        standard_library.install_hooks()
        old_meta_path = copy.copy(sys.meta_path)

        standard_library.remove_hooks()
        standard_library.scrub_future_sys_modules()
        if utils.PY2:
            self.assertTrue(len(old_meta_path) == len(sys.meta_path) + 1)
        else:
            self.assertTrue(len(old_meta_path) == len(sys.meta_path))

        # An example of fragile import code that we don't want to break:
        try:
            import builtins
        except ImportError:
            example_PY2_check = True
        if utils.PY2:
            self.assertTrue(example_PY2_check)
        else:
            self.assertFalse(example_PY2_check)
        standard_library.install_hooks()
        # The import should succeed again now:
        import builtins
        self.assertTrue(len(old_meta_path) == len(sys.meta_path))

    def test_detect_hooks(self):
        """
        Tests whether the future.standard_library.detect_hooks is doing
        its job.
        """
        standard_library.install_hooks()
        if utils.PY2:
            self.assertTrue(standard_library.detect_hooks())

        meta_path = copy.copy(sys.meta_path)

        standard_library.remove_hooks()
        if utils.PY2:
            self.assertEqual(len(meta_path), len(sys.meta_path) + 1)
            self.assertFalse(standard_library.detect_hooks())

    @unittest.skipIf(utils.PY3, 'not testing for old urllib on Py3')
    def test_old_urllib_import(self):
        """
        Tests whether an imported module can import the old urllib package.
        Importing future.standard_library in a script should be possible and
        not disrupt any uses of the old Py2 standard library names in modules
        imported by that script.
        """
        code1 = '''
                from future import standard_library
                with standard_library.suspend_hooks():
                    import module_importing_old_urllib
                '''
        self._write_test_script(code1, 'runme.py')
        code2 = '''
                import urllib
                assert 'urlopen' in dir(urllib)
                print('Import succeeded!')
                '''
        self._write_test_script(code2, 'module_importing_old_urllib.py')
        output = self._run_test_script('runme.py')
        print(output)
        self.assertTrue(True)

    def test_sys_intern(self):
        """
        Py2's builtin intern() has been moved to the sys module. Tests
        whether sys.intern is available.
        """
        from sys import intern
        if utils.PY3:
            self.assertEqual(intern('hello'), 'hello')
        else:
            # intern() requires byte-strings on Py2:
            self.assertEqual(intern(b'hello'), b'hello')

    def test_sys_maxsize(self):
        """
        Tests whether sys.maxsize is available.
        """
        from sys import maxsize
        self.assertTrue(maxsize > 0)

    def test_itertools_filterfalse(self):
        """
        Tests whether itertools.filterfalse is available.
        """
        from itertools import filterfalse
        not_div_by_3 = filterfalse(lambda x: x % 3 == 0, range(8))
        self.assertEqual(list(not_div_by_3), [1, 2, 4, 5, 7])

    def test_itertools_zip_longest(self):
        """
        Tests whether itertools.zip_longest is available.
        """
        from itertools import zip_longest
        a = (1, 2)
        b = [2, 4, 6]
        self.assertEqual(list(zip_longest(a, b)),
                         [(1, 2), (2, 4), (None, 6)])

    def test_ChainMap(self):
        """
        Tests whether collections.ChainMap is available.
        """
        from collections import ChainMap
        cm = ChainMap()

    @unittest.expectedFailure
    @unittest.skipIf(utils.PY3, 'generic import tests are for Py2 only')
    def test_import_failure_from_module(self):
        """
        Tests whether e.g. "import socketserver" succeeds in a module
        imported by another module that has used and removed the stdlib hooks.
        We want this to fail; the stdlib hooks should not bleed to imported
        modules too without their explicitly invoking them.
        """
        code1 = '''
                from future import standard_library
                standard_library.install_hooks()
                standard_library.remove_hooks()
                import importme2
                '''
        code2 = '''
                import socketserver
                print('Uh oh. importme2 should have raised an ImportError.')
                '''
        self._write_test_script(code1, 'importme1.py')
        self._write_test_script(code2, 'importme2.py')
        with self.assertRaises(CalledProcessError):
            output = self._run_test_script('importme1.py')

    # Disabled since v0.16.0:
    # def test_configparser(self):
    #     import configparser

    def test_copyreg(self):
        import copyreg

    def test_pickle(self):
        import pickle

    def test_profile(self):
        import profile

    def test_stringio(self):
        from io import StringIO
        s = StringIO(u'test')
        for method in ['tell', 'read', 'seek', 'close', 'flush']:
            self.assertTrue(hasattr(s, method))

    def test_bytesio(self):
        from io import BytesIO
        s = BytesIO(b'test')
        for method in ['tell', 'read', 'seek', 'close', 'flush', 'getvalue']:
            self.assertTrue(hasattr(s, method))

    def test_queue(self):
        import queue
        q = queue.Queue()
        q.put('thing')
        self.assertFalse(q.empty())

    def test_reprlib(self):
        import reprlib
        self.assertTrue(True)

    def test_socketserver(self):
        import socketserver
        self.assertTrue(True)

    @unittest.skip("Not testing tkinter import (it may be installed separately from Python)")
    def test_tkinter(self):
        import tkinter
        self.assertTrue(True)

    def test_builtins(self):
        import builtins
        self.assertTrue(hasattr(builtins, 'tuple'))

    @unittest.skip("ssl redirect support on pypi isn't working as expected for now ...")
    def test_urllib_request_ssl_redirect(self):
        """
        This site redirects to https://...
        It therefore requires ssl support.
        """
        import future.moves.urllib.request as urllib_request
        from pprint import pprint
        URL = 'http://pypi.python.org/pypi/{0}/json'
        package = 'future'
        r = urllib_request.urlopen(URL.format(package))
        # pprint(r.read().decode('utf-8'))
        self.assertTrue(True)

    def test_moves_urllib_request_http(self):
        """
        This site (python-future.org) uses plain http (as of 2014-09-23).
        """
        import future.moves.urllib.request as urllib_request
        from pprint import pprint
        URL = 'http://python-future.org'
        r = urllib_request.urlopen(URL)
        data = r.read()
        self.assertTrue(b'</html>' in data)

    def test_urllib_request_http(self):
        """
        This site (python-future.org) uses plain http (as of 2014-09-23).
        """
        import urllib.request as urllib_request
        from pprint import pprint
        URL = 'http://python-future.org'
        r = urllib_request.urlopen(URL)
        data = r.read()
        self.assertTrue(b'</html>' in data)

    def test_html_import(self):
        import html
        import html.entities
        import html.parser
        self.assertTrue(True)

    def test_http_client_import(self):
        import http.client
        self.assertTrue(True)

    def test_other_http_imports(self):
        import http
        import http.server
        import http.cookies
        import http.cookiejar
        self.assertTrue(True)

    def test_urllib_imports_moves(self):
        import future.moves.urllib
        import future.moves.urllib.parse
        import future.moves.urllib.request
        import future.moves.urllib.robotparser
        import future.moves.urllib.error
        import future.moves.urllib.response
        self.assertTrue(True)

    def test_urllib_imports_install_aliases(self):
        with standard_library.suspend_hooks():
            standard_library.install_aliases()
            import urllib
            import urllib.parse
            import urllib.request
            import urllib.robotparser
            import urllib.error
            import urllib.response
            self.assertTrue(True)

    def test_urllib_imports_cm(self):
        with standard_library.hooks():
            import urllib
            import urllib.parse
            import urllib.request
            import urllib.robotparser
            import urllib.error
            import urllib.response
        self.assertTrue(True)

    def test_urllib_imports_install_hooks(self):
        standard_library.remove_hooks()
        standard_library.install_hooks()
        import urllib
        import urllib.parse
        import urllib.request
        import urllib.robotparser
        import urllib.error
        import urllib.response
        self.assertTrue(True)

    def test_underscore_prefixed_modules(self):
        import _thread
        import _dummy_thread
        import _markupbase
        self.assertTrue(True)

    def test_reduce(self):
        """
        reduce has been moved to the functools module
        """
        import functools
        self.assertEqual(functools.reduce(lambda x, y: x+y, range(1, 6)), 15)

    def test_collections_userstuff(self):
        """
        UserDict, UserList, and UserString have been moved to the
        collections module.
        """
        from collections import UserDict
        from collections import UserList
        from collections import UserString
        self.assertTrue(True)

    def test_reload(self):
        """
        reload has been moved to the imp module
        """
        import imp
        imp.reload(imp)
        self.assertTrue(True)

    def test_install_aliases(self):
        """
        Does the install_aliases() interface monkey-patch urllib etc. successfully?
        """
        from future.standard_library import remove_hooks, install_aliases
        remove_hooks()
        install_aliases()

        from collections import Counter, OrderedDict   # backported to Py2.6
        from collections import UserDict, UserList, UserString

        # Requires Python dbm support:
        # import dbm
        # import dbm.dumb
        # import dbm.gnu
        # import dbm.ndbm

        from itertools import filterfalse, zip_longest

        from subprocess import check_output    # backported to Py2.6
        from subprocess import getoutput, getstatusoutput

        from sys import intern

        # test_support may not be available (e.g. on Anaconda Py2.6):
        # import test.support

        import urllib.error
        import urllib.parse
        import urllib.request
        import urllib.response
        import urllib.robotparser

        self.assertTrue('urlopen' in dir(urllib.request))


class TestFutureMoves(CodeHandler):
    def test_future_moves_urllib_request(self):
        from future.moves.urllib import request as urllib_request
        functions = ['getproxies',
                     'pathname2url',
                     'proxy_bypass',
                     'quote',
                     'request_host',
                     'splitattr',
                     'splithost',
                     'splitpasswd',
                     'splitport',
                     'splitquery',
                     'splittag',
                     'splittype',
                     'splituser',
                     'splitvalue',
                     'thishost',
                     'to_bytes',
                     'unquote',
                     # 'unquote_to_bytes',   # Is there an equivalent in the Py2 stdlib?
                     'unwrap',
                     'url2pathname',
                     'urlcleanup',
                     'urljoin',
                     'urlopen',
                     'urlparse',
                     'urlretrieve',
                     'urlsplit',
                     'urlunparse']
        self.assertTrue(all(fn in dir(urllib_request) for fn in functions))

    def test_future_moves(self):
        """
        Ensure everything is available from the future.moves interface that we
        claim and expect. (Issue #104).
        """
        from future.moves.collections import Counter, OrderedDict   # backported to Py2.6
        from future.moves.collections import UserDict, UserList, UserString

        from future.moves import configparser
        from future.moves import copyreg

        from future.moves.itertools import filterfalse, zip_longest

        from future.moves import html
        import future.moves.html.entities
        import future.moves.html.parser

        from future.moves import http
        import future.moves.http.client
        import future.moves.http.cookies
        import future.moves.http.cookiejar
        import future.moves.http.server

        from future.moves import queue

        from future.moves import socketserver

        from future.moves.subprocess import check_output              # even on Py2.6
        from future.moves.subprocess import getoutput, getstatusoutput

        from future.moves.sys import intern

        from future.moves import urllib
        import future.moves.urllib.error
        import future.moves.urllib.parse
        import future.moves.urllib.request
        import future.moves.urllib.response
        import future.moves.urllib.robotparser

        try:
            # Is _winreg available on Py2? If so, ensure future.moves._winreg is available too:
            import _winreg
        except ImportError:
            pass
        else:
            from future.moves import winreg

        from future.moves import xmlrpc
        import future.moves.xmlrpc.client
        import future.moves.xmlrpc.server

        from future.moves import _dummy_thread
        from future.moves import _markupbase
        from future.moves import _thread

    def test_future_moves_dbm(self):
        """
        Do the dbm imports work?
        """
        from future.moves import dbm
        dbm.ndbm
        from future.moves.dbm import dumb
        try:
            # Is gdbm available on Py2? If so, ensure dbm.gnu is available too:
            import gdbm
        except ImportError:
            pass
        else:
            from future.moves.dbm import gnu
        from future.moves.dbm import ndbm


# Running the following tkinter test causes the following bizzare test failure:
#
# ======================================================================
# FAIL: test_open_default_encoding (future.tests.test_builtins.BuiltinTest)
# ----------------------------------------------------------------------
# Traceback (most recent call last):
#   File "/home/user/Install/BleedingEdge/python-future/future/tests/test_builtins.py", line 1219, in test_open_default_encoding
#     self.assertEqual(fp.encoding, current_locale_encoding)
# AssertionError: 'ANSI_X3.4-1968' != 'ISO-8859-1'
#
# ----------------------------------------------------------------------
#
#     def test_future_moves_tkinter(self):
#         """
#         Do the tkinter imports work?
#         """
#         from future.moves import tkinter
#         from future.moves.tkinter import dialog
#         from future.moves.tkinter import filedialog
#         from future.moves.tkinter import scrolledtext
#         from future.moves.tkinter import simpledialog
#         from future.moves.tkinter import tix
#         from future.moves.tkinter import constants
#         from future.moves.tkinter import dnd
#         from future.moves.tkinter import colorchooser
#         from future.moves.tkinter import commondialog
#         from future.moves.tkinter import font
#         from future.moves.tkinter import messagebox

if __name__ == '__main__':
    unittest.main()
