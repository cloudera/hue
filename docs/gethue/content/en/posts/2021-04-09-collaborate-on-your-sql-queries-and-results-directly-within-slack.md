---
title: Collaborate on your SQL queries and results directly within Slack!
author: Hue Team
type: post
date: 2021-04-09T00:00:00+00:00
url: /blog/2021-04-09-collaborate-on-your-sql-queries-and-results-directly-within-slack
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
sf_remove_promo_bar:
  - 1
ampforwp-amp-on-off:
  - default
categories:
  - Version 4.10

---
<p align="center"> Introducing the Slack integration for Hue SQL Editor </p>


The Hue project which is celebrating its 11th anniversary this year is based on these three principles:

<h3 align="center"> Query. Explore. Share. </h3>

The ‘Share’ principle got its last improvement with the introduction of [Public Links and Gist Sharing](https://gethue.com/blog/2020-03-04-datawarehouse-database-sql-collaboration-and-sharing-with-link-and-gist/) for better collaboration. Following that path, it is time for the next improvement ;)

What could be better than improving the collaboration by using one of the best communication platforms present - **Slack!**

**And when there is Slack, there are Slack Apps!** And our beloved Hue is getting one!

Although currently in **beta**, this app integration expands the ability to share query links or gists to the desired Slack channels which then unfurls in a rich preview for other users. It even gives you the result file if the result has not expired.

![Share to Slack Architecture](https://cdn.gethue.com/uploads/2021/04/share_to_slack_architecture.png)

The main bot logic lies on top of the Hue server listening to the events posted by the Hue App from Slack to an endpoint, processing the data accordingly and using Slack API methods for sending the desired response.

To set-up the SQL Assistant App, follow these steps mentioned in the [Hue docs](https://docs.gethue.com/administrator/configuration/server/#manual-slack-app-installation)

Now, open Editor, run some query and copy its link:

![Run Query in Editor](https://cdn.gethue.com/uploads/2021/04/run_query_in_hue.png)

Paste it in the Slack channel and see the unfurling magic!

![Query Link Preview](https://cdn.gethue.com/uploads/2021/04/query_link_preview.png)

### Wonder why result is shown like this?

Slack currently does not support markdown tables and potential improvements with inline preview will come when Hue supports result caching via [query tasks](https://docs.gethue.com/administrator/administration/reference/#task-server).

After evaluating a lot of possible fixes (like uploading result image, truncating columns which doesn't look good, pivoting table, [uploading result file](https://github.com/slackapi/python-slack-sdk/issues/991) etc.) and seeing their tradeoffs, we chose to have few sample rows but keep all columns by pivoting the result table and to compensate for the loss of rows, Hue app gives the result file in the message thread.

![Message Thread with Result File](https://cdn.gethue.com/uploads/2021/04/message_thread_with_result_file.png)

Users can share the SQL gists too!

![Gist Link](https://cdn.gethue.com/uploads/2021/04/gist_link.png)

![Gist Link Preview](https://cdn.gethue.com/uploads/2021/04/gist_link_preview.png)

### Read access

Keeping in mind the security aspect, those Slack users who are Hue users and have the read permissions to access the query and its result will get this rich preview and result file after sharing the link. This mapping is currently done by checking the email prefix and its host for Hue username.

For example, some person ‘Alice’ having a Hue account with username ‘alice’ can have read access from some Slack account only if it's the same email address from the same domain. i.e. **alice@gethue.com slack user** can only access **Hue user ‘alice’** on **hue.gethue.com**.

### What's coming up next?

In the follow-ups, promoting the Share to Slack from the Hue side where users can select the channel to send the link.

Also stay tuned for more such functionalities such as replying to users asking questions on how to find certain data tables or to query them and also send results for scheduled queries in certain Slack channels!
### Try it out!

Log in to the [Slack workspace](https://hue-sql-assistant.slack.com/) to access the demo SQL Assistant by using the following Slack account credentials:

      email: demo@gethue.com
      password: gethue

Read its [user guide](https://docs.gethue.com/user/concept/#share-to-slack) and stay tuned for upcoming updates.

Till then, run some queries, copy those links and share ‘em all!

</br>
</br>

Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!

Onwards!

Harsh from the Hue Team
