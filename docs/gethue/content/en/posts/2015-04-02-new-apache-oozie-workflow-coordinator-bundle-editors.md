---
title: 'New Apache Oozie Workflow, Coordinator & Bundle Editors'
author: admin
type: post
date: 2015-04-02T16:39:22+00:00
url: /new-apache-oozie-workflow-coordinator-bundle-editors/
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

Oozie is one of the [initial major][1] first app in Hue. We are continuously investing in making it better and just did a major jump in its editor (to learn about the improvements in the Dashboard in <a href="https://gethue.com/oozie-dashboard-improvements/" target="_blank" rel="noopener noreferrer">the other post</a>).

This revamp of the Oozie Editor brings a new look and requires much less knowledge of [Oozie][2]! Workflows now support tens of [new functionalities][3] and require just a few clicks to be set up!

&nbsp;

{{< youtube ON15jrXpqeI >}}

&nbsp;

The files used in the videos comes with the [Oozie Examples][4].

In the new interface, only the most important properties of an action are asked to be filled, and quick-links for verifying path and other jobs are offered. Hive and Pig script files are parsed in order to extract the parameters and directly propose them with autocomplete. The advanced functionalities of an action are available in a new kind of popup with much less frictions, as it just overlaps with the current node.

&nbsp;

<figure><a href="https://cdn.gethue.com/uploads/2015/03/new-oozie-1024x557.png"><img src="https://cdn.gethue.com/uploads/2015/03/new-oozie-1024x557.png" /></a><figcaption>New Editor</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor-1024x602.png"><img src="https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor-1024x602.png" /></a><figcaption>New Editor (edit mode)</figcaption></figure>

<figure><a href="https://cdn.gethue.com/uploads/2015/03/old-oozie-1024x561.png"><img src="https://cdn.gethue.com/uploads/2015/03/old-oozie-1024x561.png" /></a><figcaption>Old Editor</figcaption></figure>

&nbsp;

Two new actions have been added:

- HiveServer2
- Spark

[<img src="https://cdn.gethue.com/uploads/2015/03/new-spark-hs2-actions.png"  />][8]

And the user experience o Pig and Sub-workflows is simplified.

&nbsp;

Decision node support has been improved, copying an existing action is also now just a way of drag & dropping. Some layout are now possible as the 'ok' and 'end' nodes can be individually changed.

[<img src="https://cdn.gethue.com/uploads/2015/03/oozie-avanced-action-options.png" />][9]

&nbsp;

Coordinators have been vastly improved! The notion of Oozie datasets is not needed anymore. The editor pulls the parameters of your workflow and offers 3 types of inputs:

- **parameters**: constant or Oozie EL function like time
- **input path**: parameterize an input path dependency and wait for it to exist, e.g.
- **output path**: like an input path but does not need to exist for starting the job

[<img src="https://cdn.gethue.com/uploads/2015/03/oozie-new-coordinator-1024x376.png" />][10]

&nbsp;

The dreaded UTC time zone format is not directly provided either by the calendar or with some helper widgets.

[<img src="https://cdn.gethue.com/uploads/2015/03/oozie-new-submit-popup.png" />][11]

&nbsp;

**Sum-up**

In addition to providing a friendlier end user experience, this new architecture opens up for innovations.

First, it makes it easy to add new Oozie actions in the editor. But most importantly, workflows are persisted using the new Hue document model, meaning their [import/export][12] is simplified and will be soon available directly from the UI. This model also enables the future generation of your workflows by just drag & dropping saved Hive, Pig, Spark jobs directly in the workflow. No need to manually duplicate your queries on HDFS!

This also opens the door of one click scheduling of any jobs saved in Hue as the coordinators are much simpler to use now. While we are continuing to polish the new editor, the [Dashboard section][13] of the app will see a major revamp next!

&nbsp;

As usual feel free to comment on the [hue-user][14] list or [@gethue][15]!

&nbsp;

**Note**

Old workflows are not automatically convert to the new format. Hue will try to import them for you, and open them in the old editor in case of problems.

[<img src="https://cdn.gethue.com/uploads/2015/03/oozie-import-try-1024x566.png" />][16]

A new [export and / export][17] is planned for Hue 4. It will let you export workflows in both XML / JSON Hue format and import from Hue’s format.

[1]: https://gethue.com/category/oozie/
[2]: http://oozie.apache.org/
[3]: https://issues.cloudera.org/browse/HUE-2180
[4]: https://github.com/cloudera/hue/tree/master/apps/oozie/examples/workflows
[5]: https://cdn.gethue.com/uploads/2015/03/new-oozie.png
[6]: https://cdn.gethue.com/uploads/2015/03/oozie-v2-editor.png
[7]: https://cdn.gethue.com/uploads/2015/03/old-oozie.png
[8]: https://cdn.gethue.com/uploads/2015/03/new-spark-hs2-actions.png
[9]: https://cdn.gethue.com/uploads/2015/03/oozie-avanced-action-options.png
[10]: https://cdn.gethue.com/uploads/2015/03/oozie-new-coordinator.png
[11]: https://cdn.gethue.com/uploads/2015/03/oozie-new-submit-popup.png
[12]: https://gethue.com/export-and-import-your-oozie-workflows/
[13]: https://issues.cloudera.org/browse/HUE-2644
[14]: http://groups.google.com/a/cloudera.org/group/hue-user
[15]: https://twitter.com/gethue
[16]: https://cdn.gethue.com/uploads/2015/03/oozie-import-try.png
[17]: https://issues.cloudera.org/browse/HUE-1660
