# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import pprint
import tempfile
from subprocess import Popen, PIPE
import os

from libfuturize.fixer_util import is_shebang_comment, is_encoding_comment
from lib2to3.fixer_util import FromImport
from lib2to3.pytree import Leaf, Node
from lib2to3.pygram import token

from future.tests.base import (CodeHandler, unittest, skip26, reformat_code,
                               order_future_lines, expectedFailurePY26)
from future.utils import PY2


class TestLibFuturize(unittest.TestCase):

    def setUp(self):
        # For tests that need a text file:
        _, self.textfilename = tempfile.mkstemp(text=True)
        super(TestLibFuturize, self).setUp()

    def tearDown(self):
        os.unlink(self.textfilename)

    def test_correct_exit_status(self):
        """
        Issue #119: futurize and pasteurize were not exiting with the correct
        status code. This is because the status code returned from
        libfuturize.main.main() etc. was a ``newint``, which sys.exit() always
        translates into 1!
        """
        from libfuturize.main import main
        retcode = main([self.textfilename])
        self.assertTrue(isinstance(retcode, int))   # i.e. Py2 builtin int

    def test_is_shebang_comment(self):
        """
        Tests whether the fixer_util.is_encoding_comment() function is working.
        """
        shebang_comments = [u'#!/usr/bin/env python\n'
                             u"#!/usr/bin/python2\n",
                             u"#! /usr/bin/python3\n",
                            ]
        not_shebang_comments = [u"# I saw a giant python\n",
                                 u"# I have never seen a python2\n",
                               ]
        for comment in shebang_comments:
            node = FromImport(u'math', [Leaf(token.NAME, u'cos', prefix=" ")])
            node.prefix = comment
            self.assertTrue(is_shebang_comment(node))

        for comment in not_shebang_comments:
            node = FromImport(u'math', [Leaf(token.NAME, u'cos', prefix=" ")])
            node.prefix = comment
            self.assertFalse(is_shebang_comment(node))


    def test_is_encoding_comment(self):
        """
        Tests whether the fixer_util.is_encoding_comment() function is working.
        """
        encoding_comments = [u"# coding: utf-8",
                             u"# encoding: utf-8",
                             u"# -*- coding: latin-1 -*-",
                             u"# vim: set fileencoding=iso-8859-15 :",
                            ]
        not_encoding_comments = [u"# We use the file encoding utf-8",
                                 u"coding = 'utf-8'",
                                 u"encoding = 'utf-8'",
                                ]
        for comment in encoding_comments:
            node = FromImport(u'math', [Leaf(token.NAME, u'cos', prefix=" ")])
            node.prefix = comment
            self.assertTrue(is_encoding_comment(node))

        for comment in not_encoding_comments:
            node = FromImport(u'math', [Leaf(token.NAME, u'cos', prefix=" ")])
            node.prefix = comment
            self.assertFalse(is_encoding_comment(node))


