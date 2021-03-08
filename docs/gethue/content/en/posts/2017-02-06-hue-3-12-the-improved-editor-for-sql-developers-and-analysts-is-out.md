---
title: Hue 3.12, the improved editor for SQL Developers and Analysts is out!
author: admin
type: post
date: 2017-02-06T22:18:26+00:00
url: /hue-3-12-the-improved-editor-for-sql-developers-and-analysts-is-out/
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
categories:
  - Release

---
Hi Big Data Explorers,

&nbsp;

The Hue Team is glad to thanks all the contributors and release Hue 3.12! [<img src="https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png" />][1]

In this latest updates of Hue, the intelligent editor for SQL Developers and Analysts the focus was on the Editor and security. More than [1570 commits][2] on top of [3.11][3] went in! Go grab the tarball release and give it a spin!

<p style="text-align: center;">
  <a class="sf-button standard accent standard  dropshadow" style="color: #fff!important; font-size: 200%;" title="Click to download the tarball release" href="https://cdn.gethue.com/downloads/releases/3.12.0/hue-3.12.0.tgz" target="_blank" rel="noopener noreferrer"><br /> <span class="text">Download</span><br /> </a>
</p>

Here is a list of the main improvements.with links to more detailed blog posts. For all the changes, check out the [release notes][4] and for <span style="font-weight: 400;">a quick try open-up </span>[<span style="font-weight: 400;">demo.gethue.com</span>][5]<span style="font-weight: 400;">.</span>

&nbsp;

# **SQL Improvements**

<span style="font-weight: 400;">The Hue editor keeps getting better with these major improvements:</span>

## <span style="font-weight: 400;">Row Count</span>

<span style="font-weight: 400;">The number of rows returned is displayed so you can quickly see the size of the dataset. If the database engine does not provide the number of rows, Hue estimates the value and appends a plus sign, e.g. 100+.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/result-count.png" />][6]

## <span style="font-weight: 400;">Sample Popup</span>

<span style="font-weight: 400;">This popup offers a quick way to see sample of the data and other statistics on databases, tables, and columns. You can open the popup from the SQL Assist or with a right-click on any SQL object (table, column, function…). In this release, it also opens faster and caches the data.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/right_click_editor_assist-1.png" />][7]

<span style="font-weight: 400;">The footer provides direct links to the metastore page or to the table in the table Assist.</span>

&nbsp;

## <span style="font-weight: 400;">SQL Assist</span>

<span style="font-weight: 400;">The rendering of the items was rewritten and optimized. You should not experience any lag on databases with thousands of columns.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/dragdrop_from_asssist.png" />][8]

## <span style="font-weight: 400;">SQL Formatter</span>

<span style="font-weight: 400;">The SQL Formatter has a new and smarter algorithm that will make your queries look pretty with a single click!</span>

## <span style="font-weight: 400;">Timeline and Pivot Graphing</span>

<span style="font-weight: 400;">These visualizations are convenient for plotting chronological data or when subsets of rows have the same attribute and they will be stacked together.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/sql_timeline_chart-1024x351.png" />][9]

<span style="font-weight: 400;">Timeline</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/pivot_graph-1024x275.png" />][10]

<span style="font-weight: 400;">Pivot</span>

## <span style="font-weight: 400;">Creating an External Table</span>

<span style="font-weight: 400;">The improved support for S3 introduced the possibility of directly creating an external table in HDFS or S3.</span>

&nbsp;

<span style="font-weight: 400;">Read more about </span>[<span style="font-weight: 400;">the SQL improvements here</span>][11]<span style="font-weight: 400;">.</span>

#

# **Automated S3 Configuration**

<span style="font-weight: 400;">When using Cloudera Manager, Hue will now inherit automatically the S3 credentials if those are configured.</span>

[<img src="https://cdn.gethue.com/uploads/2017/02/s3_connector.png" />][12]

<span style="font-weight: 400;">Regular user won't have automatically access to the </span>[<span style="font-weight: 400;">S3 Browser and autocomplete</span>][3]<span style="font-weight: 400;">. They will require to have the "File Browser S3 permission" in Hue User admin added to one of their groups.</span>

&nbsp;

<span style="font-weight: 400;">Read more about </span>[<span style="font-weight: 400;">S3 configuration here</span>][13]<span style="font-weight: 400;">.</span>

&nbsp;

