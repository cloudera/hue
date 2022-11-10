---
title: "4.11.0"
date: 2022-11-07T00:00:00+00:00
draft: false
weight: -4090
tags: ['skipIndexing']
---

## Hue v4.11.0, released  November 7th 2022

Hue is an open source SQL Cloud Assistant for querying [Databases & Data Warehouses](https://docs.gethue.com/administrator/configuration/connectors/): [gethue.com](https://gethue.com)


### Summary

Here is a summary of the [main improvements](https://gethue.com/categories/version-4.11/) of 4.11 on top of the previous [4.10](https://gethue.com/blog/hue-4-10-sql-scratchpad-component-rest-api-small-file-importer-slack-app/) release:


#### Python3.8 /Gunicorn/

Content??

#### Supporting Iceberg Syntax in Hue importer

Apache Iceberg is a high-performance format for huge analytic tables. Now you can create a Iceberg Table through Hue importer.

Read more about the [Creating Iceberg tables in Hue](https://gethue.com/blog/2022-10-11-creating-iceberg-tables-in-hue/).


#### HPL/SQL Support

HPL/SQL is an Apache open source procedural extension for SQL for Hive users. It has its own grammar. It is included with Apache Hive from version 2.0. 

You can enable the HPL/SQL dialect via desktop/conf/hue.ini config file section.
        
        [notebook]
        [[interpreters]]
        [[[hplsql]]]
        name=Hplsql
        interface=hiveserver2

Read more about the [HPL/SQL Support](https://gethue.com/blog/2022-02-01-hplsql-support/).

#### Object/File Storage public REST API

content??

#### Tech stack & Tooling

- [Create SQL tables from excel files](https://gethue.com/blog/2021-11-15-create-sql-tables-from-execl-files/)
- [Access your data in ABFS without any credential keys](https://gethue.com/blog/2021-09-21-access-your-data-in-abfs-without-any-credential-keys/)
- [Create Phoenix tables in Just 2 steps](https://gethue.com/blog/2021-08-17-create-phoenix-tables-in-just-2-steps/)
- [Open In Importer and Copy Path Options in Filebrowser](https://gethue.com/blog/2021-08-10-open-in-importer-and-copy-path-options-in-filebrowser/)
- [Create SQL tables on the fly with zero clicks](https://gethue.com/blog/2021-07-26-create-sql-tables-on-the-fly-with-zero-clicks/)
- [Azure Storage sharing by leveraging SAS tokens so that your users don’t need credentials](https://gethue.com/blog/2021-06-30-how-to-use-azure-storage-rest-api-with-shared-access-sginature-sas-tokens/)



It has more than 650+ commits and 100+ bug fixes!

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
* [Tarball](https://cdn.gethue.com/downloads/hue-4.11.0.tgz) or [source](https://github.com/cloudera/hue/archive/release-4.11.0.zip)

### Compatibility

Tested on CentOS versions 6.8+, Red Hat Enterprise Linux (RHEL 6, 7, 8), and Ubuntu 18.04 and 20.04.

Compatible with the two most recent versions of the following browsers:

* Chrome
* Firefox LTS
* Safari
* Microsoft Edge

Runs with Python 2.7 and 3.8.


### List of commits

* [676d5f4d78](https://github.com/cloudera/hue/commit/676d5f4d78) [editor] Enable the syntax checker for SparkSQL
* [6bec0b99b2](https://github.com/cloudera/hue/commit/6bec0b99b2) [editor] Add SparkSQL autocomplete for auxiliary statements
* [1f76a3443c](https://github.com/cloudera/hue/commit/1f76a3443c) [editor] Various improvements to the parser test utils
* [11fc7d8521](https://github.com/cloudera/hue/commit/11fc7d8521) [editor] Add SparkSQL autocomplete for DROP, INSERT, LOAD, MSCK and TRUNCATE statements
* [f44ad922b6](https://github.com/cloudera/hue/commit/f44ad922b6) [editor] Move the Impala DROP DATABASE tests to json
* [49e647f144](https://github.com/cloudera/hue/commit/49e647f144) [editor] Add SparkSQL autocomplete for CREATE statements
* [f443ab3e54](https://github.com/cloudera/hue/commit/f443ab3e54) [editor] Extract Hive ROW FORMAT and CLUSTERED BY clauses into separate grammar files
* [b123a39561](https://github.com/cloudera/hue/commit/b123a39561) [editor] Add SparkSQL autocomplete for ALTER statements
* [55aa213cb4](https://github.com/cloudera/hue/commit/55aa213cb4) [editor] Base SparkSQL autocompleter and syntax checker
* [89a3d65d92](https://github.com/cloudera/hue/commit/89a3d65d92) [Phoenix] Upgrading phoenixdb into it's latest version (#3053)
* [52ddca56ba](https://github.com/cloudera/hue/commit/52ddca56ba) Add DELETE to suggestKeywords of generic parser (fixes  #2983)
* [1c45fc7c5a](https://github.com/cloudera/hue/commit/1c45fc7c5a) [docker] Replace Exception with ImportError for impala import in query_api.py (#3060)
* [c2e0520a80](https://github.com/cloudera/hue/commit/c2e0520a80) Upgrading protobuf python module to 3.20.3 version
* [b8155fff5e](https://github.com/cloudera/hue/commit/b8155fff5e) Removed file chooser component folder
* [ec3ea1578c](https://github.com/cloudera/hue/commit/ec3ea1578c) [frontend]Improvements to initial file chooser commit
* [8ff802d18e](https://github.com/cloudera/hue/commit/8ff802d18e) Removed FileChooserModal.scss from import which was causing CircleCI build fail
* [74120bab25](https://github.com/cloudera/hue/commit/74120bab25) Fixed the style linting errors from initial file chooser component commit
* [4296761d2d](https://github.com/cloudera/hue/commit/4296761d2d) Initial Filechooser modal
* [4a967d1f86](https://github.com/cloudera/hue/commit/4a967d1f86) Bump django from 3.2.15 to 3.2.16 in /desktop/core (#3049)
* [3bb1e2d96f](https://github.com/cloudera/hue/commit/3bb1e2d96f) [ext-py][Py2] Bump pytz to 2015.7 for Babel 2.9.1 package (#3050)
* [d83107392a](https://github.com/cloudera/hue/commit/d83107392a) [frontend] improved copy result to clipboard support
* [67aeea75e8](https://github.com/cloudera/hue/commit/67aeea75e8) [raz] Add flag for autocreation of user directories (#3048)
* [688b03585a](https://github.com/cloudera/hue/commit/688b03585a) Receiving invalid syntax error when using MySql with RDBMS under interperter (#3045)
* [1beca69b08](https://github.com/cloudera/hue/commit/1beca69b08) [frontend] Convert the tests for the generic autocomplete parser to json format (#3040)
* [ff4b43b332](https://github.com/cloudera/hue/commit/ff4b43b332) [frontend] fix modal overflow for sharing saved sql queries
* [1db6bbdb17](https://github.com/cloudera/hue/commit/1db6bbdb17) [raz] Don't show other FS icons in RAZ enabled envs (#3043)
* [fc6411563a](https://github.com/cloudera/hue/commit/fc6411563a) [Blog] adding blog post for iceberg support in Hue importer (#3041)
* [eb9cf5c11b](https://github.com/cloudera/hue/commit/eb9cf5c11b) [CVE][Py2] Bump httplib2 to 0.20.4 to fix high and medium severity CVEs (#3036)
* [5022117c8a](https://github.com/cloudera/hue/commit/5022117c8a) [docs] create react section for CONTRIBUTING.md
* [426669d26b](https://github.com/cloudera/hue/commit/426669d26b) [frontend] Add support for parser tests next to the jison definition
* [9539e73255](https://github.com/cloudera/hue/commit/9539e73255) [frontend] add modern i18n support
* [dbc7631743](https://github.com/cloudera/hue/commit/dbc7631743) [frontend] Regenerate all the parsers
* [ba3ae3a010](https://github.com/cloudera/hue/commit/ba3ae3a010) [frontend] Improve autocomplete and syntax parser generation and structure
* [b30107515d](https://github.com/cloudera/hue/commit/b30107515d) [frontend] Add solr and global search parsers back
* [61507f0a43](https://github.com/cloudera/hue/commit/61507f0a43) [frontend] Remove the druid and elasticsearch parsers
* [19d8fe752c](https://github.com/cloudera/hue/commit/19d8fe752c) [CVE][Py3] Bump Mako and djangomako packages to fix high severity CVE (#3031)
* [674223552b](https://github.com/cloudera/hue/commit/674223552b) [CVE][Py2] Bump lxml to 4.9.1 from 3.3.6 to fix medium and high severity CVEs (#3034)
* [c13c0b11c1](https://github.com/cloudera/hue/commit/c13c0b11c1) [CVE][Py3] Bump django-celery-result to 2.4.0 to fix high severity CVE (#3033)
* [97efc9afb3](https://github.com/cloudera/hue/commit/97efc9afb3) [CVE][Py3] Bump lxml from 4.6.5 to 4.9.1 in /desktop/core (#2918)
* [cc268646b0](https://github.com/cloudera/hue/commit/cc268646b0) [fronten] add user-event library and update test example
* [d90cd6cf25](https://github.com/cloudera/hue/commit/d90cd6cf25) [CVE][Py2] Bump Babel to 2.9.1 in ext-py directory to mitigate high severity CVE (#3029)
* [fa3e3cab98](https://github.com/cloudera/hue/commit/fa3e3cab98) [core] Remove babel version bump comment from requirements.txt (#3024)
* [2c3001b89b](https://github.com/cloudera/hue/commit/2c3001b89b) [CVE] Bump babel from 2.5.3 to 2.9.1 in /desktop/core (#3022)
* [209b8db54d](https://github.com/cloudera/hue/commit/209b8db54d) Revert "Impala table import is failing when beeswax max_number_of_sessions != 0"
* [f4d0ebcbe0](https://github.com/cloudera/hue/commit/f4d0ebcbe0) [knox] Disabled the MultipleProxyMiddleware for py2 (#3021)
* [18c66856fc](https://github.com/cloudera/hue/commit/18c66856fc) [raz] Automatically create user directories for ABFS (#3016)
* [74804f7b86](https://github.com/cloudera/hue/commit/74804f7b86) [phoenix] adding phoenixdb in requirement.txt file (#3018)
* [2045a79b21](https://github.com/cloudera/hue/commit/2045a79b21) [raz] Remove extra comma in _handle_relative_path method params (#3015)
* [f997ca34bb](https://github.com/cloudera/hue/commit/f997ca34bb) [frontend] Update bable-cli to 7.18.10
* [da95c24a5e](https://github.com/cloudera/hue/commit/da95c24a5e) [frontend] Replace markdown with snarkdown
* [cf4296efdf](https://github.com/cloudera/hue/commit/cf4296efdf) [frontend] Update select2 to 4.0.13
* [a448c4e6d4](https://github.com/cloudera/hue/commit/a448c4e6d4) [frontend] Update terser to 5.15.0
* [03c124ccda](https://github.com/cloudera/hue/commit/03c124ccda) [frontend] Update async to 2.6.4/3.2.4
* [00ade8c111](https://github.com/cloudera/hue/commit/00ade8c111) [frontend] Upgrade jquery-ui to 1.13.2
* [62b0808872](https://github.com/cloudera/hue/commit/62b0808872) [frontend] Upgrade grunt to 1.5.3
* [4347fb1ab0](https://github.com/cloudera/hue/commit/4347fb1ab0) [frontend] add support for antd modal component (#3013)
* [cf3ebf8b3b](https://github.com/cloudera/hue/commit/cf3ebf8b3b) [raz] Skip checking parent path stats when RAZ is enabled (#3009)
* [2d3c8aefa1](https://github.com/cloudera/hue/commit/2d3c8aefa1) [frontend] Convert some icons to React
* [64cb0e472e](https://github.com/cloudera/hue/commit/64cb0e472e) [importer] Adding iceberg syntax in importer (#2980)
* [ef515e5f50](https://github.com/cloudera/hue/commit/ef515e5f50) [hbase] Fix module has no attribute from io.StringIO when there is no avro module loaded (#3006)
* [9888316f9a](https://github.com/cloudera/hue/commit/9888316f9a) [frontend] Add tsx to eslint and fix linting issues
* [aecf9b0ff5](https://github.com/cloudera/hue/commit/aecf9b0ff5) [oozie] Fix rerun workflow URL when Knox is enabled (#3003)
* [00aae19e84](https://github.com/cloudera/hue/commit/00aae19e84) [frontend] add ant design library (#2996)
* [8611218d71](https://github.com/cloudera/hue/commit/8611218d71) [CVE] Change version of sanitize-html to 2.7.2 and handle null condition for deXSS function (#3005)
* [f8ed919c76](https://github.com/cloudera/hue/commit/f8ed919c76) [docs] Change postresql brew command for Mac installation (#3001)
* [15f20ed70d](https://github.com/cloudera/hue/commit/15f20ed70d) Adding PPC platform support
* [14801e7ae2](https://github.com/cloudera/hue/commit/14801e7ae2) [importer] increasing the value of DATA_UPLOAD_MAX_MEMORY_SIZE to 5MB as sometime request size > 2.5MB (default value) (#2966)
* [5b3798758a](https://github.com/cloudera/hue/commit/5b3798758a) [docker_py3] Skip installing pybigquery because of protobuf changes (#2992)
* [d139bbfd13](https://github.com/cloudera/hue/commit/d139bbfd13) [docker] Revert protobuf change and set PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python in py3 image (#2991)
* [8dac801691](https://github.com/cloudera/hue/commit/8dac801691) [frontend] - unmount react root on DOM node disposal (#2982)
* [b0fa4996c6](https://github.com/cloudera/hue/commit/b0fa4996c6) [core] Add protobuf as last pypi requirement (#2988)
* [6fc577c11e](https://github.com/cloudera/hue/commit/6fc577c11e) [raz] Update mapping for ABFS list operation (#2965)
* [c6861365d7](https://github.com/cloudera/hue/commit/c6861365d7) [importer] same file re-upload (#2970)
* [42994728a5](https://github.com/cloudera/hue/commit/42994728a5) [importer] Fixing only headers CSV file table creation in Local File importer on Impala (#2967)
* [028f946691](https://github.com/cloudera/hue/commit/028f946691) [core] Bump the go version to 1.17 for documentation lint
* [d5634ef1fa](https://github.com/cloudera/hue/commit/d5634ef1fa) Bump django from 3.2.14 to 3.2.15 in /desktop/core (#2954)
* [fd1960d4df](https://github.com/cloudera/hue/commit/fd1960d4df) [frontent] add support for % in file and folder names (#2981)
* [1a6c0d4a1b](https://github.com/cloudera/hue/commit/1a6c0d4a1b) [frontend] react integration (#2963)
* [895a4b217e](https://github.com/cloudera/hue/commit/895a4b217e) [proxyfs] Shift crequest middleware import to the top (#2979)
* [d0d384550b](https://github.com/cloudera/hue/commit/d0d384550b) [assist] Prevent automatic opening of unknown tables in the right assist
* [898da24cbc](https://github.com/cloudera/hue/commit/898da24cbc) [oozie] Remove math.floor to fix scheduled workflow progress (#2881)
* [140844ba5d](https://github.com/cloudera/hue/commit/140844ba5d) [raz] Allow users with access to create own home dirs (#2968)
* [2a3a7e7e39](https://github.com/cloudera/hue/commit/2a3a7e7e39) [core] Fix query history timestamp of installing example tables (#2969)
* [6583e4de2f](https://github.com/cloudera/hue/commit/6583e4de2f) [core] Make exception for lz-string in checkLicense as it's actually MIT and not WTFPL
* [e4f14839e8](https://github.com/cloudera/hue/commit/e4f14839e8) Oozie MapReduce action should be able to accept s3a and abfs as Jar name (#2974)
* [a4df9c89bc](https://github.com/cloudera/hue/commit/a4df9c89bc) Impala table import is failing intermittently when beeswax max_number_of_sessions != 0
* [e353cd7019](https://github.com/cloudera/hue/commit/e353cd7019) [Build] Fixing django-axes editable build issue
* [7e8bea6dd1](https://github.com/cloudera/hue/commit/7e8bea6dd1) [hiveserver2] Fix unpacking guid by using base64.b64decode for python3 (#2949)
* [cc8ece8686](https://github.com/cloudera/hue/commit/cc8ece8686) [core] Fix metrics log when running Gunicorn (#2956)
* [618bee3eb0](https://github.com/cloudera/hue/commit/618bee3eb0) Impala table import is failing when beeswax max_number_of_sessions != 0
* [ba36160800](https://github.com/cloudera/hue/commit/ba36160800) [frontent] Support special and non ascii characters in file download (#2953)
* [8975533620](https://github.com/cloudera/hue/commit/8975533620) Hue with ID Broker HA (#2869)
* [c0fd538ac1](https://github.com/cloudera/hue/commit/c0fd538ac1) [py3] Fix error when start Hue shell on command line (#2947)
* [2cbeefde8a](https://github.com/cloudera/hue/commit/2cbeefde8a) [docs] Improve Hue build steps for MacOs steps with ROOT variable addition (#2933)
* [685887c933](https://github.com/cloudera/hue/commit/685887c933) [gunicorn] Fix ManualTLS 7.1.8 cluster install fails as Hue service doesn't start
* [710249012a](https://github.com/cloudera/hue/commit/710249012a) [docker] Remove redundant import of impala conf (#2945)
* [5257685bfb](https://github.com/cloudera/hue/commit/5257685bfb) [indexer] Check whether impala conf is present or not (#2944)
* [b470478f65](https://github.com/cloudera/hue/commit/b470478f65) [docker] Add ROOT variable in Hue py3 Dockerfile (#2943)
* [2fd313cb04](https://github.com/cloudera/hue/commit/2fd313cb04) [py3] Add python-pam 2.0.2 (#2942)
* [244b2edd07](https://github.com/cloudera/hue/commit/244b2edd07) [pylint] Refactor oozie dashboard.py to remove long line, bad indentation, extra spaces etc.
* [654c048117](https://github.com/cloudera/hue/commit/654c048117) [oozie] Fix submitting oozie workflow from HDFS
* [346c235dab](https://github.com/cloudera/hue/commit/346c235dab) [s3] Log potential boto error for debugging (#2940)
* [482fe0e560](https://github.com/cloudera/hue/commit/482fe0e560) Revert "Enable LDAP TLS in Hue configs is not working as expected (#2864)" (#2939)
* [bf76d8de7a](https://github.com/cloudera/hue/commit/bf76d8de7a) [Importer] notifying if file is empty (#2938)
* [d505ed3adc](https://github.com/cloudera/hue/commit/d505ed3adc) [test] Fixing Hue help test
* [0700eb5100](https://github.com/cloudera/hue/commit/0700eb5100) [build] Fixing python3 based make apps in git commitflow
* [ec1e70439f](https://github.com/cloudera/hue/commit/ec1e70439f) [backend] Enable Gunicorn server in Hue
* [c81051c937](https://github.com/cloudera/hue/commit/c81051c937) [filemanager] Fix Hue hadoop file manager issue for uploading file
* [618407fc18](https://github.com/cloudera/hue/commit/618407fc18) [notebook] Installing notebook examples gives error
* [0dcf3941e6](https://github.com/cloudera/hue/commit/0dcf3941e6) [solr] Installing solr examples gives error
* [59c7f9388a](https://github.com/cloudera/hue/commit/59c7f9388a) [oozie] Installing oozie examples gives error
* [6720597279](https://github.com/cloudera/hue/commit/6720597279) [build] Improve Hue Makefiles and scripts to enable Python 3.8
* [7708acb63f](https://github.com/cloudera/hue/commit/7708acb63f) Bump django from 3.2.13 to 3.2.14 in /desktop/core (#2917)
* [d6141b624e](https://github.com/cloudera/hue/commit/d6141b624e) [py3] Increase default MAX_NUMBER_OF_SESSIONS to 10
* [f545a3c3f2](https://github.com/cloudera/hue/commit/f545a3c3f2) [sparksql] Convert unicode values to str (#2926)
* [563ea37038](https://github.com/cloudera/hue/commit/563ea37038) Revert "[Importer] supporting large file(10MB) for local importer" (#2924)
* [93bc654a57](https://github.com/cloudera/hue/commit/93bc654a57) [local importer] restricting the upload size to 200KB (#2923)
* [6fce8924c4](https://github.com/cloudera/hue/commit/6fce8924c4) [sparksql] Make error messages friendly and understandable (#2922)
* [bfbca13657](https://github.com/cloudera/hue/commit/bfbca13657) [interpreters] Dialect field should not have spaces (#2921)
* [4a7731d4ff](https://github.com/cloudera/hue/commit/4a7731d4ff) [sparksql] Add /describe APIs, fix column /autocomplete API and skip /sample_data for transactional table (#2913)
* [ca1d9537db](https://github.com/cloudera/hue/commit/ca1d9537db) When Impala editor is not installed, then the importer fails to get the USER_SCRATCH_DIR_PERMISSION from impala conf. (#2915)
* [c257a67f58](https://github.com/cloudera/hue/commit/c257a67f58) Empty feature fails to clear .trash (#2916)
* [dd808b4617](https://github.com/cloudera/hue/commit/dd808b4617) [build] Remove extra create-static from make install (#2912)
* [5ab7cf3612](https://github.com/cloudera/hue/commit/5ab7cf3612) [frontend] Hide import button for transactional hive tables (#2910)
* [b2bab308e0](https://github.com/cloudera/hue/commit/b2bab308e0) Revert "[interpreters] Do not add all default interpreters of every whitelisted app (#2903)" (#2911)
* [38d9c9f662](https://github.com/cloudera/hue/commit/38d9c9f662) [phoenixdb] adding modified phoenixdb lib in ext-py3 folder (#2904)
* [f5407f95a3](https://github.com/cloudera/hue/commit/f5407f95a3) [frontend] fix to upload files to folders with non ascii names for s3 and abfs (#2907)
* [91062b8300](https://github.com/cloudera/hue/commit/91062b8300) [local importer] limiting the file size to 1MB (#2909)
* [6e299b11ce](https://github.com/cloudera/hue/commit/6e299b11ce) [interpreters] Do not add all default interpreters of every whitelisted app (#2903)
* [45a900b3be](https://github.com/cloudera/hue/commit/45a900b3be) [frontend] hide import in table browser for spark (#2900)
* [81758f4d63](https://github.com/cloudera/hue/commit/81758f4d63) [importer] not calling guess format just after clicking importer icon (#2902)
* [bd6324a79c](https://github.com/cloudera/hue/commit/bd6324a79c) [sparksql] Change snippet type from 'sql to 'sparksql' (#2901)
* [930c5acad1](https://github.com/cloudera/hue/commit/930c5acad1) [py3] Update default SAML signing algorithm from SHA1 to SHA256
* [dd2e3f70b9](https://github.com/cloudera/hue/commit/dd2e3f70b9) [py2] Update default SAML signing algorithm from SHA1 to SHA256
* [e1b42d7acc](https://github.com/cloudera/hue/commit/e1b42d7acc) [hdfs] Fix webhdfs code issues (#2896)
* [f33cbc4dc7](https://github.com/cloudera/hue/commit/f33cbc4dc7) [docs] Clarify setting Hue DB info under [desktop] (#2895)
* [0f1a1b7290](https://github.com/cloudera/hue/commit/0f1a1b7290) Disabling lint check for /ext-py3 folder (#2898)
* [5cf2a1c1fc](https://github.com/cloudera/hue/commit/5cf2a1c1fc) Refresh icon in left Assist while on DB panel resets to 'default' DB on table panel (#2897)
* [6d45dfc0c3](https://github.com/cloudera/hue/commit/6d45dfc0c3) Increase Gunicorn Worker Timeout Value for Upload Large File.
* [2901e0d8f6](https://github.com/cloudera/hue/commit/2901e0d8f6) [phoenix] get_view_names() returning empty list (#2889)
* [878a4bffe2](https://github.com/cloudera/hue/commit/878a4bffe2) [importer] disabling the direct upload by default (#2890)
* [117353a8b0](https://github.com/cloudera/hue/commit/117353a8b0) Export all does not work as Hive managed table location cannot be changed (#2885)
* [d61ba44d44](https://github.com/cloudera/hue/commit/d61ba44d44) [query history] Change submitted Impala job time from UTC to localtime
* [c40a2981e1](https://github.com/cloudera/hue/commit/c40a2981e1) [frontend] use encoded tags for complex db types when copying result to clipboard (#2887)
* [c07f5830aa](https://github.com/cloudera/hue/commit/c07f5830aa) [frontend] fix to upload files with non ascii names on macos (#2888)
* [9d774afeaa](https://github.com/cloudera/hue/commit/9d774afeaa) [frontend] fix issues related to file path encoding in file browser
* [05527e55ce](https://github.com/cloudera/hue/commit/05527e55ce) [sparksql] Only close livy session of particular dialect per user (#2882)
* [cd8ba1233b](https://github.com/cloudera/hue/commit/cd8ba1233b) [docs] Update Hue installation steps for macOS section (#2878)
* [90713cea6d](https://github.com/cloudera/hue/commit/90713cea6d) [jwt] Decode JWT in custom auth backend for py2 also (#2877)
* [c43c898b02](https://github.com/cloudera/hue/commit/c43c898b02) [localization] skipping the fuzzy translation (#2876)
* [7b0694aab3](https://github.com/cloudera/hue/commit/7b0694aab3) Allow only TLSv1.2 ciphers when SSL is enabled (#2872)
* [09999a1560](https://github.com/cloudera/hue/commit/09999a1560) [jwt] Bump djangorestframework-simplejwt to 5.2.0 (#2875)
* [3e6ff805bf](https://github.com/cloudera/hue/commit/3e6ff805bf) [jwt] Bump PyJWT package to 2.4.0 to fix high severity CVE (#2873)
* [ed4f20addf](https://github.com/cloudera/hue/commit/ed4f20addf) [hdfs] Fix File browser zipfile upload bug (#2862)
* [802811941d](https://github.com/cloudera/hue/commit/802811941d) Enable LDAP TLS in Hue configs is not working as expected (#2864)
* [8f24a01cf4](https://github.com/cloudera/hue/commit/8f24a01cf4) [autocomplete] Revert pluggable autocompleter as it's causing build issues
* [357fa6cc19](https://github.com/cloudera/hue/commit/357fa6cc19) [core] Remove port from database setting for Oracle RAC (#2868)
* [fdf927d55e](https://github.com/cloudera/hue/commit/fdf927d55e) [sparksql] Clean unused session from /fetch_result_data call (#2867)
* [71c588b074](https://github.com/cloudera/hue/commit/71c588b074) [frontend] Enable background for welcome tour (#2863)
* [25b30d1078](https://github.com/cloudera/hue/commit/25b30d1078) [autocomplete] make sql autocomplete and syntax parsers pluggable (#2861)
* [bf90850fa4](https://github.com/cloudera/hue/commit/bf90850fa4) [frontend] Fix welcome tour bug for admin accounts
* [c3fe65ef4a](https://github.com/cloudera/hue/commit/c3fe65ef4a) [sparksql] Store Livy session details in the UserProfile (#2860)
* [7cb46979ee](https://github.com/cloudera/hue/commit/7cb46979ee) [ui] Spark application history links not working when Knox is enabled (#2859)
* [b5d126ea65](https://github.com/cloudera/hue/commit/b5d126ea65) [build] Fix build issue on Ubuntu20 (#2857)
* [33d4f05497](https://github.com/cloudera/hue/commit/33d4f05497) [sparksql] Improve session reuse and fix corner cases (#2851)
* [cba12fbbf6](https://github.com/cloudera/hue/commit/cba12fbbf6) [phoenixdb] Switch to old user impersonation code for phoenix (#2852)
* [fea68948ea](https://github.com/cloudera/hue/commit/fea68948ea) [frontend] add iceberg indicator to table browser (#2849)
* [4d00fdc845](https://github.com/cloudera/hue/commit/4d00fdc845) [ui] Improve yarn config check for skipping job names in log div (#2853)
* [50a99466a8](https://github.com/cloudera/hue/commit/50a99466a8) [frontend] fix linechart rendering in barchart KO binding (#2844)
* [64c491582c](https://github.com/cloudera/hue/commit/64c491582c) Remove django-debug-toolbar and django_debug_panel (#2846)
* [1316403e55](https://github.com/cloudera/hue/commit/1316403e55) Merge pull request #2843 from cloudera/bjorn--Location-link-on-the-Table-Browser-page-is-dead
* [ad0dacc5b2](https://github.com/cloudera/hue/commit/ad0dacc5b2) [frontend] replace location popover with link to filebrowser
* [a7c1299f89](https://github.com/cloudera/hue/commit/a7c1299f89) [core] removing mysql config and will add this config in doc (#2841)
* [2a9fb19104](https://github.com/cloudera/hue/commit/2a9fb19104) Merge pull request #2837 from cloudera/bjorn--Left-Assists-should-have-an-icon-to-indicate-Iceberg-Tables
* [6242c23e5c](https://github.com/cloudera/hue/commit/6242c23e5c) [frontend] Add iceberg icon to tables in left assist popover
* [6ba92cc402](https://github.com/cloudera/hue/commit/6ba92cc402) [ui] Check for yarn config when adding application job ids (#2839)
* [dc301dbc75](https://github.com/cloudera/hue/commit/dc301dbc75) [config] Change config type from bool to coerce_bool (#2836)
* [42f025c7d0](https://github.com/cloudera/hue/commit/42f025c7d0) CircleCI: Add build jobs that run on Linux ARM64 (#2834)
* [9755cf0623](https://github.com/cloudera/hue/commit/9755cf0623) [UI] fitting long description in window (#2831)
* [b350c2e904](https://github.com/cloudera/hue/commit/b350c2e904) Addressing typo for default_fs.startwith('abfs://') (#2833)
* [8ea7fa562f](https://github.com/cloudera/hue/commit/8ea7fa562f) Fix Nonetype error for HS2 session properties (#2830)
* [4c9ff15758](https://github.com/cloudera/hue/commit/4c9ff15758) [frontend] Add shortcut key for toggling side panels (#2827)
* [c4b866830f](https://github.com/cloudera/hue/commit/c4b866830f) Option to get the defaultFS for ABFS from core-site else use the config from Hue (#2826)
* [2a4d826607](https://github.com/cloudera/hue/commit/2a4d826607) Added missing conditions and error logging for Hive HA via ZK (#2828)
* [627b8cae04](https://github.com/cloudera/hue/commit/627b8cae04) [sparksql] Close unused Livy sessions to free up resources (#2825)
* [9a708b97aa](https://github.com/cloudera/hue/commit/9a708b97aa) [doc] Update Python 3.8.10 installation on M1 based Mac (#2823)
* [491c83b745](https://github.com/cloudera/hue/commit/491c83b745) Bump django from 3.2.12 to 3.2.13 in /desktop/core (#2817)
* [14170fe98f](https://github.com/cloudera/hue/commit/14170fe98f) New users are not added to default group when using OIDCBackend (#2814)
* [04381aa7aa](https://github.com/cloudera/hue/commit/04381aa7aa) Add exception handling when whoami_s in ldaptest fails (#2813)
* [9bb6c67b2d](https://github.com/cloudera/hue/commit/9bb6c67b2d) [libs] upgrading pandas and openpyxl (#2807)
* [d74373dc45](https://github.com/cloudera/hue/commit/d74373dc45) Setting Atlas search to basic as default instead of DSL (#2812)
* [2290ee680b](https://github.com/cloudera/hue/commit/2290ee680b) GH-2570 - LDAP auth error: can't decode byte 0xc3 (#2622)
* [fef28c864f](https://github.com/cloudera/hue/commit/fef28c864f) Hive Autocomplete and docs update (#2811)
* [fe7f840823](https://github.com/cloudera/hue/commit/fe7f840823) [Importer] supporting large file(10MB) for local importer (#2801)
* [64c85429be](https://github.com/cloudera/hue/commit/64c85429be) [docs] Document create directory public API (#2803)
* [b523f6a409](https://github.com/cloudera/hue/commit/b523f6a409) [api] Port create directory filebrowser API to public (#2802)
* [237e38bfbe](https://github.com/cloudera/hue/commit/237e38bfbe) Set non-root default user for Hue images
* [f0fe40d076](https://github.com/cloudera/hue/commit/f0fe40d076) [docs] Fix Apache Livy dead link (#2804)
* [2726f2d730](https://github.com/cloudera/hue/commit/2726f2d730) Hue - Fix ABFS file upload (#2800)
* [e751b863ca](https://github.com/cloudera/hue/commit/e751b863ca) [sparksql] Enhance SparkSQL support via Apache Livy for Hue (#2794)
* [e95d043e3a](https://github.com/cloudera/hue/commit/e95d043e3a) [api] Add is_yarn_enabled in /get_config API (#2798)
* [257f367039](https://github.com/cloudera/hue/commit/257f367039) [docker] Add few kerberos packages in py3 Dockerfile (#2797)
* [79351e52c1](https://github.com/cloudera/hue/commit/79351e52c1) [ci] Remove failing py3.8 circleci check (#2796)
* [17087afbb2](https://github.com/cloudera/hue/commit/17087afbb2) Performed a complete manual test by stopping and starting Hive server multiple times and one at a time to ensure that the Hue code can replace the Old active HS2 with the new Active HS2. (CDPD-10924) (#1720)
* [7f3d4109e3](https://github.com/cloudera/hue/commit/7f3d4109e3) Revert eventlet from 0.31.0 back to 0.30.2 due to incompatible with gunicorn 19.9.0 (#2782)
* [baa74f8640](https://github.com/cloudera/hue/commit/baa74f8640) [core] upgrading celery to the latest version as older version has CVEs (#2776)
* [56c1355b21](https://github.com/cloudera/hue/commit/56c1355b21) Fix "trusted" column issue in django-axes-5.13.0 module
* [0128288860](https://github.com/cloudera/hue/commit/0128288860) [core] getting complete snippet for close_statement call (#2777)
* [64351af95e](https://github.com/cloudera/hue/commit/64351af95e) [core] upgrading ipython to latest version (#2775)
* [61b5efed77](https://github.com/cloudera/hue/commit/61b5efed77) [editor] Fix timing issue with import where duplicate insert statements are executed
* [698520ad16](https://github.com/cloudera/hue/commit/698520ad16) [core] closing older query before running new query (#2769)
* [8d6446c9bf](https://github.com/cloudera/hue/commit/8d6446c9bf) Bump eventlet from 0.30.2 to 0.31.0 in /desktop/core (#2366)
* [03da1b05eb](https://github.com/cloudera/hue/commit/03da1b05eb) Bump babel from 2.5.1 to 2.9.1 in /desktop/core (#2613)
* [e5fb1e27ee](https://github.com/cloudera/hue/commit/e5fb1e27ee) Bump lxml from 4.5.0 to 4.6.5 in /desktop/core (#2747)
* [a73fb0bb64](https://github.com/cloudera/hue/commit/a73fb0bb64) [editor] Update the built-in Impala language reference, UDF library and highlting rules
* [373842b714](https://github.com/cloudera/hue/commit/373842b714) [editor] Update the Impala autocomplete and syntax parsers
* [5f96d4973b](https://github.com/cloudera/hue/commit/5f96d4973b) Remove chardet dependancy
* [c2869cbc35](https://github.com/cloudera/hue/commit/c2869cbc35) Hue [py3] Revert django-axes's accessattempt and accesslog Model removal of trusted column
* [5e3eac82af](https://github.com/cloudera/hue/commit/5e3eac82af) Hue [py3] Enabling django-axes from desktop/core/ext-py3 folder
* [30b35e19c5](https://github.com/cloudera/hue/commit/30b35e19c5) Hue [py3] Adding django-axes-5.13.0 module in ext-py3
* [dcc810063f](https://github.com/cloudera/hue/commit/dcc810063f) Updating Hue package requirement
* [7613d5caa7](https://github.com/cloudera/hue/commit/7613d5caa7) Usefull scripts (#2761)
* [44051098f1](https://github.com/cloudera/hue/commit/44051098f1) [ui] Fix issues from NPM audit
* [c3d4849211](https://github.com/cloudera/hue/commit/c3d4849211) [core] Remove package-lock.json from tools and docs
* [4fdc0853b8](https://github.com/cloudera/hue/commit/4fdc0853b8) Hue [py3] Remove reseting git state step
* [ec6df264d8](https://github.com/cloudera/hue/commit/ec6df264d8) Hue [py3] Perform any other container build process
* [ddf0795208](https://github.com/cloudera/hue/commit/ddf0795208) Hue [py3] reset git state prior to docker build
* [79608c86dd](https://github.com/cloudera/hue/commit/79608c86dd) Hue [py3] Bump up Hue interim docker image version
* [3bb0ada598](https://github.com/cloudera/hue/commit/3bb0ada598) [api] Fix /get_logs and /fetch_result_size public APIs (#2749)
* [9123b75ec5](https://github.com/cloudera/hue/commit/9123b75ec5) Set catalog interface and api_url to none if Atlas and Navigator are not available (#2750)
* [70d6a89cf7](https://github.com/cloudera/hue/commit/70d6a89cf7) [ui] Fix sidebar issue with SDK apps
* [ef8a385130](https://github.com/cloudera/hue/commit/ef8a385130) [jobbrowser] Remove incomplete Hive Querybrowser skeleton (#2743)
* [07c5f7071c](https://github.com/cloudera/hue/commit/07c5f7071c) Hue [py3] Enable SAML certificate creation with passphrase support.
* [83d5effcc2](https://github.com/cloudera/hue/commit/83d5effcc2) Hue [py3] Fixing build script
* [4ddcfef2de](https://github.com/cloudera/hue/commit/4ddcfef2de) Updated config.yml. Removing python-36 build
* [4f84ab8635](https://github.com/cloudera/hue/commit/4f84ab8635) Hue [py3] Fixing charset_normalizer import
* [95ae51b0eb](https://github.com/cloudera/hue/commit/95ae51b0eb) Hue [py3] Installing djangosaml2 from ext-py3
* [fa1b914aef](https://github.com/cloudera/hue/commit/fa1b914aef) Hue [py3] Fix SAML TemplateDoesNotExist
* [5204cd63f9](https://github.com/cloudera/hue/commit/5204cd63f9) Hue [py3] Adding djangosaml2 python module
* [2645e748fd](https://github.com/cloudera/hue/commit/2645e748fd) Hue [py3] Installing pysaml2 from ext-py3
* [107cafa187](https://github.com/cloudera/hue/commit/107cafa187) Hue [py3] Enable SAML certificate creation with passphrase support.
* [bcd0192ff4](https://github.com/cloudera/hue/commit/bcd0192ff4) Hue [py3] Adding pysaml2-5.0.0 python library
* [399167634a](https://github.com/cloudera/hue/commit/399167634a) Hue [py3] Remove chardet dependency in requests
* [761f2eb064](https://github.com/cloudera/hue/commit/761f2eb064) Hue [py3] Remove chardet dependency in requests
* [cddd98d85f](https://github.com/cloudera/hue/commit/cddd98d85f) Hue [py3] Adding requests-2.27.1 python module
* [1120348a1f](https://github.com/cloudera/hue/commit/1120348a1f) Hue [py3] Improve Hue makefiles to support python 3.8 1. Use pip as python package manger. 2. Use "requirements.txt" for python packages listing. 3. Perform one of a kind package installation.
* [a3c3c7f467](https://github.com/cloudera/hue/commit/a3c3c7f467) Hue [py3] Enable gunicorn based fronend server (#2739)
* [1311c9b334](https://github.com/cloudera/hue/commit/1311c9b334) Added '/' which was missed out when performing status check when there is no slash '/' at the end of the url for Atlas server. (#2741)
* [8122467539](https://github.com/cloudera/hue/commit/8122467539) Hue [py3] Upgrade boto library to boto 2.49 (#2738)
* [bdae1fec15](https://github.com/cloudera/hue/commit/bdae1fec15) Fixing b64encode string issue (#2737)
* [be1f9068a1](https://github.com/cloudera/hue/commit/be1f9068a1) Hue [py3] Fix CsrfViewMiddleware and SAML CORS issue (#2733)
* [eb894a12c0](https://github.com/cloudera/hue/commit/eb894a12c0) Hue [py3] Improve Hue container build script to "UBI8/Python3.8" version. (#2731)
* [ddb87f3c2a](https://github.com/cloudera/hue/commit/ddb87f3c2a) Hue [py3] Enable HTTP_X_FORWARDED header detection (#2732)
* [05eee28bf4](https://github.com/cloudera/hue/commit/05eee28bf4) Hue [py3] Fix Hue code lint issues.. (#2736)
* [562077ae17](https://github.com/cloudera/hue/commit/562077ae17) Atlas add basic search option and set search cluster to 'cm' as default (#2730)
* [efb9ea9d8c](https://github.com/cloudera/hue/commit/efb9ea9d8c) [RAZ] allowing user to go outside home bucket (#2729)
* [d5088ce1b2](https://github.com/cloudera/hue/commit/d5088ce1b2) [docs] Add /get_filesystem API and improve some curl API examples (#2724)
* [049da696a5](https://github.com/cloudera/hue/commit/049da696a5) Take the Hue base URL into account when redirecting from the Hue 404 page (#2718)
* [5d16552444](https://github.com/cloudera/hue/commit/5d16552444) [docs] Replace font awesome dead link with new one (#2725)
* [586d821ff0](https://github.com/cloudera/hue/commit/586d821ff0) Bump django from 3.2.5 to 3.2.12 in /desktop/core (#2716)
* [07d484d1ad](https://github.com/cloudera/hue/commit/07d484d1ad) [api] Port /get_filesystems filebrowser API to public (#2723)
* [272f50a342](https://github.com/cloudera/hue/commit/272f50a342) [core] calling close statement api after sample query (#2715)
* [448f6c5e48](https://github.com/cloudera/hue/commit/448f6c5e48) [ui] NPM audit fixes and stylelint upgrade to address CVEs (#2709)
* [fc742d5e92](https://github.com/cloudera/hue/commit/fc742d5e92) [pylint] Fix bad indendation
* [47f0433152](https://github.com/cloudera/hue/commit/47f0433152) [tests] Give option of code coverage for explicitly mentioned packages
* [9c88b464f8](https://github.com/cloudera/hue/commit/9c88b464f8) [hplsql] temporary solution for left assist and table browser (#2707)
* [638b5d66e2](https://github.com/cloudera/hue/commit/638b5d66e2) [hplsql] replace connector_name beeswax to hive (#2706)
* [f4c0716b10](https://github.com/cloudera/hue/commit/f4c0716b10) [hplsql] adding hplsql as a connector (#2701)
* [0db15a1636](https://github.com/cloudera/hue/commit/0db15a1636) [hplsq] adding hplsql dialect in Hue docs (#2699)
* [d998f8d632](https://github.com/cloudera/hue/commit/d998f8d632) [ui] Avoid displaying service connectivity error in a popup (#2698)
* [d5082439f8](https://github.com/cloudera/hue/commit/d5082439f8) [docs] Update Hue setup guide with latest steps for M1 Macs (#2705)
* [bf9032b749](https://github.com/cloudera/hue/commit/bf9032b749) [hplsql] updating the hplsql blog post (#2700)
* [8974173ad9](https://github.com/cloudera/hue/commit/8974173ad9) [Hplsql] adding blog post of hplsql support (#2697)
* [cf040eff85](https://github.com/cloudera/hue/commit/cf040eff85) [core] update Hue SAML LOGOUT URL for CDP
* [5257098c65](https://github.com/cloudera/hue/commit/5257098c65) Bump ipython from 7.16.1 to 7.16.3 in /desktop/core (#2689)
* [fc05f5bcc3](https://github.com/cloudera/hue/commit/fc05f5bcc3) [hplsql] hplsql editor name HPL/SQL and placeholder (#2687)
* [f4a1463c9b](https://github.com/cloudera/hue/commit/f4a1463c9b) [hplsql] syntax highlight for hplsql dialect (#2682)
* [1a6aee2f9f](https://github.com/cloudera/hue/commit/1a6aee2f9f) [hplsql] changing the name from Hplsql to HPL/SQL in editor and icon (#2686)
* [22c0824b1a](https://github.com/cloudera/hue/commit/22c0824b1a) [docs] Add optional database param and update /delete connector field (#2685)
* [9ec1b48e6a](https://github.com/cloudera/hue/commit/9ec1b48e6a) [hplsql] using right method for checking key presence (#2684)
* [2b814257bf](https://github.com/cloudera/hue/commit/2b814257bf) [api] Add optional database param for /execute public API (#2683)
* [3373cfe403](https://github.com/cloudera/hue/commit/3373cfe403) [hplsql] removing v1 code and improving v2 code (#2672)
* [23f02102d4](https://github.com/cloudera/hue/commit/23f02102d4) [Hplsql] adding hplsql dialect (#2671)
* [0a580edf19](https://github.com/cloudera/hue/commit/0a580edf19) [importer] adding blog post for remote excel file importer (#2667)
* [3c6e95fc4d](https://github.com/cloudera/hue/commit/3c6e95fc4d) Bump lxml from 4.6.3 to 4.6.5 in /desktop/core
* [4982a291ab](https://github.com/cloudera/hue/commit/4982a291ab) [importer] adding excel support for remote file importer
* [28e2d38504](https://github.com/cloudera/hue/commit/28e2d38504) [filebrowser] Add test for default index dir for empty path in URL (#2665)
* [c5a44c6adb](https://github.com/cloudera/hue/commit/c5a44c6adb) GH-2631 Empty Path to Filebrowser making Folders Inaccessible (#2645)
* [28e3c2e554](https://github.com/cloudera/hue/commit/28e3c2e554) [catalog] Selecting one atlas server if there are multiple listed out under atlas.rest.address #1931. (#1931)
* [e9240fe760](https://github.com/cloudera/hue/commit/e9240fe760) [core] Add unicodecsv 0.14.1, xlrd 2.0.1 and xlwt 1.3.0 for tablib 0.12.1
* [cbd1b4fe30](https://github.com/cloudera/hue/commit/cbd1b4fe30) [core] Downgrade tablib from 0.14.0 to 0.12.1
* [2c5c886004](https://github.com/cloudera/hue/commit/2c5c886004) [saml] Fix key_file has no attribute 'strip' when resp assertion signed (#2648)
* [b07e0e7823](https://github.com/cloudera/hue/commit/b07e0e7823) [navigator] Change req params from type tuple to dict in navigator-client (#2647)
* [022ff04e55](https://github.com/cloudera/hue/commit/022ff04e55) [cve] Remove pillow from Django 1.11.29 ext-py package(#2649)
* [34950c37ab](https://github.com/cloudera/hue/commit/34950c37ab) [importer] adding xlsx file type for importer
* [d6eb81f589](https://github.com/cloudera/hue/commit/d6eb81f589) [frontend] Upgrade Jest, eslint and core-js
* [431bd78519](https://github.com/cloudera/hue/commit/431bd78519) [frontend] Bump the version of various jQuery plugins
* [42939218c6](https://github.com/cloudera/hue/commit/42939218c6) [blog] supporting xlsx file for direct importer
* [ea6d736af3](https://github.com/cloudera/hue/commit/ea6d736af3) [core] Implement Hue SAML LOGOUT URL for CDP. Redirect the client to logout URL when idle session timeout has expired (#2643)
* [62e7a7400e](https://github.com/cloudera/hue/commit/62e7a7400e) [importer] auto formatting table and header name
* [f5f0a5235d](https://github.com/cloudera/hue/commit/f5f0a5235d) Extract the build config to be reusable for AMD64 and ARM64 (#2555)
* [11944dc12a](https://github.com/cloudera/hue/commit/11944dc12a) [frontend] Bump axios to 0.24.0
* [67fd25e3dd](https://github.com/cloudera/hue/commit/67fd25e3dd) [frontend] Update the handle after execute with has_result_set from subsequent check status calls
* [538c61ed7c](https://github.com/cloudera/hue/commit/538c61ed7c) [importer] importer supporting xlsx file for local small file option
* [e548fe6181](https://github.com/cloudera/hue/commit/e548fe6181) [editor] Update has_result_set from check_status response for public API (#2638)
* [0a45f973b2](https://github.com/cloudera/hue/commit/0a45f973b2) [jb] Enable left assist jobbrowser when Query Store is present (#2633)
* [de7503b762](https://github.com/cloudera/hue/commit/de7503b762) [core] Implement Hue SAML LOGOUT URL for CDP. Redirect the client to logout URL when idle session timeout has expired
* [8f5521adc7](https://github.com/cloudera/hue/commit/8f5521adc7) Incorrect password allows to log into Hue when using pam_use_pwd_module with LDAP as a backend (#2629)
* [a6e609c444](https://github.com/cloudera/hue/commit/a6e609c444) [jobbrowser] Revert queries-hive `No JSON object could be decoded` commit (#2624)
* [8a05adf375](https://github.com/cloudera/hue/commit/8a05adf375) [dashboard] adding 'allow_unsecure_html' config flag
* [92507fa8f9](https://github.com/cloudera/hue/commit/92507fa8f9) [frontend] Append username for RAZ in Importer filechooser (#2619)
* [070d2cac15](https://github.com/cloudera/hue/commit/070d2cac15) [jobbrowser] Fix `No JSON object could be decoded` error for queries-hive (#2616)
* [c7cac77036](https://github.com/cloudera/hue/commit/c7cac77036) [Phoenix Parser] adding autocomplete support of 'UPSERT' and removing 'INSERT'
* [af1b300f8f](https://github.com/cloudera/hue/commit/af1b300f8f) [pylint] Fix bad-whitespace and long lines issues
* [cefdcd028c](https://github.com/cloudera/hue/commit/cefdcd028c) [raz] Default to accessible path in Importer filechooser
* [b41af06ded](https://github.com/cloudera/hue/commit/b41af06ded) [ci] Remove `ca-certificate upgrade` and do `apt get update` (#2610)
* [eb5429a7d0](https://github.com/cloudera/hue/commit/eb5429a7d0) Bump django from 3.2.4 to 3.2.5 in /desktop/core
* [37d90438a1](https://github.com/cloudera/hue/commit/37d90438a1) [filebrowser] preventing auto down scroll after upload, delete and create a file
* [c1e4cc6ed1](https://github.com/cloudera/hue/commit/c1e4cc6ed1) [docs] Update get user IAM public REST APIs (#2600)
* [606f73b847](https://github.com/cloudera/hue/commit/606f73b847) [filebrowser] removing 'delete-link' class from delete button
* [39c9334076](https://github.com/cloudera/hue/commit/39c9334076) [docs] Update missing Hbase section images from CDN (#2602)
* [e002726f59](https://github.com/cloudera/hue/commit/e002726f59) [raz] Append username to default home dir in RAZ enabled env (#2601)
* [68d30133bc](https://github.com/cloudera/hue/commit/68d30133bc) [api] Add IAM related public APIs (#2598)
* [c01df1ce5b](https://github.com/cloudera/hue/commit/c01df1ce5b) [beeswax] adding config flag for max no of objects in the left assist, autocomplete, table browser etc.
* [3012f07284](https://github.com/cloudera/hue/commit/3012f07284) [hplsql] adding 'HPL/SQL with 'Hive' in editor heading
* [b5f48c7acb](https://github.com/cloudera/hue/commit/b5f48c7acb) [jobbrowser] Pass cookie info to query_store
* [4f2d7df1bb](https://github.com/cloudera/hue/commit/4f2d7df1bb) [ci] Upgrade ca-certificates for `build-py-36` Circle CI check (#2596)
* [9ff2a25b55](https://github.com/cloudera/hue/commit/9ff2a25b55) [beeswax] adding unittest for sorting of tables
* [c145448706](https://github.com/cloudera/hue/commit/c145448706) [beeswax] sorting the tables
* [e37f7c33f1](https://github.com/cloudera/hue/commit/e37f7c33f1) [docs] Add Top search public API in Data Catalog section
* [feb617f306](https://github.com/cloudera/hue/commit/feb617f306) Homedirectory is created with superuser nobody or anyother user other than hdfs (hdfs superuser), can cause permission denied when accessing the homedirectory (#2569)
* [e6f16397b2](https://github.com/cloudera/hue/commit/e6f16397b2) [hplsql] modifying the get_statement according to hplsql mode
* [d135a726e5](https://github.com/cloudera/hue/commit/d135a726e5) [hplsql] hplsql_session reuse solution
* [6247b4ca09](https://github.com/cloudera/hue/commit/6247b4ca09) [frontend] Change INTERACTIVE_SEARCH_API to public
* [ee73b4d91f](https://github.com/cloudera/hue/commit/ee73b4d91f) [docs] Fix typo in custom JWT section
* [9023a17e0f](https://github.com/cloudera/hue/commit/9023a17e0f) [api] Add Top Search APIs to public
* [835fa5a1b0](https://github.com/cloudera/hue/commit/835fa5a1b0) adding more tests for hplsql parser
* [6385a12199](https://github.com/cloudera/hue/commit/6385a12199) adding logic in utils.ts for changing the parser according to hplsql mode
* [818759c3a2](https://github.com/cloudera/hue/commit/818759c3a2) [parser] adding hplsql statements parser
* [fb297ca9de](https://github.com/cloudera/hue/commit/fb297ca9de) [docs] Show how to upload resources to the CDN
* [a6d73dc01d](https://github.com/cloudera/hue/commit/a6d73dc01d) [blog] Add RAZ ADLS blog post (#2571)
* [a85d9ed942](https://github.com/cloudera/hue/commit/a85d9ed942) [docs] Add custom JWT section in REST APIs
* [18cd3094c6](https://github.com/cloudera/hue/commit/18cd3094c6) GH-2373 disable local_infile in RDBS mysql client by default  (#2541)
* [a998378f8f](https://github.com/cloudera/hue/commit/a998378f8f) GH-2542 HUE Not picking up atlas information (asnaik) (#2543)
* [148342bdda](https://github.com/cloudera/hue/commit/148342bdda) fixing pylint issues
* [66f654d24b](https://github.com/cloudera/hue/commit/66f654d24b) [hplsql] adding hplsql config to on and off the HPLSQL mode
* [c44e64e5f0](https://github.com/cloudera/hue/commit/c44e64e5f0) [importer] calling guess_field_types for both 'localfile' and 'remote file' options
* [2cc6c8534b](https://github.com/cloudera/hue/commit/2cc6c8534b) [raz_s3] Do not enable S3 browser in ADLS (#2562)
* [11f2c318d4](https://github.com/cloudera/hue/commit/11f2c318d4) [blog] Add blog post for custom JWT Auth backend (#2563)
* [21594978db](https://github.com/cloudera/hue/commit/21594978db) [ci] Keep package list up to date
* [d75c8fc7b3](https://github.com/cloudera/hue/commit/d75c8fc7b3) Bump sqlparse from 0.4.1 to 0.4.2 in /desktop/core
* [e08f801b74](https://github.com/cloudera/hue/commit/e08f801b74) Bump CircleCI version to 2.1
* [15a4c074e0](https://github.com/cloudera/hue/commit/15a4c074e0) [docs] Fix missing end tag in HBase connector docs
* [cb94d5ba59](https://github.com/cloudera/hue/commit/cb94d5ba59) Update _index.md
* [927b183572](https://github.com/cloudera/hue/commit/927b183572) [docs] Convert the title styling to basic Markdown in README
* [799ff294b2](https://github.com/cloudera/hue/commit/799ff294b2) [docs] Small README rephrasing
* [9f33cad173](https://github.com/cloudera/hue/commit/9f33cad173) [jwt] Fix thrift_util to use the right user (#2549)
* [af2a50a212](https://github.com/cloudera/hue/commit/af2a50a212) [raz] Remove checks for disabling S3 browser (#2548)
* [bb9440b663](https://github.com/cloudera/hue/commit/bb9440b663) [ci] Do not set first good issues as stale
* [bd1c5d144c](https://github.com/cloudera/hue/commit/bd1c5d144c) [docs] Add proper references to pypi
* [df0f4895d1](https://github.com/cloudera/hue/commit/df0f4895d1) [ci] Skip link checks on pypi as they are blocked
* [5ae9257d0c](https://github.com/cloudera/hue/commit/5ae9257d0c) [docs] Simplify more the top README instructions
* [23ea7b3dad](https://github.com/cloudera/hue/commit/23ea7b3dad) [docs] How to release the pypi package
* [4580e4ab4f](https://github.com/cloudera/hue/commit/4580e4ab4f) [docs] First cli docs
* [271c77c296](https://github.com/cloudera/hue/commit/271c77c296) [raz_adls] Refactor rename operation section (#2539)
* [56a6c734b0](https://github.com/cloudera/hue/commit/56a6c734b0) [jwt] Injecting JWT as bearer token over THttpClient to Impala (#2533)
* [5d506b76af](https://github.com/cloudera/hue/commit/5d506b76af) [raz_adls] Check when setting abfs default_fs to start with `abfs://`
* [8119f7d497](https://github.com/cloudera/hue/commit/8119f7d497) [raz_adls] Improve ADLS mapping and cleaner tests
* [9c7a615481](https://github.com/cloudera/hue/commit/9c7a615481) [libs] Bump to latest ipdb
* [313cfa134a](https://github.com/cloudera/hue/commit/313cfa134a) [metadata] Private UI Risk API is missing some connector properties
* [f7f2027fc8](https://github.com/cloudera/hue/commit/f7f2027fc8) [docs] Add copy operation for ADLS
* [80db312351](https://github.com/cloudera/hue/commit/80db312351) [metadata] Fix Python styling issues in test files
* [c242e1c0bc](https://github.com/cloudera/hue/commit/c242e1c0bc) [metadata] Fix serialization of risk API
* [7ccd8ae1d3](https://github.com/cloudera/hue/commit/7ccd8ae1d3) [docs] Add chmod and rename operations for ADLS
* [bd84b5037b](https://github.com/cloudera/hue/commit/bd84b5037b) [raz] Tiny code stlying issues
* [fdccf1c15c](https://github.com/cloudera/hue/commit/fdccf1c15c) [docs] Small example of Python API to submit a query
* [226dcf6d3f](https://github.com/cloudera/hue/commit/226dcf6d3f) [raz_adls] Add test for rename operation
* [40604db950](https://github.com/cloudera/hue/commit/40604db950) [raz_adls] Decouple SAS token fetching from RAZ Http Client
* [7b2b22d24e](https://github.com/cloudera/hue/commit/7b2b22d24e) [raz_adls] Improve rename operation and add chmod test
* [de02167b12](https://github.com/cloudera/hue/commit/de02167b12) [raz_adls] Add mapping for edit ops and rename ops
* [071a55513e](https://github.com/cloudera/hue/commit/071a55513e) GH-2511 Hue Document tab is using different timestamp  (asnaik) (#2512)
* [6c137d73ae](https://github.com/cloudera/hue/commit/6c137d73ae) [abfs] Specify the username in upload requests
* [218575add8](https://github.com/cloudera/hue/commit/218575add8) [jwt] Add issuer and audience for token verification (#2505)
* [b122ccee0d](https://github.com/cloudera/hue/commit/b122ccee0d) [raz_s3] Dont enable S3 when bucket prop not in core_site.xml (#2514)
* [8b61b07d2c](https://github.com/cloudera/hue/commit/8b61b07d2c) [frontend] Bump the NPM version
* [ae0f2e4b43](https://github.com/cloudera/hue/commit/ae0f2e4b43) [editor] Throttle the predict typeahead and cancel any running predicts on change
* [59359b6332](https://github.com/cloudera/hue/commit/59359b6332) [raz] Provide a 403 error instead of 503
* [56aaecacb7](https://github.com/cloudera/hue/commit/56aaecacb7) [docs] Add FS operations for ADLS client via Hue shell
* [eec293cade](https://github.com/cloudera/hue/commit/eec293cade) [raz_adls] Add append and flush operation mapping
* [43f67aaca6](https://github.com/cloudera/hue/commit/43f67aaca6) [docker] Upgrade from Python 3.6 to 3.8
* [3c0d3a9815](https://github.com/cloudera/hue/commit/3c0d3a9815) GH-2370 Hue Login Failed attempt should not expose bind_dn into the Login screen (asnaik) (#2506)
* [91609bdadf](https://github.com/cloudera/hue/commit/91609bdadf) [raz_adls] Add create and delete operations mapping
* [3f0665074c](https://github.com/cloudera/hue/commit/3f0665074c) [raz_adls] Add RAZ req mapping and update tests  (#2499)
* [6880bb2436](https://github.com/cloudera/hue/commit/6880bb2436) [raz] Check when RAZ call doesn't send response (#2497)
* [b081f84760](https://github.com/cloudera/hue/commit/b081f84760) [api] Also lookup for query in snippet in risk call
* [5a8ddcfc33](https://github.com/cloudera/hue/commit/5a8ddcfc33) [importer] Prepare import from a Kafka Topic into a Table
* [0e3b21e5dd](https://github.com/cloudera/hue/commit/0e3b21e5dd) [ci] Fix commit message max lenght check
* [c1cf3fc5b8](https://github.com/cloudera/hue/commit/c1cf3fc5b8) [docs] Improve GitHub CLI help
* [a0032fbb1a](https://github.com/cloudera/hue/commit/a0032fbb1a) [docs] Refresh help on how to get started contributing
* [f9712f89e4](https://github.com/cloudera/hue/commit/f9712f89e4) When using SQLServer JDBC for interpreters, the TABLE_COMMENT, COLUMN_COMMENT from the INFORMATION_SCHEMA table and column does not exist and LIMIT 100 also will not work instead need to use TOP 100 (#2493)
* [9a666b8ac1](https://github.com/cloudera/hue/commit/9a666b8ac1) [oozie] hive-site.xml created for spark action has 700 which causes an issue when the shared workflow is copied by user b (#2484)
* [d90cf16d2f](https://github.com/cloudera/hue/commit/d90cf16d2f) Impala daemon_api_password_script was not being used when set as it looks for only daemon_api_password (#2483)
* [ad8358d427](https://github.com/cloudera/hue/commit/ad8358d427) [raz] Do not enable S3 in Azure env (#2489)
* [5f1fe5c0a7](https://github.com/cloudera/hue/commit/5f1fe5c0a7) [py2] Rebase to phoenix 1.1.0
* [e297144957](https://github.com/cloudera/hue/commit/e297144957) [py3] Rebase to phoenix 1.1.0
* [961c310525](https://github.com/cloudera/hue/commit/961c310525) [docker] Remove ES sqlalchemy plugin
* [a8bf576a92](https://github.com/cloudera/hue/commit/a8bf576a92) [api] Remove some of the duplicate /api prefixes in the urls
* [874b5dc240](https://github.com/cloudera/hue/commit/874b5dc240) [editor] Revert deletion of sqlStatementsParser.jison
* [4e65757971](https://github.com/cloudera/hue/commit/4e65757971) [api] First pass on porting metadata API
* [4c4dd0529a](https://github.com/cloudera/hue/commit/4c4dd0529a) [frontend] Bump the NPM version for API url update
* [cc21c4bac0](https://github.com/cloudera/hue/commit/cc21c4bac0) [api] Replace old analyser URLs with public API
* [8846d432ed](https://github.com/cloudera/hue/commit/8846d432ed) [importer] adding dropping col feature for small local file
* [d47d241398](https://github.com/cloudera/hue/commit/d47d241398) [frontend] Bump the NPM version
* [18a6defa82](https://github.com/cloudera/hue/commit/18a6defa82) [editor] Fix missing predict check for optimizer type
* [0c901032f9](https://github.com/cloudera/hue/commit/0c901032f9) [editor] Fix incorrect tooltip for editor highlighting
* [e82af96bb9](https://github.com/cloudera/hue/commit/e82af96bb9) [editor] Fix asterisk expansion of selected columns
* [1d5d21eec3](https://github.com/cloudera/hue/commit/1d5d21eec3) [editor] Enable control of editor location highlighting types for the web component
* [61f2e76420](https://github.com/cloudera/hue/commit/61f2e76420) Issue #2481 - Fix Python 3 compatibility issue in Table Browser Import.
* [061951ddc7](https://github.com/cloudera/hue/commit/061951ddc7) [jwt] Fix response for pubilc key server request (#2474)
* [b0157af231](https://github.com/cloudera/hue/commit/b0157af231) [adls] Fix Python style issues
* [78d7b7856f](https://github.com/cloudera/hue/commit/78d7b7856f) [azure] Bump ADLS API version to support latest SAS
* [96d62d94c4](https://github.com/cloudera/hue/commit/96d62d94c4) [docs] Promote more how to run the unit tests
* [5e8dd9692a](https://github.com/cloudera/hue/commit/5e8dd9692a) Shorten lines exceeding 140
* [54fa12193d](https://github.com/cloudera/hue/commit/54fa12193d) Fix asserts compatible with python3
* [2d84e1500c](https://github.com/cloudera/hue/commit/2d84e1500c) [ci] Fix grep argument to unblock Python linting
* [c920adb962](https://github.com/cloudera/hue/commit/c920adb962) [jwt] Add USE_THRIFT_HTTP_JWT config in desktop/conf (#2472)
* [d0aa789959](https://github.com/cloudera/hue/commit/d0aa789959) [fs] ADLS default configuration URL is incorrect
* [df968cb5f8](https://github.com/cloudera/hue/commit/df968cb5f8) [raz] Add resourceOwner in RAZ ADLS request
* [c99497114d](https://github.com/cloudera/hue/commit/c99497114d) [raz] Raise 503 exception for no SAS token and cleaner tests
* [c5478f91e1](https://github.com/cloudera/hue/commit/c5478f91e1) [jwt] Fetch RSA public key from key_server (#2445)
* [81a3082b59](https://github.com/cloudera/hue/commit/81a3082b59) [raz] Add test for no SAS token in RAZ ADLS response
* [0b658e2cbd](https://github.com/cloudera/hue/commit/0b658e2cbd) [raz] Append SAS token only if present in response
* [b945c7721f](https://github.com/cloudera/hue/commit/b945c7721f) [jwt] Add request path to help debug API calls (#2464)
* [1dde62bee0](https://github.com/cloudera/hue/commit/1dde62bee0) [raz] Fix ADLS SAS token appending in URLs (#2463)
* [c843c7a8f7](https://github.com/cloudera/hue/commit/c843c7a8f7) [connector] correcting the name form 'kafka sql' to 'ksql'
* [0a5bc96b84](https://github.com/cloudera/hue/commit/0a5bc96b84) [frontend] Bump the NPM version
* [b32adccfa2](https://github.com/cloudera/hue/commit/b32adccfa2) [frontend] Enabled predict typeahead when connector optimizer is set to api
* [11b89004f9](https://github.com/cloudera/hue/commit/11b89004f9) Allow /api/token/auth can create user or make it active when auto login enabled (#2420)
* [2faf750771](https://github.com/cloudera/hue/commit/2faf750771) [jwt] Fix DummyCustomAuthentication class comments (#2461)
* [589358d0d5](https://github.com/cloudera/hue/commit/589358d0d5) [jwt] Allow developers test API calls without token in local dev env (#2460)
* [7b89ca04b1](https://github.com/cloudera/hue/commit/7b89ca04b1) [docs] Clarify when json POST data in API calls will work
* [4a901ca04d](https://github.com/cloudera/hue/commit/4a901ca04d) [core] Avoid old Hue 3 warning for API calls
* [35dd83abd9](https://github.com/cloudera/hue/commit/35dd83abd9) [auth] More explicit debug message when skipping cluster middleware
* [51c9164941](https://github.com/cloudera/hue/commit/51c9164941) [core] Harmonize the main ini file to be indented consistently
* [e132083856](https://github.com/cloudera/hue/commit/e132083856) add-support-trino
* [03609c028c](https://github.com/cloudera/hue/commit/03609c028c) [editor] Convert the mako syntax drop down to Vue and add it to the editor web component
* [8d8febc9e3](https://github.com/cloudera/hue/commit/8d8febc9e3) [docs] Correct connector API examples
* [ec2271d0f5](https://github.com/cloudera/hue/commit/ec2271d0f5) [filebrowser] disabling the 'Open In Importer' option for folder
* [0dadf3e8c1](https://github.com/cloudera/hue/commit/0dadf3e8c1) Open file with 'w' if python version is 3, else 'w+b'
* [2e6e13487d](https://github.com/cloudera/hue/commit/2e6e13487d) Change tempfile open mode to 'w'
* [bbd2758d22](https://github.com/cloudera/hue/commit/bbd2758d22) [frontend] Improve worker registration to support worker usage in the web components
* [93525b2143](https://github.com/cloudera/hue/commit/93525b2143) [docs] Reference to the Connector API from the config page
* [fd7095b6fb](https://github.com/cloudera/hue/commit/fd7095b6fb) [docs] Clarify more about Presto and Trino configs
* [36f850807a](https://github.com/cloudera/hue/commit/36f850807a) [sql] Split Presto and Trino in their own dialect
* [703a8b14be](https://github.com/cloudera/hue/commit/703a8b14be) [docs] Detail first hand how to authenticate for using the API
* [435d05ff0a](https://github.com/cloudera/hue/commit/435d05ff0a) Change impersonation to use principal_username
* [7486bed069](https://github.com/cloudera/hue/commit/7486bed069) [filebrowser] Prevent bucket listing when RAZ is enabled
* [fb5541163b](https://github.com/cloudera/hue/commit/fb5541163b) [jwt] Refactor custom JWT authentication config (#2438)
* [0135bfe563](https://github.com/cloudera/hue/commit/0135bfe563) [oidc] Apply fix for the login permissions issue so users are added to default group
* [c4822b577b](https://github.com/cloudera/hue/commit/c4822b577b) [oidc] Fix OIDC login issue when using Hue built with Python 3
* [c18f331510](https://github.com/cloudera/hue/commit/c18f331510) [blog] phoenix importer integration
* [b36c26ab93](https://github.com/cloudera/hue/commit/b36c26ab93) [filebrowser] removing extra whitespace between the path
* [a4615aba76](https://github.com/cloudera/hue/commit/a4615aba76) [blog] adding link to importer and example for copy path
* [18995d5705](https://github.com/cloudera/hue/commit/18995d5705) combining the code for localfile and remote file for phoenix
* [45d42a3c06](https://github.com/cloudera/hue/commit/45d42a3c06) [importer] integrating phoenix importer for a CSV file
* [65602ea360](https://github.com/cloudera/hue/commit/65602ea360) Set request variable when using LDAP authentication
* [078d4fe0fb](https://github.com/cloudera/hue/commit/078d4fe0fb) [create_session] Remove /notebook/api/create_session from not login and allowed already
* [0fc8c439d7](https://github.com/cloudera/hue/commit/0fc8c439d7) [blog] Using the Object Storage REST API
* [df9793342d](https://github.com/cloudera/hue/commit/df9793342d) [frontend] Upgrade Vue to 3.2
* [8e31a2aa30](https://github.com/cloudera/hue/commit/8e31a2aa30) [docs] Add proper links to the API pages
* [fef27f478a](https://github.com/cloudera/hue/commit/fef27f478a) [raz] Add test condition to check for S3 request params (#2423)
* [35d48b6758](https://github.com/cloudera/hue/commit/35d48b6758) [raz_s3] Change 'Accept-Encoding' request header to type 'str'
* [fbb4da1f98](https://github.com/cloudera/hue/commit/fbb4da1f98) [importer] removing 'Search index' option from drop down menu for 'manual' setup
* [07ae543409](https://github.com/cloudera/hue/commit/07ae543409) [blog] adding blog post for open in importer and copy path options in filebrowser
* [bf38cbc190](https://github.com/cloudera/hue/commit/bf38cbc190) [docs] Add get_config public API
* [ddbc93cc89](https://github.com/cloudera/hue/commit/ddbc93cc89) [jwt] Add verification config flag for custom JWT Authentication (#2414)
* [b6d738e0a9](https://github.com/cloudera/hue/commit/b6d738e0a9) [filebrowser] expanding the dragenter area so that we can drop file anywhere
* [bce88a2c85](https://github.com/cloudera/hue/commit/bce88a2c85) Invalid attribute syntax in Hue find_groups_filter (#2407)
* [da153b6f83](https://github.com/cloudera/hue/commit/da153b6f83) [docs] Refactor public REST APIs curl commands
* [e250e80ad6](https://github.com/cloudera/hue/commit/e250e80ad6) [filechooser] adding remote_storage_home in filechooser
* [0170b4a914](https://github.com/cloudera/hue/commit/0170b4a914) [importer] adding column name check in the importer
* [c6ed13cc57](https://github.com/cloudera/hue/commit/c6ed13cc57) [docs] Remove ADLS broken link from connector storage section
* [34ae4e4402](https://github.com/cloudera/hue/commit/34ae4e4402) [create_session] Remove public API POST view from notebook_api
* [89f0eba13a](https://github.com/cloudera/hue/commit/89f0eba13a) [importer] converting any char other than A-Za-z0-9 to '_'
* [f1f9f84685](https://github.com/cloudera/hue/commit/f1f9f84685) [auto_login] Auto create 'hue' user for auto_login config flag (#2402)
* [d9b127f8d8](https://github.com/cloudera/hue/commit/d9b127f8d8) [raz] Auto-configure default FS from core-site.xml (#2396)
* [e5a16076bf](https://github.com/cloudera/hue/commit/e5a16076bf) [doc] removing the extra quotation mark
* [4fb10db89f](https://github.com/cloudera/hue/commit/4fb10db89f) [docs] Add reference to PyHive issue
* [e29bc1dce5](https://github.com/cloudera/hue/commit/e29bc1dce5) update trino connector configuration with note about alternate headers
* [f6382b7649](https://github.com/cloudera/hue/commit/f6382b7649) [aws] Standardize as lower case s3a:// prefix to avoid corner cases
* [4568d96e03](https://github.com/cloudera/hue/commit/4568d96e03) [raz] Auto detect ADLS cluster name from config file (#2391)
* [c006903203](https://github.com/cloudera/hue/commit/c006903203) [direct_importer] adding blog post for zero click importer]
* [b80a403b67](https://github.com/cloudera/hue/commit/b80a403b67) [indexer] Switch to single quotes for TBLPROPERTIES values
* [adb20c6639](https://github.com/cloudera/hue/commit/adb20c6639) [importer] 'NoneType' object has no attribute 'netnormpath' because of request.fs is not defined
* [85e0a16179](https://github.com/cloudera/hue/commit/85e0a16179) [Django_axes_warning] adding axes beckend and middleware
* [7152fe5a1f](https://github.com/cloudera/hue/commit/7152fe5a1f) [raz] Retrieve Raz server URL via ADLS config property in core-site.xml
* [9ae6fd9d8e](https://github.com/cloudera/hue/commit/9ae6fd9d8e) [doc] adding Document small file import API
* [7223599049](https://github.com/cloudera/hue/commit/7223599049) [core] changing 'is' to '==' as it was syntax error
* [f8e15dc921](https://github.com/cloudera/hue/commit/f8e15dc921) [filebrowser] making drag and drop area absolute because we cannot drop a file in left assit going through fb
* [94cf663745](https://github.com/cloudera/hue/commit/94cf663745) [importer] auto table creation failing for waiting 500ms so using 'waitforobservale' function for submit
* [9fda4bab13](https://github.com/cloudera/hue/commit/9fda4bab13) [catalog] Pick-up according dialect when opening Table from popover
* [18b0ff24f5](https://github.com/cloudera/hue/commit/18b0ff24f5) Issue #2379 - Fix JSON decode error with Oozie action submission in Python 3.x environments.
* [8491241071](https://github.com/cloudera/hue/commit/8491241071) [raz] Update Raz Http Client to include actual SAS token (#2377)
* [1da17c44ed](https://github.com/cloudera/hue/commit/1da17c44ed) [raz] Raz Client for ADLS to submit proper requests to getback SAS token (#2362)
* [048b8b8607](https://github.com/cloudera/hue/commit/048b8b8607) Importer fails with READ permission due to IMPALA-10272. (#2374)
* [b0884a7911](https://github.com/cloudera/hue/commit/b0884a7911) [doc] adding the details of importer_submit api
* [3a5f6c0594](https://github.com/cloudera/hue/commit/3a5f6c0594) [filebrowser] Prevent call to HDFS happening when deleting a S3 dir
* [ffb4fe8a08](https://github.com/cloudera/hue/commit/ffb4fe8a08) [filebrowser] adding 'open in importer' button in filebrowser
* [a5e9f2d55d](https://github.com/cloudera/hue/commit/a5e9f2d55d) [frontend] Fix import path in catalog/api
* [413b55835a](https://github.com/cloudera/hue/commit/413b55835a) [aws] Fix deleting directory action
* [d8e436dc08](https://github.com/cloudera/hue/commit/d8e436dc08) [libs] Fix gunicorn and gevent lib compatibility and dependency on six
* [2380129c75](https://github.com/cloudera/hue/commit/2380129c75) [docs] More helpful connector API descriptions
* [8389ec7749](https://github.com/cloudera/hue/commit/8389ec7749) [libs] Bump django celery result to latest
* [ee81afa5e0](https://github.com/cloudera/hue/commit/ee81afa5e0) [api] adding importer_submit api to public operation
* [6b6c9396c8](https://github.com/cloudera/hue/commit/6b6c9396c8) [api] Store jwt access token in userprofile
* [1f2081bcd7](https://github.com/cloudera/hue/commit/1f2081bcd7) [api] Change JWT field username -> userId
* [a14d1b00f2](https://github.com/cloudera/hue/commit/a14d1b00f2) [api] Update JWT token decoding unit tests
* [f0fa89f0ea](https://github.com/cloudera/hue/commit/f0fa89f0ea) [jwt] Implement custom JWT Authentication and update UTs
* [8d8f319ae4](https://github.com/cloudera/hue/commit/8d8f319ae4) [sql] Surface exception message on login failure
* [9674653881](https://github.com/cloudera/hue/commit/9674653881) [docs] More information on how to configure via the connector UI
* [e722a05a37](https://github.com/cloudera/hue/commit/e722a05a37) [docs] Simplify Query API titles
* [fd8cdf7dcd](https://github.com/cloudera/hue/commit/fd8cdf7dcd) [raz] Inject proper username in case it is not present
* [1fdb800343](https://github.com/cloudera/hue/commit/1fdb800343) [docs] Refresh the top description of the README
* [e9cc9fc930](https://github.com/cloudera/hue/commit/e9cc9fc930) [filebrowser] adding delete button to the action group when is_trash_enabled is false
* [c953de6fa6](https://github.com/cloudera/hue/commit/c953de6fa6) [django_warning] NullBooleanField is deprecated
* [8c596bcd2a](https://github.com/cloudera/hue/commit/8c596bcd2a) [api] Skeleton of custom JWT authentication
* [6740f26a97](https://github.com/cloudera/hue/commit/6740f26a97) [CSS] File browser path breadcrumb setting 0 padding to the right of name
* [7801f704b4](https://github.com/cloudera/hue/commit/7801f704b4) [fb] Compressing multiple files or folder causing compression error (#2340)
* [21d3095a4a](https://github.com/cloudera/hue/commit/21d3095a4a) [docs] Remove un-needed content type header in REST API
* [372d65896c](https://github.com/cloudera/hue/commit/372d65896c) [docker] Also specify Flower pip version in Py2
* [12b148f8f5](https://github.com/cloudera/hue/commit/12b148f8f5) [docker] Keep flower compatible with celery v4
* [d619411d7f](https://github.com/cloudera/hue/commit/d619411d7f) [File Browser] Providing buttom 'Copy Path' for easy copy of S3 URL path in File Browser
* [10f3906bcc](https://github.com/cloudera/hue/commit/10f3906bcc) [docs] Fix public API path
* [cbbaea6b80](https://github.com/cloudera/hue/commit/cbbaea6b80) [docs] Improve enabling and adding connector section
* [d22ae85e5f](https://github.com/cloudera/hue/commit/d22ae85e5f) HiveServerClient: Set schemaName to None for sparksql
* [e8f4365184](https://github.com/cloudera/hue/commit/e8f4365184) [docs] Update /connector docs (#2330)
* [1c5884023b](https://github.com/cloudera/hue/commit/1c5884023b) [docs] Update Python API about Users
* [7d8f7389bc](https://github.com/cloudera/hue/commit/7d8f7389bc) [api] Port /connector APIs to public
* [894a72a670](https://github.com/cloudera/hue/commit/894a72a670) [organization] Allow to create super user with default org
* [e09346326c](https://github.com/cloudera/hue/commit/e09346326c) [editor] making absolue area for drag and drop of sql file in editor
* [d1d25b9da7](https://github.com/cloudera/hue/commit/d1d25b9da7) [importer_direct_upload] adding feature of automatic table creation when we drag and drop the local file in left assist
* [e9f33757ab](https://github.com/cloudera/hue/commit/e9f33757ab) [pypi] Bump dateutil to 2.8.1
* [d8dd42053b](https://github.com/cloudera/hue/commit/d8dd42053b) [website] Use latest Sql Scratchpad lib on home page
* [493abc48e6](https://github.com/cloudera/hue/commit/493abc48e6) [docker] Adding impyla sql alchemy dialect
* [2a1aaf16a4](https://github.com/cloudera/hue/commit/2a1aaf16a4) [docs] Update /analyze and wrong credentials in REST API section (#2320)
* [61f7ce9ad6](https://github.com/cloudera/hue/commit/61f7ce9ad6) [api] Port impala/api/analyze to public API (#2316)
* [fa0df25ed7](https://github.com/cloudera/hue/commit/fa0df25ed7) [release] Publish gethue@4.10.5
* [b5349387ce](https://github.com/cloudera/hue/commit/b5349387ce) [sqls] Avoid JSON.bigdataParse is not a function on result display
* [7d016eb23a](https://github.com/cloudera/hue/commit/7d016eb23a) [api] Initial test for SQL execute API
* [a1c35ee6d2](https://github.com/cloudera/hue/commit/a1c35ee6d2) [docs] Update /get_history API docs
* [4eab25ba46](https://github.com/cloudera/hue/commit/4eab25ba46) [frontend] Update /get_history public API in Js code
* [5a47dc78c8](https://github.com/cloudera/hue/commit/5a47dc78c8) [api] Port /notebook/api/get_history to public API
* [a5dfe29031](https://github.com/cloudera/hue/commit/a5dfe29031) Revert "[Django_warning]  NullBooleanField is deprecated. Support for it (except in historical migrations) will be removed in Django 4.0."
* [231527dd70](https://github.com/cloudera/hue/commit/231527dd70) correcting the guess apis in doc
* [c58b0a0caf](https://github.com/cloudera/hue/commit/c58b0a0caf) circular import error for py2
* [b9b2db8c68](https://github.com/cloudera/hue/commit/b9b2db8c68) ImportError: cannot import name '_get_interpreter_from_dialect' from partially initialized module 'desktop.api_public' (most likely due to a circular import)
* [9e590efc9c](https://github.com/cloudera/hue/commit/9e590efc9c) [api] Add /guess_format and /guess_field_types public operation
* [28ce578dd8](https://github.com/cloudera/hue/commit/28ce578dd8) [frontend] Bump the NPM version to 4.10.4
* [07ec333d1b](https://github.com/cloudera/hue/commit/07ec333d1b) [frontend] Switch to using the new API endpoints for describe, sample check_status, cancel_statement and fetch_result_data
* [626fcd2581](https://github.com/cloudera/hue/commit/626fcd2581) [frontend] Prevent error on undefined executable in the ExecutionAnalysisPanel
* [4f12582ca5](https://github.com/cloudera/hue/commit/4f12582ca5) [api] Port /sample APIs to public (#2294)
* [b123500100](https://github.com/cloudera/hue/commit/b123500100) [Django_warning]  NullBooleanField is deprecated. Support for it (except in historical migrations) will be removed in Django 4.0.
* [0f4ba4c5c5](https://github.com/cloudera/hue/commit/0f4ba4c5c5) [docs] Update REST API docs (#2303)
* [33f01b95db](https://github.com/cloudera/hue/commit/33f01b95db) [api] Patch /autocomplete public API for snippet
* [785b070662](https://github.com/cloudera/hue/commit/785b070662) [frontend] Bump the NPM version to 4.10.3
* [4e395545a2](https://github.com/cloudera/hue/commit/4e395545a2) [frontend] Merge Executable into SqlExecutable
* [ea7de2e833](https://github.com/cloudera/hue/commit/ea7de2e833) [api] No need to add operationId again in django_request.POST
* [4fb34a60e7](https://github.com/cloudera/hue/commit/4fb34a60e7) [api] Refactor _patch_operation_id_request in public APIs
* [5012908b62](https://github.com/cloudera/hue/commit/5012908b62) [api] Prefix editor view names
* [a00693e386](https://github.com/cloudera/hue/commit/a00693e386) [Django_warning] Port to avoid Django DEFAULT_AUTO_FIELD warnings
* [3bf8ce3fa0](https://github.com/cloudera/hue/commit/3bf8ce3fa0) [api] Port /describe APIs to public (#2293)
* [8d7b40d3f7](https://github.com/cloudera/hue/commit/8d7b40d3f7) [frontend] Update jasmine tests
* [0b5522c5d4](https://github.com/cloudera/hue/commit/0b5522c5d4) [frontend] Bump NPM version to 4.10.2
* [3d749397d4](https://github.com/cloudera/hue/commit/3d749397d4) [frontend] Add execution logs to the SQL scratchpad component
* [ce427b5f36](https://github.com/cloudera/hue/commit/ce427b5f36) [frontend] Add a sql-text web component to render formatted SQL
* [33bec79deb](https://github.com/cloudera/hue/commit/33bec79deb) [frontend] Add an execution-analysis web component for logs and errors
* [63abe58285](https://github.com/cloudera/hue/commit/63abe58285) [frontend] Gather all web component definitions under /webComponents
* [5cd428c67e](https://github.com/cloudera/hue/commit/5cd428c67e) [docs] Clarify more API upload and download parameters
* [fc4b21475d](https://github.com/cloudera/hue/commit/fc4b21475d) [api] Add /storage/upload public operation
* [7523e04157](https://github.com/cloudera/hue/commit/7523e04157) [api] Namespace view a file API
* [8f364a4128](https://github.com/cloudera/hue/commit/8f364a4128) [api] Add /storage/download public operation
* [9f6548d8aa](https://github.com/cloudera/hue/commit/9f6548d8aa) [importer] Do not hardcode Flink interpreter id
* [b28825bf46](https://github.com/cloudera/hue/commit/b28825bf46) [blog] Improve style formatting of SAS blog post
* [b195fb3df0](https://github.com/cloudera/hue/commit/b195fb3df0) [ksql] Do not hardcode connector id in metadata API
* [7284f55808](https://github.com/cloudera/hue/commit/7284f55808) Fix bug in spark shell when used with hive
* [7c8e19ec80](https://github.com/cloudera/hue/commit/7c8e19ec80) [docs] Example of Python API for ADLS
* [4ca5cb9d95](https://github.com/cloudera/hue/commit/4ca5cb9d95) [docs] Improve Python shell documentation for accessing the storages
* [2475163b20](https://github.com/cloudera/hue/commit/2475163b20) [blog] Adding blog post on Azure SAS tokens and Storage REST API
* [5caeba886a](https://github.com/cloudera/hue/commit/5caeba886a) [py3] Upgrade ipython module to not break the shell command
* [7efbb87f3d](https://github.com/cloudera/hue/commit/7efbb87f3d) [adls] Fix styling to make actuall REST call more explicit
* [d241595856](https://github.com/cloudera/hue/commit/d241595856) [raz] Remove left out print statement
* [f6ad77498d](https://github.com/cloudera/hue/commit/f6ad77498d) [lib] Disable auto URL quoting in RazHttpClient
* [ed3652cbb8](https://github.com/cloudera/hue/commit/ed3652cbb8) [abfs] Port get_url tests to the new signature
* [dccc557608](https://github.com/cloudera/hue/commit/dccc557608) [abfs] Hook-in Raz client into HttpClient
* [2cd6183778](https://github.com/cloudera/hue/commit/2cd6183778) [abfs] Go through Raz when enabled
* [e9175a9617](https://github.com/cloudera/hue/commit/e9175a9617) [abfs] Do not try to set credentials headers when Raz is on
* [370ae2eb1b](https://github.com/cloudera/hue/commit/370ae2eb1b) [abfs] Do not require credentials in client when Raz is on
* [99dead06b6](https://github.com/cloudera/hue/commit/99dead06b6) [abfs] Do not require Hue admin privileges for access if RAZ is enabled
* [ce1786a3fd](https://github.com/cloudera/hue/commit/ce1786a3fd) [fs] Fix left out Python 2 url lib import
* [ac9ed65e6f](https://github.com/cloudera/hue/commit/ac9ed65e6f) [aws] Do not enabled S3 when Azure Raz is enabled
* [cb8c4ed700](https://github.com/cloudera/hue/commit/cb8c4ed700) [raz] Nicer error message when turned on without a proper API URL
* [fac608fee6](https://github.com/cloudera/hue/commit/fac608fee6) [abfs] Turn on when cluster config and RAZ are on
* [b7d395af69](https://github.com/cloudera/hue/commit/b7d395af69) [abfs] Small typo fixes
* [53439a24c1](https://github.com/cloudera/hue/commit/53439a24c1) Hue audit logs are no longer being collected if Nav is not in use. (#2277)
* [9286bcd834](https://github.com/cloudera/hue/commit/9286bcd834) Added mapping of LDAP userID: 12345678 to OS user: a2345678 using python PWD module (#2276)
* [e76a5d1d1f](https://github.com/cloudera/hue/commit/e76a5d1d1f) [docs] Minor typo fixes in User section
* [47fe5e1c0f](https://github.com/cloudera/hue/commit/47fe5e1c0f) [editor] Update saved query snapshot
* [5e82000d97](https://github.com/cloudera/hue/commit/5e82000d97) [editor] Use gist link input field for sharing saved query
* [f748f04bcc](https://github.com/cloudera/hue/commit/f748f04bcc) Select of unicode character fails with encoding issue due to changes made via CDPD-22129 (#2269)
* [8884e7971f](https://github.com/cloudera/hue/commit/8884e7971f) [aws] Avoid bulk delete on empty directory
* [af8881cc05](https://github.com/cloudera/hue/commit/af8881cc05) [jb] Fix broken Impala profile download action
* [8e736670e5](https://github.com/cloudera/hue/commit/8e736670e5) [jb] Fix broken page after reloading the Impala query details in the Job Browser
* [48c3021bc7](https://github.com/cloudera/hue/commit/48c3021bc7) [importer_direct_upload] filtering the is_sql interpreters only
* [f54d0e23fa](https://github.com/cloudera/hue/commit/f54d0e23fa) [core] Disable Hue 4 Welcome Tour display
* [f167efd6b1](https://github.com/cloudera/hue/commit/f167efd6b1) [importer_direct_upload] handling the empty rows in csv file
* [67fafa91a1](https://github.com/cloudera/hue/commit/67fafa91a1) [aws] Avoid bulk delete if there is only one key
* [916b0888bc](https://github.com/cloudera/hue/commit/916b0888bc) [core] Update package-lock json with 4.10
* [d24e8ecf7c](https://github.com/cloudera/hue/commit/d24e8ecf7c) [slack] Update install link UT with public api namespace
* [5918f2017a](https://github.com/cloudera/hue/commit/5918f2017a) To map userID: 12345678 to OS user: a2345678 using python PWD module when there is pam service like Centrify configured at OS level (#2261)
* [58ebb6c647](https://github.com/cloudera/hue/commit/58ebb6c647) [core] Fix skipped pip install if system python has same libs preinstalled (#2258)
* [d44aff80ce](https://github.com/cloudera/hue/commit/d44aff80ce) [docs] Update Mac installation section in dependencies (#2260)
* [9999df6b8b](https://github.com/cloudera/hue/commit/9999df6b8b) [docs] localized Hue 4.10 blog into Japanese
* [f9665e4076](https://github.com/cloudera/hue/commit/f9665e4076) [docs] localized 29,May 2021 blogs into Japanese
* [3b7b720daf](https://github.com/cloudera/hue/commit/3b7b720daf) [docs] localized May 2021 blogs into Japanese
* [5fd9747f95](https://github.com/cloudera/hue/commit/5fd9747f95) [raz] Propagate the renewer user for DWX (#2256)
* [c956413504](https://github.com/cloudera/hue/commit/c956413504) [docs] Explain better the API authentication
* [67efd52582](https://github.com/cloudera/hue/commit/67efd52582) [raz] Propagate the doAs user name to Raz
* [f4c92b601b](https://github.com/cloudera/hue/commit/f4c92b601b) [fb] Refactor to have nomalization path logic into one place
* [3e60d9fe89](https://github.com/cloudera/hue/commit/3e60d9fe89) [docs] Fix minor typos in Slack install section
* [ab441e5a15](https://github.com/cloudera/hue/commit/ab441e5a15) [docs] Update installation link redirect from Slack concept section
* [f08d921ac2](https://github.com/cloudera/hue/commit/f08d921ac2) [aws] Pickup the default host provided via Raz config
* [fb44d6e6ad](https://github.com/cloudera/hue/commit/fb44d6e6ad) [raz] Explicitly corce has Raz url to boolean
* [0130cd154a](https://github.com/cloudera/hue/commit/0130cd154a) [raz] Add series of test to check the auto configuration
* [998c7c3ac7](https://github.com/cloudera/hue/commit/998c7c3ac7) [s3] Do not require Hue admin privileges for FS access if RAZ is enabled
* [d7dac58bb5](https://github.com/cloudera/hue/commit/d7dac58bb5) [raz] Try to guess default home storage
* [ed0e627bd4](https://github.com/cloudera/hue/commit/ed0e627bd4) [raz] Automatically set host and check env credential values
* [e024246bf0](https://github.com/cloudera/hue/commit/e024246bf0) [raz] Auto turn on when the Raz API is specified
* [d552ae0067](https://github.com/cloudera/hue/commit/d552ae0067) [raz] Auto detect s3 bucket and region from config file
* [6c8cf19c6e](https://github.com/cloudera/hue/commit/6c8cf19c6e) [raz] Auto detect cluster name from config file
* [0d6812679f](https://github.com/cloudera/hue/commit/0d6812679f) [raz] Auto detect API url from config file
* [c88c674537](https://github.com/cloudera/hue/commit/c88c674537) [docs] Adjust the scratchpad for Hugo modal usage
* [d976231355](https://github.com/cloudera/hue/commit/d976231355) [docs] Refresh gethue landing page and introduce scratchpad
* [5c72c84816](https://github.com/cloudera/hue/commit/5c72c84816) [catalog] Don't send the database on drop as it prevents dropping of databases
* [ca0630c62d](https://github.com/cloudera/hue/commit/ca0630c62d) [frontend] Prevent editor from failing to initialize if acePredict throws an error
* [071b684bf1](https://github.com/cloudera/hue/commit/071b684bf1) [assist] Only show the + in the DB assist when the importer browser is present in the config
* [afe4f07319](https://github.com/cloudera/hue/commit/afe4f07319) [importer_direct_upload] file storage location is changed to tempfile.NamedTemporaryFile
* [8d53fa8e7b](https://github.com/cloudera/hue/commit/8d53fa8e7b) [core] Fix ur' prefix strings to be both Py2 and 3 compatible
* [a0af6b827b](https://github.com/cloudera/hue/commit/a0af6b827b) [core] Fix Python3 incompatibility in mako macros
* [788e4774b0](https://github.com/cloudera/hue/commit/788e4774b0) [connectors] Set HDFS port to standard default
* [52e494bf40](https://github.com/cloudera/hue/commit/52e494bf40) [docs] Skip building old doc sections
* [b192941872](https://github.com/cloudera/hue/commit/b192941872) [ci] Add make prod to the Python 3 runs
* [3a00dcbed9](https://github.com/cloudera/hue/commit/3a00dcbed9) Bump django from 3.2.3 to 3.2.4 in /desktop/core
* [fbc99b2837](https://github.com/cloudera/hue/commit/fbc99b2837) [build] Remove OS restriction for npm install of fsevent


### Contributors

This Hue release is made possible thanks to the contribution from:

* 10sr
* Aaron Newton
* Aaron Peddle
* Aaron T. Myers
* Abraham Elmahrek
* Aditya Acharya
* Adrian Yavorskyy
* Ajay Jadhav
* Akhil Naik
* Akhil S Naik
* Alex (posi) Newman
* Alex Breshears
* Alex Newman
* Aliaksei
* Alvin McNair
* Ambreen Kazi
* Amit Kabra
* Amit S
* Andrei Savu
* Andrew Bayer
* Andrew Yao
* Andy Braslavskiy
* Ann McCown
* Antonio Bellezza
* Ashu Pachauri
* Asnaik HWX
* Athithyaa Selvam
* Atupal
* Avindra Goolcharan
* Ayush Goyal
* Ben Bishop
* Ben Gooley
* Ben White
* Bhargava Kalathuru
* BirdZhang
* Bjorn Alm
* Björn Alm
* Bruce Mitchener
* Bruno Mahé
* Chris Conner
* Chris Stephens
* Christopher Conner
* Christopher McConnell
* Christopherwq Conner
* Craig Minihan
* Daehan Kim
* Derek Chen-Becker
* Diego Sevilla Ruiz
* Dominik Gehl
* Duncan Buck
* Eli Collins
* Emmanuel Bessah
* Enrico Berti
* Eric Chen
* Erick Tryzelaar
* Ewan Higgs
* Gabriel Machado
* Gilad Wolff
* Gleb Zhukov
* Grzegorz Kokosiński
* Guido Serra
* Harsh
* Harsh Gupta
* Harsh J
* Harshg999
* Hector Acosta
* Henry Robinson
* Hoai-Thu Vuong
* Igor Wiedler
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
* Jean-Francois Desjeans Gauthier
* Jenny Kim
* Joe Crobak
* Joey Echeverria
* Johan Ahlen
* Johan Åhlén
* Johan Åhlén
* John Murray
* Jon Natkins
* Jordan Moore
* Josh Walters
* Justin Bradfield
* Karissa McKelvey
* Kevin Risden
* Kevin Wang
* Khwunchai Jaengsawang
* Kostas Sakellis
* Lars Francke
* Li Jiahong
* Linden Hillenbrand
* Louis de Charsonville
* Luca
* Luca Natali
* Luca Toscano
* Luke Carmichael
* Mahesh Balakrishnan
* Marcus McLaughlin
* Mariusz Strzelecki
* Martin Grigorov
* Martin Traverso
* Martin Tzvetanov Grigorov
* Mathias Rangel Wulff
* Matías Javier Rossi
* Maulik Shah
* Max T
* Michael Prim
* Michal Ferlinski
* Michalis Kongtongk
* MoA
* Mobin Ranjbar
* Mykhailo Kysliuk
* Naoki Takezoe
* Nicolas Fouché
* Nicolas Landier
* Nidhi Bhat G
* NikolayZhebet
* Nils Braun
* OOp001
* Olaf Flebbe
* Oli Steadman
* Oren Mazor
* Pala M Muthaia Chettiar
* Patricia Sz
* Patrick Carlson
* Patrycja Szabłowska
* Paul Battaglia
* Paul McCaughtry
* Peter Slawski
* Philip Zeyliger
* Piotr Ackermann
* Prachi Poddar
* Prakash Ranade
* Prasad Mujumdar
* Priyanka Chheda
* Qi Xiao
* Raghunandana S K
* Rajat Garga
* Rajeshwari
* Reinaldo de Souza Jr
* Rentao Wu
* Renxia Wang
* ReshmaFegade2022
* Rick Bernotas
* Ricky Saltzer
* Robert Wipfel
* Romain
* Romain Rigaux
* Roman Shaposhnik
* Roohi
* Roohi Syeda
* Rui Pereira
* Sai Chirravuri
* Santiago Ciciliani
* Scott Kahler
* Sean Mackrory
* Shahab Tajik
* Shawarma
* Shawn Van Ittersum
* Shin So
* Shrijeet
* Shrijeet Paliwal
* Shuo Diao
* Siddhartha Sahu
* Simon Beale
* Simon Whittaker
* Simon van der Veldt
* Sreenath Somarajapuram
* Stefano Palazzo
* Stephanie Bodoff
* Suhas Satish
* Sungpeo Kook
* TAK LON WU
* TAKLON STEPHEN WU
* Tamas Sule
* Tatsuo Kawasaki
* Taylor Ainsworth
* Thai Bui
* Thomas Aylott
* Thomas Poepping
* Thomas Tauber-Marshall
* Tianjin Gu
* Todd Lipcon
* Tom Mulder
* Tomas Coufal
* Tone Lee
* Vadim Markovtsev
* VijayaKanchamreddy
* Vinay
* Wang, Xiaozhe
* Weixia
* Weixia Xu
* William Bourque
* Word
* Xavier Morera
* Xhxiong
* Xiao Kang
* Xingang Zhang
* Ying Chen
* Yixiao Lin
* Yoer
* Yuanhao
* Yuanhao Lu
* Yubi Lee
* Yuriy Hupalo
* Zach York
* Zachary York
* Zhang Bo
* Zhang Ruiqiang
* Zhihai Xu
* abec
* agl29
* aig
* airokey
* alheio
* alphaskade
* antbell
* arahuja
* ayush.goyal
* batou9150
* bc Wong
* bcwalrus
* bschell
* bwang
* byungnam
* cconner
* cmconner156
* cwalet
* dbeech
* denniszag
* dependabot[bot]
* e11it
* ebessah
* emmanuel
* fatherfox
* ganeshk
* gdgt
* gmsantos
* gnieto
* grundprinzip
* happywind
* hueadmin
* ihacku
* jdesjean
* jeff.melching
* jheyming
* jkm
* jojodaser
* krish
* linchan-ms
* linwukang
* lvziling
* maiha
* motta
* mrmrs
* oxpa
* pat white
* peddle
* penggongkui
* pkuwm
* rainysia
* raphi
* rdeva
* realslimstan777
* richardantal
* robrotheram
* rpoluri
* sachinunravel
* sandeepreddy3647
* sbaudoin
* shobull
* sky4star
* skyyws
* spaztic1215
* sreenaths
* stephbat
* tabraiz12
* theyaa
* thinker0
* tjphilpot
* todaychi
* travisle22
* van Orlov
* vinithra
* voyageth
* vybs
* weixia
* wilson
* xq262144
* ymping
* ywheel
* z-york
* z00484332
* zhang-jc
* zhengkai
* 小龙哥
* 王添
* 白菜
* 鸿斌
