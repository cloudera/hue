---
title: I put a proxy on Hue
author: admin
type: post
date: 2014-06-12T00:06:53+00:00
url: /i-put-a-proxy-on-hue/
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
  - Development

---
A Web proxy lets you centralize all the access to a certain URL and prettify the address (e.g. `ec2-54-247-321-151.compute-1.amazonaws.com --> demo.gethue.com`).

[<img src="https://cdn.gethue.com/uploads/2014/06/Screenshot-from-2014-06-11-174627.png" alt="Screenshot from 2014-06-11 17:46:27" width="268" height="34"  />][1]

Have you ever wondered how we got Hue working under a proxy on [demo.gethue.com][2]? (if you missed the Cluster setup video, [here][3] it is!)

Here's a sample configuration we use on our servers. We know the Apache web server pretty well so we went for it. We even configured the server to display a custom error page in case the Hue server is down/not working.

What you need to do is to install and enable the `mod_proxy` module (e.g. `a2enmod proxy_http`) and then configure the main virtual host (on Ubuntu it's `/etc/apache2/sites-available/000-default.conf`) to just proxy and reverse proxy any request to your Hue instance (and any HTTP 503 error to another path):

<pre><code class="xml"><VirtualHost *:80>

ProxyPreserveHost On

ProxyPass /error/ http://localhost:81/error/

ProxyPassReverse /error http://localhost:81/error/

ProxyPass / http://_HUE_INSTANCE_IP_:8888/ connectiontimeout=15 timeout=30

ProxyPassReverse / http://_HUE_INSTANCE_IP_:8888/

SetEnv proxy-nokeepalive 1

ErrorDocument 503 /error/

ServerName demo.gethue.com

</VirtualHost>

</code></pre>

Change `demo.gethue.com` with your qualified server name available on your internal or external DNS.

and then add an additional virtual host (running on a different port, 81 for instance, on `/etc/apache2/sites-available/001-error.conf`) to serve the error path you specified in the default vhost:

<pre><code class="xml"><VirtualHost *:81>

DocumentRoot /var/www/

</VirtualHost>

</code></pre>

in `/var/www` you need to have a folder `error` with an `index.html` inside (need inspiration? look [here!][4]) that is going to be displayed when Hue is not reachable.

The last thing we need to do is to tell Apache we are listening to the port 81 as well, so edit `/etc/apache2/ports.conf` and just add

<pre><code class="xml">

Listen 81

</code></pre>

After everything, let's restart Apache with `sudo service apache2 restart` and... et voila! You are good to go!

[<img class="aligncenter wp-image-1392" src="https://cdn.gethue.com/uploads/2014/06/Screenshot-from-2014-06-11-174411.png" alt="Screenshot from 2014-06-11 17:44:11" width="280" height="234"  />][5]

 [1]: https://cdn.gethue.com/uploads/2014/06/Screenshot-from-2014-06-11-174627.png
 [2]: http://demo.gethue.com
 [3]: https://gethue.com/hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/
 [4]: http://demo.gethue.com/error/
 [5]: https://cdn.gethue.com/uploads/2014/06/Screenshot-from-2014-06-11-174411.png
