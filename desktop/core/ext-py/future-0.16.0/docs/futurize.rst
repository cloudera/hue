.. _forwards-conversion:

``futurize``: Py2 to Py2/3
--------------------------

.. include:: futurize_overview.rst


.. _forwards-conversion-stage1:

Stage 1: "safe" fixes
~~~~~~~~~~~~~~~~~~~~~

Run the first stage of the conversion process with::

	futurize --stage1 mypackage/*.py

or, if you are using zsh, recursively::

    futurize --stage1 mypackage/**/*.py

This applies fixes that modernize Python 2 code without changing the effect of
the code. With luck, this will not introduce any bugs into the code, or will at
least be trivial to fix. The changes are those that bring the Python code
up-to-date without breaking Py2 compatibility. The resulting code will be
modern Python 2.6-compatible code plus ``__future__`` imports from the
following set:

.. code-block:: python

    from __future__ import absolute_import
    from __future__ import division
    from __future__ import print_function

Only those ``__future__`` imports deemed necessary will be added unless
the ``--all-imports`` command-line option is passed to ``futurize``, in
which case they are all added.

The ``from __future__ import unicode_literals`` declaration is not added
unless the ``--unicode-literals`` flag is passed to ``futurize``.

The changes include::

    - except MyException, e:
    + except MyException as e:

    - print >>stderr, "Blah"
    + from __future__ import print_function
    + print("Blah", stderr)

    - class MyClass:
    + class MyClass(object):

    - def next(self):
    + def __next__(self):

    - if d.has_key(key):
    + if key in d:

Implicit relative imports fixed, e.g.::

    - import mymodule
    + from __future__ import absolute_import
    + from . import mymodule

.. and all unprefixed string literals '...' gain a b prefix to be b'...'.

.. (This last step can be prevented using --no-bytes-literals if you already have b'...' markup in your code, whose meaning would otherwise be lost.)

Stage 1 does not add any imports from the ``future`` package. The output of
stage 1 will probably not (yet) run on Python 3.

The goal for this stage is to create most of the ``diff`` for the entire
porting process, but without introducing any bugs. It should be uncontroversial
and safe to apply to every Python 2 package. The subsequent patches introducing
Python 3 compatibility should then be shorter and easier to review.

The complete set of fixers applied by ``futurize --stage1`` is:

.. code-block:: python

    lib2to3.fixes.fix_apply
    lib2to3.fixes.fix_except
    lib2to3.fixes.fix_exitfunc
    lib2to3.fixes.fix_funcattrs
    lib2to3.fixes.fix_has_key
    lib2to3.fixes.fix_idioms
    lib2to3.fixes.fix_intern
    lib2to3.fixes.fix_isinstance
    lib2to3.fixes.fix_methodattrs
    lib2to3.fixes.fix_ne
    lib2to3.fixes.fix_numliterals
    lib2to3.fixes.fix_paren
    lib2to3.fixes.fix_reduce
    lib2to3.fixes.fix_renames
    lib2to3.fixes.fix_repr
    lib2to3.fixes.fix_standarderror
    lib2to3.fixes.fix_sys_exc
    lib2to3.fixes.fix_throw
    lib2to3.fixes.fix_tuple_params
    lib2to3.fixes.fix_types
    lib2to3.fixes.fix_ws_comma
    lib2to3.fixes.fix_xreadlines
    libfuturize.fixes.fix_absolute_import
    libfuturize.fixes.fix_next_call
    libfuturize.fixes.fix_print_with_import
    libfuturize.fixes.fix_raise


The following fixers from ``lib2to3`` are not applied:

.. code-block:: python

    lib2to3.fixes.fix_import

The ``fix_absolute_import`` fixer in ``libfuturize.fixes`` is applied instead of
``lib2to3.fixes.fix_import``. The new fixer both makes implicit relative
imports explicit and adds the declaration ``from __future__ import
absolute_import`` at the top of each relevant module.

.. code-block:: python

    lib2to3.fixes.fix_next

The ``fix_next_call`` fixer in ``libfuturize.fixes`` is applied instead of
``fix_next`` in stage 1. The new fixer changes any ``obj.next()`` calls to
``next(obj)``, which is Py2/3 compatible, but doesn't change any ``next`` method
names to ``__next__``, which would break Py2 compatibility.

``fix_next`` is applied in stage 2.

.. code-block:: python

    lib2to3.fixes.fix_print

The ``fix_print_with_import`` fixer in ``libfuturize.fixes`` changes the code to
use print as a function and also adds ``from __future__ import
print_function`` to the top of modules using ``print()``.

In addition, it avoids adding an extra set of parentheses if these already
exist. So ``print(x)`` does not become ``print((x))``.

.. code-block:: python

    lib2to3.fixes.fix_raise

This fixer translates code to use the Python 3-only ``with_traceback()``
method on exceptions.

.. code-block:: python

    lib2to3.fixes.fix_set_literal

This converts ``set([1, 2, 3]``) to ``{1, 2, 3}``, breaking Python 2.6 support.

.. code-block:: python

    lib2to3.fixes.fix_ws_comma

