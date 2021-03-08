---
title: Suggest for Solr Search Dashboards
author: admin
type: post
date: 2016-04-06T16:08:17+00:00
url: /suggest-for-solr-search-dashboards/
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
---

Hey Search users,

The upcoming Hue version supports [Solr Suggester][1] and makes your data easier to search! Suggester assists the user by proposing an auto-completable list of queries:

&nbsp;

{{< youtube RupOQCy5DdA >}}

&nbsp;

We hope that you like the interactivity, and feel free to send feedback on the [hue-user][2] list or [@gethue][3]!

&nbsp;

**How-to**

First grab a [Solr 5][4], start it and make sure that it has a suggester configured:

<pre><code class="bash">romain@unreal:$ ./bin/solr -e techproducts

Waiting to see Solr listening on port 8983 [/]

Started Solr server on port 8983 (pid=23696). Happy searching!

Checked core existence using Core API command:

http://localhost:8983/solr/admin/cores?action=STATUS&core=techproducts

</code></pre>

Confirm that Solr has a `suggester` configured, here named `mySuggester`:

<pre><code class="bash">

http://127.0.0.1:8983/solr/#/techproducts/files?file=solrconfig.xml

<searchComponent name="suggest" class="solr.SuggestComponent">

<lst name="suggester">

<str name="name">mySuggester</str>

<str name="lookupImpl">FuzzyLookupFactory</str>

<str name="dictionaryImpl">DocumentDictionaryFactory</str>

<str name="field">cat</str>

<str name="weightField">price</str>

<str name="suggestAnalyzerFieldType">string</str>

<str name="buildOnStartup">false</str>

</lst>

</searchComponent>

</code></pre>

&nbsp;

then activate the suggester in the Hue Dashboard settings:

<img src="https://cdn.gethue.com/uploads/2016/04/suggester-settings.png" />

and see the help in the query box:

<img src="https://cdn.gethue.com/uploads/2016/04/search-suggest.png" />

[1]: https://cwiki.apache.org/confluence/display/solr/Suggester
[2]: http://groups.google.com/a/cloudera.org/group/hue-user
[3]: https://twitter.com/gethue
[4]: http://yonik.com/download/
