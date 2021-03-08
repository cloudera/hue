---
title: 'Fixing the YARN Invalid resource request, requested memory < 0, or requested memory > max configured'
author: admin
type: post
date: 2015-03-10T22:05:07+00:00
url: /fixing-the-yarn-invalid-resource-request-requested-memory-0-or-requested-memory-max-configured/
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
Are you seeing this error when submitting a job to YARN? Are you launching an Oozie workflow with a Spark action? You might be hitting this issue!

<pre><code class="bash">Error starting action [spark-e27e]. ErrorType [TRANSIENT], ErrorCode [JA009], Message [JA009: org.apache.hadoop.yarn.exceptions.InvalidResourceRequestException: Invalid resource request, requested memory < 0, or requested memory > max configured, requestedMemory=1536, maxMemory=1024

at org.apache.hadoop.yarn.server.resourcemanager.scheduler.SchedulerUtils.validateResourceRequest(SchedulerUtils.java:203)

at org.apache.hadoop.yarn.server.resourcemanager.RMAppManager.validateAndCreateResourceRequest(RMAppManager.java:377)

at org.apache.hadoop.yarn.server.resourcemanager.RMAppManager.createAndPopulateNewRMApp(RMAppManager.java:320)

at org.apache.hadoop.yarn.server.resourcemanager.RMAppManager.submitApplication(RMAppManager.java:273)

at org.apache.hadoop.yarn.server.resourcemanager.ClientRMService.submitApplication(ClientRMService.java:574)

at org.apache.hadoop.yarn.api.impl.pb.service.ApplicationClientProtocolPBServiceImpl.submitApplication(ApplicationClientProtocolPBServiceImpl.java:213)

at org.apache.hadoop.yarn.proto.ApplicationClientProtocol$ApplicationClientProtocolService$2.callBlockingMethod(ApplicationClientProtocol.java:403)

at org.apache.hadoop.ipc.ProtobufRpcEngine$Server$ProtoBufRpcInvoker.call(ProtobufRpcEngine.java:619)

at org.apache.hadoop.ipc.RPC$Server.call(RPC.java:1060)

at org.apache.hadoop.ipc.Server$Handler$1.run(Server.java:2039)

at org.apache.hadoop.ipc.Server$Handler$1.run(Server.java:2035)

at java.security.AccessController.doPrivileged(Native Method)

at javax.security.auth.Subject.doAs(Subject.java:415)

at org.apache.hadoop.security.UserGroupInformation.doAs(UserGroupInformation.java:1671)

at org.apache.hadoop.ipc.Server$Handler.run(Server.java:2033)

]</code></pre>

[

<img src="https://cdn.gethue.com/uploads/2015/03/oozie-yarn-mem-1024x558.png" />

][1]

Your job is asking for more memory than what YARN is authorizing him to do. One way to fix it is to up these parameters to more like 2000:

<pre><code class="bash">

yarn.scheduler.maximum-allocation-mb

</code></pre>

<pre><code class="bash">

yarn.nodemanager.resource.memory-mb

</code></pre>

Have any questions? Feel free to contact us on [hue-user][2] or [@gethue][3]!

 [1]: https://cdn.gethue.com/uploads/2015/03/oozie-yarn-mem.png
 [2]: http://groups.google.com/a/cloudera.org/group/hue-user
 [3]: https://twitter.com/gethue
