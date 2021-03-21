import sys
from unittest import TestCase

import pytest

from kazoo.protocol import paths


if sys.version_info > (3, ):  # pragma: nocover
    def u(s):
        return s
else:  # pragma: nocover
    def u(s):
        return unicode(s, "unicode_escape")


class NormPathTestCase(TestCase):

    def test_normpath(self):
        assert paths.normpath('/a/b') == '/a/b'

    def test_normpath_empty(self):
        assert paths.normpath('') == ''

    def test_normpath_unicode(self):
        assert paths.normpath(u('/\xe4/b')) == u('/\xe4/b')

    def test_normpath_dots(self):
        assert paths.normpath('/a./b../c') == '/a./b../c'

    def test_normpath_slash(self):
        assert paths.normpath('/') == '/'

    def test_normpath_multiple_slashes(self):
        assert paths.normpath('//') == '/'
        assert paths.normpath('//a/b') == '/a/b'
        assert paths.normpath('/a//b//') == '/a/b'
        assert paths.normpath('//a////b///c/') == '/a/b/c'

    def test_normpath_relative(self):
        with pytest.raises(ValueError):
            paths.normpath('./a/b')
        with pytest.raises(ValueError):
            paths.normpath('/a/../b')

    def test_normpath_trailing(self):
        assert paths.normpath('/', trailing=True) == '/'


class JoinTestCase(TestCase):

    def test_join(self):
        assert paths.join('/a') == '/a'
        assert paths.join('/a', 'b/') == '/a/b/'
        assert paths.join('/a', 'b', 'c') == '/a/b/c'

    def test_join_empty(self):
        assert paths.join('') == ''
        assert paths.join('', 'a', 'b') == 'a/b'
        assert paths.join('/a', '', 'b/', 'c') == '/a/b/c'

    def test_join_absolute(self):
        assert paths.join('/a/b', '/c') == '/c'


class IsAbsTestCase(TestCase):

    def test_isabs(self):
        assert paths.isabs('/') is True
        assert paths.isabs('/a') is True
        assert paths.isabs('/a//b/c') is True
        assert paths.isabs('//a/b') is True

    def test_isabs_false(self):
        assert paths.isabs('') is False
        assert paths.isabs('a/') is False
        assert paths.isabs('a/../') is False


class BaseNameTestCase(TestCase):

    def test_basename(self):
        assert paths.basename('') == ''
        assert paths.basename('/') == ''
        assert paths.basename('//a') == 'a'
        assert paths.basename('//a/') == ''
        assert paths.basename('/a/b.//c..') == 'c..'


class PrefixRootTestCase(TestCase):

    def test_prefix_root(self):
        assert paths._prefix_root('/a/', 'b/c') == '/a/b/c'
        assert paths._prefix_root('/a/b', 'c/d') == '/a/b/c/d'
        assert paths._prefix_root('/a', '/b/c') == '/a/b/c'
        assert paths._prefix_root('/a', '//b/c.') == '/a/b/c.'


class NormRootTestCase(TestCase):

    def test_norm_root(self):
        assert paths._norm_root('') == '/'
        assert paths._norm_root('/') == '/'
        assert paths._norm_root('//a') == '/a'
        assert paths._norm_root('//a./b') == '/a./b'