class TestFuturizeSimple(CodeHandler):
    """
    This class contains snippets of Python 2 code (invalid Python 3) and
    tests for whether they can be passed to ``futurize`` and immediately
    run under both Python 2 again and Python 3.
    """

    def test_encoding_comments_kept_at_top(self):
        """
        Issues #10 and #97: If there is a source encoding comment line
        (PEP 263), is it kept at the top of a module by ``futurize``?
        """
        before = """
        # coding=utf-8

        print 'Hello'
        """
        after = """
        # coding=utf-8

        from __future__ import print_function
        print('Hello')
        """
        self.convert_check(before, after)

        before = """
        #!/usr/bin/env python
        # -*- coding: latin-1 -*-"

        print 'Hello'
        """
        after = """
        #!/usr/bin/env python
        # -*- coding: latin-1 -*-"

        from __future__ import print_function
        print('Hello')
        """
        self.convert_check(before, after)

    def test_multiline_future_import(self):
        """
        Issue #113: don't crash if a future import has multiple lines
        """
        text = """
        from __future__ import (
            division
        )
        """
        self.convert(text)

    def test_shebang_blank_with_future_division_import(self):
        """
        Issue #43: Is shebang line preserved as the first
        line by futurize when followed by a blank line?
        """
        before = """
        #!/usr/bin/env python

        import math
        1 / 5
        """
        after = """
        #!/usr/bin/env python

        from __future__ import division
        from past.utils import old_div
        import math
        old_div(1, 5)
        """
        self.convert_check(before, after)

    def test_shebang_blank_with_print_import(self):
        before = """
        #!/usr/bin/env python

        import math
        print 'Hello'
        """
        after = """
        #!/usr/bin/env python
        from __future__ import print_function

        import math
        print('Hello')
        """
        self.convert_check(before, after)

    def test_shebang_comment(self):
        """
        Issue #43: Is shebang line preserved as the first
        line by futurize when followed by a comment?
        """
        before = """
        #!/usr/bin/env python
        # some comments
        # and more comments

        import math
        print 'Hello!'
        """
        after = """
        #!/usr/bin/env python
        # some comments
        # and more comments
        from __future__ import print_function

        import math
        print('Hello!')
        """
        self.convert_check(before, after)

    def test_shebang_docstring(self):
        """
        Issue #43: Is shebang line preserved as the first
        line by futurize when followed by a docstring?
        """
        before = '''
        #!/usr/bin/env python
        """
        a doc string
        """
        import math
        print 'Hello!'
        '''
        after = '''
        #!/usr/bin/env python
        """
        a doc string
        """
        from __future__ import print_function
        import math
        print('Hello!')
        '''
        self.convert_check(before, after)

    def test_oldstyle_classes(self):
        """
        Stage 2 should convert old-style to new-style classes. This makes
        the new-style class explicit and reduces the gap between the
        behaviour (e.g.  method resolution order) on Py2 and Py3. It also
        allows us to provide ``newobject`` (see
        test_oldstyle_classes_iterator).
        """
        before = """
        class Blah:
            pass
        """
        after = """
        from builtins import object
        class Blah(object):
            pass
        """
        self.convert_check(before, after, ignore_imports=False)

    def test_oldstyle_classes_iterator(self):
        """
        An old-style class used as an iterator should be converted
        properly. This requires ``futurize`` to do both steps (adding
        inheritance from object and adding the newobject import) in the
        right order. Any next() method should also be renamed to __next__.
        """
        before = """
        class Upper:
            def __init__(self, iterable):
                self._iter = iter(iterable)
            def next(self):
                return next(self._iter).upper()
            def __iter__(self):
                return self

        assert list(Upper('hello')) == list('HELLO')
        """
        after = """
        from builtins import next
        from builtins import object
        class Upper(object):
            def __init__(self, iterable):
                self._iter = iter(iterable)
            def __next__(self):
                return next(self._iter).upper()
            def __iter__(self):
                return self

        assert list(Upper('hello')) == list('HELLO')
        """
        self.convert_check(before, after, ignore_imports=False)

        # Try it again with this convention: class Upper():
        before2 = """
        class Upper():
            def __init__(self, iterable):
                self._iter = iter(iterable)
            def next(self):
                return next(self._iter).upper()
            def __iter__(self):
                return self

        assert list(Upper('hello')) == list('HELLO')
        """
        self.convert_check(before2, after)

    @unittest.expectedFailure
    def test_problematic_string(self):
        """ This string generates a SyntaxError on Python 3 unless it has
        an r prefix.
        """
        before = r"""
        s = 'The folder is "C:\Users"'.
        """
        after = r"""
        s = r'The folder is "C:\Users"'.
        """
        self.convert_check(before, after)

    @unittest.skip('--tobytes feature removed for now ...')
    def test_tobytes(self):
        """
        The --tobytes option converts all UNADORNED string literals 'abcd' to b'abcd'.
        It does apply to multi-line strings but doesn't apply if it's a raw
        string, because ur'abcd' is a SyntaxError on Python 2 and br'abcd' is a
        SyntaxError on Python 3.
        """
        before = r"""
        s0 = '1234'
        s1 = '''5678
        '''
        s2 = "9abc"
        # Unchanged:
        s3 = r'1234'
        s4 = R"defg"
        s5 = u'hijk'
        s6 = u"lmno"
        s7 = b'lmno'
        s8 = b"pqrs"
        """
        after = r"""
        s0 = b'1234'
        s1 = b'''5678
        '''
        s2 = b"9abc"
        # Unchanged:
        s3 = r'1234'
        s4 = R"defg"
        s5 = u'hijk'
        s6 = u"lmno"
        s7 = b'lmno'
        s8 = b"pqrs"
        """
        self.convert_check(before, after, tobytes=True)

    def test_cmp(self):
        before = """
        assert cmp(1, 2) == -1
        assert cmp(2, 1) == 1
        """
        after = """
        from past.builtins import cmp
        assert cmp(1, 2) == -1
        assert cmp(2, 1) == 1
        """
        self.convert_check(before, after, stages=(1, 2), ignore_imports=False)

    def test_execfile(self):
        before = """
        with open('mytempfile.py', 'w') as f:
            f.write('x = 1')
        execfile('mytempfile.py')
        x += 1
        assert x == 2
        """
        after = """
        from past.builtins import execfile
        with open('mytempfile.py', 'w') as f:
            f.write('x = 1')
        execfile('mytempfile.py')
        x += 1
        assert x == 2
        """
        self.convert_check(before, after, stages=(1, 2), ignore_imports=False)

    @unittest.expectedFailure
    def test_izip(self):
        before = """
        from itertools import izip
        for (a, b) in izip([1, 3, 5], [2, 4, 6]):
            pass
        """
        after = """
        from builtins import zip
        for (a, b) in zip([1, 3, 5], [2, 4, 6]):
            pass
        """
        self.convert_check(before, after, stages=(1, 2), ignore_imports=False)

    def test_UserList(self):
        before = """
        from UserList import UserList
        a = UserList([1, 3, 5])
        assert len(a) == 3
        """
        after = """
        from collections import UserList
        a = UserList([1, 3, 5])
        assert len(a) == 3
        """
        self.convert_check(before, after, stages=(1, 2), ignore_imports=True)

    @unittest.expectedFailure
    def test_no_unneeded_list_calls(self):
        """
        TODO: get this working
        """
        code = """
        for (a, b) in zip(range(3), range(3, 6)):
            pass
        """
        self.unchanged(code)

    @expectedFailurePY26
    def test_import_builtins(self):
        before = """
        a = raw_input()
        b = open(a, b, c)
        c = filter(a, b)
        d = map(a, b)
        e = isinstance(a, str)
        f = bytes(a, encoding='utf-8')
        for g in xrange(10**10):
            pass
        h = reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])
        super(MyClass, self)
        """
        after = """
        from builtins import bytes
        from builtins import filter
        from builtins import input
        from builtins import map
        from builtins import range
        from functools import reduce
        a = input()
        b = open(a, b, c)
        c = list(filter(a, b))
        d = list(map(a, b))
        e = isinstance(a, str)
        f = bytes(a, encoding='utf-8')
        for g in range(10**10):
            pass
        h = reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])
        super(MyClass, self)
        """
        self.convert_check(before, after, ignore_imports=False, run=False)

    def test_xrange(self):
        """
        The ``from builtins import range`` line was being added to the
        bottom of the file as of v0.11.4, but only using Py2.7's lib2to3.
        (Py3.3's lib2to3 seems to work.)
        """
        before = """
        for i in xrange(10):
            pass
        """
        after = """
        from builtins import range
        for i in range(10):
            pass
        """
        self.convert_check(before, after, ignore_imports=False)

    def test_source_coding_utf8(self):
        """
        Tests to ensure that the source coding line is not corrupted or
        removed. It must be left as the first line in the file (including
        before any __future__ imports). Also tests whether the unicode
        characters in this encoding are parsed correctly and left alone.
        """
        code = """
        # -*- coding: utf-8 -*-
        icons = [u"◐", u"◓", u"◑", u"◒"]
        """

    def test_exception_syntax(self):
        """
        Test of whether futurize handles the old-style exception syntax
        """
        before = """
        try:
            pass
        except IOError, e:
            val = e.errno
        """
        after = """
        try:
            pass
        except IOError as e:
            val = e.errno
        """
        self.convert_check(before, after)

    def test_super(self):
        """
        This tests whether futurize keeps the old two-argument super() calls the
        same as before. It should, because this still works in Py3.
        """
        code = '''
        class VerboseList(list):
            def append(self, item):
                print('Adding an item')
                super(VerboseList, self).append(item)
        '''
        self.unchanged(code)

    @unittest.expectedFailure
    def test_file(self):
        """
        file() as a synonym for open() is obsolete and invalid on Python 3.
        """
        before = '''
        f = file(self.textfilename)
        data = f.read()
        f.close()
        '''
        after = '''
        f = open(__file__)
        data = f.read()
        f.close()
        '''
        self.convert_check(before, after)

    def test_apply(self):
        before = '''
        def addup(*x):
            return sum(x)

        assert apply(addup, (10,20)) == 30
        '''
        after = """
        def addup(*x):
            return sum(x)

        assert addup(*(10,20)) == 30
        """
        self.convert_check(before, after)

    @unittest.skip('not implemented yet')
    def test_download_pypi_package_and_test(self):
        URL = 'http://pypi.python.org/pypi/{0}/json'

        import requests
        package = 'future'
        r = requests.get(URL.format(package))
        pprint.pprint(r.json())

        download_url = r.json()['urls'][0]['url']
        filename = r.json()['urls'][0]['filename']
        # r2 = requests.get(download_url)
        # with open('/tmp/' + filename, 'w') as tarball:
        #     tarball.write(r2.content)

    @expectedFailurePY26
    def test_raw_input(self):
        """
        Passes in a string to the waiting input() after futurize
        conversion.

        The code is the first snippet from these docs:
            http://docs.python.org/2/library/2to3.html
        """
        before = """
        from io import BytesIO
        def greet(name):
            print "Hello, {0}!".format(name)
        print "What's your name?"
        import sys
        oldstdin = sys.stdin

        sys.stdin = BytesIO(b'Ed\\n')
        name = raw_input()
        greet(name.decode())

        sys.stdin = oldstdin
        assert name == b'Ed'
        """
        desired = """
        from io import BytesIO
        def greet(name):
            print("Hello, {0}!".format(name))
        print("What's your name?")
        import sys
        oldstdin = sys.stdin

        sys.stdin = BytesIO(b'Ed\\n')
        name = input()
        greet(name.decode())

        sys.stdin = oldstdin
        assert name == b'Ed'
        """
        self.convert_check(before, desired, run=False)

        for interpreter in self.interpreters:
            p1 = Popen([interpreter, self.tempdir + 'mytestscript.py'],
                       stdout=PIPE, stdin=PIPE, stderr=PIPE)
            (stdout, stderr) = p1.communicate(b'Ed')
            self.assertEqual(stderr, b'')
            self.assertEqual(stdout, b"What's your name?\nHello, Ed!\n")

    def test_literal_prefixes_are_not_stripped(self):
        """
        Tests to ensure that the u'' and b'' prefixes on unicode strings and
        byte strings are not removed by the futurize script.  Removing the
        prefixes on Py3.3+ is unnecessary and loses some information -- namely,
        that the strings have explicitly been marked as unicode or bytes,
        rather than just e.g. a guess by some automated tool about what they
        are.
        """
        code = '''
        s = u'unicode string'
        b = b'byte string'
        '''
        self.unchanged(code)

    def test_division(self):
        before = """
        x = 1 / 2
        """
        after = """
        from past.utils import old_div
        x = old_div(1, 2)
        """
        self.convert_check(before, after, stages=[1, 2])

    def test_already_future_division(self):
        code = """
        from __future__ import division
        x = 1 / 2
        assert x == 0.5
        y = 3. / 2.
        assert y == 1.5
        """
        self.unchanged(code)


