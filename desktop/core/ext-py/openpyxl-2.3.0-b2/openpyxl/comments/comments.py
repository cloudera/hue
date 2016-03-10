from __future__ import absolute_import
# Copyright (c) 2010-2015 openpyxl


class Comment(object):
    __slots__ = ('_parent',
                 '_text',
                 '_author',
                 '_width',
                 '_height')

    def __init__(self, text, author):
        self._text = text
        self._author = author
        self._parent = None
        self._width = '108pt'
        self._height = '59.25pt'

    @property
    def author(self):
        """ The name recorded for the author

            :rtype: string
        """
        return self._author
    @author.setter
    def author(self, value):
        self._author = value

    @property
    def text(self):
        """ The text of the commment

            :rtype: string
        """
        return self._text
    @text.setter
    def text(self, value):
        self._text = value

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, cell):
        if cell is not None and self._parent is not None and self._parent != cell:
            raise AttributeError("Comment already assigned to %s in worksheet %s. Cannot assign a comment to more than one cell" % (cell.coordinate, cell.parent.title))
        self._parent = cell
