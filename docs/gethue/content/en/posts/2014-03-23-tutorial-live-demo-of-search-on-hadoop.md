---
title: Search samples for a live demo of Search on Hadoop
author: admin
type: post
date: 2014-03-23T05:00:00+00:00
url: /tutorial-live-demo-of-search-on-hadoop/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/78012277574/tutorial-live-demo-of-search-on-hadoop
tumblr_gethue_id:
  - 78012277574
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
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
slide_template:
  - default
categories:
---

Edit: This post is deprecated since [Hue 3.6][1], clicking on the install button is the only thing to do now!

Hue comes up with a series of examples (for [Hive][2]/[Impala][2], [HBase][3]...) to help you get started with Hadoop. Recently, some demo Collection/Indexes were added for the [Search Application][4]:

<p style="text-align: center;">
  Twitter<a href="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080626.png"><br /> <img src="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080626.png" alt="Screenshot from 2014-04-09 08:06:26" width="691" height="348"  /></a>
</p>

<p style="text-align: center;">
  Logs<br /> <a href="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080635.png"><img class="wp-image-1105 aligncenter" src="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080635.png" alt="Screenshot from 2014-04-09 08:06:35" width="690" height="347"  /></a>
</p>

<p style="text-align: center;">
  Yelp
</p>

<p style="text-align: center;">
  <a href="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080630.png"><img class="wp-image-1106 aligncenter" src="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-080630.png" alt="Screenshot from 2014-04-09 08:06:30" width="691" height="348"  /><br /> </a>
</p>

To install them,  got to Hue on the [/about/][5] page and on Step 2 click on 'Solr Search':

<p style="text-align: center;">
  <a href="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-083220.png"><img class=" wp-image-1120 aligncenter" src="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-04-09-083220.png" alt="Screenshot from 2014-04-09 08:32:20" width="520" height="427"  /></a>
</p>

This will install the search templates in Hue. To make the demo work by default, Hue is using a predefined Solr response. Hue displays a warning in this case as the page is not updated when typing a query:

[<img class="alignnone size-full wp-image-1104" src="https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-03-10-161306.png" alt="Screenshot from 2014-03-10 16:13:06" width="628" height="58"  />][6]

The next step is to create the indexed into Solr. First, make sure that Solr has been setup and initialized [correctly][7].

In order to query a live dataset, you need to index some data. Go on the Hue machine:

<pre><code class="bash">

cd $HUE_HOME

cd apps/search/examples/bin

</code></pre>

Then create the Solr collections:

<pre><code class="bash">./create_collections.sh</code></pre>

In case Solr is not on the same machine, add this parameter in the script:

<pre><code class="bash">-solr http://localhost:8983/solr</code></pre>

Then index some example data with:

<pre><code class="bash">./post.sh</code></pre>

Same, if Solr is on a different machine, update the url:

<pre><code class="bash">URL=http://localhost:8983/solr</code></pre>

And that’s it! The above warning message will disappear and you will be able to query Solr indexes in live!

Then go create your own Search!

{{< youtube ATldKiiJdqY >}}

As usual feel free to comment on the[ hue-user][8] list or [@gethue][9]!

[1]: https://gethue.com/analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr
[2]: https://gethue.com/hadoop-tutorial-new-impala-and-hive-editors/
[3]: https://gethue.com/the-web-ui-for-hbase-hbase-browser/ 'The Web UI for HBase: HBase Browser'
[4]: http://gethue.tumblr.com/post/65969470780/hadoop-tutorials-season-ii-7-how-to-index-and-search
[5]: http://127.0.0.1:8888/about/
[6]: https://cdn.gethue.com/uploads/2014/03/Screenshot-from-2014-03-10-161306.png
[7]: http://www.cloudera.com/content/cloudera-content/cloudera-docs/CDH5/latest/Search/Cloudera-Search-Installation-Guide/csig_deploy_search_solrcloud.html
[8]: http://groups.google.com/a/cloudera.org/group/hue-user
[9]: https://twitter.com/gethue
