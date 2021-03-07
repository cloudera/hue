---
title: How to Configure Hue to enable S3 file browser for standard or V4 regions
author: admin
type: post
date: 2018-09-11T15:44:50+00:00
url: /how-to-configure-hue-to-enable-s3-file-browser-for-standard-or-v4-regions/
sf_left_sidebar:
  - Sidebar-2
sf_sidebar_config:
  - left-sidebar
sf_related_articles:
  - 1
sf_social_sharing:
  - 1
sf_author_info:
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
sf_thumbnail_link_type:
  - link_to_post
sf_thumbnail_type:
  - none
ampforwp-amp-on-off:
  - default
sf_remove_promo_bar:
  - 1
sf_caption_position:
  - caption-right
sf_right_sidebar:
  - Sidebar-1
categories:
  - Version 4

---
Hello, S3 cloud users,

Hue started [supporting S3][1] since Hue 3.9. Let’s go through the detailed steps to enable S3 on Hue for CM-managed cluster:

1. Go to your CM UI: http://$YOURCMHost:7180/cmf/home

2. Click on “Administration”->”External Accounts”, http://$YOURCMHost:7180/cmf/accounts?category=AWS

3. On tab “AWS Credentials”

[<img class="aligncenter wp-image-5508" src="https://cdn.gethue.com/uploads/2018/09/AWSCredentials.png"/>][2]

Click on “Add Access Key Credentials” button to land following dialog

[<img class="aligncenter wp-image-5510" src="https://cdn.gethue.com/uploads/2018/09/Add_S3_keys.png"/>][3]

4. Filled in your S3 key id and secret key then click “Add” to land follow page:

[<img class="aligncenter wp-image-5511" src="https://cdn.gethue.com/uploads/2018/09/S3GuardOption.png"/>][4]

5. Keep “Enable S3Guard” unchecked and Click “Save” to land follow page:

[<img class="aligncenter wp-image-5512" src="https://cdn.gethue.com/uploads/2018/09/EnableForCluster1.png"/>][5]

6. Then click on “Enable for Cluster 1” to follow the wizard to “Add S3 Connector Service to Cluster 1”

[<img class="aligncenter wp-image-5513" src="https://cdn.gethue.com/uploads/2018/09/EnableS3OnCluster.png"/>][6]

By default choose “More Secure” option (Hive S3 integration will not work out of the box, but impala/HDFS/Hue works); If you do need hive query editor to work with S3, choose “Less Secure” option here.

7. Click “Continue” and “Restart Now”

[<img class="aligncenter wp-image-5515" src="https://cdn.gethue.com/uploads/2018/09/RestartNow.png"/>][7]

8. Click “Continue”

[<img src="https://cdn.gethue.com/uploads/2018/09/RestartAwaitingStalenessComputation.png"/>][8]

9. Click “Continue” then "Finish"

[<img src="https://cdn.gethue.com/uploads/2018/09/Finished.png"/>][9]

Hooray, now you are able to use S3 in HUE. You can create tables with CSV files at S3 locations or save/export query results to S3 locations(all V2 regions).

[<img src="https://cdn.gethue.com/uploads/2018/09/Hue-S3-Browsers2.png"/>][10]

**Configure cluster for [V4 region][11] access**

If you need access bucket in any S3 V4 region like “s3.eu-central-1.amazonaws.com”, remember to config it through CM on following page:

http://$YourCMHost:7180/cmf/services/14/config?q=s3_endpoint#filterfreeText=s3_endpoint

[<img src="https://cdn.gethue.com/uploads/2018/09/Configure-s3a-endpoint.png"/>][12]

Fill in the s3 endpoint like: s3.eu-central-1.amazonaws.com then click “Save Changes”

Then “Restart stale services” (Re-deploy client configuration-Restart Now)

Now you are ready to create/use S3 buckets in your configured V4 region.

[<img src="https://cdn.gethue.com/uploads/2018/09/V4_RegionAccess.png"/>][13]

 [1]: https://gethue.com/introducing-s3-support-in-hue/
 [2]: https://cdn.gethue.com/uploads/2018/09/AWSCredentials.png
 [3]: https://cdn.gethue.com/uploads/2018/09/Add_S3_keys.png
 [4]: https://cdn.gethue.com/uploads/2018/09/S3GuardOption.png
 [5]: https://cdn.gethue.com/uploads/2018/09/EnableForCluster1.png
 [6]: https://cdn.gethue.com/uploads/2018/09/EnableS3OnCluster.png
 [7]: https://cdn.gethue.com/uploads/2018/09/RestartNow.png
 [8]: https://cdn.gethue.com/uploads/2018/09/RestartAwaitingStalenessComputation.png
 [9]: https://cdn.gethue.com/uploads/2018/09/Finished.png
 [10]: https://cdn.gethue.com/uploads/2018/09/Hue-S3-Browsers2.png
 [11]: https://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region
 [12]: https://cdn.gethue.com/uploads/2018/09/Configure-s3a-endpoint.png
 [13]: https://cdn.gethue.com/uploads/2018/09/V4_RegionAccess.png
