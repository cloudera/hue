# -*- coding: utf-8 -*-
# $Id: local-reader.py 7504 2012-08-27 07:55:20Z grubert $
# Authors: Engelbert Gruber <grubert@users.sourceforge.net>
#          Toshio Kuratomi <toshio@fedoraproject.org>
# Copyright: This module is put into the public domain.

"""
mini-reader to test get_reader_class with local reader
"""

import docutils
from docutils import readers

class Reader(readers.Reader):

    supported = ('dummy',)
    """Formats this reader supports."""

    document = None
    """A document tree."""
