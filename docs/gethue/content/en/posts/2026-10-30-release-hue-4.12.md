---
title:  Hue 4.12 with a new Storage Browser, Trino support and a new platform is out!
author: Hue Team
type: post
date: 2026-10-30T00:00:00+00:00
url: /blog/hue-4-12-storage-browser-trino/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
sf_page_title_style:
  - standard
sf_no_breadcrumbs:
  - 1
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_social_sharing:
  - 1
sf_related_articles:
  - 1
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4.12
  - Release

---

Hi Data Explorers,

Hue 4.12 is out! It is the first release since January 2023, with more than 890 commits from 36 contributors.

**Note: Hue 4.12 requires Python 3.11 and is built on Django 5.2. Read the [upgrade notes](https://docs.gethue.com/releases/release-notes-4.12.0/#upgrade-notes) before you upgrade from 4.11.**

### Summary

#### A new Storage Browser

The Storage Browser is rewritten as a React application. It works with HDFS, S3, ABFS, Google Storage and Apache Ozone:

* Browse, search and sort, with breadcrumbs and a path browser.
* View, preview and edit files, rename, copy, move and delete them, change the owner and permissions, compress and extract archives.
* Upload files by drag and drop. Uploads keep running in a queue while you navigate, and large files are sent in chunks.

Enable it with `enable_new_storage_browser=true` in the `[desktop]` section of the `hue.ini`. Learn more in [Browsing data](https://docs.gethue.com/user/browsing/).

#### Trino, Flink SQL and Kyuubi

* The **Trino** connector is overhauled: catalog browsing, autocomplete, explain, multiple statements, HTTPS basic authentication, `ssl_verify` and `trino_user` options. See [Integrating the Trino editor in Hue](https://gethue.com/blog/2024-06-26-integrating-trino-editor-in-hue-supporting-data-mesh-and-sql-federation/) and the [connector documentation](https://docs.gethue.com/administrator/configuration/connectors/#trino).
* The **Apache Flink** connector now uses the Flink SQL Gateway.
* **Apache Kyuubi** is available to query Spark SQL.

#### More storage options

* [Apache Ozone](https://gethue.com/blog/discover-the-power-of-apache-ozone-using-the-hue-file-browser/) and Google Cloud Storage in the file browsers.
* S3 is rebuilt on boto3 and supports S3-compatible object stores such as MinIO, Dell ECS and NetApp through the new `[[storage_connectors]]` configuration.

#### A documented public API

The public API is versioned under `/api/v1/`, with a Swagger UI at `/api/swagger`. It covers the storage operations, the logs, the configuration check and more. See the [REST API](https://docs.gethue.com/developer/api/rest/) documentation.

#### Editor, Job Browser and administration

* Autocomplete for CTEs, a `default_interpreter` option and floating-point results that keep their precision.
* An optional Celery task server for chunked uploads, an integrated Gunicorn log listener, TLS 1.3, IPv6 and SAML local logout.
* Admin pages (configuration, server logs and metrics) rewritten in React.

#### A new platform and a security hardening round

* Python 3.11, Django 5.2, Gunicorn 23 and Node.js 22.
* CVE fixes in the backend and frontend dependencies, stricter permissions on the configuration APIs, fixes for the local file access of the importers, Content Security Policy support and non-persistent session cookies.

Hue 4.12 has more than 890 commits. For a complete list, see the [release notes](https://docs.gethue.com/releases/release-notes-4.12.0/).

Go grab it and give it a spin!

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

</br>
</br>

Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Onwards!

Harsh from the Hue Team
