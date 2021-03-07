---
title: 'Quick Task: Fixing “ImportError: No module named google_compute_engine” when building Hue'
author: admin
type: post
date: 2019-03-26T21:42:18+00:00
url: /quick-task-fixing-importerror-no-module-named-google_compute_engine-when-building-hue/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
  # - Version 4.4

---
When [building Hue][1] on a Google Compute Engine machine, you might it this issue:

<pre><code class="bash"> ImportError: No module named google_compute_engine</code></pre>

with this full trace:

<pre><code class="bash"> 

creating 'dist/kombu-4.3.0-py2.7.egg' and adding 'build/bdist.linux-x86_64/egg' to it

removing 'build/bdist.linux-x86_64/egg' (and everything under it)

- Building egg for boto-2.46.1

Traceback (most recent call last):

File "<string>", line 1, in <module>

File "/home/romain/hue/build/env/local/lib/python2.7/site-packages/setuptools/sandbox.py", line 253, in run_setup

raise

File "/usr/lib/python2.7/contextlib.py", line 35, in __exit__

self.gen.throw(type, value, traceback)

File "/home/romain/hue/build/env/local/lib/python2.7/site-packages/setuptools/sandbox.py", line 195, in setup_context

yield

File "/usr/lib/python2.7/contextlib.py", line 35, in __exit__

self.gen.throw(type, value, traceback)

File "/home/romain/hue/build/env/local/lib/python2.7/site-packages/setuptools/sandbox.py", line 166, in save_modules

saved_exc.resume()

File "/home/romain/hue/build/env/local/lib/python2.7/site-packages/setuptools/sandbox.py", line 141, in resume

six.reraise(type, exc, self._tb)

File "/home/romain/hue/build/env/local/lib/python2.7/site-packages/setuptools/sandbox.py", line 154, in save_modules

yield saved

File "/home/romain/hue/build/env/local/lib/python2.7/site-packages/setuptools/sandbox.py", line 195, in setup_context

yield

File "/home/romain/hue/build/env/local/lib/python2.7/site-packages/setuptools/sandbox.py", line 250, in run_setup

_execfile(setup_script, ns)

File "/home/romain/hue/build/env/local/lib/python2.7/site-packages/setuptools/sandbox.py", line 45, in _execfile

exec(code, globals, locals)

File "setup.py", line 37, in <module>

from boto import __version__

File "/home/romain/hue/desktop/core/ext-py/boto-2.46.1/boto/__init__.py", line 1216, in <module>

boto.plugin.load_plugins(config)

File "/home/romain/hue/desktop/core/ext-py/boto-2.46.1/boto/plugin.py", line 93, in load_plugins

_import_module(file)

File "/home/romain/hue/desktop/core/ext-py/boto-2.46.1/boto/plugin.py", line 75, in _import_module

return imp.load_module(name, file, filename, data)

File "/usr/lib/python3/dist-packages/google_compute_engine/boto/compute_auth.py", line 19, in <module>

from google_compute_engine import logger

ImportError: No module named google_compute_engine

/home/romain/hue/Makefile.sdk:120: recipe for target '/home/romain/hue/desktop/core/build/boto-2.46.1/egg.stamp' failed

make[2]: \*** [/home/romain/hue/desktop/core/build/boto-2.46.1/egg.stamp] Error 1

make[2]: Leaving directory '/home/romain/hue/desktop/core'

Makefile:106: recipe for target '.recursive-env-install/core' failed

make[1]: \*** [.recursive-env-install/core] Error 2

make[1]: Leaving directory '/home/romain/hue/desktop'

Makefile:148: recipe for target 'desktop' failed

make: \*** [desktop] Error 2

</code></pre>

<pre>On quick workaround if you do not use boto, it to no not configure it:</p>


<p>
  <pre><code class="bash">
  sudo mv /etc/boto.cfg /etc/boto.cfg.back<br />
  </code></pre>
</p>

 [1]: http://cloudera.github.io/hue/latest/administrator/installation/
