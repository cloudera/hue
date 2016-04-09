Contributing
============

First of all, thank you for your interest in contributing to pyOpenSSL!

Filing bug reports
------------------

Bug reports are very welcome.
Please file them on the Github issue tracker.
Good bug reports come with extensive descriptions of the error and how to reproduce it.
Reporters are strongly encouraged to include an `short, self contained, correct example <http://www.sscce.org/>`_.

Patches
-------

All patches to pyOpenSSL should be submitted in the form of pull requests to the main pyOpenSSL repository, ``pyca/pyopenssl``.
These pull requests should satisfy the following properties:

- The branch referenced should be a `feature branch`_ focusing on one particular improvement to pyOpenSSL.
  Create different branches and different pull requests for unrelated features or bugfixes.
- The branch referenced should have a distinctive name (in particular, please do not open pull requests for your ``master`` branch).
- Code should follow `PEP 8`_, especially in the "do what code around you does" sense.
  One notable way pyOpenSSL code differs, for example, is that there should be three empty lines between module-level elements,and two empty lines between class-level elements.
  Methods and functions are named in ``snake_case``.
  Follow OpenSSL naming for callables whenever possible is preferred.
- Pull requests that introduce code must test all new behavior they introduce as well as for previously untested or poorly tested behavior that they touch.
- Pull requests are not allowed to break existing tests.
- Pull requests that introduce features or fix bugs should note those changes in the ``ChangeLog`` text file in the root of the repository.
  They should also document the changes, both in docstrings and in the documentation in the ``doc/`` directory.

Finally, pull requests must be reviewed before merging.
This process mirrors the `cryptography code review process`_.
Everyone can perform reviews; this is a very valuable way to contribute, and is highly encouraged.

Pull requests are merged by members of the `pyopenssl-committers team <https://github.com/orgs/pyca/teams/pyopenssl-committers>`_.
They should, of course, keep all the requirements detailed in this document as well as the pyca/cryptography merge requirements in mind.

The final responsibility for the reviewing of merged code lies with the person merging it; since pyOpenSSL is obviously a sensitive project from a security perspective, so reviewers are strongly encouraged to take this review and merge process very seriously.

.. _PEP 8: http://legacy.python.org/dev/peps/pep-0008/
.. _cryptography code review process: https://cryptography.io/en/latest/development/reviewing-patches/
.. _feature branch: http://nvie.com/posts/a-successful-git-branching-model/
