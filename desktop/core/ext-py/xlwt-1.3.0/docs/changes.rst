Changes
=======

.. currentmodule:: xlwt

1.3.0 (22 August 2017)
----------------------

- Officially support Python 3.6, drop support for 2.6.

- Fix bytes/string type mismatch in :func:`upack2rt` on python 3.

- Packaging and code style tweaks.

- Use generator expressions to avoid unnecessary lists in memory.

Thanks to the following for their contributions to this release:

- Jon Dufresne
- Bill Adams

1.2.0 (4 January 2017)
----------------------

- Remove ``LOCALE`` from regular expression that caused
  :class:`DeprecationWarning` that become an exception in Python 3.6

- Add :meth:`Workbook.sheet_index` helper.

- :meth:`Workbook.get_sheet` now takes either a string name or an integer
  index.

1.1.2 (9 June 2016)
-------------------

- Fix failure in style compression under Python 3.

- Officially support Python 3.5

- Documentation tweaks.

1.1.1 (2 June 2016)
-------------------

- Fix release problems.

1.1.0 (2 June 2016)
-------------------

- Fix SST BIFF record in Python 3.

- Fix for writing :class:`ExternSheetRecord` in Python 3.

- Add the ability to insert bitmap images from buffers as well as files.

- Official support for Python 3.5.

Thanks to "thektulu" and Lele Gaifax for the Python 3 fixes.
Thanks to Ross Golder for the support for inserting images from buffers.

1.0.0 (15 April 2015)
---------------------

- Python 3 support.

- Initial set of unit tests.

- An initial set of Sphinx documentation.

- Move to setuptools for packaging.

- Wire up Travis, Coveralls and ReadTheDocs.

- Allow longs as row indexes.

Big thanks to Thomas Kluyver for his work on Python 3 support, Manfred Moitzi
for donating his unit tests.

Belated thanks to Landon Jurgens for his help on converting the documentation
to Sphinx.

0.7.5 (5 April 2013)
--------------------

- Fixes a bug that could cause a corrupt SST in .xls files written by a
  wide-unicode Python build.

- A :class:`ValueError` is now raised immediately if an attempt is made to set
  column width to other than an int in ``range(65536)``

- Added the ability to set a custom RGB colour in the palette to use for
  colours. Thanks to Alan Rotman for the work, although this could really
  use an example in the examples folder...

- Fixed an issue trying to set a diagonal border using easyxf. Thanks to
  Neil Etheridge for the fix.

- Fixed a regression from 0.7.2 when writing sheets with frozen panes.

0.7.4 (13 April 2012)
---------------------

- Python 2.3 to 2.7 are now the officially supported versions, no Python
  3 yet, sorry.

- The ``datemode`` in an xlwt :class:`Workbook` can be set to 1904 by doing
  ``workbook.dates_1904 = 1`` and is written to the output file. However the
  datemode was not being reflected in conversions from
  :class:`datetime.datetime` and :class:`datetime.date` objects to floats for
  output, resulting in dates that were 4 years too high when seen in Excel.

0.7.3 (21 February 2012)
------------------------

- Added user_set and best_fit attributes to Column class.

- Fixed an ``[Errno 0] Error`` raised when :meth:`Worksheet.flush_row_data` was
  called after :meth:`Workbook.save`

- Fixed an error on Windows that occurred when writing large blocks to
  files.

- Added the ability to write rich text cells

- Fixed a bug when writing ``MULBLANK`` records on big-endian platforms.

- allow the ``active_pane`` on worksheets to be specified

- added support for zoom (magn) factors and improved possibilities when
  generating split panes

0.7.2 (1 June 2009)
-------------------

- Added function Utils.rowcol_pair_to_cellrange.
  ``(0, 0, 65535, 255) -> "A1:IV65536"``

- Removed :class:`Worksheet` property ``show_empty_as_zero``,
  and added attribute :attr:`~Worksheet.show_zero_values`
  (default: ``1 == True``).

- Fixed formula code generation problem with formulas
  including MAX/SUM/etc functions with arguments like A1+123.

- Added .pattern_examples.xls and put a pointer to it
  in the easyxf part of Style.py.

- Fixed Row.set_cell_formula() bug introduced in 0.7.1.

- Fixed bug(?) with SCL/magnification handling causing(?) Excel
  to raise a dialogue box if sheet is set to open in page preview mode
  and user then switches to normal view.

- Added color and colour as synonyms for font.colour_index in easyxf.

- Removed unused attribute Row.__has_default_format.

0.7.1 (4 March 2009)
--------------------

See source control for changes made.

0.7.0 (19 September 2008)
-------------------------

- Fixed more bugs and added more various new bits of functionality

0.7.0a4 (8 October 2007)
------------------------

- fork of pyExcelerator, released to python-excel.

- Fixed various bugs in pyExcelerator and added various new bits of functionality
