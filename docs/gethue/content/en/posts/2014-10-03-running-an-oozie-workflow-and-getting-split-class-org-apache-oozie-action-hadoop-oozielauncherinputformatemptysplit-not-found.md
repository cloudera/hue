---
title: Running an Oozie workflow without having installed the sharelib
author: admin
type: post
date: 2014-10-03T18:22:54+00:00
url: /running-an-oozie-workflow-and-getting-split-class-org-apache-oozie-action-hadoop-oozielauncherinputformatemptysplit-not-found/
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
If after installing your cluster and submitting some Oozie jobs you are seeing this type of error:

<pre><code class="bash">2015-03-11 09:11:19,821 WARN ActionStartXCommand:544 - SERVER[local] USER[hue] GROUP[-] TOKEN[] APP[pig-app-hue-script] JOB[0000000-150311091052117-oozie-hue-W] ACTION[0000000-150311091052117-oozie-hue-W@pig] Error starting action [pig]. ErrorType [FAILED], ErrorCode [It should never happen], Message [File /user/oozie/share/lib does not exist]

org.apache.oozie.action.ActionExecutorException: File /user/oozie/share/lib does not exist

at org.apache.oozie.action.hadoop.JavaActionExecutor.addShareLib(JavaActionExecutor.java:601)

at org.apache.oozie.action.hadoop.JavaActionExecutor.addActionShareLib(JavaActionExecutor.java:725)

at org.apache.oozie.action.hadoop.JavaActionExecutor.addAllShareLibs(JavaActionExecutor.java:707)

at org.apache.oozie.action.hadoop.JavaActionExecutor.setLibFilesArchives(JavaActionExecutor.java:700)

at org.apache.oozie.action.hadoop.JavaActionExecutor.submitLauncher(JavaActionExecutor.java:895)

at org.apache.oozie.action.hadoop.JavaActionExecutor.start(JavaActionExecutor.java:1145)

at org.apache.oozie.command.wf.ActionStartXCommand.execute(ActionStartXCommand.java:228)

at org.apache.oozie.command.wf.ActionStartXCommand.execute(ActionStartXCommand.java:63)

at org.apache.oozie.command.XCommand.call(XCommand.java:281)

at org.apache.oozie.service.CallableQueueService$CompositeCallable.call(CallableQueueService.java:323)

at org.apache.oozie.service.CallableQueueService$CompositeCallable.call(CallableQueueService.java:252)

at org.apache.oozie.service.CallableQueueService$CallableWrapper.run(CallableQueueService.java:174)

at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1145)

at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:615)

at java.lang.Thread.run(Thread.java:745)

</code></pre>

or

<pre><code class="bash"> Error: java.io.IOException: Split class org.apache.oozie.action.hadoop.OozieLauncherInputFormat$EmptySplit not found

at org.apache.hadoop.mapred.MapTask.getSplitDetails(MapTask.java:363)

at org.apache.hadoop.mapred.MapTask.runOldMapper(MapTask.java:423)

at org.apache.hadoop.mapred.MapTask.run(MapTask.java:343)

at org.apache.hadoop.mapred.YarnChild$2.run(YarnChild.java:168)

at java.security.AccessController.doPrivileged(Native Method)

at javax.security.auth.Subject.doAs(Subject.java:396)

at org.apache.hadoop.security.UserGroupInformation.doAs(UserGroupInformation.java:1614)

at org.apache.hadoop.mapred.YarnChild.main(YarnChild.java:163)

Caused by: java.lang.ClassNotFoundException: Class org.apache.oozie.action.hadoop.OozieLauncherInputFormat$EmptySplit not found

at org.apache.hadoop.conf.Configuration.getClassByName(Configuration.java:1953)

at org.apache.hadoop.mapred.MapTask.getSplitDetails(MapTask.java:361)

... 7 more

</code></pre>

This is because the [Oozie Share Lib][1] is not installed. Here is one command to install the YARN one:

<pre><code class="bash">sudo -u oozie /usr/lib/oozie/bin/oozie-setup.sh sharelib create -fs hdfs://localhost:8020 -locallib /usr/lib/oozie/oozie-sharelib-yarn.tar.gz

setting JAVA_LIBRARY_PATH="$JAVA_LIBRARY_PATH:/usr/lib/hadoop/lib/native"

setting OOZIE_DATA=/var/lib/oozie

setting OOZIE_CATALINA_HOME=/usr/lib/bigtop-tomcat

setting CATALINA_TMPDIR=/var/lib/oozie

setting CATALINA_PID=/var/run/oozie/oozie.pid

