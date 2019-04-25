Goal: Automate the builds and validation of changes

## What to validate

### Python

Similar to the [Docker Hue](/tools/docker/hue). Currently doing only Python 2, but we should test the Python 3 build and run the tests.

* Python 2.7
* Python 3

The docker images could be forked for QA and comes with a series of flags.

### Documentation

By updating the makefile to build the new [Website](/docs/docs-site). Would need to install Hugo and [http://cloudera.github.io/hue/latest/developer/development/#documentation](build it).

Step 2 would be to setup so that the doc get [published automatically](https://docs.travis-ci.com/user/deployment/pages/).

### Release

[`make prod`](make prod) should work, and the tarball release should be automatically installed and checked if boots normally.

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

* js and py lint
* code coverage

# Proposal

Investigate:

* Docker based CI (e.g. [CI in Docker](https://itnext.io/shift-your-ci-scripts-to-docker-build-92453bca9f75)...)

Starting with these basic steps:

* Running an hourly master build if there are changes
* Report the runs similarly to Jenkins. Pick one of Jenkins, Travis CI, Github Action...
* Split the tests into several categories
* Add the unit tests only to the hourly run
