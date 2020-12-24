![alt text](https://raw.githubusercontent.com/cloudera/hue/master/docs/images/hue_logo.png "Hue Logo")


The Hue project gladly welcomes [pull requests](https://github.com/cloudera/hue/pulls)!

This document contains instructions on how to get involved in Hue improvement.

In any case, feel free to ask here, on the [forum](https://discourse.gethue.com/) or [@gethue](https://twitter.com/gethue).

# What to improve

Here is some inspiration on which areas we would love to have some contributions:

1. Updating a small piece of [documentation](https://docs.gethue.com)
2. High level [Roadmap](/docs/ROADMAP.md)
3. Check [Github issues](https://github.com/cloudera/hue/issues) or [the bug tracking system](https://issues.cloudera.org/browse/HUE)
4. Improving or creating SQL [autocompletes](https://docs.gethue.com/developer/parsers/) or [connectors](https://docs.gethue.com/developer/sdk/) are great projects

# Submitting an improvement

Here are some examples of changes:

* [Pull request 842](https://github.com/cloudera/hue/pull/842)
* [HUE-8802 [search] Deleting an index throws a js exception](https://issues.cloudera.org/browse/HUE-8802)

## Building

Have a look at [how to quick build](https://docs.gethue.com/developer/development/#build-start).

## Reviews

It is flexible but Github Pull request are handy.

Just post the [pull request](https://github.com/cloudera/hue/pulls) and reviewers will start from there. The CI will run a basic set of tests for you.

## Coding Style

A general rule is to follow the on-going style of the code context.

* Python: Follow [Django/PEP8](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/), with the exception of using 2 spaces per indent level
* JavaScript: Check the [EsLint](https://github.com/cloudera/hue/blob/master/.eslintrc.js) style

## CI & Tests

See how to automatically [run the tests](https://docs.gethue.com/developer/development/#testing) via [CircleCi](https://circleci.com/gh/cloudera/hue) by pushing to a branch or opening-up a pull request.
