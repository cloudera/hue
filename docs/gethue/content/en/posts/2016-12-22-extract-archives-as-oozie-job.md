---
title: Upload large archive files to HDFS and extract them in the background
author: admin
type: post
date: 2016-12-22T00:38:34+00:00
url: /extract-archives-as-oozie-job/
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

---
Hello Hue users,

Hue supports extraction of _Zip_, _Tgz_ and _Bz2_ archives via _File Browser_ app. With this [improvement][1], you will be able to perform the archive extraction as an external Oozie job that has no performance impact on Hue. Here are the steps to achieve this.

First, upload the archive as a file using the [File Browser][2] app.

[<img src="https://cdn.gethue.com/uploads/2016/12/fb-upload1.png" width="2526" height="475" />][3]

Select the archive you want to extract and you will notice that `Submit` button appear besides the `Trash` button.[<img src="https://cdn.gethue.com/uploads/2016/12/extract-button.png" width="1239" height="391" />][4]

After clicking the `Submit` button and confirming the job submission, you can go to the Oozie dashboard page to check the progress of the job. In the next release, we will show how to monitor the progress of the job without even going to the Oozie dashboard and be notified of the completion by email.

[<img src="https://cdn.gethue.com/uploads/2016/12/oozie-job2.png" width="1182" height="377" />][5]

Once the job finishes, you can find the extracted contents in the same HDFS folder.

### Note

Flag to enable this feature until Hue 4:

<pre><code class="bash">

[filebrowser]

\# enable_extract_uploaded_archive=true

</code></pre>

&nbsp;

As always, feel free to suggest new improvements or comments on the [hue-user][6] list or [@gethue][7]!

 [1]: https://issues.cloudera.org/browse/HUE-5202
 [2]: https://gethue.com/category/file-browser/
 [3]: https://cdn.gethue.com/uploads/2016/12/fb-upload1.png
 [4]: https://cdn.gethue.com/uploads/2016/12/extract-button.png
 [5]: https://cdn.gethue.com/uploads/2016/12/oozie-job2.png
 [6]: http://groups.google.com/a/cloudera.org/group/hue-user
 [7]: https://twitter.com/gethue
