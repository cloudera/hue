---
title: How to run Hue with the Apache Server
author: admin
type: post
date: 2014-12-11T23:21:39+00:00
url: /how-to-run-hue-with-the-apache-server/
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
sf_thumbnail_image:
  - 1892
categories:

---
Hue ships out of the box with the HTTP server [CherryPy][1], but some users have expressed interest having [Apache HTTP 2][2] serve Hue with [mod_wsgi][3]. Their motivation is that they are more familiar with Apache or have already several Apache instances deployed.

It turns out it’s pretty simple to do. It only requires a small script, a Hue configuration option, and a configuration block inside Apache. This post describes how to have Apache serve the static content and run the Python code of Hue.

&nbsp;

This script (which was just added in [`desktop/core/desktop/wsgi.py`][4]) enables any Web server that speaks WSGI to launch Hue and route requests to it:

<pre><code class="python">

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "desktop.settings")

\# This application object is used by the development server

\# as well as any WSGI server configured to use this file.

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()</code></pre>

The next step disables booting Hue from the `runcpserver` command. In Cloudera Manager, go to **Hue** > **Configuration** > **Service-Wide** > **Advanced**, and add the following to the hue safety valve:

<pre><a href="https://cdn.gethue.com/uploads/2014/12/Untitled.png"><img src="https://cdn.gethue.com/uploads/2014/12/Untitled.png" /></a></pre>

If you are [running Hue outside of Cloudera Manager][5], modify `desktop/conf/hue.ini` with:

<pre><code class="bash">

[desktop]

...

enable_server=no

</code></pre>

The final step is to configure Apache to launch Hue by adding the following to the `apache.conf`:

<pre><code class="bash">WSGIScriptAlias / $HUE_PATH/desktop/core/src/desktop/wsgi.py

WSGIPythonPath $HUE_PATH/desktop/core/src/desktop:$HUE_PATH/build/env/lib/python2.7/site-packages

WSGIDaemonProcess $HOSTNAME home=$HUE_PATH python-path=$HUE_PATH/desktop/core/src/desktop:$HUE_PATH/build/env/lib/python2.7/site-packages threads=30

WSGIProcessGroup $HOSTNAME

<Directory $HUE_PATH/desktop/core/src/desktop>

<Files wsgi.py>

Order Deny,Allow

\# If apache 2.4

Require all granted

\# otherwise

\# Allow from all

\# Some systems, like Redhat, lock down /var/run, so you may need to change where to store the socket with:

\# WSGISocketPrefix run/wsgi

</Files>

</Directory>

</code></pre>

Where `$HOSTNAME` should be the hostname of the machine running Hue, and `$HUE_PATH` is where Hue is installed. If you’re using Cloudera Manager, by default it should be either `/usr/lib/hue` for a package install, or `/opt/cloudera/parcels/CDH/lib/hue` for a parcel install.

[<img src="https://cdn.gethue.com/uploads/2014/12/Untitled2.png"  />][6]

&nbsp;

Have any questions? Feel free to contact us on [hue-user][7] or [@gethue][8]!

 [1]: http://www.cherrypy.org/ "CherryPy"
 [2]: http://httpd.apache.org/ "Apache HTTP 2"
 [3]: https://code.google.com/p/modwsgi/
 [4]: https://github.com/cloudera/hue/blob/master/desktop/core/src/desktop/wsgi.py
 [5]: https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/
 [6]: https://cdn.gethue.com/uploads/2014/12/Untitled2.png
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue
