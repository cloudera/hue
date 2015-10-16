from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Read in global settings to be maintained by the workbook object."""

# package imports
from openpyxl.xml.functions import fromstring, safe_iterator
from openpyxl.xml.constants import (
    DCORE_NS,
    COREPROPS_NS,
    DCTERMS_NS,
    SHEET_MAIN_NS,
    CONTYPES_NS,
    PKG_REL_NS,
    REL_NS,
    ARC_CONTENT_TYPES,
    ARC_WORKBOOK,
    ARC_WORKBOOK_RELS,
    WORKSHEET_TYPE,
    EXTERNAL_LINK,
)
from openpyxl.workbook import DocumentProperties
from openpyxl.utils.datetime  import (
    CALENDAR_WINDOWS_1900,
    CALENDAR_MAC_1904
    )
from openpyxl.workbook.names.named_range import (
    NamedRange,
    NamedValue,
    split_named_range,
    refers_to_range,
    external_range,
    )

import datetime
import re

# constants
VALID_WORKSHEET = WORKSHEET_TYPE


def read_excel_base_date(archive):
    src = archive.read(ARC_WORKBOOK)
    root = fromstring(src)
    wbPr = root.find('{%s}workbookPr' % SHEET_MAIN_NS)
    if wbPr is not None and wbPr.get('date1904') in ('1', 'true'):
        return CALENDAR_MAC_1904
    return CALENDAR_WINDOWS_1900


def read_content_types(archive):
    """Read content types."""
    xml_source = archive.read(ARC_CONTENT_TYPES)
    root = fromstring(xml_source)
    contents_root = root.findall('{%s}Override' % CONTYPES_NS)
    for type in contents_root:
        yield type.get('ContentType'), type.get('PartName')


def read_rels(archive):
    """Read relationships for a workbook"""
    xml_source = archive.read(ARC_WORKBOOK_RELS)
    tree = fromstring(xml_source)
    for element in safe_iterator(tree, '{%s}Relationship' % PKG_REL_NS):
        rId = element.get('Id')
        pth = element.get("Target")
        typ = element.get('Type')
        # normalise path
        if pth.startswith("/xl"):
            pth = pth.replace("/xl", "xl")
        elif not pth.startswith("xl") and not pth.startswith(".."):
            pth = "xl/" + pth
        yield rId, {'path':pth, 'type':typ}


def read_sheets(archive):
    """Read worksheet titles and ids for a workbook"""
    xml_source = archive.read(ARC_WORKBOOK)
    tree = fromstring(xml_source)
    for element in safe_iterator(tree, '{%s}sheet' % SHEET_MAIN_NS):
        attrib = element.attrib
        attrib['id'] = attrib["{%s}id" % REL_NS]
        del attrib["{%s}id" % REL_NS]
        if attrib['id']:
            yield attrib


def detect_worksheets(archive):
    """Return a list of worksheets"""
    # content types has a list of paths but no titles
    # workbook has a list of titles and relIds but no paths
    # workbook_rels has a list of relIds and paths but no titles
    # rels = {'id':{'title':'', 'path':''} }
    content_types = read_content_types(archive)
    valid_sheets = dict((path, ct) for ct, path in content_types if ct == VALID_WORKSHEET)
    rels = dict(read_rels(archive))
    for sheet in read_sheets(archive):
        rel = rels[sheet['id']]
        rel['title'] = sheet['name']
        rel['sheet_id'] = sheet['sheetId']
        rel['state'] = sheet.get('state', 'visible')
        if ("/" + rel['path'] in valid_sheets
            or "worksheets" in rel['path']): # fallback in case content type is missing
            yield rel


def detect_external_links(archive):
    rels = read_rels(archive)
    for rId, d in rels:
        if d['type'] == EXTERNAL_LINK:
            pth = d['path']


def read_workbook_code_name(xml_source):
    tree = fromstring(xml_source)

    pr = tree.find("{%s}workbookPr" % SHEET_MAIN_NS)

    if pr is None:
        pr = {}

    return pr.get('codeName', 'ThisWorkbook')


def read_workbook_settings(xml_source):
    root = fromstring(xml_source)
    view = root.find('*/' '{%s}workbookView' % SHEET_MAIN_NS)
    if view is not None:
        if 'activeTab' in view.attrib:
            return int(view.attrib['activeTab'])
