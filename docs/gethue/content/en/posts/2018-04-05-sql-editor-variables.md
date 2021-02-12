---
title: SQL editor variables
author: admin
type: post
date: 2018-04-05T22:59:23+00:00
url: /sql-editor-variables/
ampforwp-amp-on-off:
  - default
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
categories:
  - Querying
  - Version 4

---
_Update June 5th 2018: boolean variables were introduced in 4.3_

<p class="p1">
  Greetings SQL aficionados!
</p>

<p class="p1">
  We've been looking for ways to do small steady improvements to the usability of our editors.
</p>

## Sharing

In Hue 4.1, we added the ability to share any query you've saved with other Hue users so that you can collaborate and share your hard work. To share, access the editor right hand menu.

<img src="https://cdn.gethue.com/uploads/2018/04/btn_share.png" class="alignnone size-full wp-image-5323" />

<p class="p1">
  Once there, you have autocomplete for the users in Hue and you can decide if they should have write access.
</p>

<img src="https://cdn.gethue.com/uploads/2018/04/modal_share.png" class="alignnone size-medium wp-image-5318" />

## Variables

<p class="p1">
  For some time, you've been able to define variables in SQL queries so that you could easily configure parameters in queries. Variables are also a great way to allow other users to customize shared queries with the values they need.
</p>

<img src="https://cdn.gethue.com/uploads/2018/04/variables_basic.png" class="alignnone size-medium wp-image-5319" />

<pre><code class="bash">
select * from web_logs where country_code = "${country_code}"
</code></pre>

<p class="p1">
  In Hue 4.1, we've added the ability to add default values to your variables. Default values can be of two types:
</p>

**Single Valued**

<pre><code class="bash">
select * from web_logs where country_code = "${country_code=US}"
</code></pre>

**Multi Valued**

<pre><code class="bash">
select * from web_logs where country_code = "${country_code=CA, FR, US}"
</code></pre>

<p class="p1">
  In addition, the displayed text for multi valued variables can be changed.
</p>

<pre><code class="bash">
select * from web_logs where country_code = "${country_code=CA(Canada), FR(France), US(United States)}"
</code></pre>

<img src="https://cdn.gethue.com/uploads/2018/04/variables_multi.png" class="alignnone size-full wp-image-5321" />

<p class="p1">
  In Hue 4.3, we're adding the ability to display the column assist when clicking on the variable name, which should be handy when figuring out which value to use.
</p>

<img src="https://cdn.gethue.com/uploads/2018/04/variables_popover.png" class="alignnone size-full wp-image-5322" />

<p class="p1">
  If you're like us, remembering the correct format for dates and timestamps is the last thing you have on your mind. When the data type for the column is available in the metastore for the aforementioned types, Hue will default the value to today's date and you'll be able to pick the date from a calendar.
</p>

<img src="https://cdn.gethue.com/uploads/2018/04/variables_calendar.png" class="alignnone size-medium wp-image-5320" />

<p class="p1">
  In Hue 4.3, we made a small improvement by displaying checkbox when using boolean values as the data type.
</p>

<img src="https://cdn.gethue.com/uploads/2018/04/Screen-Shot-2018-06-04-at-4.52.44-PM.png" class="size-full wp-image-5387" />

<p class="p1">
  <h2 class="p1">
    Help<br />
  </h2>

  <p>
    Finally, if you forget how to use these new features, fret not. We've added a new help button <a href="https://cdn.gethue.com/uploads/2018/04/button_help.png"><img src="https://cdn.gethue.com/uploads/2018/04/button_help.png"class="alignnone size-full wp-image-5316" /></a> in the editor that recaps this information and more.<br /> <a href="https://cdn.gethue.com/uploads/2018/04/Screen-Shot-2018-06-05-at-8.59.40-AM.png"><img src="https://cdn.gethue.com/uploads/2018/04/Screen-Shot-2018-06-05-at-8.59.40-AM.png"/></a>
  </p>

  <p class="p1">
    As always, if you have any questions, feel free to comment here or on the <a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user list</a> or <a href="https://twitter.com/gethue">@gethue</a>!
  </p>

 [1]: https://cdn.gethue.com/uploads/2018/04/btn_share.png
 [2]: https://cdn.gethue.com/uploads/2018/04/modal_share.png
 [3]: https://cdn.gethue.com/uploads/2018/04/variables_basic.png
 [4]: https://cdn.gethue.com/uploads/2018/04/variables_multi.png
 [5]: https://cdn.gethue.com/uploads/2018/04/variables_popover.png
 [6]: https://cdn.gethue.com/uploads/2018/04/variables_calendar.png
 [7]: https://cdn.gethue.com/uploads/2018/04/Screen-Shot-2018-06-04-at-4.52.44-PM.png
