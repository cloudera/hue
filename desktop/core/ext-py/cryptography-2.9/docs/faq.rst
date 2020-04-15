Frequently asked questions
==========================

``cryptography`` failed to install!
-----------------------------------

If you are having issues installing ``cryptography`` the first troubleshooting
step is to upgrade ``pip`` and then try to install again. For most users this will
take the form of ``pip install -U pip``, but on Windows you should do
``python -m pip install -U pip``. If you are still seeing errors after upgrading
and trying ``pip install cryptography`` again, please see the :doc:`/installation`
documentation.

How does ``cryptography`` compare to NaCl (Networking and Cryptography Library)?
--------------------------------------------------------------------------------

While ``cryptography`` and `NaCl`_ both share the goal of making cryptography
easier, and safer, to use for developers, ``cryptography`` is designed to be a
general purpose library, interoperable with existing systems, while NaCl
features a collection of hand selected algorithms.

``cryptography``'s :ref:`recipes <cryptography-layout>` layer has similar goals
to NaCl.

If you prefer NaCl's design, we highly recommend `PyNaCl`_, which is also
maintained by the PyCA team.

Why use ``cryptography``?
-------------------------

If you've done cryptographic work in Python before you have likely encountered
other libraries in Python such as *M2Crypto*, *PyCrypto*, or *PyOpenSSL*. In
building ``cryptography`` we wanted to address a few issues we observed in the
legacy libraries:

* Extremely error prone APIs and insecure defaults.
* Use of poor implementations of algorithms (i.e. ones with known side-channel
  attacks).
* Lack of maintenance.
* Lack of high level APIs.
* Lack of PyPy and Python 3 support.
* Absence of algorithms such as
  :class:`AES-GCM <cryptography.hazmat.primitives.ciphers.modes.GCM>` and
  :class:`~cryptography.hazmat.primitives.kdf.hkdf.HKDF`.

Compiling ``cryptography`` on macOS produces a ``fatal error: 'openssl/aes.h' file not found`` error
----------------------------------------------------------------------------------------------------

This happens because macOS 10.11 no longer includes a copy of OpenSSL.
``cryptography`` now provides wheels which include a statically linked copy of
OpenSSL. You're seeing this error because your copy of pip is too old to find
our wheel files. Upgrade your copy of pip with ``pip install -U pip`` and then
try install ``cryptography`` again.

If you are using PyPy, we do not currently ship ``cryptography`` wheels for
PyPy. You will need to install your own copy of OpenSSL -- we recommend using
Homebrew.

``cryptography`` raised an ``InternalError`` and I'm not sure what to do?
-------------------------------------------------------------------------

Frequently ``InternalError`` is raised when there are errors on the OpenSSL
error stack that were placed there by other libraries that are also using
OpenSSL. Try removing the other libraries and see if the problem persists.
If you have no other libraries using OpenSSL in your process, or they do not
appear to be at fault, it's possible that this is a bug in ``cryptography``.
Please file an `issue`_ with instructions on how to reproduce it.

error: ``-Werror=sign-conversion``: No option ``-Wsign-conversion`` during installation
---------------------------------------------------------------------------------------

The compiler you are using is too old and not supported by ``cryptography``.
Please upgrade to a more recent version. If you are running OpenBSD 6.1 or
earlier the default compiler is extremely old. Use ``pkg_add`` to install a
newer ``gcc`` and then install ``cryptography`` using
``CC=/path/to/newer/gcc pip install cryptography``.

Installing ``cryptography`` fails with ``Invalid environment marker: python_version < '3'``
-------------------------------------------------------------------------------------------

Your ``pip`` and/or ``setuptools`` are outdated. Please upgrade to the latest
versions with ``pip install -U pip setuptools`` (or on Windows
``python -m pip install -U pip setuptools``).

Importing cryptography causes a ``RuntimeError`` about OpenSSL 1.0.1
--------------------------------------------------------------------

