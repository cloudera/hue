---
title: "Applications"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

Building a brand new application is more work but is ideal for creating a custom solution.

**Note** It is now more recommended to integrate external services (e.g. integrate a new SQL Datatase with the Editor, add a new visualization...) to the core Hue APIs instead of building brand new application. This page gives good content in both cases. Feel free to contact the community for advice.

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
