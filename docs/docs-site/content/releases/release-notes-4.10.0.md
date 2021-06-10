---
title: "4.10.0"
date: 2021-06-10T00:00:00+00:00
draft: false
weight: -4090
tags: ['skipIndexing']
---

## Hue v4.10.0, released June 14th 2021

Hue is an open source SQL Cloud Assistant for querying [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/): [gethue.com](https://gethue.com)


### Summary

Here is a summary of the [main improvements](https://gethue.com/categories/version-4.10/) of 4.10 on top of the previous [4.9](https://gethue.com/blog/hue-4-9-sql-dialects-phoenix-dasksql-flink-components/) release:


#### SQL Editor Component & API
Now build your own SQL Editor in three HTML line by leveraging the [SQL Scratchpad](https://docs.gethue.com/developer/components/scratchpad/) component. The first version of the public [REST API](https://docs.gethue.com/developer/api/rest/) for executing queries was also published.

Read more about the [SQL Scratchpad and REST API](https://gethue.com/blog/2021-05-29-create-own-sql-editor-via-webcomponent-and-public-api/).

![Adding the component in 3 lines and watching the interaction with the public API of demo.gethue.com](https://cdn-images-1.medium.com/max/2356/1*yXRjYQN_eRUimzlXPl5SwQ.gif)*Adding the component in 3 lines and watching the interaction with the public API of demo.gethue.com*

#### Create Table Wizard

Create a Hive, Impala, MySql, Phoenix SQL table via a small file in three clicks. Just upload it via your browser, without the need to have any Storage filesystem like HDFS or S3 configured and follow the wizard.

Read more about the [create table from a small file](https://gethue.com/blog/2021-05-26-improved-hue-importer-select-a-file-choose-a-dialect-create-a-table/).

![Importer direct upload steps](https://cdn.gethue.com/uploads/2021/05/Importer_direct_upload_steps.gif)

#### Slack App
Collaborate more via Slack thanks to the rich preview of SQL queries, auto links, query bank and export result to Slack.

[Install the app](https://gethue.com/blog/2021-05-18-installing-hue-slack-app-in-three-simple-steps/) in a few clicks and learn more about the [functionalities of assistance](https://docs.gethue.com/user/concept/#slack).

![Slack Installation Flow](https://cdn.gethue.com/uploads/2021/05/slack-install.gif)

#### Tech stack & Tooling

- [Provide your users proper S3 file access without giving them any credential keys](https://gethue.com/blog/2021-04-23-s3-file-access-without-any-credentials-and-signed-urls/)
- [Distribute your container App as a Package](https://gethue.com/blog/2021-04-19-publish-kubernetes-container-application-via-package-with-helm/)
- [Performing Web/API Service upgrades without Downtime](https://gethue.com/blog/2021-03-06-web-api-service-upgrade-no-downtime-kubernetes-rollout/)
- [Interactively Querying HBase via SQL - Tech Talk](https://gethue.com/blog/2021-04-05-interactively-querying-hbase-via-sql-tech-talk/)
- [Process & Learnings when upgrading the Webserver Stack - Django Upgrade (1.11 to 3.1)](https://gethue.com/blog/2021-03-09-process-and-learnings-when-upgrading-the-webserver-stack-django-upgrade-1-to-3/)
- [Introducing Vue 3 & Web Components in Hue Query Editor](https://gethue.com/blog/vue3-build-cli-options-composition-api-template-web-components-hue/)
- Docker Image size [reduced by 60%](https://github.com/cloudera/hue/pull/2129)
- [Phoenix SQL](https://gethue.com/sql-querying-apache-hbase-with-apache-phoenix/) column keys are now displayed in the left assist


It has more than 700+ commits and 100+ bug fixes!

Go grab it and give it a spin!

* Docker
    ```
    docker run -it -p 8888:8888 gethue/4.10.0
    ```
* Kubernetes :
    ```
    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue
    ```
* [demo.gethue.com](https://demo.gethue.com)
* [Tarball](https://cdn.gethue.com/downloads/hue-4.10.0.tgz) or [source](https://github.com/cloudera/hue/archive/release-4.10.0.zip)

### Compatibility

Tested on CentOS versions 6.8+, Red Hat Enterprise Linux (RHEL 6, 7, 8), and Ubuntu 18.04 and 20.04.

Compatible with the two most recent versions of the following browsers:

* Chrome
* Firefox LTS
* Safari
* Microsoft Edge

Runs with Python 2.7+. 3.6+.


### List of commits

* [13fff400b9](https://github.com/cloudera/hue/commit/13fff400b9) [release] 4.10 Blog post
* [cd6255f347](https://github.com/cloudera/hue/commit/cd6255f347) repo changed to gethue
* [1b5af67376](https://github.com/cloudera/hue/commit/1b5af67376) [django_upgrade32] djangomako supporting Mako==1.1.4 now
* [cfc4862973](https://github.com/cloudera/hue/commit/cfc4862973) PR-2235 [editor] Adding missing ANALYZE to the multi statement execution (#2235)
* [5ab70f1ea7](https://github.com/cloudera/hue/commit/5ab70f1ea7) [docs] Fix minor typo in parser section
* [be2de3068a](https://github.com/cloudera/hue/commit/be2de3068a) GH-2331 Query Editor Shows Done 0 results Though Results are available and Loaded on next REST call (#2232)
* [4dba4435b8](https://github.com/cloudera/hue/commit/4dba4435b8) Test Cookies are filling django_session table (#2063)
* [39a91c6022](https://github.com/cloudera/hue/commit/39a91c6022) [raz] Do not get confusing error message on no value arguments
* [8544bff41a](https://github.com/cloudera/hue/commit/8544bff41a) [core] Avoid exception in 500 stack printing view with Python 2
* [ee8212f7a0](https://github.com/cloudera/hue/commit/ee8212f7a0) [raz] Support creating a key by encoding headers
* [d2a8172c19](https://github.com/cloudera/hue/commit/d2a8172c19) [raz] Properly bundle the Raz request arguments
* [7da254adcb](https://github.com/cloudera/hue/commit/7da254adcb) [raz] User parameter is actually username already
* [b1d149e20e](https://github.com/cloudera/hue/commit/b1d149e20e) [docs] Update Slack App installation section
* [cfbdfab5ae](https://github.com/cloudera/hue/commit/cfbdfab5ae) [api] Provide default fs
* [27626876f3](https://github.com/cloudera/hue/commit/27626876f3) [docs] How to get more recent npm installed
* [ecda0379e0](https://github.com/cloudera/hue/commit/ecda0379e0) [api] Add proper configuration settings
* [810539e302](https://github.com/cloudera/hue/commit/810539e302) [docs] List file API
* [2abcb02608](https://github.com/cloudera/hue/commit/2abcb02608) [api] Adding storage browsing
* [ff6a27a9fa](https://github.com/cloudera/hue/commit/ff6a27a9fa) [editor] Port Ace editor v2 to use the new js formatter
* [66a87fd415](https://github.com/cloudera/hue/commit/66a87fd415) [editor] Port Ace editor v1 to use the new js formatter
* [c8a36260ee](https://github.com/cloudera/hue/commit/c8a36260ee) [fs] Stringify the user to get proper username key
* [472cf7f27e](https://github.com/cloudera/hue/commit/472cf7f27e) [api] Switch to public API for get_config()
* [e9325e6525](https://github.com/cloudera/hue/commit/e9325e6525) [slack] Add relevent queries in query bank (#2216)
* [3442808749](https://github.com/cloudera/hue/commit/3442808749) [core] Fix PIP_MODULES installation on build system
* [30571abd24](https://github.com/cloudera/hue/commit/30571abd24) [slack] Add docs link in gethue.com Slack section (#2219)
* [415d2d6ab1](https://github.com/cloudera/hue/commit/415d2d6ab1) [docker] Fix copy of the Slack manifest file
* [55de5e365e](https://github.com/cloudera/hue/commit/55de5e365e) [lib] Fix typo in boto2 request header setting
* [2ca3a6d73a](https://github.com/cloudera/hue/commit/2ca3a6d73a) [raz] Do not hardcode the user in the client
* [dddaec023e](https://github.com/cloudera/hue/commit/dddaec023e) [lib] Change boto2 to not override the User Agent if already present
* [db2ecc8a2b](https://github.com/cloudera/hue/commit/db2ecc8a2b) [raz] Integrating client with boto2
* [07189fead9](https://github.com/cloudera/hue/commit/07189fead9) [raz] Do not harcode method to GET
* [49a03546c8](https://github.com/cloudera/hue/commit/49a03546c8) [lib] Change boto2 to not override the User Agent if already present
* [6bf83972ba](https://github.com/cloudera/hue/commit/6bf83972ba) [docs] Document about form data content type
* [f9e22e1d21](https://github.com/cloudera/hue/commit/f9e22e1d21) [api] Compatibility when connectors are off
* [264ba76c67](https://github.com/cloudera/hue/commit/264ba76c67) [api] Make sure request user is wrapped with UserProfile
* [a507b3d645](https://github.com/cloudera/hue/commit/a507b3d645) as request.headers is new in django 2.2, so now compatible with both django 1.11 and 3.2
* [8ca089f780](https://github.com/cloudera/hue/commit/8ca089f780) [Django upgrade] RemovedInDjango40Warning: request.is_ajax() is deprecated in Django3.1
* [a1ed24be3b](https://github.com/cloudera/hue/commit/a1ed24be3b) [api] Fix slack API disabling all other URLs
* [fad2ae13da](https://github.com/cloudera/hue/commit/fad2ae13da) To disable SSL verification in http_client.py one need to pass it to the session.get(url, verify=False). The current code just sets the _session object which is not taken into account. Verified this fix by making the change in the live cluster.
* [87d40042e5](https://github.com/cloudera/hue/commit/87d40042e5) [docs] Update Slack section in User concepts with latest changes(#2207)
* [8f358c6d4b](https://github.com/cloudera/hue/commit/8f358c6d4b) [libs] Upgrade phoenixdb to 1.1.0.dev0 for Python 2
* [90227c70b2](https://github.com/cloudera/hue/commit/90227c70b2) [slack] Update slack install link for utilize CORS by default for public APIs
* [f5d65b6368](https://github.com/cloudera/hue/commit/f5d65b6368) [slack] Add manifest.yml in Dockerfile
* [79ef48957d](https://github.com/cloudera/hue/commit/79ef48957d) [slack] Fix install_slack_link unit test
* [bb54cd4009](https://github.com/cloudera/hue/commit/bb54cd4009) [raz] Strip the / in the server url
* [7db097f0f9](https://github.com/cloudera/hue/commit/7db097f0f9) [core] Remove duplicated line that cause build issue
* [1e236d3224](https://github.com/cloudera/hue/commit/1e236d3224) [frontend] Switch from the SourceMapDevToolPlugin to cheap-source-map
* [4529a7273d](https://github.com/cloudera/hue/commit/4529a7273d) [frontend] Include .stylelintrc in the CI flow
* [e8be679e36](https://github.com/cloudera/hue/commit/e8be679e36) [frontend] Optimize webpack build performance
* [2833dadc15](https://github.com/cloudera/hue/commit/2833dadc15) [frontend] Upgrade Typescript to the latest version
* [23d522c35a](https://github.com/cloudera/hue/commit/23d522c35a) [frontend] Add style lint to CI setup
* [1e9c5f5955](https://github.com/cloudera/hue/commit/1e9c5f5955) [frontend] Fix all js and style linting issues
* [c46f5e4f55](https://github.com/cloudera/hue/commit/c46f5e4f55) [frontend] Upgrade style, lint and test related packages to the latest versions
* [95838710a6](https://github.com/cloudera/hue/commit/95838710a6) [frontend] Upgrade django-webpack-loader to 1.0.0
* [8fec54e372](https://github.com/cloudera/hue/commit/8fec54e372) [frontend] Upgrade Webpack, Babel and Vue to the latest versions
* [caa210a1c3](https://github.com/cloudera/hue/commit/caa210a1c3) [importer_direct_upload_size] putting the limit (200KB) on size of file uploaded
* [158d2a6d65](https://github.com/cloudera/hue/commit/158d2a6d65) [slack] Enable share_from_editor only when Slack  is_enabled (#2199)
* [41d8010e98](https://github.com/cloudera/hue/commit/41d8010e98) [slack] Refactor for better end-user usability (#2202)
* [0b65573845](https://github.com/cloudera/hue/commit/0b65573845) [slack] Update latest app manifest
* [656c21bc85](https://github.com/cloudera/hue/commit/656c21bc85) [slack] Enable share directly from editor by default
* [29e5fe512b](https://github.com/cloudera/hue/commit/29e5fe512b) [slack] Add `One Click Install` API, add unit test and surface it on gethue.com (#2166)
* [74dd82ff33](https://github.com/cloudera/hue/commit/74dd82ff33) [importer] Enable automatically when direct upload is on
* [7d3134e639](https://github.com/cloudera/hue/commit/7d3134e639) [slack] Add help message for Slack users and update unit tests (#2194)
* [901496d685](https://github.com/cloudera/hue/commit/901496d685) [blog] Updating typos in some of the Scratchpad post links
* [9332c38e39](https://github.com/cloudera/hue/commit/9332c38e39) [blog] First release of SQL Scratchpad and public REST API
* [67fc4f2bb9](https://github.com/cloudera/hue/commit/67fc4f2bb9) [npm] Improve the package index page with direct links to docs
* [c442deaac6](https://github.com/cloudera/hue/commit/c442deaac6) [editor] Avoid sqlAnalyzerProvider.getSqlAnalyzer is not a function
* [eb7a46dc76](https://github.com/cloudera/hue/commit/eb7a46dc76) [docs] Better fit of the live SS in its demo page
* [ef0f464f31](https://github.com/cloudera/hue/commit/ef0f464f31) [docs] Refresh the README
* [0906b6df5d](https://github.com/cloudera/hue/commit/0906b6df5d) [editor] Fix SQL Analyzer related js exeption when predict is enabled
* [bd9ada5a6f](https://github.com/cloudera/hue/commit/bd9ada5a6f) [api] Allow credentials in Cors
* [f59d955896](https://github.com/cloudera/hue/commit/f59d955896) [docs] Fix typos in NPM documentation page
* [569a760da2](https://github.com/cloudera/hue/commit/569a760da2) [docs] Fix wrong API auth URL
* [0cfc5d95f7](https://github.com/cloudera/hue/commit/0cfc5d95f7) [frontend] Bump the NPM version to 4.9.12
* [4181c09c15](https://github.com/cloudera/hue/commit/4181c09c15) [editor] Improved autocompletion around partial backticked identifiers
* [c958dd79d0](https://github.com/cloudera/hue/commit/c958dd79d0) [api] First simplified public Execute Query
* [57522fc31f](https://github.com/cloudera/hue/commit/57522fc31f) [api] Automatically apply CORS to the /api only
* [99eafd0382](https://github.com/cloudera/hue/commit/99eafd0382) [docs] Switch to unpkg for the cdn of the Scratchpad
* [2b89c1076e](https://github.com/cloudera/hue/commit/2b89c1076e) [docs] Refresh npm package page with Scratchpad and Parsers
* [bc8d7b3aeb](https://github.com/cloudera/hue/commit/bc8d7b3aeb) [importer_direct_upload] adding snippet settings for mysql
* [95aab9365c](https://github.com/cloudera/hue/commit/95aab9365c) adding unit test for impala
* [51df6bdc28](https://github.com/cloudera/hue/commit/51df6bdc28) handling the boolend data type for impala
* [81f5e03e88](https://github.com/cloudera/hue/commit/81f5e03e88) [importer_direct_upload_impala] supporting impala dialect for direct upload
* [11ba711bcb](https://github.com/cloudera/hue/commit/11ba711bcb) Improve SAML group check logic, We are now checking one of required groups must be available from the SAML response. (#2182)
* [481f15ea4d](https://github.com/cloudera/hue/commit/481f15ea4d) [frontend] Bump NPM version to 4.9.11
* [18c4d3b70c](https://github.com/cloudera/hue/commit/18c4d3b70c) [frontend] Fix failing tests and lint issues related to SQL scratchpad and new API URLs
* [e48350136f](https://github.com/cloudera/hue/commit/e48350136f) [frontend] Add drop functionality to data catalog entries
* [404d402e1b](https://github.com/cloudera/hue/commit/404d402e1b) [frontend] Extend the js execution api lib with single statement execution
* [10db6fbff6](https://github.com/cloudera/hue/commit/10db6fbff6) [api] Fix duplicate URL rebase conflict
* [855e45ead1](https://github.com/cloudera/hue/commit/855e45ead1) [frontend] Bump NPM version to 4.9.10
* [4221264655](https://github.com/cloudera/hue/commit/4221264655) [frontend] Configure withCredentials for the global Axios instance
* [aac24ec247](https://github.com/cloudera/hue/commit/aac24ec247) [frontend] Improve SQL Scratchpad component styling
* [dea2451ddb](https://github.com/cloudera/hue/commit/dea2451ddb) [frontend] Fix type issues in editor v2 Vue components
* [e55c876bcb](https://github.com/cloudera/hue/commit/e55c876bcb) [frontend] Switch to axios for fetching nav related calls
* [d6c28c4b2b](https://github.com/cloudera/hue/commit/d6c28c4b2b) [frontend] Fix unhandled promise exceptions in assist
* [c358d4012d](https://github.com/cloudera/hue/commit/c358d4012d) [frontend] Enable ts support in the login bundle
* [e2e10c7876](https://github.com/cloudera/hue/commit/e2e10c7876) [frontend] Don't notify errors when silenceErrors is set to true in the API utils
* [edcaf1fc89](https://github.com/cloudera/hue/commit/edcaf1fc89) [frontend] Split hueUtils over multiple modules
* [394145cda6](https://github.com/cloudera/hue/commit/394145cda6) [editor] Externalize the SqlAnalyzer from the AceEditor and AceAutocomplete components
* [2e21d92afb](https://github.com/cloudera/hue/commit/2e21d92afb) [frontend] Introduce a SQL Analyzer provider and rename optimizer to SQL Analyzer in the frontend code
* [e320a6b7d5](https://github.com/cloudera/hue/commit/e320a6b7d5) [frontend] Use relative imports in exported NPM package sources
* [c240af0a10](https://github.com/cloudera/hue/commit/c240af0a10) [slack] Query bank for Assistance V1 (#2154)
* [07a7d4e9b8](https://github.com/cloudera/hue/commit/07a7d4e9b8) [importer_direct_upload] changing sourceType to sourceType() as it is now observable
* [cdc3bb9e11](https://github.com/cloudera/hue/commit/cdc3bb9e11) [api] Apply CORS to /api automatically
* [9ce62e4aea](https://github.com/cloudera/hue/commit/9ce62e4aea) [importer_direct_upload] link correction
* [a455944942](https://github.com/cloudera/hue/commit/a455944942) [libs] Bump djangorestframework-simplejwt
* [405ef8d813](https://github.com/cloudera/hue/commit/405ef8d813) [libs] Bump djangorestframework-simplejwt
* [e2e5d35d35](https://github.com/cloudera/hue/commit/e2e5d35d35) [blog] Improve blog content and fix try-out formatting (#2170)
* [5026cfcd17](https://github.com/cloudera/hue/commit/5026cfcd17) [api] Last Editor API url switches
* [2aa65cfe2c](https://github.com/cloudera/hue/commit/2aa65cfe2c) [docs] Fix various dead links
* [a25b04f47b](https://github.com/cloudera/hue/commit/a25b04f47b) [api] Simplify API and remove /iam prefix
* [ac22366efb](https://github.com/cloudera/hue/commit/ac22366efb) [docs] Add live Scratchpad to its component page
* [a04ffad9f6](https://github.com/cloudera/hue/commit/a04ffad9f6) [api] Unify /auth/ URL
* [db9a2925a8](https://github.com/cloudera/hue/commit/db9a2925a8) [api] Simplify path api/iam/token to api/token
* [84f6446129](https://github.com/cloudera/hue/commit/84f6446129) [docs] Refresh the index page
* [ce0acc7641](https://github.com/cloudera/hue/commit/ce0acc7641) [docs] Deleting the Scheduling user section
* [574bd8e5b6](https://github.com/cloudera/hue/commit/574bd8e5b6) [docs] Fix typos in REST api page
* [b1696e27c7](https://github.com/cloudera/hue/commit/b1696e27c7) [docs] Refactor component pages
* [0e6531a797](https://github.com/cloudera/hue/commit/0e6531a797) [docs] Simplifying Dev API section
* [abaf52e566](https://github.com/cloudera/hue/commit/abaf52e566) [docs] Combining Parser into Dev
* [35484de133](https://github.com/cloudera/hue/commit/35484de133) [docs] Split out Api into REST and Python
* [9ffb06051d](https://github.com/cloudera/hue/commit/9ffb06051d) [docs] Refactor connector API
* [1b10c4b4af](https://github.com/cloudera/hue/commit/1b10c4b4af) [docs] Refresh How to run API administrator
* [3e5f22683e](https://github.com/cloudera/hue/commit/3e5f22683e) [api] Port Editor js tests using the public API
* [4b8d08d719](https://github.com/cloudera/hue/commit/4b8d08d719) [docs] REST API authentication
* [73ac02b1c8](https://github.com/cloudera/hue/commit/73ac02b1c8) [api] Add endpoint for namespace config and dual auth
* [95768cd74d](https://github.com/cloudera/hue/commit/95768cd74d) [api] Switching Scratchpad to use the public API
* [559d673789](https://github.com/cloudera/hue/commit/559d673789) [api] Add user perms to the get_config call
* [36648864f4](https://github.com/cloudera/hue/commit/36648864f4) [docs] About npm install for Centos
* [ab9551da1e](https://github.com/cloudera/hue/commit/ab9551da1e) [api] Have get_config into both private and public URLs
* [a32bbd475c](https://github.com/cloudera/hue/commit/a32bbd475c) [api] Automatically grab the JWT token in axios
* [52672f5fee](https://github.com/cloudera/hue/commit/52672f5fee) [tmp] Rename the get_config API
* [ba8e79e950](https://github.com/cloudera/hue/commit/ba8e79e950) [js] Avoid duplicated get config URL
* [be01df65f0](https://github.com/cloudera/hue/commit/be01df65f0) [api] Add all APIs for Sql Scratchpad
* [cd1b67536f](https://github.com/cloudera/hue/commit/cd1b67536f) [api] Adding current SQL Scratchpad APIs
* [1577f16288](https://github.com/cloudera/hue/commit/1577f16288) [docs] API authentication refresh
* [b37907bf5c](https://github.com/cloudera/hue/commit/b37907bf5c) [api] Moving urls into its own module
* [4fc516fb38](https://github.com/cloudera/hue/commit/4fc516fb38) [importer_direct_upload] default value to 'true' in ini files
* [d42dcbf832](https://github.com/cloudera/hue/commit/d42dcbf832) [importer_direct_upload_blog] blog post for direct upload in importer is added
* [38ff1992a7](https://github.com/cloudera/hue/commit/38ff1992a7) [slack] Fix dialect when creating gist for detected SQL (#2171)
* [ba80d572cb](https://github.com/cloudera/hue/commit/ba80d572cb) [importer_direct_upload_on] default value change to 'true'
* [784f4cedac](https://github.com/cloudera/hue/commit/784f4cedac) removing trim_statement_semicolon property from connector and removing duplication of primary keys menu
* [9b9695c54b](https://github.com/cloudera/hue/commit/9b9695c54b) improoving the unit test as code changed in main file as we are always trimming the semicolon like hs2 (get_current_statement fu doing this)
* [6b8bfae966](https://github.com/cloudera/hue/commit/6b8bfae966) adding unit test for phoenix sql
* [d041721f32](https://github.com/cloudera/hue/commit/d041721f32) [importer_direct_upload] supporting phoenix dialect for direct upload
* [45221a6a70](https://github.com/cloudera/hue/commit/45221a6a70) [frontend] Add custom Hive naming to the new document assist dropdown
* [f626e07f46](https://github.com/cloudera/hue/commit/f626e07f46) [build] Unblock missing modules in `make apps` target
* [048bd23ed0](https://github.com/cloudera/hue/commit/048bd23ed0) [libs] Upgrade django-extensions to 3.1
* [e65379dd37](https://github.com/cloudera/hue/commit/e65379dd37) [importer_direct_upload] correcting the dialect value when enable_connector=true
* [9a9d2aa09a](https://github.com/cloudera/hue/commit/9a9d2aa09a) [build] `install` target should not trigger a pip2 install for py3
* [70a77e4915](https://github.com/cloudera/hue/commit/70a77e4915) [libs] Adding djangorestframework-simplejwt 3.3
* [7c0586b7c4](https://github.com/cloudera/hue/commit/7c0586b7c4) [build] Refactor pip module list into an variable
* [5380d517c1](https://github.com/cloudera/hue/commit/5380d517c1) [api] Skeleton of Public API with JWT token auth
* [d9884595a8](https://github.com/cloudera/hue/commit/d9884595a8) [libs] Adding PyJWT 1.7.1
* [7986f2aa1a](https://github.com/cloudera/hue/commit/7986f2aa1a) [libs] Adding djangorestframework 3.9.4
* [b148c2b717](https://github.com/cloudera/hue/commit/b148c2b717) [libs] Adding DRF and Jwt plugin to requirements.txt
* [e35e48a16f](https://github.com/cloudera/hue/commit/e35e48a16f) [libs] Upgrade phoenixdb to 1.0.1 with Python 2
* [4fe5217ad1](https://github.com/cloudera/hue/commit/4fe5217ad1) [libs] Upgrade phoenixdb to 1.0.1 with Python 3
* [89f90fbaf9](https://github.com/cloudera/hue/commit/89f90fbaf9) [gist] Update gist modal test snapshot
* [e3228265ea](https://github.com/cloudera/hue/commit/e3228265ea) [gist] Readonly the link field in gist modal
* [3cbf4fa7b1](https://github.com/cloudera/hue/commit/3cbf4fa7b1) [build] Install modules just after virtual-env
* [b9477f277f](https://github.com/cloudera/hue/commit/b9477f277f) [libs] Workaround potential version `GLIBCXX_3.4.26' not found
* [242cff36c7](https://github.com/cloudera/hue/commit/242cff36c7) [build] Unblock crypto lib install in make install
* [5a8efa3217](https://github.com/cloudera/hue/commit/5a8efa3217) [blog] Update the app try-out section and minor markdown changes (#2139)
* [383c14cd5b](https://github.com/cloudera/hue/commit/383c14cd5b) [blog] Update the try-out section in Slack Integration Introduction blog
* [ab0a16328a](https://github.com/cloudera/hue/commit/ab0a16328a) [docker] Do not ignore ext-py for Python2
* [4855838801](https://github.com/cloudera/hue/commit/4855838801) [blog] Add Slack App Installation Blog Post (#2130)
* [d5fb8e849a](https://github.com/cloudera/hue/commit/d5fb8e849a) [slack] Update function name for better readability
* [d17a010b3b](https://github.com/cloudera/hue/commit/d17a010b3b) [lib] Avoid infinite loop on 500 errors in file chooser popup
* [ca0270a21c](https://github.com/cloudera/hue/commit/ca0270a21c) [raz] Refactoring URL splitting to be cleaner
* [fb671b3b95](https://github.com/cloudera/hue/commit/fb671b3b95) [docs] Update Slack Installation section with new App Manifest feature(#2124)
* [3c5e91207d](https://github.com/cloudera/hue/commit/3c5e91207d) [frontend] Enable custom name for Hive interpreters
* [b803bd4828](https://github.com/cloudera/hue/commit/b803bd4828) [slack] Add unit test for SQL detect
* [7b1c798e57](https://github.com/cloudera/hue/commit/7b1c798e57) [slack] Remove gist creation duplication for detected SQL
* [5c8952d3ff](https://github.com/cloudera/hue/commit/5c8952d3ff) [Gist] Add default value to 'name' argument in _gist_create
* [3379dc66e8](https://github.com/cloudera/hue/commit/3379dc66e8) [Gist] Create helper method for gist creation API
* [d8f8b61bf9](https://github.com/cloudera/hue/commit/d8f8b61bf9) [slack] Make detected SQL Gist with default dialect
* [aa49473843](https://github.com/cloudera/hue/commit/aa49473843) [slack] Give gist link for detected SELECT statements
* [67b5d44822](https://github.com/cloudera/hue/commit/67b5d44822) [libs] Upgrade python-daemon==2.2.4
* [e9a1ced1d6](https://github.com/cloudera/hue/commit/e9a1ced1d6) [libs] Upgrade to 0.18 future module
* [4e110b8f1c](https://github.com/cloudera/hue/commit/4e110b8f1c) [phoenix] Diplay Primary Keys information
* [cedf31668d](https://github.com/cloudera/hue/commit/cedf31668d) refactor(docker): about 60% docker image size reduce (1.2GB -->> 480MB, compressed status)
* [edd2f74066](https://github.com/cloudera/hue/commit/edd2f74066) [raz] Large refactoring and adding tests
* [1b8f196493](https://github.com/cloudera/hue/commit/1b8f196493) [raz] Adding MVP of new Client
* [f666e0bd77](https://github.com/cloudera/hue/commit/f666e0bd77) [hive] Avoid session opening failure on older server
* [1722e3cb69](https://github.com/cloudera/hue/commit/1722e3cb69) [tablebrowser] Fix the link in left assist popover to the table in table browser when Knox enabled (#2111)
* [bed974b2a2](https://github.com/cloudera/hue/commit/bed974b2a2) [aws] Convert signed request into a boto HttpRequest
* [0a7d757104](https://github.com/cloudera/hue/commit/0a7d757104) [slack] Create separate SlackBotException based on PopUpException in botserver views.py (#2121)
* [d7877bcc17](https://github.com/cloudera/hue/commit/d7877bcc17) [slack] Add latest version of app manifest
* [5a6fe8852f](https://github.com/cloudera/hue/commit/5a6fe8852f) [slack] Detect SELECT statements in Slack messages
* [f1dd5350c4](https://github.com/cloudera/hue/commit/f1dd5350c4) Update AutocompleteParseResult type (#2119)
* [2e48f0cc70](https://github.com/cloudera/hue/commit/2e48f0cc70) correcting the unittest and using Mock() for user and fs
* [a96081582b](https://github.com/cloudera/hue/commit/a96081582b) [importer_direct_upload] solving the issue of snippet_type and connector_type conflict
* [ae5b51aa65](https://github.com/cloudera/hue/commit/ae5b51aa65) [core] Add a logout url with hue prefix
* [3a1c267c13](https://github.com/cloudera/hue/commit/3a1c267c13) [auth] Allow cors also on cookie auth
* [d27f5d47c9](https://github.com/cloudera/hue/commit/d27f5d47c9) [libs] Apply CORS setting according to the Python version
* [ead4dce42d](https://github.com/cloudera/hue/commit/ead4dce42d) [aws] Do not require any config keys to enable the RAZ integration
* [f37f66860c](https://github.com/cloudera/hue/commit/f37f66860c) [slack] Refactor slack permission check and UTs
* [d0449d3703](https://github.com/cloudera/hue/commit/d0449d3703) [aws] Avoid 500 as S3ListAllBucketsException does not have a message attribute
* [d946fd21d9](https://github.com/cloudera/hue/commit/d946fd21d9) [build] Upgrade pip version
* [bd9f861c44](https://github.com/cloudera/hue/commit/bd9f861c44) [libs] Delete ext-py/cffi-1.14.5
* [b8057ab2dd](https://github.com/cloudera/hue/commit/b8057ab2dd) [libs] Delete ext-py/cryptography-3.3.2
* [b2d73af5dd](https://github.com/cloudera/hue/commit/b2d73af5dd) [build] Add pip install of cryptography lib for Python2
* [08527f8e2d](https://github.com/cloudera/hue/commit/08527f8e2d) [libs] Bump cffi to 1.14.5 in requirements.txt
* [71f46130c6](https://github.com/cloudera/hue/commit/71f46130c6) [libs] Add cffi-1.14.5
* [4cce62b293](https://github.com/cloudera/hue/commit/4cce62b293) [libs] Remove cffi-1.11.5
* [075b8e622c](https://github.com/cloudera/hue/commit/075b8e622c) [docs] Refresh and simplify the SQL Scratchpad docs
* [d84a484730](https://github.com/cloudera/hue/commit/d84a484730) [importer_direct_upload] removing the 'Type' bar if there is only a Table option
* [23cfc278db](https://github.com/cloudera/hue/commit/23cfc278db) [importer_direct_upload] adding connector in snippet to remove the 'type' error
* [c5f3593331](https://github.com/cloudera/hue/commit/c5f3593331) [k8s] Fix API ingress configs
* [153d9fbf5d](https://github.com/cloudera/hue/commit/153d9fbf5d) [slack] Update Slack API links on the frontend
* [bdf7544205](https://github.com/cloudera/hue/commit/bdf7544205) [docs] Update Slack section with new url and minor markdown fixes (#2100)
* [ba7fa5e1c6](https://github.com/cloudera/hue/commit/ba7fa5e1c6) [slack] Update botserver UTs
* [6337d1a48d](https://github.com/cloudera/hue/commit/6337d1a48d) [slack] Email domain check with host domain (#2027)
* [9aaab2c0b3](https://github.com/cloudera/hue/commit/9aaab2c0b3) [slack] Change Slack URLs by adding /desktop (#2096)
* [0ece942c62](https://github.com/cloudera/hue/commit/0ece942c62) Issue 2098 - Fix assignment error when saving Oozie coordinators and bundles.
* [912071709d](https://github.com/cloudera/hue/commit/912071709d) [editor] Automatically open relevant tabs after execution in editor v2
* [c2fe588cf1](https://github.com/cloudera/hue/commit/c2fe588cf1) [importer_direct_upload] correcting the interpreter 'type' to 'dialect'
* [dd8825f053](https://github.com/cloudera/hue/commit/dd8825f053) [frontend] Fix various Vue 3 related issues with the DateRangePicker
* [e8bca34cf3](https://github.com/cloudera/hue/commit/e8bca34cf3) [frontend] Prevent closing the FacetSelector panel on inside click
* [3eb3ae50e8](https://github.com/cloudera/hue/commit/3eb3ae50e8) [frontend] Switch from node-sass to sass
* [f340f0a1d1](https://github.com/cloudera/hue/commit/f340f0a1d1) Bump hosted-git-info from 2.7.1 to 2.8.9
* [39e46cd571](https://github.com/cloudera/hue/commit/39e46cd571) Bump eventlet from 0.24.1 to 0.31.0 in /desktop/core
* [f7488ab52c](https://github.com/cloudera/hue/commit/f7488ab52c) [slack] Reply with msg when user cant aaccess to query
* [ae65c60030](https://github.com/cloudera/hue/commit/ae65c60030) [libs] Bumping PyYaml to 5.4.1 in Python 3
* [15d3c565c4](https://github.com/cloudera/hue/commit/15d3c565c4) [libs] Adding PyYAML-5.4.1
* [97523e3d94](https://github.com/cloudera/hue/commit/97523e3d94) [libs] Removing PyYAML-5.3.1
* [2739f19540](https://github.com/cloudera/hue/commit/2739f19540) [libs] Add cryptography-3.3.2
* [62d69396de](https://github.com/cloudera/hue/commit/62d69396de) [libs] Remove cryptography-2.9
* [7a24937a90](https://github.com/cloudera/hue/commit/7a24937a90) [k8s] Bump the helm version up
* [da35f7c4b0](https://github.com/cloudera/hue/commit/da35f7c4b0) Bump grunt from 1.1.0 to 1.3.0
* [350861fec0](https://github.com/cloudera/hue/commit/350861fec0) Bump lodash from 4.17.19 to 4.17.21
* [bdd61d2606](https://github.com/cloudera/hue/commit/bdd61d2606) [abfs] First skeleton of RAZ client with tests
* [d2342a6637](https://github.com/cloudera/hue/commit/d2342a6637) [rest] Slight clean-up in HttpClient
* [d9fa32fe6b](https://github.com/cloudera/hue/commit/d9fa32fe6b) Double-check https ingress trailing dash
* [9b98a355b6](https://github.com/cloudera/hue/commit/9b98a355b6) [helm] rename current ingress to v1beta
* [43b86d9aa8](https://github.com/cloudera/hue/commit/43b86d9aa8) [helm] create networking.k8s.io/v1 for k8s 1.19+
* [9a24301d8c](https://github.com/cloudera/hue/commit/9a24301d8c) [helm] support custom annotations for ingress
* [c40e996b26](https://github.com/cloudera/hue/commit/c40e996b26) [k8s] Ingress and deployment for Daphne
* [1a97eba9c2](https://github.com/cloudera/hue/commit/1a97eba9c2) [k8s] Add config hash to deployments
* [341b2e80ce](https://github.com/cloudera/hue/commit/341b2e80ce) [k8s] Adding daphne properties
* [27d8ce8dd5](https://github.com/cloudera/hue/commit/27d8ce8dd5) [aws] Adding get key test for RazS3Connection
* [3615d610cb](https://github.com/cloudera/hue/commit/3615d610cb) [aws] Adding more logic to the Raz Client
* [d703e3d7df](https://github.com/cloudera/hue/commit/d703e3d7df) [aws] Adding get key test for SelfSignedUrlS3Connection
* [807a92b32f](https://github.com/cloudera/hue/commit/807a92b32f) [aws] MVP of simpler Connection
* [f44ae03c87](https://github.com/cloudera/hue/commit/f44ae03c87) [aws] Move back url signed file reading to open()
* [5496fcb34f](https://github.com/cloudera/hue/commit/5496fcb34f) [aws] Use signed url directly in boto make_request()
* [a93f76d44a](https://github.com/cloudera/hue/commit/a93f76d44a) [aws] Use S3FileSystemException within the UrlConnections
* [b62f212832](https://github.com/cloudera/hue/commit/b62f212832) [aws] Raz client should take an HTTP action in argument
* [a30692ae1f](https://github.com/cloudera/hue/commit/a30692ae1f) [aws] HEAD on get_key to avoid downloading all the key
* [b881e9dd4c](https://github.com/cloudera/hue/commit/b881e9dd4c) [slack] Add ephemeral message when `select 1` found
* [2072ae34bd](https://github.com/cloudera/hue/commit/2072ae34bd) [frontend] Fix Knox related issues with the ajax interceptors
* [95db44d63d](https://github.com/cloudera/hue/commit/95db44d63d) Use hue service name and port for traefik
* [1491436f40](https://github.com/cloudera/hue/commit/1491436f40) Allow defining extra hosts for ingress
* [d3177a5d41](https://github.com/cloudera/hue/commit/d3177a5d41) [oozie] Fix application path for submit_external_job
* [239304cd45](https://github.com/cloudera/hue/commit/239304cd45) [importer_direct_upload] adding auto default dialect
* [a0296f53e8](https://github.com/cloudera/hue/commit/a0296f53e8) [slack] Add hue username in bot's slack message for author context and update API UTs (#2058)
* [b51ce37449](https://github.com/cloudera/hue/commit/b51ce37449) [aws] MVP of S3 file download via URL
* [fc0423b185](https://github.com/cloudera/hue/commit/fc0423b185) [aws] Move all common get_buckets code in parent method
* [19c0f767b8](https://github.com/cloudera/hue/commit/19c0f767b8) [raz] Add tests for UrlConnection with RAZ client
* [6061cf98b0](https://github.com/cloudera/hue/commit/6061cf98b0) [raz] Refactoring to share common XML unmarshalling
* [5d5151dcab](https://github.com/cloudera/hue/commit/5d5151dcab) [raz] Iteration on file reading
* [f11b3d17cd](https://github.com/cloudera/hue/commit/f11b3d17cd) [build] Moving from nodejs 10 to 14
* [e2c039e36f](https://github.com/cloudera/hue/commit/e2c039e36f) [npm] Switch to using our own sql formatter
* [85c8287e4c](https://github.com/cloudera/hue/commit/85c8287e4c) [importer] adding unit test for direct upload using sourceType as mysql
* [b46ae04f9b](https://github.com/cloudera/hue/commit/b46ae04f9b) Bump rsa from 4.1 to 4.7 in /desktop/core
* [c2fda8e1a8](https://github.com/cloudera/hue/commit/c2fda8e1a8) [importer_direct_upload_mysql] Supporting mysql dialect for the direct upload
* [05dc7aab45](https://github.com/cloudera/hue/commit/05dc7aab45) [docs] localized 23-Apr blog into Japanese
* [9d7fd5dd1e](https://github.com/cloudera/hue/commit/9d7fd5dd1e) [docs] localized 19-Apr blog into Japanese
* [9f0b1807f6](https://github.com/cloudera/hue/commit/9f0b1807f6) [docs] localized 09-Apr blog into Japanese
* [9aec3ae411](https://github.com/cloudera/hue/commit/9aec3ae411) [docs] localized 05-Apr blog into Japanese
* [d36e001078](https://github.com/cloudera/hue/commit/d36e001078) [slack] Add Share from Editor Section and Gist modal improvements (#2049)
* [4aa4b05796](https://github.com/cloudera/hue/commit/4aa4b05796) [importer_direct_upload_hive] Supporting hive dialect for the direct upload
* [4098ab7b5e](https://github.com/cloudera/hue/commit/4098ab7b5e) [importer_direct_upload_dialects] Adding drop down for selecting different dialects
* [7eaeb4069f](https://github.com/cloudera/hue/commit/7eaeb4069f) [raz] Currently need basic Key class as 404 on directories via stats_key()
* [115a13953f](https://github.com/cloudera/hue/commit/115a13953f) [importer_direct_upload] applying if else condition for default source type
* [7038fc9e71](https://github.com/cloudera/hue/commit/7038fc9e71) [importer] Fix filechooser has no initialPath (#2045)
* [b70c5d773b](https://github.com/cloudera/hue/commit/b70c5d773b) [blog] Align image legends on the new line
* [1eaebbf3b9](https://github.com/cloudera/hue/commit/1eaebbf3b9) [blog] How to give end user S3 access without giving away credentials
* [6d5fa77994](https://github.com/cloudera/hue/commit/6d5fa77994) [frontend] Bump the NPM version
* [26d363de96](https://github.com/cloudera/hue/commit/26d363de96) [editor] Simplify the SQL Scratchpad web component
* [e9999b1b1b](https://github.com/cloudera/hue/commit/e9999b1b1b) [raz] Unmarshall bucket object fully (#2042)
* [ceb26e639e](https://github.com/cloudera/hue/commit/ceb26e639e) [sqlalchemy] Hadle when /autocomplete API used to check if table exists
* [be55dd4bac](https://github.com/cloudera/hue/commit/be55dd4bac) [docs] Add channels:read in slack app scopes
* [07e13fd8a0](https://github.com/cloudera/hue/commit/07e13fd8a0) [s3] Propagate prefix key filter to Bucket list key call (#2040)
* [a601b1472b](https://github.com/cloudera/hue/commit/a601b1472b) [api] Add a auto login flag for testing purpose (#2038)
* [5eeb0c4a90](https://github.com/cloudera/hue/commit/5eeb0c4a90) [slack] Add get_channels API, separate slack_client.py and API UTs (#2036)
* [3367313f60](https://github.com/cloudera/hue/commit/3367313f60) [raz] Fix a few typos in the README
* [9a56f9d564](https://github.com/cloudera/hue/commit/9a56f9d564) [raz] Skeleton of Python Raz Client tests
* [dbd9111d4c](https://github.com/cloudera/hue/commit/dbd9111d4c) [editor] Prevent fetching more streaming result on scroll to end in the ResultTable component
* [12f475369c](https://github.com/cloudera/hue/commit/12f475369c) [editor] Show rows in reverse order for streaming results in the ResultTable component
* [6854119521](https://github.com/cloudera/hue/commit/6854119521) [editor] Show failed execution indication in the ResultTable component
* [d75ade5a27](https://github.com/cloudera/hue/commit/d75ade5a27) [editor] Don't silence result related API errors
* [e3fa585ea1](https://github.com/cloudera/hue/commit/e3fa585ea1) [editor] Switch to using the composition API for the ResultTable component
* [be0a6ec893](https://github.com/cloudera/hue/commit/be0a6ec893) [flink] Handle better expired queries (#2032)
* [1996889a77](https://github.com/cloudera/hue/commit/1996889a77) [slack] Add Sharing from Editor config flag (#2031)
* [c9c885be56](https://github.com/cloudera/hue/commit/c9c885be56) [oozie] Replace ABFS path in workflow files with full path (#2025)
* [1d496d77a3](https://github.com/cloudera/hue/commit/1d496d77a3) [importer] improvements in direct upload
* [eea5c7a07d](https://github.com/cloudera/hue/commit/eea5c7a07d) [left-assist] Automatic refresh of left assist on table DDL operation polishing
* [3bc89e1c66](https://github.com/cloudera/hue/commit/3bc89e1c66) [left assist] Automatic refresh of left assist on table DDL operation
* [36a95d03c6](https://github.com/cloudera/hue/commit/36a95d03c6) [docs] Fix Drill link from Mapr to HP
* [dce5696d1a](https://github.com/cloudera/hue/commit/dce5696d1a) [raz] Skeletons of Raz Client and S3 FileSystem via RAZ
* [b9f54d8417](https://github.com/cloudera/hue/commit/b9f54d8417) [sqlalchemy] Avoid error if the dialect does not support get_view_names (#2024)
* [0d8a712ead](https://github.com/cloudera/hue/commit/0d8a712ead) [oozie] Fix wrong if comparisons triggering warnings
* [0760e958a1](https://github.com/cloudera/hue/commit/0760e958a1) Bump django-debug-toolbar from 1.9.1 to 1.11.1 in /desktop/core
* [2a088608ad](https://github.com/cloudera/hue/commit/2a088608ad) [docs] Add how to refresh the helm package
* [5f07a54a5b](https://github.com/cloudera/hue/commit/5f07a54a5b) [blog] Fix Development category tag to be properly displayed
* [52c7837137](https://github.com/cloudera/hue/commit/52c7837137) [core] Add request as positional arg for RemoteUserDjangoBackend
* [8ac29255b8](https://github.com/cloudera/hue/commit/8ac29255b8) [slack] Split UTs for query and gist preview message
* [dab9e8e7f3](https://github.com/cloudera/hue/commit/dab9e8e7f3) [slack] Remove query result section for gist links
* [8372742e6b](https://github.com/cloudera/hue/commit/8372742e6b) [core] Adding CJK and French for check encoding (#1999)
* [80fdeba4f5](https://github.com/cloudera/hue/commit/80fdeba4f5) [docs] Refresh contributing page
* [9af402e95f](https://github.com/cloudera/hue/commit/9af402e95f) [docs] Refresh of SQL Scratchpad component
* [ecb267c9f5](https://github.com/cloudera/hue/commit/ecb267c9f5) [site] Update or remove very old links that are now broken
* [0198bbbad2](https://github.com/cloudera/hue/commit/0198bbbad2) [blog] Distribute your container App as a Package (#2015)
* [9e5039cb8b](https://github.com/cloudera/hue/commit/9e5039cb8b) [core] Call super() in HueRemoteUserMiddleware
* [51ba003622](https://github.com/cloudera/hue/commit/51ba003622) [blog] Adding Introducing Slack Integration for Hue blog post (#1992)
* [cc873ae2da](https://github.com/cloudera/hue/commit/cc873ae2da) Table assist max function does not return max value instead also executes sample query with limit 100 #2011 (#2011)
* [04411c6344](https://github.com/cloudera/hue/commit/04411c6344) [k8s] Refresh to work easily with helm3 and publick repo (#2009)
* [ad931c95b3](https://github.com/cloudera/hue/commit/ad931c95b3) [docs] Add separate Slack sections in User Concepts and Admin Configuration docs (#1991)
* [7c47702d76](https://github.com/cloudera/hue/commit/7c47702d76) [docs] Update gethue/hue install for helm3 (#2010)
* [9e6e1dc5e6](https://github.com/cloudera/hue/commit/9e6e1dc5e6) [docker] Adding example of NGINX timeout setting
* [1095d02508](https://github.com/cloudera/hue/commit/1095d02508) [ui] Also patch another jquery.notify plugin (#2006)
* [6945f585fb](https://github.com/cloudera/hue/commit/6945f585fb) [Importer] adding hasHeader, file_url and unittest to improve the code
* [3c9d0d0295](https://github.com/cloudera/hue/commit/3c9d0d0295) [ui] Avoid displaying any API error in a popup
* [48940dbe60](https://github.com/cloudera/hue/commit/48940dbe60) Bump django from 3.1.7 to 3.1.8 in /desktop/core
* [3fb65ab909](https://github.com/cloudera/hue/commit/3fb65ab909) [Phoenix] Drag & Drop table from assist only sets the table name and not SELECT sample
* [edbd48f485](https://github.com/cloudera/hue/commit/edbd48f485) [frontend] Bump the npm version to 4.9.7
* [c4e802bac9](https://github.com/cloudera/hue/commit/c4e802bac9) [editor] Various query editor web component improvements
* [83c7ee4009](https://github.com/cloudera/hue/commit/83c7ee4009) [sqlalchemy] Fix check_status for saved queries not having result section in snippet
* [51401b8667](https://github.com/cloudera/hue/commit/51401b8667) [libs] Removing another chardet dependency in requests
* [a0fd2ab7f1](https://github.com/cloudera/hue/commit/a0fd2ab7f1) [libs] Deleting requests 2.23
* [f8ad0ca7da](https://github.com/cloudera/hue/commit/f8ad0ca7da) [libs] Comment chardet dependency in requests module config
* [e74696fbbb](https://github.com/cloudera/hue/commit/e74696fbbb) [libs] Remove chardet dependency in requests
* [0f0179ce7f](https://github.com/cloudera/hue/commit/0f0179ce7f) [libs] Adding requests 2.25.1
* [8f814d6c67](https://github.com/cloudera/hue/commit/8f814d6c67) [raz] MVP clients examples for ADLS
* [c133ea1761](https://github.com/cloudera/hue/commit/c133ea1761) [lib] Adding apache-ranger lib
* [f4a317fff3](https://github.com/cloudera/hue/commit/f4a317fff3) [importer] Add default_s3_home and initiate value in  getfilesystem (#1983)
* [44ca62f4fe](https://github.com/cloudera/hue/commit/44ca62f4fe) [editor] Smart SQL formatter indentation improvements with sql-formatter
* [ed403a4e43](https://github.com/cloudera/hue/commit/ed403a4e43) [frontend] Add Python-2.0 as valid npm license
* [6518e63adb](https://github.com/cloudera/hue/commit/6518e63adb) adding upload_local_file function to remove the extra code in importer.mako (using the previously available code)
* [318cbfc0fd](https://github.com/cloudera/hue/commit/318cbfc0fd) [importer] polishing importer direct upload
* [b6b18744f1](https://github.com/cloudera/hue/commit/b6b18744f1) [Phoenix] Column autocomplete is failing for empty('') db
* [aca4787eea](https://github.com/cloudera/hue/commit/aca4787eea) [frontend] Bump the npm version
* [4704ac24fc](https://github.com/cloudera/hue/commit/4704ac24fc) [frontend] Add a complete sql-scratchpad web component
* [9015d51487](https://github.com/cloudera/hue/commit/9015d51487) [frontend] Limit baseUrl setting to the active axios instance and add bearer token interceptor
* [793a1ebc42](https://github.com/cloudera/hue/commit/793a1ebc42) [ci] Ignore LDAP tests warnings to avoid GH false positive checks (#1984)
* [43525e1c28](https://github.com/cloudera/hue/commit/43525e1c28) [slack] Improve preview UI (#1977)
* [914ff93e68](https://github.com/cloudera/hue/commit/914ff93e68) [lib] Make sure cors setting can work with Python 2 (#1982)
* [e411d174c0](https://github.com/cloudera/hue/commit/e411d174c0) [Importer] adding direct upload to importer
* [176ad38426](https://github.com/cloudera/hue/commit/176ad38426) [frontend] Various improvements to the SQL Scratchpad example project
* [b8acda12e8](https://github.com/cloudera/hue/commit/b8acda12e8) [frontend] Bump the npm version
* [22022d1bd0](https://github.com/cloudera/hue/commit/22022d1bd0) [frontend] Refresh the new left assist after data catalog cache is cleared
* [f81653a300](https://github.com/cloudera/hue/commit/f81653a300) [frontend] Expose additional functionality on the QueryEditorWebComponents
* [7cd3ffc5ff](https://github.com/cloudera/hue/commit/7cd3ffc5ff) [blog] Adding Phoenix tech talk on querying HBase via SQL (#1974)
* [364ba38ca4](https://github.com/cloudera/hue/commit/364ba38ca4) [ci] Avoid staleness on any issue or PR part of any milestone (#1975)
* [1f687ee5fe](https://github.com/cloudera/hue/commit/1f687ee5fe) [redaction] redaction engine throws exception when the query is having non-ascii character (#1973)
* [ab0114b3b3](https://github.com/cloudera/hue/commit/ab0114b3b3) [Django_middleware] fixing the middleware upgrade issue
* [1bda1a1813](https://github.com/cloudera/hue/commit/1bda1a1813) Bump rsa from 3.4.2 to 4.1 in /desktop/core
* [aa774a6d8b](https://github.com/cloudera/hue/commit/aa774a6d8b) [slack] Fix unfurl preview values for user saved query links (#1957)
* [0e419a7dd6](https://github.com/cloudera/hue/commit/0e419a7dd6) [lib] Revert django-axe 4.5.3 Model removale of trusted column (#1971)
* [c72e74f44a](https://github.com/cloudera/hue/commit/c72e74f44a) [demo] Add missing KnockoutObservable<T>
* [ea1c67faee](https://github.com/cloudera/hue/commit/ea1c67faee) [demo] Bump gethue to 4.9.4
* [15c79071bf](https://github.com/cloudera/hue/commit/15c79071bf) [demo] Removing pack-lock for now (#1970)
* [fdf5df65b9](https://github.com/cloudera/hue/commit/fdf5df65b9) [lib] Revert django-axe 4.5.3 DB migration of `axes_accessattempt.trusted` (#1968)
* [72633f8150](https://github.com/cloudera/hue/commit/72633f8150) [filebrowser] GH-1965 Default Home directory button in Filebrowser should be sanitized and should trust the input from untrusted source (asnaik) (#1966)
* [f2ea2479d1](https://github.com/cloudera/hue/commit/f2ea2479d1) [slack] Add document read permission check for Slack users as Hue users(#1947)
* [1320fe1cb7](https://github.com/cloudera/hue/commit/1320fe1cb7) [auth] Fix SpnegoMiddleware upgrade issue (#1954)
* [23d37da91a](https://github.com/cloudera/hue/commit/23d37da91a) [sqlalchemy] Avoid column autocomplete errors on unknown tables
* [555d707113](https://github.com/cloudera/hue/commit/555d707113) [sqlalchemy] Skip column key metadata retrieval for Phoenix
* [cc6264b920](https://github.com/cloudera/hue/commit/cc6264b920) [core] Enable link sharing option not propagated to UI
* [a0e8940ace](https://github.com/cloudera/hue/commit/a0e8940ace) [doc] correct developer documentation intendation to consider the content as code . (#1956)
* [0392df4dca](https://github.com/cloudera/hue/commit/0392df4dca) [document ] When the username and group name are same, precedence goes to user not group GH-1959 (#1960)
* [0001b34ebd](https://github.com/cloudera/hue/commit/0001b34ebd) Bump lxml from 4.6.2 to 4.6.3 in /desktop/core (#1952)
* [9055ef81fc](https://github.com/cloudera/hue/commit/9055ef81fc) [frontend] Bump NPM version and npm audit fix
* [ed61126cd3](https://github.com/cloudera/hue/commit/ed61126cd3) [frontend] Include the SQL assist and context selector in the packaged editor web components
* [08c22b150d](https://github.com/cloudera/hue/commit/08c22b150d) [frontend] Various improvements to the new assist panel components
* [ef097a6be6](https://github.com/cloudera/hue/commit/ef097a6be6) [frontend] Make sure CSRF token is present before mounting web components
* [e2bbc413ef](https://github.com/cloudera/hue/commit/e2bbc413ef) [frontend] Add drop arrow icon components
* [e89652d70b](https://github.com/cloudera/hue/commit/e89652d70b) [frontend] V1 of new assist panel
* [fd7090a372](https://github.com/cloudera/hue/commit/fd7090a372) [frontend] Switch to new icons in the Autcomplete results for editor v2
* [fe1c190112](https://github.com/cloudera/hue/commit/fe1c190112) [frontend] Add a couple of SQL related icons
* [8882ab5164](https://github.com/cloudera/hue/commit/8882ab5164) [frontend] Add base icon Vue components and adjust the spinner
* [fc8ad8cbac](https://github.com/cloudera/hue/commit/fc8ad8cbac) [frontend] Add the contextCatalog to the published NPM lib
* [a6762c4a4e](https://github.com/cloudera/hue/commit/a6762c4a4e) [frontend] Simplify the context catalog and switch to Axios
* [c162081f8f](https://github.com/cloudera/hue/commit/c162081f8f) [frontend] Add a SqlContextSelector Vue component
* [6608fb3aed](https://github.com/cloudera/hue/commit/6608fb3aed) [frontend] Externalize and add types for Hue config related events
* [324a4bad21](https://github.com/cloudera/hue/commit/324a4bad21) [frontend] Add a "use_new_assist_panel" feature flag
* [6c183cf9a7](https://github.com/cloudera/hue/commit/6c183cf9a7) [editor] Don't show "0" as the left most header in the ResultTable
* [9a81771f28](https://github.com/cloudera/hue/commit/9a81771f28) [docs] User concept section improvements (#1940)
* [791ed6a274](https://github.com/cloudera/hue/commit/791ed6a274) Fix minor typo in share_document_link method docstring
* [87defd31d7](https://github.com/cloudera/hue/commit/87defd31d7) [editor] jHueNotify Error message shown in UI should sanitised to prevent Html injection (#1943)
* [8aa24a8964](https://github.com/cloudera/hue/commit/8aa24a8964) [core] Add step-by-step getting started guide to the docs for macOS Big Sur with Python 3 and M1-based macs
* [4a6456bcf1](https://github.com/cloudera/hue/commit/4a6456bcf1) [frontend] Prevent "uncaught in promise" exceptions from being logged in the console
* [a37d574f3f](https://github.com/cloudera/hue/commit/a37d574f3f) [k8s] Use gunicorn sync mode in helm install for now
* [11bc84b81a](https://github.com/cloudera/hue/commit/11bc84b81a) [optimize] Avoid bubbling-up errors when no activated (#1937)
* [3de09eef75](https://github.com/cloudera/hue/commit/3de09eef75) [sqlalchemy] Avoid errors from auto explain query (#1936)
* [f17dd20451](https://github.com/cloudera/hue/commit/f17dd20451) [core] Sharing document is always turned off (#1935)
* [e27e0d9cef](https://github.com/cloudera/hue/commit/e27e0d9cef) [Django4.0 Warning] RemovedInDjango40Warning: django.utils.http.urlquote() is deprecated in favor of urllib.parse.quote()
* [d055d364d8](https://github.com/cloudera/hue/commit/d055d364d8) [Django4 Warning] RemovedInDjango40Warning: django.utils.http.is_safe_url() is deprecated in favor of url_has_allowed_host_and_scheme()
* [70d51a7fb8](https://github.com/cloudera/hue/commit/70d51a7fb8) [slack] Remove ENABLE_GIST_PREVIEW config flag
* [80ade93312](https://github.com/cloudera/hue/commit/80ade93312) [slack] Update unit tests and refactor views.py (#1923)
* [9df3435f86](https://github.com/cloudera/hue/commit/9df3435f86) [impala] Fix TSessionHandle guid and secret corrupted after save (#1918)
* [ae6f5420b1](https://github.com/cloudera/hue/commit/ae6f5420b1) [docs] Update slightly Sql Scratchpad component
* [6c63af13f3](https://github.com/cloudera/hue/commit/6c63af13f3) [docs] Small styling in demo app README
* [be87d2996b](https://github.com/cloudera/hue/commit/be87d2996b) [core] Fix LOG.warn to LOG.warning (#1926)
* [1b4f8b4856](https://github.com/cloudera/hue/commit/1b4f8b4856) [Dajngo 4.0 Warning] RemovedInDjango40Warning: django.utils.translation.ugettext_lazy() is deprecated in favor of django.utils.translation.gettext_lazy()
* [8feb5ceefa](https://github.com/cloudera/hue/commit/8feb5ceefa) [frontend] Update the SQL Scratchpad example to use the published gethue NPM version
* [2833e62b44](https://github.com/cloudera/hue/commit/2833e62b44) [frontend] Fix dependency resolution when using Hue source files from the published NPM package
* [4736e758d3](https://github.com/cloudera/hue/commit/4736e758d3) [Django4_warning_force_str] RemovedInDjango40Warning: force_text() is deprecated in favor of force_str().
* [2754747b52](https://github.com/cloudera/hue/commit/2754747b52) [slack] Add result file in link preview message thread (#1913)
* [435aa613c8](https://github.com/cloudera/hue/commit/435aa613c8) [ci] Only run autosquash on PR not coming from a Fork (#1916)
* [0f04edb6a1](https://github.com/cloudera/hue/commit/0f04edb6a1) [ci] Refactor stale yml into issue and PR sections (#1915)
* [d42fe8c2a1](https://github.com/cloudera/hue/commit/d42fe8c2a1) [ci] Also check stale PRs (#1912)
* [3cdc56048f](https://github.com/cloudera/hue/commit/3cdc56048f) [Django40 Warning] RemovedInDjango40Warning: smart_text() is deprecated in favor of smart_str()
* [a9a087cf80](https://github.com/cloudera/hue/commit/a9a087cf80) [editor] Handle query history additions in the Query Table instead of snippet for editor v2
* [13822608d8](https://github.com/cloudera/hue/commit/13822608d8) Table creation in Hive or Impala fails with UnicodeDecodeError: 'ascii' codec can't decode byte #1903 (CDPD-22129)
* [4768bd45eb](https://github.com/cloudera/hue/commit/4768bd45eb) [editor] Don't error on missing status for query history
* [553f18697b](https://github.com/cloudera/hue/commit/553f18697b) [frontend] Bump the npm package version
* [fe454e85bc](https://github.com/cloudera/hue/commit/fe454e85bc) [slack] Refactor table logic in _make_result_table and modify preview name
* [789f1fd2a8](https://github.com/cloudera/hue/commit/789f1fd2a8) Add tabulate module to desktop/core/ext-py
* [f1c2c6bd24](https://github.com/cloudera/hue/commit/f1c2c6bd24) [slack] Make result pivot table
* [88bdff1ae4](https://github.com/cloudera/hue/commit/88bdff1ae4) [slack] Use tabulate module instead of Prettytable to make result table
* [538d88ff35](https://github.com/cloudera/hue/commit/538d88ff35) fixing pylint issues
* [417c29125d](https://github.com/cloudera/hue/commit/417c29125d) making the Django 3 first as this is the future going forward and using the same name
* [cbf576d3c3](https://github.com/cloudera/hue/commit/cbf576d3c3) fixing pylint issues
* [6960bfeafc](https://github.com/cloudera/hue/commit/6960bfeafc) [Django40_warning] RemovedInDjango40Warning: django.conf.urls.url() is deprecated in favor of django.urls.re_path()
* [e91d0d6029](https://github.com/cloudera/hue/commit/e91d0d6029) [ci] Run autosquash only on the Hue repo branches (#1904)
* [b4d1f65a57](https://github.com/cloudera/hue/commit/b4d1f65a57) [core] Automatically run with Gunicorn when on Python 3
* [23efb9aa7f](https://github.com/cloudera/hue/commit/23efb9aa7f) [core] Default gunicorn workers to one
* [f1e292d8a5](https://github.com/cloudera/hue/commit/f1e292d8a5) [impala] More explict error when no active session in query browser
* [be177e13ec](https://github.com/cloudera/hue/commit/be177e13ec) [frontend] Update the SQL Scratchpad example with the latest changes
* [873ae4c1f0](https://github.com/cloudera/hue/commit/873ae4c1f0) [editor] Fix issue where the custom autocompleter is only active when the syntax checker is enabled in Editor v2
* [d9aeb224d6](https://github.com/cloudera/hue/commit/d9aeb224d6) [npm] Adding a watched dev version of webpack-npm
* [b06d06784e](https://github.com/cloudera/hue/commit/b06d06784e) [slack] Log prettytable module in ImportError
* [7c40980e4d](https://github.com/cloudera/hue/commit/7c40980e4d) [slack] Add not found message if result not available
* [f76a841a6b](https://github.com/cloudera/hue/commit/f76a841a6b) [slack] Not raise ImportError just pass
* [0549f3db38](https://github.com/cloudera/hue/commit/0549f3db38) [slack] Show fetch result, refactor payload function and better UI
* [d38310375f](https://github.com/cloudera/hue/commit/d38310375f) support clone django babel through http proxy
* [2fbbfc665d](https://github.com/cloudera/hue/commit/2fbbfc665d) [export] When exporting query result to excel it create's wrong HYPERLINK's for results with http GH-1889 (asnaik) (#1890)
* [6ebf6c4de5](https://github.com/cloudera/hue/commit/6ebf6c4de5) [connector] Do not enable Dashboard if main flag if off
* [512e4363ad](https://github.com/cloudera/hue/commit/512e4363ad) [editor] Add a QueryHistoryTable Vue component
* [b4ebf7f9a1](https://github.com/cloudera/hue/commit/b4ebf7f9a1) [frontend] Add generic FileUpload and ImportDocumentsModal Vue components
* [1a84a8c57f](https://github.com/cloudera/hue/commit/1a84a8c57f) [frontend] Externalize HueButton styles
* [c81dbce508](https://github.com/cloudera/hue/commit/c81dbce508) [frontend] Finalize the Modal component
* [54350ccff0](https://github.com/cloudera/hue/commit/54350ccff0) [frontend] Add label option to the Spinner component and fix various styling issues
* [cf1126d428](https://github.com/cloudera/hue/commit/cf1126d428) [frontend] Add page number to Paginator component events
* [f56f76e094](https://github.com/cloudera/hue/commit/f56f76e094) [frontend] Add the option to not show a header in the HueTable component
* [aed0d9a819](https://github.com/cloudera/hue/commit/aed0d9a819) [frontend] Add a small option to the SearchInput component
* [ee6c649864](https://github.com/cloudera/hue/commit/ee6c649864) [frontend] Fix positioning of the DropdownMenu component when opened near the lower edge of the window
* [81962ee7a8](https://github.com/cloudera/hue/commit/81962ee7a8) [frontend] Add generic Axios get wrapper to api utils
* [9904eaa893](https://github.com/cloudera/hue/commit/9904eaa893) [docs] localized latest blogs into Japanese (Three blogs published in March 2021)
* [2fafd839e8](https://github.com/cloudera/hue/commit/2fafd839e8) [editor] Fix syntax checker replacement in editor v2
* [64c34c0add](https://github.com/cloudera/hue/commit/64c34c0add) [frontend] Update eslint rules to allow non-null assertion
* [f8c3ba3266](https://github.com/cloudera/hue/commit/f8c3ba3266) [editor] Split the execute button and limit input in two components
* [d59943009a](https://github.com/cloudera/hue/commit/d59943009a) [frontend] Update SQL Scratchpad readme with details about Hue config
* [4dc127de31](https://github.com/cloudera/hue/commit/4dc127de31) [editor] Fix drag and drop from assist to the AceEditor component in editor v2
* [a130ab61fd](https://github.com/cloudera/hue/commit/a130ab61fd) Fix typo datavase to database in sql_alchemy prompt
* [66a1578ddc](https://github.com/cloudera/hue/commit/66a1578ddc) [ci] Properly reset home to checked out repo for doc linting (#1871)
* [2ffabcfdd2](https://github.com/cloudera/hue/commit/2ffabcfdd2) [blog] Removing dot in django URL post to avoid download of page
* [8d7d3fb6d7](https://github.com/cloudera/hue/commit/8d7d3fb6d7) [blog] Fix Django upgrade post page name to properly load
* [6acfb53662](https://github.com/cloudera/hue/commit/6acfb53662) [Blog] adding django_upgrade 1.11 to 3.1  blog
* [e12fad2be0](https://github.com/cloudera/hue/commit/e12fad2be0) Merge pull request #1872 from cloudera/dependabot/npm_and_yarn/elliptic-6.5.4
* [fb87c4007f](https://github.com/cloudera/hue/commit/fb87c4007f) Bump elliptic from 6.5.3 to 6.5.4
* [78bf5de278](https://github.com/cloudera/hue/commit/78bf5de278) [Django babel] shifting django-babel repo to gethue
* [861e173ef1](https://github.com/cloudera/hue/commit/861e173ef1) Consistent filtering of dir children in gist creation test
* [36261127c0](https://github.com/cloudera/hue/commit/36261127c0) HUE-9549 [SQLAlchemy] API - Support explain
* [dd74b92cd5](https://github.com/cloudera/hue/commit/dd74b92cd5) [fb] Fix style tabs in file
* [a71ad4e303](https://github.com/cloudera/hue/commit/a71ad4e303) Fix indentation.
* [04b1f3b297](https://github.com/cloudera/hue/commit/04b1f3b297) Issue 1851 - Fix auto-decompression of bz2, gz, and avro file types in Python 3 runtime environment.
* [d9993df5fa](https://github.com/cloudera/hue/commit/d9993df5fa) HUE-1851 - Detection of compressed binary file types in Python 3 runtime needs to treat data as bytes
* [5162ddf11d](https://github.com/cloudera/hue/commit/5162ddf11d) Add test for dup gist child and remove trash folder exclude iinside the dup gist dirs
* [9133f973bb](https://github.com/cloudera/hue/commit/9133f973bb) Check merge dir uuid with initial gist_dir1 and refactor dup_gist_dir merge logic
* [db48e91993](https://github.com/cloudera/hue/commit/db48e91993) Get parent_uuid with the help of uuid from _create_gist response in UT
* [db8ff63f05](https://github.com/cloudera/hue/commit/db8ff63f05) Check if parent directory id exist in UT
* [43acb88f2d](https://github.com/cloudera/hue/commit/43acb88f2d) Update multiple_gist_dirs UT and use queryset logic in MultipleObjectsReturned exception
* [750d649702](https://github.com/cloudera/hue/commit/750d649702) Create separate UT to handle dup gist directories and refactor get_gist_directory
* [bfa31c2cf1](https://github.com/cloudera/hue/commit/bfa31c2cf1) Handle multiple gist dirs by merging them into one and update test_create UT
* [17da17f439](https://github.com/cloudera/hue/commit/17da17f439) Test to repro multiple Gist directories
* [50a4c1406a](https://github.com/cloudera/hue/commit/50a4c1406a) [ci] Bump number of items of staleness checker to catch-up (#1869)
* [6f8d031851](https://github.com/cloudera/hue/commit/6f8d031851) [blog] Adding kubernetes rollout post
* [6399b63ab3](https://github.com/cloudera/hue/commit/6399b63ab3) Merge pull request #1868 from cloudera/review-romain2
* [0b132a08c5](https://github.com/cloudera/hue/commit/0b132a08c5) Merge branch 'master' into review-romain2
* [569fcc3dcd](https://github.com/cloudera/hue/commit/569fcc3dcd) GH-1660 [parser] shifting quoted_table_identifier file to calcite for using in other dialects also
* [47556abdd1](https://github.com/cloudera/hue/commit/47556abdd1) Merge branch 'master' into review-romain2
* [90a835946c](https://github.com/cloudera/hue/commit/90a835946c) [ci] More explicit message on how to keep issues not staled
* [953aaf21ce](https://github.com/cloudera/hue/commit/953aaf21ce) Merge branch 'master' into review-romain2
* [731eba4eaf](https://github.com/cloudera/hue/commit/731eba4eaf) [blog] Adding some SQL dialects as tags
* [29e27a0cce](https://github.com/cloudera/hue/commit/29e27a0cce) [blog] Hide stale news category for now
* [6153efc720](https://github.com/cloudera/hue/commit/6153efc720) [blog] Rename Development tag to Dev / API
* [b2da1ed3cf](https://github.com/cloudera/hue/commit/b2da1ed3cf) [blog] Remove Administration tag
* [d5d20dc823](https://github.com/cloudera/hue/commit/d5d20dc823) [blog] Remove Browsing tag
* [fd7327d206](https://github.com/cloudera/hue/commit/fd7327d206) [blog] Remove Querying tag
* [841b91bd02](https://github.com/cloudera/hue/commit/841b91bd02) [blog] Remove Scheduling tag
* [cb5d71a576](https://github.com/cloudera/hue/commit/cb5d71a576) [blog] Archive version 4.8 into v4
* [e043e04bc9](https://github.com/cloudera/hue/commit/e043e04bc9) [blog] Archive version 4.7 into v4
* [f79575b561](https://github.com/cloudera/hue/commit/f79575b561) [frontend] Improved vue3-webcomponent-wrapper README
* [fd817c1fbe](https://github.com/cloudera/hue/commit/fd817c1fbe) [fb] CI skip test_compare_to_xxd
* [b260a3e058](https://github.com/cloudera/hue/commit/b260a3e058) [ci] Port Python 3 CircleCi to GH action
* [b577ce5ec8](https://github.com/cloudera/hue/commit/b577ce5ec8) [ci] Adding autoclose stale PRs/Issues
* [03eafbd508](https://github.com/cloudera/hue/commit/03eafbd508) [blog] Use API as tag for Vue3 wrapper post
* [89ef9a2dd4](https://github.com/cloudera/hue/commit/89ef9a2dd4) [docs] More help on blog post writing
* [bf8d9285e2](https://github.com/cloudera/hue/commit/bf8d9285e2) [frontend] Show query results in the SQL Scratchpad example
* [eef361143c](https://github.com/cloudera/hue/commit/eef361143c) [editor] Supply the executor from the QueryEditorWebComponents module to ensure the same context is used
* [ed1f759545](https://github.com/cloudera/hue/commit/ed1f759545) [editor] Switch to a stateful SqlScratchpad component in the SQL Scratchpad example
* [a399148931](https://github.com/cloudera/hue/commit/a399148931) [editor] Support a custom SQL reference provider in sqlUtils
* [b51bd09d9d](https://github.com/cloudera/hue/commit/b51bd09d9d) [frontend] Switch to Axios in the SQL reference API service to support a custom base url in web components
* [05d4f09d85](https://github.com/cloudera/hue/commit/05d4f09d85) [frontend] Expose the hueConfig lib and enable custom base url
* [f3dafacc67](https://github.com/cloudera/hue/commit/f3dafacc67) [frontend] Move hue-base-url from attribute to a shared configure function in the SQL Scratchpad components
* [e75e018e58](https://github.com/cloudera/hue/commit/e75e018e58) [ci] Port Python 2 CircleCi to GH action
* [8489a84a0a](https://github.com/cloudera/hue/commit/8489a84a0a) [website] Remove Viz section from landing page
* [ec25a4dd12](https://github.com/cloudera/hue/commit/ec25a4dd12) [gethue] Add missing dockerignore
* [fc5537ecca](https://github.com/cloudera/hue/commit/fc5537ecca) [website] Add local dockerignore to offer automated build
* [207ac19d81](https://github.com/cloudera/hue/commit/207ac19d81) [blog] Tweaks for generating the content with git modification history
* [1700cf3807](https://github.com/cloudera/hue/commit/1700cf3807) [blog] Introducing Vue 3 & Web Components in Hue Query Editor
* [70d8aac539](https://github.com/cloudera/hue/commit/70d8aac539) [frontend] Publishing web component wrapper as an NPM package - vue3-webcomponent-wrapper
* [b9e52f2905](https://github.com/cloudera/hue/commit/b9e52f2905) [docs] Use SparkSql as dialect instead of sql (#1846)
* [1d873f98e9](https://github.com/cloudera/hue/commit/1d873f98e9) Merge pull request #1847 from cloudera/review-romain2
* [33e65018e7](https://github.com/cloudera/hue/commit/33e65018e7) Merge branch 'master' into review-romain2
* [91b29ef3aa](https://github.com/cloudera/hue/commit/91b29ef3aa) Merge pull request #1848 from cloudera/review-romain3
* [b063e9d6c0](https://github.com/cloudera/hue/commit/b063e9d6c0) [ci] Initial off setup for POC of autosquash commits
* [5eeb38e7f5](https://github.com/cloudera/hue/commit/5eeb38e7f5) [docs] Slight README simplification
* [8cb6c7bb26](https://github.com/cloudera/hue/commit/8cb6c7bb26) [libs] Adding django-cors-headers 2.5.3
* [ba8f19931c](https://github.com/cloudera/hue/commit/ba8f19931c) [core] Adding no auth flag for component testing
* [114fa7062a](https://github.com/cloudera/hue/commit/114fa7062a) Style fixes
* [e107af4b7c](https://github.com/cloudera/hue/commit/e107af4b7c) Issue 1799, Fix for xxd binary file view in File Browser, when using Python 3 runtime.
* [8ff34e5549](https://github.com/cloudera/hue/commit/8ff34e5549) Issue 1833 - Fix urllib.unquote reference which is exposed by Python 3 runtime, when extracting or compressing files in the File Browser.
* [54086cbe8c](https://github.com/cloudera/hue/commit/54086cbe8c) [frontend] Prevent rerender of react components in the SQL Scratchpad example
* [219f34199c](https://github.com/cloudera/hue/commit/219f34199c) [frontend] Add the remaining scratchpad components to the SQL Scratchpad example
* [fbde7fb931](https://github.com/cloudera/hue/commit/fbde7fb931) [editor] Emit active statement changed event from the AceEditor component
* [0e09d388e5](https://github.com/cloudera/hue/commit/0e09d388e5) [frontend] Don't emit arrays for single argument event details in the web component wrapper
* [d7489c406f](https://github.com/cloudera/hue/commit/d7489c406f) [frontend] Consolidate config related utils and types into a config folder
* [99b2b3609e](https://github.com/cloudera/hue/commit/99b2b3609e) [slack] Change qid_or_uuid -> qid and update Document2.DoesNotExist try/except
* [010d1de3d4](https://github.com/cloudera/hue/commit/010d1de3d4) [slack] Fix pylint issue
* [25028148fa](https://github.com/cloudera/hue/commit/25028148fa) [slack] Add document access decorator
* [101f7ee607](https://github.com/cloudera/hue/commit/101f7ee607) [slack] Add Document2.DoesNotExist and update UT
* [a3cd74e818](https://github.com/cloudera/hue/commit/a3cd74e818) [docs] ROADMAP update
* [df69acc2e0](https://github.com/cloudera/hue/commit/df69acc2e0) [frontend] Fix missing executor constructor in the SQL Scratchpad example project
* [b25aa132cb](https://github.com/cloudera/hue/commit/b25aa132cb) [slack] Add new line after test prep, call, and test check in UT
* [dcc7e7ce6e](https://github.com/cloudera/hue/commit/dcc7e7ce6e) [slack] Fix pylint issues
* [623d751901](https://github.com/cloudera/hue/commit/623d751901) [slack] Update link_shared UT by mocking document
* [76a8f08ab2](https://github.com/cloudera/hue/commit/76a8f08ab2) [slack] Delete doc in UT and fix pylint issues
* [41da052aff](https://github.com/cloudera/hue/commit/41da052aff) [slack] Aggregate link_unfurl logic and its UTs
* [1833c2de7f](https://github.com/cloudera/hue/commit/1833c2de7f) [slack] Refactor link-unfurl and update UTs
* [e18249376f](https://github.com/cloudera/hue/commit/e18249376f) Adding the view and database icon in the left and right assist
* [fecccf040c](https://github.com/cloudera/hue/commit/fecccf040c) [frontend] Add the query editor component to the SQL Scratchpad example
* [064499dd6f](https://github.com/cloudera/hue/commit/064499dd6f) [frontend] Add initial create-react-app SQL Scratchpad example
* [c1068c4883](https://github.com/cloudera/hue/commit/c1068c4883) [frontend] Add initial module export of libs needed for web component usage
* [ae309bfc64](https://github.com/cloudera/hue/commit/ae309bfc64) [frontend] Add type spec for executor
* [faa0cf0bb4](https://github.com/cloudera/hue/commit/faa0cf0bb4) [frontend] Allow empty constructor in d.ts files for type definitions
* [47f93be430](https://github.com/cloudera/hue/commit/47f93be430) [frontend] Generate and export one module for all the Query Editor web components
* [97b7981da7](https://github.com/cloudera/hue/commit/97b7981da7) [frontend] Update the web component wrapper to support the connectedCallback
* [d3a4589f20](https://github.com/cloudera/hue/commit/d3a4589f20) [frontend] Types change for moment & file-saver
* [85eb7d2880](https://github.com/cloudera/hue/commit/85eb7d2880) [frontend] Queries doesn't get refreshed
* [d691efcae2](https://github.com/cloudera/hue/commit/d691efcae2) [frontend] UI components not working as expected
* [39236111ca](https://github.com/cloudera/hue/commit/39236111ca) [frontend] hue-spinner was getting hidden behind other elements
* [cc25732809](https://github.com/cloudera/hue/commit/cc25732809) [core] Merge HUE-3102 to pysaml2 v4.9.0 (#1800)
* [c53d91533b](https://github.com/cloudera/hue/commit/c53d91533b) [slack] Test postMessage call with assert_call_with()
* [b9b0632ef2](https://github.com/cloudera/hue/commit/b9b0632ef2) [slack] Remove get_bot_id() and its UT along with SkipTest
* [7cef1247a7](https://github.com/cloudera/hue/commit/7cef1247a7) [slack] Remove private=True from SLACK_CLIENT_ID.
* [444593515f](https://github.com/cloudera/hue/commit/444593515f) [editor] Support variable alternatives in the VariableSubstitution component
* [1e9825e55a](https://github.com/cloudera/hue/commit/1e9825e55a) [frontend] Add a ComboBox component
* [e833d3d1c4](https://github.com/cloudera/hue/commit/e833d3d1c4) [frontend] Add a TypeaheadInput component
* [6736a92616](https://github.com/cloudera/hue/commit/6736a92616) [frontend] Fix Vue 3 conversion bug in the VariableSubstitution component
* [da212bbb78](https://github.com/cloudera/hue/commit/da212bbb78) [frontend] Extract a DropDownMenuOptions component
* [db97448cce](https://github.com/cloudera/hue/commit/db97448cce) [frontend] Improve the clickOutsideDirective structure
* [b7367d4bbb](https://github.com/cloudera/hue/commit/b7367d4bbb) [docs] localized latest blogs into Japanese (Flink and Hue 4.9 blogs)
* [aa8fc560e8](https://github.com/cloudera/hue/commit/aa8fc560e8) [editor] Create an ExecutableProgressBar Vue component
* [69a8e431c9](https://github.com/cloudera/hue/commit/69a8e431c9) [k8s] User proper variable in API deployment
* [9166e9b22c](https://github.com/cloudera/hue/commit/9166e9b22c) [k8s] Switch api endpoint to hostname instead of url prefi
* [b1962d5449](https://github.com/cloudera/hue/commit/b1962d5449) [importer] Use full abfs path in load data SQL (#1818)
* [b94b585ed8](https://github.com/cloudera/hue/commit/b94b585ed8) [k8s] Remove extra slash in the API url
* [1b834b08ca](https://github.com/cloudera/hue/commit/1b834b08ca) [ci] Test adding codecov action
* [c633b4a8e0](https://github.com/cloudera/hue/commit/c633b4a8e0) [k8s] Move api into its own section
* [43946d922c](https://github.com/cloudera/hue/commit/43946d922c) [docs] Connector design update
* [4361be4923](https://github.com/cloudera/hue/commit/4361be4923) [docs] Adding current design docs
* [cb5a3204df](https://github.com/cloudera/hue/commit/cb5a3204df) [docs] Update Django version in Developer section
* [8fc17f127b](https://github.com/cloudera/hue/commit/8fc17f127b) [k8s] Adding API service
* [56c4b8e71b](https://github.com/cloudera/hue/commit/56c4b8e71b) Fix SAML groups check (#1815)
* [5ce3936b11](https://github.com/cloudera/hue/commit/5ce3936b11) Use BytesIO for Thrift over http
* [d00f3f17f6](https://github.com/cloudera/hue/commit/d00f3f17f6) AttributeError: module 'django.db.models.fields' has no attribute 'FieldDoesNotExist'
* [1401c79599](https://github.com/cloudera/hue/commit/1401c79599) [Django 3.1] Upgraded Django to the latest version(3.1.7) till now
* [80f8cc705b](https://github.com/cloudera/hue/commit/80f8cc705b) GH-1807 [Django Upgrade] LDAP auth error: authenticate() missing 1 required positional argument: 'request'
* [d2db991f2d](https://github.com/cloudera/hue/commit/d2db991f2d) [Django 3.1] RemovedInDjango31Warning: CachedStaticFilesStorage is deprecated in favor of ManifestStaticFilesStorage
* [ef9c352344](https://github.com/cloudera/hue/commit/ef9c352344) [designs] High level scope for Hue 5
* [f8f4d095ea](https://github.com/cloudera/hue/commit/f8f4d095ea) [frontend] Tab selection not working after Vue3 migration, fixed it
* [60c1d75b0b](https://github.com/cloudera/hue/commit/60c1d75b0b) Added hue scripts to the Cloudera/hue repo (#1784)
* [d57d89e658](https://github.com/cloudera/hue/commit/d57d89e658) [ci] Skip script from ops to be pylinted
* [308a29c804](https://github.com/cloudera/hue/commit/308a29c804) fixing pylint issues
* [e4eec99378](https://github.com/cloudera/hue/commit/e4eec99378) Changes made to pass the unit tests
* [57a95fe722](https://github.com/cloudera/hue/commit/57a95fe722) fixing pylint issues
* [58a6aae72d](https://github.com/cloudera/hue/commit/58a6aae72d) Adding forked django-babel because the latest one does not support the Django3
* [29f303ba1c](https://github.com/cloudera/hue/commit/29f303ba1c) [Django 3.0] Adding compatible versions of other libraries according to Django==3.0.12
* [3cb4617e3a](https://github.com/cloudera/hue/commit/3cb4617e3a) [frontend] Fix incorrect type in the FacetSelector component
* [21d5f6811a](https://github.com/cloudera/hue/commit/21d5f6811a) [frontend] Fix reactivity with all knockout - vue web components after the Vue 3 upgrade
* [5b67352a3f](https://github.com/cloudera/hue/commit/5b67352a3f) [editor] Fix reactivity issues with the ExecutionAnalysis panel after the Vue 3 upgrade
* [429ac3ea00](https://github.com/cloudera/hue/commit/429ac3ea00) Whitelist contents of /ops directory
* [f9365e0a69](https://github.com/cloudera/hue/commit/f9365e0a69) [slack] update UTs with config flag
* [62b8586687](https://github.com/cloudera/hue/commit/62b8586687) [slack] Check api call for None type for py2
* [19c7bfac6f](https://github.com/cloudera/hue/commit/19c7bfac6f) [slack] load and instantiate sdk when config flag is enabled
* [b8b17a3efd](https://github.com/cloudera/hue/commit/b8b17a3efd) Fix pylint whitespaces
* [152c77db3e](https://github.com/cloudera/hue/commit/152c77db3e) Change f-string to .format()
* [1c937c868d](https://github.com/cloudera/hue/commit/1c937c868d) Update pylint issues, views PopupException and slack_sdk in requirements.txt
* [29c6678666](https://github.com/cloudera/hue/commit/29c6678666) Update slack_events view and add its unit test. Also update pylint issues
* [f81cf4f22d](https://github.com/cloudera/hue/commit/f81cf4f22d) Initial views unit tests
* [54c695544f](https://github.com/cloudera/hue/commit/54c695544f) Add docstring for dynamic default and slack token get() changes
* [6fecd9ec0a](https://github.com/cloudera/hue/commit/6fecd9ec0a) Add unit test for slack events
* [fde2a5fb5e](https://github.com/cloudera/hue/commit/fde2a5fb5e) [slack] Move credentials in [[slack]] ini properties
* [c514d25edc](https://github.com/cloudera/hue/commit/c514d25edc) Refactor code
* [d1e1efb9ee](https://github.com/cloudera/hue/commit/d1e1efb9ee) Set config flag to false
* [d17be81a36](https://github.com/cloudera/hue/commit/d17be81a36) Botserver update with Hue App greeting
* [a625c1c1d0](https://github.com/cloudera/hue/commit/a625c1c1d0) [frontend] Switch to the repo npm package files for the CI build
* [95cde8a3ca](https://github.com/cloudera/hue/commit/95cde8a3ca) [frontend] Drop flaky tests from ko.quickQueryContext
* [4eb0c81cba](https://github.com/cloudera/hue/commit/4eb0c81cba) [frontend] Add name attribute to all Vue components
* [741068e71a](https://github.com/cloudera/hue/commit/741068e71a) [frontend] Replace Vue 3 deprecated /deep/ with ::v-deep()
* [3654071545](https://github.com/cloudera/hue/commit/3654071545) [frontend] Various DropDown component improvements
* [b9558d41dd](https://github.com/cloudera/hue/commit/b9558d41dd) [frontend] Migrate the clickOutsideDirective to Vue 3
* [6466acbb29](https://github.com/cloudera/hue/commit/6466acbb29) modify MockRequest class (see issue #1754)
* [5eef596f26](https://github.com/cloudera/hue/commit/5eef596f26) [Mako] Opening table browser error need Mako upgradation
* [ad73a67a22](https://github.com/cloudera/hue/commit/ad73a67a22) GH-1682 [sql_alchemy] adding get_logs() function and unit test
* [71318d5c69](https://github.com/cloudera/hue/commit/71318d5c69) [ui] Vue 3 - HueLink - Removing href delete as it was causing test error
* [9e6cdb6285](https://github.com/cloudera/hue/commit/9e6cdb6285) [ui] Vue 3 - Fixed prop type validation warnings
* [44a96eddd8](https://github.com/cloudera/hue/commit/44a96eddd8) [ui] Vue 3 - UTs - Fixed ExecutableActions UTs
* [7a5642c42b](https://github.com/cloudera/hue/commit/7a5642c42b) [ui] Vue 3 - UTs - Fixed the way stubs are passed for test
* [5fa0b9bb8f](https://github.com/cloudera/hue/commit/5fa0b9bb8f) [ui] Vue 3 - UTs - Fixed DropdownMenu snapshots
* [43a07b6e64](https://github.com/cloudera/hue/commit/43a07b6e64) [ui] Vue 3 - UTs - Regenerating snapshots
* [5378bb246e](https://github.com/cloudera/hue/commit/5378bb246e) [ui] Vue 3 - Disabling JSX support in tsconfig, it was causing UT failures as vue-jest was interpreting <> based typecasting as JSX
* [0decc914c4](https://github.com/cloudera/hue/commit/0decc914c4) [ui] Vue 3 - Replacing vuejs-datepicker with vue3-datepicker
* [23d2138684](https://github.com/cloudera/hue/commit/23d2138684) [editor] Fix the editor related components
* [012c2d691f](https://github.com/cloudera/hue/commit/012c2d691f) [ui] Vue 3 - Migrated QueriesList component
* [c2e5f41033](https://github.com/cloudera/hue/commit/c2e5f41033) [ui] Vue 3 - Migrated HiveQueryPlan component
* [2480a0874e](https://github.com/cloudera/hue/commit/2480a0874e) [ui] Vue 3 - Migrated PresentationMode component
* [fe1a8f4913](https://github.com/cloudera/hue/commit/fe1a8f4913) [ui] Vue 3 - Migrated login.js
* [8b12576489](https://github.com/cloudera/hue/commit/8b12576489) [ui] Vue 3 - Migrated ExecutableActions components
* [5bd19c62d4](https://github.com/cloudera/hue/commit/5bd19c62d4) [ui] Vue 3 - Migrated EditorResizer components
* [8ab5aca654](https://github.com/cloudera/hue/commit/8ab5aca654) [ui] Vue 3 - Migrated AceEditor components
* [faa7724c3e](https://github.com/cloudera/hue/commit/faa7724c3e) [ui] Vue 3 - Migrated MatchedText components
* [36dd6d03d0](https://github.com/cloudera/hue/commit/36dd6d03d0) [ui] Vue 3 - Migrated AceAutocomplete components
* [5d8c0809fa](https://github.com/cloudera/hue/commit/5d8c0809fa) [ui] Vue 3 - Migrated ExecutionAnalysisPanel components
* [95f36412a9](https://github.com/cloudera/hue/commit/95f36412a9) [ui] Vue 3 - Migrated ResultTable components
* [39d087bc1c](https://github.com/cloudera/hue/commit/39d087bc1c) [ui] Vue 3 - Migrated VariableSubstitution components
* [a1eec246d9](https://github.com/cloudera/hue/commit/a1eec246d9) [ui] Vue 3 - Migrated Dropdown components
* [cfec5dce73](https://github.com/cloudera/hue/commit/cfec5dce73) [ui] Vue 3 - Migrated TimeAgo component
* [16389fa57b](https://github.com/cloudera/hue/commit/16389fa57b) [ui] Vue 3 - Migrated Tabs component
* [d458a8b3a9](https://github.com/cloudera/hue/commit/d458a8b3a9) [ui] Vue 3 - Migrated Tab component
* [e8f455b4ef](https://github.com/cloudera/hue/commit/e8f455b4ef) [ui] Vue 3 - Migrated StatusIndicator component
* [53780d52a7](https://github.com/cloudera/hue/commit/53780d52a7) [ui] Vue 3 - Migrated SqlText component
* [e3f9074ad4](https://github.com/cloudera/hue/commit/e3f9074ad4) [ui] Vue 3 - Migrated Spinner component
* [e5ecb031ec](https://github.com/cloudera/hue/commit/e5ecb031ec) [ui] Vue 3 - Migrated SearchInput component
* [32b181b8d6](https://github.com/cloudera/hue/commit/32b181b8d6) [ui] Vue 3 - Migrated Paginator component
* [44d17a9848](https://github.com/cloudera/hue/commit/44d17a9848) [ui] Vue 3 - Migrated Modal component
* [259f933793](https://github.com/cloudera/hue/commit/259f933793) [ui] Vue 3 - Migrated LogsPanel component
* [cac619ef02](https://github.com/cloudera/hue/commit/cac619ef02) [ui] Vue 3 - Migrated InlineAlert component
* [ae4c9ab48b](https://github.com/cloudera/hue/commit/ae4c9ab48b) [ui] Vue 3 - Migrated HumanByteSize component
* [b2cdaa01d9](https://github.com/cloudera/hue/commit/b2cdaa01d9) [ui] Vue 3 - Migrated HueTable component
* [013f64703a](https://github.com/cloudera/hue/commit/013f64703a) [ui] Vue 3 - Migrated HueLink component
* [8049ca8ec5](https://github.com/cloudera/hue/commit/8049ca8ec5) [ui] Vue 3 - Migrated HueIcon component
* [a6cf867d4d](https://github.com/cloudera/hue/commit/a6cf867d4d) [ui] Vue 3 - Migrated HueButton component
* [e2c3694e1d](https://github.com/cloudera/hue/commit/e2c3694e1d) [ui] Vue 3 - Migrated FacetSelector component
* [25b481530d](https://github.com/cloudera/hue/commit/25b481530d) [ui] Vue 3 - Migrated Duration component
* [6d9a4f9fe1](https://github.com/cloudera/hue/commit/6d9a4f9fe1) [ui] Vue 3 - Migrated DateRangePicker component
* [0c98ad3ecb](https://github.com/cloudera/hue/commit/0c98ad3ecb) [ui] Vue 3 - Migrated ColumnSelectorPanel component
* [70543c98a0](https://github.com/cloudera/hue/commit/70543c98a0) [ui] Vue 3 - Migrated Sidebar components
* [8b5b81d679](https://github.com/cloudera/hue/commit/8b5b81d679) [ui] Vue 3 - Migrated ERD components
* [24fde64280](https://github.com/cloudera/hue/commit/24fde64280) [ui] Vue 3 - Fixed lint errors in Web Component Wrapper
* [c39ed2d173](https://github.com/cloudera/hue/commit/c39ed2d173) [ui] Vue 3 - Web Component Wrapper - Remove dataVApp befoee sending it as prop
* [271cd3812e](https://github.com/cloudera/hue/commit/271cd3812e) [ui] Vue 3 - Improved Web Component Wrapper to automatically infer the events fired from emits option
* [6301488d91](https://github.com/cloudera/hue/commit/6301488d91) [ui] Vue 3 - Non string props/attributes were not passed to web components properly, fixed that
* [130e6b49e6](https://github.com/cloudera/hue/commit/130e6b49e6) [ui] Vue 3 - Fixed lint errors
* [933cede944](https://github.com/cloudera/hue/commit/933cede944) [ui] Vue 3 - Using setAttribute instead of Object.assign to set web component props
* [91864e7300](https://github.com/cloudera/hue/commit/91864e7300) [ui] Vue 3 - Foxed callHooks in wrapper utils
* [aeb4802646](https://github.com/cloudera/hue/commit/aeb4802646) [ui] Vue 3 - Preping jest for Vue3
* [bf5b7c0ed0](https://github.com/cloudera/hue/commit/bf5b7c0ed0) [ui] Vue 3 - Web Component Wrapper - Comment improvements
* [dfcfc0f245](https://github.com/cloudera/hue/commit/dfcfc0f245) [ui] Vue 3 - Web Component Wrapper - Supports reactive attributes, events & slots.
* [9979f3842e](https://github.com/cloudera/hue/commit/9979f3842e) [ui] Vue 3 - Web Component Wrapper - WIP - Loaded Vue component as web component using a Hue port of @vuejs/vue-web-component-wrapper
* [020c54671f](https://github.com/cloudera/hue/commit/020c54671f) [ui] Vue 3 - Integrating lint-vue-template using Vetur Terminal Interface
* [735af35bab](https://github.com/cloudera/hue/commit/735af35bab) [ui] Vue 3 - Improved webComponentWrap to prevent re-registering of web-components
* [754b46a853](https://github.com/cloudera/hue/commit/754b46a853) [ui] Vue 3 - Renaming webComponentWrapper to webComponentWrap & preping it for internal wrapper implementation
* [3b235199c6](https://github.com/cloudera/hue/commit/3b235199c6) [ui] Vue 3 - Fixed vue alias in webpack config
* [bc6540097a](https://github.com/cloudera/hue/commit/bc6540097a) [ui] Vue 3 - Removed vue-class-component
* [60aea1d195](https://github.com/cloudera/hue/commit/60aea1d195) [ui] Vue 3 - Upgrade eslint-plugin-vue
* [478bcd4d98](https://github.com/cloudera/hue/commit/478bcd4d98) [ui] Vue 3 dependency & build setup
* [90b5f052bb](https://github.com/cloudera/hue/commit/90b5f052bb) JB Progress bar wdg provides 2 different information which was causing issues with fetching of logs (#1783)
* [0d54e79696](https://github.com/cloudera/hue/commit/0d54e79696) [Django 3.0] provided an invalid language code in the LANGUAGES setting: 'pt_BR'
* [655870062e](https://github.com/cloudera/hue/commit/655870062e) [DJANGO 3.0] oozie.Coordinator.timezone: (fields.E009) 'max_length' is too small to fit the longest value in 'choices' (32 characters)
* [73066da001](https://github.com/cloudera/hue/commit/73066da001) [Django 3.0] ImportError: cannot import name 'six' from 'django.utils' due to line 13 in axes==4.5.4
* [ef6719b1fa](https://github.com/cloudera/hue/commit/ef6719b1fa) fixing pylint issues
* [4f5058548c](https://github.com/cloudera/hue/commit/4f5058548c) [Django 3.0] ImportError: cannot import name 'curry' from 'django.utils.functional'
* [d111ce8bb5](https://github.com/cloudera/hue/commit/d111ce8bb5) [Django 3.0] ImportError: cannot import name 'render_to_response' from 'django.shortcuts'
* [cd1e5b056c](https://github.com/cloudera/hue/commit/cd1e5b056c) [Django 3.0] TypeError: 'class Meta' got invalid attribute(s): manager_inheritance_from_future
* [be5d225afe](https://github.com/cloudera/hue/commit/be5d225afe) fixing Pylint issues
* [5b4ca5da2c](https://github.com/cloudera/hue/commit/5b4ca5da2c) [Django 3.0] ImportError: cannot import name 'python_2_unicode_compatible' from 'django.utils.encoding'
* [f9bcaec6ba](https://github.com/cloudera/hue/commit/f9bcaec6ba) [Django Upgrade] ImportError: cannot import name 'render_to_response' from 'django.shortcuts'
* [6791022cfa](https://github.com/cloudera/hue/commit/6791022cfa) [docs] Removing old JIRA references on architecture page
* [e5d524fa4d](https://github.com/cloudera/hue/commit/e5d524fa4d) [docs] Refresh API section summary
* [4fed8a0ffa](https://github.com/cloudera/hue/commit/4fed8a0ffa) [core] Setting to turn off CORS
* [57221ea75e](https://github.com/cloudera/hue/commit/57221ea75e) [docs] Fix typo
* [f91a469994](https://github.com/cloudera/hue/commit/f91a469994) [blog] Fix formatting of post on SQL variables
* [908665fe24](https://github.com/cloudera/hue/commit/908665fe24) HUE-9721 [Django Upgrade] upgrading Django 2.1.15 to 2.2.17
* [e388719cce](https://github.com/cloudera/hue/commit/e388719cce) [core] djangomako==1.2.1 require Mako 1.0.7 max
* [8da5cc8be1](https://github.com/cloudera/hue/commit/8da5cc8be1) [core] Adding djangomako==1.2.1
* [b4705f9f80](https://github.com/cloudera/hue/commit/b4705f9f80) [core] Disable django admin app
* [aaf2c52e02](https://github.com/cloudera/hue/commit/aaf2c52e02) Bump cryptography from 3.2 to 3.3.2 in /desktop/core
* [8d2c9631bc](https://github.com/cloudera/hue/commit/8d2c9631bc) Hue Filechooser in Workflow Page always loads abfs:// if configured and it wont load well (#GH-1764)
* [f032e92da9](https://github.com/cloudera/hue/commit/f032e92da9) [frontend] Go to my documents when clicking the sidebar Hue logo
* [f45e2e1703](https://github.com/cloudera/hue/commit/f45e2e1703) [frontend] Adjust sidebar z-index to prevent importer overlap
* [f36d8985b9](https://github.com/cloudera/hue/commit/f36d8985b9) [metadata] Add esc handler to cancel predictions and shift-tab to force indent
* [a34bf0af41](https://github.com/cloudera/hue/commit/a34bf0af41) [metadata] Prevent text case mismatch before the cursor for predictions
* [e6ad166212](https://github.com/cloudera/hue/commit/e6ad166212) [metadata] Use before and after cursor parameters
* [01d16152cc](https://github.com/cloudera/hue/commit/01d16152cc) [metadata] Only predict one simple statement
* [e66183c1ba](https://github.com/cloudera/hue/commit/e66183c1ba) [editor] Add variable substitution to presentation mode in editor v2
* [3ee5324dbc](https://github.com/cloudera/hue/commit/3ee5324dbc) [editor] Set the initial variables on load of the editor
* [94165f370f](https://github.com/cloudera/hue/commit/94165f370f) [editor] Prevent replacing variables with values in historic entries
* [50acac0c8c](https://github.com/cloudera/hue/commit/50acac0c8c) [core] Fix py linting issues in metadata conf
* [e519d15dca](https://github.com/cloudera/hue/commit/e519d15dca) [frontend] First version of predict typeahead in editor v2
* [e2842ad006](https://github.com/cloudera/hue/commit/e2842ad006) [frontend] Add a feature flag for predict typeahead
* [44b40e51b1](https://github.com/cloudera/hue/commit/44b40e51b1) [editor] Hidding query compatibility and upload actions
* [19940f2a0b](https://github.com/cloudera/hue/commit/19940f2a0b) [frontend] Make Un-expand menu full width clickable
* [dd3291fca3](https://github.com/cloudera/hue/commit/dd3291fca3) [flink] adding Flink to right assist Function panel (#1751)
* [941ae313fa](https://github.com/cloudera/hue/commit/941ae313fa) [editor] Type is now according to I18n
* [b7a2e56595](https://github.com/cloudera/hue/commit/b7a2e56595) [editor] Add "Type" text in tooltip
* [31970c9ef3](https://github.com/cloudera/hue/commit/31970c9ef3) [libs] Upgrade pytz==2021.1
* [a6ce56e0b9](https://github.com/cloudera/hue/commit/a6ce56e0b9) [editor] Add variable substitution in editor v2
* [a54b92c77d](https://github.com/cloudera/hue/commit/a54b92c77d) [connector] Adding clickhouse SQL dialect
* [952812e2c5](https://github.com/cloudera/hue/commit/952812e2c5) [docs] Adding why an extra space post cursor note
* [c9674af558](https://github.com/cloudera/hue/commit/c9674af558) [connector] Adding SqlAlchemy interface option for impala
* [5cd2d3183a](https://github.com/cloudera/hue/commit/5cd2d3183a) [phoenix] Avoid error when opening up Editor after 1 hour
* [68e56fff9a](https://github.com/cloudera/hue/commit/68e56fff9a) [slack] Change default config to false
* [01e1dd31ca](https://github.com/cloudera/hue/commit/01e1dd31ca) Update hue.ini and simpler naming/messages
* [894b421e9e](https://github.com/cloudera/hue/commit/894b421e9e) [editor] Show external statement should default to false
* [5cacf8965f](https://github.com/cloudera/hue/commit/5cacf8965f) Add @login_notrequired decorator
* [d7e779be75](https://github.com/cloudera/hue/commit/d7e779be75) Add config flag to globally turn on/off the Slack Integration
* [fc00e1fcdd](https://github.com/cloudera/hue/commit/fc00e1fcdd) Add Apache 2 license header
* [1f267f4c1e](https://github.com/cloudera/hue/commit/1f267f4c1e) Fix pylint issues
* [c2b9e79a2d](https://github.com/cloudera/hue/commit/c2b9e79a2d) Huebot django app integrate with Hue Server
* [3eed0e751c](https://github.com/cloudera/hue/commit/3eed0e751c) [ui] Feedback on login when pressing <enter>
* [32f59cf37e](https://github.com/cloudera/hue/commit/32f59cf37e) [hive] Removing extra transactional table properties in samples
* [a34cad5ed6](https://github.com/cloudera/hue/commit/a34cad5ed6) [analyser] Fixing coding nits on parsing
* [82d46e2eb0](https://github.com/cloudera/hue/commit/82d46e2eb0) [editor] Rename Add filter assist action to Fix me
* [93252bacf2](https://github.com/cloudera/hue/commit/93252bacf2) [editor] Add checkSelectStar to assist
* [d6bd874626](https://github.com/cloudera/hue/commit/d6bd874626) [analyser] Add checkSelectStar util
* [0168055627](https://github.com/cloudera/hue/commit/0168055627) [editor] Auto propose to add a LIMIT
* [44155e8cc3](https://github.com/cloudera/hue/commit/44155e8cc3) [analyser] Add tests to SqlAnalyzer abd checkMissingLimit()
* [9e829bd35c](https://github.com/cloudera/hue/commit/9e829bd35c) [analyser] Add checkMissingLimit() in SQL statement
* [55afcf46ee](https://github.com/cloudera/hue/commit/55afcf46ee) [frontend] Close the sidebar tooltip menu after click
* [6a39695ea2](https://github.com/cloudera/hue/commit/6a39695ea2) [frontend] Switch to accordion menu for the user and help menu options
* [f45fa3e9d6](https://github.com/cloudera/hue/commit/f45fa3e9d6) fix progress bar and logs icon in oozie wf when run
* [a0bd2fdfdd](https://github.com/cloudera/hue/commit/a0bd2fdfdd) [frontend] Include the package-lock.json file when building
* [e3dd9c67a8](https://github.com/cloudera/hue/commit/e3dd9c67a8) added type = 'view' for views
* [75fde49ab0](https://github.com/cloudera/hue/commit/75fde49ab0) HUE-9728 [sqlAlchemy] Add views to get_tables API
* [d8fae8057e](https://github.com/cloudera/hue/commit/d8fae8057e) Updated the RN link to point to 4.9.0 instead of 4.8.0
* [bd8ac6980a](https://github.com/cloudera/hue/commit/bd8ac6980a) [docs] Update release instructions to use 4.9
* [545bb0c9c8](https://github.com/cloudera/hue/commit/545bb0c9c8) [release] Perform 4.9 release

### Contributors

This Hue release is made possible thanks to the contribution from:

* 10sr
* Aaron Newton
* Aaron Peddle
* Aaron T. Myers
* abec
* Abraham Elmahrek
* Aditya Acharya
* Adrian Yavorskyy
* agl29
* aig
* airokey
* Ajay Jadhav
* Akhil Naik
* Akhil S Naik
* Alex Breshears
* Alex Newman
* Alex (posi) Newman
* alheio
* Aliaksei
* alphaskade
* Ambreen Kazi
* Amit Kabra
* Andrei Savu
* Andrew Bayer
* Andrew Yao
* Andy Braslavskiy
* Ann McCown
* antbell
* Antonio Bellezza
* arahuja
* Ashu Pachauri
* Asnaik HWX
* Atupal
* Avindra Goolcharan
* ayush.goyal
* Ayush Goyal
* batou9150
* bcwalrus
* bc Wong
* Ben Bishop
* Ben Gooley
* Ben White
* Bhargava Kalathuru
* BirdZhang
* Bruce Mitchener
* Bruno Mahé
* bschell
* bwang
* cconner
* Chris Conner
* Chris Stephens
* Christopher Conner
* Christopher McConnell
* Christopherwq Conner
* cmconner156
* Craig Minihan
* cwalet
* Daehan Kim
* dbeech
* denniszag
* dependabot[bot]
* Derek Chen-Becker
* Diego Sevilla Ruiz
* Dominik Gehl
* Duncan Buck
* e11it
* Eli Collins
* emmanuel
* Emmanuel Bessah
* Enrico Berti
* Eric Chen
* Erick Tryzelaar
* Ewan Higgs
* fatherfox
* Gabriel Machado
* ganeshk
* gdgt
* Gilad Wolff
* gmsantos
* gnieto
* grundprinzip
* Grzegorz Kokosiński
* Guido Serra
* happywind
* Harsh
* Harshg999
* Harsh Gupta
* Harsh J
* Hector Acosta
* Henry Robinson
* Hoai-Thu Vuong
* hueadmin
* Igor Wiedler
* ihacku
* Ilkka Turunen
* Istvan
* Ivan Dzikovsky
* Ivan Orlov
* Jack McCracken
* Jaguar Xiong
* Jakub Kukul
* Jamie Davenport
* Jarcek
* Jason Killian
* jdesjean
* Jean-Francois Desjeans Gauthier
* jeff.melching
* Jenny Kim
* jheyming
* jkm
* Joe Crobak
* Joey Echeverria
* Johan Ahlen
* Johan Åhlén
* Jon Natkins
* Jordan Moore
* Josh Walters
* Justin Bradfield
* Karissa McKelvey
* Kevin Risden
* Kevin Wang
* Khwunchai Jaengsawang
* Kostas Sakellis
* krish
* Lars Francke
* Li Jiahong
* linchan-ms
* Linden Hillenbrand
* linwukang
* Louis de Charsonville
* Luca
* Luca Natali
* Luca Toscano
* Luke Carmichael
* lvziling
* Mahesh Balakrishnan
* maiha
* Marcus McLaughlin
* Mariusz Strzelecki
* Martin Traverso
* Mathias Rangel Wulff
* Matías Javier Rossi
* Maulik Shah
* Max T
* Michael Prim
* Michal Ferlinski
* Michalis Kongtongk
* MoA
* Mobin Ranjbar
* motta
* mrmrs
* Mykhailo Kysliuk
* Naoki Takezoe
* Nicolas Fouché
* Nicolas Landier
* NikolayZhebet
* Nils Braun
* Olaf Flebbe
* Oli Steadman
* OOp001
* Oren Mazor
* oxpa
* Pala M Muthaia Chettiar
* Patricia Sz
* Patrick Carlson
* Patrycja Szabłowska
* pat white
* Paul Battaglia
* Paul McCaughtry
* peddle
* penggongkui
* Peter Slawski
* Philip Zeyliger
* Piotr Ackermann
* pkuwm
* Prachi Poddar
* Prakash Ranade
* Prasad Mujumdar
* Priyanka Chheda
* Qi Xiao
* Raghunandana S K
* rainysia
* raphi
* rdeva
* Reinaldo de Souza Jr
* Rentao Wu
* Renxia Wang
* Rick Bernotas
* Ricky Saltzer
* Robert Wipfel
* robrotheram
* Romain
* Romain Rigaux
* Roman Shaposhnik
* Roohi
* Roohi Syeda
* rpoluri
* Rui Pereira
* sachinunravel
* Sai Chirravuri
* sandeepreddy3647
* Santiago Ciciliani
* sbaudoin
* Scott Kahler
* Sean Mackrory
* Shahab Tajik
* Shawarma
* Shawn Van Ittersum
* Shin So
* shobull
* Shrijeet
* Shrijeet Paliwal
* Shuo Diao
* Siddhartha Sahu
* Simon Beale
* Simon Whittaker
* sky4star
* skyyws
* spaztic1215
* sreenaths
* Sreenath Somarajapuram
* Stefano Palazzo
* Stephanie Bodoff
* stephbat
* Suhas Satish
* Sungpeo Kook
* TAKLON STEPHEN WU
* TAK LON WU
* Tamas Sule
* Tatsuo Kawasaki
* Taylor Ainsworth
* Thai Bui
* theyaa
* thinker0
* Thomas Aylott
* Thomas Poepping
* Thomas Tauber-Marshall
* Tianjin Gu
* tjphilpot
* todaychi
* Todd Lipcon
* Tomas Coufal
* Tom Mulder
* travisle22
* Vadim Markovtsev
* van Orlov
* vinithra
* voyageth
* vybs
* Wang, Xiaozhe
* weixia
* Weixia
* Weixia Xu
* William Bourque
* wilson
* Word
* Xavier Morera
* Xhxiong
* Xiao Kang
* Xingang Zhang
* xq262144
* Ying Chen
* Yixiao Lin
* ymping
* Yoer
* Yuanhao
* Yuanhao Lu
* Yubi Lee
* Yuriy Hupalo
* ywheel
* z00484332
* Zachary York
* Zach York
* Zhang Bo
* zhang-jc
* Zhang Ruiqiang
* zhengkai
* Zhihai Xu
* z-york
* 小龙哥
* 王添
* 白菜
* 鸿斌