# **New Security Improvements**

<span style="font-weight: 400;">Many security options have been added in order to help administrators enforce and manage secure Hue installations. </span>

### Fixed Arbitrary host header acceptance

Fixed Arbitrary host header acceptance in Hue. Now one can set host/domain names that the Hue server can serve.

allowed_hosts="host.domain,host2.domain,host3.domain"

<pre><code class="bash">

[desktop]

allowed_hosts="*.domain"

\# your own fqdn example: allowed_hosts="*.hadoop.cloudera.com"

\# or specific example: allowed_hosts="hue1.hadoop.cloudera.com,hue2.hadoop.cloudera.com"

</code></pre>

<span style="color: #ff0000;"><strong>Note</strong></span>: “Bad Request (400)” error: when [hosting Hue in an AWS cluster][14], you might need to set the value to '*' to allow external client of the network to access Hue.

## <span style="font-weight: 400;">Fixed sessionid and csrftoken with HttpOnly Flag</span>

<span style="font-weight: 400;">If the HttpOnly flag is included in HTTP response header, then the cookie cannot be accessed through client side script and thus browser will not reveal the cookie to any third party. In order to help mitigate the risk of cross-site scripting, A cookie with this attribute is called an HTTP-only cookie. Any information contained in an HTTP-only cookie is less likely to be disclosed to a hacker or a malicious Web site.</span>

## <span style="font-weight: 400;">SASL Support for <code>hive.server2.thrift.sasl.qop=”auth-conf”&lt;code></code></code></span>

<span style="font-weight: 400;">SASL mechanisms support integrity and privacy protection of the communication channel after successful authentication. </span>

<span style="font-weight: 400;">In Thrift SASL library, the </span><span style="font-weight: 400;">sasl_max_buffer</span> <span style="font-weight: 400;">support is already implemented. </span><span style="font-weight: 400;">sasl_max_buffer</span> <span style="font-weight: 400;">in the </span><span style="font-weight: 400;">hue.ini</span> <span style="font-weight: 400;">provides a bigger and configurable buffer size that allow to provide support for </span><span style="font-weight: 400;"><code>hive.server2.thrift.sasl.qop="auth-conf"&lt;code></code></code></span><span style="font-weight: 400;">.</span>

<pre><code class="bash">[desktop]

\# This property specifies the maximum size of the receive buffer in bytes in thrift sasl communication (default 2 MB).

sasl_max_buffer=2 \* 1024 \* 1024

</code></pre>

## <span style="font-weight: 400;">Introducing Request HTTP Pool in Hue</span>

<span style="font-weight: 400;">The Request Session object allows the persistence of certain parameters across requests. It also persists cookies across all requests made from the Session instance, and will use urllib3’s connection pooling. We are making several requests to the same host:port, with this change the underlying TCP connection will be reused, which can result in a significant performance increase.</span>

<pre><code class="python">CACHE_SESSION = requests.Session()

CACHE_SESSION.mount('http://', requests.adapters.HTTPAdapter(pool_connections=conf.CHERRYPY_SERVER_THREADS.get(), pool_maxsize=conf.CHERRYPY_SERVER_THREADS.get()))

CACHE_SESSION.mount('https://', requests.adapters.HTTPAdapter(pool_connections=conf.CHERRYPY_SERVER_THREADS.get(), pool_maxsize=conf.CHERRYPY_SERVER_THREADS.get()))

</code></pre>

## Content-Security-Policy: header

