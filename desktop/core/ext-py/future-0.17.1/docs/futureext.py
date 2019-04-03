# -*- coding: utf-8 -*-
"""
    Python-Future Documentation Extensions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Support for automatically documenting filters and tests.

    Based on the Jinja2 documentation extensions.

    :copyright: Copyright 2008 by Armin Ronacher.
    :license: BSD.
"""
import collections
import os
import re
import inspect
from itertools import islice
from types import BuiltinFunctionType
from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.ext.autodoc import prepare_docstring
from sphinx.application import TemplateBridge
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic


def parse_rst(state, content_offset, doc):
    node = nodes.section()
    # hack around title style bookkeeping
    surrounding_title_styles = state.memo.title_styles
    surrounding_section_level = state.memo.section_level
    state.memo.title_styles = []
    state.memo.section_level = 0
    state.nested_parse(doc, content_offset, node, match_titles=1)
    state.memo.title_styles = surrounding_title_styles
    state.memo.section_level = surrounding_section_level
    return node.children


class FutureStyle(Style):
    title = 'Future Style'
    default_style = ""
    styles = {
        Comment:                    'italic #0B6A94',  # was: #0066ff',
        Comment.Preproc:            'noitalic #B11414',
        Comment.Special:            'italic #505050',

        Keyword:                    'bold #D15E27',
        Keyword.Type:               '#D15E27',

        Operator.Word:              'bold #B80000',

        Name.Builtin:               '#333333',
        Name.Function:              '#333333',
        Name.Class:                 'bold #333333',
        Name.Namespace:             'bold #333333',
        Name.Entity:                'bold #363636',
        Name.Attribute:             '#686868',
        Name.Tag:                   'bold #686868',
        Name.Decorator:             '#686868',

        String:                     '#AA891C',
        Number:                     '#444444',

        Generic.Heading:            'bold #000080',
        Generic.Subheading:         'bold #800080',
        Generic.Deleted:            '#aa0000',
        Generic.Inserted:           '#00aa00',
        Generic.Error:              '#aa0000',
        Generic.Emph:               'italic',
        Generic.Strong:             'bold',
        Generic.Prompt:             '#555555',
        Generic.Output:             '#888888',
        Generic.Traceback:          '#aa0000',

        Error:                      '#F00 bg:#FAA'
    }

def setup(app):
    pass
    # uncomment for inline toc.  links are broken unfortunately
    ##app.connect('doctree-resolved', inject_toc)
