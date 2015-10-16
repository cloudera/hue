from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl

from openpyxl.cell import column_index_from_string
from openpyxl.xml.constants import PACKAGE_IMAGES

from .drawing import Drawing


def bounding_box(bw, bh, w, h):
    """
    Returns a tuple (new_width, new_height) which has the property
    that it fits within box_width and box_height and has (close to)
    the same aspect ratio as the original size
    """
    new_width, new_height = w, h
    if bw and new_width > bw:
        new_width = bw
        new_height = new_width / (float(w) / h)
    if bh and new_height > bh:
        new_height = bh
        new_width = new_height * (float(w) / h)
    return (new_width, new_height)


def _import_image(img):
    try:
        try:
            import Image as PILImage
        except ImportError:
            from PIL import Image as PILImage
    except ImportError:
        raise ImportError('You must install PIL to fetch image objects')

    if not isinstance(img, PILImage.Image):
        img = PILImage.open(img)

    return img


class Image(object):
    """ Raw Image class """

    _id = 1

    def __init__(self, img, coordinates=((0, 0), (1, 1)), size=(None, None),
                 nochangeaspect=True, nochangearrowheads=True):

        self.image = _import_image(img)
        self.nochangeaspect = nochangeaspect
        self.nochangearrowheads = nochangearrowheads

        # the containing drawing
        self.drawing = Drawing()
        self.drawing.coordinates = coordinates

        newsize = bounding_box(size[0], size[1],
                               self.image.size[0], self.image.size[1])
        size = newsize
        self.drawing.width = size[0]
        self.drawing.height = size[1]

    def anchor(self, cell, anchortype="absolute"):
        """ anchors the image to the given cell
            optional parameter anchortype supports 'absolute' or 'oneCell'"""
        self.drawing.anchortype = anchortype
        if anchortype == "absolute":
            self.drawing.left, self.drawing.top = cell.anchor
            return ((cell.column, cell.row),
                    cell.parent.point_pos(self.drawing.top + self.drawing.height,
                                          self.drawing.left + self.drawing.width))
        elif anchortype == "oneCell":
            self.drawing.anchorcol = column_index_from_string(cell.column) - 1
            self.drawing.anchorrow = cell.row - 1
            return ((self.drawing.anchorcol, self.drawing.anchorrow), None)
        else:
            raise ValueError("unknown anchortype %s" % anchortype)


    @property
    def _path(self):
        return PACKAGE_IMAGES + '/image{0}.png'.format(self._id)
