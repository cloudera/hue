from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

import datetime

from openpyxl.compat import safe_string, unicode
from openpyxl.utils.datetime  import CALENDAR_WINDOWS_1900, datetime_to_W3CDTF, W3CDTF_to_datetime
from openpyxl.descriptors import Strict, String, Typed, Alias
from openpyxl.xml.functions import ElementTree, Element, SubElement, tostring, fromstring, safe_iterator, localname
from openpyxl.xml.constants import COREPROPS_NS, DCORE_NS, XSI_NS, DCTERMS_NS, DCTERMS_PREFIX



class W3CDateTime(Typed):

    expected_type = datetime.datetime

    def __set__(self, instance, value):
        if value is not None and isinstance(value, str):
            try:
                value = W3CDTF_to_datetime(value)
            except ValueError:
                raise ValueError("Value must be W3C datetime format")
        super(W3CDateTime, self).__set__(instance, value)


class DocumentProperties(Strict):
    """High-level properties of the document.
    Defined in ECMA-376 Par2 Annex D
    """

    category = String(allow_none=True)
    contentStatus = String(allow_none=True)
    keywords = String(allow_none=True)
    lastModifiedBy = String(allow_none=True)
    lastPrinted = W3CDateTime(expected_type=datetime.datetime, allow_none=True)
    revision = String(allow_none=True)
    version = String(allow_none=True)
    last_modified_by = Alias("lastModifiedBy")

    # Dublin Core Properties
    subject = String(allow_none=True)
    title = String(allow_none=True)
    creator = String(allow_none=True)
    description = String(allow_none=True)
    identifier = String(allow_none=True)
    language = String(allow_none=True)
    created = W3CDateTime(expected_type=datetime.datetime, allow_none=True)
    modified = W3CDateTime(expected_type=datetime.datetime, allow_none=True)

    __fields__ = ("category", "contentStatus", "lastModifiedBy", "keywords",
                "lastPrinted", "revision", "version", "created", "creator", "description",
                "identifier", "language", "modified", "subject", "title")

    def __init__(self,
                 category=None,
                 contentStatus=None,
                 keywords=None,
                 lastModifiedBy=None,
                 lastPrinted=None,
                 revision=None,
                 version=None,
                 created=datetime.datetime.now(),
                 creator="openpyxl",
                 description=None,
                 identifier=None,
                 language=None,
                 modified=datetime.datetime.now(),
                 subject=None,
                 title=None,
                 ):
        self.contentStatus = contentStatus
        self.lastPrinted = lastPrinted
        self.revision = revision
        self.version = version
        self.creator = creator
        self.lastModifiedBy = lastModifiedBy
        self.modified = modified
        self.created = created
        self.title = title
        self.subject = subject
        self.description = description
        self.identifier = identifier
        self.language = language
        self.keywords = keywords
        self.category = category

    def __iter__(self):
        for attr in self.__fields__:
            value = getattr(self, attr)
            if value is not None:
                yield attr, safe_string(value)


def write_properties(props):
    """Write the core properties to xml."""
    root = Element('{%s}coreProperties' % COREPROPS_NS)
    for attr in ("creator", "title", "description", "subject", "identifier",
                 "language"):
        SubElement(root, '{%s}%s' % (DCORE_NS, attr)).text = getattr(props, attr)

    for attr in ("created", "modified"):
        value = datetime_to_W3CDTF(getattr(props, attr))
        SubElement(root, '{%s}%s' % (DCTERMS_NS, attr),
                   {'{%s}type' % XSI_NS:'%s:W3CDTF' % DCTERMS_PREFIX}).text = value

    for attr in ("lastModifiedBy", "category", "contentStatus", "version",
                 "revision", "keywords"):
        SubElement(root, '{%s}%s' % (COREPROPS_NS, attr)).text = getattr(props, attr)

    if props.lastPrinted is not None:
        SubElement(root, "{%s}lastPrinted" % COREPROPS_NS).text = datetime_to_W3CDTF(props.lastPrinted
                                                                            )
    return tostring(root)


def read_properties(xml_source):
    properties = DocumentProperties()
    root = fromstring(xml_source)

    for node in safe_iterator(root):
        tag = localname(node)
        setattr(properties, tag, node.text)

    return properties


class DocumentSecurity(object):
    """Security information about the document."""

    def __init__(self):
        self.lock_revision = False
        self.lock_structure = False
        self.lock_windows = False
        self.revision_password = ''
        self.workbook_password = ''
