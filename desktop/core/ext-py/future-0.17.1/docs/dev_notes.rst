Notes
-----
This module only supports Python 2.7, and Python 3.4+.

The following renames are already supported on Python 2.7 without any
additional work from us::

    reload() -> imp.reload()
    reduce() -> functools.reduce()
    StringIO.StringIO -> io.StringIO
    Bytes.BytesIO -> io.BytesIO

Old things that can one day be fixed automatically by futurize.py::

  string.uppercase -> string.ascii_uppercase   # works on either Py2.7 or Py3+
  sys.maxint -> sys.maxsize      # but this isn't identical
