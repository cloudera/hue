---
title: UI to edit Sentry privileges of Solr collections
author: admin
type: post
date: 2016-06-02T23:17:05+00:00
url: /ui-to-edit-sentry-privilege-of-solr-collections/
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

The [Sentry app][1] now let's you edit Solr Collection privileges. It previously only support editing permissions of the Hive Tables.

It becomes now much easier to control the authorization of all your Solr indexes (until now privileges had to be set through a flat file with a server restart) and make sure that the powerful [Dynamic Search Dashboards][2] can be accessed securely by only certain group of users.

Here is a video demoing how to configure the access to your Solr data:

{{< youtube gSNKv5agmTU >}}

Below are screenshots of the main features of the app:

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/05/solr-secu-1024x624.png"><img src="https://cdn.gethue.com/uploads/2016/05/solr-secu-1024x624.png" /></a><figcaption>Listing of Solr collections and configs with their related privileges</figcaption></figure>

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/05/solr-secu2-e1464909489928-1024x562.png"><img src="https://cdn.gethue.com/uploads/2016/05/solr-secu2-e1464909489928-1024x562.png" /></a><figcaption>Listing of all the roles and their privileges. Possibility to filter by groups.</figcaption></figure>

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/06/solr-sentry-all.png"><img class="size-full wp-image-4091" src="https://cdn.gethue.com/uploads/2016/06/solr-sentry-all.png" /></a><figcaption>Apply privilege to all the collections or configs with *</figcaption></figure>

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/06/solr-sentry-query-error-1024x279.png"><img src="https://cdn.gethue.com/uploads/2016/06/solr-sentry-query-error-1024x279.png" /></a><figcaption>End user error when querying a collection without the QUERY privilege</figcaption></figure>

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2016/06/solr-sentry-update-error-1024x405.png"><img class="size-large wp-image-4093" src="https://cdn.gethue.com/uploads/2016/06/solr-sentry-update-error-1024x405.png" /></a><figcaption>End user error when modifying a record without the UPDATE privilege</figcaption></figure>

&nbsp;

&nbsp;

We hope that you like the ease of use and security, and feel free to send feedback on the [hue-user][7] list or [@gethue][8]!

[1]: https://gethue.com/apache-sentry-made-easy-with-the-new-hue-security-app/
[2]: https://gethue.com/dynamic-search-dashboard-improvements-3/
[3]: https://cdn.gethue.com/uploads/2016/05/solr-secu2-e1464909489928.png
[4]: https://cdn.gethue.com/uploads/2016/06/solr-sentry-all.png
[5]: https://cdn.gethue.com/uploads/2016/06/solr-sentry-query-error.png
[6]: https://cdn.gethue.com/uploads/2016/06/solr-sentry-update-error.png
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
