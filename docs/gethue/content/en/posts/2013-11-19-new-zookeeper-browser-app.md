---
title: New ZooKeeper Browser app!
author: admin
type: post
date: 2013-11-19T18:48:00+00:00
url: /new-zookeeper-browser-app/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/67482299450/new-zookeeper-browser-app
tumblr_gethue_id:
  - 67482299450
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
---

<p id="docs-internal-guid-63af2251-71ae-f7cf-e3d8-973b2294f38b">
  Hello animal lovers, in <a href="http://gethue.tumblr.com/post/62087732649/hue-3-and-the-new-sqoop-and-zookeeper-apps-are-out">Hue 3</a>, a new application was added in order to make <a href="http://zookeeper.apache.org/">Apache ZooKeeper</a> easier to use: ZooKeeper Browser.
</p>

&nbsp;

The app is not totally new: it consists of a rebasing from Hue 1 to Hue 3 of the [ZooKeeper UI][1] made by Andrei during his Google Summer of Code 3 years ago.

{{< youtube jvlKiZYf9Ys >}}

The main two features are:

- Listing of the ZooKeeper cluster stats and clients
- Browsing and editing of the ZNode hierarchy

&nbsp;

ZooKeeper Browser requires the [ZooKeeper REST][2] service to be running on the same host as ZooKeeper itself. Here is how to set it up:

&nbsp;

First get and build ZooKeeper:

<pre class="code">git clone <a href="https://github.com/apache/zookeeper">https://github.com/apache/zookeeper</a>
cd zookeeper
ant
Buildfile: /home/hue/Development/zookeeper/build.xml

init:
    [mkdir] Created dir: /home/hue/Development/zookeeper/build/classes
    [mkdir] Created dir: /home/hue/Development/zookeeper/build/lib
    [mkdir] Created dir: /home/hue/Development/zookeeper/build/package/lib
    [mkdir] Created dir: /home/hue/Development/zookeeper/build/test/lib

…</pre>

Then start the REST service:

<pre class="code">cd src/contrib/rest
nohup ant run&</pre>

&nbsp;

If ZooKeeper and the REST service are not on the same machine as Hue, please update the [Hue settings][3] and specify the correct hostnames and ports:

&nbsp;

<pre class="code">[zookeeper]

  [[clusters]]

    [[[default]]]
      # Zookeeper ensemble. Comma separated list of Host/Port.
      # e.g. localhost:2181,localhost:2182,localhost:2183
      host_ports=localhost:2181

      # The URL of the REST contrib service
      rest_url=http://localhost:9998</pre>

&nbsp;

And that’s it, jump up to [ZooKeeper Browser][4]!

&nbsp;

As usual feel free to comment on the [hue-user][5] list or [@gethue][6]!

&nbsp;

[1]: https://github.com/andreisavu/hue/tree/zookeeper-browser/
[2]: https://github.com/apache/zookeeper/tree/trunk/src/contrib/rest
[3]: https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L591
[4]: http://127.0.0.1:8888/zookeeper/
[5]: http://groups.google.com/a/cloudera.org/group/hue-user
[6]: http://twitter.com/gethue
