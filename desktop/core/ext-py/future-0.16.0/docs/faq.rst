Frequently Asked Questions (FAQ)
********************************

Who is this for?
================

1. People with existing or new Python 3 codebases who wish to provide
ongoing Python 2.6 / 2.7 support easily and with little maintenance burden.

2. People who wish to ease and accelerate migration of their Python 2 codebases
to Python 3.3+, module by module, without giving up Python 2 compatibility.


Why upgrade to Python 3?
========================

.. epigraph::

   "Python 2 is the next COBOL."

   -- Alex Gaynor, at PyCon AU 2013

Python 2.7 is the end of the Python 2 line. (See `PEP 404
<http://www.python.org/peps/pep-0404/>`_.) The language and standard
libraries are improving only in Python 3.x.

Python 3.x is a better language and better set of standard libraries than
Python 2.x in many ways. Python 3.x is cleaner, less warty, and easier to
learn than Python 2. It has better memory efficiency, easier Unicode handling,
and powerful new features like the `asyncio
<https://docs.python.org/3/library/asyncio.html>`_ module.

.. Unicode handling is also much easier. For example, see `this page
.. <http://pythonhosted.org/kitchen/unicode-frustrations.html>`_
.. describing some of the problems with handling Unicode on Python 2 that
.. Python 3 mostly solves. 


Porting philosophy
==================

Why write Python 3-style code?
------------------------------

Here are some quotes:

- "Django's developers have found that attempting to write Python 3 code
  that's compatible with Python 2 is much more rewarding than the
  opposite." from the `Django docs
  <https://docs.djangoproject.com/en/dev/topics/python3/>`_.

- "Thanks to Python 3 being more strict about things than Python 2 (e.g.,
  bytes vs. strings), the source translation [from Python 3 to 2] can be
  easier and more straightforward than from Python 2 to 3. Plus it gives
  you more direct experience developing in Python 3 which, since it is
  the future of Python, is a good thing long-term." from the official
  guide `"Porting Python 2 Code to Python 3"
  <http://docs.python.org/2/howto/pyporting.html>`_ by Brett Cannon.

- "Developer energy should be reserved for addressing real technical
  difficulties associated with the Python 3 transition (like
  distinguishing their 8-bit text strings from their binary data). They
  shouldn't be punished with additional code changes ..." from `PEP 414
  <http://www.python.org/dev/peps/pep-0414/>`_ by Armin Ronacher and Nick
  Coghlan.


Can't I just roll my own Py2/3 compatibility layer?
---------------------------------------------------

Yes, but using ``python-future`` will probably be easier and lead to cleaner
code with fewer bugs.

Consider this quote:

.. epigraph::

   "Duplication of effort is wasteful, and replacing the various
   home-grown approaches with a standard feature usually ends up making
   things more readable, and interoperable as well."

   -- Guido van Rossum (`blog post <http://www.artima.com/weblogs/viewpost.jsp?thread=86641>`_)


``future`` also includes various Py2/3 compatibility tools in
:mod:`future.utils` picked from large projects (including IPython,
Django, Jinja2, Pandas), which should reduce the burden on every project to
roll its own py3k compatibility wrapper module.


What inspired this project?
---------------------------

In our Python training courses, we at `Python Charmers
<http://pythoncharmers.com>`_ faced a dilemma: teach people Python 3, which was
future-proof but not as useful to them today because of weaker 3rd-party
package support, or teach people Python 2, which was more useful today but
would require them to change their code and unlearn various habits soon. We
searched for ways to avoid polluting the world with more deprecated code, but
didn't find a good way.

Also, in attempting to help with porting packages such as `scikit-learn
<http://scikit-learn.org>`_ to Python 3, I (Ed) was dissatisfied with how much
code cruft was necessary to introduce to support Python 2 and 3 from a single
codebase (the preferred porting option). Since backward-compatibility with
Python 2 may be necessary for at least the next 5 years, one of the promised
benefits of Python 3 -- cleaner code with fewer of Python 2's warts -- was
difficult to realize before in practice in a single codebase that supported
both platforms.

The goal is to accelerate the uptake of Python 3 and help the strong Python
community to remain united around a single version of the language.


Maturity
========

How well has it been tested?
----------------------------

``future`` is used by several major projects, including `mezzanine
<http://mezzanine.jupo.org>`_ and `ObsPy <http://www.obspy.org>`_. It is also
currently being used to help with porting 800,000 lines of Python 2 code in
`Sage <http://sagemath.org>`_ to Python 2/3.

Currently ``python-future`` has over 1000 unit tests. Many of these are straight
from the Python 3.3 and 3.4 test suites.

In general, the ``future`` package itself is in good shape, whereas the
``futurize`` script for automatic porting is imperfect; chances are it will
require some manual cleanup afterwards. The ``past`` package also needs to be
expanded.


Is the API stable?
------------------

Not yet; ``future`` is still in beta. Where possible, we will try not to break
anything which was documented and used to work.  After version 1.0 is released,
the API will not change in backward-incompatible ways until a hypothetical
version 2.0.

..
    Are there any example of Python 2 packages ported to Python 3 using ``future`` and ``futurize``?
    ------------------------------------------------------------------------------------------------
    
    Yes, an example is the port of ``xlwt``, available `here
    <https://github.com/python-excel/xlwt/pull/32>`_.
    
    The code also contains backports for several Py3 standard library
    modules under ``future/standard_library/``.


