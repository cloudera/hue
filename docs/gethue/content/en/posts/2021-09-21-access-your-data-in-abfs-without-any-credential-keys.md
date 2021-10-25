---
title: Access your data in ABFS without any credential keys!
author: Hue Team
type: post
date: 2021-09-21T00:00:00+00:00
url: /blog/2021-09-21-access-your-data-in-abfs-without-any-credential-keys/
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
  - Version 4.11
  - Development
  - Browsing

---

<p align="center"> Using Shared Access Signatures (SAS) to manage files and its operations </p>

Previously, we talked about [providing S3 data access without giving out actual credentials](/blog/2021-04-23-s3-file-access-without-any-credentials-and-signed-urls/) via S3 signed URLs. This time, this feature is coming for another major cloud provider in the market, **Microsoft Azure!**

This main use case remains the same which is to keep things simple for the end users and walk one more step on the path towards unlocking true self-service querying.

The **WHY** behind this, also remains the same which has been discussed in the previous S3 access blog. The only thing which has changed is extending this to ADLS via Azure SAS tokens!

## Where does Azure SAS actually fit in?

A [SAS](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview) is a token to append to the URI (i.e. path) of your storage objects which grants restricted access rights to those objects (meaning you can grant users access to a resource for a specified period of time, with a specified set of permissions). The SAS tokens are ‘signed’ and safe to provide publicly to the users.

Hue does not require any ADLS credentials now and neither does it generate the SAS token. Hue just asks in this example to a [RAZ Server](https://blog.cloudera.com/access-control-for-azure-adls-cloud-object-storage/) to provide the equivalent SAS token for the ADLS call (REST APIs) a user wants to make via the File Browser.

![Before: Users interacting with ADLS via Hue and a shared credential key (not very safe and not the best)](https://cdn.gethue.com/uploads/2021/09/before_raz_adls.png)<br>*Before: Users interacting with ADLS via Hue and a shared credential key (not very safe and not the best)*

<br>

![After: Users getting individual temporary SAS tokens letting them access any ADLS resource (safe and fine grain access possible)](https://cdn.gethue.com/uploads/2021/09/after_raz_adls.png)
<br>*After: Users getting individual temporary SAS tokens letting them access any ADLS resource (safe and fine grain access possible)*

<br>

One of the magic pieces is the RAZ server, which generates a temporary SAS for an ADLS call and sends it back to Hue. RAZ is also leveraging [Apache Ranger](https://ranger.apache.org/) which provides authorization and fine grain permissions *(i.e. who can access this container? Who can upload a file in this directory?)*.

Here’s a **list directory** operation call via the Hue shell:

    In [1]: from desktop.lib.fsmanager import get_client
    ......: fs = get_client('default', 'abfs', 'csso_hueuser')
    ......: fs.listdir('abfs://data/user/csso_hueuser/test_dir')

More such ADLS operations are documented [here](https://docs.gethue.com/developer/api/python/#adls).

RAZ is not open source, but the underlying integration with such a server with Hue is!

![Big picture: mainly on the left side we see the Hue File System lib, which is generic enough to provide File Browsing for any storage system (HDFS, S3 native, S3 via Signed URLs, ADLS native, ADLS via SAS tokens). On the right, this is about how to build clients that can interact with services that can generate SAS tokens for each call.](https://cdn-images-1.medium.com/max/3448/1*PZduhj0fHrxw-PVlue8aeA.png)
*Big picture: mainly on the left side we see the Hue File System lib, which is generic enough to provide File Browsing for any storage system (HDFS, S3 native, S3 via Signed URLs, ADLS…). On the right, this is about how to build clients that can interact with services that can generate signed URLs for each call.*

The above diagram describes the internal implementation in Hue. It might look complicated at first ;) but it enables a step forward towards true Self Service Querying!

</br>
</br>

Any [feedback](https://github.com/cloudera/hue/issues) or question is highly welcomed! Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!

Onwards!

Harsh from the Hue Team
