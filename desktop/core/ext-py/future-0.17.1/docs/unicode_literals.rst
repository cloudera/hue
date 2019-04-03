.. _unicode-literals:

Should I import unicode_literals?
---------------------------------

The ``future`` package can be used with or without ``unicode_literals``
imports.

In general, it is more compelling to use ``unicode_literals`` when
back-porting new or existing Python 3 code to Python 2/3 than when porting
existing Python 2 code to 2/3. In the latter case, explicitly marking up all
unicode string literals with ``u''`` prefixes would help to avoid
unintentionally changing the existing Python 2 API. However, if changing the
existing Python 2 API is not a concern, using ``unicode_literals`` may speed up
the porting process.

This section summarizes the benefits and drawbacks of using
``unicode_literals``. To avoid confusion, we recommend using
``unicode_literals`` everywhere across a code-base or not at all, instead of
turning on for only some modules.



Benefits
~~~~~~~~

1. String literals are unicode on Python 3. Making them unicode on Python 2
   leads to more consistency of your string types across the two
   runtimes. This can make it easier to understand and debug your code.

2. Code without ``u''`` prefixes is cleaner, one of the claimed advantages
   of Python 3. Even though some unicode strings would require a function
   call to invert them to native strings for some Python 2 APIs (see
   :ref:`stdlib-incompatibilities`), the incidence of these function calls
   would usually be much lower than the incidence of ``u''`` prefixes for text
   strings in the absence of ``unicode_literals``.

3. The diff when porting to a Python 2/3-compatible codebase may be smaller,
   less noisy, and easier to review with ``unicode_literals`` than if an
   explicit ``u''`` prefix is added to every unadorned string literal.

