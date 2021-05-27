---
title: Easily checking for deadlinks on docs.gethue.com
author: Hue Team
type: post
date: 2019-10-17T15:34:31+00:00
url: /easily-checking-for-deadlinks-on-docs-gethue-com/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
# - Version 4.6

---
[docs.gethue.com][1] are getting some refreshed content continuously. In addition, a series of links not working (returning a 404) have been fixed. Here is how it was done.

First we used the [muffet][2] tool. muffet is a fast link checker crawler, very easy to use:

<pre><code class="bash">sudo snap install muffet
</code></pre>

Then after booting the hugo [documentation server][3], we point to its url. We also blacklist certain urls to avoid some noisy false positives:

<pre><code class="bash">muffet http://localhost:35741/ --exclude ".*releases.*" -f
</code></pre>

And here is the output:

<pre><code class="bash">$ muffet http://localhost:35741/ --exclude ".*releases.*" -f
http://localhost:35741/user/
404 http://localhost:35741/administrator/configuration/editor/#connectors
http://localhost:35741/developer/development/#sql-parsers
404 http://localhost:35741/administrator/configuration/editor/#postgresql
http://localhost:35741/administrator/administration/reference/
dial tcp4 127.0.0.1:5555: connect: connection refused http://localhost:5555/tasks
http://localhost:35741/user/querying/
404 http://wiki.apache.org/hadoop/Hive/AdminManual/Configuration
http://localhost:35741/administrator/installation/cloud/
dial tcp4 127.0.0.1:16686: connect: connection refused http://localhost:16686
lookup prometheus on 127.0.0.53:53: server misbehaving http://prometheus:9090/graph
lookup prometheus on 127.0.0.53:53: server misbehaving http://prometheus:9090/targets
http://localhost:35741/administrator/configuration/apps/
404 http://localhost:35741/administrator/configuration/dashboard
404 http://localhost:35741/administrator/configuration/editor/
404 http://localhost:35741/developer/editor/
404 http://localhost:35741/user/editor/
dialing to the given TCP address timed out https://dev.mysql.com/downloads/connector/j/
http://localhost:35741/user/browsing/
404 http://localhost:35741/administrator/configuration/external/
http://localhost:35741/developer/sdk/
404 http://localhost:8000
404 https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/static/desktop/js/autocomplete/jison
404 https://github.com/cloudera/hue/tree/master/desktop/libs/metadata/catalog
http://localhost:35741/administrator/configuration/connectors/
404 http://localhost:35741/administrator/configuration/external/
404 http://localhost:35741/user/browsers#adls
404 http://localhost:35741/user/browsers#s3
404 http://localhost:35741/user/browsers/
http://localhost:35741/developer/development/
404 http://docs.python.org/library/hotshot.html
404 https://en.wikipedia.org/wiki/Hue_(Software
404 https://twitter.com/gethue!
lookup developer on 127.0.0.53:53: server misbehaving</code></pre>

<a href="https://cdn.gethue.com/uploads/2019/10/website_link_checker.png"><img src="https://cdn.gethue.com/uploads/2019/10/website_link_checker.png" /></a>

Et voila! Then a few searches and replaces in the [documentation content][5] and we have a cleaner experience! Next action is to add the link checking to the [Continuous Integration][6] to fully automate the process and scale the developer productivity.

<div>
  <div>
    Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> or <a href="https://twitter.com/gethue">@gethue</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!
  </div>

  <p>
    &nbsp;
  </p>
</div>

<div>
</div>

Romain from the Hue Team

 [1]: http://docs.gethue.com
 [2]: https://github.com/raviqqe/muffet
 [3]: https://docs.gethue.com/developer/development/#documentation
 [4]: https://cdn.gethue.com/uploads/2019/10/website_link_checker.png
 [5]: https://github.com/cloudera/hue/tree/master/docs/docs-site/content
 [6]: https://gethue.com/improving-the-developer-productivity-with-some-continuous-integration/