Relationship between python-future and other compatibility tools
================================================================

How does this relate to ``2to3``?
---------------------------------

``2to3`` is a powerful and flexible tool that can produce different
styles of Python 3 code. It is, however, primarily designed for one-way
porting efforts, for projects that can leave behind Python 2 support.

The example at the top of the `2to3 docs
<http://docs.python.org/2/library/2to3.html>`_ demonstrates this.  After
transformation by ``2to3``, ``example.py`` looks like this::

    def greet(name):
        print("Hello, {0}!".format(name))
    print("What's your name?")
    name = input()
    greet(name)

This is Python 3 code that, although syntactically valid on Python 2,
is semantically incorrect. On Python 2, it raises an exception for
most inputs; worse, it allows arbitrary code execution by the user
for specially crafted inputs because of the ``eval()`` executed by Python
2's ``input()`` function.

This is not an isolated example; almost every output of ``2to3`` will need
modification to provide backward compatibility with Python 2. As an
alternative, the ``python-future`` project provides a script called
``futurize`` that is based on ``lib2to3`` but will produce code that is
compatible with both platforms (Py2 and Py3).


Can I maintain a Python 2 codebase and use 2to3 to automatically convert to Python 3 in the setup script?
---------------------------------------------------------------------------------------------------------

This was originally the approach recommended by Python's core developers,
but it has some large drawbacks:
    
1. First, your actual working codebase will be stuck with Python 2's
warts and smaller feature set for as long as you need to retain Python 2
compatibility. This may be at least 5 years for many projects, possibly
much longer.
    
2. Second, this approach carries the significant disadvantage that you
cannot apply patches submitted by Python 3 users against the
auto-generated Python 3 code. (See `this talk
<http://www.youtube.com/watch?v=xNZ4OVO2Z_E>`_ by Jacob Kaplan-Moss.)


What is the relationship between ``future`` and ``six``?
--------------------------------------------------------

``python-future`` is a higher-level compatibility layer than ``six`` that
includes more backported functionality from Python 3, more forward-ported
functionality from Python 2, and supports cleaner code, but requires more
modern Python versions to run.

``python-future`` and ``six`` share the same goal of making it possible to write
a single-source codebase that works on both Python 2 and Python 3.
``python-future`` has the further goal of allowing standard Py3 code to run with
almost no modification on both Py3 and Py2. ``future`` provides a more
complete set of support for Python 3's features, including backports of
Python 3 builtins such as the ``bytes`` object (which is very different
to Python 2's ``str`` object) and several standard library modules.

``python-future`` supports only Python 2.6+ and Python 3.3+, whereas ``six``
supports all versions of Python from 2.4 onwards. (See
:ref:`supported-versions`.) If you must support older Python versions,
``six`` will be esssential for you. However, beware that maintaining
single-source compatibility with older Python versions is ugly and `not
fun <http://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/>`_.

If you can drop support for older Python versions, ``python-future`` leverages
some important features introduced into Python 2.6 and 2.7, such as
import hooks, and a comprehensive and well-tested set of backported
functionality, to allow you to write more idiomatic, maintainable code with
fewer compatibility hacks.


What is the relationship between ``python-future`` and ``python-modernize``?
----------------------------------------------------------------------------

``python-future`` contains, in addition to the ``future`` compatibility
package, a ``futurize`` script that is similar to ``python-modernize.py``
in intent and design. Both are based heavily on ``2to3``.
    
Whereas ``python-modernize`` converts Py2 code into a common subset of
Python 2 and 3, with ``six`` as a run-time dependency, ``futurize``
converts either Py2 or Py3 code into (almost) standard Python 3 code,
with ``future`` as a run-time dependency.

Because ``future`` provides more backported Py3 behaviours from ``six``,
the code resulting from ``futurize`` is more likely to work
identically on both Py3 and Py2 with less additional manual porting
effort.


Platform and version support
============================

.. _supported-versions:

Which versions of Python does ``python-future`` support?
--------------------------------------------------------

Python 2.6, 2.7, and 3.3+ only.

Python 2.6 and 2.7 introduced many important forward-compatibility
features (such as import hooks, ``b'...'`` literals and ``__future__``
definitions) that greatly reduce the maintenance burden for single-source
Py2/3 compatible code. ``future`` leverages these features and aims to
close the remaining gap between Python 3 and 2.6 / 2.7.

Python 3.2 could perhaps be supported too, although the illegal unicode
literal ``u'...'`` syntax may be inconvenient to work around. The Py3.2
userbase is very small, however. Please let us know via GitHub `issue #29
<https://github.com/PythonCharmers/python-future/issues/29>`_ if you
would like to see Py3.2 support.


Do you support Pypy?
~~~~~~~~~~~~~~~~~~~~

Yes, except for the standard library import hooks (currently). Feedback
and pull requests are welcome!


Do you support IronPython and/or Jython?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Not sure. This would be nice...


.. _support:

Support
=======

Is there a mailing list?
------------------------

Yes, please ask any questions on the `python-porting
<https://mail.python.org/mailman/listinfo/python-porting>`_ mailing list.


.. _contributing:

Contributing
============

Can I help?
-----------

Yes please :) We welcome bug reports, additional tests, pull requests,
and stories of either success or failure with using it. Help with the fixers
for the ``futurize`` script is particularly welcome.


Where is the repo?
------------------

`<https://github.com/PythonCharmers/python-future>`_.

