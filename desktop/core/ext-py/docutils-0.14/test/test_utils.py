# -*- coding: utf-8 -*-
#! /usr/bin/env python

# $Id: test_utils.py 8141 2017-07-08 17:05:18Z goodger $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Test module for utils/__init__.py.
"""

import unittest
import sys
import os
from DocutilsTestSupport import docutils, utils, nodes
try:
    from io import StringIO
except ImportError:    # io is new in Python 2.6
    from StringIO import StringIO


class ReporterTests(unittest.TestCase):

    stream = StringIO()
    reporter = utils.Reporter('test data', 2, 4, stream, 1)

    def setUp(self):
        self.stream.seek(0)
        self.stream.truncate()

    def test_level0(self):
        sw = self.reporter.system_message(0, 'debug output')
        self.assertEqual(sw.pformat(), """\
<system_message level="0" source="test data" type="DEBUG">
    <paragraph>
        debug output
""")
        self.assertEqual(self.stream.getvalue(),
                          'test data:: (DEBUG/0) debug output\n')

    def test_level1(self):
        sw = self.reporter.system_message(1, 'a little reminder')
        self.assertEqual(sw.pformat(), """\
<system_message level="1" source="test data" type="INFO">
    <paragraph>
        a little reminder
""")
        self.assertEqual(self.stream.getvalue(), '')

    def test_level2(self):
        sw = self.reporter.system_message(2, 'a warning')
        self.assertEqual(sw.pformat(), """\
<system_message level="2" source="test data" type="WARNING">
    <paragraph>
        a warning
""")
        self.assertEqual(self.stream.getvalue(),
                          'test data:: (WARNING/2) a warning\n')

    def test_level3(self):
        sw = self.reporter.system_message(3, 'an error')
        self.assertEqual(sw.pformat(), """\
<system_message level="3" source="test data" type="ERROR">
    <paragraph>
        an error
""")
        self.assertEqual(self.stream.getvalue(),
                          'test data:: (ERROR/3) an error\n')

    def test_level4(self):
        self.assertRaises(utils.SystemMessage, self.reporter.system_message, 4,
                          'a severe error, raises an exception')
        self.assertEqual(self.stream.getvalue(), 'test data:: (SEVERE/4) '
                          'a severe error, raises an exception\n')


    def test_unicode_message(self):
        sw = self.reporter.system_message(0, u'mesidʒ')
        self.assertEqual(sw.pformat(), u"""\
<system_message level="0" source="test data" type="DEBUG">
    <paragraph>
        mesidʒ
""")

    def test_unicode_message_from_exception(self):
        """Workaround for Python < 2.6 bug:
        unicode(<exception instance>) uses __str__
        and hence fails with unicode message"""
        try:
            raise Exception(u'mesidʒ')
        except Exception, err:
            sw = self.reporter.system_message(0, err)
            self.assertEqual(sw.pformat(), u"""\
<system_message level="0" source="test data" type="DEBUG">
    <paragraph>
        mesidʒ
""")

class QuietReporterTests(unittest.TestCase):

    stream = StringIO()
    reporter = utils.Reporter('test data', 5, 5, stream, 0)

    def setUp(self):
        self.stream.seek(0)
        self.stream.truncate()

    def test_debug(self):
        sw = self.reporter.debug('a debug message')
        # None because debug is disabled.
        self.assertEqual(sw, None)
        self.assertEqual(self.stream.getvalue(), '')

    def test_info(self):
        sw = self.reporter.info('an informational message')
        self.assertEqual(sw.pformat(), """\
<system_message level="1" source="test data" type="INFO">
    <paragraph>
        an informational message
""")
        self.assertEqual(self.stream.getvalue(), '')

    def test_warning(self):
        sw = self.reporter.warning('a warning')
        self.assertEqual(sw.pformat(), """\
<system_message level="2" source="test data" type="WARNING">
    <paragraph>
        a warning
""")
        self.assertEqual(self.stream.getvalue(), '')

    def test_error(self):
        sw = self.reporter.error('an error')
        self.assertEqual(sw.pformat(), """\
<system_message level="3" source="test data" type="ERROR">
    <paragraph>
        an error
