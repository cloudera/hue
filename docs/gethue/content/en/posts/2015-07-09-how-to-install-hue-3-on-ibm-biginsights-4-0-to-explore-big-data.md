---
title: How to install Hue 3 on IBM BigInsights 4.0 to explore Big Data
author: admin
type: post
date: 2015-07-09T17:42:06+00:00
url: /how-to-install-hue-3-on-ibm-biginsights-4-0-to-explore-big-data/
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
sf_remove_promo_bar:
  - 1
categories:

---
<div class="pn-copy">
  <p>
    <em>This post was originally published on the IBM blog <a href="https://developer.ibm.com/hadoop/blog/2015/06/02/deploying-hue-on-ibm-biginsights/">HUE on IBM BigInsights 4.0 to explore Big Data</a> by <span class="pn-meta-author"><a title="Posts by Vinayak Agrawal" href="https://keeponlearning1.wordpress.com/" rel="author">Vinayak Agrawal</a></span> / <a href="https://twitter.com/@vinayak_agr">@vinayak_agr</a>.</em>
  </p>
</div>

For Hue 3.9 and BigInsights 4.1 have a look to <https://developer.ibm.com/hadoop/blog/2015/10/27/how-to-install-hue-3-9-on-top-of-biginsights-4-1/>

&nbsp;

