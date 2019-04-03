.. _whats-new:

What's New
**********

What's new in version 0.17.1 (2019-10-30)
=========================================
This release address a packaging error because of an erroneous declaration that
any built wheels are universal.

What's new in version 0.17.0 (2018-10-19)
=========================================

This is a major bug-fix release, including:

- Fix ``from collections import ChainMap`` after install_aliases() (issue #226)
- Fix multiple import from ``__future__`` bug in futurize (issue #113)
- Add support for proper %s formatting of newbytes
- Properly implement iterator protocol for newrange object
- Fix ``past.translation`` on read-only file systems
- Fix Tkinter import bug introduced in Python 2.7.4 (issue #262)
- Correct TypeError to ValueError in a specific edge case for newrange
- Support inequality tests betwen newstrs and newbytes
- Add type check to __get__ in newsuper
- Fix fix_divsion_safe to support better conversion of complex expressions, and
  skip obvious float division.

As well as a number of corrections to a variety of documentation, and updates to
test infrastructure.

What's new in version 0.16.0 (2016-10-27)
==========================================

This release removes the ``configparser`` package as an alias for
``ConfigParser`` on Py2 to improve compatibility with the backported
`configparser package <https://pypi.org/project/configparser/>`. Previously
``python-future`` and the PyPI ``configparser`` backport clashed, causing
various compatibility issues. (Issues #118, #181)

If your code previously relied on ``configparser`` being supplied by
``python-future``, the recommended upgrade path is to run ``pip install
configparser`` or add ``configparser`` to your ``requirements.txt`` file.

Note that, if you are upgrading ``future`` with ``pip``, you may need to
uninstall the old version of future or manually remove the
``site-packages/future-0.15.2-py2.7.egg`` folder for this change to take
effect on your system.

This releases also fixes these bugs:

- Fix ``newbytes`` constructor bug. (Issue #163)
- Fix semantics of ``bool()`` with ``newobject``. (Issue #211)
- Fix ``standard_library.install_aliases()`` on PyPy. (Issue #205)
- Fix assertRaises for ``pow`` and ``compile``` on Python 3.5. (Issue #183)
- Fix return argument of ``future.utils.ensure_new_type`` if conversion to
  new type does not exist. (Issue #185)
- Add missing ``cmp_to_key`` for Py2.6. (Issue #189)
- Allow the ``old_div`` fixer to be disabled. (Issue #190)
- Improve compatibility with Google App Engine. (Issue #231)
- Add some missing imports to the ``tkinter`` and ``tkinter.filedialog``
  package namespaces. (Issues #212 and #233)
- More complete implementation of ``raise_from`` on PY3. (Issues #141,
  #213 and #235, fix provided by Varriount)


What's new in version 0.15.2 (2015-09-11)
=========================================

This is a minor bug-fix release:

- Fix ``socket.create_connection()`` backport on Py2.6 (issue #162)
- Add more tests of ``urllib.request`` etc.
- Fix ``newsuper()`` calls from the ``__init__`` method of PyQt subclassses
  (issue #160, thanks to Christopher Arndt)

What's new in version 0.15.1 (2015-09-09)
=========================================

This is a minor bug-fix release:

- Use 3-argument ``socket.create_connection()`` backport to restore Py2.6
  compatibility in ``urllib.request.urlopen()`` (issue #162)
- Remove breakpoint in ``future.backports.http.client`` triggered on certain
  data (issue #164)
- Move ``exec`` fixer to stage 1 of ``futurize`` because the forward-compatible ``exec(a, b)``
  idiom is supported in Python 2.6 and 2.7. See
  https://docs.python.org/2/reference/simple_stmts.html#exec.


What's new in version 0.15.0 (2015-07-25)
=========================================

This release fixes compatibility bugs with CherryPy's Py2/3 compat layer and
the latest version of the ``urllib3`` package. It also adds some additional
backports for Py2.6 and Py2.7 from Py3.4's standard library.

New features:

- ``install_aliases()`` now exposes full backports of the Py3 urllib submodules
  (``parse``, ``request`` etc.) from ``future.backports.urllib`` as submodules
  of ``urllib`` on Py2.  This implies, for example, that
  ``urllib.parse.unquote`` now takes an optional encoding argument as it does
  on Py3. This improves compatibility with CherryPy's Py2/3 compat layer (issue
  #158).
- ``tkinter.ttk`` support (issue #151)
- Backport of ``collections.ChainMap`` (issue #150)
- Backport of ``itertools.count`` for Py2.6 (issue #152)
- Enable and document support for the ``surrogateescape`` error handler for ``newstr`` and ``newbytes`` objects on Py2.x (issue #116). This feature is currently in alpha.
- Add constants to ``http.client`` such as ``HTTP_PORT`` and ``BAD_REQUEST`` (issue #137)
- Backport of ``reprlib.recursive_repr`` to Py2

Bug fixes:

- Add ``HTTPMessage`` to ``http.client``, which is missing from ``httplib.__all__`` on Python <= 2.7.10. This restores compatibility with the latest ``urllib3`` package (issue #159, thanks to Waldemar Kornewald)
- Expand newint.__divmod__ and newint.__rdivmod__ to fall back to <type 'long'>
  implementations where appropriate (issue #146 - thanks to Matt Bogosian)
- Fix newrange slicing for some slice/range combos (issue #132, thanks to Brad Walker)
- Small doc fixes (thanks to Michael Joseph and Tim Tröndle)
- Improve robustness of test suite against opening .pyc files as text on Py2
- Update backports of ``Counter`` and ``OrderedDict`` to use the newer
  implementations from Py3.4. This fixes ``.copy()`` preserving subclasses etc.
- ``futurize`` no longer breaks working Py2 code by changing ``basestring`` to
  ``str``. Instead it imports the ``basestring`` forward-port from
  ``past.builtins`` (issues #127 and #156)
- ``future.utils``: add ``string_types`` etc. and update docs (issue #126)

Previous versions
=================

See :ref:`whats-old` for versions prior to v0.15.
