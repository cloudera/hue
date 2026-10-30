---
title: "Development"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 1
---

This section goes into greater detail on how to build, test, extend and release Hue.

## Quick start

### Requirements

* The OS specific packages listed in the [install guide](/administrator/installation/dependencies/)
* Python 3.11 (the only supported Python version)
* Node.js 22.13 or later, with npm (see the `engines` field of `package.json`)

### Build & start

Build once, from the root of your Hue clone:

```bash
export PYTHON_VER=python3.11

# On macOS you might need to set
export SKIP_PYTHONDEV_CHECK=true

make apps
```

The [dependencies documentation](/administrator/installation/dependencies/) helps with troubleshooting build issues.

Create your local configuration file from the template:

```bash
cp desktop/conf/pseudo-distributed.ini.tmpl desktop/conf/pseudo-distributed.ini
```

Then start the dev server, which reloads automatically when Python files change:

```bash
./build/env/bin/hue runserver
```

If you are changing frontend files (TypeScript, JavaScript, Vue, SCSS), also start the webpack watcher in another terminal:

```bash
npm run dev
```

### Use a transactional database

Hue needs a transactional database like MySQL or PostgreSQL to support concurrent requests and to keep the registered users, saved queries and sharing permissions when the server stops. With the default SQLite database you might see `database is locked` errors.

Open the `desktop/conf/pseudo-distributed.ini` file in a text editor. Directly below the `[[database]]` line, add the following options (and modify them for your MySQL setup):

```ini
host=localhost
port=3306
engine=mysql
user=hue
password=secretpassword
name=hue
```


Read more about how [configurations work](/administrator/configuration/).

### First SQL queries

