#!/usr/bin/env python

# $Id: test_pseudoxml.py 5174 2007-05-31 00:01:52Z wiemann $
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Test for pseudo-XML writer.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.PublishTestSuite('pseudoxml')
    s.generateTests(totest)
    return s

totest = {}

totest['basic'] = [
# input
["""\
This is a paragraph.

----------

This is another paragraph.

A Section
---------

Foo.
""",
# output
"""\
<document source="<string>">
    <paragraph>
        This is a paragraph.
    <transition>
    <paragraph>
        This is another paragraph.
    <section ids="a-section" names="a\ section">
        <title>
            A Section
        <paragraph>
            Foo.
"""]
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
