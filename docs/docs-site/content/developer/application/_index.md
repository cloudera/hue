---
title: "Applications"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 5
---

Building a brand new application is more work but is ideal for creating a custom solution.

## Introduction and Overview

Hue leverages the browser to provide users with an environment for exploring
and analyzing data.

Build on top of the Hue SDK to enable your application to interact efficiently with
Hadoop and the other Hue services.

By building on top of Hue SDK, you get, out of the box:

+ Configuration Management
+ Hadoop interoperability
+ Supervision of subprocesses
+ A collaborative UI
+ Basic user administration and authorization

This document will orient you with the general structure of Hue
and will walk you through adding a new application using the SDK.


### From 30,000 feet

![From up on high](/images/from30kfeet.png)

Hue, as a "container" web application, sits in between your Hadoop installation
and the browser.  It hosts all the Hue Apps, including the built-in ones, and
ones that you may write yourself.

### The Hue Server

![Web Back-end](/images/webbackend.png)

Hue is a web application built on the Django python web framework.
Django, running on the WSGI container/web server (typically CherryPy), manages
the url dispatch, executes application logic code, and puts together the views
from their templates.  Django uses a database (typically sqlite)
to manage session data, and Hue applications can use it as well
for their "models".  (For example, the saved Editor stores
saved queries in the database.)

In addition to the web server, some Hue applications run
daemon processes "on the side". Some examples are the `Celery Task Server`, `Celery Beat`.

### Interacting with Hadoop

![Interacting with Hadoop](/images/interactingwithhadoop.png)

Hue provides some APIs for interacting with Hadoop.
Most noticeably, there are python file-object-like APIs for
interacting with HDFS.  These APIs work by making REST API or Thrift calls
the Hadoop daemons. The Hadoop administrator must enable these interfaces from
Hadoop.

### On the Front-End

