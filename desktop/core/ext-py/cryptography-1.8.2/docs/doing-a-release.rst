Doing a release
===============

Doing a release of ``cryptography`` requires a few steps.

Verifying and upgrading OpenSSL version
---------------------------------------

The release process uses a static build for Windows and OS X wheels. Check that
the Windows and OS X Jenkins builders have the latest version of OpenSSL
installed before performing the release. If they do not:

Upgrading Windows
~~~~~~~~~~~~~~~~~

Run the ``openssl-release-1.1`` Jenkins job, then copy the resulting artifacts
to the Windows builders and unzip them in the root of the file system.

Upgrading OS X
~~~~~~~~~~~~~~

``brew update`` and then ``brew upgrade openssl@1.1 --build-bottle`` to
install a 64-bit only library compatible with all Intel Macs.

Bumping the version number
--------------------------

The next step in doing a release is bumping the version number in the
software.

* Update the version number in ``src/cryptography/__about__.py``.
* Update the version number in ``vectors/cryptography_vectors/__about__.py``.
* Set the release date in the :doc:`/changelog`.
* Do a commit indicating this.
* Send a pull request with this.
* Wait for it to be merged.

Performing the release
----------------------

The commit that merged the version number bump is now the official release
commit for this release. You will need to have ``gpg`` installed and a ``gpg``
key in order to do a release. Once this has happened:

* Run ``invoke release {version}``.

The release should now be available on PyPI and a tag should be available in
the repository.

Verifying the release
---------------------

You should verify that ``pip install cryptography`` works correctly:

.. code-block:: pycon

    >>> import cryptography
    >>> cryptography.__version__
    '...'
    >>> import cryptography_vectors
    >>> cryptography_vectors.__version__
    '...'

Verify that this is the version you just released.

For the Windows wheels check the builds for the ``cryptography-wheel-builder``
job and verify that the final output for each build shows it loaded and linked
the expected OpenSSL version.

Post-release tasks
------------------

* Update the version number to the next major (e.g. ``0.5.dev1``) in
  ``cryptography/__about__.py`` and
  ``vectors/cryptography_vectors/__about__.py``.
* Close the `milestone`_ for the previous release on GitHub.
* Add new :doc:`/changelog` entry with next version and note that it is under
  active development
* Send a pull request with these items
* Check for any outstanding code undergoing a deprecation cycle by looking in
  ``cryptography.utils`` for ``DeprecatedIn**`` definitions. If any exist open
  a ticket to increment them for the next release.
* Send an email to the `mailing list`_ and `python-announce`_ announcing the
  release.

.. _`milestone`: https://github.com/pyca/cryptography/milestones
.. _`mailing list`: https://mail.python.org/mailman/listinfo/cryptography-dev
.. _`python-announce`: https://mail.python.org/mailman/listinfo/python-announce-list
