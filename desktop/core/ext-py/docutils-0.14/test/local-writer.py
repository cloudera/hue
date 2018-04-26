# -*- coding: utf-8 -*-
# $Id: local-writer.py 7500 2012-08-22 19:38:14Z grubert $
# Author: Engelbert Gruber <grubert@users.sourceforge.net>
# Copyright: This module is put into the public domain.

"""
mini-writer to test get_writer_class with local writer
"""

import docutils
from docutils import nodes, writers, languages
try:
    import roman
except ImportError:
    import docutils.utils.roman as roman

class Writer(writers.Writer):

    supported = ('dummy',)
    """Formats this writer supports."""

    output = None
    """Final translated form of `document`."""

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = Translator

    def translate(self):
        visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()

class Translator(nodes.NodeVisitor):
    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)


