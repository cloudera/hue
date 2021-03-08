---
title: Auditing User Administration Operations with Hue and Cloudera Navigator
author: admin
type: post
date: 2015-12-07T18:27:02+00:00
url: /auditing-user-administration-operations-with-hue-and-cloudera-navigator-2/
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
With the latest release of [Hue 3.9][1], we've added an additional layer of monitoring for Hue administrators.

Hue user administration operations can now be audited and written to a configurable audit log. Administrators can then use [Cloudera Navigator's Auditing Component][2] to view, search, filter, and generate reports on these audited events.

<figure><a href="https://cdn.gethue.com/uploads/2015/12/Navigator-blog-post-diagram.png"><img src="https://cdn.gethue.com/uploads/2015/12/Navigator-blog-post-diagram.png" /></a><figcaption>Tracking and audit events like the logins in Hue</figcaption></figure>

&nbsp;

Hue admins can thus easily `monitor` superuser operations such as adding/editing users and groups, editing permissions, and user logins/logouts. Most importantly, admins can easily `detect` when unauthorized attempts at these operations have been made, and capture the related metadata for those unauthorized attempts.

To enable and configure the log file used for the audit log, there are 2 new configuration properties that have been added to the hue.ini file, and can be overridden in [Cloudera Manager's Service Access Audit Log Properties][4] controls.

<pre><code class="bash">[desktop]

\# The directory where to store the auditing logs. Auditing is disable if the value is empty.

\# e.g. /var/log/hue/audit.log

audit_event_log_dir=/Users/jennykim/Dev/hue/logs/audit.log

\# Size in KB/MB/GB for audit log to rollover.

audit_log_max_file_size=100MB

</code></pre>

After configuring the audit log and restarting Hue, you can then start viewing the audited operations by tailing the log:

<pre><code class="bash">$ tail logs/audit.log

{"username": "admin", "impersonator": "hue", "eventTime": 1447271632364, "operationText": "Successful login for user: admin", "service": "accounts", "url": "/accounts/login/", "allowed": true, "operation": "USER_LOGIN", "ipAddress": "127.0.0.1"}

{"username": "admin", "impersonator": "hue", "eventTime": 1447271704937, "operationText": "Created Group: admins, with member(s): jennykim, admin, hue", "service": "useradmin", "url": "/useradmin/groups/new", "allowed": true, "operation": "CREATE_GROUP", "ipAddress": "127.0.0.1"}

{"username": "admin", "impersonator": "hue", "eventTime": 1447271778278, "operationText": "Created Group: readonly, with member(s): ", "service": "useradmin", "url": "/useradmin/groups/new", "allowed": true, "operation": "CREATE_GROUP", "ipAddress": "127.0.0.1"}

{"username": "admin", "impersonator": "hue", "eventTime": 1447271788277, "operationText": "Successfully edited permissions: useradmin/access", "service": "useradmin", "url": "/useradmin/permissions/edit/useradmin/access", "allowed": true, "operation": "EDIT_PERMISSION", "ipAddress": "127.0.0.1"}

</code></pre>

Each audited record contains fields for:

  * **username** of the user executing the action
  * **impersonator** user (always "hue" in this case)
  * **eventTime** in milliseconds since epoch
  * **allowed**, true if operation was authorized, false otherwise
  * **operation** (e.g. - USER_LOGIN, CREATE_USER, CREATE_GROUP, EDIT_PERMISSION, etc.)
  * **operationText**, descriptive text of the operation
  * **service**
  * **url**
  * **ipAddress** of client

Currently, Hue audits the following authentication and useradmin actions:

  * USER_LOGIN, USER_LOGOUT
  * CREATE_USER, DELETE_USER, EDIT_USER
  * CREATE_GROUP, DELETE_GROUP, EDIT_GROUP
  * ADD_LDAP_USERS, ADD_LDAP_GROUPS, SYNC_LDAP_USERS_GROUPS
  * EDIT_PERMISSION

If you are running Hue with Cloudera Enterprise, you can then view and manage the audit report from Cloudera Navigator and filter on the Service Name for Hue, in this case "HUE-1":

<figure><a href="https://cdn.gethue.com/uploads/2015/12/navigator1-1024x361.png"><img src="https://cdn.gethue.com/uploads/2015/12/navigator1-1024x361.png" /></a><figcaption>Navigator Audits</figcaption></figure>

&nbsp;

You can expand any audit record to view the metadata for a given operation, including whether it was allowed/authorized, the impersonated user and additional details specific to the operation.

<figure><a href="https://cdn.gethue.com/uploads/2015/12/navigator_expand_details-e1449474038525-1024x283.png"><img src="https://cdn.gethue.com/uploads/2015/12/navigator_expand_details-e1449474038525-1024x283.png" /></a><figcaption>Navigator Audit Details</figcaption></figure>

&nbsp;

Hue + Navigator provide rich data discovery, audit and policy enforcement features and Hue is evolving in a more enterprise compliance friendly product. If you have any questions, feel free to comment here or on the [hue-user][7] list or [@gethue][8]!

 [1]: https://gethue.com/hue-3-9-with-all-its-improvements-is-out/
 [2]: http://www.cloudera.com/content/www/en-us/documentation/enterprise/latest/topics/cn_iu_audit_arch.html
 [3]: https://cdn.gethue.com/uploads/2015/12/Navigator-blog-post-diagram.png
 [4]: http://www.cloudera.com/content/www/en-us/documentation/enterprise/latest/topics/cn_iu_audit_log.html
 [5]: https://cdn.gethue.com/uploads/2015/12/navigator1.png
 [6]: https://cdn.gethue.com/uploads/2015/12/navigator_expand_details.png
 [7]: http://groups.google.com/a/cloudera.org/group/hue-user
 [8]: https://twitter.com/gethue
