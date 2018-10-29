#! /usr/bin/env python

# $Id: test_code.py 7936 2016-05-14 21:15:00Z milde $
# Author: Guenter Milde
# Copyright: This module has been placed in the public domain.

"""
Test the 'code' directive in parsers/rst/directives/body.py.
"""

from __init__ import DocutilsTestSupport
from docutils.utils.code_analyzer import with_pygments

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    if not with_pygments:
        del(totest['code-parsing'])
    s.generateTests(totest)
    return s

totest = {}

totest['code'] = [
["""\
.. code::

   This is a code block.
""",
"""\
<document source="test data">
    <literal_block classes="code" xml:space="preserve">
        This is a code block.
"""],
["""\
.. code::
  :class: testclass
  :name: without argument

  This is a code block with generic options.
""",
"""\
<document source="test data">
    <literal_block classes="code testclass" ids="without-argument" names="without\ argument" xml:space="preserve">
        This is a code block with generic options.
"""],
["""\
.. code:: text
  :class: testclass

  This is a code block with text.
""",
"""\
<document source="test data">
    <literal_block classes="code text testclass" xml:space="preserve">
        This is a code block with text.
"""],
["""\
.. code::
  :number-lines:

  This is a code block with text.
""",
"""\
<document source="test data">
    <literal_block classes="code" xml:space="preserve">
        <inline classes="ln">
            1 \n\
        This is a code block with text.
"""],
["""\
.. code::
  :number-lines: 30

  This is a code block with text.
""",
"""\
<document source="test data">
    <literal_block classes="code" xml:space="preserve">
        <inline classes="ln">
            30 \n\
        This is a code block with text.
"""],
["""\
.. code::
""",
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            Content block expected for the "code" directive; none found.
        <literal_block xml:space="preserve">
            .. code::
"""],
]

totest['code-parsing'] = [
["""\
.. code:: python
  :class: testclass

   print 'hello world' # to stdout
""",
"""\
<document source="test data">
    <literal_block classes="code python testclass" xml:space="preserve">
         \n\
        <inline classes="keyword">
            print
         \n\
        <inline classes="literal string single">
            'hello world'
         \n\
        <inline classes="comment single">
            # to stdout
"""],
["""\
.. code:: python
  :class: testclass
  :name: my_function
  :number-lines: 7

  def my_function():
      '''Test the lexer.
      '''

      # and now for something completely different
      print 8/2
""",
"""\
<document source="test data">
    <literal_block classes="code python testclass" ids="my-function" names="my_function" xml:space="preserve">
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
  :class: testclass

  hello \emph{world} % emphasize
""",
"""\
<document source="test data">
    <literal_block classes="code latex testclass" xml:space="preserve">
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
["""\
.. code:: rst
  :number-lines:

  This is a code block with text.
""",
"""\
<document source="test data">
    <literal_block classes="code rst" xml:space="preserve">
        <inline classes="ln">
            1 \n\
        This is a code block with text.
"""],
["""\
.. code:: s-lang

   % abc.sl
   autoload("abc_mode", "abc");
""",
"""\
<document source="test data">
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Cannot analyze code. No Pygments lexer found for "s-lang".
        <literal_block xml:space="preserve">
            .. code:: s-lang
            \n\
               % abc.sl
               autoload("abc_mode", "abc");
"""],
["""\
Place the language name in a class argument to avoid the no-lexer warning:

.. code::
   :class: s-lang

   % abc.sl
   autoload("abc_mode", "abc");
""",
"""\
<document source="test data">
    <paragraph>
        Place the language name in a class argument to avoid the no-lexer warning:
    <literal_block classes="code s-lang" xml:space="preserve">
        % abc.sl
        autoload("abc_mode", "abc");
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
