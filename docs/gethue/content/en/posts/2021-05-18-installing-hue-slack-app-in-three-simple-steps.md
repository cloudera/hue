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
Slack recently rolled out its [App Manifest](https://api.slack.com/reference/manifests) beta feature for Slack Apps. With a manifest, you can create an app with a predefined configuration.

Using this feature, the Hue App can now be installed in your Slack workspace in just 3 simple steps!

The latest version of the App Manifest is checked-in the [Hue Repo](https://github.com/cloudera/hue/tree/master/tools/slack).

In the shared Manifest, update with your Hue instance hostname at two locations
- Under **unfurl_domains** (e.g. hue.gethue.com)
- Under **event_subscriptions**, update **request_url** `https://<hue-instance-hostname>/desktop/slack/events/`

Now, it's time to create your own app

1. Go to https://api.slack.com/apps and click **Create New App**.
2. Choose **From an app manifest** option and workspace that you'll be installing the app and click** Next**.
3. Choose **YAML** and paste the Manifest code (make sure you do the necessary changes mentioned above) and click **Next**.
4. Read the review summary and if everything’s correct, click **Create**.
5. Once the app is created, install it in the workspace!

Completing the last step of the puzzle, it's time to update your hue.ini configuration file

6. Go to the **OAuth & Permissions page**, copy the **Bot User OAuth Token** and update **slack_bot_user_token** (e.g. xoxb-xxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxx)
7. Similarly, go to the **Basic Information** page, copy the **Verification Token** and update **slack_verification_token**
8. Paste this in your hue.ini file under `[desktop]` section

        [[slack]]
        is_enabled=true
        slack_verification_token=<your-slack-verification-token>
        slack_bot_user_token=<your-slack-bot-user-token>

That’s it! Your own Hue App is ready to go!

Read its [user guide](https://docs.gethue.com/user/concept/#share-to-slack) and [feedback](https://github.com/cloudera/hue/issues) is highly welcomed!

### Try it out!

Get your hands on demo Hue App by:

Running some queries on the [demo live editor](https://demo.gethue.com/).

Joining the [demo Slack workspace](https://join.slack.com/t/hue-bot-dev/shared_invite/zt-opqwvv68-eQFeios8FzFbmqQJ5wBNzg) to see the app in action or by using the following credentials:

    Slack account email: demo@gethue.com
    Slack account password: gethue

Till then, run some queries, copy those links and share ‘em all!

</br>
</br>

Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!


Onwards!

Harsh from the Hue Team
