#!/usr/bin/env python

# $Id: test_publisher.py 7539 2012-11-26 13:50:06Z milde $
# Author: Martin Blais <blais@furius.ca>
# Copyright: This module has been placed in the public domain.

"""
Test the `Publisher` facade and the ``publish_*`` convenience functions.
"""

import pickle
import DocutilsTestSupport              # must be imported before docutils
import docutils
from docutils import core, nodes, io
from docutils._compat import b, bytes, u_prefix


test_document = """\
Test Document
=============

This is a test document with a broken reference: nonexistent_
"""
pseudoxml_output = b("""\
<document ids="test-document" names="test\ document" source="<string>" title="Test Document">
    <title>
        Test Document
    <paragraph>
        This is a test document with a broken reference: \n\
        <problematic ids="id2" refid="id1">
            nonexistent_
    <section classes="system-messages">
        <title>
            Docutils System Messages
        <system_message backrefs="id2" ids="id1" level="3" line="4" source="<string>" type="ERROR">
            <paragraph>
                Unknown target name: "nonexistent".
""")
exposed_pseudoxml_output = b("""\
<document ids="test-document" internal:refnames="{%s\'nonexistent\': [<reference: <#text: \'nonexistent\'>>]}" names="test\ document" source="<string>" title="Test Document">
    <title>
        Test Document
    <paragraph>
        This is a test document with a broken reference: \n\
        <problematic ids="id2" refid="id1">
            nonexistent_
    <section classes="system-messages">
        <title>
            Docutils System Messages
        <system_message backrefs="id2" ids="id1" level="3" line="4" source="<string>" type="ERROR">
            <paragraph>
                Unknown target name: "nonexistent".
""" % u_prefix)


class PublisherTests(DocutilsTestSupport.StandardTestCase):

    def test_input_error_handling(self):
        # core.publish_cmdline(argv=['nonexisting/path'])
        # exits with a short message, if `traceback` is False,

        # pass IOErrors to calling application if `traceback` is True
        try:
            core.publish_cmdline(argv=['nonexisting/path'],
                                       settings_overrides={'traceback': True})
        except IOError, e:
            self.assertTrue(isinstance(e, io.InputError))


    def test_output_error_handling(self):
        # pass IOErrors to calling application if `traceback` is True
        try:
            core.publish_cmdline(argv=['data/include.txt', 'nonexisting/path'],
                                       settings_overrides={'traceback': True})
        except IOError, e:
            self.assertTrue(isinstance(e, io.OutputError))


class PublishDoctreeTestCase(DocutilsTestSupport.StandardTestCase, docutils.SettingsSpec):

    settings_default_overrides = {
        '_disable_config': True,
        'warning_stream': io.NullOutput()}

    def test_publish_doctree(self):
        # Test `publish_doctree` and `publish_from_doctree`.

        # Produce the document tree.
        doctree = core.publish_doctree(
            source=test_document, reader_name='standalone',
            parser_name='restructuredtext', settings_spec=self,
            settings_overrides={'expose_internals':
                                ['refnames', 'do_not_expose'],
                                'report_level': 5})
        self.assertTrue(isinstance(doctree, nodes.document))

        # Confirm that transforms have been applied (in this case, the
        # DocTitle transform):
        self.assertTrue(isinstance(doctree[0], nodes.title))
        self.assertTrue(isinstance(doctree[1], nodes.paragraph))
        # Confirm that the Messages transform has not yet been applied:
        self.assertEqual(len(doctree), 2)

        # The `do_not_expose` attribute may not show up in the
        # pseudoxml output because the expose_internals transform may
        # not be applied twice.
        doctree.do_not_expose = 'test'
        # Write out the document:
        output = core.publish_from_doctree(
            doctree, writer_name='pseudoxml',
            settings_spec=self,
            settings_overrides={'expose_internals':
                                ['refnames', 'do_not_expose'],
                                'report_level': 1})
        self.assertEqual(output, exposed_pseudoxml_output)

        # Test publishing parts using document as the source.
        parts = core.publish_parts(
           reader_name='doctree', source_class=io.DocTreeInput,
           source=doctree, source_path='test', writer_name='html',
           settings_spec=self)
        self.assertTrue(isinstance(parts, dict))

    def test_publish_pickle(self):
        # Test publishing a document tree with pickling and unpickling.

        # Produce the document tree.
        doctree = core.publish_doctree(
            source=test_document,
            reader_name='standalone',
            parser_name='restructuredtext',
            settings_spec=self)
        self.assertTrue(isinstance(doctree, nodes.document))

        # Pickle the document.  Note: if this fails, some unpickleable
        # reference has been added somewhere within the document tree.
        # If so, you need to fix that.
        #
        # Note: Please do not remove this test, this is an important
        # requirement, applications will be built on the assumption
        # that we can pickle the document.

        # Remove the reporter and the transformer before pickling.
        doctree.reporter = None
        doctree.transformer = None

        doctree_pickled = pickle.dumps(doctree)
        self.assertTrue(isinstance(doctree_pickled, bytes))
        del doctree

        # Unpickle the document.
        doctree_zombie = pickle.loads(doctree_pickled)
        self.assertTrue(isinstance(doctree_zombie, nodes.document))

        # Write out the document:
        output = core.publish_from_doctree(
            doctree_zombie, writer_name='pseudoxml',
            settings_spec=self)
        self.assertEqual(output, pseudoxml_output)


if __name__ == '__main__':
    import unittest
    unittest.main()
