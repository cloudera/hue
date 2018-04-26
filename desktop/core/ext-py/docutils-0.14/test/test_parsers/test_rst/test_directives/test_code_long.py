#! /usr/bin/env python

# $Id: test_code_long.py 7936 2016-05-14 21:15:00Z milde $
# Author: Guenter Milde
# Copyright: This module has been placed in the public domain.

"""
Test the 'code' directive in body.py with syntax_highlight = 'long'.
"""

from __init__ import DocutilsTestSupport
from docutils.utils.code_analyzer import with_pygments

def suite():
    s = DocutilsTestSupport.ParserTestSuite(suite_settings={'syntax_highlight':'long'})
    if with_pygments:
        s.generateTests(totest)
    return s

totest = {}

totest['code-parsing-long'] = [
["""\
.. code:: python
  :number-lines: 7

  def my_function():
      '''Test the lexer.
      '''

      # and now for something completely different
      print 8/2
""",
"""\
<document source="test data">
    <literal_block classes="code python" xml:space="preserve">
        <inline classes="ln">
             7 \n\
        <inline classes="keyword">
            def
         \n\
        <inline classes="name function">
            my_function
        <inline classes="punctuation">
            ():
        \n\
        <inline classes="ln">
             8 \n\
            \n\
        <inline classes="literal string doc">
            \'\'\'Test the lexer.
        <inline classes="ln">
             9 \n\
        <inline classes="literal string doc">
                \'\'\'
        \n\
        <inline classes="ln">
            10 \n\
        \n\
        <inline classes="ln">
            11 \n\
            \n\
        <inline classes="comment single">
            # and now for something completely different
        \n\
        <inline classes="ln">
            12 \n\
            \n\
        <inline classes="keyword">
            print
         \n\
        <inline classes="literal number integer">
            8
        <inline classes="operator">
            /
        <inline classes="literal number integer">
            2
"""],
["""\
.. code:: latex

  hello \emph{world} % emphasize
""",
"""\
<document source="test data">
    <literal_block classes="code latex" xml:space="preserve">
        hello \n\
        <inline classes="keyword">
            \\emph
        <inline classes="name builtin">
            {
        world
        <inline classes="name builtin">
            }
         \n\
        <inline classes="comment">
            % emphasize"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
