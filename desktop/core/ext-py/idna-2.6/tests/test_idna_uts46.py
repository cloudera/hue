"""Tests for TR46 code."""

import gzip
import os.path
import re
import sys
import unittest

import idna

if sys.version_info[0] == 3:
    unichr = chr
    unicode = str

_RE_UNICODE = re.compile(u"\\\\u([0-9a-fA-F]{4})")
_RE_SURROGATE = re.compile(u"[\uD800-\uDBFF][\uDC00-\uDFFF]")
_MISSING_NV8 = frozenset((525, 527, 529, 531, 1022, 2083, 2914, 2919, 3482,
    3484, 4783, 4785))


def unicode_fixup(string):
    """Replace backslash-u-XXXX with appropriate unicode characters."""
    return _RE_SURROGATE.sub(lambda match: unichr(
        (ord(match.group(0)[0]) - 0xd800) * 0x400 +
        ord(match.group(0)[1]) - 0xdc00 + 0x10000),
        _RE_UNICODE.sub(lambda match: unichr(int(match.group(1), 16)), string))


def parse_idna_test_table(inputstream):
    """Parse IdnaTest.txt and return a list of tuples."""
    tests = []
    for lineno, line in enumerate(inputstream):
        line = line.decode("utf8").strip()
        if "#" in line:
            line = line.split("#", 1)[0]
        if not line:
            continue
        tests.append((lineno + 1, tuple(field.strip()
            for field in line.split(u";"))))
    return tests


class TestIdnaTest(unittest.TestCase):
    """Run one of the IdnaTest.txt test lines."""
    def __init__(self, lineno=None, fields=None):
        super(TestIdnaTest, self).__init__()
        self.lineno = lineno
        self.fields = fields

    def id(self):
        return "%s.%d" % (super(TestIdnaTest, self).id(), self.lineno)

    def shortDescription(self):
        if not self.fields:
            return ""
        return "IdnaTest.txt line %d: %r" % (self.lineno,
            u"; ".join(self.fields))

    def runTest(self):
        if not self.fields:
            return
        try:
            types, source, to_unicode, to_ascii = (unicode_fixup(field)
                for field in self.fields[:4])
            if (unicode_fixup(u"\\uD804\\uDC39") in source and
                    sys.version_info[0] < 3):
                raise unittest.SkipTest(
                    "Python 2's Unicode support is too old for this test")
        except ValueError:
            raise unittest.SkipTest(
                "Test requires Python wide Unicode support")
        if not to_unicode:
            to_unicode = source
        if not to_ascii:
            to_ascii = to_unicode
        nv8 = (len(self.fields) > 4 and self.fields[4] or
            self.lineno in _MISSING_NV8)
        try:
            output = idna.decode(source, uts46=True, strict=True)
            if to_unicode[0] == u"[":
                self.fail("decode() did not emit required error")
            self.assertEqual(output, to_unicode, "unexpected decode() output")
        except (idna.IDNAError, UnicodeError, ValueError) as exc:
            if unicode(exc).startswith(u"Unknown directionality"):
                raise unittest.SkipTest("Test requires support for a newer"
                    " version of Unicode than this Python supports")
            if to_unicode[0] != u"[" and not nv8:
                raise
        for transitional in {
                u"B": (True, False),
                u"T": (True,),
                u"N": (False,),
                }[types]:
            try:
                output = idna.encode(source, uts46=True, strict=True,
                    transitional=transitional).decode("ascii")
                if to_ascii[0] == u"[":
                    self.fail(
                        "encode(transitional={0}) did not emit required error".
                        format(transitional))
                self.assertEqual(output, to_ascii,
                    "unexpected encode(transitional={0}) output".
                    format(transitional))
            except (idna.IDNAError, UnicodeError, ValueError):
                if to_ascii[0] != u"[" and not nv8:
                    raise


def load_tests(loader, tests, pattern):
    """Create a suite of all the individual tests."""
    suite = unittest.TestSuite()
    with gzip.open(os.path.join(os.path.dirname(__file__),
            "IdnaTest.txt.gz"), "rb") as tests_file:
        suite.addTests(TestIdnaTest(lineno, fields)
            for lineno, fields in parse_idna_test_table(tests_file))
    return suite
