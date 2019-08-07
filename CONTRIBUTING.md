![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")


The Hue project gladly welcomes [pull requests](https://github.com/cloudera/hue/pulls)!

This document contains instructions on how to help get involved with Hue.

In any case, feel free to ask here, on [hue-user](http://groups.google.com/a/cloudera.org/group/hue-user) or [@gethue](https://twitter.com/gethue).

# Getting Started

1. Have a look at [how to build Hue](https://github.com/cloudera/hue#getting-started).
2. High level [Roadmap](/docs/ROADMAP.md). Updating a small piece if [documentation](https://docs.gethue.com) is also a quick way to get familiar.
3. [JIRA](https://issues.cloudera.org/browse/HUE) is the bug tracking system as well as [Github issues](https://github.com/cloudera/hue/issues).

Here are some example of changes:

* [Pull request 842](https://github.com/cloudera/hue/pull/842)
* [HUE-8802 [search] Deleting an index throws a js exception](https://issues.cloudera.org/browse/HUE-8802)

# Submitting an improvement

## Reviews

It is flexible on how to do code reviews and send patches:

* Github Pull request.
Prefered way. Just post the [pull request](https://github.com/cloudera/hue/pulls) and reviewers will start from there. The CI will run a bsic set of tests for you.
* Review Board.
For large changes. Create an account on Hue's [Review Board](https://review.cloudera.org/groups/hue).
Post the patch against the "hue-rw" repository. Enter "hue" in the "groups" field.
Example: [https://review.cloudera.org/r/4019/](https://review.cloudera.org/r/4019/)

Blog posts about using [Code Reviews](http://gethue.com/rbtools-example-how-do-easily-do-code-reviews-with-review-board/) and the [extended process](http://gethue.com/the-hue-team-development-process/).


## Coding Style

A general rule is to follow the on-going style of the code context.

* Python: Follow [Django/PEP8](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/), with the exception of using 2 spaces per indent level.
* JavaScript: Follow the style in this [file](https://github.com/cloudera/hue/blob/master/apps/oozie/src/oozie/static/oozie/js/bundle-editor.ko.js#L18).

## Tests

See the [Running the tests locally](https://docs.gethue.com/latest/developer/development/#testing) or opening-up a pull request will automatically run them via [CircleCi](https://circleci.com/gh/cloudera/hue).
