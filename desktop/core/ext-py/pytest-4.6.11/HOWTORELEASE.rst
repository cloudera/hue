Release Procedure
-----------------

Our current policy for releasing is to aim for a bugfix every few weeks and a minor release every 2-3 months. The idea
is to get fixes and new features out instead of trying to cram a ton of features into a release and by consequence
taking a lot of time to make a new one.

.. important::

    pytest releases must be prepared on **Linux** because the docs and examples expect
    to be executed in that platform.

#. Create a branch ``release-X.Y.Z`` with the version for the release.

   * **patch releases**: from the latest ``master``;

   * **minor releases**: from the latest ``features``; then merge with the latest ``master``;

   Ensure your are in a clean work tree.

#. Using ``tox``, generate docs, changelog, announcements::

    $ tox -e release -- <VERSION>

   This will generate a commit with all the changes ready for pushing.

#. Open a PR for this branch targeting ``master``.

#. After all tests pass and the PR has been approved, publish to PyPI by pushing the tag::

     git tag <VERSION>
     git push git@github.com:pytest-dev/pytest.git <VERSION>

   Wait for the deploy to complete, then make sure it is `available on PyPI <https://pypi.org/project/pytest>`_.

#. Merge the PR into ``master``.

#. Send an email announcement with the contents from::

     doc/en/announce/release-<VERSION>.rst

   To the following mailing lists:

   * pytest-dev@python.org (all releases)
   * python-announce-list@python.org (all releases)
   * testing-in-python@lists.idyll.org (only major/minor releases)

   And announce it on `Twitter <https://twitter.com/>`_ with the ``#pytest`` hashtag.
