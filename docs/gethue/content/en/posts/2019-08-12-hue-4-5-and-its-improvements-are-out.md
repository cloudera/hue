---
title: Hue 4.5 and its improvements are out!
author: Hue Team
type: post
date: 2019-08-12T02:36:35+00:00
url: /hue-4-5-and-its-improvements-are-out/
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
  - Version 4
  # - Version 4.5
  - Release

---
Hi SQL Data Explorers,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 4.5!

<img class="" src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" alt="hue-logo" width="85" height="63" />

The focus of this release was to modularize the tech stack, improve SQL integrations and prepare major upcoming features.

This release comes with 660 commits and 150+ bug fixes! For all the changes, check out the [release notes][2].

They are several ways to give it a spin!

* [Tarball](https://cdn.gethue.com/downloads/hue-4.5.0.tgz) or [source][3]
* From <a href="https://github.com/cloudera/hue/tree/master/tools/docker">Docker Hub</a>
    ```
    docker pull gethue/4.5.0
    ```
* [demo.gethue.com][4]
* Kubernetes cluster
    ```
    helm repo add gethue https://helm.gethue.com
    helm repo update
    helm install hue gethue/hue
    ```

<a href="https://cdn.gethue.com/uploads/2019/08/hue_4.5.png"><img src="https://cdn.gethue.com/uploads/2019/08/hue_4.5.png" /></a>

Here is a list of the main improvements:

<div>
  <h2>
    SQL
  </h2>

  <ul>
    <li>
      <a href="https://gethue.com/realtime-catalog-search-with-hue-and-apache-atlas/">Apache Atlas integration and Catalog API</a>
    </li>
    <li>
      <a href="https://docs.gethue.com/administrator/configuration/editor/#hiv">Hive LLAP + Service discovery</a>
    </li>
    <li>
      <a href="https://gethue.com/built-in-hive-language-reference-in-the-sql-editor/">Hive language reference is built-in</a>
    </li>
    <li>
      <a href="https://gethue.com/sql-querying-apache-hbase-with-apache-phoenix/">HBase Phoenix querying example</a>
    </li>
  </ul>

  <h2>
    Interface
  </h2>

  <ul>
    <li>
      Left menu revamp
    </li>
    <li>
      Left assist panel aggregating storage (HDFS, ADLS, S3)
    </li>
    <li>
      <a href="https://gethue.com/2x-faster-page-load-time-with-the-new-bundling-of-javascript-files/">Webpack integration</a>
    </li>
  </ul>

  <h2>
    Documentation Revamp
  </h2>

  <ul>
    <li>
      <a href="https://gethue.com/build-your-own-autocompleter/">Building SQL Autocompletes</a>
    </li>
    <li>
      <a href="https://docs.gethue.com/administrator/administration/reference/">Architecture</a>
    </li>
    <li>
      <a href="https://docs.gethue.com/administrator/configuration/editor/">SQL connectors refresh</a>
    </li>
  </ul>

  <h2>
    Cloud
  </h2>

  <ul>
    <li>
      <a href="https://gethue.com/hue-in-kubernetes/">Kubernetes Helm</a>
    </li>
    <li>
      <a href="https://gethue.com/quick-start-a-hue-development-environment-in-3-minutes-with-docker/">Docker</a>
    </li>
    <li>
      <a href="https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/">Continuous Integration</a>
    </li>
  </ul>
</div>

&nbsp;

<span style="font-weight: 400;">Thank you to everybody using the product and who contributed to this release. Now off to the next one! (Python 3 support, Apache Knox integration & more SQL/Cloud features)</span>

As usual thank you to all the project contributors and for sending feedback and participating on the [Forum][6] or [@gethue][7]!

&nbsp;

Onwards!

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: https://docs.gethue.com/releases/release-notes-4.5.0/
 [3]: https://github.com/cloudera/hue/archive/release-4.5.0.zip
 [4]: http://demo.gethue.com/
 [5]: https://cdn.gethue.com/uploads/2019/08/hue_4.5.png
 [6]: https://discourse.gethue.com/
 [7]: https://twitter.com/gethue
