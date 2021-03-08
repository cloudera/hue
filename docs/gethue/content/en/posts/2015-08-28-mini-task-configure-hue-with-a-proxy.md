---
title: 'Mini task: Configure Hue with a Proxy'
author: admin
type: post
date: 2015-08-28T22:05:50+00:00
url: /mini-task-configure-hue-with-a-proxy/
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
categories:

---
We explained how to run Hue with [NGINX][1] serving the static files or under [Apache][2]. If you use another proxy, you might need to set these options:

<pre><code class="bash">[desktop]

\# Enable X-Forwarded-Host header if the load balancer requires it.

use_x_forwarded_host=false

\# Support for HTTPS termination at the load-balancer level with SECURE_PROXY_SSL_HEADER.

secure_proxy_ssl_header=false

</code></pre>

 [1]: https://gethue.com/using-nginx-to-speed-up-hue-3-8-0/
 [2]: https://gethue.com/how-to-run-hue-with-the-apache-server/
