========================================================
pyOpenSSL -- A Python wrapper around the OpenSSL library
========================================================

.. image:: https://readthedocs.org/projects/pyopenssl/badge/?version=stable
   :target: https://pyopenssl.org/en/stable/
   :alt: Stable Docs

.. image:: https://travis-ci.org/pyca/pyopenssl.svg?branch=master
   :target: https://travis-ci.org/pyca/pyopenssl
   :alt: Build status

.. image:: https://codecov.io/github/pyca/pyopenssl/branch/master/graph/badge.svg
   :target: https://codecov.io/github/pyca/pyopenssl
   :alt: Test coverage


High-level wrapper around a subset of the OpenSSL library.  Includes

* ``SSL.Connection`` objects, wrapping the methods of Python's portable sockets
* Callbacks written in Python
* Extensive error-handling mechanism, mirroring OpenSSL's error codes

... and much more.

You can find more information in the documentation_.
Development takes place on GitHub_.


Discussion
==========

If you run into bugs, you can file them in our `issue tracker`_.

We maintain a cryptography-dev_ mailing list for both user and development discussions.

You can also join ``#cryptography-dev`` on Freenode to ask questions or get involved.


.. _documentation: https://pyopenssl.org/
.. _`issue tracker`: https://github.com/pyca/pyopenssl/issues
.. _cryptography-dev: https://mail.python.org/mailman/listinfo/cryptography-dev
.. _GitHub: https://github.com/pyca/pyopenssl
