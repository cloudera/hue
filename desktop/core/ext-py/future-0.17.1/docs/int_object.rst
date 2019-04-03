.. _int-object:

int
---

Python 3's ``int`` type is very similar to Python 2's ``long``, except
for the representation (which omits the ``L`` suffix in Python 2). Python
2's usual (short) integers have been removed from Python 3, as has the
``long`` builtin name.

Python 3::

    >>> 2**64
    18446744073709551616

Python 2::

    >>> 2**64
    18446744073709551616L

``future`` includes a backport of Python 3's ``int`` that
is a subclass of Python 2's ``long`` with the same representation
behaviour as Python 3's ``int``. To ensure an integer is long compatibly with
both Py3 and Py2, cast it like this::

    >>> from builtins import int
    >>> must_be_a_long_integer = int(1234)

The backported ``int`` object helps with writing doctests and simplifies code
that deals with ``long`` and ``int`` as special cases on Py2. An example is the
following code from ``xlwt-future`` (called by the ``xlwt.antlr.BitSet`` class)
for writing out Excel ``.xls`` spreadsheets. With ``future``, the code is::

    from builtins import int

    def longify(data):
        """
        Turns data (an int or long, or a list of ints or longs) into a
        list of longs.
        """
        if not data:
            return [int(0)]
        if not isinstance(data, list):
            return [int(data)]
        return list(map(int, data))


Without ``future`` (or with ``future`` < 0.7), this might be::

    def longify(data):
        """
        Turns data (an int or long, or a list of ints or longs) into a
        list of longs.
        """
        if not data:
            if PY3:
                return [0]
            else:
                return [long(0)]
        if not isinstance(data,list):
            if PY3:
                return [int(data)]
            else:
                return [long(data)]
        if PY3:
            return list(map(int, data))   # same as returning data, but with up-front typechecking
        else:
            return list(map(long, data))
