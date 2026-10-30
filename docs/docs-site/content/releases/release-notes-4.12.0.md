---
title: "4.12.0"
date: 2026-10-30T00:00:00+00:00
draft: false
weight: -4090
tags: ['skipIndexing']
---

## Hue v4.12.0, released October 30th 2026

Hue is an open source SQL Cloud Assistant for querying [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/): [gethue.com](https://gethue.com)

> **Note:** Hue 4.12 requires **Python 3.11** and is built on **Django 5.2**. Read the [upgrade notes](#upgrade-notes) before you upgrade from 4.11.

### Summary

Hue 4.12 is the first release since January 2023. It comes with more than 890 commits from 36 contributors. The main changes:

* A new React **Storage Browser**.
* A reworked **Trino** connector, and new **Flink SQL Gateway** and **Kyuubi** connectors.
* **Apache Ozone**, **Google Cloud Storage** and **S3-compatible object stores** in the file browsers.
* A documented public **REST API** with a Swagger UI.
* A new platform: Python 3.11, Django 5.2, Gunicorn 23 and Node.js 22.
* A security hardening round: CVE fixes, stricter API permissions, Content Security Policy support and TLS 1.3.

#### New Storage Browser

The new Storage Browser is a React application that replaces the server-rendered file browser pages. Turn it on with `enable_new_storage_browser=true` in the `[desktop]` section of the `hue.ini` (it is off by default). It works for HDFS, S3, ABFS, Google Storage and Ozone.

* Browse with breadcrumbs, a path browser, search, sorting and pagination. The URL follows the path you are browsing.
* View, preview and edit files. Rename, copy, move and delete files and folders, change the owner, group and permissions, see the content summary, compress and extract archives, and use the trash on HDFS.
* Upload files by drag and drop. Uploads run in a queue that keeps going while you navigate, with a progress bar, chunked upload for large files and handling of files that already exist.
* Create buckets, volumes and folders from the UI.
* Each file system has its own default home path (`default_home_path`).

See [Browsing data](/user/browsing/) for the user guide.

#### Trino, Flink SQL, Kyuubi and other connectors

* **Trino**: a native connector (`interface=trino`) with catalog browsing, autocomplete, query explain, multiple statements, HTTP(S) basic authentication (with a password script option), `ssl_verify` and `trino_user` options. Basic authentication is only used over HTTPS. Metadata queries now read all result pages, and queries can be cancelled. See the [Trino connector](/administrator/configuration/connectors/#trino).
* **Apache Flink**: the connector now uses the Flink SQL Gateway, with a function reference, a Cancel button, and `default_catalog` and `default_database` options.
* **Apache Kyuubi**: query Spark SQL through Kyuubi with the JDBC connector and the Kyuubi Hive JDBC driver.
* **AWS Athena**: the SQLAlchemy URL supports the optional `work_group` and `catalog_name` parameters.
* **Apache Phoenix, Hive, Impala and RDBMS** fixes: table names are no longer upper-cased for Phoenix, the describe call is skipped for views, `get_sample_data` is consistent across the RDBMS connectors, and sample data for views is opt-in with `allow_sample_data_from_views`.

#### Object stores and file systems

* **Apache Ozone** (`ofs://`): browse, upload and manage Ozone in the file browser, with a new `[[ozone]]` section in the `hue.ini`.
* **Google Cloud Storage** (`gs://`): browse buckets in the file browser with `[[gc_accounts]]`.
* **S3 and S3-compatible stores**: S3 access is rebuilt on boto3 with a new `[[storage_connectors]]` section for AWS, Dell ECS, NetApp, MinIO and other S3-compatible providers, with key or IAM role authentication, custom endpoints and regions. It is enabled by default (`use_storage_connectors=true`). Set it to `false` to keep the legacy `[aws]` accounts.
* Many fixes in the ABFS, S3, Google Storage and Ozone clients.

#### Public API

* The public API is versioned under `/api/v1/`, and the OpenAPI schema and Swagger UI are served at `/api/schema` and `/api/swagger`. See the [REST API](/developer/api/rest/) documentation.
* New endpoints for the storage operations (list, upload, create, copy, move, rename, delete, download, trash, content summary and file systems), the logs, the configuration check, the usage analytics preference and the installation of examples.
* New options for the integration with other systems: CORS (`cors_enabled`, `cors_allowed_origins`, `cors_allow_credentials`) and external JWT authentication with a configurable `username_header` and several key server URLs.

#### Editor and catalog

* Autocomplete suggests the tables and columns of CTEs (`WITH ... AS`).
* Floating-point result values keep their precision, and the sample values of complex Hive columns (arrays, maps and structs) are shown in the table browser.
* New `default_interpreter` option to choose the default editor for all users, and a `disable_source_autocomplete` option.
* Special characters are supported in table and column names in the public API and in the editor URLs.
* New alert popups and a React welcome tour. Error, warning and info messages share the same component.

#### Job Browser and Oozie

* Job Browser schedules: filter the tasks by status, rerun several tasks and open links in a new tab. The Oozie coordinator editor explains cron expressions in plain text.

#### Administration and operations

* **Task server**: an optional Celery task server (`[[task_server_v2]]`, off by default, with Redis for caching and upload tracking) runs large file uploads as background chunked tasks, with a Task Server page.
* **Gunicorn**: Gunicorn 23 is the default server with the `gthread` worker class. New options for the request limits (`limit_request_*`), worker timeouts, user and group, and the log listener (`log_listener_socket_name`) that now runs inside the server process.
* **TLS and networking**: TLS 1.3 support (`ssl_tls13_enabled` and `ssl_tls12_enabled`), IPv6 (`enable_ipv6`), opt-in forwarding of the client IP and CSRF headers to Hive and Impala (`enable_xff_for_hive_impala` and `enable_x_csrf_token_for_hive_impala`), and sticky sessions for the Hive and Impala HTTP transports.
* **Authentication**: SAML local logout (`local_logout`), SHA256 signatures by default and a new djangosaml2. OIDC extra parameters when Hue runs behind an HTTPS proxy. Cookies of the session and CSRF token expire when the browser closes.
* **Admin pages**: the configuration, server logs, metrics and quick start pages are rewritten in React, and secret values are hidden in the configuration page.
* **Content Security Policy**: the new `csp_nonce` option adds nonces to inline scripts, and the login and SAML pages and several templates no longer need `unsafe-inline`.
* **Other options**: `enable_help_menu`, `enable_workflow_creation_action`, `allow_file_extensions`, `max_file_size_upload_limit`, `file_download_cache_control`, `zookeeper_conn_timeout` and `java_path` (for the JDBC gateway).

#### Platform and build

* Python 3.11 is the supported version: Python 2 is removed, and Python 3.8, 3.9 and 3.10 are not supported anymore. Hue is tested on Python 3.11 on Linux x86_64 and ARM64.
* Django 5.2 (from 3.2 in 4.11), Django REST framework 3.18, django-axes 8 and djangosaml2 1.12.
* Node.js 22.13 or later is required to build the frontend. The backend tests run with pytest and the Python code is linted with Ruff.
* The build creates one virtualenv per Python version and generates the requirements from `generate_requirements.py`.
* WebSockets, ASGI and the PPC build are removed.

### Upgrade notes

Review these changes before you upgrade from 4.11:

| Area | Change |
|------|--------|
| Python and Node | Python 3.11 only. Node.js 22.13 or later to build. |
| Django | Django 5.2. The lockout of django-axes uses `AXES_LOCKOUT_PARAMETERS`, `CSRF_TRUSTED_ORIGINS` need a scheme (Hue adds http and https), and the logout view accepts `GET` links. Test your custom Django code and middleware. |
| Removed | WebSockets and ASGI, the PPC build, Python 2 code, the old notebooks list page, the Threads tab of the administration, the `promote_to_superuser` command, the unsupported browser check and the `editor_autocomplete_timeout` option (use `disable_source_autocomplete`). |
| Interpreters | Apps in the whitelist do not add all the default editors anymore. Define the editors in `[[interpreters]]`, or set `enable_all_interpreters=true` to restore the previous behavior. |
| Web server | Gunicorn 23 with the `gthread` worker class by default. The `eventlet` worker class is not bundled anymore: install any other worker class, such as `gevent`, separately. The separate log listener process is removed: the Gunicorn server runs it. |
| Custom connectors | The snippets of type `custom` that API clients send are disabled by default. Set `enable_custom_connectors=true` in `[notebook]` to allow them. The connectors of the `hue.ini` and the RDBMS and JDBC importer are not affected. |
| Permissions | The configuration API and the configuration check API are restricted to administrators. The `default` group gets the File Browser permission on new and upgraded installs. |
| Cookies and TLS | The session and CSRF cookies expire when the browser closes (`expire_at_browser_close=true`, `csrf_cookie_age=0`). Weak TLS ciphers are removed from the default list. The SAML signing algorithm is SHA256 by default: test your SAML integration. |
| S3 | S3 uses the boto3 based storage connectors by default. Set `use_storage_connectors=false` to keep the legacy `[aws]` accounts. |
| Public API | The paths are under `/api/v1/`. The `storage/view` endpoint and the `compression` field of `storage/display` are removed. |
| Trino | Basic authentication is only used over HTTPS. Database and table names are quoted with double quotes. |
| Defaults | The default log level is INFO. The upload temporary directory is `/tmp/hue_uploads`. `RESTRICT_FILE_EXTENSIONS` is empty by default. The frontend NPM package is 6.x. |

New options are documented in the [configuration](/administrator/configuration/server/) and in the `hue.ini`.

### Security

* Fixes for arbitrary local file read and delete in the importers, and for missing authorization checks in the configuration APIs and in the importer save.
* XSS fixes in the File Browser file names, in the clipboard copy of the editor results, and in the select2 and HBase carousel components.
* Dependency updates for known vulnerabilities, among others Django (up to 5.2), urllib3, cryptography, pyOpenSSL, PyJWT, requests, sqlparse, setuptools, Mako, Markdown, pysaml2, protobuf, axios, jQuery, Bootstrap, webpack, sanitize-html and luxon.
* The certificate authority bundle of the build is pinned and the compromised eMudhra CA is not trusted anymore.
* Content Security Policy support (`csp_nonce`), TLS 1.3 and non-persistent session cookies.

### Compatibility

Runs with Python 3.11. Continuous integration builds and tests Hue on Linux x86_64 and ARM64. The Docker image is based on Ubuntu 22.04.

Compatible with the two most recent versions of the following browsers:

* Chrome
* Firefox LTS
* Safari
* Microsoft Edge

### Get Hue 4.12

* Docker
    ```
    docker run -it -p 8888:8888 gethue/hue:4.12.0
    ```
* Kubernetes :
    ```
    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue
    ```
* [Tarball](https://cdn.gethue.com/downloads/hue-4.12.0.tgz) or [source](https://github.com/cloudera/hue/archive/release-4.12.0.zip)


### List of commits

* [6f01c16e72](https://github.com/cloudera/hue/commit/6f01c16e72) [core] Align hue.ini and the ini template with the code defaults
* [e6f3d68c4a](https://github.com/cloudera/hue/commit/e6f3d68c4a) [helm] Remove the disabled hue-api chart pieces and the Compose doc
* [7c23fca222](https://github.com/cloudera/hue/commit/7c23fca222) [core] Fix management commands with positional arguments on Django 5.2
* [0a830f5746](https://github.com/cloudera/hue/commit/0a830f5746) [docs] Refresh the user, admin and developer docs for 4.12
* [95bb766666](https://github.com/cloudera/hue/commit/95bb766666) [trino] Test the native Trino interpreter and the identifier quoting
* [e41b2d0e1c](https://github.com/cloudera/hue/commit/e41b2d0e1c) [trino] Document the Trino options and enable_custom_connectors in the ini templates and docs
* [028d46192a](https://github.com/cloudera/hue/commit/028d46192a) [notebook] Add enable_custom_connectors to restrict custom snippets sent by API clients
* [25af150cce](https://github.com/cloudera/hue/commit/25af150cce) [trino] Fix the basic Trino connector: HTTPS-only basic auth, ssl_verify, trino_user, all result pages, cancel
* [0b50a46ee5](https://github.com/cloudera/hue/commit/0b50a46ee5) [core] Upgrade cryptography to 50.0.2 and pyOpenSSL to 26.4.0
* [c555bf6e54](https://github.com/cloudera/hue/commit/c555bf6e54) [core] Upgrade setuptools to 84.1.0 and stop using pkg_resources
* [4b5d859615](https://github.com/cloudera/hue/commit/4b5d859615) [core] Fix ruff lint in the files touched by the dependency upgrades
* [0004abfb68](https://github.com/cloudera/hue/commit/0004abfb68) [core] Upgrade Django to 5.2 and the Django related packages
* [d37c8214f4](https://github.com/cloudera/hue/commit/d37c8214f4) [core] Remove the unused ASGI and WebSocket (Django channels) support
* [94d58e3e5b](https://github.com/cloudera/hue/commit/94d58e3e5b) [core] Upgrade Mako to 1.4.2 and vendor djangomako
* [30d8baa4c8](https://github.com/cloudera/hue/commit/30d8baa4c8) [raz] Upgrade protobuf to 6.33.5 and regenerate signer_protos_pb2
* [638c03efa6](https://github.com/cloudera/hue/commit/638c03efa6) [core] Upgrade Python dependencies with open Dependabot alerts
* [494b1b218b](https://github.com/cloudera/hue/commit/494b1b218b) [core] Fix npm Dependabot alerts and require Node 22.13
* [a775bf399d](https://github.com/cloudera/hue/commit/a775bf399d) [core] Pin pip and virtualenv exactly in the Dockerfiles
* [82130779d1](https://github.com/cloudera/hue/commit/82130779d1) [core] Remove unused virtual-bootstrap with bundled pip 9.0.1
* [1feab5a714](https://github.com/cloudera/hue/commit/1feab5a714) [aws] Remove boto's bundled CA list and use certifi instead
* [567ed9fa97](https://github.com/cloudera/hue/commit/567ed9fa97) [core] Pin certifi and upgrade pip and virtualenv for eMudhra CA
* [311189cda4](https://github.com/cloudera/hue/commit/311189cda4) [indexer] Enforce write access on importer save (ISEC-V2026-05)
* [22e33c0c74](https://github.com/cloudera/hue/commit/22e33c0c74) [desktop] Restrict check_config API to Hue admins (ISEC-V2026-04)
* [66e0753746](https://github.com/cloudera/hue/commit/66e0753746) [core] Complete Python 3.11-only build and packaging cleanup
* [d2496a47d9](https://github.com/cloudera/hue/commit/d2496a47d9) [desktop] Fix ruff lint in configuration API and tests
* [29fb32559a](https://github.com/cloudera/hue/commit/29fb32559a) [ci] Require Python 3.11 and fix GitHub Actions on Ubuntu 26.04
* [c3bcfe006a](https://github.com/cloudera/hue/commit/c3bcfe006a) [desktop] Enforce authorization on configuration API (ISEC-V2026-03)
* [9ec5f21633](https://github.com/cloudera/hue/commit/9ec5f21633) [editor] Fix issues preventing the Notebook from loading
* [cab676b153](https://github.com/cloudera/hue/commit/cab676b153) [importer] Block arbitrary local file read and delete in v1 API and Phoenix (#4383)
* [65d9e489f4](https://github.com/cloudera/hue/commit/65d9e489f4) [ui-oozie] Improve Coordinator UI with human-readable cron explanations (#4347)
* [8dbcb91fba](https://github.com/cloudera/hue/commit/8dbcb91fba) [editor] Show the source table name in the row details modal title
* [fdd315652a](https://github.com/cloudera/hue/commit/fdd315652a) [core] Fix open dependabot issues (#4379)
* [6054f984ce](https://github.com/cloudera/hue/commit/6054f984ce) [core] Critical and high CVE fixes and drop support for python 3.8 (#4376)
* [afa68e4008](https://github.com/cloudera/hue/commit/afa68e4008) [editor] Prevent autocomplete Metastore full scan when no database is selected (#4365)
* [6386452c9b](https://github.com/cloudera/hue/commit/6386452c9b) [editor] Support autocomplete for CTE tables (#4342)
* [ed208faa31](https://github.com/cloudera/hue/commit/ed208faa31) [importer] Fix arbitrary file read on the Hue host via the importer localfile feature
* [9ba2b3465f](https://github.com/cloudera/hue/commit/9ba2b3465f) [lint] Streamline imports and clean up test cases in Raz client tests
* [07a8dc357e](https://github.com/cloudera/hue/commit/07a8dc357e) [build] Fix cx-Oracle build failure by constraining setuptools<82
* [8e84509ca1](https://github.com/cloudera/hue/commit/8e84509ca1) [security] Redact AWS access key in S3 URL examples and tests
* [96baf7e22b](https://github.com/cloudera/hue/commit/96baf7e22b) [ui-importer] fix: settings tab for max width in input fields (#4288)
* [272ef7a94f](https://github.com/cloudera/hue/commit/272ef7a94f) [ui-importer] Add (Composite) Primary key column in bulk column modal (#4281)
* [5835719759](https://github.com/cloudera/hue/commit/5835719759) [ui-adminServer-improvements] Improving the nits for the Administrator Server Pages - Metrics and Quick start page (#4298)
* [de1a297608](https://github.com/cloudera/hue/commit/de1a297608) [ui-adminPages-config] Fix the configuration page with loading wrapper hook (#4299)
* [be06cfbf99](https://github.com/cloudera/hue/commit/be06cfbf99) [oozie]: fix random order of start end time fields (#4293)
* [e6ba1baf52](https://github.com/cloudera/hue/commit/e6ba1baf52) [libsaml] Use /saml2/login after SAML local logout
* [73ac3c53f8](https://github.com/cloudera/hue/commit/73ac3c53f8) [libsaml] Implement SAML local logout
* [9f222f8072](https://github.com/cloudera/hue/commit/9f222f8072) [core] Remove the global option in pip install cmd (#4296)
* [3829eff9a1](https://github.com/cloudera/hue/commit/3829eff9a1) [cve] Upgrade setuptools to 80.9.0 for Python 3.9+ to fix CVE-2025-47273 (#4294)
* [3a00479d66](https://github.com/cloudera/hue/commit/3a00479d66) [ui-core] Fix left assist panel to use configured default home paths for S3/ABFS/OFS (#4292)
* [5c102db670](https://github.com/cloudera/hue/commit/5c102db670) [ui-fb] Improve error handling in FileBrowserModel by extracting detailed error messages from JSON responses
* [2480e0ee4e](https://github.com/cloudera/hue/commit/2480e0ee4e) [filebrowser] Add file extension restrictions to old APIs for rename and touch operations
* [0c9913656a](https://github.com/cloudera/hue/commit/0c9913656a) Make _choose_python_version regex parser Docker-compatible
* [48f5005d3b](https://github.com/cloudera/hue/commit/48f5005d3b) Add tools/scripts to docker build
* [94e566472e](https://github.com/cloudera/hue/commit/94e566472e) [Editor] Preserve precision of numeric types in results (#4286)
* [5d2156da6e](https://github.com/cloudera/hue/commit/5d2156da6e) [ui-core]: improve subscription removal by filtering listeners instead of deleting by index (#4285)
* [e7611e9e61](https://github.com/cloudera/hue/commit/e7611e9e61) [rdbms] Fix multiple jdbc connectors port conflict (#4252)
* [3fd79018a1](https://github.com/cloudera/hue/commit/3fd79018a1) [ui-core] upgrade axios from 0.28.0 to 1.8.2 to fix CVE-2025-27152 (#4283)
* [6b10e29dbf](https://github.com/cloudera/hue/commit/6b10e29dbf) [aws][raz] Fix S3 RAZ client parameter passing bug causing AttributeError (#4280)
* [40f6ffc117](https://github.com/cloudera/hue/commit/40f6ffc117) [backend] Fix HTTP client adapter selection when TLS is disabled
* [2d7cf27db4](https://github.com/cloudera/hue/commit/2d7cf27db4) [S3] Stabilize RAZ authentication and enhance S3 client configuration (#4277)
* [d983969d3f](https://github.com/cloudera/hue/commit/d983969d3f) [ui-core] replace indexOf with more readable util functions (#4276)
* [d242f6bc62](https://github.com/cloudera/hue/commit/d242f6bc62) [ui-dataCatalog] fix key generation bug that caused frontend cache to fail
* [b5577aafbf](https://github.com/cloudera/hue/commit/b5577aafbf) [ui-core] fix: clears FileUploadQueue when user closes the Queue dialog (#4228)
* [1ca16e37a9](https://github.com/cloudera/hue/commit/1ca16e37a9) [metrics] Fix lost connection due to cx_Oracle database error (#4273)
* [4550f8c7ee](https://github.com/cloudera/hue/commit/4550f8c7ee) [ui- Quick Start] Logging Python version in the logs and display it on Quick Start page (#4274)
* [7f56ed26f7](https://github.com/cloudera/hue/commit/7f56ed26f7) [ui-core] Dashboard Js Issue. Javascript error isGridster (#4272)
* [c61bf09368](https://github.com/cloudera/hue/commit/c61bf09368) [Core] Support Redhat9-arm64 with python 3.9 and 3.11 (#4270)
* [0f40586408](https://github.com/cloudera/hue/commit/0f40586408) [core] fix again the build on redhat8-arm64 because of 3e646de44fa17760d44366a6e458ee3c29c0def2 (#4271)
* [3e646de44f](https://github.com/cloudera/hue/commit/3e646de44f) [ui-importer-modal] Bulk Edit column modal second iteration (#4165)
* [08480ccd34](https://github.com/cloudera/hue/commit/08480ccd34) [core] fix the build on redhat8-arm64 (#4269)
* [17f6e56d86](https://github.com/cloudera/hue/commit/17f6e56d86) [s3] Fix directory check in S3FileSystem by appending '/' to prefix (#4261)
* [85b8202827](https://github.com/cloudera/hue/commit/85b8202827) [ui-core] chore: replace qsEncodeData with encodeData (#4231)
* [d1514e5105](https://github.com/cloudera/hue/commit/d1514e5105) [ui]: fix the undefined check resolving as true for scheduleTask tab (#4256)
* [18198542af](https://github.com/cloudera/hue/commit/18198542af) [s3] Skip throwing S3ConnectorUploadError from scheme check method (#4255)
* [881eacad80](https://github.com/cloudera/hue/commit/881eacad80) Refactor S3 import to use renamed function is_enabled (#4253)
* [561aac1a19](https://github.com/cloudera/hue/commit/561aac1a19) Fix duplicate configuration call in audit logger initialization (#4232)
* [d02984d619](https://github.com/cloudera/hue/commit/d02984d619) [backend] Convert the test for pytest framework.
* [f7d517ea89](https://github.com/cloudera/hue/commit/f7d517ea89) [backend] Add minimal test suite for loglistener functionality
* [d9393356df](https://github.com/cloudera/hue/commit/d9393356df) [backend] Changing timer seconds to periodically update the recovery file
* [b87ca87802](https://github.com/cloudera/hue/commit/b87ca87802) [backend] Removing loglistener.py from Hue code base.
* [1c793feaa5](https://github.com/cloudera/hue/commit/1c793feaa5) [backend] Removing loglistener.py from Hue Docker installation.
* [cd5b331715](https://github.com/cloudera/hue/commit/cd5b331715) [backend] Removing loglistener.py invocation from tools/scripts/hue.sh
* [b58500899f](https://github.com/cloudera/hue/commit/b58500899f) [backend] Refactor Gunicorn Server Architecture with Integrated Log Listener This PR refactors the Gunicorn server implementation by extracting functionality into separate utility modules and introducing an integrated log listener system for improved logging management and process monitoring.
* [67b902e3d5](https://github.com/cloudera/hue/commit/67b902e3d5) [ui-sb] feat: disable drag and drop for root paths (#4240)
* [7aec1e9e38](https://github.com/cloudera/hue/commit/7aec1e9e38) [lint][ruff] Fix linting for logging init file (#4250)
* [6dd70e6076](https://github.com/cloudera/hue/commit/6dd70e6076) Bump form-data
* [5b8f53ba0d](https://github.com/cloudera/hue/commit/5b8f53ba0d) [core][s3] Add support for S3-compatible object stores with Boto3 migration (#4236)
* [4e49e62a71](https://github.com/cloudera/hue/commit/4e49e62a71) [Importer] Prevent config.get() error when indexer app is blacklisted (#4247)
* [f2fb2cb577](https://github.com/cloudera/hue/commit/f2fb2cb577) [ui-editor] add editor ready pubsub event (#4246)
* [77bad76e3d](https://github.com/cloudera/hue/commit/77bad76e3d) [cookies] cookies to expire at browser closing
* [6398b830f3](https://github.com/cloudera/hue/commit/6398b830f3) [importer] remove morphlines dependency from importer
* [113b05e9bc](https://github.com/cloudera/hue/commit/113b05e9bc) [django] upgrade django 4.1.13 -> 4.2.23
* [2f403c31bf](https://github.com/cloudera/hue/commit/2f403c31bf) [django][saml] Fix SAML for Django 4 upgrade
* [8c86920b83](https://github.com/cloudera/hue/commit/8c86920b83) [ui-security] add xss fix for select2 via ko-binding
* [7d223be088](https://github.com/cloudera/hue/commit/7d223be088) [ui-sb] fix: remove double decoding of url search params (#4235)
* [70f60914b9](https://github.com/cloudera/hue/commit/70f60914b9) [security] Implement TLS 1.3 support across Hue components (#4237)
* [e1bec0e64c](https://github.com/cloudera/hue/commit/e1bec0e64c) hue ipv6 changes
* [3fd87db70f](https://github.com/cloudera/hue/commit/3fd87db70f) [ui-doc] small fix to cursor rules and linting
* [8043281f8d](https://github.com/cloudera/hue/commit/8043281f8d) [ui-core] add cursor rules and improve code examples
* [9011d72e7d](https://github.com/cloudera/hue/commit/9011d72e7d) [ui-storageBrowser] Add create bucket/volume/filesystem functionality (#4234)
* [469edaa308](https://github.com/cloudera/hue/commit/469edaa308) [ui-sb] removes redundant file upload modal (#4227)
* [3b2068bf52](https://github.com/cloudera/hue/commit/3b2068bf52) [ui-core] feat: add transformKey to useSaveData hook (#4230)
* [d9afff360e](https://github.com/cloudera/hue/commit/d9afff360e) [core] support ubuntu24 with python 3.11 (#4225)
* [92812d42ac](https://github.com/cloudera/hue/commit/92812d42ac) [hbase] fix linting error exposed by CVE-2024-6484 changes
* [c3f1a49f57](https://github.com/cloudera/hue/commit/c3f1a49f57) [hbase] fix CVE-2024-6484 by removing usage of Bootstrap carousel
* [d432af8d0c](https://github.com/cloudera/hue/commit/d432af8d0c) [ui-importer] add Partitions tab (#4214)
* [06cd0048ee](https://github.com/cloudera/hue/commit/06cd0048ee) [ui-importer] Add settings tab (#4212)
* [58afec66fe](https://github.com/cloudera/hue/commit/58afec66fe) [useradmin] Assign filebrowser permissions to the default group (#4223)
* [088cce729f](https://github.com/cloudera/hue/commit/088cce729f) [core] remove PPC-related code as PPC builds are no longer supported (#4224)
* [7c746a3bdd](https://github.com/cloudera/hue/commit/7c746a3bdd) [api][config] Add test for get_config with unbound optional configs
* [d64f5cede5](https://github.com/cloudera/hue/commit/d64f5cede5) [api][config] Make get_config resilient to blacklisted apps via safe config access
* [15e214ae11](https://github.com/cloudera/hue/commit/15e214ae11) [ui-sb] Changes for skip/overwrite files in filebrowser (#4143)
* [e4605d3a05](https://github.com/cloudera/hue/commit/e4605d3a05) [ui-importer] Add configured filesystems in importer (#4131)
* [8d5eb8292f](https://github.com/cloudera/hue/commit/8d5eb8292f) [django] fixes for django-saml infinite redirect error
* [2a373cb918](https://github.com/cloudera/hue/commit/2a373cb918) [ui] makes tests assertion more specific by removing expect.objectContaining (#4218)
* [ecc3a7a799](https://github.com/cloudera/hue/commit/ecc3a7a799) [ui-sb] moves the destination_path from FormData to query param (#4217)
* [c209f6e99f](https://github.com/cloudera/hue/commit/c209f6e99f) [api][filebrowser] Dynamically set upload handler in APIView's dispatch method to prevent potential race condition (#4213)
* [7477aa1772](https://github.com/cloudera/hue/commit/7477aa1772) [Core] remove --system-site-packages flag from virtualenv creation (#4211)
* [5d07911107](https://github.com/cloudera/hue/commit/5d07911107) [ui-adminpage] Port usage analytics endpoints to public (#4126)
* [cedbf39338](https://github.com/cloudera/hue/commit/cedbf39338) [ui-importer] add tabs layout (#4203)
* [fe0789a287](https://github.com/cloudera/hue/commit/fe0789a287) [ui-importer] add table name validation (#4194)
* [fcde6da3b4](https://github.com/cloudera/hue/commit/fcde6da3b4) [ui-core] add put and path methods in api utils and useSaveData hook (#4199)
* [76dffc6a85](https://github.com/cloudera/hue/commit/76dffc6a85) [ui-core] add formInput component for all input types (#4193)
* [8d94bf0496](https://github.com/cloudera/hue/commit/8d94bf0496) [build] Add migration retry logic to hue.sh
* [af4342d2b8](https://github.com/cloudera/hue/commit/af4342d2b8) Fixing loglistener startup issue
* [2445ddeced](https://github.com/cloudera/hue/commit/2445ddeced) Add nested param to get_sample_data and API compatibility tests to prevent connector signature mismatches (#4202)
* [1ab48c0cfc](https://github.com/cloudera/hue/commit/1ab48c0cfc) [api][filebrowser] Refactor rename endpoint with improved validation and tests (#4198)
* [282d569fa2](https://github.com/cloudera/hue/commit/282d569fa2) [docs] Update SQL type mapping documentation to reflect changes in response format
* [d3eab61c55](https://github.com/cloudera/hue/commit/d3eab61c55) [importer] Update SQL type mapping API to return unique SQL types as a sorted list
* [90d7aaa4de](https://github.com/cloudera/hue/commit/90d7aaa4de) [docs] Update Importer API endpoints to reflect API versioning (#4196)
* [0df36ddfa3](https://github.com/cloudera/hue/commit/0df36ddfa3) [importer] Refactor file operations to use username instead of filesystem object (#4195)
* [6d6025535a](https://github.com/cloudera/hue/commit/6d6025535a) [api][filebrowser] Refactor and improve file upload public API core design (#4188)
* [fdf2be6ebe](https://github.com/cloudera/hue/commit/fdf2be6ebe) [beeswax] Do not error on invalid session in request
* [b0fbae7c9e](https://github.com/cloudera/hue/commit/b0fbae7c9e) Update apps/filebrowser/src/filebrowser/views.py
* [f02ae03e1b](https://github.com/cloudera/hue/commit/f02ae03e1b) Fix kt_renewer startup crash due to directory creation race condition
* [409416fc17](https://github.com/cloudera/hue/commit/409416fc17) [abfs] Enhance _writedata method to write data in chunks and improve flushing logic (#4189)
* [c613b319cd](https://github.com/cloudera/hue/commit/c613b319cd) [ui-importer] Public API integration (#4137)
* [ada61b276a](https://github.com/cloudera/hue/commit/ada61b276a) [demo] upgrade demo site Dockerfile to Python 3.11 and update dependencies (#4186)
* [88e04de22f](https://github.com/cloudera/hue/commit/88e04de22f) [impala][beeswax] Store cookies for beeswax http transport
* [f20fa80d4e](https://github.com/cloudera/hue/commit/f20fa80d4e) [importer] Integrate Pydantic schemas for file operations and enhance validation (#4183)
* [981baab807](https://github.com/cloudera/hue/commit/981baab807) [ui-filebrowser] remove redundant Error keyword from alert (#4185)
* [e53562ff81](https://github.com/cloudera/hue/commit/e53562ff81) [filebrowser] Improve file extension restrictions check for old upload operations (#4184)
* [666cf4e6c6](https://github.com/cloudera/hue/commit/666cf4e6c6) [api][conf] Refactor API tests and configuration handling (#4181)
* [a3c23ab974](https://github.com/cloudera/hue/commit/a3c23ab974) [metastore] add config flag to fetch sample data for views (#4172)
* [727430a92c](https://github.com/cloudera/hue/commit/727430a92c) [ui-sb] fix the deletion modal loading state (#4176)
* [c1ae5f0028](https://github.com/cloudera/hue/commit/c1ae5f0028) [docs] Fix File Import API documentation formatting for consistency (#4180)
* [ba020855e9](https://github.com/cloudera/hue/commit/ba020855e9) [build] Update .gitignore to include additional generated files and Python version specifications (#4179)
* [cf106e44e8](https://github.com/cloudera/hue/commit/cf106e44e8) [docs] modernize Apple Silicon instructions, clarify Python 3.11 support, remove Intel Mac references (#4174)
* [754d43aec7](https://github.com/cloudera/hue/commit/754d43aec7) [lint] Reorder imports, fix exception usage and remove unused imports for fix ruff linting (#4173)
* [0a3e78b2d8](https://github.com/cloudera/hue/commit/0a3e78b2d8) [ui-sb] add test for file upload hooks (#4138)
* [277a48c845](https://github.com/cloudera/hue/commit/277a48c845) [ui-importer] destination setting component and hook (#4157)
* [c2a44769bb](https://github.com/cloudera/hue/commit/c2a44769bb) [api] Refactor usage analytics API to DRF APIView and update tests (#4171)
* [3caf4618d3](https://github.com/cloudera/hue/commit/3caf4618d3) Bump @babel/runtime from 7.21.0 to 7.27.0
* [9aa033a79a](https://github.com/cloudera/hue/commit/9aa033a79a) [ci] Update PR comments CI checks to run in pull request scope only (#4170)
* [d2892ee387](https://github.com/cloudera/hue/commit/d2892ee387) [s3] Improve S3 recursive delete to handle large directories and virtual directory scenarios
* [ff7cb7766f](https://github.com/cloudera/hue/commit/ff7cb7766f) [core] Apply hue conf dir and user/group config to gunicorn options
* [77001070ad](https://github.com/cloudera/hue/commit/77001070ad) Improve kt_renewer logging for Kerberos Ticket Renewal Failures
* [4022df8e92](https://github.com/cloudera/hue/commit/4022df8e92) [ui-storageBrowser] Add data-testids for cypress intgration tests (#4167)
* [b8b96158fa](https://github.com/cloudera/hue/commit/b8b96158fa) Make sed pattern for SYS_PIP portable across macOS and Linux (#4163)
* [5d8c359a1c](https://github.com/cloudera/hue/commit/5d8c359a1c) [ci] add prettier check in Github Actions and fix YAML formatting (#4151)
* [3810dc37bf](https://github.com/cloudera/hue/commit/3810dc37bf) [ui-core] add prettier script in package.json (#4162)
* [e89a5eda39](https://github.com/cloudera/hue/commit/e89a5eda39) [importer] Change error logging from exception to warning for python-magic package import (#4160)
* [84d4002d91](https://github.com/cloudera/hue/commit/84d4002d91) [ci] Rename job for clarity and update jest coverage comment configuration
* [0dd784a9f4](https://github.com/cloudera/hue/commit/0dd784a9f4) [ui-jest] Override coverageReporters config to include json-summary
* [a4d5b3d190](https://github.com/cloudera/hue/commit/a4d5b3d190) [ci] Rename jobs in PR comments workflow for clarity and add UI code coverage steps (#4155)
* [d8a5949ed0](https://github.com/cloudera/hue/commit/d8a5949ed0) [cleanup] Remove obsolete Codecov configuration and dead link check script (#4154)
* [d1b23e4a58](https://github.com/cloudera/hue/commit/d1b23e4a58) [docs] Add comprehensive File Import API documentation with detailed endpoints, workflows, and examples
* [40d7cbfc1f](https://github.com/cloudera/hue/commit/40d7cbfc1f) [ci] Remove old and flaky documentation lint check from existing CI workflows and add a new Docs Lint workflow for improved link checking
* [a615096645](https://github.com/cloudera/hue/commit/a615096645) [importer] Introduce new Importer module with separate Configs, API Endpoints, and Dependencies (#4089)
* [2d547872c8](https://github.com/cloudera/hue/commit/2d547872c8) [core] Refactor requirements generator along with upgrading ruff and improving its configuration (#4147)
* [894067288b](https://github.com/cloudera/hue/commit/894067288b) [ci] Migrate old CircleCI arm64 workflow to GA based arm64 CI workflow with py3.11 Hue build and tests (#4149)
* [6940c9ee15](https://github.com/cloudera/hue/commit/6940c9ee15) [docs] Modernize and enhance Hue project README (#4150)
* [e5c747215a](https://github.com/cloudera/hue/commit/e5c747215a) [libsaml] Add custom config for libsaml redirect URL
* [16be4adc7b](https://github.com/cloudera/hue/commit/16be4adc7b) [multi-python] remove the pytorch and unnecessary libs from req file
* [533a5a6578](https://github.com/cloudera/hue/commit/533a5a6578) [multi-python] Fix ImportError GSSAPIProxy requires the Python gssapi library No module named 'decorator'
* [99266a4799](https://github.com/cloudera/hue/commit/99266a4799) [multi-python] Reset virtualenv VIRTUAL_ENV_VERSION version to the original version.
* [bc15fa58f4](https://github.com/cloudera/hue/commit/bc15fa58f4) [multi-python] Refactor build scripts for better multi-Python version handling and SQLite installation
* [49c32c47c3](https://github.com/cloudera/hue/commit/49c32c47c3) [multi-python] Fix is_supported_os to avoid bash -n error and ensure compatibility across OSes
* [986ebe0010](https://github.com/cloudera/hue/commit/986ebe0010) [multi-python] Refactor Hue build system for multi-python support and environment consistency
* [340aad6a90](https://github.com/cloudera/hue/commit/340aad6a90) [Core] Fix the build on centos7 and sles12
* [b8abf7e7a1](https://github.com/cloudera/hue/commit/b8abf7e7a1) Fixing RELOCATABLE variable null value issue
* [23324c79be](https://github.com/cloudera/hue/commit/23324c79be) [multi-python] Support python3.11 on ubuntu22 (#4116)
* [164a32c076](https://github.com/cloudera/hue/commit/164a32c076) [ui-importer] Adding column modal button to importer (#4121)
* [285de32986](https://github.com/cloudera/hue/commit/285de32986) [django] Upgraded djangosaml2 to 1.9.3
* [8ed894a0a5](https://github.com/cloudera/hue/commit/8ed894a0a5) [ui-sb] move fileUploadQueue at global level (#4136)
* [2265125073](https://github.com/cloudera/hue/commit/2265125073) [ui-sb] show the success icon for 2 sec when copying  path (#4134)
* [0cf1851e87](https://github.com/cloudera/hue/commit/0cf1851e87) [ui-sb] Port sb from mako based to pure frontend (#4129)
* [7f9d2936e6](https://github.com/cloudera/hue/commit/7f9d2936e6) [ui-sb] fixes file preview for non-readable file (#4061)
* [ee918ce35e](https://github.com/cloudera/hue/commit/ee918ce35e) [ui-importer] finish import API integration (#4122)
* [e7311e0e68](https://github.com/cloudera/hue/commit/e7311e0e68) [ui-sb]: Add Error handling alerts in action modals (#4118)
* [2c6299e67f](https://github.com/cloudera/hue/commit/2c6299e67f) [api] Improve error handling for non-decodable files in /display filebrowser API (#4130)
* [a614768f4f](https://github.com/cloudera/hue/commit/a614768f4f) documents uploads will use HDFSfileUploadHandler when task_server is on
* [827b1d3381](https://github.com/cloudera/hue/commit/827b1d3381) [ui-importer] show field separator and other dropdown only for CSV (#4123)
* [4d9bd2162e](https://github.com/cloudera/hue/commit/4d9bd2162e) [ui-Quick Start] Convert the Quick Start page within administrator server in ReactJS (#4025)
* [bb31ccbbb0](https://github.com/cloudera/hue/commit/bb31ccbbb0) [multi-python] pure-sasl for py3.11
* [b3fb80e13a](https://github.com/cloudera/hue/commit/b3fb80e13a) [multi-python] Fixed the kinit path
* [8c522a8bf7](https://github.com/cloudera/hue/commit/8c522a8bf7) [api] Add error handling for missing connector in notebook setup install_example API (#4120)
* [1001654e04](https://github.com/cloudera/hue/commit/1001654e04) [ui] Improve UI unit test coverage reporting
* [d0cc3fe2d8](https://github.com/cloudera/hue/commit/d0cc3fe2d8) [api] Add usage analytics public API endpoints (#4117)
* [5f7bdc840f](https://github.com/cloudera/hue/commit/5f7bdc840f) [multi-python] Improve the helper function
* [a1b747885d](https://github.com/cloudera/hue/commit/a1b747885d) [api] Skip connector_id validation in _setup_notebook_examples for spark example to install (#4114)
* [6bb1aad4c0](https://github.com/cloudera/hue/commit/6bb1aad4c0) [ui-importer] add configure setting feature in file preview (#4101)
* [b73ba9d5e1](https://github.com/cloudera/hue/commit/b73ba9d5e1) removing unset PIP_FIND_LINKS PIP_EXTRA_INDEX_URL
* [5272c5b31b](https://github.com/cloudera/hue/commit/5272c5b31b) Streamlines CI workflows and standardizes test environments
* [e0404ce651](https://github.com/cloudera/hue/commit/e0404ce651) Refactor LDAP test dependencies and error handling
* [81a3396b32](https://github.com/cloudera/hue/commit/81a3396b32) [multi-python] remove unnecessary debug echo from Makefile (#4111)
* [c7f98ccd4d](https://github.com/cloudera/hue/commit/c7f98ccd4d) [multi-python][build] add mysql and pg to path before starting
* [de00238a35](https://github.com/cloudera/hue/commit/de00238a35) Enable Multi-python support extension for Hue (#4106)
* [34418a5265](https://github.com/cloudera/hue/commit/34418a5265) [ui-core] remove redundant file chooser component (#4104)
* [f180cbede7](https://github.com/cloudera/hue/commit/f180cbede7) [ui-core] remove deprecated data-event key from buttons (#4103)
* [3cfba0ba32](https://github.com/cloudera/hue/commit/3cfba0ba32) [multi-python] scripts to simplify the selection of python version
* [30b315827c](https://github.com/cloudera/hue/commit/30b315827c) [ui-sb] show loading spinner in action modal button instead of page (#4094)
* [db8f7b2c43](https://github.com/cloudera/hue/commit/db8f7b2c43) [ui-core] add dynamic height to Paginated table component (#4091)
* [e22fab5ea0](https://github.com/cloudera/hue/commit/e22fab5ea0) [django] Fix for removal of django.conf.urls.url in Django4
* [5fdca09f80](https://github.com/cloudera/hue/commit/5fdca09f80) [ui-core] fix cuix upgrade css issues (#4100)
* [e875464bdc](https://github.com/cloudera/hue/commit/e875464bdc) fix curl enable support for redirects in file downloads
* [dec03b4251](https://github.com/cloudera/hue/commit/dec03b4251) [compute][discovery] check service-discovery cm for ldapgroup
* [72e4f9c39a](https://github.com/cloudera/hue/commit/72e4f9c39a) [flink] Improve autocomplete for functions (#4090)
* [39e2842f1e](https://github.com/cloudera/hue/commit/39e2842f1e) fixes the audio and video tags
* [d7af5bad1f](https://github.com/cloudera/hue/commit/d7af5bad1f) fixes the failing test
* [6ff754c241](https://github.com/cloudera/hue/commit/6ff754c241) fixes the achor tag issue
* [abde24e892](https://github.com/cloudera/hue/commit/abde24e892) fixes the lint errors
* [a4e866129c](https://github.com/cloudera/hue/commit/a4e866129c) [ui-accessibility] fix some accessibility lint issues
* [b49a128fd1](https://github.com/cloudera/hue/commit/b49a128fd1) [ui-ci] add eslint-plugin-jsx-a11y
* [811e43106f](https://github.com/cloudera/hue/commit/811e43106f) upgrade setuptools package due to CVE-2024-6345
* [6255dc0508](https://github.com/cloudera/hue/commit/6255dc0508) [api] Add endpoint to fetch available apps for example installation (#4093)
* [73252e5abb](https://github.com/cloudera/hue/commit/73252e5abb) [auth] Allow extra params for OIDC to override token payload for Hue to work behind https proxy (#4017)
* [a509c270f0](https://github.com/cloudera/hue/commit/a509c270f0) [ui-newimporter] add file preview page (#4088)
* [a0a6cd2376](https://github.com/cloudera/hue/commit/a0a6cd2376) [ui-core] auto set qsEncodeData key in useSaveData hook (#4082)
* [c854354e6f](https://github.com/cloudera/hue/commit/c854354e6f) [flink] Fix RecursionError in create_session method (#4085)
* [52f174f24e](https://github.com/cloudera/hue/commit/52f174f24e) [ui-newImporter]Skeleton and Importer type chooser (#4077)
* [8116961d55](https://github.com/cloudera/hue/commit/8116961d55) [ui-taskserver] refactors task server component (#4058)
* [adf189e90f](https://github.com/cloudera/hue/commit/adf189e90f) [api] Refactor task server private API endpoints (#4076)
* [a5eeb54e2f](https://github.com/cloudera/hue/commit/a5eeb54e2f) [django] fixed was_modified_since by removing size param (#4087)
* [5b81df3846](https://github.com/cloudera/hue/commit/5b81df3846) [security] fix arguments error for saml logout issue  (#4084)
* [f33cf6b3a4](https://github.com/cloudera/hue/commit/f33cf6b3a4) [logs] Remove obsolete log view code and related tests (#4081)
* [aaba74e936](https://github.com/cloudera/hue/commit/aaba74e936) [ui-core] adds showReactAppPage to allow UI routing to pure frontend (react) pages
* [d8cce1db3a](https://github.com/cloudera/hue/commit/d8cce1db3a) [api] Change HttpResponse to JsonResponse in /install_examples API (#4080)
* [3989866376](https://github.com/cloudera/hue/commit/3989866376) [ui-editor] fixes loading computes in saved query page (#4079)
* [96ffaad8b7](https://github.com/cloudera/hue/commit/96ffaad8b7) [security] Add Job Browser back for unsafe inline (#4078)
* [8312fce67a](https://github.com/cloudera/hue/commit/8312fce67a) [ui-core] update cuix component library to the latest version
* [4f591e79b9](https://github.com/cloudera/hue/commit/4f591e79b9) [CI] Improve handling of comment when no test files are present in the commit (#4075)
* [19e685a1fe](https://github.com/cloudera/hue/commit/19e685a1fe) [api] Improve filename handling in Content-Disposition header for /download API (#4074)
* [02c2b2d1e7](https://github.com/cloudera/hue/commit/02c2b2d1e7) [ui-storagebrowser] change label of HDFS root from / to hdfs (#4069)
* [9f9a4f1ec6](https://github.com/cloudera/hue/commit/9f9a4f1ec6) [compute][ui] old saved queries failing to load
* [140a5a96b3](https://github.com/cloudera/hue/commit/140a5a96b3) [ui-storagebrowser] fixes css across pages (#4047)
* [b3c641edd2](https://github.com/cloudera/hue/commit/b3c641edd2) Importer not auto refreshing for file uploads with task server
* [382177d86a](https://github.com/cloudera/hue/commit/382177d86a) [ui-storagebrowser] add progressBar in file upload (#4059)
* [7396f7ad34](https://github.com/cloudera/hue/commit/7396f7ad34) [ui-config] lint fix
* [ba4f1511d1](https://github.com/cloudera/hue/commit/ba4f1511d1) [ui-config] add search across multiple sections]
* [cdafdb6536](https://github.com/cloudera/hue/commit/cdafdb6536) [ui-core] adds Table component (#4052)
* [6eb3c567a5](https://github.com/cloudera/hue/commit/6eb3c567a5) Move to pip3.9 from pip3.8 for psycopg2 installation in rhel8
* [839568274b](https://github.com/cloudera/hue/commit/839568274b) Renaming schedule upload button to upload when task_server is on
* [c6dae7c171](https://github.com/cloudera/hue/commit/c6dae7c171) [core] Check if oozie is present in INSTALLED_APPS before importing Job model in config_validator (#4056)
* [ff157d236e](https://github.com/cloudera/hue/commit/ff157d236e) [core] Dynamically import oozie_setup for /install_esamples API to avoid oozie INSTALLED_APPS runtime error (#4050)
* [6457491915](https://github.com/cloudera/hue/commit/6457491915) [ui-admin] hide log out button for Knox
* [75b3743620](https://github.com/cloudera/hue/commit/75b3743620) [hiveserver2] Skip describing columns for views in Hive and Impala (#4045)
* [14581860d0](https://github.com/cloudera/hue/commit/14581860d0) [ui-storagebrowser] converts snakecase keys to camel in useLoadData hook (#4011)
* [cce0baea2d](https://github.com/cloudera/hue/commit/cce0baea2d) [ui-storagebrowser] add useWindowSize hook to get window size (#3930)
* [488750b641](https://github.com/cloudera/hue/commit/488750b641) [compute] fixes for session close and recreate
* [9ea4732b7c](https://github.com/cloudera/hue/commit/9ea4732b7c) [django] upgraded django to 4.1
* [e0785b182d](https://github.com/cloudera/hue/commit/e0785b182d) [compute] [discovery] remove old computes before upserting
* [28b9b7c486](https://github.com/cloudera/hue/commit/28b9b7c486) [ci] Update PR comments workflow to use pull_request_target event and adjust permissions (#4036)
* [8fe162a236](https://github.com/cloudera/hue/commit/8fe162a236) [ui-admin] Improve server log formatting
* [4781ba6990](https://github.com/cloudera/hue/commit/4781ba6990) [flink] Add default_catalog and default_database option (#4015)
* [b5fc7fab74](https://github.com/cloudera/hue/commit/b5fc7fab74) [ci] Refactor CI workflows to separate the PR comment actions into a new workflow (#4034)
* [573ee8e7d7](https://github.com/cloudera/hue/commit/573ee8e7d7) [ci] Update permissions in CI workflow for pytest coverage comment check (#4033)
* [f0987bef61](https://github.com/cloudera/hue/commit/f0987bef61) [ci] Add write permissions for pull-requests in commitflow workflow (#4030)
* [11e454e7a3](https://github.com/cloudera/hue/commit/11e454e7a3) [pytest] Add test data path in .gitignore (#4032)
* [ba0afec5c2](https://github.com/cloudera/hue/commit/ba0afec5c2) [ci] Refactor backend Github Actions workflow and add pytest coverage PR comment (#4028)
* [f576014ba9](https://github.com/cloudera/hue/commit/f576014ba9) Datahub left menu are not working redirecting to wrong link (#4027)
* [ff0039b51a](https://github.com/cloudera/hue/commit/ff0039b51a) [ui-storagebrowser] adds trash functionality (#4024)
* [f8c8dc825b](https://github.com/cloudera/hue/commit/f8c8dc825b) [ci][cov] Update coverage configs and streamline report generation (#4026)
* [4c2d68aee5](https://github.com/cloudera/hue/commit/4c2d68aee5) [ui-storagebrowser] refactor action component to extend for trash actions (#4023)
* [a0fa35743c](https://github.com/cloudera/hue/commit/a0fa35743c) [ui-documentBrowser] Hide the new workflow button based on config (#4022)
* [cc9aa66ff3](https://github.com/cloudera/hue/commit/cc9aa66ff3) [ui-storageBrowser] Add home, refresh, edit and copy path functionalities (#3996)
* [90458894c3](https://github.com/cloudera/hue/commit/90458894c3) [api] Add configuration option to enable or disable workflow creation in Hue documents (#4020)
* [ac14e98fd5](https://github.com/cloudera/hue/commit/ac14e98fd5) [api] Rename 'config_error_list' to 'config_errors' in check_config API response (#4019)
* [4d008df9ca](https://github.com/cloudera/hue/commit/4d008df9ca) [api] Add new check_config API endpoint to validate Hue configuration (#4018)
* [415e0f01cd](https://github.com/cloudera/hue/commit/415e0f01cd) [api] Add new API endpoint to install app examples with suitable setup functions (#4016)
* [b9cc76eaf5](https://github.com/cloudera/hue/commit/b9cc76eaf5) [core] Remove package-lock.json from tools/sql-scratchpad (#4012)
* [f6fa587bdd](https://github.com/cloudera/hue/commit/f6fa587bdd) Fix prettier issues
* [70e8fc3d7e](https://github.com/cloudera/hue/commit/70e8fc3d7e) Remove redundant packages from Dockerfile
* [e4678ad050](https://github.com/cloudera/hue/commit/e4678ad050) Fix get_sample_data signature
* [5ab7e19597](https://github.com/cloudera/hue/commit/5ab7e19597) Minor changes
* [3c0562249a](https://github.com/cloudera/hue/commit/3c0562249a) Display cancel button when type=flink and status=available
* [5d4b059e0c](https://github.com/cloudera/hue/commit/5d4b059e0c) Adjust flink sql connector to Apache Flink SQL Gateway
* [e59265ace0](https://github.com/cloudera/hue/commit/e59265ace0) [ci] Add code coverage report generation to CI workflow (#4010)
* [761e1393f4](https://github.com/cloudera/hue/commit/761e1393f4) [core] Check for new query handle exception message for handling expired queries better in query history (#4009)
* [1d5dfeb906](https://github.com/cloudera/hue/commit/1d5dfeb906) Upgrade gethue to 6.0.1 in sql-scratchpad to pull luxon 1.28.1 CVE-2023-22467
* [82cfce9892](https://github.com/cloudera/hue/commit/82cfce9892) [ui-editor] fixes compute selection in presentation mode (#4001)
* [6cc393f640](https://github.com/cloudera/hue/commit/6cc393f640) [api] Refactor /create/file API with better validation checks (#4003)
* [24f50679aa](https://github.com/cloudera/hue/commit/24f50679aa) [abfs] Fix isdir and isfile methods to handle exceptions better (#4002)
* [91bbc6bae9](https://github.com/cloudera/hue/commit/91bbc6bae9) [api] Improve sorting logic in the /list API and add unit tests (#3999)
* [e2bc160629](https://github.com/cloudera/hue/commit/e2bc160629) [ui-storagebrowser] moves the api and types to storagebrowser folder (#3989)
* [76b7c71fa1](https://github.com/cloudera/hue/commit/76b7c71fa1) [ui-storagebrowser] fixes labels and default value in create file (#3988)
* [42307bf4f6](https://github.com/cloudera/hue/commit/42307bf4f6) [ui-storagebrowser] moves the HDFS config to /fileSystem API (#3987)
* [0254d725e8](https://github.com/cloudera/hue/commit/0254d725e8) [api] Refactor /copy API with additional validation checks (#3993)
* [96978e742f](https://github.com/cloudera/hue/commit/96978e742f) [api] Refactor /move API with additional validation checks (#3991)
* [dae20705c2](https://github.com/cloudera/hue/commit/dae20705c2) [api] Improve content disposition handling in /download API (#3994)
* [a6794a2b76](https://github.com/cloudera/hue/commit/a6794a2b76) [api] Fix error handling in bulk operations (#3990)
* [d2ac71a52f](https://github.com/cloudera/hue/commit/d2ac71a52f) [tests] Update tests to set RESTRICT_FILE_EXTENSIONS to None
* [d492822ba0](https://github.com/cloudera/hue/commit/d492822ba0) [api] Fix handling of restricted file types in /rename API when the config is not set
* [0f2d75653c](https://github.com/cloudera/hue/commit/0f2d75653c) [conf] Update default value for RESTRICT_FILE_EXTENSIONS to None
* [6882626406](https://github.com/cloudera/hue/commit/6882626406) [ui-storagebrowser] fixes the preview for non-text files (#3981)
* [3817ea88ea](https://github.com/cloudera/hue/commit/3817ea88ea) [test] Move pytest and its dependencies from `make apps` to `make test_prep`
* [bb3606ea99](https://github.com/cloudera/hue/commit/bb3606ea99) [api] Refactor /mkdir API with better validation checks (#3985)
* [34f8b8d810](https://github.com/cloudera/hue/commit/34f8b8d810) [api] Refactor /filesystems API and include extra HDFS configs in its response (#3983)
* [d4ac561a32](https://github.com/cloudera/hue/commit/d4ac561a32) [computes] fixed impala impersonation flag
* [c762ef0582](https://github.com/cloudera/hue/commit/c762ef0582) [ui-serverLogs] Convert the Server Logs page within Administrator server in ReactJS (#3927)
* [d60b253edb](https://github.com/cloudera/hue/commit/d60b253edb) [ui-editor] changes the Active database label to database (#3980)
* [9c5906b66e](https://github.com/cloudera/hue/commit/9c5906b66e) [ui-storagebrowser] adds change permission action to new storage browser (#3975)
* [887bba5d4e](https://github.com/cloudera/hue/commit/887bba5d4e) [Trino] Enhance the logic to efficiently retrieve the rows (#3972)
* [1009872820](https://github.com/cloudera/hue/commit/1009872820) [ui-storagebrowser] fixes the regular file upload for new storage brwoser (#3960)
* [4a863dc95a](https://github.com/cloudera/hue/commit/4a863dc95a) [ui-storagebrowser] moves the new storage browser to new endpoint  (#3978)
* [17e4f36123](https://github.com/cloudera/hue/commit/17e4f36123) [api] Add workaround to fix regular file upload API (#3962)
* [92719cc1f9](https://github.com/cloudera/hue/commit/92719cc1f9) [security] Fix AJAX Loading of Inline Scripts in editFile
* [93f0ebdabd](https://github.com/cloudera/hue/commit/93f0ebdabd) [ui-storagebrowser] fixes chunk upload for new storage browser (#3977)
* [e5d26edf46](https://github.com/cloudera/hue/commit/e5d26edf46) [ui-storagebrowser] adds change owner and group action (#3973)
* [28c5987f0a](https://github.com/cloudera/hue/commit/28c5987f0a) [security] Unsafe inline fixes - Saml text issue and cross button fix. (#3974)
* [07ab5d5f53](https://github.com/cloudera/hue/commit/07ab5d5f53) [ui-core] move hooks to nested folder (#3969)
* [7d6d0d271c](https://github.com/cloudera/hue/commit/7d6d0d271c) [ui-storagebrowser] fix the translation strings (#3970)
* [12b8fbfe17](https://github.com/cloudera/hue/commit/12b8fbfe17) Bump nanoid from 3.3.7 to 3.3.8 (#3908)
* [bd8e80cf93](https://github.com/cloudera/hue/commit/bd8e80cf93) [ui-storagebrowser] port APIs to public and fixes the chunk upload (#3967)
* [f6cd307ecb](https://github.com/cloudera/hue/commit/f6cd307ecb) [ui-leftassist] auto select next compute onError (#3965)
* [162e33a880](https://github.com/cloudera/hue/commit/162e33a880) [api][logs] Add reverse order option for retrieving Hue logs (#3968)
* [864283cf08](https://github.com/cloudera/hue/commit/864283cf08) [security] SAML login issues with csp enabled
* [afc3806f8e](https://github.com/cloudera/hue/commit/afc3806f8e) HS2 JDBC URL for Oozie Workflow via config param (#3961)
* [d610479c8d](https://github.com/cloudera/hue/commit/d610479c8d) [computes] removed admissiond from impala readiness check
* [1673b1f585](https://github.com/cloudera/hue/commit/1673b1f585) mini job browser fix (#3963)
* [83337edd77](https://github.com/cloudera/hue/commit/83337edd77) [ui-storagebrowser] adds download action (#3964)
* [ab69060432](https://github.com/cloudera/hue/commit/ab69060432) [ui-storagebrowser] adds extract archive action (#3950)
* [5c18a605fd](https://github.com/cloudera/hue/commit/5c18a605fd) [ui-build] add strip-sourcemap-loader to remove 3rd party hardcoded map references
* [e67d150f97](https://github.com/cloudera/hue/commit/e67d150f97) [ui-storagebrowser] adds pagination in file preview page (#3949)
* [afcae4c109](https://github.com/cloudera/hue/commit/afcae4c109) [api] Ensure skip_trash is a boolean value in the /delete API (#3958)
* [a178e77b1f](https://github.com/cloudera/hue/commit/a178e77b1f) replace the hardcoded filename with correct text (#3957)
* [b2b0023ae5](https://github.com/cloudera/hue/commit/b2b0023ae5) inline js in the saml logout page (#3954)
* [d2c8ce0a62](https://github.com/cloudera/hue/commit/d2c8ce0a62) [ui-storagebrowser] Adds silent polling for list_dir during file upload (#3951)
* [b4b4e0ee69](https://github.com/cloudera/hue/commit/b4b4e0ee69) [api] Remove unused compression field from /display API (#3955)
* [95e4e0c37e](https://github.com/cloudera/hue/commit/95e4e0c37e) Fix JB Oozie Log Icon (#3952)
* [48b087db91](https://github.com/cloudera/hue/commit/48b087db91) [ui-storagebrowser] adds available space check in chunk upload (#3931)
* [e119138402](https://github.com/cloudera/hue/commit/e119138402) [Trino] Update Trino integration guide in Hue (#3943)
* [5b20c541d9](https://github.com/cloudera/hue/commit/5b20c541d9) Fix Metrics for Oracle DPI errors (#3944)
* [642146b3d1](https://github.com/cloudera/hue/commit/642146b3d1) Moved django-babel into hue repo
* [2810ecccc6](https://github.com/cloudera/hue/commit/2810ecccc6) [Trino] Improve session management and property handling. (#3942)
* [e5be62599c](https://github.com/cloudera/hue/commit/e5be62599c) [notebook][api] Remove Solr error handling method to fix json decode exception issue (#3940)
* [7ecdbe4d49](https://github.com/cloudera/hue/commit/7ecdbe4d49) [ui-storagebrowser] adds compress action (#3938)
* [4147e6bcda](https://github.com/cloudera/hue/commit/4147e6bcda) [ui-storagebrowser] implements error handling (#3932)
* [7b509fb58e](https://github.com/cloudera/hue/commit/7b509fb58e) [ui-importer] rename cumpute selection to virtual warehouse (#3928)
* [28e761c6d2](https://github.com/cloudera/hue/commit/28e761c6d2) [ui-storagebrowser] adds delete action for files and folder (#3926)
* [7e9165b181](https://github.com/cloudera/hue/commit/7e9165b181) [ui-storagebrowser] refactor / move actions to separate files for scaling (#3925)
* [f3b3ec9025](https://github.com/cloudera/hue/commit/f3b3ec9025) [ui-storagebrowser] adds disable button to InputModal component (#3924)
* [8f5b89463d](https://github.com/cloudera/hue/commit/8f5b89463d) [ui-storagebrowser] avoids unwanted api calls for non-editable file (#3933)
* [2f19d31831](https://github.com/cloudera/hue/commit/2f19d31831) [ui-storagebrowser] fixes console warning and types (#3929)
* [522abe68ea](https://github.com/cloudera/hue/commit/522abe68ea) [ui-storagebrowser] fixes routing between multiple fileSystem (#3937)
* [77faef4777](https://github.com/cloudera/hue/commit/77faef4777) [Trino] Ensures uninterrupted schema listing even if a catalog query fails (#3939)
* [c54f745b73](https://github.com/cloudera/hue/commit/c54f745b73) [api] Remove old storage/view public API endpoint (#3895)
* [ca873694e0](https://github.com/cloudera/hue/commit/ca873694e0) [security] Inline Js Fixes, Fixes File Browser Issues and other related problems (#3923)
* [9c6991045c](https://github.com/cloudera/hue/commit/9c6991045c) [ui-storagebrowser] adds and reads configs from .ini files (#3922)
* [fe17f6ad2a](https://github.com/cloudera/hue/commit/fe17f6ad2a) [ui-storagebrowser] refreshes file stats when file is edited (#3920)
* [4b551c94a9](https://github.com/cloudera/hue/commit/4b551c94a9) [ui-storagebrowser] updates browser url while navigating (#3919)
* [ad00b2e726](https://github.com/cloudera/hue/commit/ad00b2e726) [ui-storagebrowser] integrates file upload components to storage browser (#3916)
* [5dc39b723f](https://github.com/cloudera/hue/commit/5dc39b723f) [ui-storagebrowser] refactor browser actions (#3915)
* [23315717d9](https://github.com/cloudera/hue/commit/23315717d9) [ui-storagebrowser] refactor storage browser and folder structure (#3914)
* [d16de728ee](https://github.com/cloudera/hue/commit/d16de728ee) [api] Port chunk file upload related APIs to public (#3921)
* [a2ddc9b784](https://github.com/cloudera/hue/commit/a2ddc9b784) [ui-storagebrowser] ports APIs to public and refactors code (#3906)
* [04fe0f9b68](https://github.com/cloudera/hue/commit/04fe0f9b68) [ui-storagebrowser] refactors PathBrowser component to construct breadcrumb from filePath (#3905)
* [130bb0f306](https://github.com/cloudera/hue/commit/130bb0f306) [ui-storagebrowser] adds hooks for file upload (#3910)
* [8fe5b1a761](https://github.com/cloudera/hue/commit/8fe5b1a761) [api] optimise new storage browser rendering (#3918)
* [c67bfd69b2](https://github.com/cloudera/hue/commit/c67bfd69b2) [ui-importer] make compute selection mandatory (#3896)
* [f35615899f](https://github.com/cloudera/hue/commit/f35615899f) [backend] Remove lockfile python package due to EOL
* [8203d76dc3](https://github.com/cloudera/hue/commit/8203d76dc3) Upgrade Gunicorn to v23.0.0 and switch to gthread worker class
* [470b515654](https://github.com/cloudera/hue/commit/470b515654) [ui-core] adds drag and drop component (#3912)
* [fec209e120](https://github.com/cloudera/hue/commit/fec209e120) [ui-storageBrowser] Implement storage browser actions (#3877)
* [acdd97c481](https://github.com/cloudera/hue/commit/acdd97c481) Install psycopg2 for all os
* [74c592e619](https://github.com/cloudera/hue/commit/74c592e619) [ui-core] adds useQueueProcessor hook to manage concurrent async task (#3890)
* [1c69b6fea4](https://github.com/cloudera/hue/commit/1c69b6fea4) [ci] Upgrade go and muffet package to latest versions for docs lint check (#3907)
* [f1015c886b](https://github.com/cloudera/hue/commit/f1015c886b) [ui-config] Change MAX_FILEEDITOR_SIZE from string to number (#3904)
* [d2edbee570](https://github.com/cloudera/hue/commit/d2edbee570) [api] Add overwrite option for /upload API when file already exists (#3901)
* [cd9a3cb45a](https://github.com/cloudera/hue/commit/cd9a3cb45a) Remove psycopg2-binary due to FIPS restrictions
* [979d867b34](https://github.com/cloudera/hue/commit/979d867b34) [logs] Refactor old Hue logs views into new public APIs (#3899)
* [1675c50ebc](https://github.com/cloudera/hue/commit/1675c50ebc) [ozone] Fix edge cases when volume name start with service_id in path (#3893)
* [a8a85851ee](https://github.com/cloudera/hue/commit/a8a85851ee) [Importer] Update Iceberg table syntax for Impala (#3887)
* [7489ce0e8b](https://github.com/cloudera/hue/commit/7489ce0e8b) [computes] typo-fix k8s labels should be in lowercase
* [6948861ab8](https://github.com/cloudera/hue/commit/6948861ab8) [api] Change error message for new upload public API (#3889)
* [a104a75066](https://github.com/cloudera/hue/commit/a104a75066) [fb] Stop file uploads with restrictive file types for old upload handlers (#3888)
* [251b017ee4](https://github.com/cloudera/hue/commit/251b017ee4) [api] Prevent renaming files to restricted file types (#3886)
* [3d0bf36db2](https://github.com/cloudera/hue/commit/3d0bf36db2) [ui-configuration] Convert the Configuration page within Administrator Server in ReactJS (#3848)
* [577b140efa](https://github.com/cloudera/hue/commit/577b140efa) [api] Improve normal file upload design for public APIs (#3878)
* [ff1e56e88f](https://github.com/cloudera/hue/commit/ff1e56e88f) [security] Unsafe Inline Script (#3876)
* [7b08df4b8b](https://github.com/cloudera/hue/commit/7b08df4b8b) [Filebrowser] Fix support for reading Parquet files (#3885)
* [7d8961fd6d](https://github.com/cloudera/hue/commit/7d8961fd6d) Fixing redirect_url for Production and Dev/Staging environment
* [e9b6a452c7](https://github.com/cloudera/hue/commit/e9b6a452c7) Fix it (#3882)
* [b1d585604c](https://github.com/cloudera/hue/commit/b1d585604c) [pytest] Add warning for PRs missing unit test file changes (#3875)
* [7b542177b6](https://github.com/cloudera/hue/commit/7b542177b6) [Pytest] Generate HTML report for test results and disable warnings (#3874)
* [0e9437647e](https://github.com/cloudera/hue/commit/0e9437647e) [ui-storagebrowser] adds file preview and save for files (#3869)
* [552850ef4b](https://github.com/cloudera/hue/commit/552850ef4b) [api] Refactor old filebrowser methods to new public APIs (#3836)
* [9a85afab12](https://github.com/cloudera/hue/commit/9a85afab12) [frontend] fixed calendar button alignment in Oozie WF Submit form (#3740)
* [16c940e143](https://github.com/cloudera/hue/commit/16c940e143) [middleware][cleanup] Remove unused HtmlValidationMiddleware (#3871)
* [ccecafa513](https://github.com/cloudera/hue/commit/ccecafa513) [core][cleanup] Refactor and remove old Py2 code checks and methods (#3683)
* [2e10b7129c](https://github.com/cloudera/hue/commit/2e10b7129c) [Trino] Add a flag to distinguish between the database and table/column name (#3867)
* [6cf4875882](https://github.com/cloudera/hue/commit/6cf4875882) [commands][cleanup] Remove redundant set_default_editor scripts (#3865)
* [7f6aab62aa](https://github.com/cloudera/hue/commit/7f6aab62aa) [Core] Refactor the URL pattern to allow special characters in the table and column names. (#3866)
* [b65a11bf6b](https://github.com/cloudera/hue/commit/b65a11bf6b) use the system username for impala/hive auth from configs
* [43f8e005f6](https://github.com/cloudera/hue/commit/43f8e005f6) [ui-core] remove urlPrefix option from useLoadData hook (#3868)
* [59fad964a9](https://github.com/cloudera/hue/commit/59fad964a9) [ui-core] add useSaveData hook for api calls (#3864)
* [fa15c5b16e](https://github.com/cloudera/hue/commit/fa15c5b16e) [ui-oozie] Hide the widget drop zone above end if a decision node is present in the workflow (#3793)
* [db70e4c5e8](https://github.com/cloudera/hue/commit/db70e4c5e8) [cve] Upgrade configobj to 5.0.9 to fix CVE-2023-26112 (#3862)
* [3c01e252fe](https://github.com/cloudera/hue/commit/3c01e252fe) [sasl] Remove the prebuild saslwrapper (#3863)
* [b31a7497e1](https://github.com/cloudera/hue/commit/b31a7497e1) [raz][fips] Fix S3 WRITE operations from regressing in non-raz setup (#3861)
* [961f7ea9b2](https://github.com/cloudera/hue/commit/961f7ea9b2) [Trino] Show query ID in logs for the Trino editor (#3857)
* [1df282a340](https://github.com/cloudera/hue/commit/1df282a340) [config][cleanup] Fix bool to coerce_bool type conversion warning (#3860)
* [f46a83468a](https://github.com/cloudera/hue/commit/f46a83468a) [raz][fips] Set usedforsecurity=False for MD5 hash to support FIPS mode (#3858)
* [9b4747fbce](https://github.com/cloudera/hue/commit/9b4747fbce) [ui-editor] replaces editor shortcuts separator to plus sign (#3856)
* [cef1bae6f9](https://github.com/cloudera/hue/commit/cef1bae6f9) [ui-storagebrowser] add download button for files (#3851)
* [e806c01506](https://github.com/cloudera/hue/commit/e806c01506) [computes] Fixed the typo in picking compute display-name
* [0c66ada7d3](https://github.com/cloudera/hue/commit/0c66ada7d3) [ui-importer] adds compute selection in importer destination (#3854)
* [ce781c6fb2](https://github.com/cloudera/hue/commit/ce781c6fb2) [Trino] Update drag and drop suggestions to use double quotes instead of backticks (#3853)
* [9111b916f7](https://github.com/cloudera/hue/commit/9111b916f7) [metrics] Fix lost connection when metrics query database (#3852)
* [41fd5de981](https://github.com/cloudera/hue/commit/41fd5de981) added compute support for trino
* [d7a54dd63b](https://github.com/cloudera/hue/commit/d7a54dd63b) [Trino] Table/database names starting with digit should inclosed with double quotes (#3735)
* [53e8d58fdc](https://github.com/cloudera/hue/commit/53e8d58fdc) [ui-storagebrowser] view file content as text (#3823)
* [ad12816d88](https://github.com/cloudera/hue/commit/ad12816d88) [core][config] Hide config values having secret attribute as True (#3841)
* [9f0280ea9d](https://github.com/cloudera/hue/commit/9f0280ea9d) [ui-core]: add onSuccess and onError callback for useLoadData hook (#3849)
* [08ca92ca38](https://github.com/cloudera/hue/commit/08ca92ca38) [hdfs] Improve log message for left-over temporary file during upload op (#3843)
* [acc74f1b99](https://github.com/cloudera/hue/commit/acc74f1b99) [ruff] Change runruff args order and update docstring example (#3842)
* [eedf7543a6](https://github.com/cloudera/hue/commit/eedf7543a6) [oozie] Upgrade workflow sharing command to support Py3 (#3840)
* [82d8b0a28a](https://github.com/cloudera/hue/commit/82d8b0a28a) [core] Upgrade markdown package from 3.1 to 3.7 (#3838)
* [670c429d14](https://github.com/cloudera/hue/commit/670c429d14) [ui] Bump webpack from 5.93.0 to 5.94.0 (#3834)
* [5ec331d402](https://github.com/cloudera/hue/commit/5ec331d402) [Threads] Remove Threads tab from Administrator Server Tab (#3815)
* [bc62813214](https://github.com/cloudera/hue/commit/bc62813214) [hive] Use the right port number for server config according to thrift transport mode
* [09d13d045f](https://github.com/cloudera/hue/commit/09d13d045f) [hive] Fix config issue in HS2 ZK discovery
* [c26b467c3e](https://github.com/cloudera/hue/commit/c26b467c3e) [Python3.9] Add support for Python 3.9 on RHEL8 and RedHat8-ARM64 (#3835)
* [15c0dd5560](https://github.com/cloudera/hue/commit/15c0dd5560) [ui-metrics-cuix] Updating metrics to sync with Cloudera design (#3826)
* [64dac7fc3d](https://github.com/cloudera/hue/commit/64dac7fc3d) [ui-testing] Improve 2 unit tests
* [a2f1b62fc4](https://github.com/cloudera/hue/commit/a2f1b62fc4) Removing the import and usage of act in TaskBrowser.jsx
* [2b22c0394a](https://github.com/cloudera/hue/commit/2b22c0394a) [interpreters] Skip adding all available editors by default for every whitelisted app (#3778)
* [b2d29788c7](https://github.com/cloudera/hue/commit/b2d29788c7) [ci] Bump checkout and setup-node actions from v3 to v4 (#3825)
* [395d807f3a](https://github.com/cloudera/hue/commit/395d807f3a) [Hive][left assist] Enhanced get_tables_meta to correctly fetch and display tables (#3824)
* [f348cd7edd](https://github.com/cloudera/hue/commit/f348cd7edd) [ui-storagebrowser] chore: code cleanup (#3820)
* [8c7a36429b](https://github.com/cloudera/hue/commit/8c7a36429b) [ui-core]: feat: add useLoadData hook for API calls (#3819)
* [a6585eed96](https://github.com/cloudera/hue/commit/a6585eed96) [api] Add /get_trash_path public API (#3817)
* [2d06975913](https://github.com/cloudera/hue/commit/2d06975913) [CVE] Remove libexpat from  windows OS's virtual env directory
* [71a6726491](https://github.com/cloudera/hue/commit/71a6726491) [core] Bump up celery to 5.4.0 and django-celery-beat to 2.6.0
* [a2c3090cba](https://github.com/cloudera/hue/commit/a2c3090cba) [doc2] Fix issue where a copy of a shared document in user home becomes unreachable
* [ce08dccb5b](https://github.com/cloudera/hue/commit/ce08dccb5b) [ui-storageBrowser] Fix height layout issues in storage browser (#3813)
* [89c8ee7719](https://github.com/cloudera/hue/commit/89c8ee7719) [Python3.11] Added CI for python3.11 (#3802)
* [f75608c08c](https://github.com/cloudera/hue/commit/f75608c08c) Added the commit to support the python3.11
* [8a453b187d](https://github.com/cloudera/hue/commit/8a453b187d) [Python3.11] Adding custom commit in sasl lib to support python3.11
* [d742b42c8f](https://github.com/cloudera/hue/commit/d742b42c8f) [core] Add the document copy action to the right click context menu in the left assist panel
* [349674943d](https://github.com/cloudera/hue/commit/349674943d) [core] Add the document copy action to the right click context menu in the documents page
* [be2b3d4cc8](https://github.com/cloudera/hue/commit/be2b3d4cc8) [core] Add the inline documents search back in the documents page
* [f6e6ef15d1](https://github.com/cloudera/hue/commit/f6e6ef15d1) [Importer] Fix manual table creation from importer (#3807)
* [62be61bff2](https://github.com/cloudera/hue/commit/62be61bff2) [Python3.11] support python3.11 in Hue makefile build script (#3806)
* [493543c88e](https://github.com/cloudera/hue/commit/493543c88e) [Python3.11] Improve the regex expression (#3804)
* [03b1a53c2f](https://github.com/cloudera/hue/commit/03b1a53c2f) [Python3.11] Upgrade libs to support python3.11 with backward compatibility (#3803)
* [f3f1630352](https://github.com/cloudera/hue/commit/f3f1630352) [ci] Setup node v20 correctly for py3 checks (#3799)
* [c49ecbed2d](https://github.com/cloudera/hue/commit/c49ecbed2d) [lib] Pin krb5 to 0.5.1 for SLES12 (#3798)
* [3cb867c148](https://github.com/cloudera/hue/commit/3cb867c148) [ext-py][eventlet] Fix Tudoor DoS issue (CVE-2023-29483)
* [e51c4fddeb](https://github.com/cloudera/hue/commit/e51c4fddeb) [ext-py][dnspython] Fix Tudoor DoS issue (CVE-2023-29483)
* [ce2894e26d](https://github.com/cloudera/hue/commit/ce2894e26d) [ui-jobs] Change "Modified" header for schedules listing to "Next Materialized" (#3794)
* [034e6fd3fe](https://github.com/cloudera/hue/commit/034e6fd3fe) [api] Add swagger UI and schema for public APIs (#3776)
* [58fd518e41](https://github.com/cloudera/hue/commit/58fd518e41) [ui-core] Add missing dependencies
* [1afb798f0e](https://github.com/cloudera/hue/commit/1afb798f0e) [ui-core] Upgrade style lint to the latest version
* [103385e873](https://github.com/cloudera/hue/commit/103385e873) [ui-core] Upgrade js/ts linters to the latest possible versions
* [f67890e4a4](https://github.com/cloudera/hue/commit/f67890e4a4) [ui-core] Upgrade Typescript and related libs to the latest versions
* [1e666bedb7](https://github.com/cloudera/hue/commit/1e666bedb7) [ui-core] Upgrade babel and webpack to the latest versions
* [4c3bbcb3fd](https://github.com/cloudera/hue/commit/4c3bbcb3fd) [Taskserver] Set timezone-aware datetimes to False
* [b58074092b](https://github.com/cloudera/hue/commit/b58074092b) [ui-cve] Upgrade tar due to CVE-2024-28863
* [b960c7052a](https://github.com/cloudera/hue/commit/b960c7052a) [ui-cve] Upgrade babel related packages due to CVE-2023-45133
* [53998b392c](https://github.com/cloudera/hue/commit/53998b392c) [UI] Added a check to handle cases where the input is of type 'object' (#3786)
* [cd0a92e18d](https://github.com/cloudera/hue/commit/cd0a92e18d) [ui-leftnav] Remove "Edit List" tab from Editor dropdown in left navbar (#3784)
* [ed1867fb0e](https://github.com/cloudera/hue/commit/ed1867fb0e) [tests][cleanup] Make few unit tests not depend local Hue config and other code improvements (#3782)
* [cdfb17ea60](https://github.com/cloudera/hue/commit/cdfb17ea60) [cve] Bump requests to 2.32.3 for fixing CVE-2023-32681 (#3783)
* [666046ec00](https://github.com/cloudera/hue/commit/666046ec00) [core] Change ext-py3 package installation path again (#3785)
* [376c3c4088](https://github.com/cloudera/hue/commit/376c3c4088) [ui-storageBrowser]Implement storage browser table search (#3781)
* [df0e7f915e](https://github.com/cloudera/hue/commit/df0e7f915e) Bump braces from 3.0.2 to 3.0.3 (#3756)
* [6d08458ed6](https://github.com/cloudera/hue/commit/6d08458ed6) [ui-core] refactor storage browser to extend file preview feature (#3779)
* [c64d748a3c](https://github.com/cloudera/hue/commit/c64d748a3c) Bump ws from 7.5.2 to 7.5.10
* [9ea0ac50eb](https://github.com/cloudera/hue/commit/9ea0ac50eb) [ui-core] Allow Blue Oak License 1.0.0
* [cc70d325db](https://github.com/cloudera/hue/commit/cc70d325db) [ui-core] Upgrade all jest related libraries
* [1826fef256](https://github.com/cloudera/hue/commit/1826fef256) [ui-admin][improvement] Rename AlertComponent to GlobalAlert, MetricsComponent to Metrics and create a separate directory for the admin pages (#3767)
* [18b21b71a0](https://github.com/cloudera/hue/commit/18b21b71a0) [ui-metrics-test] Adding an additional test for the metrics Page (#3761)
* [7a3bf6646b](https://github.com/cloudera/hue/commit/7a3bf6646b) [ui-cve] Upgrade mime in the ace editor source for CVE-2017-16138 (#3763)
* [8713bf635b](https://github.com/cloudera/hue/commit/8713bf635b) [ui-cve] Upgrade Axios to fix CVE-2023-45857, CVE-2024-28849 and CVE-2023-26159 (#3774)
* [78d41a495a](https://github.com/cloudera/hue/commit/78d41a495a) [ui-storageBrowser] Implement UI for rename action (#3764)
* [db70a86346](https://github.com/cloudera/hue/commit/db70a86346) [ui-cve]Upgrade sanitize-html to fix CVE-2024-21501 (#3769)
* [4cb7a529e8](https://github.com/cloudera/hue/commit/4cb7a529e8) [Taskserver] Enhance ABFS upload logic to handle chunk position tracking
* [0c4f9d5732](https://github.com/cloudera/hue/commit/0c4f9d5732) [Blog] Trino blog correction (#3770)
* [0a7a1cea92](https://github.com/cloudera/hue/commit/0a7a1cea92) [Blog] Trino blog (#3768)
* [c702fd7c5a](https://github.com/cloudera/hue/commit/c702fd7c5a) [Hive] Support complex data type sampling (#3766)
* [d34fd43e3c](https://github.com/cloudera/hue/commit/d34fd43e3c) [docs] Add documentation for new file browser public APIs (#3759)
* [267dd86c92](https://github.com/cloudera/hue/commit/267dd86c92) [docs] Remove dead links (#3760)
* [bdeccbdd33](https://github.com/cloudera/hue/commit/bdeccbdd33) [ui-metrics] Converted the Metrics page within Admin Server in ReactJS (#3707)
* [e1182494e7](https://github.com/cloudera/hue/commit/e1182494e7) [api][fb] Refactor existing filebrowser APIs to clean public APIs (#3739)
* [33b4c90bb9](https://github.com/cloudera/hue/commit/33b4c90bb9) [cve] Bump cryptography package to 42.0.8 (#3712)
* [c740708303](https://github.com/cloudera/hue/commit/c740708303) [ui-storageBrowser]Implement multiselect for Storage browser table data (#3755)
* [e16b7f6f34](https://github.com/cloudera/hue/commit/e16b7f6f34) [ui-tablebrowser] Fix viewSQL tab for Hive (#3754)
* [c8e07e3dfd](https://github.com/cloudera/hue/commit/c8e07e3dfd) [conf] Make Gunicorn worker timeout and graceful timeout configurable (#3753)
* [342357da2d](https://github.com/cloudera/hue/commit/342357da2d) [impala] improved query timeout error logging
* [7ee5a336a9](https://github.com/cloudera/hue/commit/7ee5a336a9) [core] Use dedicated home_directory methods and introduce DEFAULT_HOME_PATH config for supported FS (#3742)
* [81a8fadb6c](https://github.com/cloudera/hue/commit/81a8fadb6c) Avoid initializing free disk space in redis for all hue shell commands (#3747)
* [b302114994](https://github.com/cloudera/hue/commit/b302114994) [computes] add k8s label selector filter for service discovery
* [9e27d5f017](https://github.com/cloudera/hue/commit/9e27d5f017) [ui-storageBrowser] Add cuix and antd classes to Storage Browser (#3741)
* [dc02b1bc73](https://github.com/cloudera/hue/commit/dc02b1bc73) [taskserver] Disable schedule tasks tab in job browser based on task_server_v2 configs (#3743)
* [52c1bf51a4](https://github.com/cloudera/hue/commit/52c1bf51a4) [taskserver] Handle concurrent uploads using a counter and locking mechanism and add new configs (TASK_SERVER_V2) (#3733)
* [d32163fd8e](https://github.com/cloudera/hue/commit/d32163fd8e) [ui-qe] Adding data-testid attribute to the Hue page HTML elements (#3652)
* [4a157d87ee](https://github.com/cloudera/hue/commit/4a157d87ee) [filebrowser] updated file compression in hdfs to support py3 (#3734)
* [32d205d238](https://github.com/cloudera/hue/commit/32d205d238) [Importer] Fix importer for Parquet, ORC, and Avro formats (#3736)
* [bb57a002a6](https://github.com/cloudera/hue/commit/bb57a002a6) [docs] Add new Python Linting section (#3737)
* [d5ab133582](https://github.com/cloudera/hue/commit/d5ab133582) [ui-doc] Documenting data-testid attribute in contributing-frontend.md file (#3732)
* [c6673f8daa](https://github.com/cloudera/hue/commit/c6673f8daa) [ui-storageBrowser] Implement UI modal for content summary (#3681)
* [f678becc03](https://github.com/cloudera/hue/commit/f678becc03) [ui][sidebar] Make visibility of the help menu in the sidebar configurable (#3722)
* [4c648c1541](https://github.com/cloudera/hue/commit/4c648c1541) [ruff] Enable isort rules for linting (#3727)
* [ffdb386cbe](https://github.com/cloudera/hue/commit/ffdb386cbe) [ui][mako] Delete unused mako files (#3731)
* [04dc6d11d9](https://github.com/cloudera/hue/commit/04dc6d11d9) [raz] Change log statements to DEBUG for RAZ HA section (#3730)
* [050cf3b6ec](https://github.com/cloudera/hue/commit/050cf3b6ec) [ruff] Skip logging subprocess exception as error (#3728)
* [879379423b](https://github.com/cloudera/hue/commit/879379423b) [Django] Upgrade the django version (#3725)
* [c1875deb9d](https://github.com/cloudera/hue/commit/c1875deb9d) [ci][ruff] Switch to new custom Ruff cmd for python linting in CI checks (#3723)
* [67828f395e](https://github.com/cloudera/hue/commit/67828f395e) [dnspython] Adding dnspython to local install ext-py3 (#3719)
* [0b8bace2ac](https://github.com/cloudera/hue/commit/0b8bace2ac) [ruff] Add custom Ruff command in Hue and improve config file (#3716)
* [aa46998e7b](https://github.com/cloudera/hue/commit/aa46998e7b) [eventlet] Add rudimentary support for Python 3.10 (#3717)
* [2fef72635c](https://github.com/cloudera/hue/commit/2fef72635c) [ubuntu22] Support Hue on ubuntu22 and sles15 with python3.10 (#3714)
* [adfc122fbd](https://github.com/cloudera/hue/commit/adfc122fbd) [core] Correct expression for python version comparison (#3718)
* [d7fd783db9](https://github.com/cloudera/hue/commit/d7fd783db9) [core] Upgrade the request_kerberos lib for python3.10 support (#3721)
* [0e6025f319](https://github.com/cloudera/hue/commit/0e6025f319) [core] Change ext-py3 package installation path (#3720)
* [eb37ea6333](https://github.com/cloudera/hue/commit/eb37ea6333) [frontend] Implement placeholder for empty table scenario (#3682)
* [7f1227fd42](https://github.com/cloudera/hue/commit/7f1227fd42) [commands] Remove promote_to_superuser  Hue command (#3715)
* [a172d006e1](https://github.com/cloudera/hue/commit/a172d006e1) [cleanup][nose] Remove old nose package references (#3711)
* [0119e0069c](https://github.com/cloudera/hue/commit/0119e0069c) [core][cve] Remove werkzeug package (#3710)
* [06c56410c1](https://github.com/cloudera/hue/commit/06c56410c1) [core][cve] Bump sqlparse to 0.5.0 (#3713)
* [3fce74c2cd](https://github.com/cloudera/hue/commit/3fce74c2cd) [connectors] connectors from request is incomplete
* [9d613c999a](https://github.com/cloudera/hue/commit/9d613c999a) [useradmin] Add new "set_user_as_active" and improve "promote_to_superuser" commands (#3690)
* [28a733553f](https://github.com/cloudera/hue/commit/28a733553f) [lint] Ignore deleted files for Ruff linting (#3709)
* [055f98e0b1](https://github.com/cloudera/hue/commit/055f98e0b1) [tests] Fix S3 tests to not pickup local Hue setup configs (#3708)
* [ba387d49e2](https://github.com/cloudera/hue/commit/ba387d49e2) [beeswax] fixed the incorrect set_nulls in hive results
* [cbef69c5f6](https://github.com/cloudera/hue/commit/cbef69c5f6) [CI] Add python 3.10 CI check in github action (#3699)
* [63958ccf0c](https://github.com/cloudera/hue/commit/63958ccf0c) [Core][Python3.10] Refactor codebase for Python 3.10 compatibility, removing Python 2.7 related stuff (#3663)
* [36baffdc80](https://github.com/cloudera/hue/commit/36baffdc80) [doc] Update documentation for running unit tests with pytest (#3706)
* [264a267b22](https://github.com/cloudera/hue/commit/264a267b22) [lint] Remove pylint and switch to ruff for Hue backend linting (#3703)
* [432cd98818](https://github.com/cloudera/hue/commit/432cd98818) [test] convert remaining nose based test to pytest (#3705)
* [264c4bbdf3](https://github.com/cloudera/hue/commit/264c4bbdf3) update nodejs version from 14 to 20 (#3584)
* [3b8881de11](https://github.com/cloudera/hue/commit/3b8881de11) [Trino] Support multiple query execution from the Hue-Trino editor (#3702)
* [0f91e3ba8a](https://github.com/cloudera/hue/commit/0f91e3ba8a) Importer supports chunked file uploads (#3686)
* [1cd19ea901](https://github.com/cloudera/hue/commit/1cd19ea901) [Frontend] Task server frontend changes. (#3673)
* [03fcee03d4](https://github.com/cloudera/hue/commit/03fcee03d4) Task server Docker changes and backend tasks changes (#3688)
* [c5c6d8e98e](https://github.com/cloudera/hue/commit/c5c6d8e98e) Adding Task server backend changes for Hue (#3687)
* [658faba0ed](https://github.com/cloudera/hue/commit/658faba0ed) [pylint] enable pylint and remove tools/ace-editor changes done in pytest PR (#3698)
* [a07820ccee](https://github.com/cloudera/hue/commit/a07820ccee) [tests] Switch Hue backend unit testing from nose to pytest (#3693)
* [682d496a02](https://github.com/cloudera/hue/commit/682d496a02) [jb] Fix issues where Hive was showing up in the job browser even though it was disabled
* [1cc2431d01](https://github.com/cloudera/hue/commit/1cc2431d01) [jb] Fix issues with Impala query detailed view in the Job Browser
* [008554cc18](https://github.com/cloudera/hue/commit/008554cc18) [tb] Fix an issue where column comments were fetched for individual columns in the Table Browser
* [c435498704](https://github.com/cloudera/hue/commit/c435498704) [Trino] Support ldap password script in trino (#3689)
* [612a83773b](https://github.com/cloudera/hue/commit/612a83773b) [fb] Changed file system name in permission_actions (#3679)
* [5f67c2c519](https://github.com/cloudera/hue/commit/5f67c2c519) [raz][s3] Fix encoding for special chars in directory name listing 1000+ keys (#3677)
* [47db78adfa](https://github.com/cloudera/hue/commit/47db78adfa) add a push hook as well
* [0c21d58a1f](https://github.com/cloudera/hue/commit/0c21d58a1f) Add Folder Pattern to linting
* [f5250cd751](https://github.com/cloudera/hue/commit/f5250cd751) [git] precommit hooks for linting
* [622a0e7b0c](https://github.com/cloudera/hue/commit/622a0e7b0c) [raz][abfs] Improve url params encoding for RAZ ABFS client (#3666)
* [8fa8144cab](https://github.com/cloudera/hue/commit/8fa8144cab) [frontend] Change typescript eslint rule from warning to error
* [56f13d2b4e](https://github.com/cloudera/hue/commit/56f13d2b4e) [frontend] Replace the use of jHueNotify with the new Alert component
* [0269dd9617](https://github.com/cloudera/hue/commit/0269dd9617) [frontend] Adjust the useHuePubSub hook to not update the state when a callback is given
* [0d9fda498f](https://github.com/cloudera/hue/commit/0d9fda498f) [frontend] Add pubsub topic to hide all open global alerts
* [7d4f3886dd](https://github.com/cloudera/hue/commit/7d4f3886dd) [frontend] Add nonStick option for global alerts
* [d8dbbf7907](https://github.com/cloudera/hue/commit/d8dbbf7907) [frontend] Added tests for input modal
* [129b43f030](https://github.com/cloudera/hue/commit/129b43f030) [frontend] Improvements and added 118n to default props
* [6ea127182d](https://github.com/cloudera/hue/commit/6ea127182d) [frontend] Improvements and replaced axios post
* [adecbc963b](https://github.com/cloudera/hue/commit/adecbc963b) [frontend] i18n changes and improvements
* [513284aea6](https://github.com/cloudera/hue/commit/513284aea6) [frontend] Removed description and placeholder from input modal.
* [1eccd9d3bc](https://github.com/cloudera/hue/commit/1eccd9d3bc) [frontend] Added new file creation functionalities to storage browser
* [14dfbf2039](https://github.com/cloudera/hue/commit/14dfbf2039) [frontend] Changes pagenumber to 1 when new folder is viewed
* [527f957c7c](https://github.com/cloudera/hue/commit/527f957c7c) [frontend]Added new folder functionalities to storage browser
* [0580e7bbdc](https://github.com/cloudera/hue/commit/0580e7bbdc) [frontend] Implement new file and folder creation modal
* [b6b2eccc90](https://github.com/cloudera/hue/commit/b6b2eccc90) [editor] Move the SQL Syntax Dropdown from mako to js to get rid of inline script (#3653)
* [1f30a3a4b2](https://github.com/cloudera/hue/commit/1f30a3a4b2) [editor] Remove mako variables for editor id and notebooks as well as the old notebooks listing page (#3657)
* [1291cc81c1](https://github.com/cloudera/hue/commit/1291cc81c1) [editor] Replace the editor_autocomplete_timeout setting with disable_source_autocomplete
* [30a1693b35](https://github.com/cloudera/hue/commit/30a1693b35) [frontend] Fix jest warning when an actual API call happens from unit tests
* [d9ae00d22f](https://github.com/cloudera/hue/commit/d9ae00d22f) [frontend] Fix missing act() in AlertComponent tests
* [b61dac9a9b](https://github.com/cloudera/hue/commit/b61dac9a9b) [fb] Check for get attribute for ARCHIVE_UPLOAD_TEMPDIR config (#3669)
* [4ccdc7bb0a](https://github.com/cloudera/hue/commit/4ccdc7bb0a) [jb] Fix bug that breaks Hue when the Job Browser is blacklisted (#3668)
* [64adde0033](https://github.com/cloudera/hue/commit/64adde0033) [api] Provide configs to control CORS
* [fd2cfdd56b](https://github.com/cloudera/hue/commit/fd2cfdd56b) [docker] fix Huefrontend pod going to carshloopbackoff state (#3658)
* [4bd2f36b37](https://github.com/cloudera/hue/commit/4bd2f36b37) [raz] Improve RAZ HA unit tests (#3651)
* [1f64deec8a](https://github.com/cloudera/hue/commit/1f64deec8a) [Trino] Adding explain query method (#3645)
* [c8872fceea](https://github.com/cloudera/hue/commit/c8872fceea) [editor] Fix a bug where saving an actual notebook has the incorrect document type (#3655)
* [08037bdca8](https://github.com/cloudera/hue/commit/08037bdca8) [knox_jwt] Improve unit tests for Knox JWT HA support (#3650)
* [57523a1b9e](https://github.com/cloudera/hue/commit/57523a1b9e) [jb] Various mini Job Browser improvements (#3654)
* [42055b421d](https://github.com/cloudera/hue/commit/42055b421d) [frontend] Turn all current linting warnings into errors (#3649)
* [46347faafd](https://github.com/cloudera/hue/commit/46347faafd) Fixing the issues in the PR
* [a3d9da04ad](https://github.com/cloudera/hue/commit/a3d9da04ad) Fixing the jest
* [64c749e9a8](https://github.com/cloudera/hue/commit/64c749e9a8) Unit testing
* [27503c6975](https://github.com/cloudera/hue/commit/27503c6975) Fixed Linting issues
* [0f1c58c87d](https://github.com/cloudera/hue/commit/0f1c58c87d) [frontend] Dismiss info alert popup messages after 3 seconds
* [b9957215af](https://github.com/cloudera/hue/commit/b9957215af) [jb] Split the Job Browser mako into a regular and mini version and extract inline js (#3646)
* [2ad938111a](https://github.com/cloudera/hue/commit/2ad938111a) [Trino] Adding unittest for trino (#3643)
* [fe9968c0d5](https://github.com/cloudera/hue/commit/fe9968c0d5) [test] Add unit test for updating the corrdinator URL pattern in Impala mini job browser
* [7f2b78897c](https://github.com/cloudera/hue/commit/7f2b78897c) [pylint] Fix the long line in Impala conf
* [4b3e9cc97d](https://github.com/cloudera/hue/commit/4b3e9cc97d) [editor] Update the corrdinator URL pattern in Impala mini job browser
* [0e711eacb0](https://github.com/cloudera/hue/commit/0e711eacb0) [idbroker] Refactor IDBroker with improved HA support and giving more preference to RAZ when both are configured in Hue (#3626)
* [4ed5b0bd84](https://github.com/cloudera/hue/commit/4ed5b0bd84) [pypi] Upgrade PyYAML package to 6.0.1 (#3635)
* [a17d4995b5](https://github.com/cloudera/hue/commit/a17d4995b5) [Trino] Refactor Trino-related code for readability and maintainability (#3637)
* [55ab28d636](https://github.com/cloudera/hue/commit/55ab28d636) [api] Add new /content_summary public api (#3620)
* [a46b3b64b4](https://github.com/cloudera/hue/commit/a46b3b64b4) [frontend] Advance the 'AND' rule in the definition of 'between' syntax for Hive and Presto (#3561)
* [2e780cb48c](https://github.com/cloudera/hue/commit/2e780cb48c) [log] Remove the comment of dev only in log conf files (#3636)
* [ba093b20a6](https://github.com/cloudera/hue/commit/ba093b20a6) Addeing HuePubSub for wrning messages (#3585)
* [5a1103e394](https://github.com/cloudera/hue/commit/5a1103e394) [docker] Upgrade PostgresSQL version from 13 to 15 (#3634)
* [437bcfbdfa](https://github.com/cloudera/hue/commit/437bcfbdfa) [ci] Updated versions of CI github actions to resolve deprecation warnings (#3629)
* [66699ebb52](https://github.com/cloudera/hue/commit/66699ebb52) [ci] increase muffet buffer size for dead link testing of docs (#3627)
* [8dd2540553](https://github.com/cloudera/hue/commit/8dd2540553) [Trino] Add ldap/basic username and password authentication support (#3624)
* [90e6dea36f](https://github.com/cloudera/hue/commit/90e6dea36f) [compute] set default user/pass for hive from config
* [fe23844f87](https://github.com/cloudera/hue/commit/fe23844f87) [raz][gs] Fix init call for RazGSConnection (#3622)
* [3f3f8e953c](https://github.com/cloudera/hue/commit/3f3f8e953c) [frontend] added missing end curly bracket that broke template (#3621)
* [18c9d8cf5d](https://github.com/cloudera/hue/commit/18c9d8cf5d) [raz] Improve RazGSConnection class for better code readability (#3617)
* [bb06b251f5](https://github.com/cloudera/hue/commit/bb06b251f5) [raz] Improve RazS3connection class for better readability (#3612)
* [79e427873d](https://github.com/cloudera/hue/commit/79e427873d) [api] Add new /rename public api (#3619)
* [b25d6d6192](https://github.com/cloudera/hue/commit/b25d6d6192) [Trino] Reformatting the return of the show_table for autocomplete call (#3616)
* [5eebfb73fe](https://github.com/cloudera/hue/commit/5eebfb73fe) [frontend] Introduced a new info message popup (#3571)
* [447c45a6cb](https://github.com/cloudera/hue/commit/447c45a6cb) [api] Add new /touch public api (#3615)
* [4d5785858a](https://github.com/cloudera/hue/commit/4d5785858a) [Trino] Add Trino pypi package in requirements (#3618)
* [667ae0679c](https://github.com/cloudera/hue/commit/667ae0679c) [raz] Remove old unused Raz client code (#3611)
* [6b693d874c](https://github.com/cloudera/hue/commit/6b693d874c) [Trino] Adding catalog support (#3610)
* [55f561bc7e](https://github.com/cloudera/hue/commit/55f561bc7e) [frontend] added 'hue' to metastore url prefix when running Knox
* [20f3cf466a](https://github.com/cloudera/hue/commit/20f3cf466a) [Trino] Add V1 support trino dialect (#3601)
* [fb0bf97e18](https://github.com/cloudera/hue/commit/fb0bf97e18) [compute] fixed the example installation for hive/impala computes
* [2290b149e3](https://github.com/cloudera/hue/commit/2290b149e3) [ci] Run frontend CI for all PRs (#3608)
* [0ba8f8f7a4](https://github.com/cloudera/hue/commit/0ba8f8f7a4) [ci] Remove old py2 docker image based py3.8 CircleCI check (#3607)
* [ac97eabe42](https://github.com/cloudera/hue/commit/ac97eabe42) [api] Add new /mkdir public API (#3597)
* [dcbdd017f1](https://github.com/cloudera/hue/commit/dcbdd017f1) [docs] Add Kyuubi JDBC config section (#3593)
* [01d00997b9](https://github.com/cloudera/hue/commit/01d00997b9) [frontend] Fix the error, info and warning alert message popups (#3578)
* [d99fc474bf](https://github.com/cloudera/hue/commit/d99fc474bf) [frontend] Added required global LESS changes from downstream
* [0f2693ceab](https://github.com/cloudera/hue/commit/0f2693ceab) [build] Update latest MySQL RPM for CentOS 7 (#3602)
* [cc7b6311ae](https://github.com/cloudera/hue/commit/cc7b6311ae) Check csrf to see if it has value before setting it up (#3592)
* [551590745f](https://github.com/cloudera/hue/commit/551590745f) [jdbc] Remove Py2 syntax (#3594)
* [94fddd7398](https://github.com/cloudera/hue/commit/94fddd7398) [jdbc] Add a new Kyuubi jdbc connector (#3586)
* [c29201f693](https://github.com/cloudera/hue/commit/c29201f693) [abfs] Fix none check for ABFSStat attributes (#3589)
* [a07544c895](https://github.com/cloudera/hue/commit/a07544c895) [docker] Upgrade PostgresSQL version from 11 to 13 (#3590)
* [200c9bf47c](https://github.com/cloudera/hue/commit/200c9bf47c) [frontend] Implementation of sorting columns in Storage browser table (#3588)
* [651a090250](https://github.com/cloudera/hue/commit/651a090250) [frontend] Initial Implementation of Storage browser table (#3525)
* [55883fb52d](https://github.com/cloudera/hue/commit/55883fb52d) [gs] Add missing gcs-oauth2-boto-plugin package for non-raz scenarios (#3523)
* [7d34b6ff2d](https://github.com/cloudera/hue/commit/7d34b6ff2d) [ldap] Fix LDAP sync group without import posix group users (#3582)
* [a8fa996fe7](https://github.com/cloudera/hue/commit/a8fa996fe7) CSS changes for chunked_fileuploader (#3581)
* [54564f7bbc](https://github.com/cloudera/hue/commit/54564f7bbc) [frontent] Make KO-react bridge consistently unwrap KO observables
* [f931e4f00d](https://github.com/cloudera/hue/commit/f931e4f00d) Adding new chunking-fileuploader template (#3501)
* [d9f0eae6ae](https://github.com/cloudera/hue/commit/d9f0eae6ae) Working S3, HDFS version, Code added for ADLS and Ozone with Test cases
* [50536705ed](https://github.com/cloudera/hue/commit/50536705ed) [raz] Add support for RAZ HA (#3558)
* [8f8e5883a6](https://github.com/cloudera/hue/commit/8f8e5883a6) [s3] Fix delete op for directories and non-ascii keys deletion (#3548)
* [5b8569d0ab](https://github.com/cloudera/hue/commit/5b8569d0ab) [frontend] Remove unsupported browser check
* [5ae2e05b78](https://github.com/cloudera/hue/commit/5ae2e05b78) [frontend] Replace outdated Shepherd tool used for the welcome tour
* [f944a878b7](https://github.com/cloudera/hue/commit/f944a878b7) [frontend] Extend the useHuePubSub hook to allow callbacks
* [e10d8985bd](https://github.com/cloudera/hue/commit/e10d8985bd) [frontend] fix ts lint warnings
* [c6ee29f53b](https://github.com/cloudera/hue/commit/c6ee29f53b) [core] Default to correct editor choice per user with default_app value (#3544)
* [d9cd203fdf](https://github.com/cloudera/hue/commit/d9cd203fdf) Update _index.md
* [10a46d16c4](https://github.com/cloudera/hue/commit/10a46d16c4) mpm_event module to improve apache scalability (#3516)
* [36de9f749a](https://github.com/cloudera/hue/commit/36de9f749a) [frontend] Move global js config from hue.mako to global_js_constants.mako
* [d08f3c24ff](https://github.com/cloudera/hue/commit/d08f3c24ff) [RAZ][S3] Force AnonAuthHandler when Raz is enabled
* [84e8e42318](https://github.com/cloudera/hue/commit/84e8e42318) [frontend] Prevent showing alerts without a message
* [2170231551](https://github.com/cloudera/hue/commit/2170231551) [frontend] Prevent showing multiple alert messages that are the same
* [fdecc6fbb1](https://github.com/cloudera/hue/commit/fdecc6fbb1) [editor] Fix issue where the editor might not have an active DB when the assist DB panel isn't visible on load
* [deac365627](https://github.com/cloudera/hue/commit/deac365627) [frontend] configure jest to work with cuix
* [eb9f673032](https://github.com/cloudera/hue/commit/eb9f673032) [frontend] Fix styling and dismissal of the new error message component
* [72e375f10e](https://github.com/cloudera/hue/commit/72e375f10e) [Importer] Standardizing the Column Name Restrictions in the Importer (#3536)
* [df26eff478](https://github.com/cloudera/hue/commit/df26eff478) [raz] Make user access for GS compatible with existing RAZ implementation (#3511)
* [82fd88d2a2](https://github.com/cloudera/hue/commit/82fd88d2a2) [Importer] Adding an option to copy and not just move files (#3520)
* [8685078d8e](https://github.com/cloudera/hue/commit/8685078d8e) [Importer] Add a regex for column name validation in table (#3530)
* [ea3a7bacdb](https://github.com/cloudera/hue/commit/ea3a7bacdb) [log] Default log level to INFO in all handlers (#3518)
* [f35f6a121f](https://github.com/cloudera/hue/commit/f35f6a121f) [compute] hide jobs, hive and impala tabs in job browser
* [09c1b0b6fa](https://github.com/cloudera/hue/commit/09c1b0b6fa) [compute] don't use session_pool by default
* [b03bfc571e](https://github.com/cloudera/hue/commit/b03bfc571e) [raz] Take S3 bucket region from Hue config instead of from core-site.xml (#3439)
* [45667d5216](https://github.com/cloudera/hue/commit/45667d5216) [frontend] Make it possible to configure the default editor to use for all users in Hue (#3514)
* [d2eaa991f5](https://github.com/cloudera/hue/commit/d2eaa991f5) [frontend] Introduced a new error message popup (#3488)
* [1ab2d9a1cf](https://github.com/cloudera/hue/commit/1ab2d9a1cf) [frontend] Fix vulnerabilities reported by npm audit
* [c7ec72dfcf](https://github.com/cloudera/hue/commit/c7ec72dfcf) [Core] Upgrading Django to address security vulnerabilities (#3453)
* [af6f4a63b9](https://github.com/cloudera/hue/commit/af6f4a63b9) [frontend] Replace deprecated xlink:href with href in svg use elements
* [1bd53ae662](https://github.com/cloudera/hue/commit/1bd53ae662) [gs] Change icon in importer path modal (#3522)
* [23d2b029ca](https://github.com/cloudera/hue/commit/23d2b029ca) [s3] Fix key prefix for directories in copy operation (#3519)
* [ec1a8e70e2](https://github.com/cloudera/hue/commit/ec1a8e70e2) [fb] Add icon branding for Google Storage
* [34207fe88d](https://github.com/cloudera/hue/commit/34207fe88d) [frontend] Add a react icon for Google Storage
* [f076fe4258](https://github.com/cloudera/hue/commit/f076fe4258) handle non numeric id for namespace
* [0e8667ed22](https://github.com/cloudera/hue/commit/0e8667ed22) [compute] check correctly for is_compute for session_type (#3510)
* [f051be86f7](https://github.com/cloudera/hue/commit/f051be86f7) Support custom jceks
* [99f7d0651f](https://github.com/cloudera/hue/commit/99f7d0651f) [compute] Ignore cluster obj when type is direct
* [490c15429e](https://github.com/cloudera/hue/commit/490c15429e) [ABFS] Fix the ABFS filebrowser listing limit (#3500)
* [aac3643548](https://github.com/cloudera/hue/commit/aac3643548) [frontend] Hue at env level hue UI changes
* [12b6e090f9](https://github.com/cloudera/hue/commit/12b6e090f9) [compute] handle case of no hive or impala compute
* [962ae057a3](https://github.com/cloudera/hue/commit/962ae057a3) [query] Stop fetching sample data of a view (#3498)
* [3a042f36f0](https://github.com/cloudera/hue/commit/3a042f36f0) [compute] fixes to handle no available compute and other options
* [2ab1de180c](https://github.com/cloudera/hue/commit/2ab1de180c) [beeswax][compute] set username for computes/hive connection
* [3ce4adb1e5](https://github.com/cloudera/hue/commit/3ce4adb1e5) [frontend]Implement UI for actions toolbar (#3459)
* [09db3e7c1a](https://github.com/cloudera/hue/commit/09db3e7c1a) [ci]Change node version from 14 to 18 in Frontend CI (#3495)
* [08034eaf56](https://github.com/cloudera/hue/commit/08034eaf56) [editor] Fix icon for SparkSQL snippets
* [56271e16c0](https://github.com/cloudera/hue/commit/56271e16c0) [gs] Add Google Storage filebrowser support in Hue (#3455)
* [c5374cbdc4](https://github.com/cloudera/hue/commit/c5374cbdc4) [core][compute] fixed username for query execution
* [6bd5d145bb](https://github.com/cloudera/hue/commit/6bd5d145bb) [core][compute] fixed username for query execution
* [398e71f43a](https://github.com/cloudera/hue/commit/398e71f43a) [gs] Add boto package changes for Hue-GCS feature (#3484)
* [ae1659e60e](https://github.com/cloudera/hue/commit/ae1659e60e) [core][computes] fixed compute selection for variety of requests
* [3faef3b1fc](https://github.com/cloudera/hue/commit/3faef3b1fc) [frontend] Fix various npm audit reported issues (#3467)
* [68d48169a5](https://github.com/cloudera/hue/commit/68d48169a5) [s3] Skip move/copy operation if parent path of source is equal to destination path (#3478)
* [093da4a6db](https://github.com/cloudera/hue/commit/093da4a6db) [circleci] Update ARM64 machine image version (#3483)
* [d265748c98](https://github.com/cloudera/hue/commit/d265748c98) [frontent] move removeLastSlash function up one level
* [6744964a4f](https://github.com/cloudera/hue/commit/6744964a4f) [frontent] fix incorrectly enabled move and copy button in modal
* [da79cb5276](https://github.com/cloudera/hue/commit/da79cb5276) Fix phoenix database and table names case sensitive (#3474)
* [cd0f6bf7b6](https://github.com/cloudera/hue/commit/cd0f6bf7b6) [core][computes] Improved error handling in sync code
* [b82b3880b0](https://github.com/cloudera/hue/commit/b82b3880b0) [abfs] Fix download by reading file correctly instead of extra 1 byte always with every chunk (#3472)
* [86a7b42f29](https://github.com/cloudera/hue/commit/86a7b42f29) Revert "[ABFS] Fix reading file operation by 1 byte (#3470)" (#3471)
* [aa85b51a5d](https://github.com/cloudera/hue/commit/aa85b51a5d) [ABFS] Fix reading file operation by 1 byte (#3470)
* [64536f9de3](https://github.com/cloudera/hue/commit/64536f9de3) [core] Use default interpreter when no compute/connector
* [40f2b2b5ab](https://github.com/cloudera/hue/commit/40f2b2b5ab) [compute] Fixed warehouses sync for impala feng (#3465)
* [077636750e](https://github.com/cloudera/hue/commit/077636750e) [core] Fixed the compute selection logic for query exec
* [7d66781f3d](https://github.com/cloudera/hue/commit/7d66781f3d) [CI] Port doc lint check from CircleCI to Github Actions (#3464)
* [283676c5f9](https://github.com/cloudera/hue/commit/283676c5f9) [core] Moved namespaces and computes to database
* [a51f01ff1f](https://github.com/cloudera/hue/commit/a51f01ff1f) [build] remove cuix dependencies from published npm package
* [e0738cdd61](https://github.com/cloudera/hue/commit/e0738cdd61) Latest virtual-env version crash with Rhel9, falling back to older versions. (#3461)
* [49751e83b7](https://github.com/cloudera/hue/commit/49751e83b7) Fix: Move VIRTUAL_ENV_VERSION and VIRTUAL_ENV_RELOCATABLE_VERSION declaration to correct location (#3457)
* [e5d2f4ea29](https://github.com/cloudera/hue/commit/e5d2f4ea29) pin virtualenv==20.24.4 virtualenv-make-relocatable==0.0.1 (#3456)
* [245c9d1101](https://github.com/cloudera/hue/commit/245c9d1101) [core] Remove redundant library names (#3452)
* [a903e183e1](https://github.com/cloudera/hue/commit/a903e183e1) [frontend]Implement pathbrowser in storage browser with improvements (#3445)
* [dccb946767](https://github.com/cloudera/hue/commit/dccb946767) [importer] Avoid creating scratchdir outside of encryption zone (#3447)
* [082dfdc63e](https://github.com/cloudera/hue/commit/082dfdc63e) hue_loglistener isn't starting. thus logs are not generated. adding python before the log listener path (#3443)
* [5981278f13](https://github.com/cloudera/hue/commit/5981278f13) [build] Pin mysqlclient 2.1.1 in Hue build time (#3440)
* [a7db927e5d](https://github.com/cloudera/hue/commit/a7db927e5d) [frontend]Separate breadcrumbs from Pathbrowser component (#3431)
* [bb1b2163b6](https://github.com/cloudera/hue/commit/bb1b2163b6) [commands] Check if Oozie is enabled in desktop document cleanup (#3430)
* [a0d0a62c78](https://github.com/cloudera/hue/commit/a0d0a62c78) [fb] Prevent cross site scripting in file and folder names
* [4bc91b57c5](https://github.com/cloudera/hue/commit/4bc91b57c5) [frontend]Storage Browser Tabs and content component (#3428)
* [78a81b18b1](https://github.com/cloudera/hue/commit/78a81b18b1) [docs] Add export ROOT section in Hue docs  (#3427)
* [895cfd4168](https://github.com/cloudera/hue/commit/895cfd4168) [Importer] Handle malformed data to improve delimiter guessing (#3423)
* [481b1d3a1a](https://github.com/cloudera/hue/commit/481b1d3a1a) [sparksql] Improve complex data type result parsing and add UTs (#3422)
* [0c4719595b](https://github.com/cloudera/hue/commit/0c4719595b) [frontend]Storage Browser initial layout implementation (#3397)
* [3c52e46a92](https://github.com/cloudera/hue/commit/3c52e46a92) Upgrading ipython, py and sqlparse library
* [3ee0d27a72](https://github.com/cloudera/hue/commit/3ee0d27a72) [Core] Add sles15 build script and removing 'bc' cmd logic
* [03510df34c](https://github.com/cloudera/hue/commit/03510df34c) [Core] Adding support for Redhat9 PPC (#3404)
* [5f022baf32](https://github.com/cloudera/hue/commit/5f022baf32) [CVE] Bump tough-cookie from 4.0.0 to 4.1.3 (#3381)
* [702c967358](https://github.com/cloudera/hue/commit/702c967358) [CVE] Bump word-wrap from 1.2.3 to 1.2.4 (#3406)
* [bb36f480d4](https://github.com/cloudera/hue/commit/bb36f480d4) [docs] Update Apache Ozone support in Hue docs section (#3410)
* [24152239c7](https://github.com/cloudera/hue/commit/24152239c7) [editor] Sanitize contents when copying results to the clipboard
* [475a60697d](https://github.com/cloudera/hue/commit/475a60697d) [security][knox] include hue_lb in the list of allowed hosts
* [65344d1dbb](https://github.com/cloudera/hue/commit/65344d1dbb) [docs] Improve public API doc sections (#3401)
* [5f47853af5](https://github.com/cloudera/hue/commit/5f47853af5) [frontend] Bump the version to 6.0.0 and publish a new NPM package (#3405)
* [3a0a0138ca](https://github.com/cloudera/hue/commit/3a0a0138ca) Revert "[core] Adde Hue LB's to the CSRF_TRUSTED_ORIGINS list (#3348)"
* [a463d3992f](https://github.com/cloudera/hue/commit/a463d3992f) [jobbrowser] fix ms conversion precision in job start_time (#3398)
* [02a46499c7](https://github.com/cloudera/hue/commit/02a46499c7) [dockerfile] Remove sudo as it clears http_proxy set by --build-arg (#3303)
* [c5f6a61c7b](https://github.com/cloudera/hue/commit/c5f6a61c7b) Hue [py3] Enable SAML certificate creation with passphrase support.
* [3d5d036e21](https://github.com/cloudera/hue/commit/3d5d036e21) [PIP] Upgrade cryptography python module from cryptography==36.0.1 to cryptography==41.0.1 in requirements.txt
* [3c0298e78e](https://github.com/cloudera/hue/commit/3c0298e78e) [PIP] Upgrading pysaml2-7.3.1 version in base_requirements.txt
* [eab9142214](https://github.com/cloudera/hue/commit/eab9142214) [py3] Update default SAML signing algorithm from SHA1 to SHA256
* [878587b555](https://github.com/cloudera/hue/commit/878587b555) Hue [py3] Enable SAML certificate creation with passphrase support.
* [4bc796ba19](https://github.com/cloudera/hue/commit/4bc796ba19) [SAML] Upgrade pysaml2 python library from pysaml2-5.0.0 to pysaml2-7.3.1 in ext-py3 folder.
* [40189a366e](https://github.com/cloudera/hue/commit/40189a366e) Revert "[core] Add psycopg2-binary 2.9.6 for Python 3 (#3340)"
* [ef9d73960e](https://github.com/cloudera/hue/commit/ef9d73960e) Revert "[core] Add mysqlclient 2.1.1 for Python 3 (#3339)"
* [8b41801713](https://github.com/cloudera/hue/commit/8b41801713) [jb] Allow rerun of multiple selected tasks in the schedules page
* [0e4c632ca2](https://github.com/cloudera/hue/commit/0e4c632ca2) [jb] Uncheck jobs that transition between completed and running
* [fe26fd2d57](https://github.com/cloudera/hue/commit/fe26fd2d57) [jb] Fix broken pagination in the Job Browser schedules tasks table
* [d193a45a10](https://github.com/cloudera/hue/commit/d193a45a10) [jb] Add status filter to the tasks listing of an Oozie schedule in the Job Browser
* [54dd39be0f](https://github.com/cloudera/hue/commit/54dd39be0f) [jb] Add support for middle button/ctrl/cmd click to open Oozie related links in a new tab
* [d5afd2ae5d](https://github.com/cloudera/hue/commit/d5afd2ae5d) [build] Pin mysqlclient 2.1.1 in Hue build time (#3370)
* [6e4c5f3d90](https://github.com/cloudera/hue/commit/6e4c5f3d90) Pass CSRF token as header in thrift calls (#3359)
* [f45bffb3d4](https://github.com/cloudera/hue/commit/f45bffb3d4) fix kill yarn job error when rm ha switch (#2611)
* [c563968708](https://github.com/cloudera/hue/commit/c563968708) [Importer] Iceberg checkbox is visible only for 'Remote File' (#3365)
* [7f07a4474d](https://github.com/cloudera/hue/commit/7f07a4474d) [sdxaas] Improve JWT fetching from Knox HA setup (#3363)
* [3a6e32910a](https://github.com/cloudera/hue/commit/3a6e32910a) Bump luxon from 1.25.0 to 1.28.1 (#3156)
* [e77ec167cd](https://github.com/cloudera/hue/commit/e77ec167cd) [jwt] Support JKU HA for public APIs JWT auth (#3360)
* [42c4711c8e](https://github.com/cloudera/hue/commit/42c4711c8e) [Backend] Fixing logging issue where it throws import desktop error (#3364)
* [2a85dc5001](https://github.com/cloudera/hue/commit/2a85dc5001) [core] Add psycopg2-binary 2.9.6 for Python 3 (#3340)
* [0a5f7aeeab](https://github.com/cloudera/hue/commit/0a5f7aeeab) [core] Add mysqlclient 2.1.1 for Python 3 (#3339)
* [88905cc4ec](https://github.com/cloudera/hue/commit/88905cc4ec) [filebrowser] Remove unused attributes in changePermissionModal inputs
* [0fee130f0f](https://github.com/cloudera/hue/commit/0fee130f0f) [filebrowser] Fix of changePermissionModal
* [b0132a3db0](https://github.com/cloudera/hue/commit/b0132a3db0) [docs] Add api version and improve custom auth section for public apis (#3358)
* [38da1583d4](https://github.com/cloudera/hue/commit/38da1583d4) [jwt] Remove redundant IS_ENABLED config (#3357)
* [06b9e1449e](https://github.com/cloudera/hue/commit/06b9e1449e) [core] Upgrade werkzeug to 2.3.6 (#3353)
* [4d303a0550](https://github.com/cloudera/hue/commit/4d303a0550) [api] Introduce API versioning for public APIs (#3352)
* [e4f5bf99cf](https://github.com/cloudera/hue/commit/e4f5bf99cf) [conf] Improve DISABLE_LOCAL_STORAGE default value (#3351)
* [2efc352491](https://github.com/cloudera/hue/commit/2efc352491) [core] Adde Hue LB's to the CSRF_TRUSTED_ORIGINS list (#3348)
* [74e93fedd0](https://github.com/cloudera/hue/commit/74e93fedd0) Add support for XFF header in Knox and SAML logins (#3325)
* [b37ac5907c](https://github.com/cloudera/hue/commit/b37ac5907c) Enable temporarily disabled lint check (#3350)
* [c15a08addf](https://github.com/cloudera/hue/commit/c15a08addf) [Backend] Fixing Hue LOG issue. Hue has __name__ tag present in the getLogger object,
* [d2ffc44e8b](https://github.com/cloudera/hue/commit/d2ffc44e8b) Temporarily disabling lint check (#3349)
* [f18275f189](https://github.com/cloudera/hue/commit/f18275f189) [jwt] Improve external JWT authentication for public APIs (#3337)
* [ac22f6feaf](https://github.com/cloudera/hue/commit/ac22f6feaf) [Backend] DATABASE_LOGGING when turned off does not generate detailed SQL debug logs.
* [b65608acbc](https://github.com/cloudera/hue/commit/b65608acbc) [frontend] removed _ typo
* [3df0b6da66](https://github.com/cloudera/hue/commit/3df0b6da66) [frontent] fixed incorrect namespaceId that caused assistpanel to switch to default DB
* [0c46dba792](https://github.com/cloudera/hue/commit/0c46dba792) [Core] Adding Redhat9 support (#3342)
* [4310ae229d](https://github.com/cloudera/hue/commit/4310ae229d) [Python2] Removing python2 related docs (#3341)
* [0b7c6466e4](https://github.com/cloudera/hue/commit/0b7c6466e4) [jdbc] Make raised exceptions syntax Py3 compatible (#3344)
* [f55721a8b5](https://github.com/cloudera/hue/commit/f55721a8b5) [core] Removing all the python2 libraries (#3319)
* [0c9360b719](https://github.com/cloudera/hue/commit/0c9360b719) [Backend] Fixing hue debug level issue
* [07fdafb4d3](https://github.com/cloudera/hue/commit/07fdafb4d3) [Dockerfile] Add /var/log/hue folder for loading log data (#3326)
* [6615635910](https://github.com/cloudera/hue/commit/6615635910) update connector athena docs (#3333)
* [8bd9a156b9](https://github.com/cloudera/hue/commit/8bd9a156b9) [docs] Fix few dead links (#3336)
* [25de430c66](https://github.com/cloudera/hue/commit/25de430c66) [sqlalchemy] Add vars 'work_group' and 'catalog_name' from python lib PyAthena for AWS Athena connector (#3327)
* [bb45a00047](https://github.com/cloudera/hue/commit/bb45a00047) [ui] Knockout wrongly mounts invisible components (#3330)
* [283e24fc32](https://github.com/cloudera/hue/commit/283e24fc32) PamBackend authentication fails with PAM_AUTH_ERR or PAM_SYSTEM_ERR (#3322)
* [48918f5a0e](https://github.com/cloudera/hue/commit/48918f5a0e) [log] Improve Hue logging (#3313)
* [c0dc0b90f5](https://github.com/cloudera/hue/commit/c0dc0b90f5) Initialize DB connection for the worker processes and close them when the process ends (#3317)
* [5d26aafb8b](https://github.com/cloudera/hue/commit/5d26aafb8b) [makefile] Fix virtual-env creation based on python version (#3310)
* [d246eced92](https://github.com/cloudera/hue/commit/d246eced92) [ci] Remove py2 CI and update other checks (#3316)
* [9c1f4b8513](https://github.com/cloudera/hue/commit/9c1f4b8513) [jb] Clear the widget status on workflow rerun (#3315)
* [f2425d6a37](https://github.com/cloudera/hue/commit/f2425d6a37) Add cache-control headers to restrict webpage caching (#3296)
* [f781abe749](https://github.com/cloudera/hue/commit/f781abe749) [core] Upgrade django-auth-ldap to 4.3.0 and python-ldap to 3.4.3 (#3306)
* [5e3a74867c](https://github.com/cloudera/hue/commit/5e3a74867c) [raz] Skip using RAZ DTs for FS operation authorisation RAZ check (#3302)
* [2131422ec4](https://github.com/cloudera/hue/commit/2131422ec4) [core] Add cx_Oracle 8.3.0 in base requirements (#3298)
* [511ef3b0d2](https://github.com/cloudera/hue/commit/511ef3b0d2) [blog] Fix Ozone HttpFS endpoint URL scheme (#3299)
* [29b4cb1789](https://github.com/cloudera/hue/commit/29b4cb1789) [raz] Add JWT support for Hue-Raz Integration (#3289)
* [e13273e9d0](https://github.com/cloudera/hue/commit/e13273e9d0) [log] Fix missing gunicorn_log.conf file in /etc/hue/conf folder.
* [c04065313c](https://github.com/cloudera/hue/commit/c04065313c) Bump webpack from 5.54.0 to 5.76.0
* [fea91a9a98](https://github.com/cloudera/hue/commit/fea91a9a98) [config] Escape passwords in URLs for dump_config (#2753)
* [114b723a59](https://github.com/cloudera/hue/commit/114b723a59) [importer] use importer snippet type instead of custom type (#3268)
* [def46f4615](https://github.com/cloudera/hue/commit/def46f4615) [Python3.9] Add github actions for py3.9 (#3295)
* [876d88c95d](https://github.com/cloudera/hue/commit/876d88c95d) [blog] Add blog post for Ozone support in Hue (#3293)
* [1ac136a5d3](https://github.com/cloudera/hue/commit/1ac136a5d3) [Python3.9] encodestring is deprecated in favour of encodebytes and decodestring is deprecated in favour of decodebytes (#3266)
* [f83c07892c](https://github.com/cloudera/hue/commit/f83c07892c) [python3.9] Upgrading greenlet and sasl as old versions are not compatible with py39 (#3290)
* [9ce5af5c20](https://github.com/cloudera/hue/commit/9ce5af5c20) [Build] Download thrift-0.16.0 package from gethue git repo
* [5583fe0282](https://github.com/cloudera/hue/commit/5583fe0282) [Pyhton3.9] Allowing Hue to install virtualenv for >= python3.8 (#3267)
* [305fef9e61](https://github.com/cloudera/hue/commit/305fef9e61) notebook multisession errror: Session matching query does not exist
* [fb6d70f838](https://github.com/cloudera/hue/commit/fb6d70f838) [release] Fix incorrect docker image url in 4.11 release notes
* [be4e2157e4](https://github.com/cloudera/hue/commit/be4e2157e4) Sass and less style cleanup and config improvements (#3283)
* [d543df0bf9](https://github.com/cloudera/hue/commit/d543df0bf9) Hue sends X-Forwarded-For header in thrift calls made via HTTP-transport-mode to Hive (#3176)
* [e390a6128d](https://github.com/cloudera/hue/commit/e390a6128d) [frontend] Add and configure cuix library (#3282)
* [c0443438e9](https://github.com/cloudera/hue/commit/c0443438e9) [download] Fix zero size file downloading for ABFS (#3280)
* [3dbf448397](https://github.com/cloudera/hue/commit/3dbf448397) Hue [backend] Force env variable DESKTOP_LOG_DIR in docker creation
* [eb83387c25](https://github.com/cloudera/hue/commit/eb83387c25) Hue [backend] Fix Hue log not found.
* [0c20905b75](https://github.com/cloudera/hue/commit/0c20905b75) Hue [Backend] Enable support passphrase supported SSL keyfile in KNOWN location
* [f75eb1ff74](https://github.com/cloudera/hue/commit/f75eb1ff74) [Python3.9] isAlive() is deprecated in py3.8 and removed from py3.9 (#3265)
* [aafb87c62a](https://github.com/cloudera/hue/commit/aafb87c62a) [download] Check for binary empty chunk string correctly (#3277)
* [6a85a64a5f](https://github.com/cloudera/hue/commit/6a85a64a5f) [Filebrowser] Add config for upload a file in a filesystem (#3262)
* [ca74ac0cdf](https://github.com/cloudera/hue/commit/ca74ac0cdf) [celery] upgrading celery and virtualenv (#3197)
* [0f80e2690c](https://github.com/cloudera/hue/commit/0f80e2690c) [ozone] Add unit test for get_scheme() for OFS upload
* [8b3fa8130a](https://github.com/cloudera/hue/commit/8b3fa8130a) [ozone] Proper handeling of _get_scheme function in ozone
* [abf131e03b](https://github.com/cloudera/hue/commit/abf131e03b) [ozone] Skip copying files with size greater than chunk size (#3259)
* [922e9578f5](https://github.com/cloudera/hue/commit/922e9578f5) [frontend] Use api/utils for loading Impala data
* [ab914bcb11](https://github.com/cloudera/hue/commit/ab914bcb11) [future] upgrading the future lib (#3255)
* [d6f7b058d7](https://github.com/cloudera/hue/commit/d6f7b058d7) Add if not exists for tmp table when using importer (#3256)
* [4bfb76592f](https://github.com/cloudera/hue/commit/4bfb76592f) [ozone] Disable the 'Action' btn for ozone volumes and buckets (#3257)
* [ec3e6b7134](https://github.com/cloudera/hue/commit/ec3e6b7134) [ozone] Update unit tests for service_id changes
* [42abc4423f](https://github.com/cloudera/hue/commit/42abc4423f) [ozone] Add serviceID in the ofs path
* [310695b485](https://github.com/cloudera/hue/commit/310695b485) [ozone] adding ozone_service_id in path and making corrections accordingly
* [ab27eaa0f4](https://github.com/cloudera/hue/commit/ab27eaa0f4) Adding .gitignore items
* [a1e874e05f](https://github.com/cloudera/hue/commit/a1e874e05f) Hue [core] Improve Logger role with uniq logger config definition
* [2c65c4ff6b](https://github.com/cloudera/hue/commit/2c65c4ff6b) [frontend]Pathbrowser in file chooser to view file path (#3130)
* [0f329ae679](https://github.com/cloudera/hue/commit/0f329ae679) [frontend] Replace ENABLE_NOTEBOOK_2 with ENABLE_HUE_5
* [6ed3d14633](https://github.com/cloudera/hue/commit/6ed3d14633) [frontend] Create a separate upstream GitHub CI workflow for UI (#3248)
* [901544a8b9](https://github.com/cloudera/hue/commit/901544a8b9) [ozone] adding warnings for illegal volume and bucket name (#3247)
* [d0fb106f8b](https://github.com/cloudera/hue/commit/d0fb106f8b) [editor] Ignore case when identifying tables for the right assist and editor locations
* [6be9383d36](https://github.com/cloudera/hue/commit/6be9383d36) [editor] Fix argument positions for nvl2 in the embedded Impala reference manual
* [4b987a200c](https://github.com/cloudera/hue/commit/4b987a200c) Hue [core] Hue needs to run under UBI8 docker. version 2
* [20f8e5b8e3](https://github.com/cloudera/hue/commit/20f8e5b8e3) Hue [core] Hue needs to run under UBI8 docker.
* [0319ab57e4](https://github.com/cloudera/hue/commit/0319ab57e4) [frontend] Display Impala query history details (#3226)
* [d00605b4b3](https://github.com/cloudera/hue/commit/d00605b4b3) Hue [core] Fix desktop.log.basic_logging call in rungunicornserver.py (#3239)
* [ec50f22ac8](https://github.com/cloudera/hue/commit/ec50f22ac8) [fb] Add custom icon for the Ozone File Browser
* [37dcd1bf25](https://github.com/cloudera/hue/commit/37dcd1bf25) [frontend] fix encoding when linking from assistpanel to Filebrowser
* [61609775df](https://github.com/cloudera/hue/commit/61609775df) [frontend] fix for jobbrowser table to handle horizontal overflow
* [74bafc7cb7](https://github.com/cloudera/hue/commit/74bafc7cb7) [raz] Dont refer client cache of default Hue user for FS client (#3229)
* [e98d2324b8](https://github.com/cloudera/hue/commit/e98d2324b8) [backend] Pull hue_image_version from hue config (#3233)
* [b15b1d4350](https://github.com/cloudera/hue/commit/b15b1d4350) Hue [core] Hue log file randomly gets rotated and Hue log lines goes missing. After using gunicorn base WSGI server, noticed the issue.
* [9b29e282e8](https://github.com/cloudera/hue/commit/9b29e282e8) Hue [core] Adding supervisor conf for Hue log listener command.
* [e8689c28a8](https://github.com/cloudera/hue/commit/e8689c28a8) Revert "[backend] mask server response header due to security vulnerabilities (#3222)" (#3232)
* [7e3760bed9](https://github.com/cloudera/hue/commit/7e3760bed9) [frontend] Add CI package.json dependency version check
* [b957904c90](https://github.com/cloudera/hue/commit/b957904c90) [backend] mask server response header due to security vulnerabilities (#3222)
* [4797e70f39](https://github.com/cloudera/hue/commit/4797e70f39) [backend]Display hue_image_version, virtual warehouse name on Hue UI. (#3221)
* [05f50b3d00](https://github.com/cloudera/hue/commit/05f50b3d00) [ozone] Better naming for abspath var and using rename API for rename operation (#3225)
* [731cc5cfe7](https://github.com/cloudera/hue/commit/731cc5cfe7) [ozone] Improve fs_defaultfs check and uploadhandler
* [08d1474354](https://github.com/cloudera/hue/commit/08d1474354) [ozone] Add unit tests and update existing tests for ofs
* [f050809f66](https://github.com/cloudera/hue/commit/f050809f66) [ozone] Connect ofs like other filesystems
* [957fe509d4](https://github.com/cloudera/hue/commit/957fe509d4) [ozone] Add fs_defaultfs in path in importer
* [de3a3e686f](https://github.com/cloudera/hue/commit/de3a3e686f) [ozone] Add UI changes
* [05e4855aa8](https://github.com/cloudera/hue/commit/05e4855aa8) [ozone] Add ofs upload filehandler
* [3a067c460e](https://github.com/cloudera/hue/commit/3a067c460e) [Ozone] Add ofsstat separately
* [6cc167afcc](https://github.com/cloudera/hue/commit/6cc167afcc) [ozone] add ofs client
* [6b03c71486](https://github.com/cloudera/hue/commit/6b03c71486) [ozone] Add initial config under desktop
* [9b90d3f083](https://github.com/cloudera/hue/commit/9b90d3f083) [frontend] Add support for showing versions and warehouse name in the left sidebar footer
* [73b9041358](https://github.com/cloudera/hue/commit/73b9041358) [backend/file-browser] config for file-download cache-control
* [7983aabacd](https://github.com/cloudera/hue/commit/7983aabacd) [docs] new blogpost about community
* [b2a2b97714](https://github.com/cloudera/hue/commit/b2a2b97714) [backend/core] remove weaker cipher suites from defaults
* [354850eb1c](https://github.com/cloudera/hue/commit/354850eb1c) New react toolbar component
* [d3df801115](https://github.com/cloudera/hue/commit/d3df801115) Adding connection timeout for zookeeper connection to get hive znode (#3212)
* [154145448f](https://github.com/cloudera/hue/commit/154145448f) [ci] Update apt cache before installing packages (#3214)
* [7cd42462ec](https://github.com/cloudera/hue/commit/7cd42462ec) Hue ID Broker HA improvement (#3211)
* [60075322a6](https://github.com/cloudera/hue/commit/60075322a6) [github] Update auto-close bot and use 'Prevent stale' label
* [58f64d19aa](https://github.com/cloudera/hue/commit/58f64d19aa) [frontend] upgrade bootstrap to 3.4.1 for CVE-2019-8331
* [b08e4442cf](https://github.com/cloudera/hue/commit/b08e4442cf) [frontend] update jQuery to 3.5.1 to fix CVE
* [a170183167](https://github.com/cloudera/hue/commit/a170183167) [frontend]Fix for sidebar accordian collapse icon failing in safari
* [a4eadb120d](https://github.com/cloudera/hue/commit/a4eadb120d) [build] upgrade webpack to 5.54.0 and specify hashFunction to fix broken build
* [8bfb98ebee](https://github.com/cloudera/hue/commit/8bfb98ebee) [community] upstream only change to improve github issues template
* [82061a7e66](https://github.com/cloudera/hue/commit/82061a7e66) [ci] Add pylint check for py3.8 CI (#3190)
* [d327f56da5](https://github.com/cloudera/hue/commit/d327f56da5) [backend/gunicorn] add configs for request header limits
* [2e1cbecf51](https://github.com/cloudera/hue/commit/2e1cbecf51) Add conf license for Ozone V1 skeleton (#3188)
* [eda7fbebfc](https://github.com/cloudera/hue/commit/eda7fbebfc) [raz] Fix rename and cases of % in path for RAZ ABFS (#3173)
* [57434c1ece](https://github.com/cloudera/hue/commit/57434c1ece) [core] sorting the document according to the dependencies (#3157)
* [e4bb6bba55](https://github.com/cloudera/hue/commit/e4bb6bba55) Revert only py2 version of phoenixdb 1.2.1 (#3184)
* [ba7ad20ba1](https://github.com/cloudera/hue/commit/ba7ad20ba1) [frontend] add reusable component PushDrawer
* [559106f683](https://github.com/cloudera/hue/commit/559106f683) Upgrade urllib3 to 1.26.12 due to critical CVEs (#3181)
* [38e803ceb8](https://github.com/cloudera/hue/commit/38e803ceb8) [blog] url correction (#3177)


### Contributors

This Hue release is made possible thanks to the contribution from:

* Aleksandr Efimov
* Amit Srivastava
* Ananya Agarwal
* Athithyaa Selvam
* Ayush Goyal
* Björn Alm
* C.J. Collier
* chengduhaha
* chenlein
* dill
* Evans Sun
* Grzegorz Kołakowski
* Halim Kim
* Harsh Gupta
* Igor Khrol
* Ivan Dzikovsky
* Janos Kovacs
* Johan Åhlén
* laochake
* Maciej Maciejko
* Madhukar
* Mahesh Balakrishnan
* NadafMM
* Nidhi Bhat G
* owenmonn
* pid998877
* Prakash Ranade
* Ram Prasad Agarwal
* sanyam43
* Sonia Park
* Sreenath Somarajapuram
* Tabraiz
* Tarun Jangid
* wgzhao
* xiearthur
* Ying Chen
