---
title: Hue 4.2 and its Self Service BI improvements are out!
author: admin
type: post
date: 2018-04-04T17:30:45+00:00
url: /hue-4-2-and-its-self-service-bi-improvements-are-out/
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
  - Release

---
Hi Big Data Explorers,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 4.2! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

Last Hue version compatible with Python 2.6, next will be 2.7 only as a major upgrade is coming next.

The focus of this release was to keep making progress on the self service BI theme and prepare the ground for next release that will include an upgraded backend and a revamped Dashboard and more improvements to the Data Catalog and Query Assistance.

This release comes with 1200 commits and 500+ bug fixes! Go grab the tarball and give it a spin!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://www.dropbox.com/s/0rhrlnjmyw6bnfc/hue-4.2.0.tgz?dl=0" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

Here is a list of the main improvements. For all the changes, check out the [release notes][2] and for <span style="font-weight: 400;">a quick try open-up </span>[<span style="font-weight: 400;">demo.gethue.com</span>][3]<span style="font-weight: 400;">.</span>

# Summary

<span style="font-weight: 300;">3 main areas of focus</span>

<span style="font-weight: 400;">Cloud</span>

<li style="font-weight: 400;">
  <a href="https://gethue.com/browsing-adls-data-querying-it-with-sql-and-exporting-the-results-back-in-hue-4-2/"><span style="font-weight: 300;">ADLS Browser</span></a>
</li>

<span style="font-weight: 400;">Analytic DB</span>

<li style="font-weight: 400;">
  <span style="font-weight: 300;">Top Search UX</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">SQL Syntax checker</span>
</li>
<li style="font-weight: 400;">
  <a href="https://gethue.com/browsing-impala-query-execution-within-the-sql-editor/"><span style="font-weight: 300;">Impala Query Browser</span></a>
</li>

<span style="font-weight: 400;">Supportability</span>

<li style="font-weight: 400;">
  <span style="font-weight: 300;">SAML update</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Documentation revamp</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Metric page</span>
</li>

&nbsp;

# <span style="font-weight: 300;">Cloud</span>

[<span style="font-weight: 300;">ADLS Browser</span>][4] <span style="font-weight: 300;">(similar to HFS & </span>[<span style="font-weight: 300;">S3 Browser</span>][5]<span style="font-weight: 300;">)</span>

<li style="font-weight: 400;">
  <span style="font-weight: 300;">Exploring ADLS in file browser</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Create Hive Tables Directly From ADLS</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Save Query Results to ADLS</span>
</li>

[<img class="alignnone wp-image-5031" src="https://cdn.gethue.com/uploads/2017/11/image2.png"/>][6]

# <span style="font-weight: 300;">Analytical DB</span>

## <span style="font-weight: 300;">Data Catalog Search</span>

<li style="font-weight: 400;">
  Available in the top bar
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Since </span><span style="font-weight: 300;"><a href="https://blog.cloudera.com/blog/2017/05/new-in-cloudera-enterprise-5-11-hue-data-search-and-tagging/">5.11</a> </span><span style="font-weight: 300;">but getting simpler</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Search Tables, Columns and Saved queries</span>
</li>

<span style="font-weight: 300;">Example of searches:</span>

<li style="font-weight: 400;">
  <span style="font-weight: 300;">table:customer → Find the </span><span style="font-weight: 300;">customer table</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">table:tax* tags:finance → </span><span style="font-weight: 300;">List all the tables starting </span><span style="font-weight: 300;">with tax and tagged with ‘finance’</span>
</li>

[<img class="alignnone wp-image-5247" src="https://cdn.gethue.com/uploads/2018/01/top_search.png"/>][7]

&nbsp;

## <span style="font-weight: 300;">Syntax Checker</span>

  * <span style="font-weight: 300;">Warn before executing</span>
  * <span style="font-weight: 300;">Can suggest simple fix</span>

[<img class="alignnone size-medium wp-image-5249" src="https://cdn.gethue.com/uploads/2018/01/syntax_checkerhigh.png"/>][8][<img class="alignnone size-full wp-image-5248" src="https://cdn.gethue.com/uploads/2018/01/checker_help.png"/>][9]

&nbsp;

## <span style="font-weight: 300;">Impala Query Browser</span>

<span style="font-weight: 300;">Goal: b</span><span style="font-weight: 300;">uilt-in Troubleshooting for:</span>

  * <span style="font-weight: 300;">Queries</span>
  * <span style="font-weight: 300;">Profiles</span>
  * <span style="font-weight: 300;">Plans</span>
  * <span style="font-weight: 300;">Memory</span>