Hue provides a front-end framework based on
[Bootstrap](http://twitter.github.com/bootstrap/) and
[Knockout js](http://knockoutjs.com/).


### An Architectural View

![Architecture](/images/architecture.png)

A Hue application may span three tiers: (1) the UI
and user interaction in the client's browser, (2) the
core application logic in the Hue web
server, and (3) external services with which applications
may interact.

The absolute minimum that you must implement (besides
boilerplate), is a
"Django [view](https://docs.djangoproject.com/en/1.11/#the-view-layer/)"
function that processes the request and the associated template
to render the response into HTML.

Many apps will evolve to have a bit of custom JavaScript and
CSS styles. Apps that need to talk to an external service
will pull in the code necessary to talk to that service.

### File Layout

The Hue "framework" is in ``desktop/core/`` and contains the Web components.
``desktop/libs/`` is the API for talking to various Hadoop services.
The installable apps live in ``apps/``.  Please place third-party dependencies in the app's ext-py/
directory.

The typical directory structure for inside an application includes:
```
  src/
    for Python/Django code
      models.py
      urls.py
      views.py
      forms.py
      settings.py

  conf/
    for configuration (``.ini``) files to be installed

  static/
    for static HTML/js resources and help doc

  templates/
    for data to be put through a template engine

  locales/
    for localizations in multiple languages
```

For the URLs within your application, you should make your own ``urls.py``
which will be automatically rooted at ``/yourappname/`` in the global
namespace. See ``apps/about/src/about/urls.py`` for an example.


## Pre-requisites


### Dependencies

* The OS specific dependencies listed [here](http://cloudera.github.io/hue/latest/admin-manual/manual.html)
* Python 2.7
* Django (1.11 included with our distribution)
* Hadoop (Apache Hadoop 2+)
* Java (Java 1.8)
* npm (6.4+)

### Recommended Reading / Important Technologies

The following are core technologies used inside of Hue.

* Python.  <a href="http://diveintopython.net/">Dive Into Python</a> is one of
  several excellent books on python.
* Django.  Start with [The Django Tutorial](https://docs.djangoproject.com/en/1.11/intro/).
* [Thrift](http://incubator.apache.org/thrift/) is used for communication
  between daemons.
* [Mako](http://www.makotemplates.org/) is the preferred templating language.

## Fast-Guide to Creating a New Hue Application

Now that we have a high-level overview of what's going on,
let's go ahead and create a new installation.

### Download, Unpack, Build Distro

The Hue SDK is available from [Github](http://github.com/cloudera/hue). Releases
can be found on the [download page](http://gethue.com/category/release/).
Releases are missing a few dependencies that could not be included because of
licencing issues. So if you prefer to have an environment ready from scratch,
it is preferable to checkout a particular release tag instead.

    cd hue
    ## Build
    make apps
    ## Run
    build/env/bin/hue runserver
    ## Alternative run
    build/env/bin/hue supervisor
    ## Visit http://localhost:8000/ with your web browser.


### Run "create_desktop_app" to Set up a New Source Tree

    ./build/env/bin/hue create_desktop_app calculator
    find calculator -type f
    calculator/setup.py                                 # distutils setup file
    calculator/src/calculator/__init__.py               # main src module
    calculator/src/calculator/forms.py
    calculator/src/calculator/models.py
    calculator/src/calculator/settings.py               # app metadata setting
    calculator/src/calculator/urls.py                   # url mapping
    calculator/src/calculator/views.py                  # app business logic
    calculator/src/calculator/templates/index.mako
    calculator/src/calculator/templates/shared_components.mako

    # Static resources
    calculator/src/static/calculator/art/calculator.png # logo
    calculator/src/static/calculator/css/calculator.css
    calculator/src/static/calculator/js/calculator.js


<div class="note">
  Some apps are blacklisted on certain versions of CDH (such as the 'Spark' app) due to
  certain incompatibilities, which prevent them loading from in Hue.
  Check the hue.ini 'app_blacklist' parameter for details.
</div>

### Install SDK Application

As you'll discover if you look at calculator's <tt>setup.py</tt>,
Hue uses a distutils <tt>entrypoint</tt> to
register applications.  By installing the calculator
package into Hue's python virtual environment,
you'll install a new app.  The "app_reg.py" tool manages
the applications that are installed. Note that in the following example, the value after the
"--install" option is the path to the root directory of the application you want to install. In this
example, it is a relative path to "/Users/philip/src/hue/calculator".

        ./build/env/bin/python tools/app_reg/app_reg.py --install calculator --relative-paths
        === Installing app at calculator
        Updating registry with calculator (version 0.1)
        --- Making egg-info for calculator


<div class="note">
  If you'd like to customize the build process, you can modify (or even complete
  rewrite) your own `Makefile`, as long as it supports the set of required
  targets. Please see `Makefile.sdk` for the required targets and their
  semantics.
</div>

Congrats, you've added a new app!

<div class="note">
  What was that all about?
  <a href="http://pypi.python.org/pypi/virtualenv">virtualenv</a>
  is a way to isolate python environments in your system, and isolate
  incompatible versions of dependencies.  Hue uses the system python, and
  that's about all.  It installs its own versions of dependencies.

  <a href="http://peak.telecommunity.com/DevCenter/PkgResources#entry-points">Entry Points</a>
  are a way for packages to optionally hook up with other packages.
</div>

You can now browse the new application.

    # If you haven't killed the old process, do so now.
    build/env/bin/hue runserver

And then visit <a href="http://localhost:8000">http://localhost:8000/</a> to check it out!
You should see the app in the left menu.


### Customizing Views and Templates

Now that your app has been installed, you'll want to customize it.
As you may have guessed, we're going to build a small calculator
application.  Edit `calculator/src/calculator/templates/index.mako`
to include a simple form and a Knockout viewmodel:


    <%!from desktop.views import commonheader, commonfooter %>
    <%namespace name="shared" file="shared_components.mako" />

    %if not is_embeddable:
    ${commonheader("Calculator", "calculator", user, "100px") | n,unicode}
    %endif

    ## Main body
    <div class="container-fluid calculator-components">
      <div class="row">
        <div class="span6 offset3 margin-top-30 text-center">
          <form class="form-inline">
            <input type="text" class="input-mini margin-right-10" placeholder="A" data-bind="value: a">
            <!-- ko foreach: operations -->
            <label class="radio margin-left-5">
              <input type="radio" name="op" data-bind="checkedValue: $data, checked: $parent.chosenOperation" /><span data-bind="text: $data"></span>
            </label>
            <!-- /ko -->
            <input type="text" class="input-mini margin-left-10" placeholder="B" data-bind="value: b">
            <button class="btn" data-bind="click: calculate">Calculate</button>
          </form>

          <h2 data-bind="visible: result() !== null">The result is <strong data-bind="text: result"></strong></h2>
        </div>
      </div>
    </div>

    <script>
      (function() {
        var CalculatorViewModel = function () {
          var self = this;

          self.operations = ko.observableArray(['+', '-', '*', '/']);

          self.a = ko.observable();
          self.b = ko.observable();
          self.chosenOperation = ko.observable('+');
          self.result = ko.observable(null);

          self.calculate = function () {
            var a = parseFloat(self.a());
            var b = parseFloat(self.b());
            var result = null;
            switch (self.chosenOperation()) {
              case '+':
                result = a + b;
                break;
              case '-':
                result = a - b;
                break;
              case '*':
                result = a * b;
                break;
              case '/':
                result = a / b;
            }
            self.result(result);
          }
        };
        $(document).ready(function () {
          ko.applyBindings(new CalculatorViewModel(), $('.calculator-components')[0]);
        });
      })();
    </script>

    %if not is_embeddable:
    ${commonfooter(messages) | n,unicode}
    %endif

The template language here is <a href="http://www.makotemplates.org/docs/">Mako</a>,
which is flexible and powerful.  If you use the "`.html`" extension, Hue
will render your page using
<a href="https://docs.djangoproject.com/en/1.11/#the-template-layer">Django templates</a>
instead.

Note that we use Knockout.js to do the heavy lifting of this app.

Let's edit `calculator/src/calculator/views.py` to simply render the page:

    #!/usr/bin/env python

    from desktop.lib.django_util import render

    def index(request):
      return render('index.mako', request, {
        'is_embeddable': request.GET.get('is_embeddable', False),
      })


You can now go and try the calculator.


# Testing

## The short story

Install the mini cluster (only once):

    ./tools/jenkins/jenkins.sh slow

Run all the tests:

    build/env/bin/hue test all

Or just some parts of the tests, e.g.:

    build/env/bin/hue test specific impala
    build/env/bin/hue test specific impala.tests:TestMockedImpala
    build/env/bin/hue test specific impala.tests:TestMockedImpala.test_basic_flow

Jasmine tests:

    npm run test


## Longer story

The ``test`` management command prepares the arguments (test app names)
and passes them to nose (django_nose.nose_runner). Nose will then magically
find all the tests to run.

Tests themselves should be named *_test.py.  These will be found
as long as they're in packages covered by django.  You can use the
unittest frameworks, or you can just name your method with
the word "test" at a word boundary, and nose will find it.
See apps/hello/src/hello/hello_test.py for an example.


### Helpful command-line tricks

To run tests that do not depend on Hadoop, use:

    build/env/bin/hue test fast

To run all tests, use:

    build/env/bin/hue test all

To run only tests of a particular app, use:

    build/env/bin/hue test specific <app>

E.g.
  build/env/bin/hue test specific filebrowser

To run a specific test, use:

    build/env/bin/hue test specific <test_func>

E.g.
  build/env/bin/hue test specific useradmin.tests:test_user_admin

Start up pdb on test failures:

    build/env/bin/hue test <args> --pdb --pdb-failure -s

Point to an Impalad and trigger the Impala tests:

    build/env/bin/hue test impala impalad-01.gethue.com


### Create and run the Jasmine tests

Add them in a "spec" subfolder relative to the file under test and the filename of the test has to end with "Spec.js".

    someFile.js              <- File under test
    ├── spec/
    │   ├── someFileSpec.js  <- File containing tests

Run all the tests once with:

    npm run test

Optionally to use Karma and headless chrome for the tests you can run

    npm run test-karma

See ```desktop/core/src/desktop/js/spec/karma.config.js``` for various options


### Special environment variables

    DESKTOP_LOGLEVEL=<level>
      level can be DEBUG, INFO, WARN, ERROR, or CRITICAL

      When specified, the console logger is set to the given log level. A console
      logger is created if one is not defined.

    DESKTOP_DEBUG
      A shorthand for DESKTOP_LOG_LEVEL=DEBUG. Also turns on output HTML
      validation.

    DESKTOP_PROFILE
      Turn on Python profiling. The profile data is saved in a file. See the
      console output for the location of the file.

    DESKTOP_LOG_DIR=$dir
      Specify the HUE log directory. Defaults to ./log.

    DESKTOP_DB_CONFIG=$db engine:db name:test db name:username:password:host:port
      Specify alternate DB connection parameters for HUE to use. Useful for
      testing your changes against, for example, MySQL instead of sqlite. String
      is a colon-delimited list.

    TEST_IMPALAD_HOST=impalad-01.gethue.com
      Point to an Impalad and trigger the Impala tests.


### Writing tests that depend on Hadoop

Use pseudo_hdfs4.py!  You should tag such tests with "requires_hadoop", as follows:

    from nose.plugins.attrib import attr

    @attr('requires_hadoop')
    def your_test():
      ...


### Jenkins Configuration

Because building Hadoop (for the tests that require it) is slow, we've
separated the Jenkins builds into "fast" and "slow".  Both are run
via scripts/jenkins.sh, which should be kept updated with the latest
and greatest in build technologies.