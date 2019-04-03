.. _isinstance-calls:

isinstance
----------

The following tests all pass on Python 3::

    >>> assert isinstance(2**62, int)
    >>> assert isinstance(2**63, int)
    >>> assert isinstance(b'my byte-string', bytes)
    >>> assert isinstance(u'unicode string 1', str)
    >>> assert isinstance('unicode string 2', str)


However, two of these normally fail on Python 2::

    >>> assert isinstance(2**63, int)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AssertionError

    >>> assert isinstance(u'my unicode string', str)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AssertionError

And if this import is in effect on Python 2::

    >>> from __future__ import unicode_literals

then the fifth test fails too::

    >>> assert isinstance('unicode string 2', str)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AssertionError


After importing the builtins from ``future``, all these tests pass on
Python 2 as on Python 3::

    >>> from builtins import bytes, int, str

    >>> assert isinstance(10, int)
    >>> assert isinstance(10**100, int)
    >>> assert isinstance(b'my byte-string', bytes)
    >>> assert isinstance(u'unicode string 1', str)

However, note that the last test requires that ``unicode_literals`` be imported to succeed.::

    >>> from __future__ import unicode_literals
    >>> assert isinstance('unicode string 2', str)

This works because the backported types ``int``, ``bytes`` and ``str``
(and others) have metaclasses that override ``__instancecheck__``. See `PEP 3119
<http://www.python.org/dev/peps/pep-3119/#overloading-isinstance-and-issubclass>`_
for details.


Passing data to/from Python 2 libraries
---------------------------------------

If you are passing any of the backported types (``bytes``, ``int``, ``dict,
``str``) into brittle library code that performs type-checks using ``type()``,
rather than ``isinstance()``, or requires that you pass Python 2's native types
(rather than subclasses) for some other reason, it may be necessary to upcast
the types from ``future`` to their native superclasses on Py2.

The ``native`` function in ``future.utils`` is provided for this. Here is how
to use it. (The output showing is from Py2)::

    >>> from builtins import int, bytes, str
    >>> from future.utils import native

    >>> a = int(10**20)     # Py3-like long int
    >>> a
    100000000000000000000
    >>> type(a)
    future.types.newint.newint
    >>> native(a)
    100000000000000000000L
    >>> type(native(a))
    long

    >>> b = bytes(b'ABC')
    >>> type(b)
    future.types.newbytes.newbytes
    >>> native(b)
    'ABC'
    >>> type(native(b))
    str

    >>> s = str(u'ABC')
    >>> type(s)
    future.types.newstr.newstr
    >>> native(s)
    u'ABC'
    >>> type(native(s))
    unicode

On Py3, the :func:`native` function is a no-op.


Native string type
------------------

Some library code, include standard library code like the ``array.array()``
constructor, require native strings on Python 2 and Python 3. This means that
there is no simple way to pass the appropriate string type when the
``unicode_literals`` import from ``__future__`` is in effect.

The objects ``native_str`` and ``native_bytes`` are available in
``future.utils`` for this case. These are equivalent to the ``str`` and
``bytes`` objects in ``__builtin__`` on Python 2 or in ``builtins`` on Python 3.

The functions ``native_str_to_bytes`` and ``bytes_to_native_str`` are also
available for more explicit conversions.
