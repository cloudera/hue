---
title: "Development"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---


This section goes into greater detail on useful features within
the Hue environment.

## User Management

Except for static content, `request.user` is always populated.  It is a
standard Django `models.User` object.  If you were to set a breakpoint at the
`index()` function in our calculator app, you will find:

    >>> request.user
    <User: test>

<div class="note">
  "Under the covers:" Django uses a notion called
  <a href="https://docs.djangoproject.com/en/1.2/topics/http/middleware/">middleware</a>
  that's called in between the request coming in and the view being executed.
  That's how <code>request.user</code> gets populated.  There's also a
  middleware for Hue that makes sure that no pages are displayed unless the
  user is authenticated.
</div>

## Configuration

### Configuration File

Hue uses a typed configuration system that reads configuration files (in an
ini-style format).  By default, Hue loads all `*.ini` files in the `build/desktop/conf`
directory.  The configuration files have the following format:

    # This is a comment
    [ app_name ]          # Same as your app's name
    app_property = "Pink Floyd"

    [[ section_a ]]         # The double brackets start a section under [ app_name ]
    a_weight = 80         # that is useful for grouping
    a_height = 180

    [[ filesystems ]]       # Sections are also useful for making a list
    [[[ cluster_1 ]]]       # All list members are sub-sections of the same type
    namenode_host = localhost
    # User may define more:
    # [[[ cluster_2 ]]]
    # namenode_host = 10.0.0.1


### Configuration Variables

Your application's `conf.py` is special. It provides access to the configuration file (and even
default configurations not specified in the file). Using the above example, your `conf.py` should
define the following:

* A `desktop.lib.conf.Config` object for `app_property`, such as:
<pre>
  MY_PROPERTY = Config(key='app_property', default='Beatles', help='blah')
</pre>
  You can access its value by `MY_PROPERTY.get()`.

* A `desktop.lib.conf.ConfigSection` object for `section_a`, such as:
<pre>
  SECTION_A = ConfigSection(key='section_a',
        help='blah',
        members=dict(
          AWEIGHT=Config(key='a_weight', type=int, default=0),
          AHEIGHT=Config(key='a_height', type=int, default=0)))
</pre>
  You can access the values by `SECTION_A.AWEIGHT.get()`.

