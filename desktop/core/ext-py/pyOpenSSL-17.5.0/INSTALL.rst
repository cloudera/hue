Installation
============

To install pyOpenSSL::

  $ pip install pyopenssl

If you are installing in order to *develop* on pyOpenSSL, move to the root directory of a pyOpenSSL checkout, and run::

  $ pip install -e .


.. warning::

   As of 0.14, pyOpenSSL is a pure-Python project.
   That means that if you encounter *any* kind of compiler errors, pyOpenSSL's bugtracker is the **wrong** place to report them because we *cannot* help you.

   Please take the time to read the errors and report them/ask help from the appropriate project.
   The most likely culprit being `cryptography <https://cryptography.io/>`_ that contains OpenSSL's library bindings.


Supported OpenSSL Versions
--------------------------

pyOpenSSL supports the same platforms and releases as the upstream cryptography project `does <https://cryptography.io/en/latest/installation/#supported-platforms>`_.
Currently that means:

- 1.0.1
- 1.0.2
- 1.1.0

If you need support for older releases, the following pinned versions will work:

- **OpenSSL 0.9.8**: ``'pyOpenSSL<17.0' 'cryptography<1.4'``
- **OpenSSL 1.0.0**: ``'pyOpenSSL<17.1' 'cryptography<1.7'``

You can always find out the versions of pyOpenSSL, cryptography, and the linked OpenSSL by running ``python -m OpenSSL.debug``.


Documentation
-------------

The documentation is written in reStructuredText and built using Sphinx::

  $ cd doc
  $ make html
