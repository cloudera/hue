from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

"""Write worksheets to xml representations."""

# Python stdlib imports
from io import BytesIO

from openpyxl.compat import safe_string, itervalues, iteritems
from openpyxl import LXML

# package imports
from openpyxl.utils import (
    coordinate_from_string,
    column_index_from_string,
)
from openpyxl.xml.functions import (
    Element,
    SubElement,
    xmlfile,
)
from openpyxl.xml.constants import (
    SHEET_MAIN_NS,
    REL_NS,
)
from openpyxl.formatting import ConditionalFormatting
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.packaging.relationship import Relationship
from openpyxl.worksheet.properties import WorksheetProperties
from openpyxl.worksheet.hyperlink import Hyperlink
from openpyxl.worksheet.related import Related

from .etree_worksheet import write_cell


def write_format(worksheet):
    attrs = {'defaultRowHeight': '15', 'baseColWidth': '10'}
    dimensions_outline = [dim.outline_level
                          for dim in itervalues(worksheet.column_dimensions)]
    if dimensions_outline:
        outline_level = max(dimensions_outline)
        if outline_level:
            attrs['outlineLevelCol'] = str(outline_level)
    return Element('sheetFormatPr', attrs)


def write_cols(worksheet):
    """Write worksheet columns to xml.

    <cols> may never be empty -
    spec says must contain at least one child
    """

    def sorter(value):
        return column_index_from_string(value[0])

    el = Element('cols')
    obj = None

    for idx, col in sorted(worksheet.column_dimensions.items(), key=sorter):
        if dict(col) == {}:
            continue
        idx = column_index_from_string(idx)
        obj = Element('col', dict(col))
        obj.set('min', '%d' % (col.min or idx))
        obj.set('max', '%d' % (col.max or idx))
        el.append(obj)

    if obj is not None:
        return el


def write_autofilter(worksheet):
    auto_filter = worksheet.auto_filter
    if auto_filter.ref is None:
        return

    el = Element('autoFilter', ref=auto_filter.ref)
    if (auto_filter.filter_columns
        or auto_filter.sort_conditions):
        for col_id, filter_column in sorted(auto_filter.filter_columns.items()):
            fc = SubElement(el, 'filterColumn', colId=str(col_id))
            attrs = {}
            if filter_column.blank:
                attrs = {'blank': '1'}
            flt = SubElement(fc, 'filters', attrs)
            for val in filter_column.vals:
                flt.append(Element('filter', val=val))
        if auto_filter.sort_conditions:
            srt = SubElement(el, 'sortState', ref=auto_filter.ref)
            for sort_condition in auto_filter.sort_conditions:
                sort_attr = {'ref': sort_condition.ref}
                if sort_condition.descending:
                    sort_attr['descending'] = '1'
                srt.append(Element('sortCondtion', sort_attr))
    return el


def write_mergecells(worksheet):
    """Write merged cells to xml."""
    cells = worksheet._merged_cells
    if not cells:
        return

    merge = Element('mergeCells', count='%d' % len(cells))
    for range_string in cells:
        merge.append(Element('mergeCell', ref=range_string))
    return merge


def write_conditional_formatting(worksheet):
    """Write conditional formatting to xml."""
    wb = worksheet.parent
    for range_string, rules in iteritems(worksheet.conditional_formatting.cf_rules):
        cf = Element('conditionalFormatting', {'sqref': range_string})

        for rule in rules:
            if rule.dxf is not None:
                if rule.dxf != DifferentialStyle():
                    rule.dxfId = len(wb._differential_styles)
                    wb._differential_styles.append(rule.dxf)
            cf.append(rule.to_tree())

        yield cf


def write_datavalidation(worksheet):
    """ Write data validation(s) to xml."""
    # Filter out "empty" data-validation objects (i.e. with 0 cells)
    required_dvs = [x for x in worksheet._data_validations
                    if len(x.cells) or len(x.ranges)]
    if not required_dvs:
        return

    dvs = Element("dataValidations", count=str(len(required_dvs)))
    for dv in required_dvs:
        dvs.append(dv.to_tree())

    return dvs


