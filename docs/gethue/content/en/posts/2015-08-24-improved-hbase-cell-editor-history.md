---
title: Improved HBase cell editor with history in Hue 3.9
author: admin
type: post
date: 2015-08-24T16:44:28+00:00
url: /improved-hbase-cell-editor-history/
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

For Hue 3.9 we've made some improvements to the HBase Browser that will make your life easier when editing cell contents.

&nbsp;

{{< youtube 62IWxigAyIc >}}

&nbsp;

In the full editor the cell history is now shown on the right-hand side and selecting an old entry will allow you to revert the current contents to that specific version. You can also look at historical entries while editing without loosing the current edited value, the current version is always shown on top of the list.

[<img src="https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.32.50-1024x503.png"  />][1]

When uploading binaries the editor will auto-sense the type and show it in the correct format. Before it was restricted to the initial type, so when uploading an image in a text cell it would show the binary string, now it shows the image.

[<img src="https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.34.44-1024x491.png"  />][2]

&nbsp;

As usual, feel free to send feedback on the [hue-user][3] list or [@gethue][4]!

&nbsp;

[1]: https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.32.50.png
[2]: https://cdn.gethue.com/uploads/2015/08/Screenshot-2015-08-20-16.34.44.png
[3]: http://groups.google.com/a/cloudera.org/group/hue-user
[4]: https://twitter.com/gethue