class TestFuturizeRenamedStdlib(CodeHandler):
    @unittest.skip('Infinite loop?')
    def test_renamed_modules(self):
        before = """
        import ConfigParser
        import copy_reg
        import cPickle
        import cStringIO
        """
        after = """
        import configparser
        import copyreg
        import pickle
        import io
        """
        # We can't run the converted code because configparser may
        # not be there.
        self.convert_check(before, after, run=False)

    @unittest.skip('Not working yet ...')
    def test_urllib_refactor(self):
        # Code like this using urllib is refactored by futurize --stage2 to use
        # the new Py3 module names, but ``future`` doesn't support urllib yet.
        before = """
        import urllib

        URL = 'http://pypi.python.org/pypi/future/json'
        package = 'future'
        r = urllib.urlopen(URL.format(package))
        data = r.read()
        """
        after = """
        from future import standard_library
        standard_library.install_aliases()
        import urllib.request

        URL = 'http://pypi.python.org/pypi/future/json'
        package = 'future'
        r = urllib.request.urlopen(URL.format(package))
        data = r.read()
        """
        self.convert_check(before, after)

    @unittest.skip('Infinite loop?')
    def test_renamed_copy_reg_and_cPickle_modules(self):
        """
        Example from docs.python.org/2/library/copy_reg.html
        """
        before = """
        import copy_reg
        import copy
        import cPickle
        class C(object):
            def __init__(self, a):
                self.a = a

        def pickle_c(c):
            print('pickling a C instance...')
            return C, (c.a,)

        copy_reg.pickle(C, pickle_c)
        c = C(1)
        d = copy.copy(c)
        p = cPickle.dumps(c)
        """
        after = """
        import copyreg
        import copy
        import pickle
        class C(object):
            def __init__(self, a):
                self.a = a

        def pickle_c(c):
            print('pickling a C instance...')
            return C, (c.a,)

        copyreg.pickle(C, pickle_c)
        c = C(1)
        d = copy.copy(c)
        p = pickle.dumps(c)
        """
        self.convert_check(before, after)

    @unittest.expectedFailure
    def test_Py2_StringIO_module(self):
        """
        This requires that the argument to io.StringIO be made a
        unicode string explicitly if we're not using unicode_literals:

        Ideally, there would be a fixer for this. For now:

        TODO: add the Py3 equivalent for this to the docs. Also add back
        a test for the unicode_literals case.
        """
        before = """
        import cStringIO
        import StringIO
        s1 = cStringIO.StringIO('my string')
        s2 = StringIO.StringIO('my other string')
        assert isinstance(s1, cStringIO.InputType)
        """

        # There is no io.InputType in Python 3. futurize should change this to
        # something like this. But note that the input to io.StringIO
        # must be a unicode string on both Py2 and Py3.
        after = """
        import io
        import io
        s1 = io.StringIO(u'my string')
        s2 = io.StringIO(u'my other string')
        assert isinstance(s1, io.StringIO)
        """
        self.convert_check(before, after)


