Contributing
============

First of all, thank you for your interest in contributing to pyOpenSSL!
This project has no company backing its development therefore we're dependent on help by the community.


Filing bug reports
------------------

Bug reports are very welcome.
Please file them on the `GitHub issue tracker`_.
Good bug reports come with extensive descriptions of the error and how to reproduce it.
Reporters are strongly encouraged to include an `short, self contained, correct example <http://www.sscce.org/>`_.


Patches
-------

All patches to pyOpenSSL should be submitted in the form of pull requests to the main pyOpenSSL repository, `pyca/pyopenssl`_.
These pull requests should satisfy the following properties:


Code
^^^^

- The pull request should focus on one particular improvement to pyOpenSSL.
  Create different pull requests for unrelated features or bugfixes.
- Code should follow `PEP 8`_, especially in the "do what code around you does" sense.
  Follow OpenSSL naming for callables whenever possible is preferred.
- Pull requests that introduce code must test all new behavior they introduce as well as for previously untested or poorly tested behavior that they touch.
- Pull requests are not allowed to break existing tests.
  We usually don't comment on pull requests that are breaking the CI because we consider them work in progress.
  Please note that not having 100% code coverage for the code you wrote/touched also causes our CI to fail.


Documentation
^^^^^^^^^^^^^

When introducing new functionality, please remember to write documentation.

- New functions and methods should have a docstring describing what they do, what parameters they takes, what types those parameters are, and what they return.

  .. code-block:: python

     def dump_publickey(type, pkey):
         """
         Dump a public key to a buffer.

         :param type: The file type (one of :data:`FILETYPE_PEM` or
             :data:`FILETYPE_ASN1`).
         :param PKey pkey: The PKey to dump.

         :return: The buffer with the dumped key in it.
         :rtype: bytes
         """


  Don't forget to add an ``.. auto(function|class|method)::`` statement to the relevant API document found in ``doc/api/`` to actually add your function to the Sphinx documentation.
- Do *not* use ``:py:`` prefixes when cross-linking (Python is default).
  Do *not* use the generic ``:data:`` or ``:obj:``.
  Instead use more specific types like ``:class:``, ``:func:`` or ``:meth:`` if applicable.
- Pull requests that introduce features or fix bugs should note those changes in the CHANGELOG.rst_ file.
  Please add new entries to the *top* of the *current* Changes section followed by a line linking to the relevant pull request:

  .. code-block:: rst

     - Added ``OpenSSL.crypto.some_func()`` to do something awesome.
       [`#1 <https://github.com/pyca/pyopenssl/pull/1>`_]


- Use `semantic newlines`_ in reStructuredText_ files (files ending in ``.rst``).


Review
------

Finally, pull requests must be reviewed before merging.
This process mirrors the `cryptography code review process`_.
Everyone can perform reviews; this is a very valuable way to contribute, and is highly encouraged.

Pull requests are merged by `members of PyCA`_.
They should, of course, keep all the requirements detailed in this document as well as the ``pyca/cryptography`` merge requirements in mind.

The final responsibility for the reviewing of merged code lies with the person merging it.
Since pyOpenSSL is a sensitive project from a security perspective, reviewers are strongly encouraged to take this review and merge process very seriously.


Finding Help
------------

If you need any help with the contribution process, you'll find us hanging out at ``#cryptography-dev`` on Freenode_ IRC.
You can also ask questions on our `mailing list`_.

Please note that this project is released with a Contributor `Code of Conduct`_.
By participating in this project you agree to abide by its terms.


Security
--------

If you feel that you found a security-relevant bug that you would prefer to discuss in private, please send us a GPG_-encrypted e-mail.

The maintainer can be reached at hs@ox.cx and his GPG key ID is ``0xAE2536227F69F181`` (Fingerprint: ``C2A0 4F86 ACE2 8ADC F817  DBB7 AE25 3622 7F69 F181``).
Feel free to cross-check this information with Keybase_.


.. _GitHub issue tracker: https://github.com/pyca/pyopenssl/issues
.. _GPG: https://en.wikipedia.org/wiki/GNU_Privacy_Guard
.. _Keybase: https://keybase.io/hynek
.. _pyca/pyopenssl: https://github.com/pyca/pyopenssl
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _cryptography code review process: https://cryptography.io/en/latest/development/reviewing-patches/
.. _freenode: https://freenode.net
.. _mailing list: https://mail.python.org/mailman/listinfo/cryptography-dev
.. _members of PyCA: https://github.com/orgs/pyca/people
.. _semantic newlines: http://rhodesmill.org/brandon/2012/one-sentence-per-line/
.. _reStructuredText: http://sphinx-doc.org/rest.html
.. _CHANGELOG.rst: https://github.com/pyca/pyopenssl/blob/master/CHANGELOG.rst
.. _`Code of Conduct`: https://github.com/pyca/pyopenssl/blob/master/CODE_OF_CONDUCT.rst
