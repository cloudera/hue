---
title: How to change or reset a forgotten password?
author: admin
type: post
date: 2013-10-10T20:50:00+00:00
url: /password-management-in-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/63670895075/password-management-in-hue
tumblr_gethue_id:
  - 63670895075
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
slide_template:
  - default
categories:
  - Development

---
<p id="docs-internal-guid-624d5ce4-a420-2c73-133c-afd4d943f32f">
  <a href="https://gethue.com">Hue</a> is the web interface that improves the <a href="http://hadoop.apache.com/">Apache Hadoop</a> user experience. It’s a Django driven application and manages users accordingly. In this tutorial, we’ll be exploring the different options available for altering passwords in Hue using the default authentication backend (<a href="https://github.com/cloudera/hue/blob/branch-3.0/desktop/conf.dist/hue.ini#L95">AllowFirstUserBackend</a>).
</p>

# User Interface

Users can change their passwords via the “<User Name>” -> “Edit Profile” found in the top-right corner of Hue.<img src="https://lh6.googleusercontent.com/ELuiWDo62BBpXahfVnSOwqFPteO_qSDNuqKnAPTpdBBEn63E78QM7u3pwyYzuMqcbeRbTNFNUmqlvGzjwZhg2GBm9uhml4pHHk-Mu-Bln65SXsvkcGbNfr5V" alt="image" width="530px;" height="540px;" />

If a user cannot remember their password, the Hue administrator can change it for them via the user manager.<img src="https://lh6.googleusercontent.com/6BeIoLNKTgKRZR6wXT_mO-q1Mk8v7Ywpt5iY6tY8h-s603LSgg0_qbmkHv2_Aj-ZCWL16CIi0-qXu-LqZ9v970nv-gM_a7NmJi_tbyu7L9OQ1YfE4tw7XXxh" alt="image" width="624px;" height="109px;" />

If the Hue administrator loses their password, then a more technical approach must be taken.

# Programmatic

When a Hue administrator loses their password, a more programmatic approach is required to secure the administrator again. Hue comes with a wrapper around the python interpreter called the “shell” command. It loads all the libraries required to work with Hue at a programmatic level. To start the Hue shell, type the following command from the Hue installation root.

If using CM, export this variable in order to point to the correct database:

<pre><code class="bash">HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-id

echo $HUE_CONF_DIR

export HUE_CONF_DIR</code></pre>

Where <id> is the most recent ID in that process directory for hue-HUE_SERVER.

A quick way to get the correct directory is to use this script:

<pre><code class="bash">export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'\`"</code></pre>

Then:

<pre><code class="bash">cd /usr/lib/hue (or /opt/cloudera/parcels/CDH-XXXXX/share/hue if using parcels and CM)

build/env/bin/hue shell</code></pre>

The following is a small script, that can be executed within the Hue shell, to change the password for a user named “example”:

<pre><code class="python">from django.contrib.auth.models import User

user = User.objects.get(username='example')

user.set_password('some password')

user.save()

</code></pre>

The script can also be invoked in the shell by using input redirection (assuming the script is in a file named script.py):

<pre><code class="bash">build/env/bin/hue shell < script.py</code></pre>

# How to make a certain user a Hue admin

<pre><code class="bash">build/env/bin/hue shell</code></pre>

Then set these properties to true:

<pre><code class="python">from django.contrib.auth.models import User

a = User.objects.get(username='hdfs')

a.is_staff = True

a.is_superuser = True

a.set_password('my_secret')

a.save()

</code></pre>

# How to change or reset a forgotten password?

Go on the Hue machine, then in the Hue home directory and either type:

To change the password of the currently logged in Unix user:

<pre><code class="bash">build/env/bin/hue changepassword</code></pre>

If you don’t remember the admin username, create a new Hue admin (you will then also be able to login and could change the password of another user in Hue):

<pre><code class="bash">build/env/bin/hue createsuperuser</code></pre>

&nbsp;

# Summary

We hope this helps you manage your password and assists administrators when they’ve lost their own passwords. In a future blog post, we will detail other ways to authenticate with Hue.

Have any suggestions? Feel free to tell us what you think through [hue-user][1] or at [@gethue][2].

 [1]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
 [2]: https://twitter.com/gethue/
