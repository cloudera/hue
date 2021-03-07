---
title: 'Self Service BI: doing a Customer 360 by querying and joining Salesforce, Marketing and log datasets'
author: admin
type: post
date: 2018-01-10T21:44:29+00:00
url: /self-service-bi-doing-a-customer-360-by-querying-and-joining-salesforce-marketing-and-log-datasets/
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
  - Tutorial
---

In this demo we use the [Editor][1] to query credit card transaction data that is saved in an object store in the cloud ([here S3][2]) and in a Kudu table. The demos leverages the Data Catalog search and tagging as well as the Query Assistant.

Note: Do it Yourself! The queries and data are freely available on [demo.gethue.com][3].

<span style="font-weight: 300;">Scenario: Digital Services International</span>

<span style="font-weight: 300;">You recently launched a new streaming service:</span>

<li style="list-style-type: none;">
  <ul>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">VP wants to understand support impact of this launch</span>
    </li>
    <li style="font-weight: 400;">
      <span style="font-weight: 300;">Marketing wants to use this to better target campaigns</span>
    </li>
  </ul>
</li>

<span style="font-weight: 400;">Goal: </span><span style="font-weight: 300;">Build a 360-degree view of your customers to understand the support costs, product usage, time-to-resolution, and current activity in marketing channels</span>

{{< youtube vTqiQIFpFxM >}}

<span style="font-weight: 300;">What we’ll cover:</span>

<li style="font-weight: 400;">
  <span style="font-weight: 300;">Find the right sales tables across all databases</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Query Salesforce to see support activity by accounts and TTR</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Join with Usage Logs (Kudu table) to correlate usage with support activity</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Join with Marketing Database to see existing campaign activity and filter out support-heavy customers for special campaign</span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 300;">Save & share queries for other members of the team and other departments</span>
</li>

&nbsp;

[<img class="aligncenter wp-image-4996" src="https://cdn.gethue.com/uploads/2017/10/360-degrees.png"/>][4]

[<img class="aligncenter wp-image-4997" src="https://cdn.gethue.com/uploads/2017/10/customer-360-datasets.png"/>][5]

[1]: https://gethue.com/sql-editor/
[2]: https://gethue.com/introducing-s3-support-in-hue/
[3]: http://demo.gethue.com/hue/editor?editor=108020&type=impala
[4]: https://cdn.gethue.com/uploads/2017/10/360-degrees.png
[5]: https://cdn.gethue.com/uploads/2017/10/customer-360-datasets.png
