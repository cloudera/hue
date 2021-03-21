---
title: Search Hadoop in Hue
author: admin
type: post
date: 2013-06-12T18:33:00+00:00
url: /tutorial-search-hadoop-in-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/52804483421/tutorial-search-hadoop-in-hue
tumblr_gethue_id:
  - 52804483421
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

<p id="docs-internal-guid-388e0995-305d-1ff0-9d32-60089c64749b">
  <span>This post talks about Hue, a </span><a href="http://gethue.com">UI</a><span> for making Apache Hadoop easier to use.</span>
</p>

Coming in [Hue 2.4][1], on top of more than 150 fixes a new app was added: Search. You can now search Hadoop like you do with Google or Yahoo!. In addition a wizard lets you tweak the result snippets and tailors the search experience to your needs.

<span>Here is a video demoing the querying and the results customization. The demo is based on the </span>[<span>Twitter Streaming</span>][2] <span>data collected with Apache Flume and indexed in real time.</span>

{{< youtube IgOSkGNmEyI >}}

<span>The new Hue Search app is adding an impressive list of features to the already enterprise grade, industry standard list of features Solr provides. More specifically, here are the most significant ones:</span>

- <span>Based on standard </span>[<span>Solr</span>][3] <span>and </span>[<span>Solr Cloud</span>][4]
- <span>Optimized for </span>[<span>Cloudera Search</span>][5] <span>for searching Hadoop</span>
- <span>Result snipped editor with live preview</span>
- <span>Field, range and date facets</span>
- <span>Sorting</span>
- <span>Highlighting</span>
- <span>Layout and functions templates</span>
- <span>Custom CSS/Javascript placeholders</span>

&nbsp;

<span>Code from Snippet Editor</span>

<span>Here are the final templates used in the Hue Search app demo. They are used for customizing the look and feel of the search results. With this HTML and CSS, we inserted the index fields we wanted to display, added Twitter profile images, icons, links and changed the font and colors of the text.</span>

&nbsp;

<span>HTML from the Source tab</span>

<pre class="code">&lt;div class="row-fluid"&gt;
  &lt;div class="row-fluid"&gt;
    &lt;div class="row-fluid"&gt;
      &lt;div class="span1"&gt;
        &lt;img src="http://twitter.com/api/users/profile_image/{{user_screen_name}}" class="avatar" /&gt;
      &lt;/div&gt;
      &lt;div class="span11"&gt;
        &lt;a href="https://twitter.com/{{user_screen_name}}/status/{{id}}" class="btn openTweet"&gt;
          &lt;i class="icon-twitter"&gt;&lt;/i&gt;
        &lt;/a&gt;
        &lt;b&gt;{{user_name}}&lt;/b&gt;
        &lt;br/&gt;
        {{text}}
        &lt;br/&gt;
        &lt;div class="created"&gt;{{#fromnow}}{{created_at}}{{/fromnow}}&lt;/div&gt;
      &lt;/div&gt;
    &lt;/div&gt;
    &lt;br/&gt;
  &lt;/div&gt;
&lt;/div&gt;</pre>

<span>CSS from the advanced tab</span>

<pre class="code">&lt;style&gt;
em {
  font-weight: bold;
  background-color: yellow;
}

.avatar {
  margin: 10px;
}

.created {
  margin-top: 10px;
  color: #CCC;
}

.openTweet {
  float: right;
  margin: 10px;
}
&lt;/style&gt;</pre>

&nbsp;

The release for Hue 2.4 is available <a class="trackLink" href="https://cdn.gethue.com/downloads/releases/2.4.0/hue-2.4.0.tgz" target="_blank" rel="noopener noreferrer">here</a>.

<span>The new Hue Search app is using the regular Solr API underneath the hood, yet adds a remarkable list of UI features that makes using search over data stored in Hadoop a breeze. It integrates with the other Hue apps like </span>[File Browser][6] <span>for looking at the index file in a few clicks. More advanced features are on the way like fine-grained security of indexes, multi-shard search or even saving results.</span>

<span>We welcome any feedback on </span>[hue-user][7] <span>and Solr-specific requests on </span>[search-user][7]<span>!</span>

[1]: http://gethue.tumblr.com/post/52904410987/hue-2-4-is-released 'Hue Hadoop UI'
[2]: https://dev.twitter.com/docs/streaming-apis
[3]: http://lucene.apache.org/solr/
[4]: http://wiki.apache.org/solr/SolrCloud
[5]: http://www.cloudera.com/content/support/en/documentation/cloudera-search/cloudera-search-documentation-v1-latest.html
[6]: http://blog.cloudera.com/blog/2013/04/demo-hdfs-file-operations-made-easy-with-hue/
[7]: blank