The OpenSSL project has dropped support for the 1.0.1 release series. Since it
is no longer receiving security patches from upstream, ``cryptography`` is also
dropping support for it. To fix this issue you should upgrade to a newer
version of OpenSSL (1.0.2 or later). This may require you to upgrade to a newer
operating system.

For the 2.9 release, you can set the ``CRYPTOGRAPHY_ALLOW_OPENSSL_101``
environment variable. Please note that this is *temporary* and will be removed
in ``cryptography`` 3.0.

Installing cryptography with OpenSSL 0.9.8 or 1.0.0 fails
---------------------------------------------------------

The OpenSSL project has dropped support for the 0.9.8 and 1.0.0 release series.
Since they are no longer receiving security patches from upstream,
``cryptography`` is also dropping support for them. To fix this issue you
should upgrade to a newer version of OpenSSL (1.0.2 or later). This may require
you to upgrade to a newer operating system.

Why are there no wheels for Python 3.6+ on Linux or macOS?
----------------------------------------------------------

Our Python3 wheels, for macOS and Linux, are ``abi3`` wheels. This means they
support multiple versions of Python. The Python 3.5 ``abi3`` wheel can be used
with any version of Python greater than or equal to 3.5. Recent versions of
``pip`` will automatically install ``abi3`` wheels.

``ImportError``: ``idna`` is not installed
------------------------------------------

``cryptography`` deprecated passing :term:`U-label` strings to various X.509
constructors in version 2.1 and in version 2.5 moved the ``idna`` dependency
to a ``setuptools`` extra. If you see this exception you should upgrade your
software so that it no longer depends on this deprecated feature. If that is
not yet possible you  can also install ``cryptography`` with
``pip install cryptography[idna]`` to automatically install the missing
dependency. This workaround will be available until the feature is fully
removed.

Why can't I import my PEM file?
-------------------------------

PEM is a format (defined by several RFCs, but originally :rfc:`1421`) for
encoding keys, certificates and others cryptographic data into a regular form.
The data is encoded as base64 and wrapped with a header and footer.

If you are having trouble importing PEM files, make sure your file fits
the following rules:

* has a one-line header like this: ``-----BEGIN [FILE TYPE]-----``
  (where ``[FILE TYPE]`` is ``CERTIFICATE``, ``PUBLIC KEY``, ``PRIVATE KEY``,
  etc.)

* has a one-line footer like this: ``-----END [FILE TYPE]-----``

* all lines, except for the final one, must consist of exactly 64
  characters.

For example, this is a PEM file for a RSA Public Key: ::

   -----BEGIN PUBLIC KEY-----
   MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7CsKFSzq20NLb2VQDXma
   9DsDXtKADv0ziI5hT1KG6Bex5seE9pUoEcUxNv4uXo2jzAUgyRweRl/DLU8SoN8+
   WWd6YWik4GZvNv7j0z28h9Q5jRySxy4dmElFtIRHGiKhqd1Z06z4AzrmKEzgxkOk
   LJjY9cvwD+iXjpK2oJwNNyavvjb5YZq6V60RhpyNtKpMh2+zRLgIk9sROEPQeYfK
   22zj2CnGBMg5Gm2uPOsGDltl/I/Fdh1aO3X4i1GXwCuPf1kSAg6lPJD0batftkSG
   v0X0heUaV0j1HSNlBWamT4IR9+iJfKJHekOqvHQBcaCu7Ja4kXzx6GZ3M2j/Ja3A
   2QIDAQAB
   -----END PUBLIC KEY-----


.. _`NaCl`: https://nacl.cr.yp.to/
.. _`PyNaCl`: https://pynacl.readthedocs.io
.. _`WSGIApplicationGroup`: https://modwsgi.readthedocs.io/en/develop/configuration-directives/WSGIApplicationGroup.html
.. _`issue`: https://github.com/pyca/cryptography/issues
