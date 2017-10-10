.. _str-object:

str
-----

The :class:`str` object in Python 3 is quite similar but not identical to the
Python 2 :class:`unicode` object.

The major difference is the stricter type-checking of Py3's ``str`` that
enforces a distinction between unicode strings and byte-strings, such as when
comparing, concatenating, joining, or replacing parts of strings.

There are also other differences, such as the ``repr`` of unicode strings in
Py2 having a ``u'...'`` prefix, versus simply ``'...'``, and the removal of
the :func:`str.decode` method in Py3.

:mod:`future` contains a :class:`newstr`` type that is a backport of the
:mod:`str` object from Python 3. This inherits from the Python 2
:class:`unicode` class but has customizations to improve compatibility with
Python 3's :class:`str` object. You can use it as follows::

    >>> from __future__ import unicode_literals
    >>> from builtins import str

On Py2, this gives us::

    >>> str
    future.types.newstr.newstr

(On Py3, it is simply the usual builtin :class:`str` object.)

Then, for example, the following code has the same effect on Py2 as on Py3::

    >>> s = str(u'ABCD')
    >>> assert s != b'ABCD'
    >>> assert isinstance(s.encode('utf-8'), bytes)
    >>> assert isinstance(b.decode('utf-8'), str)

    These raise TypeErrors:

    >>> bytes(b'B') in s
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: 'in <string>' requires string as left operand, not <type 'str'>

    >>> s.find(bytes(b'A'))
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: argument can't be <type 'str'>

Various other operations that mix strings and bytes or other types are
permitted on Py2 with the :class:`newstr` class even though they
are illegal with Python 3. For example::

    >>> s2 = b'/' + str('ABCD')
    >>> s2
    '/ABCD'
    >>> type(s2)
    future.types.newstr.newstr

This is allowed for compatibility with parts of the Python 2 standard
library and various third-party libraries that mix byte-strings and unicode
strings loosely. One example is ``os.path.join`` on Python 2, which
attempts to add the byte-string ``b'/'`` to its arguments, whether or not
they are unicode. (See ``posixpath.py``.) Another example is the
:func:`escape` function in Django 1.4's :mod:`django.utils.html`.


.. For example, this is permissible on Py2::
.. 
..     >>> u'u' > 10
..     True
.. 
..     >>> u'u' <= b'u'
..     True
.. 
.. On Py3, these raise TypeErrors.

In most other ways, these :class:`builtins.str` objects on Py2 have the
same behaviours as Python 3's :class:`str`::

    >>> s = str('ABCD')
    >>> assert repr(s) == 'ABCD'      # consistent repr with Py3 (no u prefix)
    >>> assert list(s) == ['A', 'B', 'C', 'D']
    >>> assert s.split('B') == ['A', 'CD']


The :class:`str` type from :mod:`builtins` also provides support for the
``surrogateescape`` error handler on Python 2.x. Here is an example that works
identically on Python 2.x and 3.x::

    >>> from builtins import str
    >>> s = str(u'\udcff')
    >>> s.encode('utf-8', 'surrogateescape')
    b'\xff'

This feature is in alpha. Please leave feedback `here
<https://github.com/PythonCharmers/python-future/issues>`_ about whether this
works for you.

