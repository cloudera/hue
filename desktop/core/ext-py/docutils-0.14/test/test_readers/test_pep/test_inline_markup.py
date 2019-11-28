#! /usr/bin/env python

# $Id: test_inline_markup.py 7793 2015-02-17 14:55:01Z milde $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Tests for inline markup in PEPs (readers/pep.py).
"""

from __init__ import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.PEPParserTestSuite()
    s.generateTests(totest)
    return s


totest = {}

totest['standalone_references'] = [
["""\
See PEP 287 (pep-0287.txt),
and RFC 2822 (which obsoletes RFC822 and RFC-733).
""",
"""\
<document source="test data">
    <paragraph>
        See \n\
        <reference refuri="http://www.python.org/dev/peps/pep-0287">
            PEP 287
         (
        <reference refuri="http://www.python.org/dev/peps/pep-0287">
            pep-0287.txt
        ),
        and \n\
        <reference refuri="http://tools.ietf.org/html/rfc2822.html">
            RFC 2822
         (which obsoletes \n\
        <reference refuri="http://tools.ietf.org/html/rfc822.html">
            RFC822
         and \n\
        <reference refuri="http://tools.ietf.org/html/rfc733.html">
            RFC-733
        ).
"""],
["""\
References split across lines:

PEP
287

RFC
2822
""",
"""\
<document source="test data">
    <paragraph>
        References split across lines:
    <paragraph>
        <reference refuri="http://www.python.org/dev/peps/pep-0287">
            PEP
            287
    <paragraph>
        <reference refuri="http://tools.ietf.org/html/rfc2822.html">
            RFC
            2822
"""],
["""\
Test PEP-specific implicit references before a URL:

PEP 287 (http://www.python.org/dev/peps/pep-0287), RFC 2822.
""",
"""\
<document source="test data">
    <paragraph>
        Test PEP-specific implicit references before a URL:
    <paragraph>
        <reference refuri="http://www.python.org/dev/peps/pep-0287">
            PEP 287
         (
        <reference refuri="http://www.python.org/dev/peps/pep-0287">
            http://www.python.org/dev/peps/pep-0287
        ), \n\
        <reference refuri="http://tools.ietf.org/html/rfc2822.html">
            RFC 2822
        .
"""],
]

totest['miscellaneous'] = [
["""\
For *completeness*, _`let's` ``test`` **other** forms_
|of| `inline markup` [*]_.

.. [*] See http://docutils.sf.net/docs/ref/rst/restructuredtext.html.
""",
"""\
<document source="test data">
    <paragraph>
        For \n\
        <emphasis>
            completeness
        , \n\
        <target ids="let-s" names="let's">
            let's
         \n\
        <literal>
            test
         \n\
        <strong>
            other
         \n\
        <reference name="forms" refname="forms">
            forms
        \n\
        <substitution_reference refname="of">
            of
         \n\
        <title_reference>
            inline markup
         \n\
        <footnote_reference auto="*" ids="id1">
        .
    <footnote auto="*" ids="id2">
        <paragraph>
            See \n\
            <reference refuri="http://docutils.sf.net/docs/ref/rst/restructuredtext.html">
                http://docutils.sf.net/docs/ref/rst/restructuredtext.html
            .
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