The new Content-Security-Policy HTTP response header helps you reduce XSS risks on modern browsers by declaring what dynamic resources are allowed to load via a HTTP Header. (For more reading: <https://content-security-policy.com/>)

<pre><code class="bash">

[desktop]

secure_content_security_policy="script-src 'self' 'unsafe-inline' 'unsafe-eval' \*.google-analytics.com \*.doubleclick.net \*.mathjax.org data:;img-src 'self' \*.google-analytics.com \*.doubleclick.net http://\*.tile.osm.org \*.tile.osm.org \*.gstatic.com data:;style-src 'self' 'unsafe-inline';connect-src 'self';child-src 'self' data:;object-src 'none'"

#In HUE 3.11 and higher it is enabled by default.

</code></pre>

&nbsp;

Read more about the security improvements [here][15] and [here][16].

&nbsp;

# **Oozie Improvements**

## <span style="font-weight: 400;">Email Notifications</span>

<span style="font-weight: 400;">It becomes easy to receive an email notification after a workflow execution is complete. The workflow submission popup now shows the "Send completion email" checkbox.</span>

[<img class="aligncenter wp-image-4595" src="https://cdn.gethue.com/uploads/2016/12/send-email-checkbox.png" />][17]

## <span style="font-weight: 400;">Extended Dashboard Filtering</span>

<span style="font-weight: 400;">Just start typing in the text field to get the list of jobs whose Name or Submitter partially matches with the text. From the below picture, you can see that text </span><span style="font-weight: 400;">sh</span> <span style="font-weight: 400;">partially matches with the names of all four jobs. Note that the filter is applied on all the jobs and not just the ones in the current page.</span>

[<img src="https://cdn.gethue.com/uploads/2016/12/name-search-1024x524.png" />][18]

<span style="font-weight: 400;">To find the one single job among thousands of submitted jobs, you should enter the complete ID.</span>

&nbsp;

<span style="font-weight: 400;">Read more about </span>[<span style="font-weight: 400;">the Oozie improvements here</span>][19]<span style="font-weight: 400;">.</span>

&nbsp;

## Team Retreats

[<img class="aligncenter wp-image-4551" src="https://cdn.gethue.com/uploads/2016/12/IMG_5609-1024x768.jpg" />][20] [<img class="aligncenter wp-image-4529" src="https://cdn.gethue.com/uploads/2016/10/IMG_5290-1024x768.jpg" />][21]

  * [Malaysia and Cambodia][22]
  * [Riga, the capital of Latvia][23]

&nbsp;

## **Next!**

Next iteration will keep improving the data SQL Edition and Data Discovery. Hue 4 will get real, with the goal of becoming the equivalent of “Excel for Big Data”. The current apps are being unified into the [new Editor][24] and the whole Hue will become a single app that would provide the best Data Analytics user experience for Hadoop on prem or in the Cloud.

&nbsp;

Onwards!

&nbsp;

As usual thank you to all the project contributors and for sending feedback and participating on the [hue-user][25] list or [@gethue][26]!

&nbsp;

 [1]: https://cdn.gethue.com/uploads/2015/08/hue-logo-copy.png
 [2]: http://cloudera.github.io/hue/docs-3.12.0/release-notes/release-notes-3.12.0.html#_list_of_1570_commits
 [3]: https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/
 [4]: http://cloudera.github.io/hue/docs-3.12.0/release-notes/release-notes-3.12.0.html
 [5]: http://demo.gethue.com/
 [6]: https://cdn.gethue.com/uploads/2016/12/result-count.png
 [7]: https://cdn.gethue.com/uploads/2016/12/right_click_editor_assist-1.png
 [8]: https://cdn.gethue.com/uploads/2016/12/dragdrop_from_asssist.png
 [9]: https://cdn.gethue.com/uploads/2016/12/sql_timeline_chart.png
 [10]: https://cdn.gethue.com/uploads/2016/12/pivot_graph.png
 [11]: https://gethue.com/sql-improvements-with-row-counts-sample-popup-and-more/
 [12]: https://cdn.gethue.com/uploads/2017/02/s3_connector.png
 [13]: https://www.cloudera.com/documentation/enterprise/latest/topics/hue_use_s3_enable.html#concept_p2v_1yl_gy
 [14]: https://gethue.com/hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/
 [15]: https://gethue.com/hue-security-improvements/
 [16]: https://gethue.com/security-improvements-http-only-flag-sasl-qop-and-more/
 [17]: https://cdn.gethue.com/uploads/2016/12/send-email-checkbox.png
 [18]: https://cdn.gethue.com/uploads/2016/12/name-search.png
 [19]: https://gethue.com/oozie-improvements-in-3-12-with-email-notifications-and-extended-dashboard-filtering/
 [20]: https://cdn.gethue.com/uploads/2016/12/IMG_5609.jpg
 [21]: https://cdn.gethue.com/uploads/2016/10/IMG_5290.jpg
 [22]: https://gethue.com/team-retreat-in-malaysia-an
 [23]: https://gethue.com/team-retreat-in-riga/
 [24]: https://gethue.com/sql-editor/
 [25]: http://groups.google.com/a/cloudera.org/group/hue-user
 [26]: https://twitter.com/gethue
