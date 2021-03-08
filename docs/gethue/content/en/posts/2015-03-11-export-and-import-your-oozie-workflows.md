---
title: Export and import your Oozie workflows
author: admin
type: post
date: 2015-03-11T17:31:11+00:00
url: /export-and-import-your-oozie-workflows/
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
<span style="color: #ff0000;"><em>August 7th 2015 update: this post is now deprecated as of Hue 3.9:</em></span> [Exporting and importing Oozie workflows directly from the UI](https://gethue.com/exporting-and-importing-oozie-workflows/)
&nbsp;

There is no handy way to import and export your Oozie workflows until Hue 4 and [HUE-1660][1], but here is a manual workaround possible since Hue 3.8/CDH5.4 and its new Oozie Editor.

The previous methods were very error prone as they required to insert data in multiple tables at the same time. Now, there is only one record by workflow.

&nbsp;

**Export all workflows**

    ./build/env/bin/hue dumpdata desktop.Document2 --indent 2 -natural-foreign --natural-primary > data.json


&nbsp;

**Export specific workflows**

20000013 is the id you can see in the URL of the dashboard.

    ./build/env/bin/hue dumpdata desktop.Document2 --indent 2 -natural-foreign --natural-primary --pks=20000013 > data.json

You can specify more than one id:

    --pks=20000013,20000014,20000015

&nbsp;

**Load the workflows**

Then

    /build/env/bin/hue loaddata data.json

&nbsp;

**Refresh the documents**

Until we hit Hue 4, this step is required in order to make the imported documents appear:

    ./build/env/bin/hue sync_documents

&nbsp;

And that's it, the dashboards with the same IDs will be refreshed with the imported ones!

[<img src="https://cdn.gethue.com/uploads/2015/03/oozie-spark-1024x516.png" />][2]

&nbsp;

**Note**:

If the document with the same id already exists in the database, just set its id to null in data.json and it will be inserted as a new document.

    vim data.json

then change

    "pk": 16,

to

    "pk": null,

&nbsp;

**Note**:

If using CM, export this variable in order to point to the correct database:

    HUE_CONF_DIR=/var/run/cloudera-scm-agent/process/-hue-HUE_SERVER-id

    echo $HUE_CONF_DIR

    export HUE_CONF_DIR

Where <id> is the most recent ID in that process directory for hue-HUE_SERVER.

or even quicker

    export HUE_CONF_DIR="/var/run/cloudera-scm-agent/process/\`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE | tail -1 | awk '{print $9}'\`"



&nbsp;

Have any questions? Feel free to contact us on [hue-user][3] or [@gethue][4]!

 [1]: https://issues.cloudera.org/browse/HUE-1660
 [2]: https://cdn.gethue.com/uploads/2015/03/oozie-spark.png
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
