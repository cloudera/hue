# -*- coding: utf-8 -*-
"""
Tests for the Py2-like class:`basestring` type.
"""

from __future__ import absolute_import, division, print_function
import os
import textwrap
import sys
import pprint
import tempfile
import os
import io
from subprocess import Popen, PIPE

from past import utils
from past.builtins import basestring, str as oldstr, unicode

from past.translation import install_hooks, remove_hooks, common_substring
from future.tests.base import (unittest, CodeHandler, skip26,
                               expectedFailurePY3, expectedFailurePY26)


class TestTranslate(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp() + os.path.sep

    # def tearDown(self):
    #     remove_hooks()

    def test_common_substring(self):
        s1 = '/home/user/anaconda/envs/future3/lib/python3.3/lib-dynload/math.cpython-33m.so'
        s2 = '/home/user/anaconda/envs/future3/lib/python3.3/urllib/__init__.py'
        c =  '/home/user/anaconda/envs/future3/lib/python3.3'
        self.assertEqual(c, common_substring(s1, s2))

        s1 = r'/Users/Fred Flintstone/Python3.3/lib/something'
        s2 = r'/Users/Fred Flintstone/Python3.3/lib/somethingelse'
        c =  r'/Users/Fred Flintstone/Python3.3/lib'
        self.assertEqual(c, common_substring(s1, s2))

    def write_and_import(self, code, modulename='mymodule'):
        self.assertTrue('.py' not in modulename)
        filename = modulename + '.py'
        if isinstance(code, bytes):
            code = code.decode('utf-8')
        # Be explicit about encoding the temp file as UTF-8 (issue #63):
        with io.open(self.tempdir + filename, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent(code).strip() + '\n')

        # meta_path_len = len(sys.meta_path)
        install_hooks(modulename)
        # print('Hooks installed')
        # assert len(sys.meta_path) == 1 + meta_path_len
        # print('sys.meta_path is: {0}'.format(sys.meta_path))
        module = None

        sys.path.insert(0, self.tempdir)
        try:
            module = __import__(modulename)
        except SyntaxError:
            print('Bombed!')
        else:
            print('Succeeded!')
        finally:
            remove_hooks()
            # print('Hooks removed')
            sys.path.remove(self.tempdir)
        return module
 
    def test_print_statement(self):
        code = """
            print 'Hello from a Python 2-style print statement!'
            finished = True
        """
        printer = self.write_and_import(code, 'printer')
        self.assertTrue(printer.finished)

    def test_exec_statement(self):
        code = """
            exec 'x = 5 + 2'
        """
        module = self.write_and_import(code, 'execer')
        self.assertEqual(module.x, 7)
        
    def test_div(self):
        code = """
        x = 3 / 2
        """
        module = self.write_and_import(code, 'div')
        self.assertEqual(module.x, 1)

    def test_import_future_standard_library(self):
        """
        Does futurized Py3-like code like this work under autotranslation??
        """
        code = """
        from future import standard_library
        standard_library.install_hooks()
        import configparser
        """
        module = self.write_and_import(code, 'future_standard_library')
        self.assertTrue('configparser' in dir(module))
        from future import standard_library
        standard_library.remove_hooks()

    def test_old_builtin_functions(self):
        code = """
        # a = raw_input()
        import sys
        b = open(sys.executable, 'rb')
        b.close()

        def is_even(x):
            return x % 2 == 0
        c = filter(is_even, range(10))

        def double(x):
            return x * 2
        d = map(double, c)

        e = isinstance('abcd', str)

        for g in xrange(10**3):
            pass

        # super(MyClass, self)
        """
        module = self.write_and_import(code, 'test_builtin_functions')
        self.assertTrue(hasattr(module.b, 'readlines'))
        self.assertTrue(isinstance(module.c, list))
        self.assertEqual(module.c, [0, 2, 4, 6, 8])
        self.assertEqual(module.d, [0, 4, 8, 12, 16])
        self.assertTrue(module.e)

    @expectedFailurePY3
    def test_import_builtin_types(self):
        code = """
        s1 = 'abcd'
        s2 = u'abcd'
        b1 = b'abcd'
        b2 = s2.encode('utf-8')
        d1 = {}
        d2 = dict((i, i**2) for i in range(10))
        i1 = 1923482349324234L
        i2 = 1923482349324234
        """
        module = self.write_and_import(code, 'test_builtin_types')
        self.assertTrue(isinstance(module.s1, oldstr))
        self.assertTrue(isinstance(module.s2, unicode))
        self.assertTrue(isinstance(module.b1, oldstr))

    def test_xrange(self):
        code = '''
        total = 0
        for i in xrange(10):
            total += i
        '''
        module = self.write_and_import(code, 'xrange')
        self.assertEqual(module.total, 45)

    def test_exception_syntax(self):
        """
        Test of whether futurize handles the old-style exception syntax
        """
        code = """
        value = 'string'
        try:
            value += 10
        except TypeError, e:    # old exception syntax
            value += ': success!'
        """
        module = self.write_and_import(code, 'py2_exceptions')
        self.assertEqual(module.value, 'string: success!')

 
# class TestFuturizeSimple(CodeHandler):
#     """
#     This class contains snippets of Python 2 code (invalid Python 3) and
#     tests for whether they can be imported correctly from Python 3 with the
#     import hooks.
#     """
# 
#     @unittest.expectedFailure
#     def test_problematic_string(self):
#         """ This string generates a SyntaxError on Python 3 unless it has
#         an r prefix.
#         """
#         before = r"""
#         s = 'The folder is "C:\Users"'.
#         """
#         after = r"""
#         s = r'The folder is "C:\Users"'.
#         """
#         self.convert_check(before, after)
# 
#     def test_tobytes(self):
#         """
#         The --tobytes option converts all UNADORNED string literals 'abcd' to b'abcd'.
#         It does apply to multi-line strings but doesn't apply if it's a raw
#         string, because ur'abcd' is a SyntaxError on Python 2 and br'abcd' is a
#         SyntaxError on Python 3.
#         """
#         before = r"""
#         s0 = '1234'
#         s1 = '''5678
#         '''
#         s2 = "9abc"
#         # Unchanged:
#         s3 = r'1234'
#         s4 = R"defg"
#         s5 = u'hijk'
#         s6 = u"lmno"
#         s7 = b'lmno'
#         s8 = b"pqrs"
#         """
#         after = r"""
#         s0 = b'1234'
#         s1 = b'''5678
#         '''
#         s2 = b"9abc"
#         # Unchanged:
#         s3 = r'1234'
#         s4 = R"defg"
#         s5 = u'hijk'
#         s6 = u"lmno"
#         s7 = b'lmno'
#         s8 = b"pqrs"
#         """
#         self.convert_check(before, after, tobytes=True)
# 
#     @unittest.expectedFailure
#     def test_izip(self):
#         before = """
#         from itertools import izip
#         for (a, b) in izip([1, 3, 5], [2, 4, 6]):
#             pass
#         """
#         after = """
#         from __future__ import unicode_literals
#         from future.builtins import zip
#         for (a, b) in zip([1, 3, 5], [2, 4, 6]):
#             pass
#         """
#         self.convert_check(before, after, stages=(1, 2), ignore_imports=False)
# 
#     @unittest.expectedFailure
#     def test_no_unneeded_list_calls(self):
#         """
#         TODO: get this working
#         """
#         code = """
#         for (a, b) in zip(range(3), range(3, 6)):
#             pass
#         """
#         self.unchanged(code)
# 
#     def test_xrange(self):
#         code = '''
#         for i in xrange(10):
#             pass
#         '''
#         self.convert(code)
#     
#     @unittest.expectedFailure
#     def test_source_coding_utf8(self):
#         """
#         Tests to ensure that the source coding line is not corrupted or
#         removed. It must be left as the first line in the file (including
#         before any __future__ imports). Also tests whether the unicode
#         characters in this encoding are parsed correctly and left alone.
#         """
#         code = """
#         # -*- coding: utf-8 -*-
#         icons = [u"◐", u"◓", u"◑", u"◒"]
#         """
#         self.unchanged(code)
# 
#     def test_exception_syntax(self):
#         """
#         Test of whether futurize handles the old-style exception syntax
#         """
#         before = """
#         try:
#             pass
#         except IOError, e:
#             val = e.errno
#         """
#         after = """
#         try:
#             pass
#         except IOError as e:
#             val = e.errno
#         """
#         self.convert_check(before, after)
# 
#     def test_super(self):
#         """
#         This tests whether futurize keeps the old two-argument super() calls the
#         same as before. It should, because this still works in Py3.
#         """
#         code = '''
#         class VerboseList(list):
#             def append(self, item):
#                 print('Adding an item')
#                 super(VerboseList, self).append(item)
#         '''
#         self.unchanged(code)
# 
#     @unittest.expectedFailure
#     def test_file(self):
#         """
#         file() as a synonym for open() is obsolete and invalid on Python 3.
#         """
#         before = '''
#         f = file(__file__)
#         data = f.read()
#         f.close()
#         '''
#         after = '''
#         f = open(__file__)
#         data = f.read()
#         f.close()
#         '''
#         self.convert_check(before, after)
# 
#     def test_apply(self):
#         before = '''
#         def addup(*x):
#             return sum(x)
#         
#         assert apply(addup, (10,20)) == 30
#         '''
#         after = """
#         def addup(*x):
#             return sum(x)
#         
#         assert addup(*(10,20)) == 30
#         """
#         self.convert_check(before, after)
#     
#     @unittest.skip('not implemented yet')
#     def test_download_pypi_package_and_test(self, package_name='future'):
#         URL = 'http://pypi.python.org/pypi/{0}/json'
#         
#         import requests
#         r = requests.get(URL.format(package_name))
#         pprint.pprint(r.json())
#         
#         download_url = r.json()['urls'][0]['url']
#         filename = r.json()['urls'][0]['filename']
#         # r2 = requests.get(download_url)
#         # with open('/tmp/' + filename, 'w') as tarball:
#         #     tarball.write(r2.content)
# 
#     def test_raw_input(self):
#         """
#         Passes in a string to the waiting input() after futurize
#         conversion.
# 
#         The code is the first snippet from these docs:
#             http://docs.python.org/2/library/2to3.html
#         """
#         before = """
#         def greet(name):
#             print "Hello, {0}!".format(name)
#         print "What's your name?"
#         name = raw_input()
#         greet(name)
#         """
#         desired = """
#         def greet(name):
#             print("Hello, {0}!".format(name))
#         print("What's your name?")
#         name = input()
#         greet(name)
#         """
#         self.convert_check(before, desired, run=False)
# 
#         for interpreter in self.interpreters:
#             p1 = Popen([interpreter, self.tempdir + 'mytestscript.py'],
#                        stdout=PIPE, stdin=PIPE, stderr=PIPE)
#             (stdout, stderr) = p1.communicate(b'Ed')
#             self.assertEqual(stdout, b"What's your name?\nHello, Ed!\n")
# 
#     def test_literal_prefixes_are_not_stripped(self):
#         """
#         Tests to ensure that the u'' and b'' prefixes on unicode strings and
#         byte strings are not removed by the futurize script.  Removing the
#         prefixes on Py3.3+ is unnecessary and loses some information -- namely,
#         that the strings have explicitly been marked as unicode or bytes,
#         rather than just e.g. a guess by some automated tool about what they
#         are.
#         """
#         code = '''
#         s = u'unicode string'
#         b = b'byte string'
#         '''
#         self.unchanged(code)
# 
#     @unittest.expectedFailure
#     def test_division(self):
#         """
#         TODO: implement this!
#         """
#         before = """
#         x = 1 / 2
#         """
#         after = """
#         from future.utils import old_div
#         x = old_div(1, 2)
#         """
#         self.convert_check(before, after, stages=[1])
# 
# 
# class TestFuturizeRenamedStdlib(CodeHandler):
#     def test_renamed_modules(self):
#         before = """
#         import ConfigParser
#         import copy_reg
#         import cPickle
#         import cStringIO
# 
#         s = cStringIO.StringIO('blah')
#         """
#         after = """
#         import configparser
#         import copyreg
#         import pickle
#         import io
# 
#         s = io.StringIO('blah')
#         """
#         self.convert_check(before, after)
#     
#     @unittest.expectedFailure
#     def test_urllib_refactor(self):
#         # Code like this using urllib is refactored by futurize --stage2 to use
#         # the new Py3 module names, but ``future`` doesn't support urllib yet.
#         before = """
#         import urllib
# 
#         URL = 'http://pypi.python.org/pypi/future/json'
#         package_name = 'future'
#         r = urllib.urlopen(URL.format(package_name))
#         data = r.read()
#         """
#         after = """
#         import urllib.request
#         
#         URL = 'http://pypi.python.org/pypi/future/json'
#         package_name = 'future'
#         r = urllib.request.urlopen(URL.format(package_name))
#         data = r.read()
#         """
#         self.convert_check(before, after)
# 
#     def test_renamed_copy_reg_and_cPickle_modules(self):
#         """
#         Example from docs.python.org/2/library/copy_reg.html
#         """
#         before = """
#         import copy_reg
#         import copy
#         import cPickle
#         class C(object):
#             def __init__(self, a):
#                 self.a = a
# 
#         def pickle_c(c):
#             print('pickling a C instance...')
#             return C, (c.a,)
# 
#         copy_reg.pickle(C, pickle_c)
#         c = C(1)
#         d = copy.copy(c)
#         p = cPickle.dumps(c)
#         """
#         after = """
#         import copyreg
#         import copy
#         import pickle
#         class C(object):
#             def __init__(self, a):
#                 self.a = a
# 
#         def pickle_c(c):
#             print('pickling a C instance...')
#             return C, (c.a,)
# 
#         copyreg.pickle(C, pickle_c)
#         c = C(1)
#         d = copy.copy(c)
#         p = pickle.dumps(c)
#         """
#         self.convert_check(before, after)
# 
#     @unittest.expectedFailure
#     def test_Py2_StringIO_module(self):
#         """
#         Ideally, there would be a fixer for this. For now:
# 
#         TODO: add the Py3 equivalent for this to the docs
#         """
#         before = """
#         import cStringIO
#         s = cStringIO.StringIO('my string')
#         assert isinstance(s, cStringIO.InputType)
#         """
#         after = """
#         import io
#         s = io.StringIO('my string')
#         # assert isinstance(s, io.InputType)
#         # There is no io.InputType in Python 3. What should we change this to
#         # instead?
#         """
#         self.convert_check(before, after)
# 
# 
# class TestFuturizeStage1(CodeHandler):
#     # """
#     # Tests "stage 1": safe optimizations: modernizing Python 2 code so that it
#     # uses print functions, new-style exception syntax, etc.
# 
#     # The behaviour should not change and this should introduce no dependency on
#     # the ``future`` package. It produces more modern Python 2-only code. The
#     # goal is to reduce the size of the real porting patch-set by performing
#     # the uncontroversial patches first.
#     # """
# 
#     def test_apply(self):
#         """
#         apply() should be changed by futurize --stage1
#         """
#         before = '''
#         def f(a, b):
#             return a + b
# 
#         args = (1, 2)
#         assert apply(f, args) == 3
#         assert apply(f, ('a', 'b')) == 'ab'
#         '''
#         after = '''
#         def f(a, b):
#             return a + b
# 
#         args = (1, 2)
#         assert f(*args) == 3
#         assert f(*('a', 'b')) == 'ab'
#         '''
#         self.convert_check(before, after, stages=[1])
# 
#     def test_xrange(self):
#         """
#         xrange should not be changed by futurize --stage1
#         """
#         code = '''
#         for i in xrange(10):
#             pass
#         '''
#         self.unchanged(code, stages=[1])
# 
#     @unittest.expectedFailure
#     def test_absolute_import_changes(self):
#         """
#         Implicit relative imports should be converted to absolute or explicit
#         relative imports correctly.
# 
#         Issue #16 (with porting bokeh/bbmodel.py)
#         """
#         with open('specialmodels.py', 'w') as f:
#             f.write('pass')
# 
#         before = """
#         import specialmodels.pandasmodel
#         specialmodels.pandasmodel.blah()
#         """
#         after = """
#         from __future__ import absolute_import
#         from .specialmodels import pandasmodel
#         pandasmodel.blah()
#         """
#         self.convert_check(before, after, stages=[1])
# 
#     def test_safe_futurize_imports(self):
#         """
#         The standard library module names should not be changed until stage 2
#         """
#         before = """
#         import ConfigParser
#         import HTMLParser
#         import collections
# 
#         ConfigParser.ConfigParser
#         HTMLParser.HTMLParser
#         d = collections.OrderedDict()
#         """
#         self.unchanged(before, stages=[1])
# 
#     def test_print(self):
#         before = """
#         print 'Hello'
#         """
#         after = """
#         print('Hello')
#         """
#         self.convert_check(before, after, stages=[1])
# 
#         before = """
#         import sys
#         print >> sys.stderr, 'Hello', 'world'
#         """
#         after = """
#         import sys
#         print('Hello', 'world', file=sys.stderr)
#         """
#         self.convert_check(before, after, stages=[1])
# 
#     def test_print_already_function(self):
#         """
#         Running futurize --stage1 should not add a second set of parentheses 
#         """
#         before = """
#         print('Hello')
#         """
#         self.unchanged(before, stages=[1])
# 
#     @unittest.expectedFailure
#     def test_print_already_function_complex(self):
#         """
#         Running futurize --stage1 does add a second second set of parentheses
#         in this case. This is because the underlying lib2to3 has two distinct
#         grammars -- with a print statement and with a print function -- and,
#         when going forwards (2 to both), futurize assumes print is a statement,
#         which raises a ParseError.
#         """
#         before = """
#         import sys
#         print('Hello', 'world', file=sys.stderr)
#         """
#         self.unchanged(before, stages=[1])
# 
#     def test_exceptions(self):
#         before = """
#         try:
#             raise AttributeError('blah')
#         except AttributeError, e:
#             pass
#         """
#         after = """
#         try:
#             raise AttributeError('blah')
#         except AttributeError as e:
#             pass
#         """
#         self.convert_check(before, after, stages=[1])
# 
#     @unittest.expectedFailure
#     def test_string_exceptions(self):
#         """
#         2to3 does not convert string exceptions: see
#         http://python3porting.com/differences.html.
#         """
#         before = """
#         try:
#             raise "old string exception"
#         except Exception, e:
#             pass
#         """
#         after = """
#         try:
#             raise Exception("old string exception")
#         except Exception as e:
#             pass
#         """
#         self.convert_check(before, after, stages=[1])
# 
#     @unittest.expectedFailure
#     def test_oldstyle_classes(self):
#         """
#         We don't convert old-style classes to new-style automatically. Should we?
#         """
#         before = """
#         class Blah:
#             pass
#         """
#         after = """
#         class Blah(object):
#             pass
#         """
#         self.convert_check(before, after, stages=[1])
# 
#         
#     def test_octal_literals(self):
#         before = """
#         mode = 0644
#         """
#         after = """
#         mode = 0o644
#         """
#         self.convert_check(before, after)
# 
#     def test_long_int_literals(self):
#         before = """
#         bignumber = 12345678901234567890L
#         """
#         after = """
#         bignumber = 12345678901234567890
#         """
#         self.convert_check(before, after)
# 
#     def test___future___import_position(self):
#         """
#         Issue #4: __future__ imports inserted too low in file: SyntaxError
#         """
#         code = """
#         # Comments here
#         # and here
#         __version__=''' $Id$ '''
#         __doc__="A Sequencer class counts things. It aids numbering and formatting lists."
#         __all__='Sequencer getSequencer setSequencer'.split()
#         #
#         # another comment
#         #
#         
#         CONSTANTS = [ 0, 01, 011, 0111, 012, 02, 021, 0211, 02111, 013 ]
#         _RN_LETTERS = "IVXLCDM"
#         
#         def my_func(value):
#             pass
#         
#         ''' Docstring-like comment here '''
#         """
#         self.convert(code)


if __name__ == '__main__':
    unittest.main()

