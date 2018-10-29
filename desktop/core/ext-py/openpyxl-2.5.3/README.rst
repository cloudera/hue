openpyxl
========

openpyxl is a Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files.

It was born from lack of existing library to read/write natively from Python
the Office Open XML format.

All kudos to the PHPExcel team as openpyxl was initially based on PHPExcel.


Mailing List
============

Official user list can be found on
http://groups.google.com/group/openpyxl-users


Sample code::

    from openpyxl import Workbook
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Data can be assigned directly to cells
    ws['A1'] = 42

    # Rows can also be appended
    ws.append([1, 2, 3])

    # Python types will automatically be converted
    import datetime
    ws['A2'] = datetime.datetime.now()

    # Save the file
    wb.save("sample.xlsx")


Official documentation
======================

The documentation is at: https://openpyxl.readthedocs.io

* installation methods
* code examples
* instructions for contributing

Release notes: https://openpyxl.readthedocs.io/en/latest/changes.html
