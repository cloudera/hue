from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


from openpyxl.xml.functions import Element
from openpyxl.xml.constants import (
    PKG_REL_NS,
)
from openpyxl.packaging.relationship import Relationship


def write_rels(worksheet, comments_id=None, vba_controls_id=None):
    """Write relationships for the worksheet to xml."""
    root = Element('Relationships', xmlns=PKG_REL_NS)
    rels = worksheet._rels

    # VBA
    if worksheet.vba_controls is not None:
        rel = Relationship("vmlDrawing", id=worksheet.vba_controls,
                           target='/xl/drawings/vmlDrawing%s.vml' % vba_controls_id)
        rels.append(rel)

    # Comments
    if worksheet._comment_count > 0:
        rel = Relationship(type="comments", id="comments",
                           target='/xl/comments%s.xml' % comments_id)
        rels.append(rel)

        if worksheet.vba_controls is None:
            rel = Relationship(type="vmlDrawing", id="commentsvml",
                           target='/xl/drawings/commentsDrawing%s.vml' % comments_id)
            rels.append(rel)

    for idx, rel in enumerate(rels, 1):
        if rel.id is None:
            rel.id = "rId{0}".format(idx)
        root.append(rel.to_tree())

    return root