""")
        self.assertEqual(self.stream.getvalue(), '')

    def test_severe(self):
        sw = self.reporter.severe('a severe error')
        self.assertEqual(sw.pformat(), """\
<system_message level="4" source="test data" type="SEVERE">
    <paragraph>
        a severe error
""")
        self.assertEqual(self.stream.getvalue(), '')


class NameValueTests(unittest.TestCase):

    def test_extract_name_value(self):
        self.assertRaises(utils.NameValueError, utils.extract_name_value,
                          'hello')
        self.assertRaises(utils.NameValueError, utils.extract_name_value,
                          'hello')
        self.assertRaises(utils.NameValueError, utils.extract_name_value,
                          '=hello')
        self.assertRaises(utils.NameValueError, utils.extract_name_value,
                          'hello=')
        self.assertRaises(utils.NameValueError, utils.extract_name_value,
                          'hello="')
        self.assertRaises(utils.NameValueError, utils.extract_name_value,
                          'hello="something')
        self.assertRaises(utils.NameValueError, utils.extract_name_value,
                          'hello="something"else')
        output = utils.extract_name_value(
              """att1=val1 att2=val2 att3="value number '3'" att4=val4""")
        self.assertEqual(output, [('att1', 'val1'), ('att2', 'val2'),
                                   ('att3', "value number '3'"),
                                   ('att4', 'val4')])


class ExtensionOptionTests(unittest.TestCase):

    optionspec = {'a': int, 'bbb': float, 'cdef': (lambda x: x),
                  'empty': (lambda x: x)}

    def test_assemble_option_dict(self):
        input = utils.extract_name_value('a=1 bbb=2.0 cdef=hol%s' % chr(224))
        self.assertEqual(
              utils.assemble_option_dict(input, self.optionspec),
              {'a': 1, 'bbb': 2.0, 'cdef': ('hol%s' % chr(224))})
        input = utils.extract_name_value('a=1 b=2.0 c=hol%s' % chr(224))
        self.assertRaises(KeyError, utils.assemble_option_dict,
                          input, self.optionspec)
        input = utils.extract_name_value('a=1 bbb=two cdef=hol%s' % chr(224))
        self.assertRaises(ValueError, utils.assemble_option_dict,
                          input, self.optionspec)

    def test_extract_extension_options(self):
        field_list = nodes.field_list()
        field_list += nodes.field(
              '', nodes.field_name('', 'a'),
              nodes.field_body('', nodes.paragraph('', '1')))
        field_list += nodes.field(
              '', nodes.field_name('', 'bbb'),
              nodes.field_body('', nodes.paragraph('', '2.0')))
        field_list += nodes.field(
              '', nodes.field_name('', 'cdef'),
              nodes.field_body('', nodes.paragraph('', u'hol\u00e0')))
        field_list += nodes.field(
              '', nodes.field_name('', 'empty'), nodes.field_body())
        self.assertEqual(
              utils.extract_extension_options(field_list, self.optionspec),
              {'a': 1, 'bbb': 2.0,
               'cdef': u'hol\u00e0',
               'empty': None})
        self.assertRaises(KeyError, utils.extract_extension_options,
                          field_list, {})
        field_list += nodes.field(
              '', nodes.field_name('', 'cdef'),
              nodes.field_body('', nodes.paragraph('', 'one'),
                               nodes.paragraph('', 'two')))
        self.assertRaises(utils.BadOptionDataError,
                          utils.extract_extension_options,
                          field_list, self.optionspec)
        field_list[-1] = nodes.field(
              '', nodes.field_name('', 'cdef bad'),
              nodes.field_body('', nodes.paragraph('', 'no arguments')))
        self.assertRaises(utils.BadOptionError,
                          utils.extract_extension_options,
                          field_list, self.optionspec)
        field_list[-1] = nodes.field(
              '', nodes.field_name('', 'cdef'),
              nodes.field_body('', nodes.paragraph('', 'duplicate')))
        self.assertRaises(utils.DuplicateOptionError,
                          utils.extract_extension_options,
                          field_list, self.optionspec)
        field_list[-2] = nodes.field(
              '', nodes.field_name('', 'unkown'),
              nodes.field_body('', nodes.paragraph('', 'unknown')))
        self.assertRaises(KeyError, utils.extract_extension_options,
                          field_list, self.optionspec)


class HelperFunctionsTests(unittest.TestCase):

    def test_version_identifier(self):
        """
        docutils.utils.version_identifier() depends on
        docutils.__version_info__, so this also tests that
        docutils.__version__ is equivalent to docutils.__version_info__.
        """
        self.assertEqual(utils.version_identifier(), docutils.__version__)

    def test_normalize_language_tag(self):
        self.assertEqual(utils.normalize_language_tag('de'), ['de'])
        self.assertEqual(utils.normalize_language_tag('de-AT'),
                         ['de-at', 'de'])
        self.assertEqual(utils.normalize_language_tag('de-AT-1901'),
                         ['de-at-1901', 'de-at', 'de-1901', 'de'])
        self.assertEqual(utils.normalize_language_tag('de-AT-1901-frak'),
                         ['de-at-1901-frak', 'de-at-1901', 'de-at-frak',
                          'de-1901-frak', 'de-at', 'de-1901', 'de-frak', 'de'])
        self.assertEqual(utils.normalize_language_tag('grc-ibycus-x-altquot'),
                         ['grc-ibycus-x-altquot', 'grc-ibycus',
                          'grc-x-altquot', 'grc'])

    def test_column_width(self):
        self.assertEqual(utils.column_width(u'de'), 2)
        self.assertEqual(utils.column_width(u'dâ'), 2) # pre-composed
        self.assertEqual(utils.column_width(u'dâ'), 2) # combining


    def test_relative_path(self):
        # Build and return a path to `target`, relative to `source`:
        # Use '/' as path sep in result.
        self.assertEqual(utils.relative_path('spam', 'spam'), '')
        source = os.path.join('h\xE4m', 'spam', 'fileA')
        target = os.path.join('h\xE4m', 'spam', 'fileB')
        self.assertEqual(utils.relative_path(source, target), 'fileB')
        source = os.path.join('h\xE4m', 'spam', 'fileA')
        target = os.path.join('h\xE4m', 'fileB')
        self.assertEqual(utils.relative_path(source, target), '../fileB')
        # if source is None, default to the cwd:
        target = os.path.join('eggs', 'fileB')
        self.assertEqual(utils.relative_path(None, target), 'eggs/fileB')
        # If there is no common prefix, return the absolute path to `target`:
        # source = '/foo/bar/fileA' # POSIX
        #   TODO: how to specify an absolute path independent of the OS?
        # target = os.path.join('eggs', 'fileB')
        # self.assertEqual(utils.relative_path(source, target),
        #                  os.path.abspath('fileB'))
        # Correctly process unicode instances:
        self.assertEqual(utils.relative_path(u'spam', u'spam'), u'')
        source = os.path.join(u'h\xE4m', u'spam', u'fileA')
        target = os.path.join(u'h\xE4m', u'spam', u'fileB')
        self.assertEqual(utils.relative_path(source, target), u'fileB')
        source = os.path.join(u'h\xE4m', u'spam', u'fileA')
        target = os.path.join(u'h\xE4m', u'fileB')
        self.assertEqual(utils.relative_path(source, target), u'../fileB')
        # if source is None, default to the cwd:
        target = os.path.join(u'eggs', u'fileB')
        self.assertEqual(utils.relative_path(None, target), u'eggs/fileB')

    def test_find_file_in_dirs(self):
        # Search for file `path` in the sequence of directories `dirs`.
        # Return the first expansion that matches an existing file.
        dirs = ('nonex', '.', '..')
        found = utils.find_file_in_dirs('HISTORY.txt', dirs)
        # returns
        # '..\\HISTORY.txt' on windows
        # '../HISTORY.txt' on other platforms
        # 'HISTORY.txt' if not called from docutils directory.
        self.assertTrue(found.startswith('..'))
        # Return `path` if the file exists in the cwd or if there is no match
        self.assertEqual(utils.find_file_in_dirs('alltests.py', dirs),
                         'alltests.py')
        self.assertEqual(utils.find_file_in_dirs('gibts/nicht.txt', dirs),
                         'gibts/nicht.txt')


if __name__ == '__main__':
    unittest.main()
