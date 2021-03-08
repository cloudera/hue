---
title: How to use HCatalog with Pig in a secured cluster
author: admin
type: post
date: 2014-12-09T20:43:46+00:00
url: /how-to-use-hcatalog-with-pig-in-a-secured-cluster/
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
In Hue 3.0 we made transparent the use of [HCatalog in the Pig][1] scripts. Today, we are going to detail how to run Pig script with HCatalog in some secured cluster.

The process is somehow still complicated, we will try to make it transparent to the user in <a href="https://issues.cloudera.org/browse/HUE-2480" target="_blank" rel="noopener noreferrer">HUE-2480</a>.

As usual, if you have questions or feedback, feel free to contact the Hue community on [hue-user][2] or [@gethue.com][3]!

&nbsp;

## Pig script to execute

We are going to use this simple script that display the first records of one of the sample Hive tables:

<pre><code class="bash">- Load table 'sample_07'

sample_07 = LOAD 'sample_07' USING org.apache.hcatalog.pig.HCatLoader();

out = LIMIT sample_07 15;

DUMP out;

</code></pre>

&nbsp;

## Make sure that the Oozie Share Lib is installed

As usual, if it is [missing][4], some jars won't be found and you will get:

<pre><code class="bash">

ERROR 1070: Could not resolve org.apache.hcatalog.pig.HCatLoader using imports: [, java.lang., org.apache.pig.builtin., org.apache.pig.impl.builtin.]

org.apache.pig.impl.logicalLayer.FrontendException: ERROR 1000: Error during parsing. Could not resolve org.apache.hcatalog.pig.HCatLoader using imports: [, java.lang., org.apache.pig.builtin., org.apache.pig.impl.builtin.]

</code></pre>

&nbsp;

## Oozie Editor

[Oozie][5] let's you chain and schedule jobs together. This is a bit tricky. In the Pig action, make sure that you click on the 'Advanced' link and check the HCat Credential. Upload the 'hive-site.xml' used by Hue and fill the 'Job XML' field.

[<img src="https://cdn.gethue.com/uploads/2014/12/oozie-pig-hact-cred-1024x777.png" />][6]

In the workflow properties, make sure that these Oozie properties are set:

<pre><code class="bash">

oozie.use.system.libpath true

oozie.action.sharelib.for.pig pig,hcatalog

</code></pre>

[<img src="https://cdn.gethue.com/uploads/2014/12/pig-hcat-cred-1024x402.png" />][7]

That's it!

&nbsp;

## Pig Editor

To make it work in the [Pig Editor][8] in secure mode, you will need [HUE-2152][9] or Hue 3.8 / CDH5.4 (but not needed if not using Kerberos).

Then just upload the hive-site.xml used by Hue and add it as a 'File' resource in the properties of the script. Contrary to the Hive action, the name must be 'hive-site.xml'.

[<img src="https://cdn.gethue.com/uploads/2014/12/pig-hive-site-1024x366.png" />][10]

And that's it!

[<img src="https://cdn.gethue.com/uploads/2014/12/pig-hcat-1024x568.png" />][11]

## Appendix

Examples of XML workflow

<pre><code class="xml"><workflow-app name="pig-app-hue-script" xmlns="uri:oozie:workflow:0.4">

<credentials>

<credential name="hcat" type="hcat">

<property>

<name>hcat.metastore.uri</name>

<value>thrift://hue-c5-sentry.ent.cloudera.com:9083</value>

</property>

<property>

<name>hcat.metastore.principal</name>

<value>hive/hue-c5-sentry.ent.cloudera.com@ENT.CLOUDERA.COM</value>

</property>

</credential>

</credentials>

<start to="pig"/>

<action name="pig" cred="hcat">

<pig>

<job-tracker>${jobTracker}</job-tracker>

<name-node>${nameNode}</name-node>

<script>/user/hue/oozie/workspaces/_hive_-oozie-253-1418153366.31/script.pig</script>

<file>/user/hue/oozie/workspaces/_hive_-oozie-242-1418149386.4/hive-site.xml#hive-site.xml</file>

</pig>

<ok to="end"/>

<error to="kill"/>