class TestFuturizeStage1(CodeHandler):
    """
    Tests "stage 1": safe optimizations: modernizing Python 2 code so that it
    uses print functions, new-style exception syntax, etc.

    The behaviour should not change and this should introduce no dependency on
    the ``future`` package. It produces more modern Python 2-only code. The
    goal is to reduce the size of the real porting patch-set by performing
    the uncontroversial patches first.
    """

    def test_apply(self):
        """
        apply() should be changed by futurize --stage1
        """
        before = '''
        def f(a, b):
            return a + b

        args = (1, 2)
        assert apply(f, args) == 3
        assert apply(f, ('a', 'b')) == 'ab'
        '''
        after = '''
        def f(a, b):
            return a + b

        args = (1, 2)
        assert f(*args) == 3
        assert f(*('a', 'b')) == 'ab'
        '''
        self.convert_check(before, after, stages=[1])

    def test_next_1(self):
        """
        Custom next methods should not be converted to __next__ in stage1, but
        any obj.next() calls should be converted to next(obj).
        """
        before = """
        class Upper:
            def __init__(self, iterable):
                self._iter = iter(iterable)
            def next(self):                 # note the Py2 interface
                return next(self._iter).upper()
            def __iter__(self):
                return self

        itr = Upper('hello')
        assert itr.next() == 'H'
        assert next(itr) == 'E'
        assert list(itr) == list('LLO')
        """

        after = """
        class Upper:
            def __init__(self, iterable):
                self._iter = iter(iterable)
            def next(self):                 # note the Py2 interface
                return next(self._iter).upper()
            def __iter__(self):
                return self

        itr = Upper('hello')
        assert next(itr) == 'H'
        assert next(itr) == 'E'
        assert list(itr) == list('LLO')
        """
        self.convert_check(before, after, stages=[1], run=PY2)

    @unittest.expectedFailure
    def test_next_2(self):
        """
        This version of the above doesn't currently work: the self._iter.next() call in
        line 5 isn't converted to next(self._iter).
        """
        before = """
        class Upper:
            def __init__(self, iterable):
                self._iter = iter(iterable)
            def next(self):                 # note the Py2 interface
                return self._iter.next().upper()
            def __iter__(self):
                return self

        itr = Upper('hello')
        assert itr.next() == 'H'
        assert next(itr) == 'E'
        assert list(itr) == list('LLO')
        """

        after = """
        class Upper(object):
            def __init__(self, iterable):
                self._iter = iter(iterable)
            def next(self):                 # note the Py2 interface
                return next(self._iter).upper()
            def __iter__(self):
                return self

        itr = Upper('hello')
        assert next(itr) == 'H'
        assert next(itr) == 'E'
        assert list(itr) == list('LLO')
        """
        self.convert_check(before, after, stages=[1], run=PY2)

    def test_xrange(self):
        """
        xrange should not be changed by futurize --stage1
        """
        code = '''
        for i in xrange(10):
            pass
        '''
        self.unchanged(code, stages=[1], run=PY2)

    @unittest.expectedFailure
    def test_absolute_import_changes(self):
        """
        Implicit relative imports should be converted to absolute or explicit
        relative imports correctly.

        Issue #16 (with porting bokeh/bbmodel.py)
        """
        with open(self.tempdir + 'specialmodels.py', 'w') as f:
            f.write('pass')

        before = """
        import specialmodels.pandasmodel
        specialmodels.pandasmodel.blah()
        """
        after = """
        from __future__ import absolute_import
        from .specialmodels import pandasmodel
        pandasmodel.blah()
        """
        self.convert_check(before, after, stages=[1])

    def test_safe_futurize_imports(self):
        """
        The standard library module names should not be changed until stage 2
        """
        before = """
        import ConfigParser
        import HTMLParser
        from itertools import ifilterfalse

        ConfigParser.ConfigParser
        HTMLParser.HTMLParser
        assert list(ifilterfalse(lambda x: x % 2, [2, 4])) == [2, 4]
        """
        self.unchanged(before, stages=[1], run=PY2)

    def test_print(self):
        before = """
        print 'Hello'
        """
        after = """
        print('Hello')
        """
        self.convert_check(before, after, stages=[1])

        before = """
        import sys
        print >> sys.stderr, 'Hello', 'world'
        """
        after = """
        import sys
        print('Hello', 'world', file=sys.stderr)
        """
        self.convert_check(before, after, stages=[1])

    def test_print_already_function(self):
        """
        Running futurize --stage1 should not add a second set of parentheses
        """
        before = """
        print('Hello')
        """
        self.unchanged(before, stages=[1])

    @unittest.expectedFailure
    def test_print_already_function_complex(self):
        """
        Running futurize --stage1 does add a second second set of parentheses
        in this case. This is because the underlying lib2to3 has two distinct
        grammars -- with a print statement and with a print function -- and,
        when going forwards (2 to both), futurize assumes print is a statement,
        which raises a ParseError.
        """
        before = """
        import sys
        print('Hello', 'world', file=sys.stderr)
        """
        self.unchanged(before, stages=[1])

    def test_exceptions(self):
        before = """
        try:
            raise AttributeError('blah')
        except AttributeError, e:
            pass
        """
        after = """
        try:
            raise AttributeError('blah')
        except AttributeError as e:
            pass
        """
        self.convert_check(before, after, stages=[1])

    @unittest.expectedFailure
    def test_string_exceptions(self):
        """
        2to3 does not convert string exceptions: see
        http://python3porting.com/differences.html.
        """
        before = """
        try:
            raise "old string exception"
        except Exception, e:
            pass
        """
        after = """
        try:
            raise Exception("old string exception")
        except Exception as e:
            pass
        """
        self.convert_check(before, after, stages=[1])

    def test_oldstyle_classes(self):
        """
        We don't convert old-style classes to new-style automatically in
        stage 1 (but we should in stage 2). So Blah should not inherit
        explicitly from object yet.
        """
        before = """
        class Blah:
            pass
        """
        self.unchanged(before, stages=[1])

    def test_stdlib_modules_not_changed(self):
        """
        Standard library module names should not be changed in stage 1
        """
        before = """
        import ConfigParser
        import HTMLParser
        import collections

        print 'Hello'
        try:
            raise AttributeError('blah')
        except AttributeError, e:
            pass
        """
        after = """
        import ConfigParser
        import HTMLParser
        import collections

        print('Hello')
        try:
            raise AttributeError('blah')
        except AttributeError as e:
            pass
        """
        self.convert_check(before, after, stages=[1], run=PY2)

    def test_octal_literals(self):
        before = """
        mode = 0644
        """
        after = """
        mode = 0o644
        """
        self.convert_check(before, after)

    def test_long_int_literals(self):
        before = """
        bignumber = 12345678901234567890L
        """
        after = """
        bignumber = 12345678901234567890
        """
        self.convert_check(before, after)

    def test___future___import_position(self):
        """
        Issue #4: __future__ imports inserted too low in file: SyntaxError
        """
        code = """
        # Comments here
        # and here
        __version__=''' $Id$ '''
        __doc__="A Sequencer class counts things. It aids numbering and formatting lists."
        __all__='Sequencer getSequencer setSequencer'.split()
        #
        # another comment
        #

        CONSTANTS = [ 0, 01, 011, 0111, 012, 02, 021, 0211, 02111, 013 ]
        _RN_LETTERS = "IVXLCDM"

        def my_func(value):
            pass

        ''' Docstring-like comment here '''
        """
        self.convert(code)

    def test_issue_45(self):
        """
        Tests whether running futurize -f libfuturize.fixes.fix_future_standard_library_urllib
        on the code below causes a ValueError (issue #45).
        """
        code = r"""
            from __future__ import print_function
            from urllib import urlopen, urlencode
            oeis_url = 'http://oeis.org/'
            def _fetch(url):
                try:
                    f = urlopen(url)
                    result = f.read()
                    f.close()
                    return result
                except IOError as msg:
                    raise IOError("%s\nError fetching %s." % (msg, url))
        """
        self.convert(code)

    def test_order_future_lines(self):
        """
        Tests the internal order_future_lines() function.
        """
        before = '''
               # comment here
               from __future__ import print_function
               from __future__ import absolute_import
                                 # blank line or comment here
               from future.utils import with_metaclass
               from builtins import zzz
               from builtins import aaa
               from builtins import blah
               # another comment

               import something_else
               code_here
               more_code_here
               '''
        after = '''
               # comment here
               from __future__ import absolute_import
               from __future__ import print_function
                                 # blank line or comment here
               from future.utils import with_metaclass
               from builtins import aaa
               from builtins import blah
               from builtins import zzz
               # another comment

               import something_else
               code_here
               more_code_here
               '''
        self.assertEqual(order_future_lines(reformat_code(before)),
                         reformat_code(after))

    @unittest.expectedFailure
    def test_issue_12(self):
        """
        Issue #12: This code shouldn't be upset by additional imports.
        __future__ imports must appear at the top of modules since about Python
        2.5.
        """
        code = """
        from __future__ import with_statement
        f = open('setup.py')
        for i in xrange(100):
            pass
        """
        self.unchanged(code)

    @expectedFailurePY26
    def test_range_necessary_list_calls(self):
        """
        On Py2.6 (only), the xrange_with_import fixer somehow seems to cause
            l = range(10)
        to be converted to:
            l = list(list(range(10)))
        with an extra list(...) call.
        """
        before = """
        l = range(10)
        assert isinstance(l, list)
        for i in range(3):
            print i
        for i in xrange(3):
            print i
        """
        after = """
        from __future__ import print_function
        from builtins import range
        l = list(range(10))
        assert isinstance(l, list)
        for i in range(3):
            print(i)
        for i in range(3):
            print(i)
        """
        self.convert_check(before, after)

    def test_basestring(self):
        """
        The 2to3 basestring fixer breaks working Py2 code that uses basestring.
        This tests whether something sensible is done instead.
        """
        before = """
        assert isinstance('hello', basestring)
        assert isinstance(u'hello', basestring)
        assert isinstance(b'hello', basestring)
        """
        after = """
        from past.builtins import basestring
        assert isinstance('hello', basestring)
        assert isinstance(u'hello', basestring)
        assert isinstance(b'hello', basestring)
        """
        self.convert_check(before, after)

    def test_safe_division(self):
        """
        Tests whether Py2 scripts using old-style division still work
        after futurization.
        """
        before = """
        import random
        class fraction(object):
            numer = 0
            denom = 0
            def __init__(self, numer, denom):
                self.numer = numer
                self.denom = denom

            def total_count(self):
                return self.numer * 50

        x = 3 / 2
        y = 3. / 2
        foo = list(range(100))
        assert x == 1 and isinstance(x, int)
        assert y == 1.5 and isinstance(y, float)
        a = 1 + foo[len(foo) / 2]
        b = 1 + foo[len(foo) * 3 / 4]
        assert a == 51
        assert b == 76
        r = random.randint(0, 1000) * 1.0 / 1000
        output = { "SUCCESS": 5, "TOTAL": 10 }
        output["SUCCESS"] * 100 / output["TOTAL"]
        obj = fraction(1, 50)
        val = float(obj.numer) / obj.denom * 1e-9
        obj.numer * obj.denom / val
        obj.total_count() * val / 100
        original_numer = 1
        original_denom = 50
        100 * abs(obj.numer - original_numer) / float(max(obj.denom, original_denom))
        100 * abs(obj.numer - original_numer) / max(obj.denom, original_denom)
        float(original_numer) * float(original_denom) / float(obj.numer)
        """
        after = """
        from __future__ import division
        from past.utils import old_div
        import random
        class fraction(object):
            numer = 0
            denom = 0
            def __init__(self, numer, denom):
                self.numer = numer
                self.denom = denom

            def total_count(self):
                return self.numer * 50

        x = old_div(3, 2)
        y = 3. / 2
        foo = list(range(100))
        assert x == 1 and isinstance(x, int)
        assert y == 1.5 and isinstance(y, float)
        a = 1 + foo[old_div(len(foo), 2)]
        b = 1 + foo[old_div(len(foo) * 3, 4)]
        assert a == 51
        assert b == 76
        r = old_div(random.randint(0, 1000) * 1.0, 1000)
        output = { "SUCCESS": 5, "TOTAL": 10 }
        old_div(output["SUCCESS"] * 100, output["TOTAL"])
        obj = fraction(1, 50)
        val = float(obj.numer) / obj.denom * 1e-9
        old_div(obj.numer * obj.denom, val)
        old_div(obj.total_count() * val, 100)
        original_numer = 1
        original_denom = 50
        100 * abs(obj.numer - original_numer) / float(max(obj.denom, original_denom))
        old_div(100 * abs(obj.numer - original_numer), max(obj.denom, original_denom))
        float(original_numer) * float(original_denom) / float(obj.numer)
        """
        self.convert_check(before, after)

    def test_safe_division_overloaded(self):
        """
        If division is overloaded, futurize may produce spurious old_div
        calls.  This test is for whether the code still works on Py2
        despite these calls.
        """
        before = """
        class Path(str):
            def __div__(self, other):
                return self.__truediv__(other)
            def __truediv__(self, other):
                return Path(str(self) + '/' + str(other))
        path1 = Path('home')
        path2 = Path('user')
        z = path1 / path2
        assert isinstance(z, Path)
        assert str(z) == 'home/user'
        """
        after = """
        from __future__ import division
        from past.utils import old_div
        class Path(str):
            def __div__(self, other):
                return self.__truediv__(other)
            def __truediv__(self, other):
                return Path(str(self) + '/' + str(other))
        path1 = Path('home')
        path2 = Path('user')
        z = old_div(path1, path2)
        assert isinstance(z, Path)
        assert str(z) == 'home/user'
        """
        self.convert_check(before, after)

    def test_basestring_issue_156(self):
        before = """
        x = str(3)
        allowed_types = basestring, int
        assert isinstance('', allowed_types)
        assert isinstance(u'', allowed_types)
        assert isinstance(u'foo', basestring)
        """
        after = """
        from builtins import str
        from past.builtins import basestring
        x = str(3)
        allowed_types = basestring, int
        assert isinstance('', allowed_types)
        assert isinstance(u'', allowed_types)
        assert isinstance(u'foo', basestring)
        """
        self.convert_check(before, after)


