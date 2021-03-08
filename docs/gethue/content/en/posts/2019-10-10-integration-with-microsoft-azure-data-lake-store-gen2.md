---
title: Integration with Microsoft Azure Data Lake Store Gen2
author: Hue Team
type: post
date: 2019-10-10T19:09:23+00:00
url: /integration-with-microsoft-azure-data-lake-store-gen2/
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
# - Version 4.6

---
Hue continues its progress to make the Cloud platforms easier to use.

We’re happy to preset compatibility with Microsoft Azure Data Lake Store Gen2 (ADLS Gen2). Hue 4.6 release brings the ability to read and write from a configured ADLS Gen2. Almost like ADLS, users can save data to ADLS Gen2 without copying or moving to HDFS. The difference between ADLS Gen1 and Gen2 is that ADLS Gen2 does not rely on the HDFS driver. Instead, it provides its own driver to manage its own filesystems and

In case you missed the one for ADLS (also known as ADLS Gen 1), here is the [link to the post][1].

## Exploring ADLS in Hue’s file browser

Once Hue is configured to connect to ADLS Gen2, we can view all accessible folders within the account by clicking on ABFS (Azure Blob Filesystem). The reason why it is listed as ABFS is because ADLS Gen2 branches off from hadoop and uses its own driver called ABFS. Through ABFS, we view filesystems, directories and files along with creating, renaming, moving, copying, or deleting existing directories and files. We also allowed files to uploaded to ADLS Gen2. (In other words, it can do the basics of file system management. Though, files can not be uploaded to the root directory)

<a href="https://cdn.gethue.com/uploads/2019/10/adls2_browse.png"><img src="https://cdn.gethue.com/uploads/2019/10/adls2_browse.png" /></a>

## Create Hive Tables directly from ADLS Gen2

As mentioned in ADLS Blog post, Hue’s import wizard can create external Hive tables directly from files in ADLS Gen2 to be queried via SQL from Hive. Impala needs some more testing. To create an external Hive table from ADLS, navigate to table browser, select the desired database and then select the New icon. Select a file using the file picker and browse to a file on ADLS.

<a href="https://cdn.gethue.com/uploads/2019/10/adls2_upload.png"><img src="https://cdn.gethue.com/uploads/2019/10/adls2_upload.png" /></a>

## Save Query Results to ADLS Gen2

If you want to save your tables to ADLS Gen2, you can do so. Select ABFS as your filesystem and export the table. The table data should be saved to ABFS. Table data cannot be saved in the root directory.

<a href="https://cdn.gethue.com/uploads/2019/10/adls2_export_to.png"><img src="https://cdn.gethue.com/uploads/2019/10/adls2_export_to.png" /></a>

## ADLS Gen2 Configuration

Hue’s file browser allows users to explore, manage, and upload data in both versions of ADLS.

As a result of adding ADLS Gen 2, the [configuration][5] for ADLS will be different. Nonetheless, the same client id, client secret and tenant ID can be used for ADLS Gen2. The same scripts can also be used to output the actual access key and secret key to stdout to be read by Hue. To use script files, add the following section to your hue.ini configuration file:

<pre><code class="ini">[azure]
  [[azure_accounts]]
    [[[default]]]
    client_id_script=/path/to/client_id_script.sh
    client_secret_script=/path/to/client_secret_script.sh
    tenant_id_script=/path/to/tenant_id_script.sh&lt;/pre&gt;
  [[abfs_clusters]]
    [[[default]]]
    fs_defaultfs=abfs://&lt;filesystem_name&gt;@&lt;account_name&gt;.dfs.core.windows.net
    webhdfs_url=https://&lt;account_name&gt;.dfs.core.windows.net
</code></pre>

If ADLS configuration exists just add the following to the end of “[azure]”:

<pre><code class="ini">[[abfs_clusters]]
  [[[default]]]
  fs_defaultfs=abfs://&lt;filesystem_name&gt;@&lt;account_name&gt;.dfs.core.windows.net
  webhdfs_url=https://&lt;account_name&gt;.dfs.core.windows.net
</code></pre>

## Integrating Hadoop with ADLS Gen2

If ADLS Gen 1 is configured to Hadoop, then ADLS Gen2 should be able to use the same authentication credentials in order to read from and save to ADLS. Assuming that ADLS Gen1 credentials does not work or that the user does not have it, users can set the following properties in the core-site.xml file.

<pre><code class="xml">&lt;property&gt;
  &lt;name&gt;fs.azure.account.auth.type&lt;/name&gt;
  &lt;value&gt;OAuth&lt;/value&gt;
&lt;/property&gt;

&lt;property&gt;
  &lt;name&gt;fs.azure.account.oauth.provider.type&lt;/name&gt;
  &lt;value&gt;org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider&lt;/value&gt;
&lt;/property&gt;

&lt;property&gt;
  &lt;name&gt;fs.azure.account.oauth2.client.id&lt;/name&gt;
  &lt;value&gt;azureclientid&lt;/value&gt;
&lt;/property&gt;

&lt;property&gt;
  &lt;name&gt;fs.azure.account.oauth2.client.secret&lt;/name&gt;
  &lt;value&gt;azureclientsecret&lt;/value&gt;
&lt;/property&gt;

&lt;property&gt;
  &lt;name&gt;fs.azure.account.oauth2.client.endpoint&lt;/name&gt;
  &lt;value&gt;https://login.microsoftonline.com/${azure_tenant_id}/oauth2/token&lt;/value&gt;
&lt;/property&gt;
</code></pre>

Hue integrates with HDFS, S3, ADLS v1/v2 and soon Google Cloud Storage. So go [query][6] data in these [storages][7]!

&nbsp;

<div>
  <div>
    Any feedback or question? Feel free to comment here or on the <a href="https://discourse.gethue.com/">Forum</a> or <a href="https://twitter.com/gethue">@gethue</a> and <a href="https://docs.gethue.com/quickstart/">quick start</a> SQL querying!
  </div>

  <p>
    &nbsp;
  </p>
</div>

<div>
</div>

 [1]: https://gethue.com/browsing-adls-data-querying-it-with-sql-and-exporting-the-results-back-in-hue-4-2/
 [2]: https://cdn.gethue.com/uploads/2019/10/adls2_browse.png
 [3]: https://cdn.gethue.com/uploads/2019/10/adls2_upload.png
 [4]: https://cdn.gethue.com/uploads/2019/10/adls2_export_to.png
 [5]: https://docs.gethue.com/administrator/configuration/files/#adls
 [6]: https://docs.gethue.com/quickstart/
 [7]: https://docs.gethue.com/administrator/configuration/files/
