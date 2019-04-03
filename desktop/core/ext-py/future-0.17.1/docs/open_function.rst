.. _open-function:

open()
------

The Python 3 builtin :func:`open` function for opening files returns file
contents as (unicode) strings unless the binary (``b``) flag is passed, as in::

    open(filename, 'rb')

in which case its methods like :func:`read` return Py3 :class:`bytes` objects.

On Py2 with ``future`` installed, the :mod:`builtins` module provides an
``open`` function that is mostly compatible with that on Python 3 (e.g. it
offers keyword arguments like ``encoding``). This maps to the ``open`` backport
available in the standard library :mod:`io` module on Py2.7.

One difference to be aware of between the Python 3 ``open`` and
``future.builtins.open`` on Python 2 is that the return types of methods such
as :func:`read()` from the file object that ``open`` returns are not
automatically cast from native bytes or unicode strings on Python 2 to the
corresponding ``future.builtins.bytes`` or ``future.builtins.str`` types. If you
need the returned data to behave the exactly same way on Py2 as on Py3, you can
cast it explicitly as follows::

    from __future__ import unicode_literals
    from builtins import open, bytes

    data = open('image.png', 'rb').read()
    # On Py2, data is a standard 8-bit str with loose Unicode coercion.
    # data + u'' would likely raise a UnicodeDecodeError

    data = bytes(data)
    # Now it behaves like a Py3 bytes object...

    assert data[:4] == b'\x89PNG'
    assert data[4] == 13     # integer
    # Raises TypeError:
    # data + u''
