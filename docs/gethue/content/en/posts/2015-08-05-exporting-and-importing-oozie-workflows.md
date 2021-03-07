---
title: Exporting and importing Oozie workflows directly from the UI
author: admin
type: post
date: 2015-08-05T19:28:28+00:00
url: /exporting-and-importing-oozie-workflows/
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
categories:
---

Until now Hue did not have a good way to backup or transfer workflows between servers. A [command][1] was added in [Hue 3.8][2] but its usage was still advanced.

In Hue 3.9, the command is directly integrated in the UI.

&nbsp;

{{< youtube JpLMLzUmzaE >}}

[<img src="https://cdn.gethue.com/uploads/2015/08/import-export-documents-1024x569.png" />][3]

Note that this export/import interface will be generic in Hue 4 and will support any document or script like Hive, Pig. In addition to exporting the Hue json document, sql or workflow.xml files will be included in the export.

Future improvements will make it easier to change the owner of the workflows without having to edit the json file manually.

&nbsp;

So it is time to build even more [workflows][4]! Feel free to comment on the [hue-user][5] list or [@gethue][6]!

[1]: https://gethue.com/export-and-import-your-oozie-workflows/
[2]: https://gethue.com/hue-3-8-with-an-oozie-editor-revamp-better-performances-improved-spark-ui-is-out/
[3]: https://cdn.gethue.com/uploads/2015/08/import-export-documents.png
[4]: https://gethue.com/new-apache-oozie-workflow-coordinator-bundle-editors/
[5]: http://groups.google.com/a/cloudera.org/group/hue-user
[6]: https://twitter.com/gethue
