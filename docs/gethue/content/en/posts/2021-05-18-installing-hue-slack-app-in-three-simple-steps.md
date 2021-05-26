---
title: Installing Hue Slack App in 3 Simple Steps!
author: Hue Team
type: post
date: 2021-05-18T00:00:00+00:00
url: /blog/2021-05-18-installing-hue-slack-app-in-three-simple-steps
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
Ever wondered about having a SQL Assistant which can help you to collaborate better with other SQL users in your team? That too in Slack itself!?

This Slack Integration for Hue can fit those shoes for assisting you with your SQL queries in your Slack channels. [Easy to use](https://docs.gethue.com/user/concept/#slack) and now even easy to install for Slack workspace admins in just 3 simple steps!

Kudos to Slack for recently rolling out its [App Manifest](https://api.slack.com/reference/manifests) beta feature for Slack Apps! With a manifest now, you can create an app with a predefined configuration.

The latest version of the App Manifest is checked-in the [Hue Repository](https://github.com/cloudera/hue/blob/master/tools/slack/manifest.yml).

In the shared manifest, update the two _demo.gethue.com_ with **your Hue instance hostname:**
- Under **unfurl_domains**
- Under **event_subscriptions**, in **request_url** `https://<hue-instance-hostname>/desktop/slack/events/`

Now, it's time to create your own app:
- Go to https://api.slack.com/apps and click **Create New App**.
- Choose **From an app manifest** option and workspace that you'll be installing the app and click **Next**.
- Choose **YAML** and paste the Manifest code (make sure you do the necessary changes mentioned above) and click **Next**.
- Read the review summary and if everything’s correct, click **Create**.
- Once the app is created, install it in the workspace!

![Slack Installation Flow](https://cdn.gethue.com/uploads/2021/05/slack-install.gif)

Completing the last step of plugging it with Hue, it's time to update your hue.ini configuration file:
- Go to the **OAuth & Permissions page**, copy the **Bot User OAuth Token** and update **slack_bot_user_token** (e.g. xoxb-xxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxx)
- Similarly, go to the **Basic Information** page, copy the **Verification Token** and update **slack_verification_token**

And paste this in your hue.ini file under `[desktop]` section

    [[slack]]
    is_enabled=true
    slack_verification_token=<your-slack-verification-token>
    slack_bot_user_token=<your-slack-bot-user-token>

That’s it! Your own Hue App is ready to roll!
### Try it out!

Log in to the [Slack workspace](https://hue-sql-assistant.slack.com/) to access the demo SQL Assistant by using the following Slack account credentials:

      email: demo@gethue.com
      password: gethue

Run some queries on the [demo live editor](https://demo.gethue.com/) and share their links. Read its [user guide](https://docs.gethue.com/user/concept/#share-to-slack) or the [blog](https://gethue.com/blog/2021-04-09-collaborate-on-your-sql-queries-and-results-directly-within-slack/) and stay tuned for upcoming updates.

</br>
</br>

Any [feedback](https://github.com/cloudera/hue/issues) or question is highly welcomed! Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!

Onwards!

Harsh from the Hue Team
