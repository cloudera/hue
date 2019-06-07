---
title: "Files and Stores"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 4
---

## HDFS

Hue supports one HDFS cluster. That cluster should be defined under the `[[[default]]]` sub-section.

    [hadoop]

      # Configuration for HDFS NameNode
      # ------------------------------------------------------------------------
      [[hdfs_clusters]]

        [[[default]]]
          fs_defaultfs=hdfs://hdfs-name-node.com:8020
          webhdfs_url=http://hdfs-name-node.com:20101/webhdfs/v1

HA is supported by pointing to the HttpFs service instead of the NameNode.


Make sure the HDFS service has in it `hdfs-site.xml`:

    <property>
    <name>dfs.webhdfs.enable</name>
    <value>true</value>
    </property>

Configure Hue as a proxy user for all other users and groups, meaning it may submit a request on behalf of any other user:

WebHDFS: Add to core-site.xml:

        <!-- Hue WebHDFS proxy user setting -->
        <property>
        <name>hadoop.proxyuser.hue.hosts</name>
        <value>*</value>
        </property>
        <property>
        <name>hadoop.proxyuser.hue.groups</name>
        <value>*</value>
        </property>

HttpFS: Verify that /etc/hadoop-httpfs/conf/httpfs-site.xml has the following configuration:

        <!-- Hue HttpFS proxy user setting -->
        <property>
        <name>httpfs.proxyuser.hue.hosts</name>
        <value>*</value>
        </property>
        <property>
        <name>httpfs.proxyuser.hue.groups</name>
        <value>*</value>
        </property>

If the configuration is not present, add it to /etc/hadoop-httpfs/conf/httpfs-site.xml and restart the HttpFS daemon.
Verify that core-site.xml has the following configuration:

        <property>
        <name>hadoop.proxyuser.httpfs.hosts</name>
        <value>*</value>
        </property>
        <property>
        <name>hadoop.proxyuser.httpfs.groups</name>
        <value>*</value>
        </property>

If the configuration is not present, add it to /etc/hadoop/conf/core-site.xml and restart Hadoop.
## S3

Hue's filebrowser can now allow users to explore, manage, and upload data in an S3 account, in addition to HDFS.

Read more about it in the [S3 User Documentation]({{% param baseURL %}}user/browsers#s3).

In order to add an S3 account to Hue, you'll need to configure Hue with valid S3 credentials, including the access key ID and secret access key: [AWSCredentials](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html)

These keys can securely stored in a script that outputs the actual access key and secret key to stdout to be read by Hue (this is similar to how Hue reads password scripts). In order to use script files, add the following section to your hue.ini configuration file:


    [aws]
    [[aws_accounts]]
    [[[default]]]
    access_key_id_script=/path/to/access_key_script
    secret_access_key_script= /path/to/secret_key_script
    allow_environment_credentials=false
    region=us-east-1


Alternatively (but not recommended for production or secure environments), you can set the access_key_id and secret_access_key values to the plain-text values of your keys:

    [aws]
    [[aws_accounts]]
    [[[default]]]
    access_key_id=s3accesskeyid
    secret_access_key=s3secretaccesskey
    allow_environment_credentials=false
    region=us-east-1

The region should be set to the AWS region corresponding to the S3 account. By default, this region will be set to 'us-east-1'.


**Using Ceph**
New end points have been added in [HUE-5420](https://issues.cloudera.org/browse/HUE-5420)


## ADLS

Hue's file browser can now allow users to explore, manage, and upload data in an ADLS, in addition to HDFS and S3.

Read more about it in the [ADLS User Documentation]({{% param baseURL %}}user/browsers#adls).

In order to add an ADLS account to Hue, you'll need to configure Hue with valid ADLS credentials, including the client ID, client secret and tenant ID.
These keys can securely stored in a script that outputs the actual access key and secret key to stdout to be read by Hue (this is similar to how Hue reads password scripts). In order to use script files, add the following section to your hue.ini configuration file:

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

Alternatively (but not recommended for production or secure environments), you can set the client_secret value in plain-text:

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


## HBase

Specify the comma-separated list of HBase Thrift servers for clusters in the format of "(name|host:port)":

    [hbase]
    hbase_clusters=(Cluster|localhost:9090)

HBase Impersonation:

Enable impersonation for the Thrift server by adding the following properties to hbase-site.xml on each Thrift gateway:

    <property>
      <name>hbase.regionserver.thrift.http</name>
      <value>true</value>
    </property>
    <property>
      <name>hbase.thrift.support.proxyuser</name>
      <value>true/value>
    </property>

Note: If you use framed transport, you cannot use doAs impersonation, because SASL does not work with Thrift framed transport.

doAs Impersonation provides a flexible way to use the same client to impersonate multiple principals. doAs is supported only in Thrift 1.
Enable doAs support by adding the following properties to hbase-site.xml on each Thrift gateway:

    <property>
      <name>hbase.regionserver.thrift.http</name>
      <value>true</value>
    </property>
    <property>
      <name>hbase.thrift.support.proxyuser</name>
      <value>true/value>
    </property>
