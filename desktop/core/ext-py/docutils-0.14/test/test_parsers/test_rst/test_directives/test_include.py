#! /usr/bin/env python

# $Id: test_include.py 7959 2016-07-28 21:56:00Z milde $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Tests for misc.py "include" directive.
"""

import os.path
import sys
from __init__ import DocutilsTestSupport
from docutils.parsers.rst import states
from docutils._compat import b
from docutils.utils.code_analyzer import with_pygments

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    if not with_pygments:
        del(totest['include-code'])
    s.generateTests(totest)
    return s

# prepend this directory (relative to the test root):
def mydir(path):
    return os.path.join('test_parsers/test_rst/test_directives/', path)
# make `path` relative with utils.relative_path():
def reldir(path):
    return DocutilsTestSupport.utils.relative_path(None, path)

include1 = mydir('include1.txt')
include2 = mydir('include2.txt')
include3 = mydir('include3.txt')
include6 = mydir('includes/more/include6.txt')
include8 = mydir('include8.txt')
include10 = mydir('include10.txt')
include11 = mydir('include 11.txt')
include12 = mydir('include12.txt')
include13 = mydir('include13.txt')
include14 = mydir('includes/include14.txt')
include_literal = mydir('include_literal.txt')
utf_16_file = mydir('utf-16.csv')
utf_16_error_str = ("UnicodeDecodeError: 'ascii' codec can't decode byte 0xfe "
                    "in position 0: ordinal not in range(128)")
if sys.version_info < (3,0):
    utf_16_error_str = ("UnicodeError: Unable to decode input data.  "
                        "Tried the following encodings: 'ascii'.\n"
                        "            (%s)" % utf_16_error_str)
nonexistent = os.path.join(os.path.dirname(states.__file__),
                           'include', 'nonexistent')
nonexistent_rel = DocutilsTestSupport.utils.relative_path(
    os.path.join(DocutilsTestSupport.testroot, 'dummy'), nonexistent)

# Different error for path with 8bit chars with locale == C or None:
try:
    open(u'\u043c\u0438\u0440.txt')
except UnicodeEncodeError:
    errstr_8bit_path = u"""\
Cannot encode input file path "\u043c\u0438\u0440.txt" (wrong locale?).\
"""
except:
    errstr_8bit_path = u"""\
InputError: [Errno 2] No such file or directory: '\u043c\u0438\u0440.txt'.\
"""

totest = {}

totest['include'] = [
["""\
Include Test
============

.. include:: %s

