---
title: Cloudera Enterprise 5.7 brings a faster and prettier SQL in Hue
author: admin
type: post
date: 2014-04-25T22:32:36+00:00
url: /cloudera-enterprise-5-7-brings-a-faster-and-prettier-hue-for-sql/
sf_remove_promo_bar:
  - 1
sf_caption_position:
  - caption-right
sf_right_sidebar:
  - Sidebar-1
sf_left_sidebar:
  - Sidebar-2
sf_sidebar_config:
  - left-sidebar
sf_related_articles:
  - 1
sf_social_sharing:
  - 1
sf_background_image_size:
  - cover
sf_page_title_text_style:
  - light
sf_page_title_bg:
  - none
sf_page_title_style:
  - standard
sf_page_title:
  - 1
sf_detail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_thumbnail_type:
  - none
categories:
#  - News
---

Cloudera Enterprise 5.7 brings a lot of changes (more than 1500) to HUE (the Web interface for querying and browsing data). The emphasize on performances and security continues from [5.5][1] as well as the improvement of the SQL user experience.

&nbsp;

## New Hive Metastore interface

The app is now single page and offers speed and more accessible statistics and data preview. See more of the improvements below or take a look at the following video demo.

{{< youtube MykO9McaxCk >}}

### New UI

**Fresh restart**

The front-end has been rewritten to be slicker and more user-friendly. More information is displayed and navigating across tabs is seamless as it no longer entails a page refresh.

<div id="attachment_3765" class="wp-caption aligncenter">
  <p>
    <a href="https://cdn.gethue.com/uploads/2016/02/blog-57-metastore-table.png" ><img class="wp-image-3765 size-large" src="https://cdn.gethue.com/uploads/2016/02/blog-57-metastore-table-1024x511.png" sizes="(max-width: 1024px) 100vw, 1024px" srcset="https://cdn.gethue.com/uploads/2016/02/blog-57-metastore-table-1024x511.png 1024w, /uploads/2016/02/blog-57-metastore-table-300x150.png 300w, /uploads/2016/02/blog-57-metastore-table-768x383.png 768w, /uploads/2016/02/blog-57-metastore-table-1280x639.png 1280w, /uploads/2016/02/blog-57-metastore-table-800x399.png 800w"  /></a>
  </p>

  <p class="wp-caption-text">
    Table specific page after
  </p>
</div>

<div id="attachment_3764" class="wp-caption aligncenter">
  <p>
    <a href="https://cdn.gethue.com/uploads/2016/02/blog-55-metastore-table.png.png" ><img class="wp-image-3764 size-large" src="https://cdn.gethue.com/uploads/2016/02/blog-55-metastore-table.png-1024x511.png" sizes="(max-width: 1024px) 100vw, 1024px" srcset="https://cdn.gethue.com/uploads/2016/02/blog-55-metastore-table.png-1024x511.png 1024w, /uploads/2016/02/blog-55-metastore-table.png-300x150.png 300w, /uploads/2016/02/blog-55-metastore-table.png-768x383.png 768w, /uploads/2016/02/blog-55-metastore-table.png-1280x638.png 1280w, /uploads/2016/02/blog-55-metastore-table.png-800x399.png 800w"  /></a>
  </p>

  <p class="wp-caption-text">
    Table specific page before
  </p>
</div>

&nbsp;

### Speed

&nbsp;

**Single page app**: first, now the initial page loads very quickly and fetches asynchronously the list of tables, table statistics, data sample, partition list. We are not blocking anymore until everything is queried in Hive. Subsequent navigation clicks will trigger only 1 or 2 calls to the server, instead of reloading all the page resources again. As an added bonus, the browser history now works on all the pages.

<img src="https://cdn.gethue.com/uploads/2016/02/meta-slow-1024x260.png" sizes="(max-width: 1024px) 100vw, 1024px" srcset="https://cdn.gethue.com/uploads/2016/02/meta-slow-1024x260.png 1024w, /uploads/2016/02/meta-slow-300x76.png 300w, /uploads/2016/02/meta-slow-768x195.png 768w, /uploads/2016/02/meta-slow-800x203.png 800w, /uploads/2016/02/meta-slow.png 1079w" /> <img src="https://cdn.gethue.com/uploads/2016/02/meta-quick.png" sizes="(max-width: 814px) 100vw, 814px" srcset="https://cdn.gethue.com/uploads/2016/02/meta-quick.png 814w, /uploads/2016/02/meta-quick-300x98.png 300w, /uploads/2016/02/meta-quick-768x251.png 768w, /uploads/2016/02/meta-quick-800x261.png 800w" />

**Caching**: The new assist caches all the Hive metadata. The pages listing tables and database also point to the same cache, as well as the editor autocomplete. This means that now the fetching of thousand of Hive tables and databases will only happen once. On the Hive side, these calls have even been optimized for taking seconds instead of previously minutes ([HIVE-7575][2]).

