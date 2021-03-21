# Contribution Guidelines

We gladly accept outside contributions. We use our
[Github issue tracker](https://github.com/python-zk/kazoo/issues)
for both discussions and talking about new features or bugs. You can
also fork the project and sent us a pull request. If you have a more
general topic to discuss, the
[user@zookeeper.apache.org](https://zookeeper.apache.org/lists.html)
mailing list is a good place to do so. You can sometimes find us on
IRC in the
[#zookeeper channel on freenode](https://zookeeper.apache.org/irc.html).

[See the README](/README.rst) for contact information.

## Development

If you want to work on the code and send us a
[pull request](https://help.github.com/articles/using-pull-requests),
first fork the repository on github to your own account. Then clone
your new repository and run the build scripts:

```
    git clone git@github.com:<username>/kazoo.git
    cd kazoo
    make
```

You need a supported version of Python installed and available as `python`
in your shell. To run Zookeeper you also need a Java runtime (JRE or JDK).
Please refer to the Zookeeper documentation for compatible Java versions for
each Zookeeper version. To run tests, you need to have `tox`, the Python
testing tool, installed in your shell.

You can run all the tests by calling:

```
    make test
```

Or to run individual tests:

```
    export ZOOKEEPER_PATH=/<path to current folder>/bin/zookeeper/
    bin/pytest -v kazoo/tests/test_client.py::TestClient::test_create
```

The pytest test runner allows you to filter by test module, class or
individual test method.

If you made changes to the documentation, you can build it locally:

```
    make html
```

And then open `./docs/_build/html/index.html` in a web browser to
verify the correct rendering.


## Bug Reports

You can file issues here on GitHub. Please try to include as much information as
you can and under what conditions you saw the issue.

## Adding Recipes

New recipes are welcome, however they should include the status/maintainer
RST information so its clear who is maintaining the recipe. This means
that if you submit a recipe for inclusion with Kazoo, you should be ready
to support/maintain it, and address bugs that may be found.

Ideally a recipe should have at least two maintainers.

## Sending Pull Requests

Patches should be submitted as pull requests (PR).

Before submitting a PR:
- Your code must run and pass all the automated tests before you submit your PR
  for review. "Work in progress" pull requests are allowed to be submitted, but
  should be clearly labeled as such and should not be merged until all tests
  pass and the code has been reviewed.
- Your patch should include new tests that cover your changes. It is your and
  your reviewer's responsibility to ensure your patch includes adequate tests.

When submitting a PR:
- You agree to license your code under the project's open source license
  ([APL 2.0](/LICENSE)).
- Base your branch off the current `master`.
- Add both your code and new tests if relevant.
- Sign your git commit.
- Run the test suite to make sure your code passes linting and tests.
- Ensure your changes do not reduce code coverage of the test suite.
- Please do not include merge commits in pull requests; include only commits
  with the new relevant code.


## Code Review

This project is production Mozilla code and subject to our [engineering practices and quality standards](https://developer.mozilla.org/en-US/docs/Mozilla/Developer_guide/Committing_Rules_and_Responsibilities). Every patch must be peer reviewed.

## Git Commit Guidelines

We loosely follow the [Angular commit guidelines](https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md#type)
of `<type>(scope): <subject>` where `type` must be one of:

* **feat**: A new feature
* **fix**: A bug fix
* **docs**: Documentation only changes
* **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing
  semi-colons, etc)
* **refactor**: A code change that neither fixes a bug or adds a feature
* **perf**: A code change that improves performance
* **test**: Adding missing tests
* **chore**: Changes to the build process or auxiliary tools and libraries such as documentation
  generation

Scope may be left off if none of these components are applicable:

* **core**: Core client/connection handling
* **recipe**: Changes/Fixes/Additions to recipes

### Subject

The subject contains succinct description of the change:

* use the imperative, present tense: "change" not "changed" nor "changes"
* don't capitalize first letter
* no dot (.) at the end

### Body

In order to maintain a reference to the context of the commit, add
`closes #<issue_number>` if it closes a related issue or `issue #<issue_number>`
if it's a partial fix.

You can also write a detailed description of the commit. Just as in the
**subject**, use the imperative, present tense: "change" not "changed" nor
"changes". Please include the motivation for the change and contrast this with
previous behavior.

### Footer

The footer should contain any information about **Breaking Changes** and is also
the place to reference GitHub issues that this commit **Closes**.

### Example

A properly formatted commit message should look like:

```
feat(core): add tasty cookies to the client handler

Properly formatted commit messages provide understandable history and
documentation. This patch will provide a delicious cookie when all tests have
passed and the commit message is properly formatted.

BREAKING CHANGE: This patch requires developer to lower expectations about
    what "delicious" and "cookie" may mean. Some sadness may result.

Closes #3.14, #9.75
```

# Legal

Currently we don't have any legal contributor agreement, so code
ownership stays with the original authors.
