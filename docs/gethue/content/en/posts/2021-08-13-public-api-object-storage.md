---
title: Object/File Storage public REST API
author: Hue Team
type: post
date: 2021-08-13T00:00:00+00:00
url: /blog/2021-08-13-public-api-object-file-storage
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

Leveraging more [REST API](https://docs.gethue.com/developer/api/rest/) into your own project: list, upload, download... data files.

This post comes with a live tutorial of the [file listing API](https://docs.gethue.com/user/browsing/#data).

The [Hue SQL Editor](https://gethue.com/) project has been evolving for more than [10 years](/blog/2020-01-28-ten-years-data-querying-ux-evolution/) and allows you to query any Database or Data Warehouse.

Like previously described in the [SQL Editor API post](/blog/2021-05-29-create-own-sql-editor-via-webcomponent-and-public-api/), all the end user functionalities and under the cover grunt work of integration can be simply reused programmatically (freeing up time to let you focus on the data work itself instead).

The main use cases for the File API is to upload files and create an SQL Table on top of them or retrieve those pesky URIs:
![Filebrowser Copy Path and Open In Importer Options](https://cdn.gethue.com/uploads/2021/08/Filebrowser_copypath_openinimporter.png)

The API leverages the standard credentials of your users (SSO via LDAP, SAML...) and is the same as if they were interacting via the Web UI directly. In bonus, it is Cloud agnostic so end users don't need to learn about the intricacies of each provided and use an interface they are already familiar with.

**Object Storage API**

The simplest operation is to list the content of your buckets or directories.

Start by asking for an API access token (also known as JWT):

    curl -X POST https://demo.gethue.com/api/token/auth -d 'username=demo&password=demo'

    {"refresh":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyOTQ3MTE0MiwianRpIjoiYjNkMDUzN2I1OGU5NDNlZGE0OTJiYzVmOTkzMDEwOTEiLCJ1c2VyX2lkIjoyfQ._MXo09PzisvqY7-1NMVIaLiUCVksYx2ZA5v_PWTk0TY","access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI4OTUyNzQyLCJqdGkiOiJkYTEzZjI2OWY2N2M0MTNiODNiNGYwNzY1ZDA3NzdmMCIsInVzZXJfaWQiOjJ9.47gnDdIwVSo_cULXU856WUgW8FW7UHXMg7FH-dDpoRc"}

Then provide the `access` value in each following calls. In your case, update the examples below with your own:

    Authorization: Bearer <Your access value here>"

Here is how to list the content of a path, here a S3 bucket `s3a://demo-gethue`:

    curl -X GET https://demo.gethue.com/api/storage/view=s3a://demo-gethue -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI4OTUyNzQyLCJqdGkiOiJkYTEzZjI2OWY2N2M0MTNiODNiNGYwNzY1ZDA3NzdmMCIsInVzZXJfaWQiOjJ9.47gnDdIwVSo_cULXU856WUgW8FW7UHXMg7FH-dDpoRc"

    {
      "path": "s3a://demo-gethue",
      "breadcrumbs": [
        {
          "url": "s3a%3A%2F%2F",
          "label": "s3a://"
        },
        {
          "url": "s3a%3A%2F%2Fdemo-gethue",
          "label": "demo-gethue"
        }
      ],
      "current_request_path": "/filebrowser/view=s3a%3A%2F%2Fdemo-gethue",
      "is_trash_enabled": false,
      "files": [
        {
          "path": "s3a://",
          "name": "..",
          "stats": {
            "path": "s3a://",
            "size": 0,
            "atime": null,
            "mtime": null,
            "mode": 16895,
            "user": "",
            "group": "",
            "aclBit": false
          },
          "mtime": "",
          "humansize": "0 bytes",
          "type": "dir",
          "rwx": "drwxrwxrwx",
          "mode": "40777",
          "url": "/filebrowser/view=s3a%3A%2F%2F",
          "is_sentry_managed": false
        },
        {
          "path": "s3a://demo-gethue",
          "name": ".",
          "stats": {
            "path": "s3a://demo-gethue",
            "size": 0,
            "atime": 1628866612,
            "mtime": 1628866612,
            "mode": 16895,
            "user": "",
            "group": "",
            "aclBit": false
          },
          "mtime": "August 13, 2021 02:56 PM",
          "humansize": "0 bytes",
          "type": "dir",
          "rwx": "drwxrwxrwx",
          "mode": "40777",
          "url": "/filebrowser/view=s3a%3A%2F%2Fdemo-gethue",
          "is_sentry_managed": false
        },
        {
          "path": "s3a://demo-gethue/data",
          "name": "data",
          "stats": {
            "path": "s3a://demo-gethue/data/",
            "size": 0,
            "atime": null,
            "mtime": null,
            "mode": 16895,
            "user": "",
            "group": "",
            "aclBit": false
          },
          "mtime": "",
          "humansize": "0 bytes",
          "type": "dir",
          "rwx": "drwxrwxrwx",
          "mode": "40777",
          "url": "/filebrowser/view=s3a%3A%2F%2Fdemo-gethue%2Fdata",
          "is_sentry_managed": false
        }
      ],
      "page": {
        "number": 1,
        "num_pages": 1,
        "previous_page_number": 0,
        "next_page_number": 0,
        "start_index": 1,
        "end_index": 1,
        "total_count": 1
      },
      "pagesize": 30,
      "home_directory": null,
      "descending": null,
      "cwd_set": true,
      "file_filter": "any",
      "current_dir_path": "s3a://demo-gethue",
      "is_fs_superuser": false,
      "groups": [],
      "users": [],
      "superuser": null,
      "supergroup": null,
      "is_sentry_managed": false,
      "apps": [
        "filebrowser",
        "metastore",
        "useradmin",
        "indexer",
        "notebook"
      ],
      "show_download_button": true,
      "show_upload_button": true,
      "is_embeddable": false,
      "s3_listing_not_allowed": ""
    }

Some of the parameters:
 - pagesize=45
 - pagenum=1
 - filter=
 - sortby=name
 - descending=false

e.g. pagesize=45&pagenum=1&filter=&sortby=name&descending=false

Then peek at the data of the `s3a://demo-gethue/data/web_logs/index_data.csv` file:

    curl -X GET https://demo.gethue.com/api/storage/view=s3a://demo-gethue/data/web_logs/index_data.csv -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI4OTUyNzQyLCJqdGkiOiJkYTEzZjI2OWY2N2M0MTNiODNiNGYwNzY1ZDA3NzdmMCIsInVzZXJfaWQiOjJ9.47gnDdIwVSo_cULXU856WUgW8FW7UHXMg7FH-dDpoRc"

    {
      "show_download_button": true,
      "is_embeddable": false,
      "editable": false,
      "mtime": "October 31, 2016 03:34 PM",
      "rwx": "-rw-rw-rw-",
      "path": "s3a://demo-gethue/data/web_logs/index_data.csv",
      "stats": {
      "size": 6199593,
      "aclBit": false,
      ...............
      "contents": "code,protocol,request,app,user_agent_major,region_code,country_code,id,city,subapp,latitude,method,client_ip,  user_agent_family,bytes,referer,country_name,extension,url,os_major,longitude,device_family,record,user_agent,time,os_family,country_code3
        200,HTTP/1.1,GET /metastore/table/default/sample_07 HTTP/1.1,metastore,,00,SG,8836e6ce-9a21-449f-a372-9e57641389b3,Singapore,table,1.2931000000000097,GET,128.199.234.236,Other,1041,-,Singapore,,/metastore/table/default/sample_07,,103.85579999999999,Other,"demo.gethue.com:80 128.199.234.236 - - [04/May/2014:06:35:49 +0000] ""GET /metastore/table/default/sample_07 HTTP/1.1"" 200 1041 ""-"" ""Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)""
        ",Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org),2014-05-04T06:35:49Z,Other,SGP
        200,HTTP/1.1,GET /metastore/table/default/sample_07 HTTP/1.1,metastore,,00,SG,6ddf6e38-7b83-423c-8873-39842dca2dbb,Singapore,table,1.2931000000000097,GET,128.199.234.236,Other,1041,-,Singapore,,/metastore/table/default/sample_07,,103.85579999999999,Other,"demo.gethue.com:80 128.199.234.236 - - [04/May/2014:06:35:50 +0000] ""GET /metastore/table/default/sample_07 HTTP/1.1"" 200 1041 ""-"" ""Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org)""
        ",Mozilla/5.0 (compatible; phpservermon/3.0.1; +http://www.phpservermonitor.org),2014-05-04T06:35:50Z,Other,SGP
      ...............
    }

Some of the parameters:
- offset=0
- length=204800
- compression=none
- mode=text

e.g. ?offset=0&length=204800&compression=none&mode=text

And then decide to download it:

    curl -X GET https://demo.gethue.com/api/storage/download=s3a://demo-gethue/data/web_logs/index_data.csv -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjI4OTUyNzQyLCJqdGkiOiJkYTEzZjI2OWY2N2M0MTNiODNiNGYwNzY1ZDA3NzdmMCIsInVzZXJfaWQiOjJ9.47gnDdIwVSo_cULXU856WUgW8FW7UHXMg7FH-dDpoRc"

- download: file path from any configured remote file system

It is also possible to upload your data directly (if you have the proper write permissions in the remote destination folder):

    curl -X POST https://demo.gethue.com/api/storage/upload/file?dest=s3a://demo-gethue/web_log_data/ --form hdfs_file=@README.md

- dest: folder path will be created if it does not exist yet
- hdfs_file: relative or absolute path to a file. It should be read more like `local_file`, it is not related to HDFS

When the data is stored in the cloud, it becomes easy to create a SQL table so that it can be queried. One way it to open up the [File Browser](/blog/2021-08-10-open-in-importer-and-copy-path-options-in-filebrowser/) and copy the path of the data into a CREATE TABLE or go via the Create table wizard which will do all the work for you.

Note that small data files don't even need to go via the cloud storage and can be [directly uploaded via drag & drop](blog/2021-07-26-create-sql-tables-on-the-fly-with-zero-clicks/) in the Web interface or [Importer API](https://docs.gethue.com/developer/api/rest/#file-import). Something that will be demoed next so stay tuned!

![Importer direct upload steps gif](https://cdn.gethue.com/uploads/2021/07/drag_and_drop_importer2.gif)

**Proper security**

It is also a good timing. The [file listing](https://docs.gethue.com/user/browsing/#data) (for [HDFS](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html), the Hadoop file system) has be present since day one. Later on AWS S3, Azure Storage, Google Cloud Storage have been added but were lacking fine grained security (i.e. all the users were using the same credentials).

This is not true anymore as recently the shared signed URL technology of these cloud storages is being leveraged under the hood to have each user perform file operations under their own distinct credentials. This allows true self service instead of restricting data uploads to only admin. Users can upload their own files and analyze them without contacting anybody else. Another bottleneck removed!

If interested in more technical details, read more about [AWS Shared Signature](/blog/2021-06-30-how-to-use-azure-storage-rest-api-with-shared-access-sginature-sas-tokens/) or [Azure Signed URLs](/blog/2021-04-23-s3-file-access-without-any-credentials-and-signed-urls/).

![Open the Create Table Wizard or copy a file URI](https://cdn-images-1.medium.com/max/2000/1*hqkJ2QR1SdLf4Af0Z4ABHw.png)
<br>
*Open the Create Table Wizard or copy a file URI*


Now there is no excuses to not be data driven via self service ;)

Using GCP or other storage? Let us know!

And In case you missed it, the coolest API is the [Execute a SQL query](https://docs.gethue.com/developer/api/rest/#execute-a-query), play with it!


Onwards!

Romain from the Hue Team