</action>

<kill name="kill">

<message>Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]</message>

</kill>

<end name="end"/>

</workflow-app>

</code></pre>

Properties

<pre><code class="bash">

Name Value

credentials {u'hcat': {'xml_name': u'hcat', 'properties': [('hcat.metastore.uri', u'thrift://hue-c5-sentry.ent.cloudera.com:9083'), ('hcat.metastore.principal', u'hive/hue-c5-sentry.ent.cloudera.com@ENT.CLOUDERA.COM')]}, u'hive2': {'xml_name': u'hive2', 'properties': [('hive2.jdbc.url', 'jdbc:hive2://hue-c5-sentry.ent.cloudera.com:10000/default'), ('hive2.server.principal', u'hive/hue-c5-sentry.ent.cloudera.com@ENT.CLOUDERA.COM')]}, u'hbase': {'xml_name': u'hbase', 'properties': []}}

hue-id-w 253

jobTracker hue-c5-sentry.ent.cloudera.com:8032

mapreduce.job.user.name hive

nameNode hdfs://hue-c5-sentry.ent.cloudera.com:8020

oozie.action.sharelib.for.pig pig,hcatalog

oozie.use.system.libpath true

oozie.wf.application.path hdfs://hue-c5-sentry.ent.cloudera.com:8020/user/hue/oozie/workspaces/_hive_-oozie-253-1418153366.31

user.name hive

</code></pre>

If you get the dreaded 'ERROR 2245: Cannot get schema from loadFunc org.apache.hcatalog.pig.HCatLoader' error this could be that the hive-site.xml is not added or that you need[HUE-2152][9] that injects the HCat credential in the script.

<pre><code class="bash">ERROR 2245: Cannot get schema from loadFunc org.apache.hcatalog.pig.HCatLoader

org.apache.pig.impl.logicalLayer.FrontendException: ERROR 1000: Error during parsing. Cannot get schema from loadFunc org.apache.hcatalog.pig.HCatLoader

at org.apache.pig.PigServer$Graph.parseQuery(PigServer.java:1689)

at org.apache.pig.PigServer$Graph.access$000(PigServer.java:1409)

at org.apache.pig.PigServer.parseAndBuild(PigServer.java:342)

at org.apache.pig.PigServer.executeBatch(PigServer.java:367)

at org.apache.pig.PigServer.executeBatch(PigServer.java:353)

at org.apache.pig.tools.grunt.GruntParser.executeBatch(GruntParser.java:140)

at org.apache.pig.tools.grunt.GruntParser.processDump(GruntParser.java:769)

at org.apache.pig.tools.pigscript.parser.PigScriptParser.parse(PigScriptParser.java:372)

at org.apache.pig.tools.grunt.GruntParser.parseStopOnError(GruntParser.java:198)

at org.apache.pig.tools.grunt.GruntParser.parseStopOnError(GruntParser.java:173)

at org.apache.pig.tools.grunt.Grunt.exec(Grunt.java:84)

at org.apache.pig.Main.run(Main.java:478)

at org.apache.pig.PigRunner.run(PigRunner.java:49)

at org.apache.oozie.action.hadoop.PigMain.runPigJob(PigMain.java:286)

at org.apache.oozie.action.hadoop.PigMain.run(PigMain.java:226)

at org.apache.oozie.action.hadoop.LauncherMain.run(LauncherMain.java:39)

at org.apache.oozie.action.hadoop.PigMain.main(PigMain.java:74)

at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)

at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:57)

at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)

at java.lang.reflect.Method.invoke(Method.java:606)

at org.apache.oozie.action.hadoop.LauncherMapper.map(LauncherMapper.java:227)

at org.apache.hadoop.mapred.MapRunner.run(MapRunner.java:54)

at org.apache.hadoop.mapred.MapTask.runOldMapper(MapTask.java:450)

at org.apache.hadoop.mapred.MapTask.run(MapTask.java:343)

at org.apache.hadoop.mapred.LocalContainerLauncher$EventHandler.runSubtask(LocalContainerLauncher.java:370)

at org.apache.hadoop.mapred.LocalContainerLauncher$EventHandler.runTask(LocalContainerLauncher.java:295)