<a href="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each1.png" ><img src="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each1.png" sizes="(max-width: 871px) 100vw, 871px" srcset="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each1.png 871w, /uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each1-300x236.png 300w, /uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each1-768x603.png 768w, /uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each1-800x628.png 800w" alt="New Metastore blog post caching and hue each(1)" width="871" height="684"  /></a>

**Don’t freeze my browser**: on top of the caching, Hue is now much smarter and only displays the elements visible on the screen. For example if the user has a list of 5000 tables, only tens of them will actually be rendered (the rendering is the costly part).

<a href="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each.png" ><img src="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each.png" sizes="(max-width: 442px) 100vw, 442px" srcset="https://cdn.gethue.com/uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each.png 442w, /uploads/2016/02/New-Metastore-blog-post-caching-and-hue-each-214x300.png 214w" /></a>

&nbsp;

(Read more [here][3]).

&nbsp;

## SQL Editor improvements

The most used app in HUE is getting a

- Format queries button
- Delete history button
- Fixed columns and rows headers for a smoother scrolling
- Hive on Spark support

[<img src="https://cdn.gethue.com/uploads/2014/04/editor-57-1024x499.png"  />][4]

##

## Security

- A timeout now logs out inactive user after `idle_session_timeout seconds`
- Optional custom security splash screen at log-in with `login_splash_html`
- [TLS certificate chain][5] support for HUE
- SAML
  - Password for the key_file was introduced with `key_file_password`
  - Customize your xmlsec1 binary by changing `xmlsec_binary`
  - Customize your [SAML username mapping][6]. It also supports syncing groups on login

[<img src="https://cdn.gethue.com/uploads/2014/04/hue-splash-login-small.png" />][7]

## Search suggest

Result in the Grid Widget can be plotted like in the SQL editor. This is ideal for clicking visualizing the rows returned by the search query.

[<img src="https://cdn.gethue.com/uploads/2014/04/search-grid-plot-1024x331.png" />][8]

Hue supports [Solr Suggesters][9] and makes your data easier to search! Suggester assists the user by proposing an auto-completable list of queries:

{{< youtube RupOQCy5DdA >}}

(Read more [here][10]).

## HDFS summary

Right click on a file or directory to access their disk space consumed, quotas and number of directories and files.

[<img src="https://cdn.gethue.com/uploads/2014/04/fb-summary-icon.png" />][11]

&nbsp;

## Oozie Improvements

- External Workflow Graph: This feature enables us to see the graph for workflows submitted form File-browser as well as the ones submitted from CLI.
- Dryrun Oozie job: The <tt>dryrun</tt> option tests running a workflow/coordinator/bundle job with given properties and does not create the job.
- Timezone improvements: All the times on the dashboard are now defaulted to browser timezone and submitting a coordinator/bundle no longer need UTC times.
- Emailing automatically on failure: Each kill node now embeds an optional email action. Edit a kill node to insert a custom message if case it gets called.

(Read more [here][12]).

[<img src="https://cdn.gethue.com/uploads/2016/03/timezone-1024x306.png" />][13]

&nbsp;

## Next Up!

Next CDH version (5.8) of Hue will be rebased on Hue 3.10 that was released this May. On top of hundreds of improvements it brings a revamp of the SQL editor and the home page!

&nbsp;

If you have any questions or feedback, feel free to comment here, on the [hue-user][14] list or via [@gethue][15]!

[1]: http://blog.cloudera.com/blog/2015/12/new-in-cloudera-enterprise-5-5-improvements-to-hue-for-automatic-ha-setup-and-more/
[2]: https://issues.apache.org/jira/browse/HIVE-7575
[3]: https://gethue.com/browsing-hive-tables-data-and-metadata-is-getting-faster-and-prettier/
[4]: https://cdn.gethue.com/uploads/2014/04/editor-57.png
[5]: https://issues.cloudera.org/browse/HUE-2582
[6]: https://github.com/romainr/custom_saml_backend
[7]: https://cdn.gethue.com/uploads/2014/04/hue-splash-login-small.png
[8]: https://cdn.gethue.com/uploads/2014/04/search-grid-plot.png
[9]: https://cwiki.apache.org/confluence/display/solr/Suggester
[10]: https://gethue.com/suggest-for-solr-search-dashboards/
[11]: https://cdn.gethue.com/uploads/2014/04/fb-summary-icon.png
[12]: https://gethue.com/oozie-improvements-in-hue-3-10/
[13]: https://cdn.gethue.com/uploads/2016/03/timezone.png
[14]: http://groups.google.com/a/cloudera.org/group/hue-user
[15]: https://twitter.com/gethue
