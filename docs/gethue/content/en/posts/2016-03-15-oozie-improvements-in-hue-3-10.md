---
title: Oozie performance and usability improvements in Hue 3.10
author: admin
type: post
date: 2016-03-15T00:08:18+00:00
url: /oozie-improvements-in-hue-3-10/
sf_left_sidebar:
  - Sidebar-2
sf_sidebar_config:
  - left-sidebar
sf_social_sharing:
  - 1
sf_background_image_size:
  - cover
sf_page_title_text_style:
  - light
sf_page_title_bg:
  - none
sf_no_breadcrumbs:
  - 1
sf_page_title_style:
  - standard
sf_page_title:
  - 1
sf_detail_type:
  - none
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
sf_caption_position:
  - caption-right
sf_remove_promo_bar:
  - 1
sf_right_sidebar:
  - Sidebar-1
categories:
---

Hello Oozie users,

We are really excited to announce several improvements for Oozie in the upcoming Hue 3.10 (~April ETA) that enhance its usability and robustness. Here is the new feature list.

&nbsp;

\*\*External Workflow Graph

\*\* <span style="font-weight: 400;">Hue supports workflow execution from Workflow Editor and File-browser. After submission, Hue takes the user to the Workflow dashboard page that shows the execution flow graph among other data. Earlier, this functionality was only supported when the workflow was submitted from the Editor. This feature </span><span style="font-weight: 400;"><span style="font-weight: 400;">enables us to see the graph for workflows submitted form File-browser as well as the ones submitted from CLI. Here is a video that demonstrates this.</span></span>

{{< youtube ObwBkiIqxeA >}}

&nbsp;

\*\*Single Action Execution

\*\* This feature enables you to execute actions individually after a workflow is saved. Using the play button at the top right corner of an action, you can submit an individual action which helps you to test the correctness of your workflow.

<a href="https://cdn.gethue.com/uploads/2016/03/single_action.png" ><img src="https://cdn.gethue.com/uploads/2016/03/single_action.png" /></a><!--more-->

&nbsp;

\*\*Update Workflow of Running Coordinator

\*\* Earlier, after running a coordinator it wasn't possible to make small changes to the workflow it's pointing to. One had to kill and rerun the coordinator for the changes to take effect. Now, using the Sync Workflow button at the bottom left corner of the coordinator dashboard page, you can merge the new changes into a running coordinator. The workflow changes will only impact the actions that haven't started yet.

<a href="https://cdn.gethue.com/uploads/2016/03/sync-wf-coordinator.png" ><img src="https://cdn.gethue.com/uploads/2016/03/sync-wf-coordinator-1024x495.png"/></a>

&nbsp;

\*\*Dryrun Oozie job

\*\* The <tt>dryrun</tt> option tests running a workflow/coordinator/bundle job with given properties and does not create the job. Now, you can dryrun a job by selecting the checkbox before you submit it as shown in the below figure.

&nbsp;

<a href="https://cdn.gethue.com/uploads/2016/03/Dryrun.png" ><img src="https://cdn.gethue.com/uploads/2016/03/Dryrun-1024x587.png"/></a>

\*\*Timezone improvements

\*\* First, all the times on the dashboard are now defaulted to browser timezone. For example, submission/completion times for workflows and start/completion times for coordinator. Second, when submitting a coordinator/bundle, user is no longer needed to enter times in UTC. Now, the user has an option to choose any timezone and enter the time. Lastly, hue 3.10 supports `oozie.processsing.timezone`(Oozie server processing timezone) by doing the timezone conversion locally before submission.

<a href="https://cdn.gethue.com/uploads/2016/03/timezone.png" ><img src="https://cdn.gethue.com/uploads/2016/03/timezone-1024x306.png"/></a>

&nbsp;

\*\*Upgrade email action schema to 0.2

\*\* The new email action supports bcc, attachment and content type.

<a href="https://cdn.gethue.com/uploads/2016/03/email.png" ><img src="https://cdn.gethue.com/uploads/2016/03/email.png"/></a>

&nbsp;

\*\*Emailing automatically on failure

\*\* Each kill node now embed an optional email action. Edit a kill node to insert a custom message if case it gets called.

&nbsp;

<a href="https://cdn.gethue.com/uploads/2016/03/oozie-email-opened.png" ><img src="https://cdn.gethue.com/uploads/2016/03/oozie-email-opened.png"/></a>

\*\*Generic action is back!

\*\* This action lets you insert your any action XML verbatim in case you have some custom Oozie action.

&nbsp;

<a href="https://cdn.gethue.com/uploads/2016/03/oozie-generic-action.png" ><img src="https://cdn.gethue.com/uploads/2016/03/oozie-generic-action.png"/></a>

&nbsp;

\*\*Workflow submission history is back!

\*\* The icon in the top menu will list the series of past submission of the workflow.

&nbsp;

<a href="https://cdn.gethue.com/uploads/2016/03/oozie-submission-history.png" ><img src="https://cdn.gethue.com/uploads/2016/03/oozie-submission-history.png"/></a>

&nbsp;

Other significant improvements include improving the dashboard [response time][1] (thanks to pagination and optimization the page should not take more than 1-3s for busy dashboards), retry configuration for any action. There is a lot more exciting stuff coming up like drag & dropping any saved SQL query directly into a workflow ([HUE-1389][2]) and import existing action from other workflows ([HUE-2994][3]).

As always, feel free to suggest new improvements or comment on the [hue-user][4] list or [@gethue][5]!

[1]: https://issues.cloudera.org/browse/HUE-3185
[2]: https://issues.cloudera.org/browse/HUE-1389
[3]: https://issues.cloudera.org/browse/HUE-2994
[4]: http://groups.google.com/a/cloudera.org/group/hue-user
[5]: https://twitter.com/gethue
