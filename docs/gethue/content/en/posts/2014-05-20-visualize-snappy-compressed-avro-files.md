---
title: Visualize Snappy compressed Avro files
author: admin
type: post
date: 2014-05-20T16:05:49+00:00
url: /visualize-snappy-compressed-avro-files/
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
slide_template:
  - default
categories:
---

You can now view Snappy compressed <a href="http://avro.apache.org/" target="_blank" rel="noopener noreferrer">Avro</a> files in Hue through the [File Browser][1]! Here is a quick guide on how to get setup with Snappy and Avro.

#

# Tutorial

## Installation

1. Make sure Hue is stopped before installing.
2. Install the snappy system packages on your system. They can either be downloaded from <https://code.google.com/p/snappy/> or, preferably, installed via your package management system (e.g. `yum install snappy-devel`).
3. Install the python-snappy package via ‘pip’ from the Hue home (cd /usr/lib/hue or /opt/cloudera/parcels/CDH/lib/hue):
   <pre><code class="bash">yum install gcc gcc-c++ python-devel snappy-devel


    build/env/bin/pip install -U setuptools

    build/env/bin/pip install python-snappy</code></pre>

4. Start Hue!

## Demo

Once Snappy and python-snappy have been installed, the File Browser will automatically detect and view Snappy compressed Avro files. Here is a quick video demonstrating this!

{{< youtube jfoEvwwdZ_Y >}}

Note: In this demo, we are using Avro files found in this [github][2] (1).

&nbsp;

**Note**

It turns out that `python-snappy` is not compatible with the python library called `snappy`. If you see this error, uninstall `snappy`:

<pre><code class="bash">

[03/Sep/2015 06:56:34 -0700] views WARNING Could not read avro file at //user/cconner/test_snappy.avro

Traceback (most recent call last):

File "/usr/lib//lib/hue/apps/filebrowser/src/filebrowser/views.py", line 701, in _read_avro

data_file_reader = datafile.DataFileReader(fhandle, io.DatumReader())

File "/usr/lib//lib/hue/build/env/lib/python2.6/site-packages/avro-1.7.6-py2.6.egg/avro/datafile.py", line 240, in _init_

raise DataFileException('Unknown codec: %s.' % self.codec)

DataFileException: Unknown codec: snappy.

[03/Sep/2015 06:56:34 -0700] middleware INFO Processing exception: Failed to read Avro file.: Traceback (most recent call last):

File "/usr/lib//lib/hue/build/env/lib/python2.6/site-packages/Django-1.4.5-py2.6.egg/django/core/handlers/base.py", line 111, in get_response

response = callback(request, \*callback_args, \**callback_kwargs)

File "/usr/lib//lib/hue/apps/filebrowser/src/filebrowser/views.py", line 168, in view

return display(request, path)

File "/usr/lib//lib/hue/apps/filebrowser/src/filebrowser/views.py", line 573, in display

read_contents(compression, path, request.fs, offset, length)

File "/usr/lib//lib/hue/apps/filebrowser/src/filebrowser/views.py", line 663, in read_contents

contents = _read_avro(fhandle, path, offset, length, stats)

File "/usr/lib//lib/hue/apps/filebrowser/src/filebrowser/views.py", line 716, in _read_avro

raise PopupException(_("Failed to read Avro file."))

PopupException: Failed to read Avro file.

</code></pre>

#

# Conclusion

We hope this helps you look at the inputs and outputs of MapReduce jobs, Hive queries, and Pig scripts. Have any suggestions? Feel free to tell us what you think through [hue-user][3] or [@gethue][4]!

#

# References:

1. Reading and writing Avro files from the command line - <http://www.michael-noll.com/blog/2013/03/17/reading-and-writing-avro-files-from-the-command-line/>

[1]: https://gethue.com/category/file-browser/
[2]: https://github.com/miguno/avro-cli-examples
[3]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
[4]: https://twitter.com/gethue
