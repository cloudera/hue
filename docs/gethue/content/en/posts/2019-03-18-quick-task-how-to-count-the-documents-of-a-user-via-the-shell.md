---
title: 'Quick Task: How to count the documents of a user via the Shell?'
author: admin
type: post
date: 2019-03-18T18:05:05+00:00
url: /quick-task-how-to-count-the-documents-of-a-user-via-the-shell/
sf_thumbnail_link_type:
  - link_to_post
sf_thumbnail_type:
  - none
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
ampforwp-amp-on-off:
  - default
categories:

---
### How to count the documents of a user? {#how-to-count-documents-of-a-user}

Sometimes, it is convenient to administrate Hue directly via the command line. While investigating while <http://demo.gethue.com> was slow, we discovered that the `demo` user had more than 85 000 documents! This was a quick way to validate this and delete the extra ones.

&nbsp;

On the command line:

<pre><code class="hljs dts">.&lt;span class="hljs-meta-keyword">/build/&lt;/span>env&lt;span class="hljs-meta-keyword">/bin/&lt;/span>hue shell
</code></pre>

If using Cloudera Manager, as a `root` user launch the shell.

Export the configuration directory:

<pre><code class="hljs bash">&lt;span class="hljs-built_in">export&lt;/span> HUE_CONF_DIR=&lt;span class="hljs-string">"/var/run/cloudera-scm-agent/process/`ls -alrt /var/run/cloudera-scm-agent/process | grep HUE_SERVER | tail -1 | awk '{print &lt;span class="hljs-variable">$9&lt;/span>}'`"&lt;/span>
&lt;span class="hljs-built_in">echo&lt;/span> &lt;span class="hljs-variable">$HUE_CONF_DIR&lt;/span>
&gt; /var/run/cloudera-scm-agent/process/2061-hue-HUE_SERVER
</code></pre>

Get the process id:

<pre><code class="hljs nginx">&lt;span class="hljs-attribute">lsof&lt;/span> -i :&lt;span class="hljs-number">8888&lt;/span>|grep -m1 hue|awk &lt;span class="hljs-string">'{ print &lt;span class="hljs-variable">$2&lt;/span> }'&lt;/span>
&gt; &lt;span class="hljs-number">14850&lt;/span>
</code></pre>

In order to export all Hue’s env variables:

<pre><code class="hljs bash">&lt;span class="hljs-keyword">for&lt;/span> line &lt;span class="hljs-keyword">in&lt;/span> `strings /proc/$(lsof -i :8888|grep -m1 hue|awk &lt;span class="hljs-string">'{ print $2 }'&lt;/span>)/environ|egrep -v &lt;span class="hljs-string">"^HOME=|^TERM=|^PWD="&lt;/span>`;&lt;span class="hljs-keyword">do&lt;/span> &lt;span class="hljs-built_in">export&lt;/span> &lt;span class="hljs-variable">$line&lt;/span>;&lt;span class="hljs-keyword">done&lt;/span>
</code></pre>

And finally launch the shell by:

<pre><code class="hljs groovy">HUE_IGNORE_PASSWORD_SCRIPT_ERRORS=&lt;span class="hljs-number">1&lt;/span> &lt;span class="hljs-regexp">/opt/&lt;/span>cloudera&lt;span class="hljs-regexp">/parcels/&lt;/span>CDH&lt;span class="hljs-regexp">/lib/&lt;/span>hue&lt;span class="hljs-regexp">/build/&lt;/span>env&lt;span class="hljs-regexp">/bin/&lt;/span>hue shell
&gt; &lt;span class="hljs-string">ALERT:&lt;/span> This appears to be a CM Managed environment
&gt; &lt;span class="hljs-string">ALERT:&lt;/span> HUE_CONF_DIR must be set when running hue commands &lt;span class="hljs-keyword">in&lt;/span> CM Managed environment
&gt; &lt;span class="hljs-string">ALERT:&lt;/span> Please run &lt;span class="hljs-string">'hue &lt;command&gt; --cm-managed'&lt;/span>
</code></pre>

Then use the Python code to access a certain user information:

