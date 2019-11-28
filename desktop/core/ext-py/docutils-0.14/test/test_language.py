#!/usr/bin/env python

# $Id: test_language.py 7503 2012-08-26 15:42:37Z grubert $
# Authors: Engelbert Gruber <grubert@users.sourceforge.net>;
#          David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Tests for language module completeness.

Specify a language code (e.g. "de") as a command-line parameter to test only
that language.
"""

import sys
import os
import re
import DocutilsTestSupport              # must be imported before docutils
import docutils.languages
import docutils.parsers.rst.languages
from docutils.parsers.rst import states, directives, roles
import docutils.utils, docutils.frontend

_settings = docutils.frontend.OptionParser().get_default_values()
_reporter = docutils.utils.new_reporter('', _settings)

reference_language = 'en'


class LanguageTestSuite(DocutilsTestSupport.CustomTestSuite):

    language_module_pattern = re.compile('^([a-z]{2,3}(_[a-z]{2,8})*)\.py$')

    def __init__(self, languages=None):
        DocutilsTestSupport.CustomTestSuite.__init__(self)
        if languages:
            self.languages = languages
        else:
            self.get_languages()

    def get_languages(self):
        """
        Get installed language translations from docutils.languages and from
        docutils.parsers.rst.languages.
        """
        languages = {}
        for mod in (os.listdir(docutils.languages.__path__[0])
                    + os.listdir(docutils.parsers.rst.languages.__path__[0])):
            match = self.language_module_pattern.match(mod)
            if match:
                languages[match.group(1)] = 1
        self.languages = languages.keys()
        # test language tag normalization:
        self.languages += ['en_gb', 'en_US', 'en-CA', 'de-DE', 'de-AT-1901',
                           'pt-BR', 'pt-foo-BR']
        # test that locally created language files are also loaded.
        # requires local_dummy_lang.py in test directory (testroot)
        # The local_dummy_lang.py contains all the fields from both
        # the docutils language tags and the parser.rst language tags
        self.languages += ['local_dummy_lang']

    def generateTests(self):
        for language in self.languages:
            for method in LanguageTestCase.test_methods:
                self.addTestCase(LanguageTestCase, method, None, None,
                                 id=language+'.py', language=language)


class LanguageTestCase(DocutilsTestSupport.CustomTestCase):

    test_methods = ['test_labels', 'test_bibliographic_fields',
                    'test_directives', 'test_roles']
    """Names of methods used to test each language."""

    def __init__(self, *args, **kwargs):
        self.ref = docutils.languages.get_language(reference_language,
                                                   _reporter)
        self.language = kwargs['language']
        del kwargs['language']          # only wanted here
        DocutilsTestSupport.CustomTestCase.__init__(self, *args, **kwargs)

    def _xor(self, ref_dict, l_dict):
        """
        Returns entries that are only in one dictionary.
        (missing_in_lang, more_than_in_ref).
        """
        missing  = []   # in ref but not in l.
        too_much = []   # in l but not in ref.
        for label in ref_dict.keys():
            if label not in l_dict:
                missing.append(label)
        for label in l_dict.keys():
            if label not in ref_dict:
                too_much.append(label)
        return (missing, too_much)

    def _invert(self, adict):
        """Return an inverted (keys & values swapped) dictionary."""
        inverted = {}
        for key, value in adict.items():
            inverted[value] = key
        return inverted

    def test_labels(self):
        try:
            module = docutils.languages.get_language(self.language, _reporter)
            if not module:
                raise ImportError
        except ImportError:
            self.fail('No docutils.languages.%s module.' % self.language)
        missed, unknown = self._xor(self.ref.labels, module.labels)
        if missed or unknown:
            self.fail('Module docutils.languages.%s.labels:\n'
                      '    Missed: %s; Unknown: %s'
                      % (self.language, str(missed), str(unknown)))

    def test_bibliographic_fields(self):
        try:
            module = docutils.languages.get_language(self.language, _reporter)
            if not module:
                raise ImportError
        except ImportError:
            self.fail('No docutils.languages.%s module.' % self.language)
        missed, unknown = self._xor(
            self._invert(self.ref.bibliographic_fields),
            self._invert(module.bibliographic_fields))
        if missed or unknown:
            self.fail('Module docutils.languages.%s.bibliographic_fields:\n'
                      '    Missed: %s; Unknown: %s'
                      % (self.language, str(missed), str(unknown)))

    def test_directives(self):
        try:
            module = docutils.parsers.rst.languages.get_language(
                self.language)
            if not module:
                raise ImportError
        except ImportError:
            self.fail('No docutils.parsers.rst.languages.%s module.'
                      % self.language)
        failures = []
        for d in module.directives.keys():
            try:
                func, msg = directives.directive(d, module, None)
                if not func:
                    failures.append('"%s": unknown directive' % d)
            except Exception, error:
                failures.append('"%s": %s' % (d, error))
        inverted = self._invert(module.directives)
        canonical = directives._directive_registry.keys()
        canonical.sort()
        canonical.remove('restructuredtext-test-directive')
        for name in canonical:
            if name not in inverted:
                failures.append('"%s": translation missing' % name)
        if failures:
            text = ('Module docutils.parsers.rst.languages.%s:\n    %s'
                    % (self.language, '\n    '.join(failures)))
            if type(text) is unicode:
                text = text.encode('raw_unicode_escape')
            self.fail(text)

    def test_roles(self):
        try:
            module = docutils.parsers.rst.languages.get_language(
                self.language)
            if not module:
                raise ImportError
            module.roles
        except ImportError:
            self.fail('No docutils.parsers.rst.languages.%s module.'
                      % self.language)
        except AttributeError:
            self.fail('No "roles" mapping in docutils.parsers.rst.languages.'
                      '%s module.' % self.language)
        failures = []
        for d in module.roles.values():
            try:
                method = roles._role_registry[d]
                #if not method:
                #    failures.append('"%s": unknown role' % d)
            except KeyError, error:
                failures.append('"%s": %s' % (d, error))
        inverted = self._invert(module.roles)
        canonical = roles._role_registry.keys()
        canonical.sort()
        canonical.remove('restructuredtext-unimplemented-role')
        for name in canonical:
            if name not in inverted:
                failures.append('"%s": translation missing' % name)
        if failures:
            text = ('Module docutils.parsers.rst.languages.%s:\n    %s'
                    % (self.language, '\n    '.join(failures)))
            if type(text) is unicode:
                text = text.encode('raw_unicode_escape')
            self.fail(text)

languages_to_test = []

def suite():
    s = LanguageTestSuite(languages_to_test)
    s.generateTests()
    return s

def get_language_arguments():
    while len(sys.argv) > 1:
        last = sys.argv[-1]
        if last.startswith('-'):
            break
        languages_to_test.append(last)
        sys.argv.pop()
    languages_to_test.reverse()


if __name__ == '__main__':
    get_language_arguments()
    import unittest
    unittest.main(defaultTest='suite')

# vim: set et ts=4 ai :
