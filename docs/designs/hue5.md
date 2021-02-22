# Compose

A modernized and pluggable Query Editor Service.

Compose is the name of the new packages (pypi and npm) that will be made available via Hue 5. The goal is to have traditional Hue repository import these packages (note: API/UI core logic refactoring will happen first the other way around before "filling -up" the compose API). Hue is 11 year old and saw many technically revolutions and technical shifts across the year. Hue saw 4 iterative rewrites so far and this is now #5.

The API revamp is coupled with the UI revamp, Editor 2 and Connectors.

Overall repo architecture:

    gethue/compose
      compose
        editor
        connectors
        iam (auth, users, orgs..)
        documents
        [scheduler, catalog, storage ..]
        docs
        tools, docker, docker-compose, kubernetes...
      compose-ui

A single approach like in Hue 4 instead of a multi repo like https://github.com/kubernetes projects (which has docs, demos, roadmap... repos) was taken to keep things simple/contained for now.

Note that a lot of the format/syntax will change until v1 and in the future the low level source of truth will be in the code itself while this document will stay high level.

Here are the core components:

* api server
* static UI
* DBs

And the optional services:

* Task Server
* Task Scheduler
* Web Socket Server
* Caching Server

## API

A refactored compose module (very similar to the simple REST API) is now available for easily handling the query operations. Those used to be mingled in multiple parts in Hue 4 (e.g. models, API, views, beeswax...).

High level example:

    from compose.editor import execute

    execute('SELECT 1', url="sqlite:///../db.sqlite3")
    execute('SELECT 1', {"url: "", ...})
    execute('SELECT 1', connector_id)

    execute('SELECT 1', {connector}, sync=True)

## Ops

The system will be one-click to run and provide standard Cloud CNCF monitoring to allow a transparent view of the activity of the Query Service.

* docker/docker compose of the full system
* kubernetes
* basic analytics, metrics, tracing, logs

# REST API

Clean, skeletons for modern. Leveraging Django REST Framework.
Runs on port 8005.

## Execute sync query

    curl -u hue:hue -X POST http://localhost:8000/notebook/api/execute/sqlite --data 'snippet={"statement":"SELECT 1000, 1001"}'

## Auth

CORS is enabled
No CSRF needed with JWT

Ask for JWT token:

    curl -X POST -d "username=hue&password=hue" http://localhost:8000/api-token-auth/

    curl -X POST http://localhost:8000/query/ --data 'snippet={"statement":"SELECT 1000, 1001"}' -H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6Imh1ZSIsImV4cCI6MTYxMjk3MTc0MywiZW1haWwiOiJodWVAZ2V0aHVlLmNvbSIsIm9yaWdfaWF0IjoxNjEyODg1MzQzfQ._HViX-D9h1ZfcXPAaY4KL0SNkx7MvXCH41T8Upkja3o" | jq

Basic Auth without token:

    curl -u hue:hue

## UI Integration

A live demo with the SQL Scratchpad is coming. In the meantime:

    <script src="https://unpkg.com/axios@0.21.1/dist/axios.min.js"></script>

    <script type="text/javascript">
      const API_URL = "http://localhost:8000";
      axios.defaults.baseURL = API_URL;

      axios.post('v1/iam/get/auth-token/', {username: "hue", password: "hue"}).then(function(data) {
        console.log(data['data']);

        // Util to check if cached token is still valid before asking to auth for a new one
        axios.post('v1/iam/verify/auth-token/', {token: data['data']['token']});

        axios.defaults.headers.common['Authorization'] = 'JWT ' + data['data']['token'];
      }).then(function() {
        axios.post('/v1/editor/query/sqlite', {snippet: "{\"statement\":\"SELECT 1000, 1001\""}).then(function(data) {
          console.log(data['data']);
        });

        axios.post('/v1/connectors/types/').then(function(data) {
          console.log(data['data']);
        });
      });

    </script>

## Pypi

Comes via https://pypi.org/project/gethue/

After installing it:

    python3 -m pip install gethue

Either use the Python compose API or boot the REST API:

    gunicorn core.wsgi --bind 0.0.0.0:8005

## API Live Docs

    http://127.0.0.1:8000/api/schema/swagger-ui/
    http://127.0.0.1:8000/api/schema/re-doc/

# Dev

There is no more makefile and the OS dependencies can be setup via a one time bash script:

    ./install.sh

Above script also create the virtual environment and install all the Python module dependencies from [hue/requirements.txt](hue/requirements.txt).

Afterwards all the dependencies are contained into the dedicated virtual environment:

    source python_env/bin/activate

Starting the API server is now a standard Django command:

    python manage.py runserver

## Docker

    docker build hue -t gethue/compose-api:latest -f hue/docker/Dockerfile
    docker push gethue/compose-api:latest

    docker run -it -p 8005:8000 gethue/compose-api:latest

    curl -X POST http://localhost:8000/notebook/api/execute/sqlite --data 'snippet={"statement":"SELECT 1000, 1001"}'  | jq

## CI

The CI is now based on GitHub actions to keeps all the things in one place. Direct pushes to master branch are disabled and need to go via the pre-commit CI.

Various actions are happening in order to check the styles and run the tests. e.g.

    black
    isort
    coverage
    license check
    unused imports removal
    ...

[pre-commits](https://pre-commit.com/hooks.html) hooks can be run automatically

# Hue 5 vs Hue 4 differences

There is a 80% drop of custom/code debt while keeping 80% of the functionalities. Main focus is on the Editor while Storage Browser, Catalog can be simply brought back gradually and quickly.

* This is now Django3/Vue.js3/Python3 only
* The old apps, desktop/core, desktop/libs are now at the same level (many old dead libs/code like ZooKeeper, Oozie, etc are not ported)
* SQL Thrift interface is phased out in favor or SqlAlchemy (the former saw Beeswax, HiverServer and HiveServer2 transition shifts)
* There is no more cumbersome 'ext-py' directory, now using  [hue/requirements.txt](hue/requirements.txt).
* CI is via GitHub actions vs CircleCI
* CI now automatically perform the grunts work/checks for coding styles, missing licenses, unused imports etc...
* There is no more custom Hue apps, command, packages, permissions... but only standard Django
* ini was phased out in favor or the regular Django settings.py
* Templates (Django, Mako) are not used anymore and the UI is not 100% separated and based on View.js.
* Hue is now released as a standard pypi module instead of a custom tarball that required to be compiled again.
* nose was phased out in favor of pytest for running the tests
* code coverage is now made transparent and visible on each PR
* Jira is not used anymore in favor of GitHub issues and projects
* Old websites are not present anymore

Notes:
* requirements.txt/setup.py needs to be split with regard to dev/prod versions
* no full dependencies on all the modules: e.g. LDAP, mysql DB, phoenix... are optional and easy to add/remove
* internationalization still need to be ported somehow
