---
title: "API"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 5
---

Hue can be accessed directly via a Django Python Shell or by its REST API.

## REST

REST APIs are not all public yet but this is work in progress in [HUE-1450](https://issues.cloudera.org/browse/HUE-1450).

Hue is Ajax based and has a REST API used by the browser to communicate (e.g. submit a query or workflow,
list some S3 files, export a document...). Currently this API is private and subject to change but
can be easily reused. You would need to GET */accounts/login* to get the CSRF token
and POST it back along *username* and *password* and reuse the *sessionid* cookie in next
communication calls.

### Quickstart

Hue is based on the Django Web Framework. Django comes with user authentication system. Django uses sessions and middleware to hook the authentication system into request object. Hue uses stock auth form which uses *username* and *password* and *csrftoken* form variables to authenticate.

In this code snippet, we will use well-known python *requests* library. We will first acquire *csrftoken* by GET *login_url* and then create a dictionary of form data which contains *username*, *password* and *csrftoken* and the *next_url* and another dictionary for header which contains the *Referer* url and an empty dictionary for the cookies. After the POST request to *login_url* we will check the reponse code, which should be *r.status_code == 200*.

Once the request is successful then capture headers and cookies for subsequent requests. Subsequent *request.session* calls can be made by providing *cookies=session.cookies* and *headers=session.headers*.

    import requests

    next_url = "/"
    login_url = "http://localhost:8888/accounts/login"

    session = requests.Session()
    response = session.get(login_url)

    form_data = {
        'username': '[your Hue username]',
        'password': '[your Hue password]',
        'csrfmiddlewaretoken': session.cookies['csrftoken'],
        'next': next_url
    }
    response = session.post(login_url, data=form_data, cookies={}, headers={'Referer': login_url})

    print('Logged in successfully: %s %s' % (response.status_code == 200, response.status_code))

    cookies = session.cookies
    headers = session.headers

    response = session.get('http://localhost:8888/metastore/databases/default/metadata')
    print(response.status_code)
    print(response.text)

### Data Catalog

The [metadata API](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata) is powering [Search and Tagging here](/user/browsing/#data-catalogs).

See the backends API in the [data catalog connector](/developer/connectors/#data-catalog) section.

#### Searching for entities

    $.post("/metadata/api/catalog/search_entities_interactive/", {
        query_s: ko.mapping.toJSON("*sample"),
        sources: ko.mapping.toJSON(["sql", "hdfs", "s3"]),
        field_facets: ko.mapping.toJSON([]),
        limit: 10
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

Searching for entities with the dummy backend:

    $.post("/metadata/api/catalog/search_entities_interactive/", {
        query_s: ko.mapping.toJSON("*sample"),
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

#### Finding an entity in order to get its id

    $.get("/metadata/api/navigator/find_entity", {
        type: "table",
        database: "default",
        name: "sample_07",
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

Adding/updating a comment with the dummy backend:

    $.post("/metadata/api/catalog/update_properties/", {
        id: "22",
        properties: ko.mapping.toJSON({"description":"Adding a description"}),
        interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

#### Adding a tag with the dummy backend

    $.post("/metadata/api/catalog/add_tags/", {
      id: "22",
      tags: ko.mapping.toJSON(["usage"]),
      interface: "dummy"
    }, function(data) {
        console.log(ko.mapping.toJSON(data));
    });

#### Deleting a key/value property

    $.post("/metadata/api/catalog/delete_metadata_properties/", {
       "id": "32",
       "keys": ko.mapping.toJSON(["project", "steward"])
    }, function(data) {
       console.log(ko.mapping.toJSON(data));
    });

#### Deleting a key/value property

    $.post("/metadata/api/catalog/delete_metadata_properties/", {
      "id": "32",
      "keys": ko.mapping.toJSON(["project", "steward"])
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


#### Getting the model mapping

    $.get("/metadata/api/catalog/models/properties/mappings/", function(data) {
      console.log(ko.mapping.toJSON(data));
    });


#### Getting a namespace

    $.post("/metadata/api/catalog/namespace/", {
      namespace: 'huecatalog'
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

#### Creating a namespace

    $.post("/metadata/api/catalog/namespace/create/", {
      "namespace": "huecatalog",
      "description": "my desc"
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


#### Creating a namespace property

    $.post("/metadata/api/catalog/namespace/property/create/", {
      "namespace": "huecatalog",
      "properties": ko.mapping.toJSON({
        "name" : "relatedEntities2",
        "displayName" : "Related objects",
        "description" : "My desc",
        "multiValued" : true,
        "maxLength" : 50,
        "pattern" : ".*",
        "enumValues" : null,
        "type" : "TEXT"
      })
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });


#### Map a namespace property to a class

    $.post("/metadata/api/catalog/namespace/property/map/", {
      "class": "hv_view",
      "properties": ko.mapping.toJSON([{
          namespace: "huecatalog",
          name: "relatedQueries"
      }])
    }, function(data) {
      console.log(ko.mapping.toJSON(data));
    });

### SQL Querying
### SQL Risk Optimization
### Data Browsing
### Workflow scheduling

## Python

* [Hue API: Execute some builtin or shell commands](http://gethue.com/hue-api-execute-some-builtin-commands/).
* [How to manage the Hue database with the shell](http://gethue.com/how-to-manage-the-hue-database-with-the-shell/).

### How to count documents of a user

On the command line:

    ./build/env/bin/hue shell

If using Cloudera Manager, as a *root* user launch the shell.

Export the configuration directory:

    export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE_SERVER | tail -1 | awk '{print $9}'`"
    echo $HUE_CONF_DIR
    > /var/run/cloudera-scm-agent/process/2061-hue-HUE_SERVER

Get the process id:

    lsof -i :8888|grep -m1 hue|awk '{ print $2 }'
    > 14850

In order to export all Hue's env variables:

    for line in `strings /proc/$(lsof -i :8888|grep -m1 hue|awk '{ print $2 }')/environ|egrep -v "^HOME=|^TERM=|^PWD="`;do export $line;done

And finally launch the shell by:

    HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=1 /opt/cloudera/parcels/CDH/lib/hue/build/env/bin/hue shell
    > ALERT: This appears to be a CM Managed environment
    > ALERT: HUE_CONF_DIR must be set when running hue commands in CM Managed environment
    > ALERT: Please run 'hue <command> --cm-managed'

Then use the Python code to access a certain user information:

    Python 2.7.6 (default, Oct 26 2016, 20:30:19)
    Type "copyright", "credits" or "license" for more information.

    IPython 5.2.0 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    from django.contrib.auth.models import User
    from desktop.models import Document2

    user = User.objects.get(username='demo')
    Document2.objects.documents(user=user).count()

    In [8]: Document2.objects.documents(user=user).count()
    Out[8]: 1167

    In [10]: Document2.objects.documents(user=user, perms='own').count()
    Out[10]: 1166

    In [11]: Document2.objects.documents(user=user, perms='own', include_history=True).count()
    Out[11]: 7125

    In [12]: Document2.objects.documents(user=user, perms='own', include_history=True, include_trashed=True).count()
    Out[12]: 7638

    In [13]: Document2.objects.documents(user=user, perms='own', include_history=True, include_trashed=True, include_managed=True).count()
    Out[13]: 31408

    Out[14]:
    (85667L,
    {u'desktop.Document': 18524L,
      u'desktop.Document2': 31409L,
      u'desktop.Document2Permission': 556L,
      u'desktop.Document2Permission_groups': 277L,
      u'desktop.Document2Permission_users': 0L,
      u'desktop.Document2_dependencies': 15087L,
      u'desktop.DocumentPermission': 1290L,
      u'desktop.DocumentPermission_groups': 0L,
      u'desktop.DocumentPermission_users': 0L,
      u'desktop.Document_tags': 18524L})


### Creating an App

Building a brand new application is more work but is ideal for creating a custom solution.

**Note** It is now more recommended to integrate external services (e.g. integrate a new SQL Datatase with the Editor, add a new visualization...) to the core Hue APIs instead of building brand new application. This page gives good content in both cases. Feel free to contact the community for advice.

#### Overview

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

#### Creating the app

Run "create_desktop_app" to Set up a New Source Tree

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

#### Install SDK Application

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

#### Customizing

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
