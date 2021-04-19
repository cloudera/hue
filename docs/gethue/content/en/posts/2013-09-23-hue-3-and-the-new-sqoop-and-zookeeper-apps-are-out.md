---
title: Hue 3 and the new Sqoop and ZooKeeper apps are out!
author: admin
type: post
date: 2013-09-23T20:40:00+00:00
url: /hue-3-and-the-new-sqoop-and-zookeeper-apps-are-out/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/62087732649/hue-3-and-the-new-sqoop-and-zookeeper-apps-are-out
tumblr_gethue_id:
  - 62087732649
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
  - Release

---
## Hi Big Data Surfers,

<span id="docs-internal-guid-0768643e-1223-5a03-20cc-6cb512e36ff6">The Hue team is pleased to bring you Hue 3.0, available as a </span>[tarball][1]{.trackLink} release.

Please see the [release notes][2] for more information and the <a href="http://cloudera.github.io/hue/docs-3.0.0/" target="_blank" rel="noopener noreferrer">documentation</a>.

Hue 3.0 brings a browser for ZooKeeper and 245 commits. The tech stack was upgraded and a new phase of redesign was performed in order to improve the UX.

## Notable Features

  * <span><span>Sqoop</span></span>&nbsp;
    <span>With the Sqoop 2 application data from databases can be easily exported or imported into HDFS in a scalable way. The Job Wizard hides the </span><span><span>complexity of creating Sqoop jobs and the dashboard offers a live progress and log access.</span></span><a href="https://cdn.gethue.com/downloads/screenshots/hue-3-sqoop.png" target="_blank" rel="noopener noreferrer"><img alt="image" src="https://cdn.gethue.com/downloads/screenshots/hue-3-sqoop.png" width="900" /></a></li>

      * <span><span>ZooKeeper</span></span>&nbsp;
        <span>Navigate and browse the Znode hierarchy and content of a Zookeeper cluster. Znodes can be added, deleted and edited.<br /> </span><span><span>Multi-clusters are supported and their various statistics are available.</span></span><a href="https://cdn.gethue.com/downloads/screenshots/hue-3-zoo.png" target="_blank" rel="noopener noreferrer"><img alt="image" src="https://cdn.gethue.com/downloads/screenshots/hue-3-zoo.png" width="900" /></a></li>

          * <span><span>Shell app is removed and replaced by Pig Editor, HBase Browser and the Sqoop apps.</span></span>&nbsp;
          * <span><span>Python 2.6 is required.</span></span>&nbsp;
          * <span><span>Beeswax daemon is replaced by HiveServer2.</span></span>&nbsp;</ul>

        ## Notable Fixes

          * <span>HUE-897 [core] Redesign of the overall layout</span>
          * <span>HUE-1521 [core] Improve JT HA</span>
          * <span>HUE-1493 [beeswax] Replace Beeswaxd by HiveServer2</span>
          * <span>HUE-1474 [core] upgrade django from 1.2 to 1.4</span>
          * <span>HUE-1506 [search] Impersonation support</span>
          * <span>HUE-1475 [core] Switch back from spawning server</span>

        <span> </span>

        <span id="docs-internal-guid-0768643e-1223-9198-1d84-c7ebd87794ae">Thank you for all the</span>[ bugs, suggestions, and feedback][3]<span> and stay tuned, a few major changes could not make it to 3.0 but will land soon!</span>

        <span>Follow @<a class="tumblelog" href="http://tmblr.co/mjrjfJ-GIti18oBq2GmTjjA">gethue</a> for the latest updates!</span>

        <span> </span>

        The Hue team

 [1]: https://cdn.gethue.com/downloads/releases/3.0.0/hue-3.0.0.tgz
 [2]: https://gethue.com
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
