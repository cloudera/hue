Frequently asked questions
==========================

How does ``cryptography`` compare to NaCl (Networking and Cryptography Library)?
--------------------------------------------------------------------------------

While ``cryptography`` and `NaCl`_ both share the goal of making cryptography
easier, and safer, to use for developers, ``cryptography`` is designed to be a
general purpose library, interoperable with existing systems, while NaCl
features a collection of hand selected algorithms.

``cryptography``'s :ref:`recipes <cryptography-layout>` layer has similar goals
to NaCl.

If you prefer NaCl's design, we highly recommend `PyNaCl`_.

Compiling ``cryptography`` on OS X produces a ``fatal error: 'openssl/aes.h' file not found`` error
---------------------------------------------------------------------------------------------------

This happens because OS X 10.11 no longer includes a copy of OpenSSL.
``cryptography`` now provides wheels which include a statically linked copy of
OpenSSL. You're seeing this error because your copy of pip is too old to find
our wheel files. Upgrade your copy of pip with ``pip install -U pip`` and then
try install ``cryptography`` again.

Starting ``cryptography`` using ``mod_wsgi`` produces an ``InternalError`` during a call in ``_register_osrandom_engine``
-------------------------------------------------------------------------------------------------------------------------

Upgrade to the latest ``cryptography`` and this issue should be resolved.

``cryptography`` raised an ``InternalError`` and I'm not sure what to do?
-------------------------------------------------------------------------

Frequently ``InternalError`` is raised when there are errors on the OpenSSL
error stack that were placed there by other libraries that are also using
OpenSSL. Try removing the other libraries and see if the problem persists.
If you have no other libraries using OpenSSL in your process, or they do not
appear to be at fault, it's possible that this is a bug in ``cryptography``.
Please file an `issue`_ with instructions on how to reproduce it.

Installing ``cryptography`` fails with ``ImportError: No module named setuptools_ext``
--------------------------------------------------------------------------------------

Your ``cffi`` package is out of date. ``pip install -U cffi`` to update it.

Installing cryptography with OpenSSL 0.9.8 or 1.0.0 fails
---------------------------------------------------------

The OpenSSL project has dropped support for the 0.9.8 and 1.0.0 release series.
Since they are no longer receiving security patches from upstream,
``cryptography`` is also dropping support for them. To fix this issue you
should upgrade to a newer version of OpenSSL (1.0.1 or later). This may require
you to upgrade to a newer operating system.

.. _`NaCl`: https://nacl.cr.yp.to/
.. _`PyNaCl`: https://pynacl.readthedocs.io
.. _`WSGIApplicationGroup`: https://modwsgi.readthedocs.io/en/develop/configuration-directives/WSGIApplicationGroup.html
.. _`issue`: https://github.com/pyca/cryptography/issues
