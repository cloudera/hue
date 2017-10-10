.. _automatic-conversion:

Automatic conversion to Py2/3
=============================

The ``future`` source tree includes scripts called ``futurize`` and
``pasteurize`` to aid in making Python 2 code or Python 3 code compatible with
both platforms (Py2/3) using the :mod:`future` module. These are based on
``lib2to3`` and use fixers from ``2to3``, ``3to2``, and ``python-modernize``.

``futurize`` passes Python 2 code through all the appropriate fixers to turn it
into valid Python 3 code, and then adds ``__future__`` and ``future`` package
imports.

For conversions from Python 3 code to Py2/3, use the ``pasteurize`` script
instead. This converts Py3-only constructs (e.g. new metaclass syntax) and adds
``__future__`` and ``future`` imports to the top of each module.

In both cases, the result should be relatively clean Py3-style code that runs
mostly unchanged on both Python 2 and Python 3.


.. include:: futurize.rst

.. include:: futurize_cheatsheet.rst

.. include:: pasteurize.rst

.. include:: conversion_limitations.rst

