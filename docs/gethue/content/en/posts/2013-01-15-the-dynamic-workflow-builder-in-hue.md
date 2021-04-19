---
title: The Dynamic Workflow Builder in Hue
author: admin
type: post
date: 2013-01-15T05:00:00+00:00
url: /the-dynamic-workflow-builder-in-hue/
tumblr_gethue_permalink:
  - http://gethue.tumblr.com/post/48706105303/the-dynamic-workflow-builder-in-hue
tumblr_gethue_id:
  - 48706105303
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
[Hue][1] is a web interface for [Apache Hadoop][2] that makes common Hadoop tasks such as running [MapReduce][3] jobs, browsing [HDFS][3], and creating [Apache Oozie][4] workflows, easier. In this post, we’re going to focus on the dynamic workflow builder that Hue provides for Oozie that will be released in Hue 2.2.0 (For a high-level description of Oozie integration in Hue, see this [blog post][5]).

The dynamic workflow editor is feature packed and emphasizes usability. The heavy lifting is delegated to the client via Javascript to provide a more “dynamic” experience for the user. This is achieved by using the [MVVM][6] (Model View View-Model) design pattern with [KnockoutJS][7] and event handling with [JQuery][8]. In effect, moving, creating, modifying, and deleting actions will be much easier. Also, the workflow editor will support Oozie’s Decision node.

## Basic Operations on Actions

The experience of performing basic operations on actions has been simplified (IE: Creating, updating, and deleting a node).

Nodes can be added seamlessly by clicking on the desired node type and filling out a few parameters. The parameters shown will vary depending on the type of node being added.

<img class="aligncenter" alt="" src="https://lh4.googleusercontent.com/OOyYGn9Wn-rtwqL6mWFbtpbWfkzc-xXEYBSOtmv8WUjIipPriV9swfBPa5WcsZ3I-beGHF9u5qAyAHha0h7CUW_WOXl_9mxWyosHIBl4fXoES9HRpCY" width="574px;" height="305px;" />

The node’s attributes can be modified in the future by clicking on the name of the node. Whenever a node is added or updated, the node will be validated before the popup will be closed. Also, a node can be removed by clicking on the “x” symbol within the node:

## Drag and Drop Actions in the Workflow

The dynamic workflow editor has three main movement functions: action placement, forking, and splitting by decision.

Here’s a quick demo of each of the main movement functions in the new workflow editor:

{{< vimeo 56045585 >}}

### Basic Node Placement

Actions can be placed almost anywhere in the workflow by simply dragging the action to the desired location. This can be in between two other actions, at the top of the workflow, or at the very bottom of the workflow.

### Forking

Fork nodes split the path of execution into multiple paths of execution. These paths of execution run concurrently. Fork nodes can be created by dragging an action onto another action. More paths of execution can be added by dropping an action to the fork node itself. Fork nodes are immobile, but can be removed by moving all actions out of the split paths of execution.

### Decision Node Support

Decision nodes choose a path of execution based on conditions specified in the node itself. To create a decision node, users will need to convert existing Fork nodes by clicking on a Fork node’s name.

The conditions can be added, or modified, by editing the node itself and providing expressions in the form ${ } as shown below.

<img class="aligncenter" alt="" src="https://lh5.googleusercontent.com/NtJwHpR8zeXMAiDNIBoKPpTps9JSp52ZuAbuupYL2MwkvaS7800akIfKO4QPONPklNxDls1zJ7PKyqKjwBDvXNMhZN5d5aHNOSTO9x-BX9-TPulgeYA" width="607px;" height="249px;" />

## Summary

The soon to be released workflow editor is much more usable and flexible. It allows users to drag actions to any location in the workflow, trivially create forks, and perform basic operations on actions. It also introduces the decision node, which can be used to conditionally split the paths of execution.

Hue will be seeing a slew of updates in the near future. The workflow editor itself will support more actions and provide a better experience when managing coordinators.

Have any suggestions? Feel free to tell us what you think through [hue-user][9].

 [1]: https://gethue.com
 [2]: http://hadoop.apache.com/
 [3]: http://hadoop.apache.org/
 [4]: http://oozie.apache.org/
 [5]: http://blog.cloudera.com/blog/2012/10/whats-new-in-cdh4-1-hue/
 [6]: http://en.wikipedia.org/wiki/MVVM
 [7]: http://knockoutjs.com/
 [8]: http://jquery.com/
 [9]: https://groups.google.com/a/cloudera.org/forum/?fromgroups#!forum/hue-user