* A `desktop.lib.conf.UnspecifiedConfigSection` object for `filesystems`, such as:
<pre>
  FS = UnspecifiedConfigSection(
      key='filesystems',
      each=ConfigSection(members=dict(
          nn_host=Config(key='namenode_host', required=True))
</pre>
  An `UnspecifiedConfigSection` is useful when the children of the section are not known.
  When Hue loads your application's configuration, it binds all sub-sections. You can
  access the values by:
<pre>
  cluster1_val = FS['cluster_1'].nn_host.get()
  all_clusters = FS.keys()
  for cluster in all_clusters:
      val = FS[cluster].nn_host.get()
</pre>

Your Hue application can automatically detect configuration problems and alert
the admin. To take advantage of this feature, create a `config_validator`
function in your `conf.py`:

<pre>
  def config_validator(user):
    """
    config_validator(user) -> [(config_variable, error_msg)] or None
    Called by core check_config() view.
    """
    res = [ ]
    if not REQUIRED_PROPERTY.get():
      res.append((REQUIRED_PROPERTY, "This variable must be set"))
    if MY_INT_PROPERTY.get() < 0:
      res.append((MY_INT_PROPERTY, "This must be a non-negative number"))
    return res
</pre>


<div class="note">
  You should specify the <code>help="..."</code> argument to all configuration
  related objects in your <code>conf.py</code>. The examples omit some for the
  sake of space. But you and your application's users can view all the
  configuration variables by doing:
  <pre>
    $ build/env/bin/hue config_help
  </pre>
</div>


### Running "Helper Processes"

Some Hue applications need to run separate daemon processes on the side.

Suppose your application needs a helper `my_daemon.py`. You need to register it by:

* In `setup.py`, add to `entry_points`:
<pre>
    entry_points = {
      'desktop.sdk.application': 'my_app = my_app',
      'desktop.supervisor.specs': [ 'my_daemon = my_app:SUPERVISOR_SPEC' ] }
</pre>

* In `src/my_app/__init__.py`, tell Hue what to run by adding:
<pre>
    SUPERVISOR_SPEC = dict(django_command="my_daemon")
</pre>

* Then in `src/my_app/management/commands`, create `__init__.py` and `my_daemon.py`. Your
  daemon program has only one requirement: it must define a class called `Command` that
  extends `django.core.management.base.BaseCommand`. Please see `kt_renewer.py` for an example.

The next time Hue restarts, your `my_daemon` will start automatically.
If your daemon program dies (exits with a non-zero exit code), Hue will
restart it.

"Under the covers:" Threading.  Hue, by default, runs CherryPy web server.
If Hue is configured (and it may be, in the future)
to use mod_wsgi under Apache httpd, then there would be multiple python
processes serving the backend.  This means that your Django application
code should avoid depending on shared process state.  Instead, place
the stored state in a database or run a separate server.

## Walk-through of a Django View

![Django Flow](django_request.png)

Django is an MVC framework, except that the controller is called a
"[view](https://docs.djangoproject.com/en/1.11/#the-view-layer)" and
the "view" is called a "template".  For an application developer, the essential
flow to understand is how the "urls.py" file provides a mapping between URLs (expressed as a
regular expression, optionally with captured parameters) and view functions.
These view functions typically use their arguments (for example, the captured parameters) and
their request object (which has, for example, the POST and GET parameters) to
prepare dynamic content to be rendered using a template.

## Templates: Django and Mako

In Hue, the typical pattern for rendering data through a template
is:

    from desktop.lib.django_util import render

    def view_function(request):
      return render('view_function.mako', request, dict(greeting="hello"))

The `render()` function chooses a template engine (either Django or Mako) based on the
extension of the template file (".html" or ".mako"). Mako templates are more powerful,
in that they allow you to run arbitrary code blocks quite easily, and are more strict (some
would say finicky); Django templates are simpler, but are less expressive.

## Django Models

[Django Models](https://docs.djangoproject.com/en/1.11/#the-model-layer)
are Django's Object-Relational Mapping framework. If your application
needs to store data (history, for example), models are a good way to do it.

From an abstraction perspective, it's common to imagine external services
as "models".  For example, the Job Browser treats the Hadoop JobTracker
as a "model", even though there's no database involved.

## Accessing Hadoop

It is common for applications to need to access the underlying HDFS.
The `request.fs` object is a "file system" object that exposes
operations that manipulate HDFS.  It is pre-configured to access
HDFS as the user that's currently logged in.  Operations available
on `request.fs` are similar to the file operations typically
available in python.  See `webhdfs.py` for details; the list
of functions available is as follows:
`chmod`,
`chown`,
`exists`,
`isdir`,
`isfile`,
`listdir` (and `listdir_stats`),
`mkdir`,
`open` (which exposes a file-like object with `read()`, `write()`, `seek()`, and `tell()` methods),
`remove`,
`rmdir`,
`rmtree`, and
`stats`.


## Making Your Views Thread-safe

Hue works in any WSGI-compliant container web server.
The current recommended deployment server is the built-in CherryPy server.
The CherryPy server, which is multi-threaded, is invoked by `runcpserver`
and is configured to start when Hue's `supervisor` script is used.
Meanwhile, `runserver` start a single-threaded
testing server.

Because multiple threads may be accessing your views
concurrently, your views should not use shared state.
An exception is that it is acceptable to initialize
some state when the module is first imported.
If you must use shared state, use Python's `threading.Lock`.

Note that any module initialization may happen multiple times.
Some WSGI containers (namely, Apache), will start multiple
Unix processes, each with multiple threads. So, while
you have to use locks to protect state within the process,
there still may be multiple copies of this state.

For persistent global state, it is common to place the state
in the database or on the Browser local storage.

## Authentication Backends

Hue exposes a configuration flag ("auth") to configure
a custom authentication backend.  See
See http://docs.djangoproject.com/en/dev/topics/auth/#writing-an-authentication-backend
for writing such a backend.

In addition to that, backends may support a `manages_passwords_externally()` method, returning
True or False, to tell the user manager application whether or not changing
passwords within Hue is possible.

## Authorization

Applications may define permission sets for different actions. Administrators
can assign permissions to user groups in the UserAdmin application. To define
custom permission sets, modify your app's `settings.py` to create a list of
`(identifier, description)` tuples:

    PERMISSION_ACTIONS = [
      ("delete", "Delete really important data"),
      ("email", "Send email to the entire company"),
      ("identifier", "Description of the permission")
    ]

Then you can use this decorator on your view functions to enforce permission:

    @desktop.decorators.hue_permission_required("delete", "my_app_name")
    def delete_financial_report(request):
      ...

## Using and Installing Thrift

Right now, we check in the generated thrift code.
To generate the code, you'll need the thrift binary version 0.9.0.
Please download from http://thrift.apache.org/.

The modules using ``Thrift`` have some helper scripts like ``regenerate_thrift.sh``
for regenerating the code from the interfaces.

## Profiling Hue Apps

Hue has a profiling system built in, which can be used to analyze server-side
performance of applications.  To enable profiling::

    build/env/bin/hue runprofileserver

Then, access the page that you want to profile.  This will create files like
/tmp/useradmin.users.000072ms.2011-02-21T13:03:39.745851.prof.  The format for
the file names is /tmp/<app_module>.<page_url>.<time_taken>.<timestamp>.prof.

Hue uses the hotshot profiling library for instrumentation.  The documentation
for this library is located at: http://docs.python.org/library/hotshot.html.

You can use kcachegrind to view the profiled data graphically::

    $ hotshot2calltree /tmp/xyz.prof > /tmp/xyz.trace
    $ kcachegrind /tmp/xyz.trace

More generally, you can programmatically inspect a trace::

    #!/usr/bin/python
    import hotshot.stats
    import sys

    stats = hotshot.stats.load(sys.argv[1])
    stats.sort_stats('cumulative', 'calls')
    stats.print_stats(100)

This script takes in a .prof file, and orders function calls by the cumulative
time spent in that function, followed by the number of times the function was
called, and then prints out the top 100 time-wasters.  For information on the
other stats available, take a look at this website:
http://docs.python.org/library/profile.html#pstats.Stats



## Django Models

Each app used to have its own model to store its data (e.g. a SQL query, a workflow). In Hue 3
a unification of all the models happened and any app now uses a single Document2 model:
``desktop/core/src/desktop/models.py``. This enables to avoid simply re-use document
creation, sharing, saving etc...

## REST
Hue is Ajax based and has a REST API used by the browser to communicate (e.g. submit a query or workflow,
list some S3 files, export a document...). Currently this API is private and subject to change but
can be easily reused. You would need to GET ``/accounts/login`` to get the CSRF token
and POST it back along ``username`` and ``password`` and reuse the ``sessionid`` cookie in next
communication calls.

** With Python Request **

Hue is based on the Django Web Framework. Django comes with user authentication system. Django uses sessions and middleware to hook the authentication system into request object. HUE uses stock auth form which uses “username” and “password” and “csrftoken” form variables to authenticate.

In this code snippet, we will use well-known python “requests” library. we will first acquire “csrftoken” by GET “login_url”. We will create python dictionary of form data which contains “username”, “password” and “csrftoken” and the “next_url” and another python dictionary for header which contains the “Referer” url and empty python dictionary for the cookies. After POST request to “login_url” we will get status. Check the r.status_code. If r.status_code!=200 then you have problem in username and/or password.

Once the request is successful then capture headers and cookies for subsequent requests. Subsequent request.session calls can be made by providing cookies=session.cookies and headers=session.headers.

<pre>
import requests

def login_djangosite():
 next_url = "/"
 login_url = "http://localhost:8888/accounts/login?next=/"

 session = requests.Session()
 r = session.get(login_url)
 form_data = dict(username="[your hue username]",password="[your hue password]",
                  csrfmiddlewaretoken=session.cookies['csrftoken'],next=next_url)
 r = session.post(login_url, data=form_data, cookies=dict(), headers=dict(Referer=login_url))

 # check if request executed successfully?
 print r.status_code

 cookies = session.cookies
 headers = session.headers

 r=session.get('http://localhost:8888/metastore/databases/default/metadata',
 cookies=session.cookies, headers=session.headers)
 print r.status_code

 # check metadata output
 print r.text
</pre>

[Read more about it here](http://gethue.com/login-into-hue-using-the-python-request-library/).

<div class="note">
  http://issues.cloudera.org/browse/HUE-1450 is tracking a more official public API.
</div>


## Upgrade path

After upgrading the version of Hue, running these two commands will make sure the
database has the correct tables and fields.

    ./build/env/bin/hue syncdb
    ./build/env/bin/hue migrate

# Front-end Development

Developing applications for Hue requires a minimal amount of CSS
(and potentially JavaScript) to use existing functionality. As covered above,
creating an application for the Hue is a matter of creating a standard HTML
application.

In a nutshell, front-end development in Hue is using
[Bootstrap](http://twitter.github.com/bootstrap/) and
[Knockout js](http://knockoutjs.com/) to layout your app and script the custom
interactions.


## CSS Styles

Hue uses [Bootstrap](http://twitter.github.com/bootstrap/) version 2.0 CSS
styles and layouts. They are highly reusable and flexible. Your app doesn't
have to use these styles, but if you do, it'll save you some time and make your
app look at home in Hue.

On top of the standard Bootstrap styles, Hue defines a small set of custom
styles in *desktop/core/static/css/jhue.css*.

## Defining Styles for Your Application

When you create your application it will provision a CSS file for you in the
*static/css* directory. For organization purposes, your styles should go here
(and any images you have should go in *static/art*). Your app's name will be a
class that is assigned to the root of your app in the DOM. So if you created an
app called "calculator" then every window you create for your app will have the
class "calculator".  Every style you define should be prefixed with this to
prevent you from accidentally colliding with the framework style. Examples:

    /* the right way: */
    .calculator p {
      /* all my paragraphs should have a margin of 8px */
      margin: 8px;
      /* and a background from my art directory */
      background: url(../art/paragraph.gif);
    }
    /* the wrong way: */
    p {
      /* woops; we're styling all the paragraphs on the page, affecting
         the common header! */
      margin: 8px;
      background: url(../art/paragraph.gif);
    }

## Icons

You should create an icon for your application that is a transparent png sized
24px by 24px. Your `settings.py` file should point to your icon via the `ICON`
variable. The `create_desktop_app` command creates a default icon for you.

<div class="note">
  If you do not define an application icon, your application will not show up
  in the navigation bar.
</div>

Hue ships with Twitter Bootstrap and Font Awesome 3 (http://fortawesome.github.io/Font-Awesome/)
so you have plenty of scalable icons to choose from. You can style your elements to use them
like this (in your mako template):

    <!-- show a trash icon in a link -->
    <a href="#something"><i class="icon-trash"></i> Trash</a>

## Static files

For better performances, Hue uses the Django staticfiles app. If in production mode, if you edit
some static files, you would need to run this command or `make apps`. No actions are needed in
development mode.
```
./build/env/bin/hue collectstatic
```

## Adding Interactive Elements to Your UI

Hue by default loads these JavaScript components:

* Ko js
* jQuery
* Bootstrap

These are used by some Hue applications, but not loaded by default:

* Knockout js (`desktop/core/static/ext/js/knockout-min.js`)
* jQuery UI (`desktop/core/static/ext/js/jquery/plugins/jquery-ui-autocomplete-1.8.18.min.js`)

These standard components have their own online documentation, which we will
not repeat here. They let you write interactive behaviors with little or no
JavaScript.


## Debugging Tips and Tricks

* Set `DESKTOP_DEBUG=1` as an environment variable if you want logs to go to stderr
  as well as to the respective log files.
* Use runserver.  If you want to set a CLI breakpoint, just insert
  `__import__("ipdb").set_trace()`
  into your code.
* Django tends to restart its server whenever it notices a file changes.  For
  certain things (like configuration changes), this is not sufficient.  Restart
  the server whole-heartedly.
* We recommend developing with the Chrome console.

## Building

### Documentation

Building with

    make docs

### Javascript

The javascript files are currently being migrated to webpack bundles, during this process some files will live under src/desktop/static/ and some will live under src/dekstop/js

#### For changes to the files under src/desktop/js the following applies:

First make sure all third-party dependencies defined in package.json are installed into node_modules/

    npm install

Also run this after making changes to package.json, adding new third-party dependencies etc.

To generate the js bundles run:

    npm run webpack
    npm run webpack-workers
    npm run webpack-login

During development the bundles can be autogenerated when it detects changes to the .js files, for this run:

    npm run dev

Before sending a review with changes to the bundles run:

    npm run lint-fix

and possibly fix any issues it might report.

### CSS / LESS

After changing the CSS in a .less file, rebuilding with:

    make css

### SQL Autocomplete

Install a patched jison:

    git clone https://github.com/JohanAhlen/jison
    cd jison
    npm install -g .

Then run:

    make sql-all-parsers

### Ace Editor

After modifying files under tools/ace-editor run the following to build ace.js

    npm install
    make ace

### Internationalization

How to update all the messages and compile them:

    make locales

How to update and compile the messages of one app:

    cd apps/beeswax
    make compile-locale

How to create a new locale for an app:

    cd $APP_ROOT/src/$APP_NAME/locale
    $HUE_ROOT/build/env/bin/pybabel init -D django -i en_US.pot -d . -l fr
