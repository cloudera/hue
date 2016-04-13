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

This happens because ``mod_wsgi`` uses sub-interpreters, which can cause a
problem during initialization of the OpenSSL backend. To resolve this set the
`WSGIApplicationGroup`_ to ``%{GLOBAL}`` in the ``mod_wsgi`` configuration.

``cryptography`` raised an ``InternalError`` and I'm not sure what to do?
-------------------------------------------------------------------------

Frequently ``InternalError`` is raised when there are errors on the OpenSSL
error stack that were placed there by other libraries that are also using
OpenSSL. Try removing the other libraries and see if the problem persists.
If you have no other libraries using OpenSSL in your process, or they do not
appear to be at fault, it's possible that this is a bug in ``cryptography``.
Please file an `issue`_ with instructions on how to reproduce it.

.. _`NaCl`: https://nacl.cr.yp.to/
.. _`PyNaCl`: https://pynacl.readthedocs.org
.. _`WSGIApplicationGroup`: https://modwsgi.readthedocs.org/en/develop/configuration-directives/WSGIApplicationGroup.html
.. _`issue`: https://github.com/pyca/cryptography/issues
