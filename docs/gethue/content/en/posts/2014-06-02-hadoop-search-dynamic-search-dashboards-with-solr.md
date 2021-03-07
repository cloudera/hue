---
title: 'Hadoop search: Dynamic search dashboards with Solr'
author: admin
type: post
date: 2014-06-02T15:39:07+00:00
url: /hadoop-search-dynamic-search-dashboards-with-solr/
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
sf_remove_promo_bar:
  - 1
slide_template:
  - default
categories:
---

[Hue 3.6][1] and a team retreat in [Curacao][2] bring the second version of the previous [Search App][3] to some higher standards. The user experience has been greatly improved as now the app provides a very easy way to build custom dashboards and visualizations.

Here is a video demoing how to interactively explore some real Apache Log data coming from the live Hue of [demo.gethue.com][2]. In just a few clicks, we look for pages with errors, what are the most used Hue apps, the top Web Browsers or inspect the user traffic on a gradient colored World map:

{{< youtube hVBxH7w3EP8 >}}

**Update!**

New widgets are available in Hue 3.7: <https://gethue.com/search-app-enhancements-explore-even-more-data/>

{{< youtube K6YVZq8wymw >}}

The main features are:

- Dynamic interface updating in live
- Drag & Drop dashboard builder
- Text, Timeline, Pie, Line, Bar, Map, Filters, Grid and HTML widgets
- Solr Index creation wizard from a file

&nbsp;

<figure>
  <a href="https://cdn.gethue.com/uploads/2014/03/hue-3.6-search-v2-1024x548.png">
    <img src="https://cdn.gethue.com/uploads/2014/03/hue-3.6-search-v2-1024x548.png" />
  </a>
  <figcaption>Build your own dynamic dashboard</figcaption>
</figure>

&nbsp;

More is on the roadmap, like integration with other Hue apps like Hive/HBase, export/import of results to Hadoop, more data types to plot. A following tutorial presents how to [index the Apache Log][5] into Solr and start doing your own analytics. In the meantime, feel free to give the search dashboards a try with [Hue 3.6][1]  or the upcoming C5.1 package!

As usual, we welcome any feedback on [@gethue][6] or [hue-user][7]!

[1]: https://gethue.com/hadoop-ui-hue-3-6-and-the-search-dashboards-are-out
[2]: https://gethue.com/team-retreat-in-the-caribbean-curacao/
[3]: https://gethue.com/tutorial-search-hadoop-in-hue/
[4]: https://cdn.gethue.com/uploads/2014/03/hue-3.6-search-v2.png
[5]: https://gethue.com/analyse-apache-logs-and-build-your-own-web-analytics-dashboard-with-hadoop-and-solr
[6]: http://twitter.com/gethue
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