at org.apache.hadoop.mapred.LocalContainerLauncher$EventHandler.access$200(LocalContainerLauncher.java:181)

at org.apache.hadoop.mapred.LocalContainerLauncher$EventHandler$1.run(LocalContainerLauncher.java:224)

at java.util.concurrent.Executors$RunnableAdapter.call(Executors.java:471)

at java.util.concurrent.FutureTask.run(FutureTask.java:262)

at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1145)

at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:615)

at java.lang.Thread.run(Thread.java:745)

Caused by: Failed to parse: Can not retrieve schema from loader org.apache.hcatalog.pig.HCatLoader@5e2e886d

at org.apache.pig.parser.QueryParserDriver.parse(QueryParserDriver.java:198)

at org.apache.pig.PigServer$Graph.parseQuery(PigServer.java:1676)

... 33 more

Caused by: java.lang.RuntimeException: Can not retrieve schema from loader org.apache.hcatalog.pig.HCatLoader@5e2e886d

at org.apache.pig.newplan.logical.relational.LOLoad.<init>(LOLoad.java:91)

at org.apache.pig.parser.LogicalPlanBuilder.buildLoadOp(LogicalPlanBuilder.java:853)

at org.apache.pig.parser.LogicalPlanGenerator.load_clause(LogicalPlanGenerator.java:3568)

at org.apache.pig.parser.LogicalPlanGenerator.op_clause(LogicalPlanGenerator.java:1625)

at org.apache.pig.parser.LogicalPlanGenerator.general_statement(LogicalPlanGenerator.java:1102)

at org.apache.pig.parser.LogicalPlanGenerator.statement(LogicalPlanGenerator.java:560)

at org.apache.pig.parser.LogicalPlanGenerator.query(LogicalPlanGenerator.java:421)

at org.apache.pig.parser.QueryParserDriver.parse(QueryParserDriver.java:188)

... 34 more

Caused by: org.apache.pig.impl.logicalLayer.FrontendException: ERROR 2245: Cannot get schema from loadFunc org.apache.hcatalog.pig.HCatLoader

at org.apache.pig.newplan.logical.relational.LOLoad.getSchemaFromMetaData(LOLoad.java:179)

at org.apache.pig.newplan.logical.relational.LOLoad.<init>(LOLoad.java:89)

... 41 more

Caused by: java.io.IOException: java.lang.Exception: Could not instantiate a HiveMetaStoreClient connecting to server uri:[null]

at org.apache.hcatalog.pig.PigHCatUtil.getTable(PigHCatUtil.java:205)

at org.apache.hcatalog.pig.HCatLoader.getSchema(HCatLoader.java:195)

at org.apache.pig.newplan.logical.relational.LOLoad.getSchemaFromMetaData(LOLoad.java:175)

... 42 more

Caused by: java.lang.Exception: Could not instantiate a HiveMetaStoreClient connecting to server uri:[null]

at org.apache.hcatalog.pig.PigHCatUtil.getHiveMetaClient(PigHCatUtil.java:160)

at org.apache.hcatalog.pig.PigHCatUtil.getTable(PigHCatUtil.java:200)

... 44 more

Caused by: com.google.common.util.concurrent.UncheckedExecutionException: javax.jdo.JDOFatalInternalException: Error creating transactional connection factory

NestedThrowables:

java.lang.reflect.InvocationTargetException

at com.google.common.cache.LocalCache$Segment.get(LocalCache.java:2234)

at com.google.common.cache.LocalCache.get(LocalCache.java:3965)

at com.google.common.cache.LocalCache$LocalManualCache.get(LocalCache.java:4764)

at org.apache.hcatalog.common.HiveClientCache.getOrCreate(HiveClientCache.java:167)

at org.apache.hcatalog.common.HiveClientCache.get(HiveClientCache.java:143)

at org.apache.hcatalog.common.HCatUtil.getHiveClient(HCatUtil.java:548)

at org.apache.hcatalog.pig.PigHCatUtil.getHiveMetaClient(PigHCatUtil.java:158)

... 45 more

