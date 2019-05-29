# Goal: Automate the builds and validation of changes

Be fast and simple:

* Cloud based
* 100% automated
* Below 5 minutes for basic unit tests (API and UI)
* Prepare the ground for other components
* Eventually lock master branch

## What to validate

### Python

Similar to the [Docker Hue](/tools/docker/hue). Currently doing only Python 2, but we should test the Python 3 build and run the tests.

* Python 2.7
* Python 3.5+

The docker images could be forked for QA and comes with a series of flags.

### Documentation

By updating the makefile to build the new [Website](/docs/docs-site). Would need to install Hugo and [build it](http://cloudera.github.io/hue/latest/developer/development/#documentation).

Step 2 would be to setup so that the documentation would get published automatically.

### Release

`make prod` should work, and the tarball release should be automatically installed and checked if boots normally.

### Docker images

Building the images: [Docker](/tools/docker/).
Ideally the images should then be sent to demo.gethue.com for deployment and reverted in case of issues.

## Tests

Those could be broken into several categories and labelled accordingly:

* Unit tests `unit`
* Integration tests (testing a certain connector would involve a live URL or booting its k8s service) `integration`
  * Hive `hive`
  * Impala
  * HDFS
  * MySQL...
* Frontend tests `frontend`
* Migration tests `migration`

Those tests would run on:

* master branch
* testing branch
* pull requests

## More quality metrics

Several areas to track:

* js
* linting (and missing tests, warnings added)
* Coverage
* MyPy

# Proposal

Investigate:

* Cloud based: https://circleci.com currently (free for open source, easy to use)
* Docker based CI (e.g. [CI in Docker](https://itnext.io/shift-your-ci-scripts-to-docker-build-92453bca9f75)...)
* [Tox](https://tox.readthedocs.io)
* Build and Makefile refactoring with standard `requirement.txt` and pypy package
* git clone under 10s
* Unit tests under 5min

Starting with these basic steps:

* Report the runs via UI and github checks
* Split the tests into several categories
  * unit Python
  * integrations
  * js
