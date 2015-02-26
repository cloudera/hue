=================
How to contribute
=================

We gladly accept outside contributions. We use our
`Github issue tracker <https://github.com/python-zk/kazoo/issues>`_
for both discussions and talking about new features or bugs. You can
also fork the project and sent us a pull request. If you have a more
general topic to discuss, the
`user@zookeeper.apache.org <https://zookeeper.apache.org/lists.html>`_
mailing list is a good place to do so. You can sometimes find us on
IRC in the
`#zookeeper channel on freenode <https://zookeeper.apache.org/irc.html>`_.


Development
===========

If you want to work on the code and sent us a
`pull request <https://help.github.com/articles/using-pull-requests>`_,
first fork the repository on github to your own account. Then clone
your new repository and run the build scripts::

    git clone git@github.com:<username>/kazoo.git
    cd kazoo
    make
    make zookeeper

You need to have some supported version of Python installed and have
it available as ``python`` in your shell. To run Zookeeper you also
need a Java runtime (JRE or JDK) version 6 or 7.

You can run all the tests by calling::

    make test

Or to run individual tests::

    export ZOOKEEPER_PATH=/<path to current folder>/bin/zookeeper/
    bin/nosetests -s -d kazoo.tests.test_client:TestClient.test_create

The nose test runner allows you to filter by test module, class or
individual test method.

If you made changes to the documentation, you can build it locally::

    make html

And then open ``./docs/_build/html/index.html`` in a web browser to
verify the correct rendering.


Submitting changes
==================

We appreciate getting changes sent as pull requests via github. We have
travis-ci set up, which will run all tests on all supported version
combinations for submitted pull requests, which makes it easy to see
if new code breaks tests on some weird version combination.

If you introduce new functionality, please also add documentation and
a short entry in the top-level ``CHANGES.rst`` file.


Adding Recipes
==============

New recipes are welcome, however they should include the status/maintainer
RST information so its clear who is maintaining the recipe. This does mean
that if you submit a recipe for inclusion with Kazoo, you should be ready
to support/maintain it, and address bugs that may be found.

Ideally a recipe should have at least two maintainers.

Legal
=====

Currently we don't have any legal contributor agreement, so code
ownership stays with the original authors. The project is licensed
under the
`Apache License Version 2 <https://github.com/python-zk/kazoo/blob/master/LICENSE>`_.
