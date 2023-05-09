---
title:  Discover the power of Apache Ozone using the Hue File Browser
author: Hue Team
type: post
date: 2023-05-03T00:00:00+00:00
url: /blog/discover-the-power-of-apache-ozone-using-the-hue-file-browser/
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
  - Version 5.0
  - Browsing

---

Greetings, Ozone users!

Hue officially supports browsing Apache Ozone using the Hue File Browser. Hue can be set-up to seamlessly read and write to a configured Apache Ozone filesystem service, and users can directly query from and save data in it.

![Ozone Hue integration](https://cdn.gethue.com/uploads/2023/05/Hue_Ozone_UI.png)

## Exploring the Ozone filesystem using Hue
Apache Ozone is a highly scalable, distributed storage solution for analytics, big data, and cloud native applications. It is an efficient object store and optimized for filesystem operations. Ozone offers a multi-protocol filesystem that now supports HttpFS REST APIs.

Hue integrates with these HttpFS APIs to offer a convenient method for browsing and accessing the entirety of an Ozone filesystem, including all volumes, buckets, and directories.

![High Level Architecture](https://cdn.gethue.com/uploads/2023/05/HueFS.png)

In addition to simplifying navigation, this approach allows for easier maintenance of the integration. As Ozone continues to expand support for additional HttpFS APIs, future updates to Hue will provide even greater functionality, such as expanded filesystem operations and capabilities!

## Getting Started

To configure Hue for Ozone file browsing, make the necessary changes to the hue.ini configuration file. Add the following settings under `[desktop]`, and within the `[[ozone]]` section:

```
[[[default]]]
fs_defaultfs=ofs://[**SERVICE_ID**]
webhdfs_url=http(s)://[***OZONE-HTTPFS-HOST***]:[***OZONE-HTTPFS-PORT***]/webhdfs/v1
ssl_cert_ca_verify=true
security_enabled=true
```
Where,
- **fs_defaultfs**: Ozone service ID (HA mode) or URL for Ozone Manager (non-HA mode).
- **webhdfs_url**: URL of HttpFS endpoint for the running Ozone service.

</br>
</br>

For feedback, questions, or suggestions, feel free to comment on the [GitHub Discussions](https://github.com/cloudera/hue/discussions) and [quick start](https://docs.gethue.com/quickstart/) SQL querying!

Upwards and Onwards!


[Harsh](https://github.com/Harshg999) and [Ayush](https://github.com/agl29) from the Hue Team
