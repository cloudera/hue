---
title: 'How-to: Import a Pre-existing Oozie Workflow into Hue'
author: admin
type: post
date: 2013-01-20T05:00:00+00:00
url: /how-to-import-a-pre-existing-oozie-workflow-into-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/48706145575/how-to-import-a-pre-existing-oozie-workflow-into-hue
tumblr_gethue_id:
  - 48706145575
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
[Hue][1] is an open-source web interface for Apache Hadoop packaged with CDH that focuses on improving the overall experience for the average user. The [Apache Oozie][2] application in Hue provides an easy-to-use interface to build workflows and coordinators. Basic management of workflows and coordinators is available through the dashboards with operations such as killing, suspending, or resuming a job.

Prior to [Hue 2.2][3] (included in CDH 4.2), there was no way to manage workflows within Hue that were created outside of Hue. As of Hue 2.2, importing a pre-existing Oozie workflow by its XML definition is now possible.

## **How to import a workflow**

Importing a workflow is pretty straightforward. All it requires is the workflow definition file and access to the Oozie application in Hue. Follow these steps to import a workflow:

  1. Go to Oozie Editor/Dashboard > Workflows and click the “Import” button.[<img alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/oozie-workflow-editor-import.png" width="600" height="186" />][4]
  2. Provide at minimum a name and workflow definition file.&nbsp;
    [<img alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/oozie-import-workflow-upload-definition.png" width="600" height="411" />][5]

    &nbsp;</li>

      * Click “Save”. This will redirect you to the workflow builder with a message in blue near the top stating “Workflow imported”.[<img alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/builder.png" width="600" height="212" />][6]</ol>

    ## How It Works

    The definition file describes a workflow well enough for Hue to infer its structure. It also provides the majority of the attributes associated with a node, with the exception of some resource references. Resource reference handling is detailed in the following paragraphs.

    A workflow is imported into Hue by uploading the XML definition. Its nodes are transformed into Django serialized objects, and then grok’d by Hue:

    [<img alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/import-process.png" width="600" height="88" />][7]

    **Workflow transformation pipeline (Without hierarchy resolution)**

    **Workflow Definitions Transformation**

    Workflow definitions have a general form, which make them easy to transform. There are several kinds of nodes, all of which have a unique representation. There are patterns that simplify the task of transforming the definition XML:

    <pre class="code">&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;workflow-app xmlns="uri:oozie:workflow:0.4" name="fs-test"&gt;
  &lt;start to="Fs" /&gt;
  &lt;action name="Fs"&gt;
    &lt;fs&gt;
      &lt;delete path="${nameNode}${output}/testfs" /&gt;
      &lt;mkdir path="${nameNode}${output}/testfs" /&gt;
      &lt;mkdir path="${nameNode}${output}/testfs/source" /&gt;
      &lt;move source="${nameNode}${output}/testfs/source" target="${nameNode}${output}/testfs/renamed" /&gt;
      &lt;chmod path="${nameNode}${output}/testfs/renamed" permissions="700" dir-files="false" /&gt;
      &lt;touchz path="${nameNode}${output}/testfs/new_file" /&gt;
    &lt;/fs&gt;
    &lt;ok to="end" /&gt;
    &lt;error to="kill" /&gt;
  &lt;/action&gt;
  &lt;kill name="kill"&gt;
    &lt;message&gt;Action failed, error message[${wf:errorMessage(wf:lastErrorNode())}]&lt;/message&gt;
  &lt;/kill&gt;
  &lt;end name="end" /&gt;
&lt;/workflow-app&gt;</pre>

    Nodes are children of the root element `workflow-app`. Every node has a unique representation varying in at least their name. Every action is defined by the element `action` with a unique name. Its immediate children consist of the action type and links. The children of the node type tag are various properties associated with the action. The `start`,`end`, `fork`, `decision`, `join`, and `kill` nodes have their own transformation, where actions are transformed using a general Extensible Stylesheet Language Transformation, or [XSLT][8].

    The different attributes are generally not unique to an action. For instance, the Hive action and Sqoop action both have the `prepare` attribute. Hue provides an XSLT for every action type, but only to import non-unique attributes and to define transformations for unique attributes. In the XSLT below, the sqoop action is defined by importing all of the general fields and defining any Sqoop-specific fields:

    <pre class="code">&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:workflow="uri:oozie:workflow:0.1" xmlns:sqoop="uri:oozie:sqoop-action:0.2" version="1.0" exclude-result-prefixes="workflow sqoop"&gt;
  &lt;xsl:import href="../nodes/fields/archives.xslt" /&gt;
  &lt;xsl:import href="../nodes/fields/files.xslt" /&gt;
  &lt;xsl:import href="../nodes/fields/job_properties.xslt" /&gt;
  &lt;xsl:import href="../nodes/fields/job_xml.xslt" /&gt;
  &lt;xsl:import href="../nodes/fields/params.xslt" /&gt;
  &lt;xsl:import href="../nodes/fields/prepares.xslt" /&gt;
  &lt;xsl:template match="sqoop:sqoop"&gt;
    &lt;object model="oozie.sqoop" pk="0"&gt;
      &lt;xsl:call-template name="archives" /&gt;
      &lt;xsl:call-template name="files" /&gt;
      &lt;xsl:call-template name="job_properties" /&gt;
      &lt;xsl:call-template name="job_xml" /&gt;
      &lt;xsl:call-template name="params" /&gt;
      &lt;xsl:call-template name="prepares" /&gt;
      &lt;field name="script_path" type="CharField"&gt;
        &lt;xsl:value-of select="*[local-name()='command']" /&gt;
      &lt;/field&gt;
    &lt;/object&gt;
  &lt;/xsl:template&gt;
  &lt;xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" /&gt;
&lt;/xsl:stylesheet&gt;</pre>

    The above XSLT imports transformation definitions for the archives, files, job properties, job XML, params, and prepares attributes. If a Sqoop action XML definition were to be transformed by the above XSLT, the resulting XML would take on the following form:

    <pre class="code">&lt;object model="oozie.sqoop" pk="0"&gt;
  &lt;field name="archives" type="TextField"&gt;...&lt;/field&gt;
  &lt;field name="files" type="TextField"&gt;...&lt;/field&gt;
  &lt;field name="job_properties" type="TextField"&gt;...&lt;/field&gt;
  &lt;field name="job_xml" type="TextField"&gt;...&lt;/field&gt;
  &lt;field name="params" type="TextField"&gt;...&lt;/field&gt;
  &lt;field name="prepares" type="TextField"&gt;...&lt;/field&gt;
  &lt;field name="script_path" type="CharField"&gt;...&lt;/field&gt;
&lt;/object&gt;</pre>

    **Workflow Structure Resolution**

    The structure of the workflow is created after the nodes are imported. Internally, the workflow hierarchy is represented as a set of “links” between nodes. The workflow definition contains references to next nodes in the graph through the tags `ok`, `error`, and `start`. These references are used to create transitions. The following code snippet illustrates a transition that goes to a node called `end` and an error transition that goes to a node named `kill`:

    <pre class="code">&lt;ok to="end" /&gt;
&lt;error to="kill" /&gt;</pre>

    Workflow definitions do not have resources, such as a jar file used when running a MapReduce action. Hue intentionally leaves this information out when performing the transformation because it is not in the workflow definition. This forces users to update any resource-specific information within actions.

    [<img alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/missing-jar-path-highlighted.png" width="600" height="684" />][9]

    **An imported workflow. Note that its resource information is missing.**

    ## Summary and Next Steps

    Hue can manage workflows with its dynamic [workflow builder][10] and now, officially, can import predefined workflows into its system. Another benefit of parsing the XML definition is it enables all workflows to be displayed as a graph in the dashboard:

    [<img alt="" src="http://www.cloudera.com/wp-content/uploads/2013/03/dashboard-graph.png" width="600" height="307" />][11]

    **Dashboard graph of an imported workflow**

    The workflow import process is good, but not perfect yet. Ideally, as detailed above, resources will be found on the system and validated before being imported or resources should be optionally [provided][12].

    Have any suggestions? Feel free to tell us what you think via [hue-user][13].

 [1]: https://gethue.com
 [2]: http://oozie.apache.org/
 [3]: http://blog.cloudera.com/blog/2013/03/whats-new-in-hue-2-2/
 [4]: http://www.cloudera.com/wp-content/uploads/2013/03/oozie-workflow-editor-import.png
 [5]: http://www.cloudera.com/wp-content/uploads/2013/03/oozie-import-workflow-upload-definition.png
 [6]: http://www.cloudera.com/wp-content/uploads/2013/03/builder.png
 [7]: http://www.cloudera.com/wp-content/uploads/2013/03/import-process.png
 [8]: http://www.w3.org/TR/xslt
 [9]: http://www.cloudera.com/wp-content/uploads/2013/03/missing-jar-path-highlighted.png
 [10]: http://blog.cloudera.com/blog/2013/01/dynamic-workflow-builder-in-hue/
 [11]: http://www.cloudera.com/wp-content/uploads/2013/03/dashboard-graph.png
 [12]: https://issues.cloudera.org/browse/HUE-1001
 [13]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
