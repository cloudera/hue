---
title: Improving the developer productivity with some Continuous Integration
author: admin
type: post
date: 2019-06-12T17:16:31+00:00
url: /improving-the-developer-productivity-with-some-continuous-integration/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
  # - Version 4.5

---
Tooling and automation has been simplified dramatically with technologies like [Docker][1] and the Cloud. On top of this, continuous integration companies like [Circle CI][2] and [Travis CI][3] have added one more layer of simplicity.

## Background


  <a href="https://gethue.com/">Hue</a>&#8216;s scope has been pretty wide (ranging from SQL parsers to CSS to scheduling jobs or querying any type of databases&#8230;) and the increase of external contributions has made the previous <a href="https://gethue.com/the-hue-team-development-process/">Development process</a> outdated. It was becoming frequent to brake the master branch with errors or not making easy for developer to contribute by asking to manual run the test suite. It was time to modernize the development experience!


## Goals

  * Automate all the test runs and remove the manual steps burden of the contributors
  * Forbid to push code that breaks tests
  * Keep the overall runs below 10min and closer to 5min (the less friction, the better)
  * Keep it simple

## Picking up a CI infrastructure


  <a href="https://en.wikipedia.org/wiki/Continuous_integration">Continuous Integration</a> (CI) is a mean to automate checks on developer changes. The team looked at three separate systems:


  * Build our own in Docker images and Jenkins
  * Travis CI
  * Circle CI


  The goal was to minimized the time spent on the setups while providing a maximum of automation to the developers. Influential open source projects like <a href="https://github.com/kubernetes/kubernetes">Kubernetes</a> were also looked at for inspiration. We played with Travis CI and Circle CI and found Circle CI free open source plan clear and interface pretty easy to use (literally 5 minutes to get a first pipeline started). The documentation was good even if mostly only needed for more advanced automation points (e.g. automatically pushing commits to the master branch). The paying plans seemed also fair, even if we would not need it as Hue is <a href="https://github.com/cloudera/hue">open source</a>.



## Integrating the CI to Github


  On the Github side, these steps below were added to the project configuration. Circle CI was also authorized to access the repository.


  * Protect master branch
  * Require Circle CI check
  * Require pushed branch to be up to date with master


  <a href="https://cdn.gethue.com/uploads//2019/06/github_protect_branch.png"><img src="https://cdn.gethue.com/uploads/2019/06/github_protect_branch.png" /></a>


On the Circle side:

For historical reason, traditional `pip install` of requirements is not possible yet in Hue. For the record, this will be cleaner after the migration to Python 3 support [HUE-8737][4]. In the meantime, the Hue docker base image is pulled, the repository is checked out and the Python and JavaScript code changes are applied to the image. Here is the [Circle CI configuration][5].

On the Hue side, here are the current checks:

[<img src="https://cdn.gethue.com/uploads/2019/06/ci_full_run.png" />][6]

### Python tests

> <div style="text-align: center;">
>   Ran 641 tests in 131.800s
> </div>

### JavaScript tests

> <div style="text-align: center;">
>   2289 specs, 0 failures, 10 pending specs
> </div>
>
> <div style="text-align: center;">
>   Finished in 5.627 seconds
> </div>

### JavaScript linting

> <div style="text-align: center;">
>   15s
> </div>

## Pull requests

Pull requests (PR) automatically gets the test suite and code analysis ran for them. It shows up directly within the PR page:


[<img src="https://cdn.gethue.com/uploads/2019/06/pr_ci_checks.png" />][7]

## Automatic pushes

First the process required developers to push to a branch, then push again to the master branch. This was cumbersome as it was easy to forget to push to master, was a redundant steps and easier to get into conflicts as someone might push some other commits to master in the meantime.

<div>
</div>

<div>
</div>

Via Circle CI workflows, and only on some dedicated branches, the commits are now automatically pushed to master if the test passes. Regular test branches can still be used and we also took the opportunity to disable the duplicate re-run of the test on the master branch:

<div>
</div>

<div>
  <a href="https://cdn.gethue.com/uploads/2019/06/ci_workflow_test_push.png"><img src="https://cdn.gethue.com/uploads/2019/06/ci_workflow_test_push.png" /></a>
</div>

&nbsp;

## Results

So far the time invested (~1 week) is already paid back after less than a month. Developer likes the ease of use and the lead does not need to police and revert commits breaking the master branch. Accepting [external contribution][8] has been facilitated too. Developer are even asking for integrating more checks like linting and code coverage.


As the core is now there, it is easy to iteratively add more functionalities to save even more time going forward. For example by adding steps to build Docker images, check Python 2 and 3 compatibility, add Python test coverage checks, start having integration tests or publish documentation changes automatically. Also with some more tweaks on the image we could shave off 1 or 2 minutes of run time.


To finish, here is an example of a [CI run][9]. If you also want to play with SQL, just open-up [demo.gethue.com][10].


What is your favorite CI process? Any feedback? Feel free to comment here or on <a href="https://twitter.com/gethue">@gethue</a>!


 [1]: https://www.docker.com/
 [2]: https://circleci.com/
 [3]: https://travis-ci.org/
 [4]: https://issues.cloudera.org/browse/HUE-8737
 [5]: https://github.com/cloudera/hue/blob/master/.circleci/config.yml#L45
 [6]: https://cdn.gethue.com/uploads/2019/06/ci_full_run.png
 [7]: https://cdn.gethue.com/uploads/2019/06/pr_ci_checks.png
 [8]: https://github.com/cloudera/hue/blob/master/docs/CONTRIBUTING.md
 [9]: https://circleci.com/gh/cloudera/hue/tree/ci-commit-master-romain
 [10]: http://demo.gethue.com
