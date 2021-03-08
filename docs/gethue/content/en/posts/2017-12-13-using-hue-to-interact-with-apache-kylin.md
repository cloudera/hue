---
title: Using Hue to interact with Apache Kylin in your cluster or on AWS
author: admin
type: post
date: 2017-12-13T06:34:52+00:00
url: /using-hue-to-interact-with-apache-kylin/
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
categories:
  - Version 4

---
_This is a blog post from the community by Joanna He and Yongjie Zhao._

### <a class="md-header-anchor " name="header-n2"></a>What is Apache Kylin

[Apache Kylin][1] is a leading open-source online analytical processing (OLAP) engine that’s built for interactive analytics for Big Data. It provides an ANSI-SQL interface and multi-dimensional OLAP for massive datasets. It supports consuming data in batch and streaming and offers sub-second query latency on petabyte-scale dataset. It seamlessly integrates with BI tools via ODBC driver, JDBC driver, and REST API.

### <a class="md-header-anchor " name="header-n6"></a>What is Hue

Hue is a very easy-to-use SQL editor that allows you to query Hadoop-based service using a user-friendly web-based interface. Hue makes access big data on Hadoop easier for Analysts as SQL is the most familiar language analysts could use.

In this post, we will demonstrate how you can connect Hue to Apache Kylin and get quick insight from huge volume data in seconds.

### <a class="md-header-anchor " name="header-n11"></a>Build Docker Image of Hue with Apache Kylin

#### <a class="md-header-anchor " name="header-n12"></a>Prepare hue image

Use docker to pull the latest hue.

<pre><code class="bash">docker pull gethue/hue:latest</code></pre>

#### <a class="md-header-anchor " name="header-n16"></a>Prepare kylin jdbc driver

Download Apache Kylin installer package

<pre><code class="bash">wget -c http://mirror.bit.edu.cn/apache/kylin/apache-kylin-2.2.0/apache-kylin-2.2.0-bin-hbase1x.tar.gz</code></pre>

Unzip package

<pre><code class="bash">tar -zxvf apache-kylin-2.2.0-bin-hbase1x.tar.gz</code></pre>

cp Kylin jdbc driver

<pre><code class="bash">cp apache-kylin-2.2.0-bin/lib/kylin-jdbc-2.2.0.jar .

hue$ ls

apache-kylin-2.2.0-bin apache-kylin-2.2.0-bin-hbase1x.tar.gz kylin-jdbc-2.2.0.jar

</code></pre>

#### <a class="md-header-anchor " name="header-n27"></a>Copy hub config file to host machine

Copy the file from docker

<pre><code class="bash">docker run -it -d -name hue_tmp gethue/hue /bin/bash

cp hue_tmp:/hue/desktop/conf/pseudo-distributed.ini .

docker stop hue_tmp; docker rm hue_tmp

</code></pre>

Now you should have the `pseudo-distributed.ini` in your current directory.

#### <a class="md-header-anchor " name="header-n35"></a>Configure pseudo-distributed.ini with Kylin connection

<pre><code class="bash">vim pseudo-distributed.ini</code></pre>

copy below kylin section in the file

<pre><code class="bash">dbproxy_extra_classpath=/hue/kylin-jdbc-2.2.0.jar

[[[kylin]]]

name=kylin JDBC

interface=jdbc

options='{"url": "jdbc:kylin://<your_host>:<port>/<project_name>","driver": "org.apache.kylin.jdbc.Driver", "user": "<username>", "password": "<password>"}'

</code></pre>

For example, add below configuration section in the file

<pre><code class="bash">dbproxy_extra_classpath=/hue/kylin-jdbc-2.2.0.jar

\# One entry for each type of snippet.

[[interpreters]]

\# Define the name and how to connect and execute the language.

[[[kylin]]]

name=kylin JDBC

interface=jdbc

options='{"url": "jdbc:kylin://localhost:7070/learn_kylin","driver": "org.apache.kylin.jdbc.Driver", "user": "ADMIN", "password": "KYLIN"}'

[[[hive]]]

\# The name of the snippet.

name=Hive

\# The backend connection to use to communicate with the server.

interface=hiveserver2

</code></pre>

#### <a class="md-header-anchor " name="header-n43"></a>Edit Dockerfile

<pre><code class="bash">touch Dockerfile

vim Dockerfile

</code></pre>

paste below script in Dockerfile

<pre><code class="bash">FROM gethue/hue:latest

COPY ./kylin-jdbc-2.2.0.jar /hue/kylin-jdbc-2.2.0.jar