Caused by: javax.jdo.JDOFatalInternalException: Error creating transactional connection factory

NestedThrowables:

java.lang.reflect.InvocationTargetException

at org.datanucleus.api.jdo.NucleusJDOHelper.getJDOExceptionForNucleusException(NucleusJDOHelper.java:587)

at org.datanucleus.api.jdo.JDOPersistenceManagerFactory.freezeConfiguration(JDOPersistenceManagerFactory.java:781)

at org.datanucleus.api.jdo.JDOPersistenceManagerFactory.createPersistenceManagerFactory(JDOPersistenceManagerFactory.java:326)

at org.datanucleus.api.jdo.JDOPersistenceManagerFactory.getPersistenceManagerFactory(JDOPersistenceManagerFactory.java:195)

at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)

at sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:57)

at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)

at java.lang.reflect.Method.invoke(Method.java:606)

at javax.jdo.JDOHelper$16.run(JDOHelper.java:1965)

at java.security.AccessController.doPrivileged(Native Method)

at javax.jdo.JDOHelper.invoke(JDOHelper.java:1960)

at javax.jdo.JDOHelper.invokeGetPersistenceManagerFactoryOnImplementation(JDOHelper.java:1166)

at javax.jdo.JDOHelper.getPersistenceManagerFactory(JDOHelper.java:808)

at javax.jdo.JDOHelper.getPersistenceManagerFactory(JDOHelper.java:701)

at org.apache.hadoop.hive.metastore.ObjectStore.getPMF(ObjectStore.java:313)

at org.apache.hadoop.hive.metastore.ObjectStore.getPersistenceManager(ObjectStore.java:342)

at org.apache.hadoop.hive.metastore.ObjectStore.initialize(ObjectStore.java:249)

at org.apache.hadoop.hive.metastore.ObjectStore.setConf(ObjectStore.java:224)

at org.apache.hadoop.util.ReflectionUtils.setConf(ReflectionUtils.java:73)

at org.apache.hadoop.util.ReflectionUtils.newInstance(ReflectionUtils.java:133)

at org.apache.hadoop.hive.metastore.RawStoreProxy.<init>(RawStoreProxy.java:58)

at org.apache.hadoop.hive.metastore.RawStoreProxy.getProxy(RawStoreProxy.java:67)

at org.apache.hadoop.hive.metastore.HiveMetaStore$HMSHandler.newRawStore(HiveMetaStore.java:506)

at org.apache.hadoop.hive.metastore.HiveMetaStore$HMSHandler.getMS(HiveMetaStore.java:484)

at org.apache.hadoop.hive.metastore.HiveMetaStore$HMSHandler.createDefaultDB(HiveMetaStore.java:532)

at org.apache.hadoop.hive.metastore.HiveMetaStore$HMSHandler.init(HiveMetaStore.java:406)

at org.apache.hadoop.hive.metastore.HiveMetaStore$HMSHandler.<init>(HiveMetaStore.java:365)

at org.apache.hadoop.hive.metastore.RetryingHMSHandler.<init>(RetryingHMSHandler.java:55)

at org.apache.hadoop.hive.metastore.RetryingHMSHandler.getProxy(RetryingHMSHandler.java:60)

at org.apache.hadoop.hive.metastore.HiveMetaStore.newHMSHandler(HiveMetaStore.java:4953)

at org.apache.hadoop.hive.metastore.HiveMetaStoreClient.<init>(HiveMetaStoreClient.java:172)

at org.apache.hadoop.hive.metastore.HiveMetaStoreClient.<init>(HiveMetaStoreClient.java:155)

at org.apache.hcatalog.common.HiveClientCache$CacheableHiveMetaStoreClient.<init>(HiveClientCache.java:246)

at org.apache.hcatalog.common.HiveClientCache$4.call(HiveClientCache.java:170)

at org.apache.hcatalog.common.HiveClientCache$4.call(HiveClientCache.java:167)

at com.google.common.cache.LocalCache$LocalManualCache$1.load(LocalCache.java:4767)

at com.google.common.cache.LocalCache$LoadingValueReference.loadFuture(LocalCache.java:3568)