def write_header_footer(worksheet):
    header = worksheet.header_footer.getHeader()
    footer = worksheet.header_footer.getFooter()
    if header or footer:
        tag = Element('headerFooter')
        if header:
            SubElement(tag, 'oddHeader').text = header
        if footer:
            SubElement(tag, 'oddFooter').text = footer
        return tag


def write_hyperlinks(worksheet):
    """Write worksheet hyperlinks to xml."""
    if not worksheet.hyperlinks:
        return
    tag = Element('hyperlinks')
    for cell in worksheet.hyperlinks:
        link = cell.hyperlink
        link.ref = cell.coordinate
        rel = Relationship(type="hyperlink", targetMode="External", target=link.target)
        worksheet._rels.append(rel)
        link.id = "rId{0}".format(len(worksheet._rels))

        tag.append(link.to_tree())
    return tag


def write_drawing(worksheet):
    """
    Add link to drawing if required
    """
    if worksheet._charts or worksheet._images:
        rel = Relationship(type="drawing", target="")
        worksheet._rels.append(rel)
        drawing = Related()
        drawing.id = "rId%s" % len(worksheet._rels)
        return drawing.to_tree("drawing")


def write_worksheet(worksheet, shared_strings):
    """Write a worksheet to an xml file."""
    worksheet._rels = []
    if LXML is True:
        from .lxml_worksheet import write_cell, write_rows
    else:
        from .etree_worksheet import write_cell, write_rows

    out = BytesIO()

    with xmlfile(out) as xf:
        with xf.element('worksheet', xmlns=SHEET_MAIN_NS):

            props = worksheet.sheet_properties.to_tree()
            xf.write(props)

            dim = Element('dimension', {'ref': '%s' % worksheet.calculate_dimension()})
            xf.write(dim)

            views = Element('sheetViews')
            views.append(worksheet.sheet_view.to_tree())
            xf.write(views)

            xf.write(write_format(worksheet))
            cols = write_cols(worksheet)
            if cols is not None:
                xf.write(cols)
            write_rows(xf, worksheet)

            if worksheet.protection.sheet:
                xf.write(worksheet.protection.to_tree())

            af = write_autofilter(worksheet)
            if af is not None:
                xf.write(af)

            merge = write_mergecells(worksheet)
            if merge is not None:
                xf.write(merge)

            cfs = write_conditional_formatting(worksheet)
            for cf in cfs:
                xf.write(cf)

            dv = write_datavalidation(worksheet)
            if dv is not None:
                xf.write(dv)

            hyper = write_hyperlinks(worksheet)
            if hyper is not None:
                xf.write(hyper)

            options = worksheet.print_options
            if dict(options):
                new_element = options.to_tree()
                xf.write(new_element)

            margins = worksheet.page_margins.to_tree()
            xf.write(margins)

            setup = worksheet.page_setup
            if dict(setup):
                new_element = setup.to_tree()
                xf.write(new_element)

            hf = write_header_footer(worksheet)
            if hf is not None:
                xf.write(hf)

            drawing = write_drawing(worksheet)
            if drawing is not None:
                xf.write(drawing)

            # If vba is being preserved then add a legacyDrawing element so
            # that any controls can be drawn.
            if worksheet.vba_controls is not None:
                legacyDrawing = Related(id=worksheet.vba_controls)
                xml = legacyDrawing.to_tree("legacyDrawing")
                xf.write(xml)

            elif worksheet._comment_count > 0:
                # add a legacyDrawing so that excel can draw comments
                # If a legacyDrawing element has already been added then
                # we have to hope it already contains the vml for
                # comments because we cannot add another.
                legacyDrawing = Related(id="commentsvml")
                xml = legacyDrawing.to_tree("legacyDrawing")
                xf.write(xml)

            if len(worksheet.page_breaks):
                xf.write(worksheet.page_breaks.to_tree())


    xml = out.getvalue()
    out.close()
    return xml
