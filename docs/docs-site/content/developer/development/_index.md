---
title: "Development"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

This section goes into greater detail on how to build and reuse the components of Hue.


## Quick Start

### Dependencies

* The OS specific install instructions are listed in the [install guide](/administrator/installation/dependencies/)
* Python 2.7+ (Python 3 support tracked in [HUE-8737](https://issues.cloudera.org/browse/HUE-8737))
* Django (1.11 already included in the distribution)
* Java (Java 1.8) (should go away after [HUE-8740](https://issues.cloudera.org/browse/HUE-8740))
* npm ([10.0+](https://deb.nodesource.com/setup_10.x))

### Build & Start

Build once:

    make apps

Then start the dev server (which will auto reload):

    ./build/env/bin/hue runserver

If you are changing Javascript or CSS files, also start:

    npm run dev

Then it is recommended to use MySQL or PostGres as the database.

Open the `hue.ini` file in a text editor. Directly below the `[[database]]` line, add the following options (and modify accordingly for
your MySQL setup):

    host=localhost
    port=3306
    engine=mysql
    user=hue
    password=secretpassword
    name=hue

### Dev environment

#### Visual Code

Adding 'hue' as a workspace, then:

Recommended extensions:

* Python - Microsoft
* EsLint - Dirk Baeumur https://github.com/cloudera/hue/blob/master/.eslintrc.js
* Mako - tommorris
* Docker - Microsoft

#### PyCharm

First step is to configure pycharm to use the Hue virtual environment at ./build/env/env
![Pycharm virtualenv](/images/pycharm_virtualenv.png)

Second step is to configure the debug configuration
![Pycharm debug](/images/pycharm_debug.png)

#### Eclipse

First step is to configure Eclipse to use the Hue virtual environment at ./build/env/env
![Eclipse interpreter](/images/eclipse_interpreter.png)

Second step is to configure the debug configuration
![Eclipse debug](/images/eclipse_debug.png)
![Eclipse debug arguments](/images/eclipse_debug_arguments.png)
![Eclipse debug interpreter](/images/eclipse_debug_interpreter.png)


## API Server

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

### Interacting with external services

![Interacting with Hadoop](/images/interactingwithhadoop.png)

Hue provides some APIs for interacting with external services like Databases of File storages.
These APIs work by making REST or Thrift calls.

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

### Configurations

#### File

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


#### Variables

Your application's `conf.py` is special. It provides access to the configuration file (and even
default configurations not specified in the file). Using the above example, your `conf.py` should
define the following:

A `desktop.lib.conf.Config` object for `app_property`, such as:

    MY_PROPERTY = Config(key='app_property', default='Beatles', help='blah')

  You can access its value by `MY_PROPERTY.get()`.

A `desktop.lib.conf.ConfigSection` object for `section_a`, such as:

    SECTION_A = ConfigSection(key='section_a',
          help='blah',
          members=dict(
            AWEIGHT=Config(key='a_weight', type=int, default=0),
            AHEIGHT=Config(key='a_height', type=int, default=0)))

  You can access the values by `SECTION_A.AWEIGHT.get()`.

A `desktop.lib.conf.UnspecifiedConfigSection` object for `filesystems`, such as:

    FS = UnspecifiedConfigSection(
        key='filesystems',
        each=ConfigSection(members=dict(
            nn_host=Config(key='namenode_host', required=True))

An `UnspecifiedConfigSection` is useful when the children of the section are not known.
When Hue loads your application's configuration, it binds all sub-sections. You can
access the values by:

    cluster1_val = FS['cluster_1'].nn_host.get()
    all_clusters = FS.keys()
    for cluster in all_clusters:
        val = FS[cluster].nn_host.get()


Application can automatically detect configuration problems and alert
the admin. To take advantage of this feature, create a `config_validator`
function in your `conf.py`:

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


<div class="note">
  You should specify the <code>help="..."</code> argument to all configuration
  related objects in your <code>conf.py</code>. The examples omit some for the
  sake of space. But you and your application's users can view all the
  configuration variables by doing:
  <pre>
    $ build/env/bin/hue config_help
  </pre>
</div>


### Saving documents

Each app used to have its own model to store its data (e.g. a saving a SQL query, query history...). All the models have been unified into a single Document2 model in the desktop app:

``desktop/core/src/desktop/models.py``.

The `Document2` model provides automatically creation, sharing and saving. It persists the document data into a json field, which limits the need ot database migrations and simplifies the interaction with the frontend.

`Document2` is based on [Django Models](https://docs.djangoproject.com/en/1.11/#the-model-layer)
are Django's Object-Relational Mapping framework.


### Walk-through of a Django View

![Django Request](/images/django_request.png)


Django is an MVC framework, except that the controller is called a
"[view](https://docs.djangoproject.com/en/1.11/#the-view-layer)" and
the "view" is called a "template".  For an application developer, the essential
flow to understand is how the "urls.py" file provides a mapping between URLs (expressed as a
regular expression, optionally with captured parameters) and view functions.
These view functions typically use their arguments (for example, the captured parameters) and
their request object (which has, for example, the POST and GET parameters) to
prepare dynamic content to be rendered using a template.

### Templates: Django and Mako

In Hue, the typical pattern for rendering data through a template
is:

    from desktop.lib.django_util import render

    def view_function(request):
      return render('view_function.mako', request, dict(greeting="hello"))

The `render()` function chooses a template engine (either Django or Mako) based on the
extension of the template file (".html" or ".mako"). Mako templates are more powerful,
in that they allow you to run arbitrary code blocks quite easily, and are more strict (some
would say finicky); Django templates are simpler, but are less expressive.


### Authentication Backends

Hue exposes a configuration flag ("auth") to configure
a custom authentication backend.
See http://docs.djangoproject.com/en/dev/topics/auth/#writing-an-authentication-backend
for writing such a backend.

In addition to that, backends may support a `manages_passwords_externally()` method, returning
True or False, to tell the user manager application whether or not changing
passwords within Hue is possible.

### Authorization

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

### Using and Installing Thrift

Right now, we check in the generated thrift code.
To generate the code, you'll need the thrift binary version 0.9.0.
Please download from http://thrift.apache.org/.

The modules using ``Thrift`` have some helper scripts like ``regenerate_thrift.sh``
for regenerating the code from the interfaces.


### Upgrades

After upgrading the version of Hue, running these two commands will make sure the
database has the correct tables and fields.

    ./build/env/bin/hue syncdb
    ./build/env/bin/hue migrate


### Debugging Tips and Tricks

* Set `DESKTOP_DEBUG=1` as an environment variable if you want logs to go to stderr
  as well as to the respective log files.
* Use runserver.  If you want to set a CLI breakpoint, just insert
  `__import__("ipdb").set_trace()`
  into your code.
* Django tends to restart its server whenever it notices a file changes.  For
  certain things (like configuration changes), this is not sufficient.  Restart
  the server whole-heartedly.
* We recommend developing with the Chrome console.

* Special environment variables

    DESKTOP_LOGLEVEL=<level>
      level can be DEBUG, INFO, WARN, ERROR, or CRITICAL.
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

## User interface

Developing applications for Hue requires a minimal amount of CSS
(and potentially JavaScript) to use existing functionality.

In a nutshell, front-end development is using:

* [Mako](http://www.makotemplates.org/) is the templating language (Mako to be slowly removed in [HUE-9036](https://issues.cloudera.org/browse/HUE-9036))
* [Bootstrap](http://twitter.github.com/bootstrap/) to layout your app
* [Knockout js](http://knockoutjs.com/) to script the custom interactions


### Javascript

The javascript files are currently being migrated to webpack bundles, during this process some files will live under src/desktop/static/ and some will live under src/dekstop/js

For changes to the files under src/desktop/js the following applies:

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

Hue uses [Bootstrap](http://twitter.github.com/bootstrap/) version 2.0 CSS
styles and layouts. They are highly reusable and flexible. Your app doesn't
have to use these styles, but if you do, it'll save you some time and make your
app look at home in Hue.

After changing the CSS in a .less file, rebuilding with:

    npm run less

Or run in watch mode that will generate the .css on any change to the .less files:

    npm run less-dev

After less changes make sure linting is run with:

    npm run less-lint

### Icons

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

### Static files

For better performances, Hue uses the Django staticfiles app. If in production mode, if you edit
some static files, you would need to run this command or `make apps`. No actions are needed in
development mode.
```
./build/env/bin/hue collectstatic
```

## Testing

### The short story

Run the unit tests

    ./build/env/bin/hue test unit

Open a pull request which will automaticlly trigger a [CircleCi](https://circleci.com/gh/cloudera/hue) unit test run.

How to run just some parts of the tests, e.g.:

    build/env/bin/hue test specific impala
    build/env/bin/hue test specific impala.tests:TestMockedImpala
    build/env/bin/hue test specific impala.tests:TestMockedImpala.test_basic_flow

Jest tests:

    npm run test


### Longer story

The ``test`` management command prepares the arguments (test app names)
and passes them to nose (django_nose.nose_runner). Nose will then magically
find all the tests to run.

Tests themselves should be named *_test.py.  These will be found
as long as they're in packages covered by django.  You can use the
unittest frameworks, or you can just name your method with
the word "test" at a word boundary, and nose will find it.

See apps/hello/src/hello/hello_test.py for an example.


#### Running only specific tests

To run the unit tests (should take 5-10 minutes):

    build/env/bin/hue test fast

To run all the tests (unit and integration), use:

    build/env/bin/hue test all

To run only tests of a particular app, use:

    build/env/bin/hue test specific <app>

e.g.

    build/env/bin/hue test specific filebrowser

To run a specific test, use:

    build/env/bin/hue test specific <app><module>:<test_func>
    build/env/bin/hue test specific <app><module>:<class>

e.g.

    build/env/bin/hue test specific useradmin.tests:test_user_admin
    build/env/bin/hue test specific useradmin.tests:AdminTest

To run a specific test in a class, use:

    build/env/bin/hue test specific <app><module>:<class><test_func>

e.g.

    build/env/bin/hue test specific useradmin.tests:AdminTest.test_login

Start up pdb on test failures:

    build/env/bin/hue test <args> --pdb --pdb-failure -s

#### Coverage

Add the following options:

    ./build/env/bin/hue test unit --with-xunit --with-cover

For js run:

    npm run test-coverage

#### Create and run the Jest tests

Add them next to the file under test, the filename of the test has to end with ".test.js".

    someFile.js         <- File under test
    someFile.test.js    <- File containing tests

Run all the tests once with:

    npm run test

Run tests from a specific file once:

    npm run test -- foo.test.js

To run the tests in watch mode:

    npm run test-dev

While in watch mode Jest will detect changes to all files and re-run related tests. There are
also options to target specific files or tests. Press 'w' in the console to see the options.

#### Testing KO components and bindings

koSetup provides utilities to test knockout components and bindings using jsdom from jest.

An example of component test:

```
import { koSetup } from 'jest/koTestUtils';

import 'ko/someComponent';

describe('ko.someComponent.js', () => {
  const setup = koSetup(); // Adds the necessary setup and teardown

  it('should render component', async () => {
    const someParams = {}

    const element = await setup.renderComponent('someComponent', someParams);

    expect(element.innerHTML).toMatchSnapshot();
  });

  it('should change after observable update', async () => {
    const someParams = { visible: ko.observable(false) };
    const wrapper = await setup.renderComponent('someComponent', someParams);
    expect(wrapper.querySelector('[data-test="some-test-id"]').style['display']).toEqual('none');

    someParams.visible(true); // Or trigger some event on an elmement etc.
    await setup.waitForKoUpdate(); // Waits for re-render

    expect(wrapper.querySelector('[data-test="some-test-id"]').style['display']).toEqual('inline-block');
  });
});
```

An example of a binding test:

```
import ko from 'knockout';
import { koSetup } from 'jest/koTestUtils';
import './ko.myBinding';

describe('ko.myBinding.js', () => {
  const setup = koSetup();

  it('should toggle observable', async () => {
    const viewModel = { testObservable: ko.observable(false) };
    const wrapper = await setup.renderKo(
      '<div class="click-test" data-bind="myBinding: testObservable"></div>',
      viewModel
    );

    expect(viewModel.testObservable()).toBeFalsy();

    wrapper.querySelector('.click-test').click();
    await setup.waitForKoUpdate();

    expect(viewModel.testObservable()).toBeTruthy();
  });
});
```

#### Continuous Integration (CI)

[CircleCi](https://circleci.com/gh/cloudera/hue) automatically run the unit tests (Python, Javascript, linting) on branch updates and pull requests. Branches containing `ci-commit-master` will try to be auto pushed to master if the run is green and the Github permissions match.
This logic is described in the [config.yml](https://github.com/cloudera/hue/tree/master/.circleci).

The runs happen in an image based on [latest Hue's image](https://hub.docker.com/u/gethue/).

Note: until the `desktop/ext-py` dependencies are moved to a `requirement.txt`, adding new Python modules will require adding them first to the Docker image by building a Hue branch which has them.

#### Integration tests

To not fail on integration tests, Hue would need to be configured to point to a live cluster, or you could install the mini cluster (only once) with:

    ./tools/jenkins/jenkins.sh slow

Note: the integration tests are going to be ported to a more modern CI with dependencies provided by containers.

Those are tagged with `integration` either at the class or method level:

    class BeeswaxSampleProvider(object):
      integration = True

      @attr('integration')
      def test_add_ldap_users_case_sensitivity(self):
        if is_live_cluster():
          raise SkipTest('HUE-2897: Cannot yet guarantee database is case sensitive')

        ...

Historically, the same thing used to be done with the `requires_hadoop` tag:

    from nose.plugins.attrib import attr

    @attr('requires_hadoop')
    def your_test():
      ...

## Releasing

Update the versions to the next release (current release +1):

    :100644 100644 4db6d5f... f907d04... M	VERSION
    :100644 100644 9332f95... 45b28ad... M	desktop/libs/librdbms/java/pom.xml
    :100644 100644 551f62f... 694f021... M	maven/pom.xml
    :100644 100644 658d54a... 671ce01... M  package.json

How to count the number of commits since the last release:

    git log --oneline --since=2019-08-01 | grep 'release' -n -i
    git log --oneline -449 > commits.txt

    cat commits.txt | sed 's/\(HUE\-[[:digit:]][[:digit:]][[:digit:]][[:digit:]]\)/\[\1\]\(https:\/\/issues.cloudera.org\/browse\/\1\)/' | sed 's/^\(.*\)/* \1/' > commits.md

And add them and the authors to the release notes:

    git log --pretty="%an" | sort | uniq | sed 's/^\(.*\)/* \1/' > authors.txt

Pushing the release branch:

    git push origin HEAD:branch-4.6.0

Tagging the release:

    git tag -a release-4.6.0 -m "release-4.6.0"
    git push origin release-4.6.0

Building the tarball release:

    make prod

Source of the release: https://github.com/cloudera/hue/archive/release-4.6.0.zip

Push to the CDN:

    scp hue-4.6.0.tgz root@cdn.gethue.com:/var/www/cdn.gethue.com/downloads

Other things to update:

* In Jira, setting the [release as shipped](https://issues.cloudera.org/projects/HUE?selectedItem=com.atlassian.jira.jira-projects-plugin%3Arelease-page&status=all) and moving all non finished jiras to another target. Also archiving old releases.
* Create the after next release tag in Jira and Blog
* Update Docker image https://hub.docker.com/u/gethue/
* Update release date on https://wikipedia.org/wiki/Hue_(Software)

Instructions:

    docker build https://github.com/cloudera/hue.git#release-4.6.0 -t gethue/hue:4.6.0 -f tools/docker/hue/Dockerfile
    docker tag gethue/hue:4.6.0 gethue/hue:latest
    docker images
    docker login
    docker push gethue/hue
    docker push gethue/hue:4.6.0

    docker build . -t gethue/nginx:4.6.0 -f tools/docker/nginx/Dockerfile;
    docker tag gethue/nginx:4.6.0 gethue/nginx:latest
    docker push gethue/nginx
    docker push gethue/nginx:4.6.0

Documentation

[Build it](#Documentation) and push it to the docs host.

Build the doc website:

    cd docs/docs-site

    hugo

Release:

    ssh root@docs.gethue.com
    cd /var/www/docs.gethue.com
    mkdir 4.6.0
    rm latest; ln -s 4.6.0 latest

    scp -r docs/docs-site/public/* root@docs.gethue.com:/var/www/docs.gethue.com/4.6.0

    scp -r hue-4.6/build/release/prod/hue-4.6.0.tgz root@cdn.gethue.com:/var/www/cdn.gethue.com/downloads/


Then send release notes to the [Forum](https://discourse.gethue.com/), [hue-user](https://groups.google.com/a/cloudera.org/forum/#!forum/hue-user), https://twitter.com/gethue !

## Building

### Dev Docker

Try basic changes in Hue without compiling it locally:

    git clone https://github.com/cloudera/hue.git
    cd hue
    cp desktop/conf/pseudo-distributed.ini.tmpl desktop/conf/pseudo-distributed.ini

Then edit the `[[database]]` section to specify a proper database, here MySql:

    host=127.0.0.1 # Not localhost if Docker
    engine=mysql
    user=hue
    password=hue
    name=huedb

Then map the local Hue source code into the running container (so that local edits are seen in the running Hue):

    sudo docker run -it -v $PWD/apps:/usr/share/hue/apps -v $PWD/desktop:/usr/share/hue/desktop -v $PWD/desktop/conf/pseudo-distributed.ini:/usr/share/hue/desktop/conf/z-hue.ini --network="host" gethue/hue

Note: code updates won’t be seen after the Docker container runs. For this Hue would need to be started in dev server mode by replacing the [line](https://github.com/cloudera/hue/blob/master/tools/docker/hue/startup.sh#L5) by

    ./build/env/bin/hue runserver 0.0.0.0:8888

and recompiling the Docker image. It will then auto-restart on Python code changes. For JavaScript, those would need to be [compiled](//developer/development/#javascript).


### Documentation

Install [Hugo](https://gohugo.io/getting-started/quick-start/).

Build it and see live changes:

    cd docs/docs-site

    hugo serve

Check for links not working (returning a 404) with muffet, a fast link checker crawler:

    sudo snap install muffet

Then after booting the hugo documentation server, we point to its url. We also blacklist certain urls to avoid some noisy false positives:

    muffet http://localhost:35741/ --exclude ".*releases.*" -f

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

### Embedded language references

The tools for generating the embedded language reference manuals can be found under `hue/tools/sql-docs/`

#### Hive
The Hive documentation is generated directly from the Hive wiki by using an exported epub file.

1. Goto https://cwiki.apache.org/confluence/display/Hive/LanguageManual
2. Click the three dots '...' in the upper right corner
3. Click 'Export to EPUB'
4. In the Hue folder run:

        node tools/sql-docs/hiveExtractor.js --epub /path/to/epub/file

#### Impala
The Impala documentation is generated from the ditamap files in the Impala GitHub repo.

1. Clone the Impala repo next to hue from https://github.com/apache/impala
2. In the Hue folder run:

        node tools/sql-docs/docExtractor.js -c hue -f ../impala/docs/ -d impala_langref.ditamap,impala_keydefs.ditamap,impala.ditamap -o desktop/core/src/desktop/static/desktop/docs/impala/ -m desktop/core/src/desktop/templates/impala_doc_index.mako

### Internationalization

How to update all the messages and compile them:

    make locales

How to update and compile the messages of one app:

    cd apps/beeswax
    make compile-locale

How to create a new locale for an app:

    cd $APP_ROOT/src/$APP_NAME/locale
    $HUE_ROOT/build/env/bin/pybabel init -D django -i en_US.pot -d . -l fr
