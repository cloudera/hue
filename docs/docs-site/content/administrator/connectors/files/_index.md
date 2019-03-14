---
title: "Files and Object Store"
date: 2019-03-13T18:28:09-07:00
draft: false
weight: 2
---

### HDFS

Hue supports one HDFS cluster. That cluster should be defined
under the `[[[default]]]` sub-section.

    fs_defaultfs::
      This is the equivalence of `fs.defaultFS` (aka `fs.default.name`) in
      Hadoop configuration.

    webhdfs_url::
      You can also set this to be the HttpFS url. The default value is the HTTP
      port on the NameNode.

    hadoop_conf_dir::
      This is the configuration directory of the HDFS, typically
      `/etc/hadoop/conf`.

### S3

Hue's filebrowser can now allow users to explore, manage, and upload data in an S3 account, in addition to HDFS.

Read more about it in the [S3 User Documentation](../user-guide/user-guide.html#s3).

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


### ADLS

Hue's file browser can now allow users to explore, manage, and upload data in an ADLS, in addition to HDFS and S3.

Read more about it in the [ADLS User Documentation](../user-guide/user-guide.html#adls).

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


## YARN Cluster

Hue supports one or two Yarn clusters (two for HA). These clusters should be defined
under the `[[[default]]]` and `[[[ha]]]` sub-sections.

    resourcemanager_host:
      The host running the ResourceManager.

    resourcemanager_port:
      The port for the ResourceManager REST service.

    logical_name:
      NameNode logical name.

    submit_to:
      To enable the section, set to True.

## Oozie

In the `[liboozie]` section of the configuration file, you should
specify:

    oozie_url:
      The URL of the Oozie service. It is the same as the `OOZIE_URL`
      environment variable for Oozie.


## Solr

In the `[search]` section of the configuration file, you should
specify:

    solr_url:
      The URL of the Solr service.


## HBase

In the `[hbase]` section of the configuration file, you should
specify:

    hbase_clusters:
      Comma-separated list of HBase Thrift servers for clusters in the format of "(name|host:port)".