This performs cosmetic changes. This is not applied by default because it
does not serve to improve Python 2/3 compatibility. (In some cases it may
also reduce readability: see issue #58.)



.. _forwards-conversion-stage2:

Stage 2: Py3-style code with wrappers for Py2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run stage 2 of the conversion process with::

    futurize --stage2 myfolder/*.py

This stage adds a dependency on the ``future`` package. The goal for stage 2 is
to make further mostly safe changes to the Python 2 code to use Python 3-style
code that then still runs on Python 2 with the help of the appropriate builtins
and utilities in ``future``.

For example::

    name = raw_input('What is your name?\n')

    for k, v in d.iteritems():
        assert isinstance(v, basestring)

    class MyClass(object):
        def __unicode__(self):
            return u'My object'
        def __str__(self):
            return unicode(self).encode('utf-8')

would be converted by Stage 2 to this code::

    from builtins import input
    from builtins import str
    from future.utils import iteritems, python_2_unicode_compatible

    name = input('What is your name?\n')

    for k, v in iteritems(d):
        assert isinstance(v, (str, bytes))

    @python_2_unicode_compatible
    class MyClass(object):
        def __str__(self):
            return u'My object'

Stage 2 also renames standard-library imports to their Py3 names and adds these
two lines::

    from future import standard_library
    standard_library.install_aliases()

For example::

    import ConfigParser

becomes::

    from future import standard_library
    standard_library.install_aliases()
    import configparser

The complete list of fixers applied in Stage 2 is::

    lib2to3.fixes.fix_basestring
    lib2to3.fixes.fix_dict
    lib2to3.fixes.fix_exec
    lib2to3.fixes.fix_getcwdu
    lib2to3.fixes.fix_input
    lib2to3.fixes.fix_itertools
    lib2to3.fixes.fix_itertools_imports
    lib2to3.fixes.fix_filter
    lib2to3.fixes.fix_long
    lib2to3.fixes.fix_map
    lib2to3.fixes.fix_nonzero
    lib2to3.fixes.fix_operator
    lib2to3.fixes.fix_raw_input
    lib2to3.fixes.fix_zip

    libfuturize.fixes.fix_cmp
    libfuturize.fixes.fix_division
    libfuturize.fixes.fix_execfile
    libfuturize.fixes.fix_future_builtins
    libfuturize.fixes.fix_future_standard_library
    libfuturize.fixes.fix_future_standard_library_urllib
    libfuturize.fixes.fix_metaclass
    libpasteurize.fixes.fix_newstyle
    libfuturize.fixes.fix_object
    libfuturize.fixes.fix_unicode_keep_u
    libfuturize.fixes.fix_xrange_with_import


Not applied::

    lib2to3.fixes.fix_buffer    # Perhaps not safe. Test this.
    lib2to3.fixes.fix_callable  # Not needed in Py3.2+
    lib2to3.fixes.fix_execfile  # Some problems: see issue #37.
                                # We use the custom libfuturize.fixes.fix_execfile instead.
    lib2to3.fixes.fix_future    # Removing __future__ imports is bad for Py2 compatibility!
    lib2to3.fixes.fix_imports   # Called by libfuturize.fixes.fix_future_standard_library
    lib2to3.fixes.fix_imports2  # We don't handle this yet (dbm)
    lib2to3.fixes.fix_metaclass # Causes SyntaxError in Py2! Use the one from ``six`` instead
    lib2to3.fixes.fix_unicode   # Strips off the u'' prefix, which removes a potentially
                                # helpful source of information for disambiguating
                                # unicode/byte strings.
    lib2to3.fixes.fix_urllib    # Included in libfuturize.fix_future_standard_library_urllib
    lib2to3.fixes.fix_xrange    # Custom one because of a bug with Py3.3's lib2to3


Fixes applied with the ``futurize --conservative`` option::

    libfuturize.fixes.fix_division_safe    # instead of libfuturize.fixes.fix_division.



.. Ideally the output of this stage should not be a ``SyntaxError`` on either
.. Python 3 or Python 2.

.. _forwards-conversion-text:

Separating text from bytes
~~~~~~~~~~~~~~~~~~~~~~~~~~

After applying stage 2, the recommended step is to decide which of your Python
2 strings represent text and which represent binary data and to prefix all
string literals with either ``b`` or ``u`` accordingly. Furthermore, to ensure
that these types behave similarly on Python 2 as on Python 3, also wrap
byte-strings or text in the ``bytes`` and ``str`` types from ``future``. For
example::

    from builtins import bytes, str
    b = bytes(b'\x00ABCD')
    s = str(u'This is normal text')

Any unadorned string literals will then represent native platform strings
(byte-strings on Py2, unicode strings on Py3).

An alternative is to pass the ``--unicode-literals`` flag::

  $ futurize --unicode-literals mypython2script.py

After running this, all string literals that were not explicitly marked up as
``b''`` will mean text (Python 3 ``str`` or Python 2 ``unicode``).



.. _forwards-conversion-stage3:

Post-conversion
~~~~~~~~~~~~~~~

After running ``futurize``, we recommend first running your tests on Python 3 and making further code changes until they pass on Python 3.

The next step would be manually tweaking the code to re-enable Python 2
compatibility with the help of the ``future`` package. For example, you can add
the ``@python_2_unicode_compatible`` decorator to any classes that define custom
``__str__`` methods. See :ref:`what-else` for more info.