<div class="pn-copy">
  <h2>
    Task
  </h2>

  <p>
    This article will walk you through the steps required to deploy/setup HUE on IBM BigInsights version 4.0 and above.
  </p>

  <h2>
    Introduction
  </h2>

  <p>
    HUE or Hadoop User Experience is a Web interface for analyzing data with Apache Hadoop. With Big Data, you need a tool to navigate through your data, query your data and even search it. This is all tied up together in one place with HUE.
  </p>

  <h2>
    Pre-requisites
  </h2>

  <p>
    To deploy HUE on BigInsights, you need an up and running BigInsights Version 4.x cluster. For the purpose of this article, we can use BigInsights V4 Quickstart edition that is available on IBM website for free. You can download the Quick Start Edition <a title="here" href="http://www-01.ibm.com/software/data/infosphere/biginsights/quick-start/">here</a>. It is assumed that your OS is redhat 6.x. If not, you will need to change the package installation commands as per your linux distro.
  </p>

  <h2>
    Install Dependencies
  </h2>

  <p>
    A couple of dependencies are required by HUE to run. So lets start with downloading the required packages. Launch terminal and download the required packages.
  </p>

  <table bgcolor="#F5F5F5">
    <tr>
      <td>
        [root@rvm /]# yum install ant<br /> [root@rvm /]# yum install python-devel.x86_64<br /> [root@rvm /]# yum install krb5-devel.x86_64<br /> [root@rvm /]# yum install krb5-libs.x86_64<br /> [root@rvm /]# yum install libxml2.x86_64<br /> [root@rvm /]# yum install python-lxml.x86_64<br /> [root@rvm /]# yum install libxslt-devel.x86_64<br /> [root@rvm /]# yum install mysql-devel.x86_64<br /> [root@rvm /]# yum install openssl-devel.x86_64<br /> [root@rvm /]# yum install libgsasl-devel.x86_64<br /> [root@rvm /]# yum install sqlite-devel.x86_64<br /> [root@rvm /]# yum install openldap-devel.x86_64
      </td>
    </tr>
  </table>

  <h2>
    Download HUE
  </h2>

  <p>
    We will download the latest version of HUE as of today which is version 3.7.1 and extract it. In the terminal, run the following commands:
  </p>

  <table bgcolor="#F5F5F5">
    <tr>
      <td>
        [root@rvm /]# wget https://cdn.gethue.com/downloads/releases/3.7.1/hue-3.7.1.tgz<br /> [root@rvm /]# sudo echo “JAVA_HOME=\”/usr/lib/jvm/java-7-openjdk-1.7.0.75.x86_64/jre\”” >> /etc/environment<br /> [root@rvm /]# tar zxvf hue-3.7.1.tgz
      </td>
    </tr>
  </table>

  <h2>
    Add User And Group for HUE
  </h2>

  <table bgcolor="#F5F5F5">
    <tr>
      <td>
        [root@rvm /]# groupadd hue<br /> [root@rvm /]# useradd hue -g hue<br /> [root@rvm /]# passwd hue
      </td>
    </tr>
  </table>

  <p>
    Now give ownership of extracted hue folder to user hue by executing the following command.
  </p>

  <table bgcolor="#F5F5F5">
    <tr>
      <td>
        [root@rvm /]# chown hue:hue hue-3.7.1
      </td>
    </tr>
  </table>

  <p>
    You will also need to add user hue to sudoers file as a sudoer.
  </p>

  <h2>
    Install HUE
  </h2>

  <p>
    1. As user hue, start the installation as shown below.<br /> <code>[root@rvm /]#sudo make install</code><br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/make_install.png"><img class="alignnone size-full wp-image-4995" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/make_install.png" /></a><br /> 2. By default, HUE installs to ‘/usr/local/hue’ in your Management node’s local filesystem as shown below. Make user hue, the owner of /usr/local/hue folder by executing<br /> <code>sudo chown –R hue:hue /usr/local/hue</code>
  </p>

  <h2>
    Setting up hadoop properties for HUE
  </h2>

  <h3>
    1. Configure properties in core-site.xml
  </h3>

  <p>
    i. Enable Webhdfs<br /> Go to Ambari, select HDFS on the left side and then select config as shown.<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hdfs_config.png"><img class="alignnone size-full wp-image-4967" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hdfs_config.png" /></a><br /> Then scroll down and make sure webdfs is check marked as shown below:<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/web_hdfs.png"><img class="alignnone size-full wp-image-4978" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/web_hdfs.png" /></a><br /> ii. Add the following 2 properties under custom core-site.xml with value “*” as shown below:<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/core_site.png"><img class="alignnone size-full wp-image-4965" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/core_site.png" /></a>
  </p>

  <h3>
    2. Configure properties in oozie-site.xml
  </h3>

  <p>
    Just like above, now select oozie on the left side in Ambari and then select config.<br /> i. Add two properties in oozie for HUE as shown below.<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/zookeeper_config.png"><img class="alignnone size-full wp-image-5001" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/zookeeper_config.png" /></a>
  </p>

  <h3>
    3. Configure properties in webcat-site.xml
  </h3>

  <p>
    Now navigate to Hive on left side in Ambari and then select config.<br /> i. Keep scrolling down until you see webcat-site and add two properties in webhcat configuration for HUE as shown below:<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/webhcat_site.png"><img class="alignnone size-full wp-image-4979" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/webhcat_site.png" /></a>
  </p>

  <h2>
    Configure HUE.ini file to point to your Hadoop cluster
  </h2>

  <p>
    – Go to /usr/local/hue/desktop/conf<br /> – Start editing hue.ini using any editor(like vim) after making a backup file.<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_ini.png"><img class="alignnone size-full wp-image-4974" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_ini.png" /></a>
  </p>

  <p>
    Note: In this article, the cluster is small-one node, therefore services like Hive Server, Hive Metastore, HBase Master, Zookeepers etc are deployed on one node itself. In case of bigger cluster, put the correct node information for the respective services that we are editing next. The screenshots below are just example to help you configure.
  </p>

  <h3>
    i. Edit Hdfs and webhdfs parameters to point to your cluster. Make the changes as shown. Don’t forget to uncomment these parameters after adding values.
  </h3>

  <p>
    <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini.png"><img class="alignnone size-full wp-image-4968" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini.png" /></a>
  </p>

  <h3>
    ii. Configure YARN parameters and don’t forget to uncomment these parameters as shown:
  </h3>

  <p>
    <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini_2.png"><img class="alignnone size-full wp-image-4969" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini_2.png" /></a>
  </p>

  <h3>
    iii. Configure Oozie, hive and hbase as show below. Don’t forget to uncomment the parameters.<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini_3.png"><img class="alignnone size-full wp-image-4970" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini_3.png" /></a><br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini_4.png"><img class="alignnone size-full wp-image-4971" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini_4.png" /></a><a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini_5.png"><img class="alignnone size-full wp-image-4973" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/hue_config_ini_5.png" /></a>
  </h3>

  <p>
    – Save all the changes.
  </p>

  <h2>
    Start HUE
  </h2>

  <p>
    – As hue user, go to /usr/local/hue/build/env folder and start HUE by executing <code>./supervisor</code> as shown below<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/start_hue.png"><img class="alignnone size-full wp-image-4977" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/start_hue.png" /></a>
  </p>

  <h2>
    Testing HUE
  </h2>

  <p>
    In your browser, go to<br /> <code>yourserver:8888/filebrowser</code><br /> When prompted for userid/password, use user hue and its password that you created earlier to login.<br /> You should see the following screen making sure that HUE is working properly.<br /> <a href="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/demo_start.png"><img class="alignnone size-full wp-image-4966" src="http://developer.ibm.com/hadoop/wp-content/uploads/sites/28/2015/06/demo_start.png" /></a>
  </p>

  <h2>
    Conclusion
  </h2>

  <p>
    In this article we have successfully deployed HUE 3.7.1 on top of BigInsights V4.0 using Quick Start edition.This setup would allow an end user to browse/copy/delete HDFS files, fire queries to hive/hbase and even create a dashboard for data analysis. This interface can also be used as a front end for your enterprise search application powered by Solr.
  </p>
</div>