COPY ./pseudo-distributed.ini /hue/desktop/conf/pseudo-distributed.ini

EXPOSE 8888

</code></pre>

This configuration will copy the kylin jdbc jar and pseudo-distributed.ini into the hue in Docker. And expose port 8888 in Docker.

#### <a class="md-header-anchor " name="header-n50"></a>Build and start docker container

<pre><code class="bash">docker build -t hue-demo -f Dockerfile .

docker run -itd -p 8888:8888 -name hue hue-demo

</code></pre>

Hue is now up and running in your localhost:8888

<img src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.34.20-PM.png"/>

&nbsp;

You can now query kylin from Hue.

[<img class="aligncenter wp-image-5133" src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.01.53-PM.png"/>][2]

[<img class="aligncenter wp-image-5132" src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.02.13-PM.png"/>][3]

&nbsp;

&nbsp;

### <a class="md-header-anchor " name="header-n62"></a>Deploy Hue with Apache Kylin on AWS

Below content will guide you how to deploy Hue with Apache Kylin on AWS EMR.

#### <a class="md-header-anchor " name="header-n65"></a>Install Apache Kylin on AWS EMR

You may refer to [this document][4] to install Apache Kylin on AWS EMR.

#### <a class="md-header-anchor " name="header-n68"></a>Install Hue with Apache Kylin configured on AWS EMR

After you installed Apache Kylin on AWS EMR, you can now deploy Hue on AWS EMR with Kylin configured easily using our bootstrap file.

<ol start="">
  <li>
    Download the <em>download.sh</em> file from <a href="https://github.com/Kyligence/emr-hue-kylin">this github</a> to a S3 bucket;
  </li>
</ol>

<ol start="2">
  <li>
    In <em>configurations.json</em>, replace Apache Kylin host, port, project, credential with you own, then run below script in AWS CLI to create a EMR cluster.Make sure you escape options setting as shown below.
  </li>
</ol>

<pre><code class="bash">[

{

"Classification": "hue-ini",

"Properties": {},

"Configurations": [

{

"Classification": "notebook",

"Properties": {

"dbproxy_extra_classpath": "/opt/kylin_jdbc/kylin-jdbc-2.2.0.jar"

},

"Configurations": [

{

"Classification": "interpreters",

"Properties": {},

"Configurations": [

{

"Classification": "kylin",

"Properties": {

"name": "kylin JDBC",

"interface": "jdbc",

"options": "{\"url\": \"jdbc:kylin://<host>:<port>/<project>\", \"driver\": \"org.apache.kylin.jdbc.Driver\", \"user\": \"<username>\", \"password\": \"<password>\"}"

},

"Configurations": []

}

]

}

]

}

]

}

]

</code></pre>

<pre><code class="bash">aws emr create-cluster -name "HUE Cluster" -release-label emr-5.10.0 \

-ec2-attributes KeyName=<keypair_name>,InstanceProfile=EMR_EC2_DefaultRole,SubnetId=<subnet_id> \

-service-role EMR_DefaultRole \

-applications Name=Hive Name=Hue Name=Pig \

-emrfs Consistent=true,RetryCount=5,RetryPeriod=30 \

-instance-count 1 -instance-type m3.xlarge \

-configurations file://configurations.json \

-bootstrap-action Path="s3://<your_bucket>/download.sh"

</code></pre>

<ol start="3">
  <li>
    After the cluster is in "Waiting" status, open web browser at: http://:8888 , you will see the cluster with hue is ready.
  </li>
</ol>

&nbsp;

[<img class="aligncenter wp-image-5130" src="https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-12-05-at-6.15.36-PM.png"/>][5]

### <a class="md-header-anchor " name="header-n89"></a>Conclusion

We have demonstrate how you can easily configure Hue to query Apache Kylin. Hue is a great open source SQL editor for your interative analytics on Kylin. Both Hue and Apache Kylin can be deployed either on premises or in the cloud so you can utilize this combination anywhere.

The whole document and related files are on this repo for your reference:

<a href="https://github.com/Kyligence/emr-hue-kylin" target="_blank" rel="noopener noreferrer">https://github.com/Kyligence/emr-hue-kylin</a>

 [1]: http://kylin.apache.org/
 [2]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.01.53-PM.png
 [3]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-11-15-at-3.02.13-PM.png
 [4]: http://kylin.apache.org/docs21/install/kylin_aws_emr.html
 [5]: https://cdn.gethue.com/uploads/2017/12/Screen-Shot-2017-12-05-at-6.15.36-PM.png
