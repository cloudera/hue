---
title: How to create a real Hadoop cluster in 10 minutes?
author: admin
type: post
date: 2014-04-17T12:37:45+00:00
url: /hadoop-tutorial-how-to-create-a-real-hadoop-cluster-in-10-minutes/
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
slide_template:
  - default
categories:
---

<p dir="ltr">
  <em>Last update <span style="color: #ff0000;">February 2nd 2017</span></em>
</p>

<p id="docs-internal-guid-5f9e143b-5ded-3474-e3cb-2476b7aedb36" dir="ltr">
  We recently launched <a href="http://demo.gethue.com">demo.gethue.com</a>, which in <a href="https://gethue.com/hadoop-tutorial-live-demo-hadoop-directly-from-your-browser">one click</a> lets you try out a real Hadoop cluster. We followed the exact same process as building a production ready cluster. Here is how we did it.
</p>

<p dir="ltr">
  Before getting started, you will need to get your hands on some machines. Hadoop runs on commodity hardware, so any regular computer with a major linux distribution will work. To follow along with the demo, take a look at Amazon Cloud Computing service. If you already have a server or two, or don't mind running Hadoop on your local linux box, then go straight to Machine Setup!
</p>

<p dir="ltr">
  Here is a video demoing how easy it is to boot your own cluster and start crunching data!
</p>

{{< youtube MJYeiPt3r_0 >}}

<h1 dir="ltr">
  Machine setup
</h1>

<p dir="ltr">
  We picked <a href="http://aws.amazon.com/">AWS</a> and started 4 <a href="https://aws.amazon.com/ec2/pricing/">r3.large</a> instances with Ubuntu 14.04 and <span style="color: #ff0000;">100 GB storage</span> (instead of the default 8GB). If you need less performance, one xlarge instance is enough or you can install less services on an even smaller instance.
</p>

<p dir="ltr">
  Then configure the security group like below. We allow everything between the instances (the first row, don’t forget it on multi machine cluster!) and open up Cloudera Manager and Hue ports to the outside.
</p>

<div dir="ltr">
  <table>
    <colgroup> <col width="163" /> <col width="103" /> <col width="89" /> <col width="269" /></colgroup> <tr>
      <td>
        <p dir="ltr">
          All TCP
        </p>
      </td>

      <td>
        <p dir="ltr">
          TCP
        </p>
      </td>

      <td>
        <p dir="ltr">
          0 - 65535
        </p>
      </td>

      <td>
        <p dir="ltr">
          sg-e2db7777 (hue-demo)
        </p>
      </td>
    </tr>

    <tr>
      <td>
        <p dir="ltr">
          SSH
        </p>
      </td>

      <td>
        <p dir="ltr">
          TCP
        </p>
      </td>

      <td>
        <p dir="ltr">
          22
        </p>
      </td>

      <td>
        <p dir="ltr">
          0.0.0.0/0
        </p>
      </td>
    </tr>

    <tr>
      <td>
        <p dir="ltr">
          Custom TCP Rule
        </p>
      </td>

      <td>
        <p dir="ltr">
          TCP
        </p>
      </td>

      <td>
        <p dir="ltr">
          7180
        </p>
      </td>

      <td>
        <p dir="ltr">
          0.0.0.0/0
        </p>
      </td>
    </tr>

    <tr>
      <td>
        <p dir="ltr">
          Custom TCP Rule
        </p>
      </td>

      <td>
        <p dir="ltr">
          TCP
        </p>
      </td>

      <td>
        <p dir="ltr">
          8888
        </p>
      </td>

      <td>
        <p dir="ltr">
          0.0.0.0/0
        </p>
      </td>
    </tr>

    <tr>
      <td>
        <p dir="ltr">
          Custom ICMP Rule
        </p>
      </td>

      <td>
        <p dir="ltr">
          Echo Reply
        </p>
      </td>

      <td>
        <p dir="ltr">
          N/A
        </p>
      </td>

      <td>
        <p dir="ltr">
          0.0.0.0/0
        </p>
      </td>
    </tr>

  </table>
</div>

<h1 dir="ltr">
  Hadoop Setup
</h1>

<p dir="ltr">
  Now that we have some machines, let’s install Hadoop. We used Cloudera Manager as it installs everything for us and just followed this <a href="http://www.cloudera.com/content/cloudera-content/cloudera-docs/CM5/latest/Cloudera-Manager-Installation-Guide/cm5ig_install_on_ec2.html#cmig_topic_8_1_unique_1">guide</a>. Moreover, post install monitoring and configuration are also greatly simplified with the administration interface.
</p>

<p dir="ltr">
  Start first by connecting to one of the machine:
</p>

<!--email_off-->

<pre><code class="bash">ssh -i ~/demo.pem ubuntu@ec2-11-222-333-444.compute-1.amazonaws.com</code></pre>

&nbsp;

<p dir="ltr">
  Retrieve and start Cloudera Manager:
</p>

<pre><code class="bash">wget http://archive.cloudera.com/cm5/installer/latest/cloudera-manager-installer.bin

chmod +x cloudera-manager-installer.bin

sudo ./cloudera-manager-installer.bin

</code></pre>

<p dir="ltr">
  After, login with the default credentials admin/admin (note: you might need to wait 5 minutes before http://ec2-54-178-21-60.compute-1.amazonaws.com:7180/ becomes available).
</p>

<p dir="ltr">
  Then enter all the Public DNS IP (e.g. ec2-11-222-333-444.compute-1.amazonaws.com) of your machines in the Install Wizard and click go! Et voila, Cloudera Manager will setup your whole cluster automatically for you!
</p>

<p dir="ltr">
  Assign a dynamic IP to your machine with Hue and then go to IP:8888 and start <a href="https://gethue.com/tutorials/">playing</a> with your fully functional Hadoop cluster and its <a href="https://gethue.com/tutorial-live-demo-of-search-on-hadoop/">examples</a>!
</p>

<p dir="ltr">
  As usual feel free to comment on the<a href="http://groups.google.com/a/cloudera.org/group/hue-user"> hue-user</a> list or<a href="https://twitter.com/gethue"> @gethue</a>!
</p>

<p dir="ltr">
  <strong>Note</strong>
</p>

<p dir="ltr">
  If you are getting a "Bad Request (400)" error, you will need to enter in the hue.ini or CM safety valve:
</p>

<pre><code class="bash">[desktop]

allowed_hosts=*</code></pre>

<p dir="ltr">
  <strong>Note</strong>
</p>

<p dir="ltr">
  If you have several machines, it is recommended to move the services around in order to homogenize the memory/CPU usage. For example split HBase, Oozie, Hive and Solr on different hosts.
</p>

<p dir="ltr">
  <strong>Note</strong>
</p>

<p dir="ltr">
  When running some MapReduce jobs with YARN, if all the jobs deadlock in ACCEPTED or READY states, you might be hitting this YARN bug.
</p>

<p dir="ltr">
  The solution is to use a low number like 2 or 3 for the Dynamic resource manager pools. Go to CM → Clusters → Other → Dynamic Resource Pools → Configuration → Edit → YARN and set ‘Max Running Apps’ to 2.
</p>

<p style="text-align: center;">
  <a href="https://cdn.gethue.com/uploads/2014/04/cm-yarn-pool.png"><img class=" wp-image-1143 aligncenter" src="https://cdn.gethue.com/uploads/2014/04/cm-yarn-pool.png" /></a>
</p>

<p style="text-align: left;">
  You can also try to decrease yarn.nodemanager.resource.memory-mb and the task memory and bump the memory of yarn.app.mapreduce.am.resource.mb.
</p>
