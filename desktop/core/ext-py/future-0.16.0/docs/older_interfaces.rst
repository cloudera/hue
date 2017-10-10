.. _older-standard-library-interfaces:

Older interfaces
~~~~~~~~~~~~~~~~

In addition to the direct and ``install_aliases()`` interfaces (described in
:ref:`standard-library-imports`), ``future`` supports four other interfaces to
the reorganized standard library. This is largely for historical reasons (for
versions prior to 0.14).


``future.moves`` interface
__________________________

The ``future.moves`` interface avoids import hooks. It may therefore be more
robust, at the cost of less idiomatic code. Use it as follows::

    from future.moves import queue
    from future.moves import socketserver
    from future.moves.http.client import HTTPConnection
    # etc.

If you wish to achieve the effect of a two-level import such as this::

    import http.client 

portably on both Python 2 and Python 3, note that Python currently does not
support syntax like this::

    from future.moves import http.client

One workaround is to replace the dot with an underscore::

    import future.moves.http.client as http_client


Comparing future.moves and six.moves
++++++++++++++++++++++++++++++++++++

``future.moves`` and ``six.moves`` provide a similar Python 3-style
interface to the native standard library module definitions.

The major difference is that the ``future.moves`` package is a real Python package
(``future/moves/__init__.py``) with real modules provided as ``.py`` files, whereas
``six.moves`` constructs fake ``_LazyModule`` module objects within the Python
code and injects them into the ``sys.modules`` cache.

The advantage of ``six.moves`` is that the code fits in a single module that can be
copied into a project that seeks to eliminate external dependencies.

The advantage of ``future.moves`` is that it is likely to be more robust in the
face of magic like Django's auto-reloader and tools like ``py2exe`` and
``cx_freeze``. See issues #51, #53, #56, and #63 in the ``six`` project for
more detail of bugs related to the ``six.moves`` approach.


``import_`` and ``from_import`` functions
_________________________________________

The functional interface is to use the ``import_`` and ``from_import``
functions from ``future.standard_library`` as follows::

    from future.standard_library import import_, from_import
    
    http = import_('http.client')
    urllib = import_('urllib.request')

    urlopen, urlsplit = from_import('urllib.request', 'urlopen', 'urlsplit')

This interface also works with two-level imports.


Context-manager for import hooks
________________________________

The context-manager interface is via a context-manager called ``hooks``::

    from future.standard_library import hooks
    with hooks():
        import socketserver
        import queue
        import configparser
        import test.support
        import html.parser
        from collections import UserList
        from itertools import filterfalse, zip_longest
        from http.client import HttpConnection
        import urllib.request
        # and other moved modules and definitions

This interface is straightforward and effective, using PEP 302 import
hooks. However, there are reports that this sometimes leads to problems
(see issue #238). Until this is resolved, it is probably safer to use direct
imports or one of the other import mechanisms listed above.


install_hooks() call (deprecated)
_________________________________

The last interface to the reorganized standard library is via a call to
``install_hooks()``::

    from future import standard_library
    standard_library.install_hooks()

    import urllib
    f = urllib.request.urlopen('http://www.python.org/')

    standard_library.remove_hooks()

If you use this interface, it is recommended to disable the import hooks again
after use by calling ``remove_hooks()``, in order to prevent the futurized
modules from being invoked inadvertently by other modules. (Python does not
automatically disable import hooks at the end of a module, but keeps them
active for the life of a process unless removed.)

.. The call to ``scrub_future_sys_modules()`` removes any modules from the
.. ``sys.modules`` cache (on Py2 only) that have Py3-style names, like ``http.client``.
.. This can prevent libraries that have their own Py2/3 compatibility code from
.. importing the ``future.moves`` or ``future.backports`` modules unintentionally.
.. Code such as this will then fall through to using the Py2 standard library
.. modules on Py2::
.. 
..     try:
..         from http.client import HTTPConnection
..     except ImportError:
..         from httplib import HTTPConnection
.. 
.. **Requests**: The above snippet is from the `requests
.. <http://docs.python-requests.org>`_ library. As of v0.12, the
.. ``future.standard_library`` import hooks are compatible with Requests.


.. If you wish to avoid changing every reference of ``http.client`` to
.. ``http_client`` in your code, an alternative is this::
.. 
..     from future.standard_library import http
..     from future.standard_library.http import client as _client
..     http.client = client

.. but it has the advantage that it can be used by automatic translation scripts such as ``futurize`` and ``pasteurize``.