[<span style="font-weight: 300;">Read more in this blog post.</span>][10]

&nbsp;

[<img class="alignnone size-full wp-image-5083" src="https://cdn.gethue.com/uploads/2017/11/General.png"/>][11]

&nbsp;

# <span style="font-weight: 300;">Dashboard</span>

<span style="font-weight: 300;">Apache Solr <a href="https://gethue.com/search-dashboards/">dynamic Dashboards</a>:</span>

<li style="font-weight: 400;">
  <a href="https://gethue.com/intuitively-discovering-and-exploring-a-wine-dataset-with-the-dynamic-dashboards/"><span style="font-weight: 300;">Dashboard autocomplete</span></a>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">More Like This</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Collection page</span>
</li>

[<img class="alignnone wp-image-5250" src="https://cdn.gethue.com/uploads/2018/01/solr_more_like_this.png"/>][12] [<img class="alignnone wp-image-5251" src="https://cdn.gethue.com/uploads/2018/01/dashboard_autocomplete.png"/>][13]

&nbsp;

# <span style="font-weight: 300;">Supportability</span>

<li style="font-weight: 400;">
  <span style="font-weight: 300;">SAML update (with idle session fix)</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;"><a href="http://cloudera.github.io/hue/latest/">Documentation revamp</a></span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Thread page</span>
</li>

[<img class="alignnone size-full wp-image-5252" src="https://cdn.gethue.com/uploads/2018/01/hue_metric_page.png"/>][14]

<li style="font-weight: 400;">
  <span style="font-weight: 300;">Bug fixes</span> <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">UX improvements (document listing, opening back query history scroll, CTRL+Z...)</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">Performances (concurrency, file downloads, query timeouts)</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">Support multi-authentication with LDAP</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">YARN "Diagnostics" info in Job Browser</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">Option to disable concurrent user sessions "concurrent_user_session_limit"</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">Rebalance user on log out</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">Editor grid result not correctly aligned when browser zoom is not 100%</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">...</span>
    </li>
  </ul>
</li>

&nbsp;

# <span style="font-weight: 300;">Demo use case: </span><span style="font-weight: 300;">Customer 360</span>

In this [Self Service analytics Customer 360 demo][15] we use the [Editor][16] to query credit card transaction data that is saved in an object store in the cloud ([here S3][5]) and in a Kudu table. The demos leverages the Data Catalog search and tagging as well as the Query Assistant.

[<img class="alignnone wp-image-4997" src="https://cdn.gethue.com/uploads/2017/10/customer-360-datasets.png"/>][17]

Onwards!

&nbsp;

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][18] list or [@gethue][19]!

p.s.: in case the Dropbox link doesn't work on the network you are currently in, here's a [mirror of the release][20].

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: http://cloudera.github.io/hue/docs-4.2.0/release-notes/release-notes-4.2.0.html
 [3]: http://demo.gethue.com/
 [4]: https://gethue.com/browsing-adls-data-querying-it-with-sql-and-exporting-the-results-back-in-hue-4-2/
 [5]: https://gethue.com/introducing-s3-support-in-hue/
 [6]: https://cdn.gethue.com/uploads/2017/11/image2.png
 [7]: https://cdn.gethue.com/uploads/2018/01/top_search.png
 [8]: https://cdn.gethue.com/uploads/2018/01/syntax_checkerhigh.png
 [9]: https://cdn.gethue.com/uploads/2018/01/checker_help.png
 [10]: https://gethue.com/browsing-impala-query-execution-within-the-sql-editor/
 [11]: https://cdn.gethue.com/uploads/2017/11/General.png
 [12]: https://cdn.gethue.com/uploads/2018/01/solr_more_like_this.png
 [13]: https://cdn.gethue.com/uploads/2018/01/dashboard_autocomplete.png
 [14]: https://cdn.gethue.com/uploads/2018/01/hue_metric_page.png
 [15]: https://gethue.com/self-service-bi-doing-a-customer-360-by-querying-and-joining-salesforce-marketing-and-log-datasets/
 [16]: https://gethue.com/sql-editor/
 [17]: https://cdn.gethue.com/uploads/2017/10/customer-360-datasets.png
 [18]: http://groups.google.com/a/cloudera.org/group/hue-user
 [19]: https://twitter.com/gethue
 [20]: https://cdn.gethue.com/downloads/releases/4.2.0/hue-4.2.0.tgz
