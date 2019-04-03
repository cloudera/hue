.. _dict-object:

dict
----

Python 3 dictionaries have ``.keys()``, ``.values()``, and ``.items()``
methods which return memory-efficient set-like iterator objects, not lists.
(See `PEP 3106 <http://www.python.org/dev/peps/pep-3106/>`_.)

If your dictionaries are small, performance is not critical, and you don't need
the set-like behaviour of iterator objects from Python 3, you can of course
stick with standard Python 3 code in your Py2/3 compatible codebase::

    # Assuming d is a native dict ...

    for key in d:
        # code here

    for item in d.items():
        # code here

    for value in d.values():
        # code here

In this case there will be memory overhead of list creation on Py2 for each
call to ``items``, ``values`` or ``keys``.

For improved efficiency, ``future.builtins`` (aliased to ``builtins``) provides
a Python 2 ``dict`` subclass whose :func:`keys`, :func:`values`, and
:func:`items` methods return iterators on all versions of Python >= 2.7. On
Python 2.7, these iterators also have the same set-like view behaviour as
dictionaries in Python 3. This can streamline code that iterates over large
dictionaries. For example::

    from __future__ import print_function
    from builtins import dict, range

    # Memory-efficient construction:
    d = dict((i, i**2) for i in range(10**7))

    assert not isinstance(d.items(), list)

    # Because items() is memory-efficient, so is this:
    d2 = dict((v, k) for (k, v) in d.items())

As usual, on Python 3 ``dict`` imported from either ``builtins`` or
``future.builtins`` is just the built-in ``dict`` class.


Memory-efficiency and alternatives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you already have large native dictionaries, the downside to wrapping them in
a ``dict`` call is that memory is copied (on both Py3 and on Py2). For
example::

    # This allocates and then frees a large amount of temporary memory:
    d = dict({i: i**2 for i in range(10**7)})

If dictionary methods like ``values`` and ``items`` are called only once, this
obviously negates the memory benefits offered by the overridden methods through
not creating temporary lists.

The memory-efficient (and CPU-efficient) alternatives are:

- to construct a dictionary from an iterator. The above line could use a
  generator like this::

      d = dict((i, i**2) for i in range(10**7))

- to construct an empty dictionary with a ``dict()`` call using
  ``builtins.dict`` (rather than ``{}``) and then update it;

- to use the ``viewitems`` etc. functions from :mod:`future.utils`, passing in
  regular dictionaries::

    from future.utils import viewkeys, viewvalues, viewitems

    for (key, value) in viewitems(hugedictionary):
        # some code here

    # Set intersection:
    d = {i**2: i for i in range(1000)}
    both = viewkeys(d) & set(range(0, 1000, 7))

    # Set union:
    both = viewvalues(d1) | viewvalues(d2)

For compatibility, the functions ``iteritems`` etc. are also available in
:mod:`future.utils`. These are equivalent to the functions of the same names in
``six``, which is equivalent to calling the ``iteritems`` etc. methods on
Python 2, or to calling ``items`` etc. on Python 3.
