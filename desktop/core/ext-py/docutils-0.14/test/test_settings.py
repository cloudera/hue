#!/usr/bin/env python
# -*- coding: utf-8 -*-

# $Id: test_settings.py 8068 2017-05-08 22:10:39Z milde $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Tests of runtime settings.
"""

import sys
import os
import difflib
import pprint
import warnings
import unittest
import DocutilsTestSupport              # must be imported before docutils
from docutils import frontend, utils
from docutils.writers import html4css1, pep_html
from docutils.parsers import rst


warnings.filterwarnings(action='ignore',
                        category=frontend.ConfigDeprecationWarning)


def fixpath(path):
    return os.path.abspath(os.path.join(*(path.split('/'))))


class ConfigFileTests(unittest.TestCase):

    config_files = {'old': fixpath('data/config_old.txt'),
                    'one': fixpath('data/config_1.txt'),
                    'two': fixpath('data/config_2.txt'),
                    'list': fixpath('data/config_list.txt'),
                    'list2': fixpath('data/config_list_2.txt'),
                    'error': fixpath('data/config_error_handler.txt')}

    settings = {
        'old': {u'datestamp': u'%Y-%m-%d %H:%M UTC',
                u'generator': True,
                u'no_random': True,
                u'python_home': u'http://www.python.org',
                u'source_link': True,
                'stylesheet': None,
                u'stylesheet_path': [u'stylesheets/pep.css'],
                'template': fixpath(u'data/pep-html-template')},
        'one': {u'datestamp': u'%Y-%m-%d %H:%M UTC',
                u'generator': True,
                u'no_random': True,
                u'python_home': u'http://www.python.org',
                u'raw_enabled': False,
                'record_dependencies': utils.DependencyList(),
                u'source_link': True,
                'stylesheet': None,
                u'stylesheet_path': [u'stylesheets/pep.css'],
                u'tab_width': 8,
                u'template': fixpath(u'data/pep-html-template'),
                u'trim_footnote_reference_space': True,
               },
        'two': {u'footnote_references': u'superscript',
                u'generator': False,
                'record_dependencies': utils.DependencyList(),
                u'stylesheet': None,
                u'stylesheet_path': [u'test.css'],
                'trim_footnote_reference_space': None},
        'list': {u'expose_internals': [u'a', u'b', u'c', u'd', u'e'],
                 u'strip_classes': [u'spam', u'pan', u'fun', u'parrot'],
                 u'strip_elements_with_classes': [u'sugar', u'flour', u'milk',
                                                  u'safran']},
        'list2': {u'expose_internals': [u'a', u'b', u'c', u'd', u'e', u'f'],
                  u'strip_classes': [u'spam', u'pan', u'fun', u'parrot',
                                     u'ham', u'eggs'],
                  u'strip_elements_with_classes': [u'sugar', u'flour',
                                                   u'milk', u'safran',
                                                   u'eggs', u'salt']},
        'error': {u'error_encoding': u'ascii',
                  u'error_encoding_error_handler': u'strict'},
        }

    compare = difflib.Differ().compare
    """Comparison method shared by all tests."""

    def setUp(self):
        self.option_parser = frontend.OptionParser(
            components=(pep_html.Writer, rst.Parser), read_config_files=None)

    def files_settings(self, *names):
        settings = frontend.Values()
        for name in names:
            settings.update(self.option_parser.get_config_file_settings(
                self.config_files[name]), self.option_parser)
        return settings.__dict__

    def expected_settings(self, *names):
        expected = {}
        for name in names:
            expected.update(self.settings[name])
        return expected

    def compare_output(self, result, expected):
        """`result` and `expected` should both be dicts."""
        self.assertTrue('record_dependencies' in result)
        if 'record_dependencies' not in expected:
            # Delete it if we don't want to test it.
            del result['record_dependencies']
        result = pprint.pformat(result) + '\n'
        expected = pprint.pformat(expected) + '\n'
        try:
            self.assertEqual(result, expected)
        except AssertionError:
            print >>sys.stderr, '\n%s\n' % (self,)
            print >>sys.stderr, '-: expected\n+: result'
            print >>sys.stderr, ''.join(self.compare(expected.splitlines(1),
                                                     result.splitlines(1)))
            raise

    def test_nofiles(self):
        self.compare_output(self.files_settings(),
                            self.expected_settings())

    def test_old(self):
        self.compare_output(self.files_settings('old'),
                            self.expected_settings('old'))

    def test_one(self):
        self.compare_output(self.files_settings('one'),
                            self.expected_settings('one'))

    def test_multiple(self):
        self.compare_output(self.files_settings('one', 'two'),
                            self.expected_settings('one', 'two'))

    def test_old_and_new(self):
        self.compare_output(self.files_settings('old', 'two'),
                            self.expected_settings('old', 'two'))

    def test_list(self):
        self.compare_output(self.files_settings('list'),
                            self.expected_settings('list'))

    def test_list2(self):
        self.compare_output(self.files_settings('list', 'list2'),
                            self.expected_settings('list2'))

    def test_error_handler(self):
        self.compare_output(self.files_settings('error'),
                            self.expected_settings('error'))


class ConfigEnvVarFileTests(ConfigFileTests):

    """
    Repeats the tests of `ConfigFileTests` using the ``DOCUTILSCONFIG``
    environment variable and the standard Docutils config file mechanism.
    """

    def setUp(self):
        ConfigFileTests.setUp(self)
        self.orig_environ = os.environ
        os.environ = os.environ.copy()

    def files_settings(self, *names):
        files = [self.config_files[name] for name in names]
        os.environ['DOCUTILSCONFIG'] = os.pathsep.join(files)
        settings = self.option_parser.get_standard_config_settings()
        return settings.__dict__

    def tearDown(self):
        os.environ = self.orig_environ


class HelperFunctionsTests(unittest.TestCase):

    pathdict = {'foo': 'hallo', 'ham': u'h\xE4m', 'spam': u'spam'}
    keys = ['foo', 'ham']

    def setUp(self):
        self.option_parser = frontend.OptionParser(
            components=(rst.Parser,), read_config_files=None)

    def test_make_paths_absolute(self):
        pathdict = self.pathdict.copy()
        frontend.make_paths_absolute(pathdict, self.keys, base_path='base')
        self.assertEqual(pathdict['foo'], os.path.abspath('base/hallo'))
        self.assertEqual(pathdict['ham'], os.path.abspath(u'base/h\xE4m'))
        # not touched, because key not in keys:
        self.assertEqual(pathdict['spam'], u'spam')

    def test_make_paths_absolute_cwd(self):
        # With base_path None, the cwd is used as base path.
        # Settings values may-be `unicode` instances, therefore
        # os.getcwdu() is used and the converted path is a unicode instance:
        pathdict = self.pathdict.copy()
        frontend.make_paths_absolute(pathdict, self.keys)
        self.assertEqual(pathdict['foo'], os.path.abspath(u'hallo'))
        self.assertEqual(pathdict['ham'], os.path.abspath(u'h\xE4m'))
        # not touched, because key not in keys:
        self.assertEqual(pathdict['spam'], u'spam')

    boolean_settings = (
                (True, True ),
                ('1', True ),
                (u'on', True ),
                ('yes', True ),
                (u'true', True ),
                (u'0', False ),
                ('off', False ),
                (u'no', False ),
                ('false', False ),
               )
    def test_validate_boolean(self):
        for t in self.boolean_settings:
            self.assertEqual(
                frontend.validate_boolean(None, t[0], self.option_parser),
                             t[1])

    def test_validate_ternary(self):
        tests = (
                 ('500V', '500V'),
                 (u'parrot', u'parrot'),
                )
        for t in self.boolean_settings + tests:
            self.assertEqual(
                frontend.validate_ternary(None, t[0], self.option_parser),
                             t[1])

    def test_validate_colon_separated_string_list(self):
        tests = (
                    (u'a', ['a',] ),
                    ('a', ['a',] ),
                    (u'a:b', ['a', 'b'] ),
                    ('a:b', ['a', 'b'] ),
                    ([u'a',], ['a',] ),
                    ([u'a', u'b:c'], ['a', 'b', 'c'] ),
                )
        for t in tests:
            self.assertEqual(
                    frontend.validate_colon_separated_string_list(None, t[0], None),
                    t[1])

    def test_validate_comma_separated_list(self):
        tests = (
                    (u'a', ['a',] ),
                    ('a', ['a',] ),
                    (u'a,b', ['a', 'b'] ),
                    ('a,b', ['a', 'b'] ),
                    ([u'a',], ['a',] ),
                    ([u'a', u'b,c'], ['a', 'b', 'c'] ),
                    (['a', 'b,c'], ['a', 'b', 'c'] ),
                )
        for t in tests:
            self.assertEqual(
                    frontend.validate_comma_separated_list(None, t[0], None),
                    t[1])

    def test_validate_url_trailing_slash(self):
        tests = (
                    ('', './' ),
                    (None, './' ),
                    (u'http://example.org', u'http://example.org/' ),
                    ('http://example.org/', 'http://example.org/' ),
                )
        for t in tests:
            self.assertEqual(
                    frontend.validate_url_trailing_slash(None, t[0], None),
                    t[1])

    def test_validate_smartquotes_locales(self):
        tests = (
                 ('en:ssvv', [('en', 'ssvv')]),
                 (u'sd:«»°°', [(u'sd', u'«»°°')]),
                 ([('sd', u'«»°°'), u'ds:°°«»'], [('sd', u'«»°°'),
                                                  ('ds', u'°°«»')]),
                 (u'frs:« : »:((:))', [(u'frs', [u'« ', u' »',
                                                 u'((', u'))'])]),
                )
        for t in tests:
            self.assertEqual(
                    frontend.validate_smartquotes_locales(None, t[0], None),
                    t[1])



if __name__ == '__main__':
    unittest.main()
