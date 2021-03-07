---
title: 'Quick Task: Restrict Number of Concurrent Sessions Per User'
author: admin
type: post
date: 2019-03-26T18:30:27+00:00
url: /restrict-number-of-concurrent-sessions-per-user/
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title_style:
  - standard
sf_page_title_bg:
  - none
sf_page_title_text_style:
  - light
sf_background_image_size:
  - cover
sf_author_info:
  - 1
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

---
<span style="font-weight: 400;">Hue administrators can restrict the number of concurrent sessions per user. The default value is 0 to represent no restrictions. In that case, a user can have as many simultaneous Hue sessions, i.e. logins, as he wishes. For security purposes, this can be restricted. When it is, normally the concurrent_user_session_limit is set to 1.</span>

<pre><code class="bash">[desktop]

[[session]]

concurrent_user_session_limit=1

</code></pre>

<span style="font-weight: 400;">When concurrent_user_session_limit is set to 1 any session, i.e. on a different machine or browser, in excess of 1 is removed by eldest. If a user gets logged out automatically, then he or she can assume somebody else is logging in as his/her credential on a different machine.</span>

**Note**<span style="font-weight: 400;">:</span>

<li style="font-weight: 400;">
  <span style="font-weight: 400;">Most of the browsers for example Chrome is sharing the same session between windows or tabs. </span>
</li>
<li style="font-weight: 400;">
  <span style="font-weight: 400;">This feature is not for restricting how many queries user can submit to Hive/Impala. Instead, they should set the Hive/YARN and Impala resource management pools properly (at the query engine, not the clients like Hue).</span>
</li>
