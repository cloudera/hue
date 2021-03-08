---
title: Oozie Dashboard Improvements
author: admin
type: post
date: 2015-04-10T22:07:31+00:00
url: /oozie-dashboard-improvements/
sf_page_title_style:
  - standard
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_detail_type:
  - none
sf_page_title:
  - 1
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

In the upcoming Hue 3.8, Oozie Dashboard just got several improvements making them and their navigation even more intuitive (for the Editor revamp, see [this][1]). Here is a video demo that sums them up:

{{< youtube U4L_qlNhjcc >}}

**New Oozie features**

In Workflow dashboard:

- Job parent column (parent can be nothing or a workflow or a coordinator)
- Job parent “Submitted by” filter

---

[<img src="https://cdn.gethue.com/uploads/2015/04/parent-1024x835.png"/>][2]\*\*\*\*

&nbsp;

- Navigate to Sub-Workflow action and editor pages from a submitted workflow graph

[<img src="https://cdn.gethue.com/uploads/2015/04/graph-1024x642.png"/>][3]

&nbsp;

- Navigate to parent Job from an action/workflow in a submitted Workflow

[<img src="https://cdn.gethue.com/uploads/2015/04/navigate-1024x414.png"/>][4]

&nbsp;

- Update end time of running Coordinator

[<img src="https://cdn.gethue.com/uploads/2015/04/endtime-1024x630.png"/>][5]

&nbsp;

**Next !**

A lot more is coming up:

- Faster log retrieval
- [Live graph display][6] of any running Workflow
- [Smarter file symlinking][7] in Workflow action
- [Coordinator actions pagination][8]

and rebasing the workflow dashboard on the editor is being evaluated. Stay tuned!

&nbsp;

As usual feel free to comment on the [hue-user][9] list or [@gethue][10]!

&nbsp;

[1]: https://gethue.com/new-apache-oozie-workflow-coordinator-bundle-editors/
[2]: https://cdn.gethue.com/uploads/2015/04/parent.png
[3]: https://cdn.gethue.com/uploads/2015/04/graph.png
[4]: https://cdn.gethue.com/uploads/2015/04/navigate.png
[5]: https://cdn.gethue.com/uploads/2015/04/endtime.png
[6]: https://issues.cloudera.org/browse/HUE-2659
[7]: https://issues.cloudera.org/browse/HUE-1922
[8]: https://issues.cloudera.org/browse/HUE-2292
[9]: http://groups.google.com/a/cloudera.org/group/hue-user
[10]: https://twitter.com/gethue