A paragraph.
""" % include1,
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <section ids="inclusion-1" names="inclusion\ 1">
            <title>
                Inclusion 1
            <paragraph>
                This file is used by \n\
                <literal>
                    test_include.py
                .
            <paragraph>
                A paragraph.
"""],
["""\
Include Test
============

.. include:: %s
   :literal:
   :class: test
   :name: my name

A paragraph.
""" % include1,
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <literal_block classes="test" ids="my-name" names="my\ name" source="%s" xml:space="preserve">
            Inclusion 1
            -----------
            \n\
            This file is used by ``test_include.py``.
        <paragraph>
            A paragraph.
""" % reldir(include1)],
["""\
Literal include, add line numbers

.. include:: %s
   :literal:
   :number-lines:
""" % include1,
"""\
<document source="test data">
    <paragraph>
        Literal include, add line numbers
    <literal_block source="%s" xml:space="preserve">
        <inline classes="ln">
            1 \n\
        Inclusion 1
        <inline classes="ln">
            2 \n\
        -----------
        <inline classes="ln">
            3 \n\
        \n\
        <inline classes="ln">
            4 \n\
        This file is used by ``test_include.py``.
""" % reldir(include1)],
["""\
Include code

.. include:: %s
   :code:
   :class: test
   :name: my name
""" % include1,
"""\
<document source="test data">
    <paragraph>
        Include code
    <literal_block classes="code test" ids="my-name" names="my\ name" source="%s" xml:space="preserve">
        Inclusion 1
        -----------
        \n\
        This file is used by ``test_include.py``.
""" % reldir(include1)],
["""\
Include code, add line numbers

.. include:: %s
   :code:
   :number-lines:
""" % include1,
"""\
<document source="test data">
    <paragraph>
        Include code, add line numbers
    <literal_block classes="code" source="%s" xml:space="preserve">
        <inline classes="ln">
            1 \n\
        Inclusion 1
        <inline classes="ln">
            2 \n\
        -----------
        <inline classes="ln">
            3 \n\
        \n\
        <inline classes="ln">
            4 \n\
        This file is used by ``test_include.py``.
""" % reldir(include1)],
["""\
Let's test the parse context.

    This paragraph is in a block quote.

    .. include:: %s

The included paragraphs should also be in the block quote.
""" % include2,
"""\
<document source="test data">
    <paragraph>
        Let's test the parse context.
    <block_quote>
        <paragraph>
            This paragraph is in a block quote.
        <paragraph>
            Here are some paragraphs
            that can appear at any level.
        <paragraph>
            This file (include2.txt) is used by
            <literal>
                test_include.py
            .
    <paragraph>
        The included paragraphs should also be in the block quote.
"""],
["""\
Include Test
============

.. include:: nonexistent.txt

A paragraph.
""",
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <system_message level="4" line="4" source="test data" type="SEVERE">
            <paragraph>
                Problems with "include" directive path:
                InputError: [Errno 2] No such file or directory: 'nonexistent.txt'.
            <literal_block xml:space="preserve">
                .. include:: nonexistent.txt
        <paragraph>
            A paragraph.
"""],
["""\
Include Test
============

.. include:: %s

.. include:: %s

A paragraph.
""" % (include1, include1),
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <section dupnames="inclusion\ 1" ids="inclusion-1">
            <title>
                Inclusion 1
            <paragraph>
                This file is used by 
                <literal>
                    test_include.py
                .
        <section dupnames="inclusion\ 1" ids="id1">
            <title>
                Inclusion 1
            <system_message backrefs="id1" level="1" line="2" source="%s" type="INFO">
                <paragraph>
                    Duplicate implicit target name: "inclusion 1".
            <paragraph>
                This file is used by 
                <literal>
                    test_include.py
                .
            <paragraph>
                A paragraph.
""" % reldir(include1)],
["""\
Include Test
============

.. include:: %s

----------

.. include:: %s

A paragraph.
""" % (include1, include1),
"""\
<document source="test data">
    <section ids="include-test" names="include\ test">
        <title>
            Include Test
        <section dupnames="inclusion\ 1" ids="inclusion-1">
            <title>
                Inclusion 1
            <paragraph>
                This file is used by \n\
                <literal>
                    test_include.py
                .
            <transition>
        <section dupnames="inclusion\ 1" ids="id1">
            <title>
                Inclusion 1
            <system_message backrefs="id1" level="1" line="2" source="%s" type="INFO">
                <paragraph>
                    Duplicate implicit target name: "inclusion 1".
            <paragraph>
                This file is used by \n\
                <literal>
                    test_include.py
                .
            <paragraph>
                A paragraph.
""" % reldir(include1)],
["""\
Recursive inclusions: adapt paths.

In test data

.. include:: %s
""" % include3,
"""\
<document source="test data">
    <paragraph>
        Recursive inclusions: adapt paths.
    <paragraph>
        In test data
    <paragraph>
        In include3.txt
    <paragraph>
        In includes/include4.txt
    <paragraph>
        In includes/include5.txt
    <paragraph>
        In includes/more/include6.txt
    <paragraph>
        In includes/sibling/include7.txt
    <literal_block source="test_parsers/test_rst/test_directives/includes/include5.txt" xml:space="preserve">
        In includes/include5.txt
        
        .. include:: more/include6.txt
    <table>
        <tgroup cols="2">
            <colspec colwidth="50">
            <colspec colwidth="50">
            <tbody>
                <row>
                    <entry>
                        <paragraph>
                            In
                    <entry>
                        <paragraph>
                            includes/sibling/include7.txt
"""],
["""\
In test data

Section
=======

(Section contents in nested parse; slice of input_lines ViewList.)

.. include:: %s
""" % include3,
"""\
<document source="test data">
    <paragraph>
        In test data
    <section ids="section" names="section">
        <title>
            Section
        <paragraph>
            (Section contents in nested parse; slice of input_lines ViewList.)
        <paragraph>
            In include3.txt
        <paragraph>
            In includes/include4.txt
        <paragraph>
            In includes/include5.txt
        <paragraph>
            In includes/more/include6.txt
        <paragraph>
            In includes/sibling/include7.txt
        <literal_block source="test_parsers/test_rst/test_directives/includes/include5.txt" xml:space="preserve">
            In includes/include5.txt
            
            .. include:: more/include6.txt
        <table>
            <tgroup cols="2">
                <colspec colwidth="50">
                <colspec colwidth="50">
                <tbody>
                    <row>
                        <entry>
                            <paragraph>
                                In
                        <entry>
                            <paragraph>
                                includes/sibling/include7.txt
"""],
["""\
Testing relative includes:

.. include:: %s
""" % include8,
"""\
<document source="test data">
    <paragraph>
        Testing relative includes:
    <paragraph>
        In include8.txt
    <paragraph>
        In ../includes/include9.txt.
    <paragraph>
        Here are some paragraphs
        that can appear at any level.
    <paragraph>
        This file (include2.txt) is used by
        <literal>
            test_include.py
        .
"""],
["""\
Encoding:

.. include:: %s
   :encoding: utf-16
""" % reldir(utf_16_file),
b("""\
<document source="test data">
    <paragraph>
        Encoding:
    <paragraph>
        "Treat", "Quantity", "Description"
        "Albatr\xb0\xdf", 2.99, "\xa1On a \\u03c3\\u03c4\\u03b9\\u03ba!"
        "Crunchy Frog", 1.49, "If we took the b\xf6nes out, it wouldn\\u2019t be
        crunchy, now would it?"
        "Gannet Ripple", 1.99, "\xbfOn a \\u03c3\\u03c4\\u03b9\\u03ba?"
""").decode('raw_unicode_escape')],
["""\
Include file is UTF-16-encoded, and is not valid ASCII.

.. include:: %s
   :encoding: ascii
""" % reldir(utf_16_file),
"""\
<document source="test data">
    <paragraph>
        Include file is UTF-16-encoded, and is not valid ASCII.
    <system_message level="4" line="3" source="test data" type="SEVERE">
        <paragraph>
            Problem with "include" directive:
            %s
        <literal_block xml:space="preserve">
            .. include:: %s
               :encoding: ascii
""" % (utf_16_error_str, reldir(utf_16_file))],
[u"""\
cyrillic filename:

.. include:: \u043c\u0438\u0440.txt
""",
u"""\
<document source="test data">
    <paragraph>
        cyrillic filename:
    <system_message level="4" line="3" source="test data" type="SEVERE">
        <paragraph>
            Problems with "include" directive path:
            %s
        <literal_block xml:space="preserve">
            .. include:: \u043c\u0438\u0440.txt
""" % errstr_8bit_path],
["""\
Testing errors in included file:

.. include:: %s
""" % include10,
"""\
<document source="test data">
    <paragraph>
        Testing errors in included file:
    <system_message level="3" line="1" source="%(source)s" type="ERROR">
        <paragraph>
            Invalid character code: 0x11111111
            %(unichr_exception)s
        <literal_block xml:space="preserve">
            unicode:: 0x11111111
    <system_message level="2" line="1" source="%(source)s" type="WARNING">
        <paragraph>
            Substitution definition "bad" empty or invalid.
        <literal_block xml:space="preserve">
            .. |bad| unicode:: 0x11111111
    <section dupnames="hi" ids="hi">
        <title>
            hi
        <block_quote>
            <paragraph>
                indent
        <system_message level="2" line="7" source="%(source)s" type="WARNING">
            <paragraph>
                Block quote ends without a blank line; unexpected unindent.
        <paragraph>
            error
    <section dupnames="hi" ids="id1">
        <title>
            hi
        <system_message backrefs="id1" level="1" line="10" source="%(source)s" type="INFO">
            <paragraph>
                Duplicate implicit target name: "hi".
        <system_message level="4" line="12" source="%(source)s" type="SEVERE">
            <paragraph>
                Problems with "include" directive path:
                InputError: [Errno 2] No such file or directory: '%(nonexistent)s'.
            <literal_block xml:space="preserve">
                .. include:: <nonexistent>
        <system_message level="3" line="14" source="%(source)s" type="ERROR">
            <paragraph>
                Content block expected for the "note" directive; none found.
            <literal_block xml:space="preserve">
                .. note::
        <system_message level="3" line="16" source="%(source)s" type="ERROR">
            <paragraph>
                Content block expected for the "admonition" directive; none found.
            <literal_block xml:space="preserve">
                .. admonition::
                   without title
        <system_message level="3" line="19" source="%(source)s" type="ERROR">
            <paragraph>
                Content block expected for the "epigraph" directive; none found.
            <literal_block xml:space="preserve">
                .. epigraph::
        <system_message level="3" line="21" source="%(source)s" type="ERROR">
            <paragraph>
                Content block expected for the "highlights" directive; none found.
            <literal_block xml:space="preserve">
                .. highlights::
        <system_message level="3" line="23" source="%(source)s" type="ERROR">
            <paragraph>
                Content block expected for the "pull-quote" directive; none found.
            <literal_block xml:space="preserve">
                .. pull-quote::
        <system_message level="3" line="25" source="%(source)s" type="ERROR">
            <paragraph>
                Invalid context: the "date" directive can only be used within a substitution definition.
            <literal_block xml:space="preserve">
                .. date::
        <paragraph>
            not a
            definition list:
        <system_message level="3" line="29" source="%(source)s" type="ERROR">
            <paragraph>
                Unexpected indentation.
        <block_quote>
            <paragraph>
                as a term may only be one line long.
        <system_message level="3" line="31" source="%(source)s" type="ERROR">
            <paragraph>
                Error in "admonition" directive:
                1 argument(s) required, 0 supplied.
            <literal_block xml:space="preserve">
                .. admonition::
                
                   without title and content following a blank line
    <section ids="section-underline-too-short" names="section\ underline\ too\ short">
        <title>
            section underline too short
        <system_message level="2" line="36" source="%(source)s" type="WARNING">
            <paragraph>
                Title underline too short.
            <literal_block xml:space="preserve">
                section underline too short
                -----
        <table>
            <tgroup cols="2">
                <colspec colwidth="14">
                <colspec colwidth="6">
                <thead>
                    <row>
                        <entry>
                            <paragraph>
                                A simple table
                        <entry>
                            <paragraph>
                                cell 2
                <tbody>
                    <row>
                        <entry>
                            <paragraph>
                                cell 3
                        <entry>
                            <paragraph>
                                cell 4
        <system_message level="2" line="43" source="%(source)s" type="WARNING">
            <paragraph>
                Blank line required after table.
        <paragraph>
            No blank line after table.
        <system_message level="3" line="45" source="%(source)s" type="ERROR">
            <paragraph>
                Error in "unicode" directive:
                1 argument(s) required, 0 supplied.
            <literal_block xml:space="preserve">
                unicode::
        <system_message level="2" line="45" source="%(source)s" type="WARNING">
            <paragraph>
                Substitution definition "empty" empty or invalid.
            <literal_block xml:space="preserve">
                .. |empty| unicode::
        <system_message level="3" line="47" source="%(source)s" type="ERROR">
            <paragraph>
                Error in "topic" directive:
                1 argument(s) required, 0 supplied.
            <literal_block xml:space="preserve">
                .. topic::
        <system_message level="3" line="49" source="%(source)s" type="ERROR">
            <paragraph>
                Error in "rubric" directive:
                1 argument(s) required, 0 supplied.
            <literal_block xml:space="preserve">
                .. rubric::
        <rubric>
            A rubric has no content
        <comment xml:space="preserve">
            _`target: No matching backquote.
        <system_message level="2" line="52" source="%(source)s" type="WARNING">
            <paragraph>
                malformed hyperlink target.
        <comment xml:space="preserve">
            __malformed: no good
        <system_message level="2" line="53" source="%(source)s" type="WARNING">
            <paragraph>
                malformed hyperlink target.
        <definition_list>
            <definition_list_item>
                <term>
                    A literal block::
                <definition>
                    <system_message level="1" line="57" source="%(source)s" type="INFO">
                        <paragraph>
                            Blank line missing before literal block (after the "::")? Interpreted as a definition list item.
                    <paragraph>
                        with no blank line above.
        <literal_block xml:space="preserve">
            > A literal block.
        <system_message level="3" line="61" source="%(source)s" type="ERROR">
            <paragraph>
                Inconsistent literal block quoting.
        <paragraph>
            $ with inconsistent quoting.
        <paragraph>
            <problematic ids="id3" refid="id2">
                :unknown-role:`role`
            
            and 
            <problematic ids="id5" refid="id4">
                *
            unbalanced
            <problematic ids="id7" refid="id6">
                `
            inline
            <problematic ids="id9" refid="id8">
                **
            markup
        <system_message level="1" line="63" source="%(source)s" type="INFO">
            <paragraph>
                No role entry for "unknown-role" in module "docutils.parsers.rst.languages.en".
                Trying "unknown-role" as canonical role name.
        <system_message backrefs="id3" ids="id2" level="3" line="63" source="%(source)s" type="ERROR">
            <paragraph>
                Unknown interpreted text role "unknown-role".
        <system_message backrefs="id5" ids="id4" level="2" line="63" source="%(source)s" type="WARNING">
            <paragraph>
                Inline emphasis start-string without end-string.
        <system_message backrefs="id7" ids="id6" level="2" line="63" source="%(source)s" type="WARNING">
            <paragraph>
                Inline interpreted text or phrase reference start-string without end-string.
        <system_message backrefs="id9" ids="id8" level="2" line="63" source="%(source)s" type="WARNING">
            <paragraph>
                Inline strong start-string without end-string.
        <paragraph>
            <problematic ids="id11" refid="id10">
                :PEP:`-1`
        <system_message backrefs="id11" ids="id10" level="3" line="68" source="%(source)s" type="ERROR">
            <paragraph>
                PEP number must be a number from 0 to 9999; "-1" is invalid.
        <system_message level="1" line="66" source="%(source)s" type="INFO">
            <paragraph>
                No directive entry for "unknown" in module "docutils.parsers.rst.languages.en".
                Trying "unknown" as canonical directive name.
        <system_message level="3" line="70" source="%(source)s" type="ERROR">
            <paragraph>
                Unknown directive type "unknown".
            <literal_block xml:space="preserve">
                .. unknown:: directive (info still reported with wrong line)
        <system_message level="3" line="72" source="%(source)s" type="ERROR">
            <paragraph>
                Malformed table.
                No bottom table border found.
            <literal_block xml:space="preserve">
                ==============  ======
                A simple table  with
                no bottom       border
""" % {'source': reldir(include10), 'nonexistent': reldir(nonexistent),
       'unichr_exception':
       DocutilsTestSupport.exception_data(unichr, int("11111111", 16))[2]
      }],
["""\
Include file with whitespace in the path:

.. include:: %s
""" % reldir(include11),
"""\
<document source="test data">
    <paragraph>
        Include file with whitespace in the path:
    <paragraph>
        some text
"""],
["""\
Standard include data file:

.. include:: <isogrk4.txt>
""",
b("""\
<document source="test data">
    <paragraph>
        Standard include data file:
    <comment xml:space="preserve">
        This data file has been placed in the public domain.
    <comment xml:space="preserve">
        Derived from the Unicode character mappings available from
        <http://www.w3.org/2003/entities/xml/>.
        Processed by unicode2rstsubs.py, part of Docutils:
        <http://docutils.sourceforge.net>.
    <substitution_definition names="b.Gammad">
        \\u03dc
    <substitution_definition names="b.gammad">
        \\u03dd
""").decode('raw_unicode_escape')],
["""\
Nonexistent standard include data file:

.. include:: <nonexistent>
""",
"""\
<document source="test data">
    <paragraph>
        Nonexistent standard include data file:
    <system_message level="4" line="3" source="test data" type="SEVERE">
        <paragraph>
            Problems with "include" directive path:
            InputError: [Errno 2] No such file or directory: '%s'.
        <literal_block xml:space="preserve">
            .. include:: <nonexistent>
""" % nonexistent_rel],
["""\
Include start-line/end-line Test

.. include:: %s
   :start-line: 3
   :end-line: 4
""" % include2,
"""\
<document source="test data">
    <paragraph>
        Include start-line/end-line Test
    <paragraph>
        This file (include2.txt) is used by
"""],
["""\
Include start-line/end-line + start-after Test

.. include:: %s
   :start-line: 2
   :end-line: 5
   :start-after: here

Text search is limited to the specified lines.
""" % include12,
"""\
<document source="test data">
    <paragraph>
        Include start-line/end-line + start-after Test
    <paragraph>
        In include12.txt (after "start here", before "stop here")
    <paragraph>
        Text search is limited to the specified lines.
"""],
["""\
Include start-after/end-before Test

.. include:: %s
   :start-after: .. start here
   :end-before: .. stop here

A paragraph.
""" % include12,
"""\
<document source="test data">
    <paragraph>
        Include start-after/end-before Test
    <paragraph>
        In include12.txt (after "start here", before "stop here")
    <paragraph>
        A paragraph.
"""],
["""\
Include start-after/end-before Test, single option variant

.. include:: %s
   :end-before: .. start here

.. include:: %s
   :start-after: .. stop here

A paragraph.
""" % (include12, include12),
"""\
<document source="test data">
    <paragraph>
        Include start-after/end-before Test, single option variant
    <paragraph>
        In include12.txt (but before "start here")
    <paragraph>
        In include12.txt (after "stop here")
    <paragraph>
        A paragraph.
"""],
["""\
Include start-after/end-before multi-line test.

.. include:: %s
   :start-after: From: me
                 To: you
   :end-before: -------
                -- mork of ork

.. include:: %s
   :start-after: From: me
                 To: you
   :end-before:
       -------
         -- mork of ork

A paragraph.
""" % (include13, include13),
"""\
<document source="test data">
    <paragraph>
        Include start-after/end-before multi-line test.
    <system_message level="4" line="3" source="test data" type="SEVERE">
        <paragraph>
            Problem with "end-before" option of "include" directive:
            Text not found.
        <literal_block xml:space="preserve">
            .. include:: %s
               :start-after: From: me
                             To: you
               :end-before: -------
                            -- mork of ork
    <paragraph>
        In include13.txt (between header and signature)
    <paragraph>
        A paragraph.
""" % include13],
["""\
Error handling test; "end-before" error handling tested in previous test.

.. include:: %s
   :start-after: bad string
   :end-before: mork of ork
""" % include13,
"""\
<document source="test data">
    <paragraph>
        Error handling test; "end-before" error handling tested in previous test.
    <system_message level="4" line="3" source="test data" type="SEVERE">
        <paragraph>
            Problem with "start-after" option of "include" directive:
            Text not found.
        <literal_block xml:space="preserve">
            .. include:: %s
               :start-after: bad string
               :end-before: mork of ork
""" % include13],
["""\
TAB expansion with literal include:

.. include:: %s
   :literal:
""" % include_literal,
"""\
<document source="test data">
    <paragraph>
        TAB expansion with literal include:
    <literal_block source="%s" xml:space="preserve">
        Literal included this should **not** be *marked* `up`.
                <- leading raw tab.
        
        Newlines
        are
        normalized.
""" % include_literal],
["""\
Custom TAB expansion with literal include:

.. include:: %s
   :literal:
   :tab-width: 2
""" % include_literal,
"""\
<document source="test data">
    <paragraph>
        Custom TAB expansion with literal include:
    <literal_block source="%s" xml:space="preserve">
        Literal included this should **not** be *marked* `up`.
          <- leading raw tab.
        
        Newlines
        are
        normalized.
""" % include_literal],
["""\
No TAB expansion with literal include:

.. include:: %s
   :literal:
   :tab-width: -1
""" % include_literal,
"""\
<document source="test data">
    <paragraph>
        No TAB expansion with literal include:
    <literal_block source="%s" xml:space="preserve">
        Literal included this should **not** be *marked* `up`.
        \t<- leading raw tab.
        
        Newlines
        are
        normalized.
""" % include_literal],
]

totest['include-code'] = [
["""\
Included code

.. include:: %s
   :code: rst
""" % include1,
"""\
<document source="test data">
    <paragraph>
        Included code
    <literal_block classes="code rst" source="%s" xml:space="preserve">
        <inline classes="generic heading">
            Inclusion 1
        \n\
        <inline classes="generic heading">
            -----------
        \n\
        \n\
        This file is used by \n\
        <inline classes="literal string">
            ``test_include.py``
        .
""" % reldir(include1)],
["""\
Included code

.. include:: %s
   :code: rst
   :number-lines:
""" % include1,
"""\
<document source="test data">
    <paragraph>
        Included code
    <literal_block classes="code rst" source="%s" xml:space="preserve">
        <inline classes="ln">
            1 \n\
        <inline classes="generic heading">
            Inclusion 1
        \n\
        <inline classes="ln">
            2 \n\
        <inline classes="generic heading">
            -----------
        \n\
        <inline classes="ln">
            3 \n\
        \n\
        <inline classes="ln">
            4 \n\
        This file is used by \n\
        <inline classes="literal string">
            ``test_include.py``
        .
""" % reldir(include1)],
["""\
Including includes/include14.txt

.. include:: %s
""" % include14,
"""\
<document source="test data">
    <paragraph>
        Including includes/include14.txt
    <paragraph>
        Including more/include6.txt as rst-code from includes/include14.txt:
    <literal_block classes="code rst" source="%s" xml:space="preserve">
        In includes/more/include6.txt
        \n\
        <inline classes="punctuation">
            ..
         \n\
        <inline classes="operator word">
            include
        <inline classes="punctuation">
            ::
         ../sibling/include7.txt
""" % reldir(include6)],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