class TestConservativeFuturize(CodeHandler):
    @unittest.expectedFailure
    def test_basestring(self):
        """
        In conservative mode, futurize would not modify "basestring"
        but merely import it from ``past``, and the following code would still
        run on both Py2 and Py3.
        """
        before = """
        assert isinstance('hello', basestring)
        assert isinstance(u'hello', basestring)
        assert isinstance(b'hello', basestring)
        """
        after = """
        from past.builtins import basestring
        assert isinstance('hello', basestring)
        assert isinstance(u'hello', basestring)
        assert isinstance(b'hello', basestring)
        """
        self.convert_check(before, after, conservative=True)

    @unittest.expectedFailure
    def test_open(self):
        """
        In conservative mode, futurize would not import io.open because
        this changes the default return type from bytes to text.
        """
        before = """
        filename = 'temp_file_open.test'
        contents = 'Temporary file contents. Delete me.'
        with open(filename, 'w') as f:
            f.write(contents)

        with open(filename, 'r') as f:
            data = f.read()
        assert isinstance(data, str)
        assert data == contents
        """
        after = """
        from past.builtins import open, str as oldbytes, unicode
        filename = oldbytes(b'temp_file_open.test')
        contents = oldbytes(b'Temporary file contents. Delete me.')
        with open(filename, oldbytes(b'w')) as f:
            f.write(contents)

        with open(filename, oldbytes(b'r')) as f:
            data = f.read()
        assert isinstance(data, oldbytes)
        assert data == contents
        assert isinstance(oldbytes(b'hello'), basestring)
        assert isinstance(unicode(u'hello'), basestring)
        assert isinstance(oldbytes(b'hello'), basestring)
        """
        self.convert_check(before, after, conservative=True)

class TestFuturizeAllImports(CodeHandler):
    """
    Tests "futurize --all-imports".
    """
    @expectedFailurePY26
    def test_all_imports(self):
        before = """
        import math
        import os
        l = range(10)
        assert isinstance(l, list)
        print 'Hello'
        for i in xrange(100):
            pass
        print('Hello')
        """
        after = """
        from __future__ import unicode_literals
        from __future__ import print_function
        from __future__ import division
        from __future__ import absolute_import
        from future import standard_library
        standard_library.install_aliases()
        from builtins import range
        from builtins import *
        import math
        import os
        l = list(range(10))
        assert isinstance(l, list)
        print('Hello')
        for i in range(100):
            pass
        print('Hello')
        """
        self.convert_check(before, after, all_imports=True)


if __name__ == '__main__':
    unittest.main()