<pre><code class="hljs powershell">Python &lt;span class="hljs-number">2.7&lt;/span>.&lt;span class="hljs-number">6&lt;/span> (default, Oct &lt;span class="hljs-number">26&lt;/span> &lt;span class="hljs-number">2016&lt;/span>, &lt;span class="hljs-number">20&lt;/span>:&lt;span class="hljs-number">30&lt;/span>:&lt;span class="hljs-number">19&lt;/span>)
Type &lt;span class="hljs-string">"copyright"&lt;/span>, &lt;span class="hljs-string">"credits"&lt;/span> or &lt;span class="hljs-string">"license"&lt;/span> &lt;span class="hljs-keyword">for&lt;/span> more information.

IPython &lt;span class="hljs-number">5.2&lt;/span>.&lt;span class="hljs-number">0&lt;/span> -- An enhanced Interactive Python.
?         -&gt; Introduction and overview of IPython&lt;span class="hljs-string">'s features.
%quickref -&gt; Quick reference.
help      -&gt; Python'&lt;/span>s own help system.
object?   -&gt; Details about &lt;span class="hljs-string">'object'&lt;/span>, use &lt;span class="hljs-string">'object??'&lt;/span> &lt;span class="hljs-keyword">for&lt;/span> extra details.

from django.contrib.auth.models import User
from desktop.models import Document2

user = User.objects.get(username=&lt;span class="hljs-string">'demo'&lt;/span>)
Document2.objects.documents(user=user).count()

&lt;span class="hljs-keyword">In&lt;/span> [&lt;span class="hljs-number">8&lt;/span>]: Document2.objects.documents(user=user).count()
Out[&lt;span class="hljs-number">8&lt;/span>]: &lt;span class="hljs-number">1167&lt;/span>

&lt;span class="hljs-keyword">In&lt;/span> [&lt;span class="hljs-number">10&lt;/span>]: Document2.objects.documents(user=user, perms=&lt;span class="hljs-string">'own'&lt;/span>).count()
Out[&lt;span class="hljs-number">10&lt;/span>]: &lt;span class="hljs-number">1166&lt;/span>

&lt;span class="hljs-keyword">In&lt;/span> [&lt;span class="hljs-number">11&lt;/span>]: Document2.objects.documents(user=user, perms=&lt;span class="hljs-string">'own'&lt;/span>, include_history=True).count()
Out[&lt;span class="hljs-number">11&lt;/span>]: &lt;span class="hljs-number">7125&lt;/span>

&lt;span class="hljs-keyword">In&lt;/span> [&lt;span class="hljs-number">12&lt;/span>]: Document2.objects.documents(user=user, perms=&lt;span class="hljs-string">'own'&lt;/span>, include_history=True, include_trashed=True).count()
Out[&lt;span class="hljs-number">12&lt;/span>]: &lt;span class="hljs-number">7638&lt;/span>

&lt;span class="hljs-keyword">In&lt;/span> [&lt;span class="hljs-number">13&lt;/span>]: Document2.objects.documents(user=user, perms=&lt;span class="hljs-string">'own'&lt;/span>, include_history=True, include_trashed=True, include_managed=True).count()
Out[&lt;span class="hljs-number">13&lt;/span>]: &lt;span class="hljs-number">31408&lt;/span>

Out[&lt;span class="hljs-number">14&lt;/span>]:
(&lt;span class="hljs-number">85667&lt;/span>L,
{u&lt;span class="hljs-string">'desktop.Document'&lt;/span>: &lt;span class="hljs-number">18524&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.Document2'&lt;/span>: &lt;span class="hljs-number">31409&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.Document2Permission'&lt;/span>: &lt;span class="hljs-number">556&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.Document2Permission_groups'&lt;/span>: &lt;span class="hljs-number">277&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.Document2Permission_users'&lt;/span>: &lt;span class="hljs-number">0&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.Document2_dependencies'&lt;/span>: &lt;span class="hljs-number">15087&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.DocumentPermission'&lt;/span>: &lt;span class="hljs-number">1290&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.DocumentPermission_groups'&lt;/span>: &lt;span class="hljs-number">0&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.DocumentPermission_users'&lt;/span>: &lt;span class="hljs-number">0&lt;/span>L,
  u&lt;span class="hljs-string">'desktop.Document_tags'&lt;/span>: &lt;span class="hljs-number">18524&lt;/span>L})
</code></pre>

Et voila, it is much cleaner now!

[<img src="https://cdn.gethue.com/uploads/2019/03/hue_documents_page.png"/>][1]

 [1]: https://cdn.gethue.com/uploads/2019/03/hue_documents_page.png
