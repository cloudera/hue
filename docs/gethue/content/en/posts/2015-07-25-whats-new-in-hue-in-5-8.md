---
title: What’s new in Hue in CDH 5.8
author: admin
type: post
date: 2015-07-25T20:09:53+00:00
url: /whats-new-in-hue-in-5-8/
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
sf_remove_promo_bar:
  - 1
categories:
---

[Cloudera Enterprise 5.8][1] brings the latest Hue 3.10, the Web UI that makes Hadoop easier to use.

&nbsp;

The focus on performances on the user experience continues from [C5.7][2], with a revamped SQL Editor that will make you productive with Hive and Impala queries. This new version is also available for a quick try in one click on [demo.gethue.com][3]!

Here is a description of the main improvements.

## New SQL Editor

Hue now has a generic editor that supports any languages but currently focuses on SQL. It is a single page app that is much slicker than before and simpler to use. Here is a list of the new functionalities and a video demo that show them in action:

- Switch between queries without any page reload
- Live history of running and past queries
- Query result grid is simplified and lets you refine your results
- Code editor has more operations like autocomplete values, search and replace, fold code, go to line number
- [Drag & Drop saved queries into workflows][4]

{{< youtube LvTWPgkrdvM >}}

<figure><a href="https://cdn.gethue.com/uploads/2016/06/editor-grid-1024x524.png"><img src="https://cdn.gethue.com/uploads/2016/06/editor-grid-1024x524.png" /></a><figcaption>The new look of the editor</figcaption></figure>

&nbsp;

Read more [about it here...][6]

&nbsp;

## New home page

Hue documents can now be managed via an intuitive directory and file-based interface. Rather than utilizing the tag-based system from older versions of Hue, users can create their own directories and subdirectories and drag and drop documents within the simple filebrowser interface. Users can import and export documents or directories directly from the Home Page. Users can easily share a folder or document with other users or groups by selecting the desired item(s) and selecting “Share” in the contextual menu or in the top right icon menu.

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2016/06/create_directory.gif" />][7]

&nbsp;

Read more [about it here...][8]

&nbsp;

## CM database wizard

In order to support [the native Load Balancer][9] for High Availability and 10x more performances, Hue needs to be configured with a robust database like MySQL, PostgreSQL or Oracle. The setup can now be done directly from the CM interface which will let you enter the properties and test the connection of the Hue service. Additional new Hue instances will automatically be configured for you.

[<img src="https://cdn.gethue.com/uploads/2016/06/cm-db-wizard-1024x409.png" />][10]

&nbsp;

## Sentry Solr UI

The Sentry app now let’s you edit Apache Solr Collection privileges via a Web UI (instead of a configuration file). [Apache Sentry][11] allows you to define via privileges who can access or update data. It previously only had editing capabilities for Hive tables. It becomes now much easier to control the authorization of all your Solr indexes and leverage the [Dynamic Search dashboards][12].

[<img src="https://cdn.gethue.com/uploads/2016/05/solr-secu-1024x624.png" />][13]

Read more [about it here...][14]

&nbsp;

## Idle Session Timeout

An additional security feature for Hue administrators to enforce and manage idle session timeouts in Hue. We’ve also improved the experience of re-authenticating into Hue when a user’s session is timed out by introducing a new login modal that prevents the user from losing his current work.

[<img src="https://cdn.gethue.com/uploads/2016/02/loginmodal.gif" />][15]

Read more [about it here...][16]

## Next Up!

More SQL improvements and optimizations are in the pipeline. In the top three, a brand new SQL autocomplete will assist users even with their giant queries, large query results browsing and export will scale and queries can be scheduled to run repetitively in just a click.

If you have any questions, feel free to comment here, on the [hue-user][17] list or via [@gethue][18]!

##

[1]: http://blog.cloudera.com/blog/2016/07/cloudera-enterprise-5-8-is-now-available/
[2]: http://blog.cloudera.com/blog/2016/05/new-in-cdh-5-7-improved-performance-security-and-sql-experience-in-hue/
[3]: http://demo.gethue.com
[4]: https://gethue.com/drag-drop-saved-hive-queries-into-your-workflows/
[5]: https://cdn.gethue.com/uploads/2016/06/editor-grid.png
[6]: https://gethue.com/new-sql-editor/
[7]: https://cdn.gethue.com/uploads/2016/06/create_directory.gif
[8]: https://gethue.com/introducing-hues-new-home-page/
[9]: http://blog.cloudera.com/blog/2015/12/new-in-cloudera-enterprise-5-5-improvements-to-hue-for-automatic-ha-setup-and-more/
[10]: https://cdn.gethue.com/uploads/2016/06/cm-db-wizard.png
[11]: https://sentry.apache.org/
[12]: https://gethue.com/dynamic-search-dashboard-improvements-3/
[13]: https://cdn.gethue.com/uploads/2016/05/solr-secu.png
[14]: https://gethue.com/ui-to-edit-sentry-privilege-of-solr-collections/
[15]: https://cdn.gethue.com/uploads/2016/02/loginmodal.gif
[16]: https://gethue.com/introducing-the-new-login-modal-and-idle-session-timeout/
[17]: http://groups.google.com/a/cloudera.org/group/hue-user
[18]: https://twitter.com/gethue
