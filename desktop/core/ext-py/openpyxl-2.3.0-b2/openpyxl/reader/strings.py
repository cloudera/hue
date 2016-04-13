from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Read the shared strings table."""

from openpyxl.compat import unicode

# package imports
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.xml.functions import fromstring, safe_iterator
from openpyxl.xml.constants import SHEET_MAIN_NS, XML_NS


def read_string_table(xml_source):
    """Read in all shared strings in the table"""
    root = fromstring(text=xml_source)
    nodes = safe_iterator(root, '{%s}si' % SHEET_MAIN_NS)
    strings = (get_string(node) for node in nodes)
    return IndexedList(strings)


def get_string(string_index_node):
    """Read the contents of a specific string index"""
    rich_nodes = string_index_node.findall('{%s}r' % SHEET_MAIN_NS)
    if rich_nodes:
        reconstructed_text = []
        for rich_node in rich_nodes:
            partial_text = get_text(rich_node)
            reconstructed_text.append(partial_text)
        return unicode(''.join(reconstructed_text))
    return get_text(string_index_node)


def get_text(rich_node):
    """Read rich text, discarding formatting if not disallowed"""
    text_node = rich_node.find('{%s}t' % SHEET_MAIN_NS)
    text = text_node.text or unicode('')

    if text_node.get('{%s}space' % XML_NS) != 'preserve':
        text = text.strip()

    # fix XML escaping sequence for '_x'
    text = text.replace('x005F_', '')
    return unicode(text)
