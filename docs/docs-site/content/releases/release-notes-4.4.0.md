---
title: "4.4.0"
date: 2019-03-13T18:28:08-07:00
draft: false
weight: -4040
tags: ['skipIndexing']
---

### Hue v4.4.0, released March 28th 2019


Hue, http://gethue.com, is Hue is an open source SQL Cloud Assistant for developing and accessing SQL/Data Apps.

Its main features:

* Editors to query with SQL any database and submit jobs
* Dashboards to dynamically interact and visualize data
* Scheduler of jobs and workflows
* Browsers for data and a Data Catalog

Read the complete list of improvements on [Hue 4.4 is out!](http://gethue.com/hue-4-4-and-its-improvements-are-out/).


Summary
-------
The focus of this release was to improve the self service SQL troubleshooting and stability.


Notable Changes
---------------

* Easier Self Service Query Troubleshooting
  * Prettier display of the SQL Query Profile
* Better compatibility with Hive in HDP
  * Apache Hive has typically been very innovative in the Hortonworks distribution. Support for Tez and Hive LLAP was bumped.
  * The jobs will show up in Job Browser
  * The query ID is printed
  * The progress is displayed
*  Misc Improvements
  * More than 80 bugs were fixed to improve the supportability and stability. The full list is in the release notes but here are the top ones:
  * [HUE-7474](https://issues.cloudera.org/browse/HUE-7474) [core] Add ability to enable/disable Hue data/file "download" options globally
  * [HUE-7128](https://issues.cloudera.org/browse/HUE-7128) [core] Apply config ENABLE_DOWNLOAD to search dashboard
  * [HUE-8680](https://issues.cloudera.org/browse/HUE-8680) [core] Fill in Impalad WEBUI username passwords automatically
  * [HUE-8585](https://issues.cloudera.org/browse/HUE-8585) [useradmin] Bubbling up errors for Add Sync Ldap Users
  * [HUE-8690](https://issues.cloudera.org/browse/HUE-8690) [backend] Fix Hue allows unsigned SAML assertions
  * [HUE-8140](https://issues.cloudera.org/browse/HUE-8140) [editor] Improve multi-statement execution
  * [HUE-8662](https://issues.cloudera.org/browse/HUE-8662) [core] Fix missing static URLs
* The [Hue Docker image](https://github.com/cloudera/hue/tree/master/tools/docker) was simplified
* [Upstream](http://cloudera.github.io/hue/latest/) documentations has a better table of contents, restyling, update of old instructions... Reporting issues or sending a suggestion is one click away via GitHub, so feel free to send some pull requests!


Compatibility
-------------

Runs on CentOS versions 6.8+, Red Hat Enterprise Linux (RHEL 6, 7), and Ubuntu 16.04 and 18.04.

Tested with CDH6. Specifically:

- Hadoop 3.0
- Hive 2.1 / 3.0
- Oozie 5.0
- HBase 2.0
- Pig 0.17
- Impala 3.0
- Solr 7.4
- Spark 2.2

Other versions should work, but not tested.


Supported Browsers:

Hue works with the two most recent versions of the following browsers.

* Chrome
* Firefox LTS
* Safari (not supported on Windows)
* Internet Explorer / Edge



Runs with Python 2.7+

Note: CentOS 6 and RHEL 6 require EPEL python 2.7 package.


List of 450+ Commits
---------------------
* 3d2c2a4 [HUE-8769](https://issues.cloudera.org/browse/HUE-8769) [core] Perform 4.4 release
* 64c5ea1 [HUE-8740](https://issues.cloudera.org/browse/HUE-8740) [docs] Refactor some of the old dev content
* 43a1329 [HUE-8770](https://issues.cloudera.org/browse/HUE-8770) [docs] Document about Livy CSRF option
* 2222250 [HUE-8772](https://issues.cloudera.org/browse/HUE-8772) [core] Add custom commit on top of Django upgrade fixing 'user is missing in mako context'
* e9a6a03 [HUE-8772](https://issues.cloudera.org/browse/HUE-8772) [core] Upgrade Django from 1.11 to 1.11.20
* b14016e [HUE-8770](https://issues.cloudera.org/browse/HUE-8770) [spark] Send proper header to Livy when CSRF protection is enabled (#823)
* 9d68e94 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Better nodejs installation instructions of nodejs for Ubuntu
* 664992c [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Add dev steps for pycharm / eclipse.
* bd7ae37 [HUE-6238](https://issues.cloudera.org/browse/HUE-6238) [doc] Update Hue admin config doc
* 1100dcf [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fix for removed ko_components.mako
* 5d0b85c [HUE-8760](https://issues.cloudera.org/browse/HUE-8760) [core] Fix TestStrictRedirection.test_redirection_blocked
* bfeb97b [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Add the list of authentication backends
* 6b8a6f3 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Add missing proxy user information
* e353ff5 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Add a reference to Gunicorn
* 5d97755 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Starting to update the Editor end user section
* 792b687 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Refactoring of the developer section
* 4814746 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Another pass of clean-up on the user section
* aa350b8 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Adding source version control documentation
* f2501b7 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Refactor and refresh SQL connectors
* 945098b [HUE-8759](https://issues.cloudera.org/browse/HUE-8759) [importer] Fix import to index, importing to hive instead.
* b51ecc0 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Add resizing for profile details.
* 1ac4457 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Fix profile ellipsis for Firefox
* 3e6ed07 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Improve scroll to top behaviour in docs
* f0d5737 [HUE-8763](https://issues.cloudera.org/browse/HUE-8763) [autocomplete] Add definitions to the autocomplete parse results
* e434298 [HUE-8762](https://issues.cloudera.org/browse/HUE-8762) [frontend] Stabilize parser generation
* 9e05a0a [HUE-8691](https://issues.cloudera.org/browse/HUE-8691) [useradmin] Fix group sync fail to import member
* ccc31bc [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Add Druid to the list of connectors
* 17b3889 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [docs] Pass updating the content and reorganazing the configuration toc
* 55b06f3 [HUE-8756](https://issues.cloudera.org/browse/HUE-8756) [doc] Fix a series of broken links
* 14cb3e9 [HUE-8760](https://issues.cloudera.org/browse/HUE-8760): [core] Error with redirect to page
* be6b453 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Tone down the logo and left and right navigation chevrons
* f19efdb [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add scroll to top button
* 30a6d44 [HUE-8754](https://issues.cloudera.org/browse/HUE-8754) [editor] Fix various js exceptions from the charts when switching between chart types
* fd63d83 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move reminding chart components into webpack bundles
* 5f9ba5d [HUE-8753](https://issues.cloudera.org/browse/HUE-8753) [frontend] Fix about page step 2 js exception
* be77ac4 [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [catalog] Rename get_navigator_url() to get_catalog_url()
* 869d366 [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [catalog] Remove hardcoded Navigator from the messages
* 932f8c8 [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [catalog] Rename has_navigator() to has_catalog()
* 2acd475 [HUE-8749](https://issues.cloudera.org/browse/HUE-8749) [catalog] Rename has_file_search method to be generic
* cb51e9b [HUE-8775](https://issues.cloudera.org/browse/HUE-8775): [editor] Boolean variable substitution fails with coercion error
* 8a1469e [HUE-8752](https://issues.cloudera.org/browse/HUE-8752): [editor] Variable substitution does not use the default value when empty (#814)
* a236969 [HUE-8717](https://issues.cloudera.org/browse/HUE-8717) [oozie] Fix Sqoop1 editor fail to execute
* b50914b [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [editor] Fix timing issue when loading the editor
* 7cc87bc [HUE-8751](https://issues.cloudera.org/browse/HUE-8751) [editor] Prevent showing all editor types in the header briefly on load
* 5add249 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fetch topo json on demand for map charts
* f9fb4f5 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move datamap topo graphs into webpack
* 0d724dc [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] How to document how to access the shell and count documents
* 268622c [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Do not leave install top page empty
* 86064ae [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Clean-up the Administration hierarchy
* 8c5e683 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Split Hue administration and configuration in two
* 6025056 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Instruction on how to run the doc site in dev mode
* 2c5878a [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Adding Hue favicon
* 657301f [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Use correct path for the search
* b4d5219 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Move build instruction to the top in the development section
* ce18113 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add correct link for the images
* 66fb38a [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fix for removed ko_components.mako
* 35277c0 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add Apache Ranger, Atlas and Knox integrations to the roadmap
* 2525d3b [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add GA to doc footer
* 2342db3 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Tweak menu footer to be lighter for now
* 165f0a8 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add back the search and a way to skip release notes from indexing
* f45df0b [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add instruction on how to build the new website
* 2dccc0e [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] New documentation website
* 5395b88 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add links to jiras to the roadmap page
* acd1027 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move all the common ko components into webpack modules
* dbaf300 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Introduce an I18n global js function
* 1606475 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move D3 and chart bindings into webpack
* cda0268 [HUE-8746](https://issues.cloudera.org/browse/HUE-8746) [pig] Add hcat support in the Pig Editor in Hue
* ad3c4c4 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Fix typo in roadmap about NGINX
* e3d4132 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add a few more top jiras to the roadmap
* e9ebc51 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Clean-up of the end user guide
* 7ab3fde [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] TOC re-organization of the SDK
* d48508e [HUE-8742](https://issues.cloudera.org/browse/HUE-8742) [catalog] Fix navigation on table create.
* d0a3897 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add info about SparkSQL Livy connector
* abec26e [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add a high level roadmap
* 97b23f3 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] List more supported DBs
* 2feb553 [HUE-8728](https://issues.cloudera.org/browse/HUE-8728) [jb] Fix optimzer_api test.
* c41b8ec [HUE-8728](https://issues.cloudera.org/browse/HUE-8728) [jb] Fix download test.
* af7338c [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Add contributing page to repo
* 6b09493 [HUE-8741](https://issues.cloudera.org/browse/HUE-8741) [doc] Refresh Admin documentation content
* 368c2dd [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [doc] Fix link to Docker page
* 503132c [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [doc] Improve syling of js parser command instructions
* cdab63f [HUE-8735](https://issues.cloudera.org/browse/HUE-8735) [jb] Handle null bytes in query id
* 5cc202b [HUE-7621](https://issues.cloudera.org/browse/HUE-7621) [sqlalchemy] Adding connector example in the inis
* 8a9a0f9 [HUE-7621](https://issues.cloudera.org/browse/HUE-7621) [sqlalchemy] Avoid list index out of range on empty result
* f5f58e5 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Add back codegen to profile.
* 7aa2c46 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Fix Kudu icon in profile
* bb8b15f [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [doc] Improve instructions on how to re-generate the js SQL parser
* e075de2 [HUE-8732](https://issues.cloudera.org/browse/HUE-8732) [jb] Convert FINISHED state to SUCCEEDED in API comment
* 9fd8b2d [HUE-8732](https://issues.cloudera.org/browse/HUE-8732) [jb] Force Knockout to handle the update of rerunModalContent before trying to modify its DOM
* b7d188a [HUE-8732](https://issues.cloudera.org/browse/HUE-8732) [jb] Fix rerun_coord_popup for normal JB mode and mini JB mode
* ec488cc [HUE-8732](https://issues.cloudera.org/browse/HUE-8732) [jb] Rerun button for scheduler tasks is not working
* e12e9fe [HUE-8732](https://issues.cloudera.org/browse/HUE-8732) [jb] 'Select all' button is not working for sheduler tasks
* ce523a6 [HUE-8730](https://issues.cloudera.org/browse/HUE-8730) [docker] Workaround the webpack generation
* 02791a2 [HUE-8730](https://issues.cloudera.org/browse/HUE-8730) [docker] Hook-in webpack bundle generation into the image
* b4e8d56 [HUE-8730](https://issues.cloudera.org/browse/HUE-8730) [docker] Add npm packages to compile the js properly
* c7f0acd [HUE-8734](https://issues.cloudera.org/browse/HUE-8734) [editor] Fix zero width column filter in the results
* 279be3f [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [editor] Split notebook.ko.js and move js code blocks from editor_components into webpack
* 66f4daf [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [editor] Move additional editor dependencies into webpack and add a runtime bundle
* 251a654 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Speed up bundle generation by separating workers and login generation
* 1da717c [HUE-8729](https://issues.cloudera.org/browse/HUE-8729) [oozie] Add property archive to Spark Action
* 89589f7 [HUE-8730](https://issues.cloudera.org/browse/HUE-8730) [docker] Refactor and organize the image building
* 4cb5abd [HUE-8728](https://issues.cloudera.org/browse/HUE-8728) [jb] Redirect client for file download.
* 5321892 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fix sprintf in ko
* 6206c4d [HUE-8731](https://issues.cloudera.org/browse/HUE-8731) [oozie] Can not save coordinator from examples (#807)
* ce743a0 [HUE-8608](https://issues.cloudera.org/browse/HUE-8608) [useradmin] Add config check on num of QueryHistory, SavedQuery, and Job
* 8fac8c2 [HUE-8298](https://issues.cloudera.org/browse/HUE-8298) [core] Update configuration flag for Cloudera Manager API URL
* 0d0a776 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fix less generation and add style linter
* 4658b81 [HUE-8727](https://issues.cloudera.org/browse/HUE-8727) [frontend] Prevent Chrome from autofilling user name in various input elements
* a88901f [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move the reminding autocompleter logic into the webpack bundle
* 7a14481 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move all the jasmine tests into the new js structure
* 1b99978 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Add webpack-stats.json to gitignore
* 3544332 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move all the remaining parsers into webpack bundles
* fbd3b2c [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [notebook] Support any type of computes in multi cluster
* c0f91d9 [HUE-8725](https://issues.cloudera.org/browse/HUE-8725) [core] Adding python-crontab lib for Celery Beat
* aeb9c8a [HUE-8725](https://issues.cloudera.org/browse/HUE-8725) [core] Adding django-timezone-field lib for Celery Beat
* 9b9caec [HUE-8725](https://issues.cloudera.org/browse/HUE-8725) [core] Add configuration for Celery Beat
* 4827624 [HUE-8725](https://issues.cloudera.org/browse/HUE-8725) [core] Adding Django Celery Beat lib
* 634ddbb [HUE-8259](https://issues.cloudera.org/browse/HUE-8259) [core] Integrate task server in the configuration
* eaa8c1c [HUE-8259](https://issues.cloudera.org/browse/HUE-8259) [core] Integrating Celery
* 92cf5a5 [HUE-8259](https://issues.cloudera.org/browse/HUE-8259) [core] Adding python packages dependencies of Task Service
* dcca94e [HUE-8724](https://issues.cloudera.org/browse/HUE-8724) [k8s] Provide how to run Hue server in Kubernetes
* f8631e1 [HUE-8723](https://issues.cloudera.org/browse/HUE-8723) [editor] Remove old autocompleter and use the new one for all SQL editors
* cfff677 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move the hue.mako view models into webpack
* 3a82479 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Add "npm install" to make apps and update the sdk docs
* f779446 [HUE-8721](https://issues.cloudera.org/browse/HUE-8721) [frontend] Remove the is_hue_4 and disable_hue_3 configuration flags
* a3f50f7 [HUE-8720](https://issues.cloudera.org/browse/HUE-8720) [importer] Fix importer with custom separator
* d1c8af9 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Fix profile exchange time.
* a2906a1 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Display IO + CPU time on profile node.
* 51956bd [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Hide profile health risks behind flag.
* b66e735 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Add generated js bundles to .gitignore
* 8542cef [HUE-8713](https://issues.cloudera.org/browse/HUE-8713) [jb] Fetch log name list dynamically for Yarn jobs.
* d0969cd [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Add initial notebook bundle
* 2d7d2cc [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Add custom js bundle for the login page
* 2de3fa5 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Add automatic bundle cleaning when running "npm run dev"
* c40271f [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Update sdk docs and licence file for npm and webpack bundling
* 6ac54c5 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Drop the use of expose-loader
* 5ed04bd [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move additional third party dependencies to the webpack bundle
* 282d0c3 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Migrate additional jquery plugins to webpack
* ea80b4d [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Modularize all custom ko bindings
* d60d130 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Modularize the SQL syntax parser and add a dedicated web worker bundle
* cee13ff [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fix linting issues
* 9449dc6 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Move the assist models into the wepback bundle
* 8bf78c9 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Modularize the context catalog
* 827da5e [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Modularize the data catalog
* 361770c [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Modularize and bundle the ApiHelper and related util classes
* 50b77d8 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Add eslint
* 9b5cfc5 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Prevent initially garbled page when switching apps
* dead422 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fix jquery upgrade issue with draggable
* d92d831 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Migrate various jquery plugins to webpack
* 6b2d0ae [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Bundle additional modules
* 0ef3c51 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Upgrade jQuery to 3.3.1
* 339c922 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Refactor and modularize hue.utils.js
* 5004838 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Fix issue with page.js routing
* 634bc81 [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Bump versions for webpack and babel to the latest
* 4b534cb [HUE-8687](https://issues.cloudera.org/browse/HUE-8687) [frontend] Add webpack for js modularity and bundling
* 1e85de1 [HUE-8718](https://issues.cloudera.org/browse/HUE-8718) [doc] Add info on how to build the Ace editor
* 045be23 [HUE-8713](https://issues.cloudera.org/browse/HUE-8713) [assist] Add missing column in TEZ.
* 9ad1b33 [HUE-8713](https://issues.cloudera.org/browse/HUE-8713) [notebook] Add progress updates for TEZ jobs.
* 403c6f8 [HUE-8713](https://issues.cloudera.org/browse/HUE-8713) [jb] Support TEZ jobs.
* 318fb85 [HUE-8708](https://issues.cloudera.org/browse/HUE-8708) [jb] Less aggresive job fetching.
* 7969581 [HUE-8714](https://issues.cloudera.org/browse/HUE-8714) [core] force flag use_new_editor is true all the time
* af64f77 [HUE-8717](https://issues.cloudera.org/browse/HUE-8717) [oozie] Fix Oozie action Sqoop job failed to execute
* cd2701d [HUE-8716](https://issues.cloudera.org/browse/HUE-8716) [core] Default value of ssl_cipher_list in hue.ini does not match with real value in desktop/conf.py (#805)
* c78a800 PR795 [editor] Add a ClickHouse connector using jdbc (#795)
* c169794 [HUE-8693](https://issues.cloudera.org/browse/HUE-8693) [useradmin] Fix Security app only display 100 user in impersonate list
* f18726d [HUE-7258](https://issues.cloudera.org/browse/HUE-7258) [jb] Get conf via CM if Spnego enabled on Spark history server
* afa1f28 [HUE-8709](https://issues.cloudera.org/browse/HUE-8709) [useradmin] Fix black transparent screen remains after confirmation modal is hidden
* 9e50d5b [HUE-8692](https://issues.cloudera.org/browse/HUE-8692) [useradmin] Fix group sync stops when a group member is not found
* d4276fe [HUE-8707](https://issues.cloudera.org/browse/HUE-8707) [doc] Add info for building the sql autocomplete
* 197b12b [HUE-8706](https://issues.cloudera.org/browse/HUE-8706) [frontend] Add Dashboard to DW left menu
* b52380c [HUE-8707](https://issues.cloudera.org/browse/HUE-8707) [doc] Add a footer with link to the page source on github
* 3ea64aa [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Update generated thrift for profile.
* a16e201 [HUE-8691](https://issues.cloudera.org/browse/HUE-8691) [useradmin] Fix importing users failed silently if objectClass posixGroup exists in group
* b1406a0 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Fix profile expand doesn't respond to click.
* 074c509 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Improve profile performance.
* 8d23228 PR798 [oozie] Fix workflow widget id colliding bug (#798)
* e509718 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Fix profile unit test.
* 9c8c32c [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Fixed profile with missing stats.
* 2c5dcb5 PR800 [notebook] Add JDBC Assist for Presto (#800)
* 8f48ba6 [HUE-8705](https://issues.cloudera.org/browse/HUE-8705) [oozie] Fix hiding chooseWorkflowDemiModal clickable in coordinator
* 60d6518 [HUE-8690](https://issues.cloudera.org/browse/HUE-8690) [core] Add allows unsigned SAML assertions properties to inis
* 804d095 [HUE-8706](https://issues.cloudera.org/browse/HUE-8706) [frontend] Change the top nav logo in DW mode
* ab56d8d [HUE-8706](https://issues.cloudera.org/browse/HUE-8706) [frontend] Change the left nav design in DW mode
* 9d8c013 [HUE-8584](https://issues.cloudera.org/browse/HUE-8584) [useradmin] Bubbling up errors for Add Sync Ldap Group
* 96fbe70 [HUE-8704](https://issues.cloudera.org/browse/HUE-8704) [jb] Add health risks to profile.
* d5d479c [HUE-8585](https://issues.cloudera.org/browse/HUE-8585) [useradmin] Bubbling up errors for Add Sync Ldap Users
* 8b99e35 [HUE-8703](https://issues.cloudera.org/browse/HUE-8703) [editor] Clear the URL parameters when creating a new editor
* 0d755eb [HUE-8140](https://issues.cloudera.org/browse/HUE-8140) [editor] Additional improvements to multi statement execution
* 66b8645 [HUE-8701](https://issues.cloudera.org/browse/HUE-8701) [tb] Prevent eternal spinner when there are no namespaces
* b17973e [HUE-8701](https://issues.cloudera.org/browse/HUE-8701) [editor] Prevent js exception in the context selector when no namespaces exist
* 2307f53 [HUE-8700](https://issues.cloudera.org/browse/HUE-8700) [editor] Highlight empty variables.
* 60dc8c9 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Added overview details on profile.
* 0fd4d3c [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Update metrics on profile.
* 5f3170e [HUE-8699](https://issues.cloudera.org/browse/HUE-8699) [jb] Disable recurrent Yarn job browser status check for now in k8s mode
* 2dcf14e [HUE-8699](https://issues.cloudera.org/browse/HUE-8699) [core] Adding skeleton of Hue on Kubernetes
* 712372e [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Added IO to cpu time in profile.
* 899148b [HUE-8690](https://issues.cloudera.org/browse/HUE-8690) [backend] Fix Hue allows unsigned SAML assertions
* 73764c9 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Fetch jobs only if interface is defined.
* 6754e44 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Added simplified timeline to profile.
* 716ef9f [HUE-8695](https://issues.cloudera.org/browse/HUE-8695) [importer] Do not show the command but submit when clicking on submit button
* e066d05 [HUE-8694](https://issues.cloudera.org/browse/HUE-8694) [frontend] Fix scroll in the database dropdown
* c05be9e [HUE-8140](https://issues.cloudera.org/browse/HUE-8140) [editor] Improve multi-statement execution
* e211a8a [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Remove unused C3 lib
* 1b77b93 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Add network time to profile.
* e66d5bc [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Add filters and groupby conditions to profile
* 48a1b5b [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Add more metrics to query plan.
* 5146aec [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Add more metrics to query plan.
* cacf60f [HUE-8688](https://issues.cloudera.org/browse/HUE-8688) [core] update Chinese language code to enable Hue Chinese localization
* 5e78413 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Fix timeline for multicluster.
* b0bd9f7 [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [impala] Fix hostname in remote cluster profile fetching
* f3d4ac7 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Add timeline to profile.
* dadf7b5 [HUE-8680](https://issues.cloudera.org/browse/HUE-8680) [core] Fill in Impalad WEBUI username passwords automatically if needed
* 4082346 [HUE-8682](https://issues.cloudera.org/browse/HUE-8682) [backend] Update third party README
* 72fbdb0 [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [jb] Fix query interface single cluster after query
* 56b665d [HUE-7258](https://issues.cloudera.org/browse/HUE-7258) [jb] Add config check for Spark history server URL
* f67abf3 [HUE-8577](https://issues.cloudera.org/browse/HUE-8577) [editor] Fix internal topic links in the language reference
* 78b9c97 [HUE-8577](https://issues.cloudera.org/browse/HUE-8577) [editor] Sync the built in UDF library with the Impala language reference
* 30ba0ce [HUE-8577](https://issues.cloudera.org/browse/HUE-8577) [editor] Preserve formatting in language reference code blocks
* 46ef524 [HUE-8577](https://issues.cloudera.org/browse/HUE-8577) [editor] Update the Impala Language Reference to the latest version
* c5cb6f2 [HUE-8577](https://issues.cloudera.org/browse/HUE-8577) [autocomplete] Add support for Impala ALTER DATABASE statements
* 1193436 [HUE-8577](https://issues.cloudera.org/browse/HUE-8577) [autocomplete] Update the Impala SET options and UDFs
* 81cb646 [HUE-8577](https://issues.cloudera.org/browse/HUE-8577) [autocomplete] Add support for the Impala REFRESH AUTHORIZATION statement
* 884b58b [HUE-8682](https://issues.cloudera.org/browse/HUE-8682) [backend] Change PAM lib to python-pam-1.8.4
* 8d66b0b [HUE-8685](https://issues.cloudera.org/browse/HUE-8685) [importer] DB importer always shows DB already exists
* 02a236e [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [jb] Fix query interface single cluster
* a61122c [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Add additional metrics to query profile.
* 6bd7d7d [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [jb] Only show chart metrics when the API is enabled
* 367a905 [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [cluster] Add Warehouse title without tabs
* 1bc3ff8 [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [cluster] Hide extra apps in k8s mode too
* 2466152 [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [core] Avoid config checks false positive error in multi cluster mode
* f735b4f [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [cluster] Add proper Impala API in multicluster Impala
* b27dc3f [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [notebook] Order of ini properties is not properly loaded in global constant file
* 1856351 [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [jb] Show query profile in multi cluster multi cluster logic
* ad2cbe5 [HUE-8679](https://issues.cloudera.org/browse/HUE-8679) [notebook] Open query profile in correct cluster
* 88f944d [HUE-8681](https://issues.cloudera.org/browse/HUE-8681) [assist] Include non-opened topics in the language ref filter
* 4a0b2e9 [HUE-8677](https://issues.cloudera.org/browse/HUE-8677) [oozie] Oozie batch snippet hangs (#787)
* bd24275 PR737 [oozie] Support multiple groups in workflow permissions (#737)
* 4db8f45 [[HUE-7919](https://issues.cloudera.org/browse/HUE-7919)] oozie error 'NoneType' object has no attribute 'is_superuser' (#775)
* 52e8b9a PR791 [docker] correct the command to copy the hue.ini file (#791)
* c6fff47 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [libanalyse] Add missing localization folder
* ad820d7 [HUE-8598](https://issues.cloudera.org/browse/HUE-8598) [autocomplete] Improve autocomplete for CREATE statements
* f91ebbb [HUE-8671](https://issues.cloudera.org/browse/HUE-8671) [autocomplete] handle two escape character within quotes (#780)
* 02be9ec [HUE-8598](https://issues.cloudera.org/browse/HUE-8598) [autocomplete] Split the rules WithSerdeproperties and OptionalWithSerdeproperties into one for Impala and one for Hive (#749)
* 03850f1 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Add reset button to Impala plan.
* c331f37 [HUE-8587](https://issues.cloudera.org/browse/HUE-8587) [jb] Make impala api cache url specific.
* 5fa75c3 [HUE-8675](https://issues.cloudera.org/browse/HUE-8675) [core] Fix external users created as superuser
* 74af933 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Add more icons to Impala plan & fix Subplan
* cc15921 [HUE-8676](https://issues.cloudera.org/browse/HUE-8676) [jb] Fix pagination with is_hue_4 flag off
* fb3eb25 [HUE-8674](https://issues.cloudera.org/browse/HUE-8674) [jb] Revamp UX for Impala query plan.
* c6ea3ca [HUE-8587](https://issues.cloudera.org/browse/HUE-8587) [jb] Fix Jobbrowser to work with Smart Connection Pool
* 0113911 [HUE-8673](https://issues.cloudera.org/browse/HUE-8673) [notebook] Flag for the Impala query hints
* c05d0fb [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Make sure we alway have values for metrics in the resource graph
* 39dc303 [HUE-8673](https://issues.cloudera.org/browse/HUE-8673) [metrics] Get metrics for the proper cluster only
* 0116bef [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [impala] Add back query count metric variable
* 9c1bf12 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Show a message when metrics are being loaded
* bc2cd5e [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Get some metrics from prometheus instead of random data
* fcb7d10 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Add some transitions and format the performance graph axes
* b8d23df [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Switch to checkboxes for the legend in the performance graph
* 3d91405 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Add custom brush handles and improve colors in the performance graph
* 362339d [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Fix issue with flickering tooltip in the performance graph
* 4901183 [HUE-8672](https://issues.cloudera.org/browse/HUE-8672) [jb] Protect against basic graph display when data is empty
* cf01c37 [HUE-8672](https://issues.cloudera.org/browse/HUE-8672) [jb] Stopped cluster is different than terminated and should be in running category
* a80b889 [HUE-8672](https://issues.cloudera.org/browse/HUE-8672) [jb] Fix signature of profile function of get clusters
* c1fac4c [HUE-8672](https://issues.cloudera.org/browse/HUE-8672) [jb] Partially hook-in the metric stats to the usage chart
* 1c748a3 [HUE-8672](https://issues.cloudera.org/browse/HUE-8672) [core] Rename parameter steps to step in the Prometheus API
* 3bab502 [HUE-8672](https://issues.cloudera.org/browse/HUE-8672) [core] Provide an entry point to the Prometheus API
* 359ad79 [HUE-8672](https://issues.cloudera.org/browse/HUE-8672) [core] Add Prometheus querying API
* b3fdedd [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Remember the selected granularity in the performance graph
* fce9f2f [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Remember which graph is enabled in the performance graph
* a8bb7ab [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Improve focus indicators and add date to focus tooltip in the performance graph
* f322ba4 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Fix closest point detection on hover in the performance graph
* e155009 [HUE-8564](https://issues.cloudera.org/browse/HUE-8564) [useradmin] Fix last activity update for jobbrowser oozie logs
* 41f94ff [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Update scanner_filter rule with supported predicates.
* 9748f96 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Fix execution analysis disposal.
* 3c8df3f [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Add predicate optimization rule for Kudu.
* 7cfd6c9 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Fix Kudu missing stats reason.
* 1dcb093 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Add navigation from risk to plan.
* 0bc55aa [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Add Y axis labels to the performance graph
* 1084ac8 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Add granularity options to the performance graph
* b38051b [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Have the performance graph roll over instead of append
* ae8daa2 [HUE-8760](https://issues.cloudera.org/browse/HUE-8760) [jb] Polish hpa logic to display desired replicas and current CPU usage
* 4eef24e [HUE-8670](https://issues.cloudera.org/browse/HUE-8670) [jb] Reset or load autoscaling info properly in the forms
* 6d83ff8 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Add fix for missing statistics.
* 7b66215 [HUE-8670](https://issues.cloudera.org/browse/HUE-8670) [cluster] Switch Terminating cluster to Stopped when properly shutdown
* 5ad4813 [HUE-8670](https://issues.cloudera.org/browse/HUE-8670) [cluster] Wire-in the autoscale API
* 6a656d9 [HUE-8670](https://issues.cloudera.org/browse/HUE-8670) [jb] Add more air to mini Impala query browser to promote the query plan
* 78eaae3 [HUE-8670](https://issues.cloudera.org/browse/HUE-8670) [cluster] Adding auto resize option to the update cluster API
* d397106 [HUE-8670](https://issues.cloudera.org/browse/HUE-8670) [cluster] Updating UI to display auto scale properties
* 9fa9340 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Add background color and formatting to heatmap popup.
* 53c2a75 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Hide execution analysis tab prior to query execution.
* cf29e40 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Hide nodes that do not have risks.
* 641f23a [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Add rule to check if statistics are missing.
* 48b8d74 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Add tooltip and stacked bars for queries
* d7734e4 [HUE-8668](https://issues.cloudera.org/browse/HUE-8668) [editor] Add table names to syntax checker suggestions
* 07a0919 [HUE-8667](https://issues.cloudera.org/browse/HUE-8667) [autocomplete] Fix issue where order by and group by suggestions aren't displayed properly
* 85ff344 [HUE-8666](https://issues.cloudera.org/browse/HUE-8666) [autocomplete] Fix timing issue with "... ? from table" completion
* ea6df5e [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Add rule to detect missing metadata.
* e74c096 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Add number to risk alerts.
* 6c5e764 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [importer] Do not actually create the table when displaying the command
* dd09085 [HUE-8664](https://issues.cloudera.org/browse/HUE-8664) [importer] Fixed Flume source import properties initialization
* 9e817b3 [HUE-8665](https://issues.cloudera.org/browse/HUE-8665) [editor] Add basic execution analysis for Impala
* 61f2e40 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Create ApiHelper skeleton and fetch random stats every second in the performance graph
* 5c2b2f4 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Add support for appending data in the performance graph
* 938a9a2 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Support arbitrary amount of performance graphs
* 521c644 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Switch to D3 for rendering the performance graph
* 6c1dfdc [HUE-8140](https://issues.cloudera.org/browse/HUE-8140) [editor] Add additional statement types to automatic multi query execution
* cbf84f0 [HUE-8661](https://issues.cloudera.org/browse/HUE-8661) [assist] Enable scrollbars in context popover view sql
* abfa446 [HUE-7128](https://issues.cloudera.org/browse/HUE-7128) [core] Apply config ENABLE_DOWNLOAD to search dashboard download
* a8aae58 [HUE-8664](https://issues.cloudera.org/browse/HUE-8664) [metadata] Perform prefix search only
* 48da580 [HUE-8663](https://issues.cloudera.org/browse/HUE-8663) [core] Fix SAML TemplateDoesNotExist
* dbabd5c [HUE-8662](https://issues.cloudera.org/browse/HUE-8662) [core] Fix missing static URLs
* 5d94781 [HUE-8660](https://issues.cloudera.org/browse/HUE-8660) [assist] Support multiple # in file names for assist preview
* c7365a4 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Show multiple resources in the performance graph
* d5ba166 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Add auto resize threshold to performance graphs
* 4c045e1 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Add zoom and style the performance graph
* 5346841 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [jb] Switch to C3js for rendering performance graphs
* 6362225 [HUE-8649](https://issues.cloudera.org/browse/HUE-8649) [frontend] Add a performance graph component
* 7df4c16 [HUE-8659](https://issues.cloudera.org/browse/HUE-8659) [importer] Fix js exception with the field editor
* 4291704 [HUE-8660](https://issues.cloudera.org/browse/HUE-8660) [core] Fix page routing issues with file browser paths containing #
* cf89af8 [HUE-8660](https://issues.cloudera.org/browse/HUE-8660) [assist] Fix file preview in left assist for files with # in the name
* f043d76 [HUE-8658](https://issues.cloudera.org/browse/HUE-8658) [frontend] Fix popover alignment on first show
* b467c1c [HUE-8657](https://issues.cloudera.org/browse/HUE-8657) [jb] Add cluster configure action to single cluster view
* 12ccdf0 [HUE-8657](https://issues.cloudera.org/browse/HUE-8657) [jb] Adjust headings and paginator for warehouses mode
* 8ab6d78 [HUE-8657](https://issues.cloudera.org/browse/HUE-8657) [frontend] Switch to popover for create cluster options
* 2cc120b [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) test_fetch_result_size_mr increase timeout.
* d058bf9 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [notebook] Disable by default showing the file snippet selector
* e6ea83f [HUE-8656](https://issues.cloudera.org/browse/HUE-8656) [tb] Make sure a compute is always set in the table browser
* b3ea40d [HUE-8655](https://issues.cloudera.org/browse/HUE-8655) [editor] Have the location handler wait for a compute and namespace to be set
* 4253f9a [HUE-8654](https://issues.cloudera.org/browse/HUE-8654) [editor] Prevent setting empty object for namespace and compute
* 70d0367 [HUE-8654](https://issues.cloudera.org/browse/HUE-8654) [editor] Guarantee a namespace and compute is set in single cluster mode
* 5c4b159 [HUE-8652](https://issues.cloudera.org/browse/HUE-8652) [frontend] Fix JS exception in jquery.hiveautocomplete when no namespaces are returned
* 123fa67 [HUE-8651](https://issues.cloudera.org/browse/HUE-8651) [editor] Add a dedicated execution analysis tab in the editor
* d4b188f [HUE-8651](https://issues.cloudera.org/browse/HUE-8651) [frontend] Add an execution analysis component
* b56f954 [HUE-8651](https://issues.cloudera.org/browse/HUE-8651) [assist] Remove execution analysis from the right assist
* 551769b [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] test_get_interpreters_to_show reset DESKTOP_APPS redux
* 077fd90 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] xxd_test SkipTest import
* 0479b9d [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] test_get_interpreters_to_show reset DESKTOP_APPS
* 2b38919 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] xxd_test SkipTest if xxd is not found.
* 85dcb96 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] TestResourceManagerHaNoHadoop tearDown reset API_CACHE
* 7cadf0d [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix solr_client_test reset_properties correctly.
* 26e7f35 [HUE-8647](https://issues.cloudera.org/browse/HUE-8647) [assist] Show DB info icon regardless of nav configuration
* f1e1be2 [HUE-8631](https://issues.cloudera.org/browse/HUE-8631) [hbase] pull thrift transport from hbase-site.xml
* 16f2e75 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix impala integration tests setup.
* 255aa7c [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix test_get_interpreters_to_show reset blacklist
* fce4687 [HUE-8648](https://issues.cloudera.org/browse/HUE-8648) [importer] sqoop configured rdbms fails
* ab79f5c [core] Hue-8644 fixing test_user_admin
* 10306fa [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] dbms swap caching key username to id.
* d98fff7 [HUE-8645](https://issues.cloudera.org/browse/HUE-8645) [jb] Clear cluster selection after killing a cluster
* ecbde74 [[HUE-8645](https://issues.cloudera.org/browse/HUE-8645)](https://issues.cloudera.org/browse/[HUE-8645](https://issues.cloudera.org/browse/HUE-8645)) [assist] Refresh namespaces when a cluster is killed
* bb0fe68 [[HUE-8645](https://issues.cloudera.org/browse/HUE-8645)](https://issues.cloudera.org/browse/[HUE-8645](https://issues.cloudera.org/browse/HUE-8645)) [assist] Poll for namespace status change when a namespace is starting
* ae25884 PR770 [doc] Edited markdown headers (#770)
* 4723c65 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix test_db_migrations_mysql mysql not installed.
* 5842bac [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] TestDashboard catch_unicode_time unable to parse date
* ffb6a19 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix test_dump_config & test_config_check HUE_CONF_DIR
* 3c2f1d8 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix tests_doc2 test_import_owned_document data
* 507bd41 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix notebook get_sample_data operation default
* 45364f0 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [metadata] Skip tests that fail when the catalog is to slow to update
* f141c1f [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix test_show_tables metastore table post
* 841da88 [HUE-8643](https://issues.cloudera.org/browse/HUE-8643) [importer] Fix showing the import command
* 3b2be2c [core] [HUE-8640](https://issues.cloudera.org/browse/HUE-8640) adding missing parameters like statement_raw and variables in snippets to fix test in TestNotebookApi
* a7ac485 [HUE-8641](https://issues.cloudera.org/browse/HUE-8641) [frontend] Trigger a namespace refresh when the context catalog is cleared
* b11d426 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [importer] Enable context popover and syntax error highlighting in the importer field editor
* 9719948 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [core] Remove dead webworker code for embedded mode
* 91b7e4b [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [frontend] Disable operations in the context popover for temporary entries
* c6f0648 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [frontend] Enable breadcrumb navigation in the context popover for temporary entries
* 740c138 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [frontend] Add samples to temporary catalog entries
* 55f5253 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [frontend] Make sure a temporary source is created in the data catalog for temporary tables
* af6b424 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [editor] Move context popover and tooltip logic out of the aceEditor binding
* b1e0243 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [editor] Extract editor webworker logic to global handler
* 643ce72 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [importer] Pre-fill a complete statement for the field editor
* d28c18f [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [importer] Improve the query editor table name
* 1d091ea [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix TestBeeswaxWithHadoop describe_table post
* 64014ca [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] sql_tests missing sourceType
* 42b2198 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix test_create_database metastore url
* 918dd21 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix install_samples loaddata atomic
* 0b7ce11 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix import_documents loaddata atomic
* f63c4ab [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix test_db_migrations_mysql missing mysql command
* 62424ef [HUE-8639](https://issues.cloudera.org/browse/HUE-8639) [metadata] Include the docstring into the configuration
* fa4a904 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [importer] Add autocomplete of source fields to the editor in the importer
* 2383933 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [frontend] Add default set of metadata for temporary entries
* 3917cc8 [HUE-8638](https://issues.cloudera.org/browse/HUE-8638) [frontend] Add the ability to create temporary tables in the data catalog
* fd0cd4f [HUE-8639](https://issues.cloudera.org/browse/HUE-8639) [metadata] Do not do Sentry filtering when Sentry is not configured
* 291ec57 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [metastore] Update describe table tests to use POST and not GET now
* 3a9fc19 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix test_make_log_links hue 4 links
* eb5cc60 [HUE-8630](https://issues.cloudera.org/browse/HUE-8630) [core] Fix test_db_migrations_sqlite missing import
* 9f99f69 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Keep only external cluster configs in [[clusters]]
* 38c59fd [HUE-8636](https://issues.cloudera.org/browse/HUE-8636) [assist] Fix the show in assist link in the language reference context popover
* 1263ece [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [sql] Remove hardcoding to timeout after 5s when executing statement
* 3c85e44 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [core] API should not check for remote cloud clusters if they are not configured
* 1f2229d [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Improve font in wxm images when Roboto isn't available
* cec46c1 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Improve SFDC import autocomplete
* 1a20edc [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Use oozie icon for workflows in the sidebar
* b2041f9 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Fix invalidate flush in K8S mode
* 09607f4 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Have the sidebar items depend on the current cluster mode
* 215c7d4 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Increase the size of the DE logo
* 8e3e247 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Add pubSub to switch between DE and DW mode
* 026c972 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Hide json message when creating a k8 cluster
* 489b710 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Fix bug disabling the Kill button for k8s services
* d89f5fd [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [impapal] Fix _get_impala_result_size when using multi cluster
* a96edec [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [js] Fix typo when importing cluster flag
* fc58c39 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Use URL to determine which left nav item is active
* 2b83a35 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Change the workflows icon
* f5056fa [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Add DE logo
* 41eefcb [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Always flush all on invalidate in K8 only mode
* 7fb0945 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Use smaller input for the number of replicas
* 468906f [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [jb] Move resize action to show on the same line
* dab24a4 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Tweak the menu to show clusters in the bottom
* cfcc227 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Use cluster icon for warehouses
* 95da0bc [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Save sidebar collapsed state in total storage and have it open by default
* 321c7ae [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [jb] Add tabs in cluster view
* cdbcbcd [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Prevent initial js error in the dw sidebar when no app is set
* 160d5fd [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Add warehouses icon
* ecb4723 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Keep left sidebar items constant
* 438f496 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [jb] Simplify cluster service page
* 4555512 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Remove double level menu links for now
* 69927f3 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Tweak the menu to only show the core apps
* 19515d3 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Add an inner left nav for multi cluster only mode
* c937a14 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Remove home, data eng and stewart from the left hamburger menu
* f3cfe08 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [frontend] Add dw logos
* e78a63c [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [core] Tweak the left menu items
* 67e565f [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [impala] Remove mocked impalad http address
* 193582e [HUE-8610](https://issues.cloudera.org/browse/HUE-8610) [tb] Convert GET format to POST for describe table
* 93029ba [HUE-8610](https://issues.cloudera.org/browse/HUE-8610) [tb] Post the source type when calling describe table
* f48ba7e [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [jb] Add PoC WXM Summary
* 2621aef [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Add more information to the service section
* 26a2d82 [HUE-8617](https://issues.cloudera.org/browse/HUE-8617) [impala] Support multi cluster in invalidate metadata
* 0b32fb6 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Split cluster and service creation in two
* 6f08a22 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [cluster] Consolidate the menu
* 4b763ca [HUE-8616](https://issues.cloudera.org/browse/HUE-8616) [cluster] getNamespaces for impala returns namespace with hive compute
* 7275c9c [HUE-8605](https://issues.cloudera.org/browse/HUE-8605) [metadata] Only show the Table Privilege tab when Sentry is enabled
* 68d65c0 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Show generated command for Flume pipelines
* 8e6e155 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [metadata] DESCRIBE EXTENTED DATABASE incompability with Impala
* 22bc6e8 [HUE-8586](https://issues.cloudera.org/browse/HUE-8586) [metastore] Support multi cluster parameters
* b409450 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Saving pipeline API skeleton
* 9237f43 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Skeleton of show command popup for Sqoop import
* 7baece9 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Skeleton of show command popup for CREATE TABLE from a file
* 96afa5b [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Include morphline files into the tasks
* e04e5e8 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Do not disable submit when input is Kafka and output Kudu and table already exists
* 98cdc84 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Add skeleton support for from Kafka to Solr
* 602f50f [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Example of from Kafka to Kudu via Spark
* 2afc770 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [importer] Automatically prefill output table name when sqooping one table
* 487fc7f [HUE-8586](https://issues.cloudera.org/browse/HUE-8586) [notebook] Add selected cluster to the sample popup check status call
* 3f28d33 [HUE-8586](https://issues.cloudera.org/browse/HUE-8586) [notebook] Fix interface name conflict on data API calls with multi cluster
* 798709a [HUE-8586](https://issues.cloudera.org/browse/HUE-8586) [metadata] Integrate sample API with the multi cluster logic
* fce62d6 [HUE-8330](https://issues.cloudera.org/browse/HUE-8330) [metadata] Convert /impala-hive/api API to support multi cluster
* 326ca89 [HUE-8586](https://issues.cloudera.org/browse/HUE-8586) [cluster] Properly list compute clusters in compute API with k8s
* 05c4501 [HUE-8586](https://issues.cloudera.org/browse/HUE-8586) [notebook] Add selected cluster to the create session call
* 28d756e [HUE-8586](https://issues.cloudera.org/browse/HUE-8586) [cluster] Rename k8 properties to k8s
* 3ea20d8 PR759 [doc] Update installation guide for MacOS (#759)


Contributors
------------

This Hue release is made possible thanks to the contribution from:

* Aaron Newton
* Aaron Peddle
* Aaron T. Myers
* abec
* Abraham Elmahrek
* Aditya Acharya
* Adrian Yavorskyy
* aig
* airokey
* Alex Breshears
* Alex Newman
* Alex (posi) Newman
* alheio
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
* Atupal
* Avindra Goolcharan
* bcwalrus
* bc Wong
* Ben Bishop
* Ben Gooley
* Ben White
* Bhargava Kalathuru
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
* Derek Chen-Becker
* Diego Sevilla Ruiz
* Dominik Gehl
* Eli Collins
* Enrico Berti
* Erick Tryzelaar
* Ewan Higgs
* fatherfox
* gdgt
* Gilad Wolff
* grundprinzip
* Grzegorz Kokosiński
* Guido Serra
* happywind
* Harsh
* Harsh J
* Hector Acosta
* Henry Robinson
* Igor Wiedler
* Ilkka Turunen
* Istvan
* Ivan Dzikovsky
* Ivan Orlov
* Jack McCracken
* Jaguar Xiong
* Jakub Kukul
* Jarcek
* jdesjean
* jeff.melching
* Jenny Kim
* jheyming
* Joe Crobak
* Joey Echeverria
* Johan Ahlen
* Johan Åhlén
* Jon Natkins
* Josh Walters
* Karissa McKelvey
* Kevin Wang
* Khwunchai Jaengsawang
* Kostas Sakellis
* krish
* Lars Francke
* Li Jiahong
* linchan-ms
* Linden Hillenbrand
* Luca Natali
* Luke Carmichael
* lvziling
* maiha
* Marcus McLaughlin
* Mariusz Strzelecki
* Mathias Rangel Wulff
* Matías Javier Rossi
* Max T
* Michael Prim
* Michal Ferlinski
* Michalis Kongtongk
* Mobin Ranjbar
* motta
* mrmrs
* Mykhailo Kysliuk
* Nicolas Fouché
* NikolayZhebet
* Olaf Flebbe
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
* Peter Slawski
* Philip Zeyliger
* Piotr Ackermann
* pkuwm
* Prachi Poddar
* Prakash Ranade
* Prasad Mujumdar
* Qi Xiao
* rainysia
* raphi
* Renxia Wang
* Rick Bernotas
* Ricky Saltzer
* robrotheram
* Romain Rigaux
* Roman Shaposhnik
* Roohi
* Roohi Syeda
* Rui Pereira
* Sai Chirravuri
* Scott Kahler
* Sean Mackrory
* Shahab Tajik
* Shawarma
* Shawn Van Ittersum
* shobull
* Shrijeet
* Shrijeet Paliwal
* Shuo Diao
* Siddhartha Sahu
* Simon Beale
* Simon Whittaker
* sky4star
* spaztic1215
* Stefano Palazzo
* Stephanie Bodoff
* Suhas Satish
* TAKLON STEPHEN WU
* Tamas Sule
* Tatsuo Kawasaki
* Taylor Ainsworth
* Thai Bui
* thinker0
* Thomas Aylott
* Thomas Poepping
* Tianjin Gu
* tjphilpot
* todaychi
* Todd Lipcon
* Tom Mulder
* Vadim Markovtsev
* van Orlov
* vinithra
* voyageth
* vybs
* Wang, Xiaozhe
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
* Yoer
* Yuriy Hupalo
* ywheel
* Zachary York
* Zach York
* Zhang Bo
* Zhang Ruiqiang
* zhengkai
* Zhihai Xu
* z-york
* 小龙哥
