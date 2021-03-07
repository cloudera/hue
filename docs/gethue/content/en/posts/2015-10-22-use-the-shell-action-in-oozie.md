---
title: Use the Shell Action in Oozie
author: admin
type: post
date: 2015-10-22T21:49:27+00:00
url: /use-the-shell-action-in-oozie/
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
ampforwp-amp-on-off:
  - default
categories:

---
The following steps will successfully guide you to execute a Shell Action form [Oozie Editor][1].

If the executable is a standard Unix command, you can directly enter it in the `Shell Command` field and click Add button.

[<img class="alignnone wp-image-3402 size-full" src="https://cdn.gethue.com/uploads/2015/10/1.png" />][2]

Arguments to the command can be added by clicking the `Arguments+` button.

[<img class="alignnone wp-image-3393 size-full" src="https://cdn.gethue.com/uploads/2015/10/2.png" />][3]

${VARIABLE} syntax will allow you to dynamically enter the value via Submit popup.

[<img class="alignleft wp-image-3409 size-full" src="https://cdn.gethue.com/uploads/2015/10/31.png" />][4][<img class="alignnone wp-image-3412 size-full" src="https://cdn.gethue.com/uploads/2015/10/4.png" />][5]

If using Hue version less than 4.3 (it is automated from then):

If the executable is a script instead of a standard UNIX command, it needs to be copied to HDFS and the path can be specified by using the File Chooser in `Files+` field.

<pre><code class="bash">#!/usr/bin/env bash

sleep

</code></pre>

[<img class="alignnone wp-image-3417 size-full" src="https://cdn.gethue.com/uploads/2015/10/5.png" />][6]

Additional Shell-action properties can be set by clicking the settings button at the top right corner.

Next version will support direct script path along with standard UNIX commands in `Shell Command` field making it even more intuitive.

 [1]: https://gethue.com/new-apache-oozie-workflow-coordinator-bundle-editors/
 [2]: https://cdn.gethue.com/uploads/2015/10/1.png
 [3]: https://cdn.gethue.com/uploads/2015/10/2.png
 [4]: https://cdn.gethue.com/uploads/2015/10/31.png
 [5]: https://cdn.gethue.com/uploads/2015/10/4.png
 [6]: https://cdn.gethue.com/uploads/2015/10/5.png
