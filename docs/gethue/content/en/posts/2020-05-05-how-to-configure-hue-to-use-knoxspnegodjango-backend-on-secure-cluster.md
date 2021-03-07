---
title: How to Configure Hue to authenticate with Apache Knox SSO on a Secure Cluster
author: Weixia Xu
type: post
date: 2020-05-05T00:00:00+00:00
url: /blog/how-to-configure-hue-to-use-knoxspnegodjango-backend/
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
ampforwp-amp-on-off:
  - default
categories:
  - Version 4
#  - Version 4.8

---
Hello, Hue administrators,

The [Apache Knox™ Gateway](https://knox.apache.org/) is an Application Gateway for interacting with the REST APIs
 and UIs of Apache Hadoop deployments.

Hue supports KnoxSpnegoDjango since Hue4.6, we can turn on Hue’s KnoxSpnegoDjango auth by updating Hue configurations
 through CM UI or hue.ini.

On any cluster with Knox service installed, update hue.ini as following and restart Hue:

    [desktop]
    [[auth]]
    backend=desktop.auth.backend.KnoxSpnegoDjangoBackend
    [[knox]]
    knox_principal=knox
    knox_proxyhosts=weixia-1.domain.site,weixia-2.domain.site

Or on any CM managed cluster, Hue can be configured with KnoxSpnegoDjango backend through CM UI:
![hue-auth-knoxspnego.png](https://cdn.gethue.com/uploads/2020/05/hue-auth-knoxspnego.png)

Fill knox_proxyhosts field with accurate knox proxy hostname, you can get the hosts by navigating to Clusters->KNOX, and
click on 'Instances' tab:
![knox-ha-hosts.png](https://cdn.gethue.com/uploads/2020/05/knox-ha-hosts.png)
For Knox HA cluster, you can fill in all the hosts by clicking on "+" icon:
![configure-hue-with-knox-ha.png](https://cdn.gethue.com/uploads/2020/05/configure-hue-with-knox-ha.png)

Click 'Save Changes', you will see a warning about role missing kerberos keytab. Click on “Administration”-->”Security” as shown below:
![role-missing-kerberos-keytab.png](https://cdn.gethue.com/uploads/2020/05/role-missing-kerberos-keytab.png)
![generate-missing-credentials.png](https://cdn.gethue.com/uploads/2020/05/generate-missing-credentials.png)
Then navigate back to Clusters->HUE-1, click on the "stale configuration: Restart" icon beside the "Actions" button,
![stale-configuration-restart.png](https://cdn.gethue.com/uploads/2020/05/stale-configuration-restart.png)
follow the wizard to choose "Restart staled services", select "Re-deploy client configuration" and click on "Restart Now",
wait till it finishes.

Navigate to Hue’s Web UI dropdown and select “Knox Gateway UI” to load Knox UI:
![knox-gateway-ui.png](https://cdn.gethue.com/uploads/2020/05/knox-gateway-ui.png)
Then click on “+” icon of “+cdp-proxy” to expand:
![knox-gateway-ui-cdp-proxy.png](https://cdn.gethue.com/uploads/2020/05/knox-gateway-ui-cdp-proxy.png)

Now click on the Hue icon:
![knox-proxy-login-hue-icon.png](https://cdn.gethue.com/uploads/2020/05/knox-proxy-login-hue-icon.png)

You should be able to log in to hue page:

![hue-page.png](https://cdn.gethue.com/uploads/2020/05/hue-page.png)


## Troubleshooting
1. If you hit error like "The username or password you entered is incorrect."

![incorrect-user-or-password.png](https://cdn.gethue.com/uploads/2020/05/incorrect-user-or-password.png)

Check on your knox proxy hosts that user or password is correct.

    ssh root@weixia-1.domain.site
    useradd weixia
    passwd weixia

2. If you hit 403 error:

![hue-login-403.png](https://cdn.gethue.com/uploads/2020/05/hue-login-403.png)

Log in to your ranger service and ensure your user or group say 'public' has proper permissions.

![ranger-cm-knox-policies.png](https://cdn.gethue.com/uploads/2020/05/ranger-cm-knox-policies.png)

Any feedback or questions? Feel free to comment here or on the [Forum](https://discourse.gethue.com/) or
[@gethue](https://twitter.com/gethue) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Weixia Xu from the Hue Team