Here is how to point the Editor to either MySQL or [Apache Hive](https://hive.apache.org/) and execute your first SQL queries. For other supported databases refer to the [connectors](/administrator/configuration/connectors/).

#### MySQL

In `desktop/conf/pseudo-distributed.ini`, below the `[[interpreters]]` section of `[notebook]`, add:

```ini
[[[mysql]]]
name=MySQL
interface=sqlalchemy
options='{"url": "mysql://${USER}:${PASSWORD}@localhost:3306/hue"}'
```

#### Apache Hive

You can connect to an existing Hive instance or setup a new one locally. An easy way to setup one is with Docker. You could use this [Hive 2 container](https://github.com/big-data-europe/docker-hive).

```bash
git clone https://github.com/big-data-europe/docker-hive
cd docker-hive
docker-compose up -d
```

Those three commands give you a running Hive instance on `jdbc:hive2://localhost:10000`.

Now under Hue open `desktop/conf/pseudo-distributed.ini` file in a text editor, and modify the following properties:

1. Directly below the `[[beeswax]]` line, add the following:

   ```ini
   # Host where HiveServer2 is running.
   hive_server_host=localhost
   # Port where HiveServer2 Thrift server runs on.
   hive_server_port=10000
   thrift_version=7
   ```

2. Below the `[[interpreters]]` of `[notebook]`, add:

   ```ini
   [[[hive]]]
   name=Hive
   interface=hiveserver2
   ```


And restart Hue, open the Editors and start typing your first queries!

### Development environment

#### Lint configs

* [pyproject.toml](https://github.com/cloudera/hue/blob/master/pyproject.toml): Ruff (Python lint and format), pytest and coverage settings
* [.eslintrc.js](https://github.com/cloudera/hue/blob/master/.eslintrc.js)
* [.prettierrc](https://github.com/cloudera/hue/blob/master/.prettierrc)
* [.stylelintrc](https://github.com/cloudera/hue/blob/master/.stylelintrc)
* Git hooks: [commit message hook](https://github.com/cloudera/hue/blob/master/tools/githooks/commit-msg) and [pre-commit / pre-push hooks](https://github.com/cloudera/hue/tree/master/tools/git-hooks)

To check the commit message format locally, install the commit message hook:

```bash
cp tools/githooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

To also run ESLint on the staged JavaScript and TypeScript files before each commit, install the pre-commit hook (it installs ESLint globally if missing):

```bash
./setup-hooks.sh
```


#### Visual Studio Code

Add the `hue` directory as a workspace, then install the recommended extensions:

* [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) - Microsoft
* [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) - Astral Software
* [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) - Microsoft
* [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) - Prettier
* [Mako](https://marketplace.visualstudio.com/items?itemName=tommorris.mako) - tommorris
* [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) - Microsoft

#### PyCharm

First step is to configure pycharm to use the Hue virtual environment at `./build/env`

![Pycharm virtualenv](/images/pycharm_virtualenv.png)

Second step is to configure the debug configuration
![Pycharm debug](/images/pycharm_debug.png)

#### Eclipse

First step is to configure Eclipse to use the Hue virtual environment at `./build/env`
![Eclipse interpreter](/images/eclipse_interpreter.png)

Second step is to configure the debug configuration
![Eclipse debug](/images/eclipse_debug.png)
![Eclipse debug arguments](/images/eclipse_debug_arguments.png)
![Eclipse debug interpreter](/images/eclipse_debug_interpreter.png)


## Development process

If you face a problem, search the [Forum](https://discourse.gethue.com/) and the [bug tracker](https://github.com/cloudera/hue/issues?q=is%3Aissue+) first.

This section explains how to send a change for review.

### Setup

The Hue project uses GitHub pull requests (PRs) for code reviews. The CI (build, lint, tests) runs automatically on each PR.

If you have never used Git and GitHub, follow this [first-time setup guide](https://kbroman.org/github_tutorial/pages/first_time.html) before going further.

Clone [cloudera/hue](https://github.com/cloudera/hue) (or your fork):

```bash
git clone https://github.com/cloudera/hue
```

Create a branch named after the GitHub issue (`GH-XXX`) or with an explicit name:

```bash
git checkout master
git pull --rebase origin master
git checkout -b GH-XXX
```

Make your changes, then commit them:

```bash
git add <file>
git diff --cached
git commit -m "GH-XXX [hive] Add numExecutors option"
```

### Commit message format

The first line of each commit is checked by the CI with [`tools/ci/check_for_commit_message.sh`](https://github.com/cloudera/hue/blob/master/tools/ci/check_for_commit_message.sh), which relies on the [commit-msg hook](https://github.com/cloudera/hue/blob/master/tools/githooks/commit-msg). The only enforced rule is a maximum of 71 characters (50 recommended). By convention, start with a label for the area you are changing:

    [hive] Add numExecutors option
    [hive] Add numExecutors option (#1000)
    GH-1000 [hive] Add numExecutors option

Common labels are `[hive]`, `[impala]`, `[ui]`, `[docs]`, `[api]`, `[core]`, `[trino]`.

### Post a review

Either create the pull request with the [GitHub CLI](https://github.com/cli/cli):

```bash
gh pr create --fill --web
```

Or push your branch to your fork, for example if you are `bob`:

```bash
git remote add bob https://github.com/bob/hue
git fetch bob
git push bob HEAD:GH-1000-fix
```

Then open the pull request to `cloudera/hue` from the `https://github.com/bob/hue/tree/GH-1000-fix` page.

With the GitHub CLI, you can also ask for reviewers and enable auto-merge once all the checks are green:

```bash
gh pr create --fill --reviewer=<github_user>
gh pr merge --auto --rebase <pr_number>
```

### Update a review

Modify the previous commit:

```bash
git add <file>
git commit --amend
```

Update the pull request:

```bash
git push bob HEAD:GH-1000-fix -f
```

This re-runs the CI and notifies the reviewers.

### Merge

Once the pull request is approved and the CI checks are green, a maintainer merges it into `master`. Before that, keep your branch up to date:

```bash
git fetch origin
git rebase origin/master
```

You can follow the CI runs on [GitHub Actions](https://github.com/cloudera/hue/actions). The workflows are in [`.github/workflows`](https://github.com/cloudera/hue/tree/master/.github/workflows):

| Workflow | What it checks |
| -------- | -------------- |
| Python 3 CI (`commitflow-py3.yml`) | Commit titles, build on Python 3.11, `pytest`, `hue runruff check` |
| Frontend CI (`commitflow-frontend.yml`) | Commit titles, pinned versions, licenses, `prettier`, `eslint`, `stylelint`, `jest` |
| Docs Lint (`docs_lint.yml`) | Dead links in `docs/docs-site` (runs on docs changes) |

### Sum-up

We hope that these commands make your life easier and encourage you to [contribute to Hue](https://github.com/cloudera/hue/blob/master/CONTRIBUTING.md).

As usual, feel free to send feedback on the [Forum](https://discourse.gethue.com/) list or [GitHub issues](https://github.com/cloudera/hue/issues)!


## API server

### The Hue server

![Web Back-end](/images/webbackend.png)

Hue is a web application built on the Django python web framework.
Django, running on a WSGI container/web server (Gunicorn or CherryPy), manages
the url dispatch, executes application logic code, and puts together the views
from their templates. Django uses a database (typically MySQL or PostgreSQL) to manage session data, and Hue applications can use it as well
for their "models". (For example, the saved Editor stores saved queries in the database.)

In addition to the web server, some Hue applications run
daemon processes "on the side". Some examples are the `Celery Task Server`, `Celery Beat`.

![Reference Architecture](/images/hue_architecture.png)

### File layout

The Hue "framework" is in `desktop/core/` and contains the Web components.
`desktop/libs/` is the API for talking to various Hadoop services.
The installable apps live in `apps/`.  Third-party Python packages are listed in
`desktop/core/base_requirements.txt`. A few vendored packages live in `desktop/core/ext-py3/`.

The typical directory structure inside an application includes:

```text
src/        Python/Django code (models.py, urls.py, views.py, forms.py, settings.py)
conf/       configuration (.ini) files to be installed
static/     static HTML/JS resources and help docs
templates/  data to be put through a template engine
locales/    localizations in multiple languages
```

For the URLs within your application, make your own `urls.py`
which will be automatically rooted at `/yourappname/` in the global
namespace. See `apps/about/src/about/urls.py` for an example.

### Configurations

#### File

Hue uses a typed configuration system that reads configuration files (in an
ini-style format). By default, Hue loads all `*.ini` files in the `desktop/conf`
directory (or the directory pointed to by the `HUE_CONF_DIR` environment variable). The configuration files have the following format:

```ini
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
```



#### Variables

Your application's `conf.py` is special. It provides access to the configuration file (and even
default configurations not specified in the file). Using the above example, your `conf.py` should
define the following.

A `desktop.lib.conf.Config` object for `app_property`, such as:

```python
MY_PROPERTY = Config(key='app_property', default='Beatles', help='blah')
```

You can access its value with `MY_PROPERTY.get()`.

A `desktop.lib.conf.ConfigSection` object for `section_a`, such as:

```python
SECTION_A = ConfigSection(
  key='section_a',
  help='blah',
  members=dict(
    AWEIGHT=Config(key='a_weight', type=int, default=0),
    AHEIGHT=Config(key='a_height', type=int, default=0)))
```

You can access the values with `SECTION_A.AWEIGHT.get()`.

A `desktop.lib.conf.UnspecifiedConfigSection` object for `filesystems`, such as:

```python
FS = UnspecifiedConfigSection(
  key='filesystems',
  each=ConfigSection(members=dict(
    nn_host=Config(key='namenode_host', required=True))))
```



### Saving documents

Each app used to have its own model to store its data (e.g. a saving a SQL query, query history...). All the models have been unified into a single Document2 model in the desktop app:

`desktop/core/src/desktop/models.py`.

The `Document2` model provides automatically creation, sharing and saving. It persists the document data into a json field, which limits the need for database migrations and simplifies the interaction with the frontend.

`Document2` is based on [Django models](https://docs.djangoproject.com/en/5.2/#the-model-layer),
Django's Object-Relational Mapping (ORM) framework.

### Authentication backends

Hue exposes a configuration flag ("auth") to configure a custom authentication [backend](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/auth/backend.py).
See [writing an authentication backend](https://docs.djangoproject.com/en/5.2/topics/auth/customizing/#writing-an-authentication-backend)
for more details.

In addition to that, backends may support a `manages_passwords_externally()` method, returning True or False, to tell the user manager application whether or not changing passwords within Hue is possible.

### Using and installing Thrift

Right now, we check in the generated thrift code.
To generate the code, you'll need the thrift binary version 0.9.0.
Please download from http://thrift.apache.org/.

The modules using Thrift have some helper scripts like `regenerate_thrift.sh`
for regenerating the code from the interfaces.

### Upgrades

After upgrading the version of Hue, run this command to make sure the database has the correct tables and fields:

```bash
./build/env/bin/hue migrate
```

### Debugging tips and tricks

* Set `DESKTOP_DEBUG=1` as an environment variable if you want logs to go to stderr
  as well as to the respective log files.
* Use `runserver`. If you want to set a CLI breakpoint, insert
  `breakpoint()` into your code.
* Django tends to restart its server whenever it notices a file changes.  For
  certain things (like configuration changes), this is not sufficient.  Restart
  the server whole-heartedly.
* We recommend developing with the browser developer tools open.

Special environment variables:

```text
DESKTOP_LOGLEVEL=<level>
  level can be DEBUG, INFO, WARN, ERROR, or CRITICAL.
  When specified, the console logger is set to the given log level. A console
  logger is created if one is not defined.

DESKTOP_DEBUG
  A shorthand for DESKTOP_LOGLEVEL=DEBUG.

DESKTOP_PROFILE
  Turn on Python profiling. The profile data is saved in a file. See the
  console output for the location of the file.

DESKTOP_LOG_DIR=$dir
  Specify the Hue log directory.

DESKTOP_DB_CONFIG=$db engine:db name:test db name:username:password:host:port
  Specify alternate DB connection parameters for Hue to use. Useful for
  testing your changes against, for example, MySQL instead of SQLite. The
  string is a colon-delimited list.
```


## User interface (UI)

Developing applications for Hue requires a minimal amount of CSS
(and potentially JavaScript) to use existing functionality.

In a nutshell, frontend development uses:

* [React](https://react.dev/) with [TypeScript](https://www.typescriptlang.org/) for all new UI, built with [Ant Design](https://ant.design/) and Cloudera UI (`cuix`) components. See the [frontend contributing guide](https://github.com/cloudera/hue/blob/master/contributing-frontend.md).
* SCSS (using BEM naming) for new styles
* [Mako](https://www.makotemplates.org/) as the server-side templating language
* Legacy code in Knockout.js, jQuery, Vue.js and [Bootstrap](https://getbootstrap.com/) 2, which is progressively being migrated to React

### JavaScript and TypeScript

The frontend source lives in `desktop/core/src/desktop/js` and is built into webpack bundles. Third-party libraries that are not managed by npm live under `desktop/core/src/desktop/static/desktop/ext`.

First make sure all third-party dependencies defined in `package.json` are installed into `node_modules/`:

```bash
npm install
```

Run this again after changing `package.json`.

To generate the bundles run:

```bash
npm run webpack
npm run webpack-workers
npm run webpack-login
```

During development, the bundles are regenerated when files change with:

```bash
npm run dev
```

If you work on the web workers or the login page, also run `npm run dev-workers` or `npm run dev-login`.

Before sending a review, run the checks that the CI runs and fix the issues they report:

```bash
npm run lint-fix
npm run prettier-fix
npm run style-lint-fix
```

### CSS and SCSS

Write new styles in SCSS (`.scss` files next to the component, with BEM class names) and use the existing variables instead of hardcoded colors. Do not add new Less files; migrate a Less file to SCSS when you touch it.

SCSS files under `desktop/core/src/desktop/js` are bundled by webpack. Lint them with:

```bash
npm run style-lint
```

Legacy Less files live in `desktop/core/src/desktop/static/desktop/less` and are compiled with Grunt. Hue also uses [Bootstrap](https://getbootstrap.com/) 2 CSS styles and layouts in the legacy pages. After changing a `.less` file, rebuild the CSS with:

```bash
npm run less
```

Or run in watch mode to regenerate the `.css` on any change to the `.less` files:

```bash
npm run less-dev
```


### Icons

You should create an icon for your application that is a transparent png sized
24px by 24px. Your `settings.py` file should point to your icon via the `ICON`
variable. The `create_desktop_app` command sets `ICON` in the `settings.py` of the new app. Put your icon at that path.

**NOTE:** If you do not define an application icon, your application will not show up in the navigation bar.

Hue ships with Twitter Bootstrap and Font Awesome 4 so you have plenty of scalable icons to choose from. You can style your elements to use them like this (in your Mako template):

```html
<!-- show a trash icon in a link -->
<a href="#something"><i class="icon-trash"></i> Trash</a>
```

### Static files

For better performance, Hue uses the Django staticfiles app. In production mode, if you edit
some static files, you need to run this command or `make apps`. No action is needed in
development mode.

```bash
./build/env/bin/hue collectstatic
```

## Testing

### The short story

Prerequisite: build Hue and install the test dependencies once:

```bash
export PYTHON_VER=python3.11
make apps test_prep
```

Run the API unit tests:

```bash
./build/env/bin/pytest
```

Run the user interface tests:

```bash
npm run test
```

When you open a pull request, [GitHub Actions](https://github.com/cloudera/hue/actions/) automatically runs the unit tests, the linters and the commit message check.

### Running the API tests

The pytest configuration (test discovery, markers, report and coverage options) is in the `[tool.pytest.ini_options]` section of `pyproject.toml`. By default, tests marked `integration` are skipped.

Pytest discovers the files named `tests.py`, `test_*.py`, `*_tests.py`, `tests_*` or `*_test.py`. It then collects:

1. Test functions or methods prefixed with `test_` outside of a class.
2. Test functions or methods prefixed with `test_` inside classes prefixed with `Test`.

Refer to `desktop/libs/notebook/src/notebook/connectors/trino_tests.py` for an example of how tests are organized.

Run all the unit tests (this can take several minutes):

```bash
./build/env/bin/pytest
```

Run the tests of a particular app or directory:

```bash
./build/env/bin/pytest apps/filebrowser
```

Run the tests of a specific class:

```bash
./build/env/bin/pytest apps/useradmin/src/useradmin/tests.py::TestUserAdmin
```

Run a specific test in a class:

```bash
./build/env/bin/pytest apps/useradmin/src/useradmin/tests.py::TestUserAdmin::test_user_admin
```

If a test fails with an error similar to:

```text
ValueError: The file 'desktop/js/bundles/hue/vendors~hue~notebook~tableBrowser-chunk-f7c8562ecf79bc8f1f16.js' could not be found with <django.contrib.staticfiles.storage.CachedStaticFilesStorage object at 0x7faf77042630>.
```

rebuild the collection of static files:

```bash
./build/env/bin/hue collectstatic
```

### Running the UI tests

Tests live next to the file under test. The test filename must end with `.test.ts`, `.test.tsx`, `.test.js` or `.test.jsx` (see `testMatch` in `jest.config.js`):

```text
someFile.ts         <- File under test
someFile.test.ts    <- File containing tests
```

For React components, use [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) (`@testing-library/react`).

Run all the tests once:

```bash
npm test
```

Run the tests of a specific file once:

```bash
npm test -- foo.test.js
```

Run the tests in watch mode:

```bash
npm run test-dev
```

In watch mode, Jest detects changes to all files and re-runs the related tests. Press `w` in the console to see the options to target specific files or tests. To update the test snapshots, let the first run of the tests complete and then press `u`.

On some operating systems, like Ubuntu, running the tests via a global Jest can avoid system hangs:

```bash
npm install jest --global
```

For example:

```bash
jest calciteAutocompleteParser.Select.stream.test.js --testPathIgnorePatterns=[]
jest calciteAutocompleteParser --testPathIgnorePatterns=[]
```

Update the snapshots of all tests:

```bash
jest --updateSnapshot
```

The tests of some SQL parsers (for example Calcite, Presto or Phoenix) are skipped by default via `testPathIgnorePatterns` in `jest.config.js`. Pass `--testPathIgnorePatterns=[]` as above to run them.


#### Testing KO Js components

koSetup provides utilities to test Knockout components and bindings using `jsdom` from `jest`.

An example of component test:

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

An example of a binding test:

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


### Coverage

The pytest options in `pyproject.toml` already collect the coverage. After `./build/env/bin/pytest`, the reports are in the `reports/` directory (`reports/code-cov/coverage-html` for HTML, `reports/pytest/report.html` for the test report). The `pytest-cov` package is installed by `make test_prep`.

For JavaScript, run:

```bash
npm run test-coverage
```

The report is written to `reports/jest`.


### Python linting

Hue uses [Ruff](https://docs.astral.sh/ruff/) for linting its backend codebase. The Ruff configuration is in the [pyproject.toml](https://github.com/cloudera/hue/blob/master/pyproject.toml) file at the project root (2-space indentation, 140 characters per line).

The GitHub Actions CI also runs Ruff on pull requests.

To check for linting violations **on the modified files**, run:

```bash
./build/env/bin/hue runruff check
```

By default, this lints all the Python files modified compared to `origin/master`. To use another base branch, pass `--diff-branch` before the Ruff command:

```bash
./build/env/bin/hue runruff --diff-branch=<base_branch> check
```

Ruff can autofix most of the flagged violations:

```bash
./build/env/bin/hue runruff check --fix
```

Some violations can't be autofixed and require manual fixing. The other Ruff commands are listed in the [Ruff documentation](https://docs.astral.sh/ruff/configuration/#full-command-line-interface).

### Frontend linting

The CI runs the following checks on the frontend code (see `package.json` for the exact commands):

```bash
npm run prettier      # formatting
npm run lint          # ESLint
npm run style-lint    # Stylelint (SCSS and legacy Less)
```

Use `npm run prettier-fix`, `npm run lint-fix` and `npm run style-lint-fix` to autofix.


### Integration tests

Integration tests need a live cluster or service and are skipped by default (`-m 'not integration'` in `pyproject.toml`). They are tagged with the `integration` pytest marker (or `requires_hadoop` for a live Hadoop cluster) at the class or method level:

```python
import pytest

@pytest.mark.integration
class TestWithLiveCluster:
  def test_something(self):
    ...
```

Point Hue to the live cluster in its configuration before running them.

Note: the Python integration tests are going to be ported to a more modern CI with dependencies provided by containers.


## Releasing

The checklist below details the steps. Then send the release notes to the [Forum](https://discourse.gethue.com/) and the [Hue account on X](https://twitter.com/gethue).

Also update https://wikipedia.org/wiki/Hue_(Software).

### Before you start

* Write access to the repository, to the Docker Hub organization and to the NPM package (for the steps you perform)
* A clean checkout of the commit to release, with the build prerequisites from the [quick start](#requirements)

### Version

Update the version to the one being released (for example 4.12.0) in these files:

| File | Change |
| ---- | ------ |
| `VERSION` | `VERSION="4.12.0"` |
| `NOTICE.txt` | First line: `Cloudera Hue 4.12.0` |
| `maven/pom.xml` | Project version: `4.12.0-SNAPSHOT` |
| `desktop/libs/librdbms/java/pom.xml` | Parent version: `4.12.0-SNAPSHOT` |

The `package.json` version is the version of the `gethue` NPM package, which is versioned independently of Hue. Only bump it when you publish a new NPM package.

Then add the release notes page `docs/docs-site/content/releases/release-notes-4.12.0.md`, using the previous page as a template. Keep the front matter `weight` ordering consistent with the other release notes.

How to count the number of commits since the last release:

```bash
git log --oneline --since=2023-01-01 | grep 'release' -n -i
git log --oneline -449 > commits.txt
```

Then convert them to a Markdown list with links:

```bash
sed 's/^\([[:alnum:]]\{10\}\)/[\1](https:\/\/github.com\/cloudera\/hue\/commit\/\1)/' commits.txt | sed 's/^\(.*\)/* \1/' > commits.md
```

And add them and the authors to the release notes:

```bash
git log --pretty="%an" | sort | uniq | sed 's/^\(.*\)/* \1/' > authors.txt
```

Optionally, add a release blog post in `docs/gethue/content/en/posts`.

### Git

Commit the changes above and merge them into `master` via a pull request. Then push the release branch (from the release commit):

```bash
git push origin HEAD:branch-4.12.0
```

Tag the release:

```bash
git tag -a release-4.12.0 -m "release-4.12.0"
git push origin release-4.12.0
```

Draft a new release on [GitHub releases](https://github.com/cloudera/hue/releases).

### Tarball

Build the tarball from the release tag:

```bash
git checkout release-4.12.0
export PYTHON_VER=python3.11
make prod
```

The tarball is generated under `build/release/prod/`.

You might need to upgrade the [mysqlclient](/administrator/installation/dependencies/#mysql--mariadb) if you see:

```text
_mysql.c:44:10: fatal error: my_config.h: No such file or directory
  44 | #include "my_config.h"
     |          ^~~~~~~~~~~~~
```

The source of the release is available at `https://github.com/cloudera/hue/archive/release-4.12.0.zip`.

Publish the tarball to the downloads host (for example the CDN of gethue.com):

```bash
scp hue-4.12.0.tgz <user>@<downloads_host>:<downloads_directory>
```

### Docker

The Dockerfiles are in `tools/docker/hue` and `tools/docker/nginx`. Images are published on [Docker Hub](https://hub.docker.com/u/gethue/).

```bash
docker build https://github.com/cloudera/hue.git#release-4.12.0 -t gethue/hue:4.12.0 -f tools/docker/hue/Dockerfile
docker tag gethue/hue:4.12.0 gethue/hue:latest
docker images
docker login -u gethue
docker push gethue/hue
docker push gethue/hue:4.12.0

docker build https://github.com/cloudera/hue.git#release-4.12.0 -t gethue/nginx:4.12.0 -f tools/docker/nginx/Dockerfile
docker tag gethue/nginx:4.12.0 gethue/nginx:latest
docker push gethue/nginx
docker push gethue/nginx:4.12.0
```

### Kubernetes and Helm

The chart is in `tools/kubernetes/helm/hue`. Bump `version` in its `Chart.yaml` if the chart changed, then build the package from the Helm root directory:

```bash
cd tools/kubernetes/helm/
helm package hue
```

Then publish it to your Helm repository host and index the package:

```bash
scp hue-<chart_version>.tgz <user>@<helm_host>:<helm_repo_directory>
ssh <user>@<helm_host>
cd <helm_repo_directory>
helm repo index .
```

### Documentation

The documentation site is refreshed automatically and runs as a container (see `tools/docker/documentation`).

Otherwise, [build it](#documentation-1) and push it to the docs host.

Resources like images go to the CDN:

```bash
scp <image_file> <user>@<cdn_host>:<cdn_uploads_directory>
```


### NPM registry

To publish the `gethue` package to the [NPM registry](https://www.npmjs.com/package/gethue), bump the `version` in `package.json` and run:

```bash
npm run publish-gethue
```

This regenerates the SQL parsers (`make sql-all-parsers`), builds the package with `webpack.config.npm.js` into `npm_dist` and publishes it. You need to be logged in to NPM (`npm login`).

## Building

### Dev Docker

Try basic changes [in 3 minutes](https://gethue.com/quick-start-a-hue-development-environment-in-3-minutes-with-docker/) without compiling Hue locally hence avoiding the setting up of [dependencies](/developer/):

```bash
git clone https://github.com/cloudera/hue.git
cd hue
cp desktop/conf/pseudo-distributed.ini.tmpl desktop/conf/pseudo-distributed.ini
```

Then edit the `[[database]]` section to specify a proper database, here MySQL:

```ini
host=127.0.0.1 # Don't use 'localhost' if Docker
engine=mysql
user=hue
password=hue
name=huedb
```

Then map the local Hue source code into the running container (so that local edits are seen in the running Hue):

```bash
sudo docker run -it -v $PWD/apps:/usr/share/hue/apps -v $PWD/desktop:/usr/share/hue/desktop -v $PWD/desktop/conf/pseudo-distributed.ini:/usr/share/hue/desktop/conf/z-hue.ini --network="host" gethue/hue
```

Note: code updates won’t be seen after the Docker container runs. For this, Hue needs to be started in dev server mode by replacing the `supervisor` line of [`startup.sh`](https://github.com/cloudera/hue/blob/master/tools/docker/hue/startup.sh) by:

```bash
./build/env/bin/hue runserver 0.0.0.0:8888
```

and recompiling the Docker image. It will then auto-restart on Python code changes. For JavaScript, those would need to be [compiled](/developer/development/#javascript-and-typescript).


### Documentation

Install [Hugo](https://gohugo.io/getting-started/quick-start/). The `Docs Lint` CI job builds the site with Hugo 0.69.0, so use that version to check your changes locally (the theme does not render with recent Hugo versions). Each page has a link to its own source file in the top right corner.

Build the [source](https://github.com/cloudera/hue/tree/master/docs/docs-site) and see live changes:

```bash
cd docs/docs-site
hugo serve
```

The [Docs Lint](https://github.com/cloudera/hue/blob/master/.github/workflows/docs_lint.yml) workflow serves the site and checks it for dead links with [Lychee](https://github.com/lycheeverse/lychee) on pull requests that change `docs/docs-site`. You can run the same check locally against `http://localhost:1313/`.

To build the static site, run `hugo` in `docs/docs-site` (or `make doc` from the Hue root) and grab the `public` directory.

### gethue.com Blog & Website

Like for the [Documentation](#documentation-1), install Hugo. The content for each language is in its [own directory](https://github.com/cloudera/hue/tree/master/docs/gethue/content).

Blog posts are located in [docs/gethue/content/en/posts](https://github.com/cloudera/hue/tree/master/docs/gethue/content/en/posts). Here is an example of the source of a [release post](https://github.com/cloudera/hue/commit/fcc0078a4ba59e450a2e081ad0cc27e482a8703b#diff-9b1261f162231be68d3c30329e73b458c874858c0d685cf0c213fdace3309679).

Build it and see live changes:

```bash
cd docs/gethue
hugo serve
```

This automatically starts one server for each language domain.

gethue.com refresh is currently manually kicked but this will be automated soon.

### SQL autocomplete

The parsers are generated with a patched [jison](https://github.com/JohanAhlen/jison), which is installed as a dependency of `tools/jison` (no global install is needed). To regenerate the generic, Hive and Impala parsers, run:

```bash
make sql-all-parsers
```

See [SQL parsers](#sql-parsers) for the other dialects.

### Ace editor

After modifying files under `tools/ace-editor`, run the following to build `ace.js`:

```bash
npm install
make ace
```

### Language references

The tools for generating the embedded language reference manuals are in `tools/sql-docs/`.

#### Hive
The Hive documentation is generated directly from the Hive wiki by using an exported epub file.

1. Goto https://cwiki.apache.org/confluence/display/Hive/LanguageManual
2. Click the three dots '...' in the upper right corner
3. Click 'Export to EPUB'
4. In the Hue folder run:

   ```bash
   node tools/sql-docs/hiveExtractor.js --epub /path/to/epub/file
   ```

#### Impala
The Impala documentation is generated from the ditamap files in the Impala GitHub repo.

1. Clone the Impala repo next to hue from https://github.com/apache/impala
2. In the Hue folder run:

   ```bash
   node tools/sql-docs/docExtractor.js -c hue -f ../impala/docs/ -d impala_langref.ditamap,impala_keydefs.ditamap,impala.ditamap -o desktop/core/src/desktop/static/desktop/docs/impala/ -m desktop/core/src/desktop/templates/impala_doc_index.mako
   ```

### Internationalization

How to compile all the messages:

```bash
make locales
```

How to compile the messages of one app:

```bash
cd apps/beeswax
make compile-locale
```

How to create a new locale for an app:

```bash
cd $APP_ROOT/src/$APP_NAME/locale
$HUE_ROOT/build/env/bin/pybabel init -D django -i en_US.pot -d . -l fr
```

## SQL parsers

The parsers are the flagship part of Hue and power extremely advanced autocompletes and other [SQL functionalities](/user/querying/#autocomplete). They run on the client side and come with just a few megabytes of JavaScript that are cached by the browser. This provides a very reactive experience to the end user and let you [import them](#reusing-a-parser-in-your-project) as classic JavaScript modules for your own development needs.

While the dynamic content like the list of tables, columns is obviously fetched via [remote endpoints](/administrator/configuration/connectors/), all the SQL knowledge of the statements is available.

The main dialects are:

* Apache Hive
* Apache Impala
* Presto
* Apache Calcite

But there are more! See all the currently shipped [SQL dialects](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql).

This guide takes you through the steps necessary to create an autocompleter for any [SQL dialect](/administrator/configuration/connectors/#databases) in Hue. The major benefits are:

* Proposing only valid syntax in the autocomplete
* Getting the list of tables, columns, UDFs... automatically
* Suggesting fixes
* Diffing, formatting... queries

**Looking at quick code examples?**

- Adding `SHOW` syntax to Flink SQL [GH-1399](https://github.com/cloudera/hue/issues/1399)
- Adding a Dask SQL parser and connector [GH-1480](https://github.com/cloudera/hue/issues/1480)

### Parser theory

There are several parsers in Hue already (e.g. one for Impala, one for Hive..) and a generic SQL that is used for other dialects. The parsers are written using a [bison](https://www.gnu.org/software/bison/) grammar and are generated with [jison](https://github.com/zaach/jison). They are 100% Javascript and live on the client side, this gives the performance of a desktop editor in your browser.

Building a dedicated parser is more effort but it then allows a very rich end user experience, e.g.:

* Handle invalid/incomplete queries and propose suggestions/fixes
* date_column = <Date compatible UDF ...>
* Language reference or data samples just by pointing the cursor on SQL identifiers
* Leverage the parser for risk alerts (e.g. adding automatic LIMIT) or proper re-formatting

#### Structure

Normally parsers generate a parse tree but for our purposes we don’t really care about the statement itself but rather about what should happen when parts of a particular statement is encountered. During parsing the state is kept outside the parse tree and in case of syntax errors this enables us to provide some results up to the point of the error. There are two ways that incomplete/erroneous statements are handled, first we try to define most of the incomplete grammar and secondly we rely on the “error” token which allows the parser to recover.

The parsers provide one function, parseSql, that accepts the text before the cursor and the text after the cursor as arguments. The function returns an object containing instructions on what to suggest given the input.

As an example:

    sqlParserRepository.getAutocompleteParser('impala').then(parser => {
      console.log(parser.parseSql('SELECT * FROM customers'));
    });

Would output something like:

    {
      definitions: [],
      locations: (6) [{…}, {…}, {…}, {…}, {…}, {…}],
      lowerCase: false,
      suggestAggregateFunctions: {tables: [Array(1)]},
      suggestAnalyticFunctions: true,
      suggestColumns: {source: "select", tables: [{identifierChain: [{name: "customers"}]}]},
      suggestFunctions: {},
      suggestKeywords: (8) [{…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}]
    }

We take this output and link it to various sources of metadata to provide the list of suggestions the user finally sees. In this case we’d use the data from “suggestColumns” to call the backend for all the columns of the “customers” table. We’d also use the functions library to list all the UDFs etc.

Here’s a list of some of the different types of suggestions the parser can identify:

    suggestAggregateFunctions
    suggestAnalyticFunctions
    suggestColRefKeywords
    suggestColumnAliases
    suggestColumns
    suggestCommonTableExpressions
    suggestDatabases
    suggestFilters
    suggestFunctions
        suggestGroupBys
    suggestHdfs
    suggestIdentifiers
    suggestJoinConditions
    suggestJoins
    suggestKeywords
    suggestOrderBys
    suggestSetOptions
    suggestTables
    suggestValues

Parsers are generated and added to the repository with `generateParsers.js` under `tools/jison/`. For instance, to generate all the Impala parsers, run the following in the Hue folder:

```bash
cd tools/jison
npm install
node generateParsers.js impala
```

The arguments are parser names (for example `hiveAutocompleteParser`), dialect name prefixes (for example `hive`) or `all`. Each dialect folder under `desktop/core/src/desktop/js/parse/sql/` that contains a `jison/structure.json` file is picked up automatically.

In reality two parsers are generated per dialect, one for syntax and one for autocomplete. The syntax parser is a subset of the autocomplete parser with no error recovery and without the autocomplete specific grammar.

The jison grammar files of each dialect are in its `jison` folder, e.g. [parse/sql/hive/jison](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql/hive/jison). The generated parsers are committed next to them in [parse/sql](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql), together with their tests.

Parsers share as much of the common syntax as possible via modules, so that it is easy to improve the specificity of any of them without starting from scratch.

e.g. in [structure.json](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/js/parse/sql/hive/jison/structure.json):

```json
{
  "lexer": "sql.jisonlex",
  "autocomplete": [
    "../../generic/jison/autocomplete_header.jison",
    "abort/abort_transactions.jison",
    "common/table_constraint.jison",
    "alter/alter_common.jison",
    "alter/alter_connector.jison",
    "alter/alter_database.jison",
    ...
  ],
  "syntax": [
    "../../generic/jison/syntax_header.jison",
    "abort/abort_transactions.jison",
    "common/table_constraint.jison",
    "alter/alter_common.jison",
    ...
  ]
}
```

#### The grammar

In a regular SQL parser you might define the grammar of a select statement like this:

    SelectStatement
      : 'SELECT' ColumnList 'FROM' Identifier
      ;

    ColumnList
      : Identifier
      | ColumnList ',' Identifier
      ;

This would be able to parse a statement like 'SELECT a, b, c FROM some_table' (depending on lexer definitions of course).

#### Notion of cursor

To turn this into an autocompleter we add the notion of a cursor. Often, the user has the cursor somewhere in the statement. In the previous section, we were assuming that the query was already typed and the user had not mouse cursor within it.

The cursor is represented as an obscure character that is unlikely to be used in a statement. Currently '\u2020' was picked, the dagger, identified as 'CURSOR' in the lexer. The actual parsed string is therefore beforeCursor + '\u2020' + afterCursor.

For the statement above we’d add an extra rule with an _EDIT postfix like this:

    SelectStatement
      : 'SELECT' ColumnList 'FROM' Identifier
      ;

    SelectStatement_EDIT
      : 'CURSOR' --> { suggestKeywords: ['SELECT'] }
      | 'SELECT' ColumnList_EDIT
      | 'SELECT' ColumnList 'CURSOR' --> { suggestKeywords: ['FROM'] }
      | 'SELECT' ColumnList 'FROM' 'CURSOR'  --> { suggestTables: {} }
      | 'SELECT' ColumnList_EDIT 'FROM' Identifier --> { suggestColumns: { table: $4 } }
      ;

So for example if a cursor without any text is encountered, it will tell us to suggest the 'SELECT' keyword etc.

#### Why an extra space

The extra space is just for the documentation to show the complete output with locations, it should indeed be clarified a bit. The reason for the extra space is that the parser ignores partial words, consider the following where | denotes the cursor:

    SELECT * FROM som|

The parser will treat this as "SELECT * FROM |" and it leaves it up to the editor logic to filter any tables, starting with "som".

### Tutorial: Creating a parser

The goal is to create from scratch a new parser for the PostgreSQL database.

#### Prerequisites

Make sure you have a [development](/administrator/installation/dependencies/) Hue and ran `npm install` in the Hue folder and in `tools/jison` (this installs the patched [jison](#sql-autocomplete)). Then configure a [PostgreSQL interpreter](/administrator/configuration/connectors/#postgresql).

In the Hue folder:

```bash
./build/env/bin/pip install psycopg2-binary
```

and edit your Hue config `desktop/conf/pseudo-distributed.ini` to contain:

```ini
[notebook]
[[interpreters]]
[[[postgresql]]]
name = postgresql
interface=sqlalchemy
options='{"url": "postgresql://hue:hue@localhost:31335/hue"}'
```

The parser generator discovers every dialect folder under `desktop/core/src/desktop/js/parse/sql/` that contains a `jison/structure.json` file. Create the new dialect by copying the `generic` one, in the Hue folder:

```bash
cd desktop/core/src/desktop/js/parse/sql
cp -r generic postgresql
cd postgresql
rm genericAutocompleteParser*.js genericAutocompleteParser.test.ts genericSyntaxParser*.js
mkdir test
```

Then register the new dialect in `desktop/core/src/desktop/js/parse/sql/sqlParserRepository.ts` by adding a `postgresql` entry next to the `hive` one in both `AUTOCOMPLETE_MODULES` (importing `./postgresql/postgresqlAutocompleteParser`) and `SYNTAX_MODULES` (importing `./postgresql/postgresqlSyntaxParser`).

Generate the new `postgresqlAutocompleteParser.js` and `postgresqlSyntaxParser.js`:

```bash
cd tools/jison
npm install
node generateParsers.js postgresql
```

The jison files are under `desktop/core/src/desktop/js/parse/sql/postgresql/jison/` and the tests go in `desktop/core/src/desktop/js/parse/sql/postgresql/test`.

To regenerate the parsers after changes to the jison files, run the same command again:

```bash
cd tools/jison
node generateParsers.js postgresql
```

The tool reports any problems with the grammar. Note that it might still generate a parser if the grammar isn’t ambiguous, but it’s likely that there will be test failures.

#### Extending the grammar

This gives you an idea on how to add custom syntax to the newly generated postgresql parser. For this example we’ll add the [REINDEX](https://www.postgresql.org/docs/9.1/sql-reindex.html) statement as it’s quite simple.

    REINDEX { INDEX | TABLE | DATABASE | SYSTEM } name [ FORCE ]

We’ll start by adding a test. Create `postgresqlAutocompleteParser.test.js` in the test folder, modeled on the [Hive tests](https://github.com/cloudera/hue/tree/master/desktop/core/src/desktop/js/parse/sql/hive/test):

```js
import postgresqlAutocompleteParser from '../postgresqlAutocompleteParser';

describe('postgresqlAutocompleteParser.js', () => {
  beforeAll(() => {
    postgresqlAutocompleteParser.yy.parseError = function (msg) {
      throw Error(msg);
    };
  });

  const assertAutoComplete = testDefinition => {
    const debug = false;

    expect(
      postgresqlAutocompleteParser.parseSql(
        testDefinition.beforeCursor,
        testDefinition.afterCursor,
        debug
      )
    ).toEqualDefinition(testDefinition);
  };

  // Add the tests below here
});
```

Then add the following tests inside the main `describe` function:

    describe('REINDEX', () => {
      it('should handle "REINDEX TABLE foo FORCE; |"', () => {
        assertAutoComplete({
          beforeCursor: 'REINDEX TABLE foo FORCE;  ',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['SELECT'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "REINDEX |"', () => {
        assertAutoComplete({
          beforeCursor: 'REINDEX ',
          afterCursor: '',
          noErrors: true,
          containsKeywords: ['INDEX', 'DATABASE'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

When we now run `npm run test -- postgresqlAutocompleteParser.test.js` there should be two failing tests.

Alternatively, if using Jest directly and working on parsers currently being skipped in the CI, provide matching file names and an empty blacklist file pattern. e.g.:

    jest calciteAutocompleteParser.Select.stream.test.js --testPathIgnorePatterns=[]
    jest calciteAutocompleteParser --testPathIgnorePatterns=[]

Next we’ll have to add the keyword to the lexer, let’s open `sql.jisonlex` in the jison folder for postgresql and add the following new tokens:

    'REINDEX'                                  { parser.determineCase(yytext); return 'REINDEX'; }
    'INDEX'                                    { return 'INDEX'; }
    'SYSTEM'                                   { return 'SYSTEM'; }
    'FORCE'                                    { return 'FORCE'; }

Now let’s add the grammar, starting with the complete specification. For simplicity we’ll add it in `sql_main.jison`, at the bottom of the file add:

    DataDefinition
    : ReindexStatement
    ;

    ReindexStatement
    : 'REINDEX' ReindexTarget RegularOrBacktickedIdentifier OptionalForce
    ;

    ReindexTarget
    : 'INDEX'
    | 'TABLE'
    | 'DATABASE'
    | 'SYSTEM'
    ;

    OptionalForce
    :
    | 'FORCE'
    ;

"DataDefinition" is an existing rule and this extends that rule with "ReindexStatement".

Save the files and first run `node tools/jison/generateParsers.js postgresql` then `npm run test -- postgresqlAutocompleteParser.test.js` and we should be down to one failing test.

For the next one we’ll add some keyword suggestions after the user has typed REINDEX, we’ll continue below the ReindexStatement in `sql_main.jison`:

    DataDefinition_EDIT
    : ReindexStatement_EDIT
    ;

    ReindexStatement_EDIT
    : 'REINDEX' 'CURSOR'
      {
        parser.suggestKeywords(['DATABASE', 'INDEX', 'SYSTEM', 'TABLE']);
      }
    ;

Again, run `cd  tools/jison/; node generateParsers.js postgresql` then `npm run test -- postgresqlAutocompleteParser.test.js` and the tests should both be green.

We also want the autocompleter to suggest the keyword REINDEX when the user hasn’t typed anything, to do that let’s first add the following test with the other new ones in `postgresqlAutocompleteParser.test.js`:

    it('should suggest REINDEX for "|"', () => {
      assertAutoComplete({
        beforeCursor: '',
        afterCursor: '',
        noErrors: true,
        containsKeywords: ['REINDEX'],
        expectedResult: {
          lowerCase: false
        }
      });
    });

For this to pass we need to add REINDEX to the list of DDL and DML keywords in the file `sqlParseSupport.js` next to the generated parser (`desktop/core/src/desktop/js/parse/sql/postgresql/sqlParseSupport.js`). Find the function `parser.suggestDdlAndDmlKeywords` and add ‘REINDEX’ to the keywords array. Now run `npm run test -- postgresqlAutocompleteParser.test.js` and the three tests should pass.

Before you continue further, note that in this case there will be two new failing tests where the keyword ‘REINDEX’ has to be added.

In order to use the newly generated parsers we have to add them to the webpack bundles:

```bash
npm run webpack
npm run webpack-workers
```

While developing, it is faster to run the webpack bundling in the background. Open two terminal sessions and run `npm run dev` in one and `npm run dev-workers` in the other. They monitor changes to the files and rebuild a lot quicker.

After the bundling you can now test it directly in the editor!

### Syntax highlighting

New keywords might not be properly colored highlighted in the editor. This is especially true when adding a new language. Here is how to fix that.

![Missing highlighting](https://cdn.gethue.com/docs/dev/syntax_highlighting_missing.png)

Missing highlighting for 'REINDEX' keyword

![With highlighting](https://cdn.gethue.com/docs/dev/syntax_highlighting_updated.png)

With correct highlighting

#### Updating keywords

The Editor is currently visually powered by [Ace](https://ace.c9.io). The list of supported languages is found in the [mode](https://github.com/cloudera/hue/tree/master/tools/ace-editor/lib/ace/mode) directory.

For each dialect, we have two files. e.g. with PostgreSQL:

    pgsql.js
    pgsql_highlight_rules.js

The list of keywords is present in `*_highlight_rules.js` and can be updated there.

    var keywords = (
        "ALL|ALTER|REINDEX|..."
    )

Afterwards, run:

    make ace

And after refreshing the editor page, the updated mode will be activated.

#### Adding new dialect

To add a new dialect, it is recommended to copy the two files of the closest mode and rename all the names inside. For example, if we were creating a new `ksql` mode, `pgsql_highlight_rules.js` would become `ksql_highlight_rules.js` and we would rename all the references inside to `psql` to `ksql`. Same with `pgsql.js` to `ksql.js`. In particular, the name of the mode to be referenced later is in:

    KsqlHighlightRules.metaData = {
      fileTypes: ["ksql"],
      name: "ksql",
      scopeName: "source.ksql"
    };

Tip: inheritance of modes is supported by Ace, which make it handy for avoiding potential duplications.

In the Editor, the mapping between Ace's modes and the type of snippets is happening in [editor2.mako](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/templates/editor2.mako).

In the KSQL case we have:

    ksql: {
      placeHolder: '${ _("Example: SELECT * FROM stream, or press CTRL + space") }',
      aceMode: 'ace/mode/ksql',
      snippetIcon: 'fa-database',
      sqlDialect: true
    },

And cf. above [prerequisites](#prerequisites), any interpreter snippet with `ksql` will pick-up the new highlighter:

    [[[ksql]]]
    name=KSQL Analytics
    interface=ksql

### Reusing a parser in your project

The parsers ship as a pluggable [component](/developer/components/parsers).


## Connectors

Connectors provide pluggable integration to any external data service so that an admin can easily allow end users to interact with them.

* List of all the [existing connectors](/administrator/configuration/connectors/)
* Check "Potential connectors" ideas in each section
* Feel free to contact the [community](https://discourse.gethue.com/c/developer-sdk-api)

### Databases

#### SqlAlchemy

[SqlAlchemy](https://www.sqlalchemy.org) is the preferred way if the Hive API is not supported by the database. The core implementation is in [`sql_alchemy.py`](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/sql_alchemy.py) and relies on each respective SqlAlchemy dialect.

#### Hive Interface

This [asynchronous API](https://github.com/cloudera/hue/tree/master/apps/beeswax) based on the Thrift API of Hive is very mature and powers an excellent integration of Apache Hive and Apache Impala.

#### Custom

If the built-in HiveServer2 (Hive, Impala, Spark SQL), SqlAlchemy (MySQL, PostgreSQL, Oracle, Presto...) don’t meet your needs, you can implement your own connector to the notebook app:

* List of [all connectors](https://github.com/cloudera/hue/tree/master/desktop/libs/notebook/src/notebook/connectors)
* Each connector API subclasses the [Base API](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/base.py) and must implement the methods defined within. Refer to the [JDBC](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/jdbc.py) or [RdbmsApi](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/rdbms.py) for representative examples

* [Kafka SQL](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/ksql.py)
* [Solr SQL](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/solr.py)
* [JDBC](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/jdbc.py)

The JDBC API relies on a small JDBC proxy running next to the Hue API. By default it is not built unless you set the `BUILD_DB_PROXY` variable, e.g.:

```bash
BUILD_DB_PROXY=true make install
```

**Note** In the long term, SqlAlchemy is preferred as more "Python native".

#### Potential connectors

It is recommended to develop an SqlAlchemy connector if yours is not already [existing](/administrator/configuration/connectors/#databases).

### Catalogs

The backends is pluggable by providing alternative [client interfaces](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata/src/metadata/catalog):

* [Apache Atlas](https://atlas.apache.org/)
* Cloudera Navigator
* Dummy (skeleton for integrating new catalogs)

#### Apache Atlas

* [Client API](https://github.com/cloudera/hue/tree/master/desktop/libs/metadata/src/metadata/catalog/atlas_client.py)

#### Potential connectors

* [Linkedin DataHub](https://github.com/linkedin/datahub)
* [Lift Amundsen](https://github.com/lyft/amundsen)
* AWS Glue
* Google Cloud Data Catalog
* Alation

### Storages

Various storage systems can be interacted with. The [`fsmanager.py`](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/lib/fsmanager.py) is the main router to each API.

**Note** Apache Ozone as well as Ceph can be used via the S3 browser.

#### Hadoop HDFS

* [WebHdfs API](https://github.com/cloudera/hue/blob/master/desktop/libs/hadoop/src/hadoop/fs/webhdfs.py)

#### AWS S3

* [S3 API](https://github.com/cloudera/hue/blob/master/desktop/libs/aws/src/aws/s3)

#### Azure ADLS

* [ADLS v2](https://github.com/cloudera/hue/blob/master/desktop/libs/azure/src/azure/abfs)
* [ADLS v1](https://github.com/cloudera/hue/blob/master/desktop/libs/azure/src/azure/adls)

#### HBase / Key Value Stores

With just a few changes in the [Python API](https://github.com/cloudera/hue/blob/master/apps/hbase/src/hbase/api.py), the HBase browser could be compatible with Apache Kudu or Google Big Table.

### Jobs

#### Apache Spark / Livy

Based on the [Livy REST API](/administrator/configuration/connectors/#apache-spark).

* [Notebook connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/spark_shell.py)
  * PySpark
  * Scala
  * Spark SQL
* [Batch connector](https://github.com/cloudera/hue/blob/master/desktop/libs/notebook/src/notebook/connectors/spark_batch.py)

#### Schedulers

Currently only Apache Oozie is supported for your Datawarehouse, but the scheduler API is generic so that other schedulers can be added.

#### Potential connectors

* Elastic Search: a connector similar to Solr for searching. SQL querying is already supported.
* [Livy Browser API](https://github.com/cloudera/hue/blob/master/apps/jobbrowser/src/jobbrowser/apis/livy_api.py)
* [Celery API](https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/lib/scheduler/lib/beat.py)
* Apache Hive native support of query scheduling [HIVE-21884](https://issues.apache.org/jira/browse/HIVE-21884)
