.. _intro:

============
Introduction
============


History
=======

pyOpenSSL was originally created by Martin Sjögren because the SSL support in the standard library in Python 2.1 (the contemporary version of Python when the pyOpenSSL project was begun) was severely limited.
Other OpenSSL wrappers for Python at the time were also limited, though in different ways.

Later it was maintained by `Jean-Paul Calderone`_ who among other things managed to make pyOpenSSL a pure Python project which the current maintainers are *very* grateful for.

Over the time the standard library's ``ssl`` module improved, never reaching the completeness of pyOpenSSL's API coverage.
Despite `PEP 466`_ many useful features remain Python 3-only and pyOpenSSL remains the only alternative for full-featured TLS code across all noteworthy Python versions from 2.6 through 3.5 and PyPy_.


Development
===========

pyOpenSSL is collaboratively developed by the Python Cryptography Authority (PyCA_) that also maintains the low-level bindings called cryptography_.

Current maintainer and release manager is `Hynek Schlawack`_.


.. include:: ../CONTRIBUTING.rst


.. _Jean-Paul Calderone: https://github.com/exarkun
.. _PyPy: http://pypy.org
.. _PEP 466: https://www.python.org/dev/peps/pep-0466/
.. _PyCA: https://github.com/pyca
.. _cryptography: https://github.com/pyca/cryptography
.. _Hynek Schlawack: https://hynek.me/