4. If support for Python 3.2 is required (e.g. for Ubuntu 12.04 LTS or
   Debian wheezy), ``u''`` prefixes are a ``SyntaxError``, making
   ``unicode_literals`` the only option for a Python 2/3 compatible
   codebase. [However, note that ``future`` doesn't support Python 3.0-3.2.]


Drawbacks
~~~~~~~~~

1. Adding ``unicode_literals`` to a module amounts to a "global flag day" for
   that module, changing the data types of all strings in the module at once.
   Cautious developers may prefer an incremental approach. (See
   `here <http://lwn.net/Articles/165039/>`_ for an excellent article
   describing the superiority of an incremental patch-set in the the case
   of the Linux kernel.)

.. This is a larger-scale change than adding explicit ``u''`` prefixes to
..  all strings that should be Unicode.

2. Changing to ``unicode_literals`` will likely introduce regressions on
   Python 2 that require an initial investment of time to find and fix. The
   APIs may be changed in subtle ways that are not immediately obvious.

   An example on Python 2::

       ### Module: mypaths.py

       ...
       def unix_style_path(path):
           return path.replace('\\', '/')
       ...

       ### User code:

       >>> path1 = '\\Users\\Ed'
       >>> unix_style_path(path1)
       '/Users/ed'

   On Python 2, adding a ``unicode_literals`` import to ``mypaths.py`` would
   change the return type of the ``unix_style_path`` function from ``str`` to
   ``unicode`` in the user code, which is difficult to anticipate and probably
   unintended.

   The counter-argument is that this code is broken, in a portability
   sense; we see this from Python 3 raising a ``TypeError`` upon passing the
   function a byte-string. The code needs to be changed to make explicit
   whether the ``path`` argument is to be a byte string or a unicode string.

3. With ``unicode_literals`` in effect, there is no way to specify a native
   string literal (``str`` type on both platforms). This can be worked around as follows::

       >>> from __future__ import unicode_literals
       >>> ...
       >>> from future.utils import bytes_to_native_str as n

       >>> s = n(b'ABCD')
       >>> s
       'ABCD'  # on both Py2 and Py3

   although this incurs a performance penalty (a function call and, on Py3,
   a ``decode`` method call.)

   This is a little awkward because various Python library APIs (standard
   and non-standard) require a native string to be passed on both Py2
   and Py3. (See :ref:`stdlib-incompatibilities` for some examples. WSGI
   dictionaries are another.)

3. If a codebase already explicitly marks up all text with ``u''`` prefixes,
   and if support for Python versions 3.0-3.2 can be dropped, then
   removing the existing ``u''`` prefixes and replacing these with
   ``unicode_literals`` imports (the porting approach Django used) would
   introduce more noise into the patch and make it more difficult to review.
   However, note that the ``futurize`` script takes advantage of PEP 414 and
   does not remove explicit ``u''`` prefixes that already exist.

4. Turning on ``unicode_literals`` converts even docstrings to unicode, but
   Pydoc breaks with unicode docstrings containing non-ASCII characters for
   Python versions < 2.7.7. (`Fix
   committed <http://bugs.python.org/issue1065986#msg207403>`_ in Jan 2014.)::

       >>> def f():
       ...     u"Author: Martin von Löwis"

       >>> help(f)

       /Users/schofield/Install/anaconda/python.app/Contents/lib/python2.7/pydoc.pyc in pipepager(text, cmd)
          1376     pipe = os.popen(cmd, 'w')
          1377     try:
       -> 1378         pipe.write(text)
          1379         pipe.close()
          1380     except IOError:

       UnicodeEncodeError: 'ascii' codec can't encode character u'\xf6' in position 71: ordinal not in range(128)

See `this Stack Overflow thread
<http://stackoverflow.com/questions/809796/any-gotchas-using-unicode-literals-in-python-2-6>`_
for other gotchas.


Others' perspectives
~~~~~~~~~~~~~~~~~~~~

In favour of ``unicode_literals``
*********************************

Django recommends importing ``unicode_literals`` as its top `porting tip <https://docs.djangoproject.com/en/dev/topics/python3/#unicode-literals>`_ for
migrating Django extension modules to Python 3.  The following `quote
<https://groups.google.com/forum/#!topic/django-developers/2ddIWdicbNY>`_ is
from Aymeric Augustin on 23 August 2012 regarding why he chose
``unicode_literals`` for the port of Django to a Python 2/3-compatible
codebase.:

    "... I'd like to explain why this PEP [PEP 414, which allows explicit
    ``u''`` prefixes for unicode literals on Python 3.3+] is at odds with
    the porting philosophy I've applied to Django, and why I would have
    vetoed taking advantage of it.

    "I believe that aiming for a Python 2 codebase with Python 3
    compatibility hacks is a counter-productive way to port a project. You
    end up with all the drawbacks of Python 2 (including the legacy `u`
    prefixes) and none of the advantages Python 3 (especially the sane
    string handling).

    "Working to write Python 3 code, with legacy compatibility for Python
    2, is much more rewarding. Of course it takes more effort, but the
    results are much cleaner and much more maintainable. It's really about
    looking towards the future or towards the past.

    "I understand the reasons why PEP 414 was proposed and why it was
    accepted. It makes sense for legacy software that is minimally
    maintained. I hope nobody puts Django in this category!"


Against ``unicode_literals``
****************************

    "There are so many subtle problems that ``unicode_literals`` causes.
    For instance lots of people accidentally introduce unicode into
    filenames and that seems to work, until they are using it on a system
    where there are unicode characters in the filesystem path."

    -- Armin Ronacher

    "+1 from me for avoiding the unicode_literals future, as it can have
    very strange side effects in Python 2.... This is one of the key
    reasons I backed Armin's PEP 414."

    -- Nick Coghlan

    "Yeah, one of the nuisances of the WSGI spec is that the header values
    IIRC are the str or StringType on both py2 and py3. With
    unicode_literals this causes hard-to-spot bugs, as some WSGI servers
    might be more tolerant than others, but usually using unicode in python
    2 for WSGI headers will cause the response to fail."

    -- Antti Haapala
