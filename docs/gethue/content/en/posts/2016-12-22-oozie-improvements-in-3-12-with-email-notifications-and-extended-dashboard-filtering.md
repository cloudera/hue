---
title: Oozie Improvements with email notifications and extended dashboard filtering
author: admin
type: post
date: 2016-12-22T01:03:38+00:00
url: /oozie-improvements-in-3-12-with-email-notifications-and-extended-dashboard-filtering/
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
categories:

---
Hello Oozie users,

Among other improvements, [Hue 3.12][1] comes with two very useful updates in Oozie.

**Email Notifications**

With [HUE-4995][2], it is very easy to send an email notification after a workflow execution is complete. The following steps will guide you to enable this.

In the Workflow submission popup, if your email is not already setup, the email notification checkbox is disabled[<img src="https://cdn.gethue.com/uploads/2016/12/email-not-set.png" width="590" height="213" />][3]

Clicking on `profile` button should take you to the u_seradmin_ page, where you can save your email.

[<img src="https://cdn.gethue.com/uploads/2016/12/useradmin.png" width="569" height="475" />][4]

After this, the workflow submission popup will show the `Send completion email` checkbox, which can be enabled to receive the email notification.[<img src="https://cdn.gethue.com/uploads/2016/12/send-email-checkbox.png" width="591" height="212" />][5]

### **Note**

If [SMTP server][6] is not configured in Oozie, you will see the following configuration alert in the quick start page.

[<img src="https://cdn.gethue.com/uploads/2016/12/config-alert.png" width="743" height="439" />][7]

**Extended Dashboard Filtering ([OOZIE-2225][8] & [HUE-5202][9])**

##### [requires Apache Oozie 5.0+]

Just start typing in the text field to get the list of jobs whose _Name_ or _Submitter_ partially matches with the text. From the below picture, you can see that text _sh_ partially matches with the names of all 4 jobs. Note that the filter is applied on all the jobs and not just the ones in the current page.

[<img src="https://cdn.gethue.com/uploads/2016/12/name-search.png" width="1157" height="592" />][10]

To find the one single job among thousands of submitted jobs, you should enter the complete ID as shown below.

[<img src="https://cdn.gethue.com/uploads/2016/12/id-search.png" width="1173" height="280" />][11]

### Note

Flag to enable Oozie backend filtering instead of doing it at the page level in Javascript. Requires Oozie 5.0+.

`[oozie]<br />
enable_oozie_backend_filtering=true`

As always, feel free to suggest new improvements or comment on the [hue-user][12] list or [@gethue][13]!

 [1]: https://gethue.com/category/hue-3-12/
 [2]: https://issues.cloudera.org/browse/HUE-4995
 [3]: https://cdn.gethue.com/uploads/2016/12/email-not-set.png
 [4]: https://cdn.gethue.com/uploads/2016/12/useradmin.png
 [5]: https://cdn.gethue.com/uploads/2016/12/send-email-checkbox.png
 [6]: https://oozie.apache.org/docs/3.3.0/DG_EmailActionExtension.html
 [7]: https://cdn.gethue.com/uploads/2016/12/config-alert.png
 [8]: https://issues.apache.org/jira/browse/OOZIE-2225
 [9]: https://issues.cloudera.org/browse/HUE-5202
 [10]: https://cdn.gethue.com/uploads/2016/12/name-search.png
 [11]: https://cdn.gethue.com/uploads/2016/12/id-search.png
 [12]: http://groups.google.com/a/cloudera.org/group/hue-user
 [13]: https://twitter.com/gethue
