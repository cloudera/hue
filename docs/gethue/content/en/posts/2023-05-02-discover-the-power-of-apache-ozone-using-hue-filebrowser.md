---
title:  Discover the Power of Apache Ozone using Hue Filebrowser
author: Hue Team
type: post
date: 2023-05-02T00:00:00+00:00
url: /blog/discover-the-power-of-apache-ozone-using-hue-filebrowser/
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

Hue has recently added official support for browsing Apache Ozone using its file browser! Hue can be set-up to seamlessly read and write to a configured Apache Ozone file system service, and users can directly query from and save data in it.

![Ozone Youtube Video]()

### Exploring Ozone in Hue
Apache Ozone is a highly scalable, distributed storage solution for analytics, big data, and cloud native applications. It is optimized for both efficient object store and file system operations. Ozone offers a multi-protocol file system that recently has started supporting HttpFS REST APIs. 

Hue integrates with these HttpFS APIs to offer a convenient method for browsing and accessing the entirety of an Ozone file system, including all volumes, buckets, and directories.

![High Level Architecture]()

In addition to simplifying navigation, this approach allows for easier maintenance of its features. As Ozone continues to expand support for additional HttpFS APIs, future updates to Hue will provide even greater functionality, such as expanded file system capabilities!

### Getting Started

To configure Hue for Ozone file browsing, make the necessary changes to the hue.ini configuration file.

Add the following settings under the `[desktop]` section, within the `[[ozone]]` section:

```
[[[default]]]
fs_defaultfs=ofs://[**SERVICE_ID**]
webhdfs_url=http://[***OZONE-HTTPFS-HOST***]:[***OZONE-HTTPFS-PORT***]/webhdfs/v1
ssl_cert_ca_verify=true
security_enabled=true
```

- **fs_defaultfs**: Ozone service ID (HA mode) or URL for Ozone Manager (non-HA mode).
- **webhdfs_url**: URL of HttpFS endpoint for the running Ozone service.

![Ozone Hue integration]()


</br>
</br>
For feedback, questions, or suggestions, feel free to comment on ![GitHub Discussions](https://github.com/cloudera/hue/discussions) and ![quick start](https://docs.gethue.com/quickstart/) SQL querying!


Upwards and Onwards!


[Harsh](https://github.com/Harshg999) and [Ayush](https://github.com/agl29) from the Hue Team
