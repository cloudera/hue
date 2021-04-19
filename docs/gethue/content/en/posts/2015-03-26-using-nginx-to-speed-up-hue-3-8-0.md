---
title: Using NGINX to speed up Hue
author: admin
type: post
date: 2015-03-26T18:55:07+00:00
url: /using-nginx-to-speed-up-hue-3-8-0/
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
categories:
  - Development

---
# Need for Speed!

In the soon to be released Hue 3.8, we have added the ability to serve Hue’s static files (images, JavaScript, and etc) with an external server like [NGINX][1]. This allows us to dramatically cut down on the number of files served by the Hue application, making the whole user experience dramatically faster.

For example, in the old version of Hue, rendering the beeswax application on [demo.gethue.com][2] performs 73 requests in 3 seconds to download 2.5MB of data.

[<img src="https://cdn.gethue.com/uploads/2015/03/without-nginx.png" />][3]

&nbsp;

In comparison, in Hue 3.8 behind NGINX, rendering that same page performs 5 requests for 130KB in 0.7 seconds.

# [<img src="https://cdn.gethue.com/uploads/2015/03/with-nginx.png" />

][4]

# Configuring NGINX

The simplest option is to just follow the instructions described in [Automatic High Availability with Hue and Cloudera Manager][5], which we’ve updated to support this optimization. Or if you want to just set up a simple NGINX configuration, you can install NGINX on Redhat systems with:

<pre><code class="bash">

% yum install nginx

</code></pre>

Or on a Debian/Ubuntu system with:

<pre><code class="bash">

% apt-get install nginx

</code></pre>

Next, add a `/etc/nginx/conf.d/hue.conf` file with the following contents. Make sure to tweak `server_name` to this machine's hostname (or just localhost), the `alias` to point at Hue's static files, and the `server` to point at the Hue instance. Note that if you're running multiple Hue instances, be sure to use a database like MySQL, PostgreSQL, or Oracle which allows for remote access:

<pre><code class="bash">

server {

server_name NGINX_HOSTNAME;

charset utf-8;

listen 8001;

\# Or if running hue on https://

\## listen 8001 ssl;

\## ssl_certificate /path/to/ssl/cert;

\## ssl_certificate_key /path/to/ssl/key;

location / {

proxy_pass http://hue;

\# Or if the upstream Hue instances are running behind https://

\## proxy_pass https://hue;

}

location /static/ {

\# Uncomment to expose the static file directories.

\## autoindex on;

\# If Hue was installed with packaging install:

alias /usr/lib/hue/build/static/;

\# Or if on a parcel install:

\## /opt/cloudera/parcels/CDH/lib/hue/build/static/;

expires 30d;

add_header Cache-Control public;

}

}

upstream hue {

ip_hash;

\# List all the Hue instances here for high availability.

server HUE_HOST1:8888 max_fails=3;

server HUE_HOST2:8888 max_fails=3;

...

}

</code></pre>

Finally, start NGINX with `sudo service nginx start` and navigate to http://NGINX_HOSTNAME:8001.

As usual feel free to comment on the [hue-user][6] list or [@gethue][7]!

&nbsp;

**Note for HTTPS**

After changing X-Forwarded-Proto to X-Forwarded-Protocol in the Load Balancer configuration the rewrite from http to https worked

 [1]: http://nginx.org/
 [2]: http://demo.gethue.com/beeswax/#query
 [3]: https://cdn.gethue.com/uploads/2015/03/without-nginx.png
 [4]: https://cdn.gethue.com/uploads/2015/03/with-nginx.png
 [5]: https://gethue.com/automatic-high-availability-with-hue-and-cloudera-manager/
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: https://twitter.com/gethue
