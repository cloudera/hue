from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


import os.path

from openpyxl.comments import Comment
from openpyxl.xml.constants import (
    PACKAGE_WORKSHEET_RELS,
    SHEET_MAIN_NS,
    COMMENTS_NS,
    PACKAGE_XL,
    )
from openpyxl.xml.functions import fromstring, safe_iterator

def _get_author_list(root):
    author_subtree = root.find('{%s}authors' % SHEET_MAIN_NS)
    return [author.text for author in author_subtree]

def read_comments(ws, xml_source):
    """Given a worksheet and the XML of its comments file, assigns comments to cells"""
    root = fromstring(xml_source)
    authors = _get_author_list(root)
    comment_nodes = safe_iterator(root, ('{%s}comment' % SHEET_MAIN_NS))
    for node in comment_nodes:
        author = authors[int(node.attrib['authorId'])]
        cell = node.attrib['ref']
        text_node = node.find('{%s}text' % SHEET_MAIN_NS)
        substrs = []
        for run in text_node.findall('{%s}r' % SHEET_MAIN_NS):
            runtext = ''.join([t.text for t in run.findall('{%s}t' % SHEET_MAIN_NS)])
            substrs.append(runtext)
        comment_text = ''.join(substrs)

        comment = Comment(comment_text, author)
        ws.cell(coordinate=cell).comment = comment

def get_comments_file(worksheet_path, archive, valid_files):
    """Returns the XML filename in the archive which contains the comments for
    the spreadsheet with codename sheet_codename. Returns None if there is no
    such file"""
    sheet_codename = os.path.split(worksheet_path)[-1]
    rels_file = PACKAGE_WORKSHEET_RELS + '/' + sheet_codename + '.rels'
    if rels_file not in valid_files:
        return None
    rels_source = archive.read(rels_file)
    root = fromstring(rels_source)
    for i in root:
        if i.attrib['Type'] == COMMENTS_NS:
            comments_file = os.path.split(i.attrib['Target'])[-1]
            comments_file = PACKAGE_XL + '/' + comments_file
            if comments_file in valid_files:
                return comments_file
    return None
