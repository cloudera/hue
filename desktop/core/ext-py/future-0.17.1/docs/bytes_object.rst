.. _bytes-object:

bytes
-----

Handling ``bytes`` consistently and correctly has traditionally been one
of the most difficult tasks in writing a Py2/3 compatible codebase. This
is because the Python 2 :class:`bytes` object is simply an alias for
Python 2's :class:`str`, rather than a true implementation of the Python
3 :class:`bytes` object, which is substantially different.

:mod:`future` contains a backport of the :mod:`bytes` object from Python 3
which passes most of the Python 3 tests for :mod:`bytes`. (See
``tests/test_future/test_bytes.py`` in the source tree.) You can use it as
follows::

    >>> from builtins import bytes
    >>> b = bytes(b'ABCD')

On Py3, this is simply the builtin :class:`bytes` object. On Py2, this
object is a subclass of Python 2's :class:`str` that enforces the same
strict separation of unicode strings and byte strings as Python 3's
:class:`bytes` object::

    >>> b + u'EFGH'      # TypeError
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: argument can't be unicode string

    >>> bytes(b',').join([u'Fred', u'Bill'])
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: sequence item 0: expected bytes, found unicode string

    >>> b == u'ABCD'
    False

    >>> b < u'abc'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unorderable types: bytes() and <type 'unicode'>


In most other ways, these :class:`bytes` objects have identical
behaviours to Python 3's :class:`bytes`::

    b = bytes(b'ABCD')
    assert list(b) == [65, 66, 67, 68]
    assert repr(b) == "b'ABCD'"
    assert b.split(b'B') == [b'A', b'CD']

Currently the easiest way to ensure identical behaviour of byte-strings
in a Py2/3 codebase is to wrap all byte-string literals ``b'...'`` in a
:func:`~bytes` call as follows::

    from builtins import bytes

    # ...

    b = bytes(b'This is my bytestring')

    # ...

This is not perfect, but it is superior to manually debugging and fixing
code incompatibilities caused by the many differences between Py3 bytes
and Py2 strings.


The :class:`bytes` type from :mod:`builtins` also provides support for the
``surrogateescape`` error handler on Python 2.x. Here is an example that works
identically on Python 2.x and 3.x::

    >>> from builtins import bytes
    >>> b = bytes(b'\xff')
    >>> b.decode('utf-8', 'surrogateescape')
    '\udcc3'

This feature is in alpha. Please leave feedback `here
<https://github.com/PythonCharmers/python-future/issues>`_ about whether this
works for you.