at com.google.common.cache.LocalCache$Segment.loadSync(LocalCache.java:2350)

at com.google.common.cache.LocalCache$Segment.lockedGetOrLoad(LocalCache.java:2313)

at com.google.common.cache.LocalCache$Segment.get(LocalCache.java:2228)

... 51 more

Caused by: java.lang.reflect.InvocationTargetException

at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)

at sun.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:57)

at sun.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)

at java.lang.reflect.Constructor.newInstance(Constructor.java:526)

at org.datanucleus.plugin.NonManagedPluginRegistry.createExecutableExtension(NonManagedPluginRegistry.java:631)

at org.datanucleus.plugin.PluginManager.createExecutableExtension(PluginManager.java:325)

at org.datanucleus.store.AbstractStoreManager.registerConnectionFactory(AbstractStoreManager.java:281)

at org.datanucleus.store.AbstractStoreManager.<init>(AbstractStoreManager.java:239)

at org.datanucleus.store.rdbms.RDBMSStoreManager.<init>(RDBMSStoreManager.java:292)

at sun.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)

at sun.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:57)

at sun.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)

at java.lang.reflect.Constructor.newInstance(Constructor.java:526)

at org.datanucleus.plugin.NonManagedPluginRegistry.createExecutableExtension(NonManagedPluginRegistry.java:631)

at org.datanucleus.plugin.PluginManager.createExecutableExtension(PluginManager.java:301)

at org.datanucleus.NucleusContext.createStoreManagerForProperties(NucleusContext.java:1069)

at org.datanucleus.NucleusContext.initialise(NucleusContext.java:359)

at org.datanucleus.api.jdo.JDOPersistenceManagerFactory.freezeConfiguration(JDOPersistenceManagerFactory.java:768)

... 89 more

Caused by: org.datanucleus.exceptions.NucleusException: Attempt to invoke the "BONECP" plugin to create a ConnectionPool gave an error : The specified datastore driver ("org.apache.derby.jdbc.EmbeddedDriver") was not found in the CLASSPATH. Please check your CLASSPATH specification, and the name of the driver.

at org.datanucleus.store.rdbms.ConnectionFactoryImpl.generateDataSources(ConnectionFactoryImpl.java:237)

at org.datanucleus.store.rdbms.ConnectionFactoryImpl.initialiseDataSources(ConnectionFactoryImpl.java:110)

at org.datanucleus.store.rdbms.ConnectionFactoryImpl.<init>(ConnectionFactoryImpl.java:82)

... 107 more

Caused by: org.datanucleus.store.rdbms.datasource.DatastoreDriverNotFoundException: The specified datastore driver ("org.apache.derby.jdbc.EmbeddedDriver") was not found in the CLASSPATH. Please check your CLASSPATH specification, and the name of the driver.

at org.datanucleus.store.rdbms.datasource.AbstractDataSourceFactory.loadDriver(AbstractDataSourceFactory.java:58)

at org.datanucleus.store.rdbms.datasource.BoneCPDataSourceFactory.makePooledDataSource(BoneCPDataSourceFactory.java:61)

at org.datanucleus.store.rdbms.ConnectionFactoryImpl.generateDataSources(ConnectionFactoryImpl.java:217)

... 109 more

</code></pre>

 [1]: https://gethue.com/hadoop-tutorial-how-to-access-hive-in-pig-with/
 [2]: http://groups.google.com/a/cloudera.org/group/hue-user
 [3]: http://twitter.com/gethue
 [4]: http://blog.cloudera.com/blog/2014/05/how-to-use-the-sharelib-in-apache-oozie-cdh-5/
 [5]: https://gethue.com/category/oozie/
 [6]: https://cdn.gethue.com/uploads/2014/12/oozie-pig-hact-cred.png
 [7]: https://cdn.gethue.com/uploads/2014/12/pig-hcat-cred.png
 [8]: https://gethue.com/category/pig/
 [9]: https://issues.cloudera.org/browse/HUE-2152
 [10]: https://cdn.gethue.com/uploads/2014/12/pig-hive-site.png
 [11]: https://cdn.gethue.com/uploads/2014/12/pig-hcat.png
