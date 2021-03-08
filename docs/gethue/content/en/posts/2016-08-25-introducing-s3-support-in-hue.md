---
title: Introducing Amazon S3 Support in Hue
author: admin
type: post
date: 2016-08-25T08:15:20+00:00
url: /introducing-s3-support-in-hue/
sf_no_breadcrumbs:
  - 1
sf_page_title_style:
  - standard
sf_page_title:
  - 1
sf_detail_type:
  - none
sf_thumbnail_type:
  - none
sf_thumbnail_link_type:
  - link_to_post
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
sf_remove_promo_bar:
  - 1
categories:
---

<p class="p1">
  We’re very excited to officially introduce <a href="https://aws.amazon.com/s3/">Amazon S3</a> (Amazon Simple Storage Service) integration in Hue with <a href="https://gethue.com/hue-3-11-with-its-new-s3-browser-and-sql-autocomplete-is-out/">Hue’s 3.11 release</a>. Hue can be setup to read and write to a configured S3 account, and users can directly query from and save data to S3 without any intermediate moving/copying to HDFS.
</p>

{{< youtube P-7XH78aT9s >}}

## S3 Configuration in Hue {.p3}

<p class="p1">
  Hue’s filebrowser can now allow users to explore, manage, and upload data in an S3 account, in addition to HDFS.
</p>

<p class="p1">
  In order to add an S3 account to Hue, you’ll need to configure Hue with valid S3 credentials, including the access key ID and secret access key: <a href="http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html"><span class="s1">http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html</span></a>
</p>

<p class="p1">
  These keys can securely stored in a script that outputs the actual access key and secret key to stdout to be read by Hue (this is similar to how <a href="https://gethue.com/storing-passwords-in-script-rather-than-hue-ini-files/">Hue reads password scripts</a>). In order to use script files, add the following section to your <code>hue.ini</code> configuration file:
</p>

<pre><code class="bash">[aws]

[[aws_accounts]]

[[[default]]]

access_key_id_script=/path/to/access_key_script

secret_access_key_script= /path/to/secret_key_script

allow_environment_credentials=false

region=us-east-1

</code></pre>

<p class="p1">
  Alternatively (but not recommended for production or secure environments), you can set the <code>access_key_id</code> and <code>secret_access_key</code> values to the plain-text values of your keys:
</p>

<pre><code class="bash">[aws]

[[aws_accounts]]

[[[default]]]

access_key_id=s3accesskeyid

secret_access_key=s3secretaccesskey

allow_environment_credentials=false

region=us-east-1

</code></pre>

<p class="p1">
  The region should be set to the AWS region corresponding to the S3 account. By default, this region will be set to ‘us-east-1’.
</p>

### Integrating Hadoop with S3 {.p3}

<p class="p1">
  In addition to configuring Hue with your S3 credentials, Hadoop will also need to be configured with the S3 authentication credentials in order to read from and save to S3. This can be done by setting the following properties in your <code>core-site.xml</code> file:
</p>

<pre><code class="xml">

<property>

<name>fs.s3a.awsAccessKeyId</name>

<value>AWS access key ID</value>

</property/>

<property>

<name>fs.s3a.awsSecretAccessKey</name>

<value>AWS secret key</value>

</property/>

</code></pre>

<p class="p4">
  <span class="s2">For more information see <a href="http://wiki.apache.org/hadoop/AmazonS3"><span class="s1">http://wiki.apache.org/hadoop/AmazonS3</span></a></span>
</p>

<p class="p1">
  With Hue and Hadoop configured, we can verify that Hue is able to successfully connect to your S3 account by restarting Hue and checking the configuration page. You should not see any errors related to AWS, and you should notice an additional dropdown option in the Filebrowser menu from the main navigation:
</p>

[<img src="https://cdn.gethue.com/uploads/2016/08/s3_configuration-1024x559.png"  />][1]

## {.p3}

## Exploring S3 in Hue’s Filebrowser {.p3}

<p class="p1">
  Once Hue is successfully configured to connect to S3, we can view all accessible buckets within the account by clicking on the S3 root.
</p>

<p class="p1">
  Users can also create new buckets or delete existing buckets from this view.
</p>

#### NOTE: Unique Bucket Names

❗️ S3 bucket names must be unique _across all regions_. Hue will raise an error if you attempt to create or rename a bucket with a reserved name.

<p class="p1">
  However, in most cases users will be working directly with keys within a bucket. From the buckets-view, users can click on a bucket to expand its contents. From here, we can view the existing keys (both directories and files) and create, rename, move, copy, or delete existing directories and files. Additionally, we can directly upload files to S3
</p>

<img data-gifffer="https://cdn.gethue.com/uploads/2016/08/s3_filebrowser.gif"  />

## Create Hive Tables Directly From S3 {.p3}

Hue's Metastore Import Data Wizard can create external Hive tables directly from data directories in S3. This allows S3 data to be queried via [SQL from Hive or Impala][2], without moving or copying the data into HDFS or the Hive Warehouse.

To create an external Hive table from S3, navigate to the Metastore app, select the desired database and then click the "Create a new table from a file" icon in the upper right.

Enter the table name and optional description, and in the "Input File or Directory" filepicker, select the S3A filesystem and navigate to the parent directory containing the desired data files and click the "Select this folder" button. The "Load Data" dropdown should automatically select the "Create External Table" option which indicates that this table will directly reference an external data directory.

Choose your input files' delimiter and column definition options and finally click "Create Table" when you're ready to create the Hive table. Once created, you should see the newly created table details in the Metastore.

<img data-gifffer="https://cdn.gethue.com/uploads/2016/08/s3_metastore.gif"  />

## Save Query Results to S3 {.p3}

Now that we have created external Hive tables created from our S3 data, we can jump into either the Hive or Impala editor and start querying the data directly from S3 seamlessly. These queries can join tables and objects that are backed either by S3, HDFS, or both. Query results can then easily be saved back to S3.

<img data-gifffer="https://cdn.gethue.com/uploads/2016/08/s3_query_and_save.gif"  />

#### TIP: Impala and S3

???? For further advanced use-cases with Impala and S3, read: [Analytics and BI on Amazon S3 with Apache Impala (Incubating)][3].

&nbsp;

## Using Ceph

New end points have been added in <https://issues.cloudera.org/browse/HUE-5420>

## What's Next {.p3}

Hue 3.11's seamless support for S3 as an additional filesystem is just the beginning of a long-term roadmap for greater data flexibility and portability in the Cloud. Stay tuned for future enhancements like cross file transfers, execution and schedule of queries directly from the object store... that will provide a tighter integration between HDFS, S3, and additional filesystems.

As always, if you have any questions, feel free to comment here or on the [hue-user list][4] or [@gethue][5]!

[1]: https://cdn.gethue.com/uploads/2016/08/s3_configuration.png
[2]: https://gethue.com/sql-editor/
[3]: http://blog.cloudera.com/blog/2016/08/analytics-and-bi-on-amazon-s3-with-apache-impala-incubating/
[4]: http://groups.google.com/a/cloudera.org/group/hue-user
[5]: https://twitter.com/gethue
