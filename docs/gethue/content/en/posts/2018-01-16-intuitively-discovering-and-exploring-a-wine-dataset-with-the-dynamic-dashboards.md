---
title: Intuitively discovering and exploring a Wine dataset with the Dynamic Dashboards
author: admin
type: post
date: 2018-01-16T15:35:09+00:00
url: /intuitively-discovering-and-exploring-a-wine-dataset-with-the-dynamic-dashboards/
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
---

[Dashboards][1] are an easy way to quickly explore a new dataset without typing any SQL. It usually complements the analyses before or after the querying activity in the [SQL Editor][2]. In this scenario we are using [Apache Solr][3] as the analytic database backend.

Goal: we are picking a [Wine dataset][4] from the Machine Learning Competition website Kaggle and want to get a feeling of the industry and select some good wines similar to one of our best ranked favorite Pink / "Rosé" wine. Let's continue in the video demo:

{{< youtube 9iVkVML5vYI >}}

[<img class="wp-image-5185 aligncenter" src="https://cdn.gethue.com/uploads/2018/01/wine-dashboard.png"/>][5]

## Importing

Any CSV file can be dragged & dropped and ingested into an index in a few clicks via the Data Import Wizard [link]. The indexed data is immediately queryable and its facets/dimensions will be very fast to explore.

## Browsing

The Collection browser got polished in the last releases and provide more information on the columns. The left metadata assist of [Hue 4][6] makes it handy to list them and peak at their content via the sample popup.

## Querying

The search box support live prefix filtering of field data and comes with a Solr syntax autocomplete in order to make the querying intuitive and quick. Any field can be inspected for its top values of statistic. This analysis happens very fast as the data is indexed.

On top of this, the Solr 7 Analytic Facets are close to be fully supported in the Dashboard. More on this is coming in a follow-up blog post. The "More like This" feature lets you selected fields you would like to use to find similar records. This is a great way to find similar items like wine in this tutorial, or similar issues, customers, people...

&nbsp;

**Note**:

If you are not getting any suggestion, and opening the field information popup on the right assist shows the error below, it means the collection needs to have the [Solr Term Handler][7] configured.

<pre><code class="bash">

<h1>HTTP Status 404 - /solr/jira_search/terms</h1>

There are no terms to be shown

</code></pre>

## Coming up Next!

A deeper presentation of Solr's Analytic Facet is coming as well as how we could have [Geo-IPed][8] our wine list and visualize it via maps. A revamp of the layout to make the Dashboards even more intuitive and how the SQL Editor and Dashboards are getting tied together will also be on the menu. We wish you some Happy Explorations!

[1]: https://gethue.com/search-dashboards/
[2]: https://gethue.com/sql-editor/
[3]: http://lucene.apache.org/solr/
[4]: https://www.kaggle.com/zynicide/wine-reviews
[5]: https://cdn.gethue.com/uploads/2018/01/wine-dashboard.png
[6]: https://gethue.com/the-hue-4-user-interface-in-detail/
[7]: https://lucene.apache.org/solr/guide/6_6/the-terms-component.html
[8]: https://gethue.com/easy-indexing-of-data-into-solr/
