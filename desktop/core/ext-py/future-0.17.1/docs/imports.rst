.. _imports:

Imports
=======

.. _-__future__-imports:

__future__ imports
------------------

To write a Python 2/3 compatible codebase, the first step is to add this line
to the top of each module::

    from __future__ import absolute_import, division, print_function

For guidelines about whether to import ``unicode_literals`` too, see below
(:ref:`unicode-literals`).

For more information about the ``__future__`` imports, which are a
standard feature of Python, see the following docs:

- absolute_import: `PEP 328: Imports: Multi-Line and Absolute/Relative <http://www.python.org/dev/peps/pep-0328>`_
- division: `PEP 238: Changing the Division Operator <http://www.python.org/dev/peps/pep-0238>`_
- print_function: `PEP 3105: Make print a function <http://www.python.org/dev/peps/pep-3105>`_
- unicode_literals: `PEP 3112: Bytes literals in Python 3000 <http://www.python.org/dev/peps/pep-3112>`_

These are all available in Python 2.7 and up, and enabled by default in Python 3.x.


.. _builtins-imports:

Imports of builtins
-------------------

.. _star-imports:

Implicit imports
~~~~~~~~~~~~~~~~

If you don't mind namespace pollution, the easiest way to provide Py2/3
compatibility for new code using ``future`` is to include the following imports
at the top of every module::

    from builtins import *

On Python 3, this has no effect. (It shadows builtins with globals of the same
names.)

On Python 2, this import line shadows 18 builtins (listed below) to
provide their Python 3 semantics.


.. _explicit-imports:

Explicit imports
~~~~~~~~~~~~~~~~

Explicit forms of the imports are often preferred and are necessary for using
certain automated code-analysis tools.

The complete set of imports of builtins from ``future`` is::

    from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                          int, map, next, oct, open, pow, range, round,
                          str, super, zip)

These are also available under the ``future.builtins`` namespace for backward compatibility.

Importing only some of the builtins is cleaner but increases the risk of
introducing Py2/3 portability bugs as your code evolves over time. For example,
be aware of forgetting to import ``input``, which could expose a security
vulnerability on Python 2 if Python 3's semantics are expected.

.. One further technical distinction is that unlike the ``import *`` form above,
.. these explicit imports do actually modify ``locals()`` on Py3; this is
.. equivalent to typing ``bytes = bytes; int = int`` etc. for each builtin.

The internal API is currently as follows::

    from future.types import bytes, dict, int, range, str
    from future.builtins.misc import (ascii, chr, hex, input, next,
                                      oct, open, pow, round, super)
    from future.builtins.iterators import filter, map, zip

Please note that this internal API is evolving and may not be stable between
different versions of ``future``. To understand the details of the backported
builtins on Python 2, see the docs for these modules.

For more information on what the backported types provide, see :ref:`what-else`.

.. < Section about past.translation is included here >


.. _obsolete-builtins:

Obsolete Python 2 builtins
__________________________

Twelve Python 2 builtins have been removed from Python 3. To aid with
porting code to Python 3 module by module, you can use the following
import to cause a ``NameError`` exception to be raised on Python 2 when any
of the obsolete builtins is used, just as would occur on Python 3::

    from future.builtins.disabled import *

This is equivalent to::

    from future.builtins.disabled import (apply, cmp, coerce, execfile,
                                 file, long, raw_input, reduce, reload,
                                 unicode, xrange, StandardError)

Running ``futurize`` over code that uses these Python 2 builtins does not
import the disabled versions; instead, it replaces them with their
equivalent Python 3 forms and then adds ``future`` imports to resurrect
Python 2 support, as described in :ref:`forwards-conversion-stage2`.


.. include:: standard_library_imports.rst

.. include:: translation.rst

.. include:: unicode_literals.rst

Next steps
----------
See :ref:`what-else`.