setting CATALINA_BASE=/var/lib/oozie/tomcat-deployment

setting OOZIE_HTTPS_PORT=11443

setting OOZIE_HTTPS_KEYSTORE_PASS=password

setting CATALINA_OPTS="$CATALINA_OPTS -Doozie.https.port=${OOZIE_HTTPS_PORT}"

setting CATALINA_OPTS="$CATALINA_OPTS -Doozie.https.keystore.pass=${OOZIE_HTTPS_KEYSTORE_PASS}"

setting CATALINA_OPTS="$CATALINA_OPTS -Xmx1024m"

setting OOZIE_CONFIG=/etc/oozie/conf

setting OOZIE_LOG=/var/log/oozie

setting JAVA_LIBRARY_PATH="$JAVA_LIBRARY_PATH:/usr/lib/hadoop/lib/native"

setting OOZIE_DATA=/var/lib/oozie

setting OOZIE_CATALINA_HOME=/usr/lib/bigtop-tomcat

setting CATALINA_TMPDIR=/var/lib/oozie

setting CATALINA_PID=/var/run/oozie/oozie.pid

setting CATALINA_BASE=/var/lib/oozie/tomcat-deployment

setting OOZIE_HTTPS_PORT=11443

setting OOZIE_HTTPS_KEYSTORE_PASS=password

setting CATALINA_OPTS="$CATALINA_OPTS -Doozie.https.port=${OOZIE_HTTPS_PORT}"

setting CATALINA_OPTS="$CATALINA_OPTS -Doozie.https.keystore.pass=${OOZIE_HTTPS_KEYSTORE_PASS}"

setting CATALINA_OPTS="$CATALINA_OPTS -Xmx1024m"

setting OOZIE_CONFIG=/etc/oozie/conf

setting OOZIE_LOG=/var/log/oozie

log4j:WARN No appenders could be found for logger (org.apache.hadoop.util.Shell).

log4j:WARN Please initialize the log4j system properly.

log4j:WARN See http://logging.apache.org/log4j/1.2/faq.html#noconfig for more info.

SLF4J: Class path contains multiple SLF4J bindings.

SLF4J: Found binding in [jar:file:/usr/lib/oozie/libserver/slf4j-log4j12-1.7.5.jar!/org/slf4j/impl/StaticLoggerBinder.class]

SLF4J: Found binding in [jar:file:/usr/lib/oozie/libserver/slf4j-simple-1.7.5.jar!/org/slf4j/impl/StaticLoggerBinder.class]

SLF4J: See http://www.slf4j.org/codes.html#multiple_bindings for an explanation.

SLF4J: Actual binding is of type [org.slf4j.impl.Log4jLoggerFactory]

the destination path for sharelib is: /user/oozie/share/lib/lib_20141003111250

</code></pre>

On latest version of Oozie, just point to a folder instead:

<pre><code class="bash">sudo -u oozie /usr/lib/oozie/bin/oozie-setup.sh sharelib create -fs hdfs://localhost:8020 -locallib /usr/lib/oozie/oozie-sharelib-yarn</code></pre>

And how to check it:

<pre><code class="bash">sudo -u oozie oozie admin -shareliblist -oozie http://localhost:11000/oozie

[Available ShareLib]

oozie

hive

distcp

hcatalog

sqoop

mapreduce-streaming

hive2

pig

</code></pre>

&nbsp;

**Note**

If you have upgraded your cluster, use 'upgrade' instead of 'create':

<pre><code class="bash">sudo -u oozie /usr/lib/oozie/bin/oozie-setup.sh sharelib upgrade -fs hdfs://localhost:8020 -locallib /usr/lib/oozie/oozie-sharelib-yarn.tar.gz</code></pre>

**Note**

If you are seeing:

<pre><code class="bash">sharelib.system.libpath (unavailable)</code></pre>

You need something like that in your oozie-site.xml

<pre><code class="xml"><property>

<name>oozie.service.HadoopAccessorService.hadoop.configurations</name>

<value>*=/etc/hadoop/conf</value>

</property></code></pre>

And now restart Oozie:

<pre><code class="bash">sudo service oozie restart</code></pre>

That's it, you are now ready to submit [workflows][2]!

&nbsp;

As usual feel free to comment and send feedback on the [hue-user][3] list or [@gethue][4]!

&nbsp;

 [1]: http://blog.cloudera.com/blog/2014/05/how-to-use-the-sharelib-in-apache-oozie-cdh-5/
 [2]: https://gethue.com/category/oozie/
 [3]: http://groups.google.com/a/cloudera.org/group/hue-user
 [4]: https://twitter.com/gethue
