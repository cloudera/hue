---
title: Browsing ADLS data, querying it with SQL and exporting the results back in Hue 4.2
author: admin
type: post
date: 2017-11-20T22:21:34+00:00
url: /browsing-adls-data-querying-it-with-sql-and-exporting-the-results-back-in-hue-4-2/
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
sf_sidebar_config:
  - left-sidebar
sf_left_sidebar:
  - Sidebar-2
sf_right_sidebar:
  - Sidebar-1
sf_caption_position:
  - caption-right
categories:
  - Version 4
---

<p class="p1">
  We’re happy to present <a href="https://azure.microsoft.com/en-us/services/data-lake-store/">Microsoft Azure Data Lake Store</a> (ADLS) integration in Hue with Hue 4.2 release. Similarly to the <a href="https://gethue.com/introducing-s3-support-in-hue/">S3 integration</a>, Hue can be setup to read and write to a configured ADLS, and users can directly query from and save data to ADLS without any intermediate moving / copying to HDFS.
</p>

<p class="p1">
  For a detailed video walkthrough of file manipulation using ADLS in Hue, have a look:
</p>

{{< youtube JKm2bv1CvGQ >}}

<p class="p1">
  In case you missed the one for S3, here is the <a href="https://gethue.com/introducing-s3-support-in-hue/">link to the post</a>.
</p>

&nbsp;

## Exploring ADLS in Hue’s file browser {.p3}

<p class="p1">
  Once Hue is successfully configured to connect to ADLS, we can view all accessible folders within the account by clicking on the ADLS root. From here, we can view the existing keys (both directories and files) and create, rename, move, copy, or delete existing directories and files. Additionally, we can directly upload files to ADLS.
</p>

<img src="https://cdn.gethue.com/uploads/2016/08/image2.png"/>

## Create Hive Tables Directly From ADLS {.p3}

<p class="p1">
  Hue’s <a href="https://gethue.com/browsing-hive-tables-data-and-metadata-is-getting-faster-and-prettier/">table browser </a>import wizard can create external Hive tables directly from files in ADLS. This allows ADLS data to be queried via <a href="https://gethue.com/sql-editor/">SQL from Hive or Impala</a>, without moving or copying the data into HDFS or the Hive Warehouse. To create an external Hive table from ADLS, navigate to the table browser, select the desired database and then click the plus icon in the upper right. Select a file using the file picker and browse to a file on ADLS.
</p>

<img src="https://cdn.gethue.com/uploads/2017/11/image4-1.png"/>

<p class="p1">
  Choose your input files’ delimiter and press next. Keep unchecked “Store in Default location” if you want the file to stay intact on ADLS, update the column definition options and finally click “Submit” when you’re ready to create the Hive table. Once created, you should see the newly created table details in the table browser.
</p>

## Save Query Results to ADLS {.p3}

<p class="p1">
  Now that we have created external Hive tables created from our ADLS data, we can jump into either the Hive or Impala editor and start querying the data directly from ADLS seamlessly. These queries can join tables and objects that are backed either by ADLS, HDFS, or both. Query results can then easily be saved back to ADLS.
</p>

<img src="https://cdn.gethue.com/uploads/2017/11/image1-1.png"/>

&nbsp;

## ADLS Configuration in Hue {.p3}

<p class="p1">
  Hue’s file browser can now allow users to explore, manage, and upload data in an ADLS, in addition to HDFS and S3.
</p>

<p class="p1">
  In order to add an ADLS account to Hue, you’ll need to configure Hue with valid <a href="https://docs.microsoft.com/en-us/azure/data-lake-store/data-lake-store-service-to-service-authenticate-rest-api">ADLS credentials</a>, including the client ID, client secret and tenant ID.<br /> These keys can securely stored in a script that outputs the actual access key and secret key to stdout to be read by Hue (this is similar to how <a href="https://gethue.com/storing-passwords-in-script-rather-than-hue-ini-files/">Hue reads password scripts</a>). In order to use script files, add the following section to your hue.ini configuration file:
</p>

<pre><code class="bash">

[adls]

[[azure_accounts]]

[[[default]]]

client_id_script=/path/to/client_id_script.sh

client_secret_script=/path/to/client_secret_script.sh

tenant_id_script=/path/to/tenant_id_script.sh

[[adls_clusters]]

[[[default]]]

fs_defaultfs=adl://<account_name>.azuredatalakestore.net

webhdfs_url=https://<account_name>.azuredatalakestore.net

</code></pre>

<p class="p1">
  Alternatively (but not recommended for production or secure environments), you can set the client_secret value in plain-text:
</p>

<pre><code class="bash">

[adls]

[[azure_accounts]]

[[[default]]]

client_id_script=/path/to/client_id_script.sh

client_secret_script=/path/to/client_secret_script.sh

tenant_id_script=/path/to/tenant_id_script.sh

[[adls_clusters]]

[[[default]]]

fs_defaultfs=adl://<account_name>.azuredatalakestore.net

webhdfs_url=https://<account_name>.azuredatalakestore.net

</code></pre>

<p class="p1">
  Alternatively (but not recommended for production or secure environments), you can set the client_secret value in plain-text:
</p>

<pre><code class="bash">

[adls]

[[azure_account]]

[[[default]]]

client_id=adlsclientid

client_secret=adlsclientsecret

tenant_id=adlstenantid

[[adls_clusters]]

[[[default]]]

fs_defaultfs=adl://<account_name>.azuredatalakestore.net

webhdfs_url=https://<account_name>.azuredatalakestore.net

</code></pre>

## Integrating Hadoop with ADLS {.p3}

<p class="p1">
  In addition to configuring Hue with your ADLS credentials, Hadoop will also need to be configured with the ADLS authentication credentials in order to read from and save to ADLS. This can be done by setting the following properties in your <a href="https://hadoop.apache.org/docs/current/hadoop-azure-datalake/index.html#Using_Client_Keys">core-site.xml</a> file:
</p>

<pre><code class="xml">

<property>

<name>fs.adl.oauth2.access.token.provider.type</name>

<value>ClientCredential</value>

</property/>

<property>

<name>fs.adl.oauth2.refresh.url</name>

<value>https://login.microsoftonline.com/<tenant_id>/oauth2/token</value>

</property/>

<property>

<name>fs.adl.oauth2.client.id</name>

<value>adlsclientid</value>

</property/>

<property>

<name>fs.adl.oauth2.credential</name>

<value>adlsclientsecret</value>

</property/>

</code></pre>

<p class="p1">
  With Hue and Hadoop configured, we can verify that Hue is able to successfully connect to ADLS by restarting Hue and checking the configuration page. You should not see any errors related to ADLS, and you should notice an additional option in the menu from the main navigation.
</p>

<p class="p1">
  For performance numbers on ADLS, please read: <a href="http://blog.cloudera.com/blog/2017/10/a-look-at-adls-performance-throughput-and-scalability/">A look at ADLS Performance</a>.<br /> As always, if you have any questions, feel free to comment here or on the <a href="http://groups.google.com/a/cloudera.org/group/hue-user">hue-user list</a> or <a href="https://twitter.com/gethue">@gethue</a>!
</p>
