---
title: Hive UDF in 1 minute!
author: admin
type: post
date: 2013-08-19T17:57:00+00:00
url: /hadoop-tutorial-hive-udf-in-1-minute/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/58711590309/hadoop-tutorial-hive-udf-in-1-minute
tumblr_gethue_id:
  - 58711590309
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
slide_template:
  - default
categories:
---

<p id="docs-internal-guid-7f706b2a-97b5-9a0c-5dff-ae0ff0c1eaad">
  Apache Hive comes with a lot of <a href="https://cwiki.apache.org/confluence/display/Hive/LanguageManual+UDF#">built-in</a> UDFs, but what happens when you need a “special one”? This post is about how to get started with a custom Hive UDF from compilation to execution in no time.
</p>

&nbsp;

{{< youtube Zz60VoMJSAc >}}

&nbsp;

# Let’s go!

Our goal is to create a UDF that transforms its input to upper case. All the code is available in our public repository of [Hadoop examples and tutorials][1].

If you want to go even faster, the UDF is already precompiled [here][2].

If not, checkout the [code][3]:

<pre class="code">git clone <a href="https://github.com/romainr/hadoop-tutorials-examples.git">https://github.com/romainr/hadoop-tutorials-examples.git</a>
cd hive-udf</pre>

And compile the UDF (Java and Hive need to be installed):

<pre class="code">javac -cp $(ls /usr/lib/hive/lib/hive-exec*.jar):/usr/lib/hadoop/hadoop-common.jar org/hue/udf/MyUpper.java

jar -cf myudfs.jar  -C . .</pre>

&nbsp;

Or use Maven with our [pom.xml][4] that will automatically pull the dependent jars

<pre class="code">mvn install</pre>

&nbsp;

# Register the UDF in the Hive Editor

Then open up Beeswax in the [Hadoop UI Hue][5], click on the 'Settings' tab.

In File Resources, upload _<span class="code">myudfs.jar</span>_, pick the jar file and point to it, e.g.:

<pre><code class="bash">/user/hue/myudf.jar</code></pre>

Make the UDF available by registering a UDF (User Defined Function ):

Name

<pre><code class="bash">myUpper</code></pre>

Class

<pre><code class="bash">org.hue.udf.MyUpper</code></pre>

&nbsp;

**That’s it**! Just test it on one of the Hue example tables:

<pre><code class="sql">select myUpper(description) FROM sample_07 limit 10</code></pre>

# Summary

We are using the most common type of UDF. If you want to learn more in depth about the other ones, some great resources like the [Hadoop Definitive][6] guide are available. Notice that adding a jar loads it for the entirety of the session so you don’t need to load it again. Next time we will demo how to create a Python UDF for Hive!

&nbsp;

Have any questions? Feel free to contact us on [hue-user][7] or [@gethue][8]!

&nbsp;

**Note**:

If you did not register the UDF as explained above, you will get this error:

<pre><code class="bash">error while compiling statement: failed: parseexception line 1:0 cannot recognize input near 'myupper' " "</code></pre>

[1]: https://github.com/romainr/hadoop-tutorials-examples
[2]: https://github.com/romainr/hadoop-tutorials-examples/raw/master/hive-udf/myudfs.jar
[3]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hive-udf/org/hue/udf/MyUpper.java
[4]: https://github.com/romainr/hadoop-tutorials-examples/blob/master/hive-udf/pom.xml
[5]: http://gethue.com
[6]: https://www.inkling.com/read/hadoop-definitive-guide-tom-white-3rd/chapter-12/ch12-section-08
[7]: http://groups.google.com/a/cloudera.org/group/hue-user
[8]: https://twitter.com/gethue
