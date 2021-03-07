---
title: Add a top banner to Hue!
author: admin
type: post
date: 2015-03-26T17:05:02+00:00
url: /add-a-top-banner-to-hue/
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
We have already seen <a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank" rel="noopener noreferrer">in this post</a> how you can configure Hue in your cluster. But did you know that there’s a property that can make a top banner appear in your Hue installation? [<img src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.33.12-1024x610.png"  />][1] This is quite useful if you want for instance to show a disclaimer to your users, or to clearly mark a testing or production environment, or if you want to display some dynamic information there. Depending on if you are using <a href="https://gethue.com/hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/" target="_blank" rel="noopener noreferrer">Cloudera Manager</a> or not, you should either add a safety valve or edit a .ini file to use this feature. For details on how to change the configuration, <a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank" rel="noopener noreferrer">read here</a>. In the desktop/custom section of the ini file you can find the banner_top_html property:

<pre><code class="bash">[desktop]

[[custom]]

\# Top banner HTML code

banner_top_html=

</code></pre>

Then it’s just a matter of writing some HTML/CSS and even Javascript code to customized it as you prefer. Keep in mind that you have a limited height to do that (30px). For instance, to write a the same message you see on <a href="demo.gethue.com" target="_blank" rel="noopener noreferrer">demo.gethue.com</a>, you can write this:

<!--email_off-->

<pre><code class="bash">[desktop]

[[custom]]

\# Top banner HTML code

banner_top_html='<div style="padding: 4px; text-align: center; background-color: #EEE; height: 40px"><i class="fa fa-flash muted"></i> This is Hue 3.11 read-only demo - <a href="https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/" target="_blank">Read more about it</a> or <a href="/notebook/editor?editor=11">open a sample query</a>! <i class="fa fa-flash muted"></i></div>'

</code></pre>

<!--/email_off-->Or we could even use a very old HTML tag to display a running ticker!

<pre><code class="bash">[desktop]

[[custom]]

\# Top banner HTML code

banner_top_html='<marquee behavior="scroll" direction="left" scrollamount="2" style="font-size: 15px;padding: 5px;color:#338BB8;font-weight:bold">Welcome to the test environment.</marquee>'

</code></pre>

[<img src="https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-18.56.32-1024x610.png"  />][2].

Pretty cool, uh? Now it’s your turn to create something useful with it! As usual feel free to comment on the [hue-user][3] list or [@gethue][4]!

 [1]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-16.33.12.png
 [2]: https://cdn.gethue.com/uploads/2015/03/Screenshot-2015-03-23-18.56.32.png
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
