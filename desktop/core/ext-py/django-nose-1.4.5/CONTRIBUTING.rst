============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/django-nose/django-nose/issues.

If you are reporting a bug, please include:

* The version of django, nose, and django-nose you are using, and any other
  applicable packages (``pip freeze`` will show current versions)
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

When someone submits a pull request to fix your bug, please try it out and
report if it worked for you.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything untagged or tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything untagged ot tagged with
"feature" is open to whoever wants to implement it.

django-nose is built on nose, which supports plugins.  Consider implementing
your feature as a plugin, maintained by the community using that feature,
rather than adding to the django-nose codebase.

Write Documentation
~~~~~~~~~~~~~~~~~~~

django-nose could always use more documentation, whether as part of the
official django-nose, as code comments, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at 
https://github.com/django-nose/django-nose/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up django-nose
for local development.

1. Fork the `django-nose` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/django-nose.git

3. Install your local copy into a virtualenv. Assuming you have
   virtualenvwrapper installed, this is how you set up your fork for local
   development::

    $ mkvirtualenv django-nose
    $ cd django-nose/
    $ pip install -r requirements.txt
    $ ./manage.py migrate

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. Make sure existing tests continue to pass with your new code::

   $ make qa

6. When you're done making changes, check that your changes pass flake8 and the
   tests, including testing other Python versions with tox::

    $ make qa-all

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should be in a branch.
2. The pull request should include tests.
3. You agree to license your contribution under the BSD license.
4. If the pull request adds functionality, the docs should be updated.
5. Make liberal use of `git rebase` to ensure clean commits on top of master.
6. The pull request should pass QA tests and work for supported Python / Django
   combinations.  Check
   https://travis-ci.org/django-nose/django-nose/pull_requests
   and make sure that the tests pass for all supported Python versions.

Tips
----

The django-nose testapp uses django-nose, so all of the features are available.
To run a subset of tests::

    $ ./manage.py test testapp/tests.py

To mark failed tests::

    $ ./manage.py test --failed

To re-run only the failed tests::

    $ ./manage.py test --failed

