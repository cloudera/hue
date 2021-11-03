---
title: Azure Storage sharing by leveraging SAS tokens so that your users don’t need credentials
author: Hue Team
type: post
date: 2021-06-30T00:00:00+00:00
url: /blog/2021-06-30-how-to-use-azure-storage-rest-api-with-shared-access-sginature-sas-tokens
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

---

Example tutorial on how to use the the Azure storage REST API with Shared Access Signatures.

We previously covered a similar methodology for [providing access to S3 data without giving out actual credentials](https://medium.com/data-querying/provide-your-users-proper-s3-file-access-without-giving-them-any-credential-keys-272675631875) via some S3 signed URLs. This time we will explore it on Azure, the Cloud data platform from Microsoft.
> “Trying to” keep things simple for the end users

The main use case for us is still to provide a platform agnostic [File Browser](https://docs.gethue.com/user/browsing/#data) for the Hue users to allow self service data querying. They are free to upload files, see files… and create SQL tables on top of them without having to bug IT or know anything about Azure. IT can also implement a less locking strategy with multi-cloud as the end users are not interacting directly with the platforms.

![Hue’s File Browser listing an ADLS Gen2 directory](https://cdn-images-1.medium.com/max/2332/0*Dv3Yd8uGXfpJn3Ml.png)*Hue’s File Browser listing an ADLS Gen2 directory*

The [Azure SAS documentation](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview) is pretty extensive, so we won’t repeat here all its possibilities and instead focus on the simplest examples that can be buried under all the information, namely:
> How to list objects and download a file

Azure has multiple storages, in particular Hue is integrated with ADLS Gen1 and Gen2, but the demo is with the “Blob” containers as those are ready to go.

After the demo you will have the big picture of what Hue is doing under the cover to provide this unified File Browser, and will know how to query the Azure REST API with a SAS token.

## What is a SAS?

[Long story short](https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview#sas-token), a Shared Access Signatures (SAS) is a token to append to the URI (i.e. path) of your storage objects.

e.g. Let’s share the container named “test” with READ and LIST permissions for 1 day to anybody.

Resource (i.e. the container URI):

    https://gethue.blob.core.windows.net/test

Resource with SAS:

    https://gethue.blob.core.windows.net/test?sp=rl&st=2021-06-30T19:41:46Z&se=2021-07-01T19:41:46Z&sv=2020-02-10&sr=c&sig=NuHOuuzdQN7VRM%2FOpOeqBlawRCA845IY05h9eu1Yte4%3D

A bit cryptic at first, here are the meaning of these new parameters:

* sp: the access permission (e.g. READ, WRITE, LIST…)
* st: start time of the link (e.g. 2021–06–30T19:41:46Z)
* se: expiration time of the link (e.g. 2021–07–01T19:41:46Z)
* sv: version of SAS we use (e.g. 2020–02–10)
* sr: the resource type (e.g. “c” for “container”)
* sig: the hash of above and the URI (e.g. NuHOuuzdQN7VRM%2FOpOeqBlawRCA845IY05h9eu1Yte4%3D)

## Getting the SAS

The simplest way is to navigate in the Storage Explorer, select the object you want to share and manually create a Shared Access Signature.

Obviously in the real world this would be done via an Authorization Provider like Ranger RAZ or more sophisticated rules/groups.

Let’s get our two signed URLs:

![Navigating to the resource we want to share](https://cdn-images-1.medium.com/max/2000/1*dd2d-niNu2y1y73H5GKM-g.png)

*Navigating to the resource we want to share*

![And generating a temporary link with the according permissions](https://cdn-images-1.medium.com/max/2000/1*fz3E3vq4GcB-l5j1RHja6Q.png)

*And generating a temporary link with the according permissions*

### Listing

Here is the URI for listing the test folder:

    https://gethue.blob.core.windows.net/test?sp=rl&st=2021-06-30T19:41:46Z&se=2021-07-01T19:41:46Z&sv=2020-02-10&sr=c&sig=NuHOuuzdQN7VRM%2FOpOeqBlawRCA845IY05h9eu1Yte4%3D

### Downloading

Here the URI for accessing the weblogs data file:

    https://gethue.blob.core.windows.net/test/query-hive-weblogs.csv?sp=rl&st=2021-06-30T19:40:15Z&se=2021-07-01T19:40:15Z&sv=2020-02-10&sr=b&sig=EeNV5VG41mw8TxO2yEEWdAJzNQR5Cl2ZUtWqKEuvasc%3D

## Making the REST API requests

Now that we have the URI of the container with a built-in authorization, we inject the [LIST command](https://docs.microsoft.com/en-us/rest/api/storageservices/list-blobs) **comp=list&restype=container** into the URL and issue the REST request to list its content.

In a shell Terminal or in your Browser:

    curl -X GET "https://gethue.blob.core.windows.net/test?comp=list&restype=container&sp=rl&st=2021-06-30T19:41:46Z&se=2021-07-01T19:41:46Z&sv=2020-02-10&sr=c&sig=NuHOuuzdQN7VRM%2FOpOeqBlawRCA845IY05h9eu1Yte4%3D"

And we get back the directory listing in XML:

    <?xml version="1.0" encoding="UTF-8"?>
    <EnumerationResults ServiceEndpoint="https://gethue.blob.core.windows.net/" ContainerName="test">
       <Blobs>
          <Blob>
             <Name>data/query-impala-16.csv</Name>
             <Properties>
                <Creation-Time>Wed, 30 Jun 2021 17:44:24 GMT</Creation-Time>
                <Last-Modified>Wed, 30 Jun 2021 17:44:24 GMT</Last-Modified>
                <Etag>0x8D93BEEB30C99F6</Etag>
                <Content-Length>20</Content-Length>
                <Content-Type>text/csv</Content-Type>
                <Content-Encoding />
                <Content-Language />
                <Content-CRC64 />
                <Content-MD5>0UQq07gv7BluVP8fx/N7tg==</Content-MD5>
                <Cache-Control />
                <Content-Disposition />
                <BlobType>BlockBlob</BlobType>
                <AccessTier>Hot</AccessTier>
                <AccessTierInferred>true</AccessTierInferred>
                <LeaseStatus>unlocked</LeaseStatus>
                <LeaseState>available</LeaseState>
                <ServerEncrypted>true</ServerEncrypted>
             </Properties>
             <OrMetadata />
          </Blob>
          <Blob>
             <Name>query-hive-weblogs.csv</Name>
             <Properties>
                <Creation-Time>Mon, 10 May 2021 22:18:05 GMT</Creation-Time>
                <Last-Modified>Mon, 10 May 2021 22:18:05 GMT</Last-Modified>
                <Etag>0x8D914017BE8F64E</Etag>
                <Content-Length>53779</Content-Length>
                <Content-Type>text/csv</Content-Type>
                <Content-Encoding />
                <Content-Language />
                <Content-CRC64 />
                <Content-MD5>om+hCV1t9ERuZOnskNRreA==</Content-MD5>
                <Cache-Control />
                <Content-Disposition />
                <BlobType>BlockBlob</BlobType>
                <AccessTier>Hot</AccessTier>
                <AccessTierInferred>true</AccessTierInferred>
                <LeaseStatus>unlocked</LeaseStatus>
                <LeaseState>available</LeaseState>
                <ServerEncrypted>true</ServerEncrypted>
             </Properties>
             <OrMetadata />
          </Blob>
       </Blobs>
       <NextMarker />
    </EnumerationResults>

For downloading the file, directly doing a GET works:

    curl -X GET "https://gethue.blob.core.windows.net/test/query-hive-weblogs.csv?sp=rl&st=2021-06-30T19:40:15Z&se=2021-07-01T19:40:15Z&sv=2020-02-10&sr=b&sig=EeNV5VG41mw8TxO2yEEWdAJzNQR5Cl2ZUtWqKEuvasc%3D"

And the file content is retrieved:

    web_logs._version_,web_logs.app,web_logs.bytes,web_logs.city,web_logs.client_ip,web_logs.code,web_logs.country_code,web_logs.country_code3,web_logs.country_name,web_logs.device_family,web_logs.extension,web_logs.latitude,web_logs.longitude,web_logs.method,web_logs.os_family,web_logs.os_major,web_logs.protocol,web_logs.record,web_logs.referer,web_logs.region_code,web_logs.request,web_logs.subapp,web_logs.time,web_logs.url,web_logs.user_agent,web_logs.user_agent_family,web_logs.user_agent_major,web_logs.id,web_logs.date
    1480895575515725824,metastore,1041,Singapore,128.199.234.236,200,SG,SGP,Singapore,Other,,1.2931,103.8558,GET,Other,,HTTP/1.1,,-,00,GET /metastore/table/default/sample_07 HTTP/1.1,table,2014-05-04T06:35:49Z,/metastore/table/default/sample_07,Mozilla/5.0 (compatible; phpservermon/3.0.1; +[http://www.phpservermonitor.org),Other,,8836e6ce-9a21-449f-a372-9e57641389b3,2015-11-18](http://www.phpservermonitor.org),Other,,8836e6ce-9a21-449f-a372-9e57641389b3,2015-11-18)
    14
    ...
    ...
    ...

Et voila!

Stay tuned for more examples on how to use the [Hue API](https://docs.gethue.com/developer/api/rest/#file-browsing) and its [SQL components](https://docs.gethue.com/developer/components/scratchpad/).

Onwards!

Romain from the Hue Team
