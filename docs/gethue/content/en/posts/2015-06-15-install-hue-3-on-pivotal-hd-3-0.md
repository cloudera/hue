---
title: Install Hue 3 on Pivotal HD 3.0
author: admin
type: post
date: 2015-06-15T16:08:03+00:00
url: /install-hue-3-on-pivotal-hd-3-0/
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
This post was originally published on [Install Hue 3 with Pivotal HD 3.0][1] by [Christian Tzolov][2] of [@Pivotal][3].

<div class="article-content entry-content">
  <div dir="ltr">
    <p>
      <i>Latest </i><i>Hadoop distributions from </i><i>Pivotal (<a href="http://pivotal.io/big-data/pivotal-hd">PHD3.0</a>) and Hortonworks (HDP2.2) come with support for <a href="http://pivotalhd.docs.pivotal.io/docs/install-manually.html#ref-acf369d8-ef80-4030-a296-45fa22f9b723">Hue 2.6</a>. Unfortunately Hue 2.6 is quite old and does not provide any RDBMS UI. The RDBMS view is useful for Pivotal as it allows friendly web interface for running adhoc HAWQ SQL queries. This feature is demoed here:</i>
    </p>
  </div>

  <p>
    &nbsp;
  </p>

  <div dir="ltr">
  </div>

  <div>
    <iframe class="YOUTUBE-iframe-video" src="https://www.youtube.com/embed/MfCoXtvUtvw?feature=player_embedded&wmode=opaque" width="320" height="266" frameborder="0" allowfullscreen="allowfullscreen" data-thumbnail-src="https://i.ytimg.com/vi/MfCoXtvUtvw/0.jpg"></iframe>
  </div>

  <div>
  </div>

  <p>
    &nbsp;
  </p>

  <div>
    <p>
      Below I will show how to install latest <a href="https://gethue.com/hue-3-7-with-sentry-app-and-new-search-widgets-are-out/">Hue 3.7.1</a> on PHD3.0 and how to use it with HAWQ.
    </p>

    <p>
      <strong>Disclaimer</strong>: This is an experimental work. It is not thoughtfully tested and will not be supported in the future. The article expresses author’s own opinion.
    </p>

    <p>
      &nbsp;
    </p>

    <p>
      <strong>Installing Hue 3.7.1 on Pivotal HD 3.0</strong>
    </p>
  </div>

  <div dir="ltr">
    The following Hue 3.7.1 rpms are built with <a href="http://bigtop.apache.org/">Apache BigTop</a>. You can download compressed bundle with all Hue rpms: <a href="https://www.dropbox.com/s/v7o5mxybvuhy4l4/hue-all-3.7.1-1.el6.x86_64.zip">hue-all-3.7.1-1.el6.x86_64.zip</a>. It contains the following packages:
  </div>

  <div dir="ltr">
  </div>

  <div dir="ltr">
    <table>
      <colgroup> <col width="319" /> <col width="305" /></colgroup> <tr>
        <td>
          <div dir="ltr">
            hue-common
          </div>
        </td>

        <td>
          <div dir="ltr">
            hue-spark - requires additional services
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hue-server
          </div>
        </td>

        <td>
          <div dir="ltr">
            hue-sqoop
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hue-rdbms
          </div>
        </td>

        <td>
          <div dir="ltr">
            hue-doc
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hue-pig
          </div>
        </td>

        <td>
          <div dir="ltr">
            hue-search
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hue-zookeeper
          </div>
        </td>

        <td>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hue-beeswax
          </div>
        </td>

        <td>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hue-hbase
          </div>
        </td>

        <td>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hue-impala - required due to issue <a href="https://issues.cloudera.org/browse/HUE-2492">HUE-2492 </a>
          </div>
        </td>

        <td>
        </td>
      </tr>
    </table>
  </div>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Uncompress hue-all.zip bundle on the Ambari node and install the packages as explained below. For some packages the dependency check needs to be disabled (e.g.use rpm -i with  -nodeps option).
  </div>

  <p>
    <b><br /> </b>
  </p>

  <p>
    <pre><code class="bash"># External dependencies<br /> sudo yum -y install cyrus-sasl-gssapi cyrus-sasl-plain libxml2 libxslt zlib python sqlite python-psycopg2<br /> # Hue packages<br /> sudo yum -y install ./hue-common-3.7.1-1.el6.x86_64.rpm<br /> sudo yum -y install ./hue-server-3.7.1-1.el6.x86_64.rpm<br /> sudo yum -y install ./hue-rdbms-3.7.1-1.el6.x86_64.rpm<br /> sudo yum -y install ./hue-zookeeper-3.7.1-1.el6.x86_64.rpm<br /> sudo yum -y install ./hue-pig-3.7.1-1.el6.x86_64.rpm<br /> sudo yum -y install ./hue-hbase-3.7.1-1.el6.x86_64.rpm<br /> sudo yum -y install ./hue-beeswax-3.7.1-1.el6.x86_64.rpm<br /> (sudo rpm -i -nodeps hue-beeswax-3.7.0+cdh5.3.3+180-1.cdh5.3.3.p0.8.el6.x86_64.rpm)<br /> sudo yum -y install ./hue-sqoop-3.7.1-1.el6.x86_64.rpm<br /> sudo yum -y install ./hue-impala-3.7.1-1.el6.x86_64.rpm<br /> </code></pre>
  </p>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Start Hue:
  </div>

  <p>
    <pre><code class="bash">sudo /etc/init.d/hue start</code></pre>
  </p>

  <div dir="ltr">
    Open the Ambari UI on port https://<Ambari-Host>:8888 (<a href="https://ambari.localadmin:8888/">https://ambari.localadmin:8888</a>):
  </div>

  <p>
    <b><br /> <img src="https://lh5.googleusercontent.com/YeDOuxhiQ_Z2-k2pZe2xgxVCxixaa_fthHRPNFfZ3ZgnvnEUjpnO3pZVyrTP25bjrt1ZkxbbXHGJCjqce_2F71Fr8vKkbxbCRLwgxCi9Nqztzt8C-hltXHocat6oad9aL6lNqBE" alt="Screen Shot 2015-04-13 at 3.02.30 PM.png" width="272px;" height="234px;" /></b>
  </p>

  <div dir="ltr">
    The first login will ask for an username and a password.  Make sure to set the username to hue! Pick a password of your choice.
  </div>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Next configure Hue. Edit the /etc/hue/conf/hue.ini as explained in <a href="#appendixa">Appendix A</a>  and apply the RDBMS table view workaround as explained in <a href="#appendixb">Appendix B</a>.
  </div>

  <div dir="ltr">
    <br class="kix-line-break" />Restart Hue:
  </div>

  <div dir="ltr">
    <p>
      <pre><code class="bash">sudo /etc/init.d/hue restart</code></pre>
    </p>
  </div>

  <p>
    <b><br /> </b>
  </p>

  <h2 dir="ltr">
    Enable HAWQ remote access
  </h2>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Enable the remote access from the Ambari to HAWQ. On the HAWQ master (phd3) open the master’s pg_hba.conf file:
  </div>

  <div dir="ltr">
    <p>
      <pre><code class="bash">sudo vi /data/hawq/master/gpseg-1/pg_hba.conf</code></pre>
    </p>
  </div>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    and add the following line. Replace the IP with the address of you the Ambari node.
  </div>

  <div dir="ltr">
    <p>
      <pre><code class="bash">host    all     gpadmin <Add your AmbariHost IP here>/32        trust</code></pre>
    </p>
  </div>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Restart the HAWQ Service (using Ambari):
  </div>

  <div dir="ltr">
    <img src="https://lh5.googleusercontent.com/L7imqvIKKpDdtPDspewQwrx0Pi1tMdBp7yaOaIt7DKaU2knv_WS8iKxfIZoEi713C1NsZmIZZwApguGR9yFcEDgHXlosG75bBSBKckgnHuA703qXoBIn07ZBcfaYMYm-ZoD_hYI" alt="Ambari-Restart-HAWQ-Service.png" width="432px;" height="243px;" />
  </div>

  <p>
    <b><br /> </b>
  </p>

  <h2 dir="ltr">
    Start HBase Thrift Server
  </h2>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Hue communicates with the HBase service via Thrift. To start the server on the HBase master node (phd2.localdomain) run:
  </div>

  <p>
    <pre><code class="bash">sudo nohup /usr/bin/hbase thrift start &</code></pre>
  </p>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Hadoop Proxy configuration
  </div>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    To allow HUE to impersonate various Hadoop services you have to enable the following hadoop proxies. In Ambari from the Dashboard view select the HDFS service and then the ‘Config’ tab. Type ‘proxy’ in the search field and press enter. Change or add the properties to match those values:
  </div>

  <p>
    <b><br /> <img src="https://lh3.googleusercontent.com/MAXdf4RXF7jPm77DBho2oQ7880Aqadtg26gPu0UJcyWZalCw8eOnQCCzzwCWRhhUUaMjXgknB11o0X7ju35PdynVAdhC6QmPGxeb7MpufZkgRdQUPIrS1LO9Xxvoq35FQM4PeBQ" alt="Screen Shot 2015-04-14 at 12.27.36 AM.png" width="334px;" height="240px;" /></b>
  </p>

  <div dir="ltr">
    <table>
      <colgroup> <col width="196" /> <col width="66" /></colgroup> <tr>
        <td>
          <div dir="ltr">
            Property name
          </div>
        </td>

        <td>
          <div dir="ltr">
            value
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hadoop.proxyuser.hcat.groups
          </div>
        </td>

        <td>
          <div dir="ltr">
            *
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hadoop.proxyuser.hcat.hosts
          </div>
        </td>

        <td>
          <div dir="ltr">
            *
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hadoop.proxyuser.hive.groups
          </div>
        </td>

        <td>
          <div dir="ltr">
            *
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hadoop.proxyuser.hive.hosts
          </div>
        </td>

        <td>
          <div dir="ltr">
            *
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hadoop.proxyuser.hue.groups
          </div>
        </td>

        <td>
          <div dir="ltr">
            *
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hadoop.proxyuser.hue.hosts
          </div>
        </td>

        <td>
          <div dir="ltr">
            *
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hadoop.proxyuser.oozie.groups
          </div>
        </td>

        <td>
          <div dir="ltr">
            *
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            hadoop.proxyuser.oozie.hosts
          </div>
        </td>

        <td>
          <div dir="ltr">
            *
          </div>
        </td>
      </tr>
    </table>
  </div>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Save the modified configuration and restart the affected services (HDFS, YARN and MapReduce). Tip: follow the restart suggestions.
  </div>
</div>

<div class="article-content entry-content">
</div>

&nbsp;

<div id="appendixa" class="article-content entry-content">
  <strong>Appendix A: HUE Configuration</strong><br /> Hue configuration is in /etc/hue/conf/hue.ini file. Run ‘/etc/init.d/hue restart’ after configuration modification.<br /> <b><br /> </b></p>

  <div dir="ltr">
    The following service deployment topology is being used for this particular hue.ini configuration:
  </div>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    <table>
      <colgroup> </colgroup> <tr>
        <td>
          <div dir="ltr">
            ambari.localadmin
          </div>
        </td>

        <td>
          <div dir="ltr">
            Ambari, Hue, Nagios, Ganglia
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            phd1.localadmin
          </div>
        </td>

        <td>
          <div dir="ltr">
            HAWQ SMaster, NameNode, HiveServer2, Hive Metastore, ResourceManager, WebHCat Server, DataNode, HAWQ Segment, RegionServer, NodeManager, PXF
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            phd2.localadmin
          </div>
        </td>

        <td>
          <div dir="ltr">
            App Timeline Server, History Server, HBase Master, Oozie Server, SNameNode, Zookeeper Server, DataNode, HAWQ Segment, RegionServer, NodeManager, PXF
          </div>
        </td>
      </tr>

      <tr>
        <td>
          <div dir="ltr">
            phd3.localadmin
          </div>
        </td>

        <td>
          <div dir="ltr">
            HAWQ Master, DataNode, HAWQ Segment, RegionServer, NodeManager, PXF
          </div>
        </td>
      </tr>
    </table>
  </div>

  <p>
    <b><br /> </b>
  </p>

  <div dir="ltr">
    Only the modification from the the default hue configuration properties are listed below. Configuration is aligned with PHD3.0 cluster with the following topology:
  </div>

  <p>
    &nbsp;
  </p>

  <p>
    <pre><code class="bash"><br /> ###########################################################################<br /> # General configuration for core Desktop features (authentication, etc)<br /> ###########################################################################<br /> [desktop]<br />  # Set this to a random string, the longer the better.<br />  # This is used for secure hashing in the session store.<br />  secret_key=bozanovakozagoza<br />  # Time zone name<br />  time_zone=Europe/Amsterdam<br />  # Comma separated list of apps to not load at server startup.<br />  # e.g.: pig,zookeeper<br />  app_blacklist=impala,indexer<br /> ###########################################################################<br /> # Settings for the RDBMS application<br /> ###########################################################################<br /> [librdbms]<br />  # The RDBMS app can have any number of databases configured in the databases<br />  # section. A database is known by its section name<br />  # (IE sqlite, mysql, psql, and oracle in the list below).<br />  [[databases]]<br />    # mysql, oracle, or postgresql configuration.<br />    [[[postgresql]]]<br />      # Name to show in the UI.<br />      nice_name=&quot;HAWQ&quot;<br />      name=postgres<br />      engine=postgresql<br />      host=phd3.localdomain<br />      port=5432<br />      user=gpadmin<br />      password=<br /> ###########################################################################<br /> # Settings to configure your Hadoop cluster.<br /> ###########################################################################<br /> [hadoop]<br />  # Configuration for HDFS NameNode<br />  # ------------------------<br />  [[hdfs_clusters]]<br />    [[[default]]]<br />      # Enter the filesystem uri<br />      fs_defaultfs=hdfs://phd1.localdomain:8020<br />      # Use WebHdfs/HttpFs as the communication mechanism.<br />      # Domain should be the NameNode or HttpFs host.<br />      # Default port is 14000 for HttpFs.<br />      webhdfs_url=http://phd1.localdomain:50070/webhdfs/v1<br />  # Configuration for YARN (MR2)<br />  # ------------------------<br />  [[yarn_clusters]]<br />    [[[default]]]<br />      # Enter the host on which you are running the ResourceManager<br />      resourcemanager_host=phd1.localdomain<br />      # The port where the ResourceManager IPC listens on<br />      resourcemanager_port=8030<br />      # URL of the ResourceManager API<br />      resourcemanager_api_url=http://phd1.localdomain:8088<br />      # URL of the HistoryServer API<br />      history_server_api_url=http://phd2.localdomain:19888<br /> ###########################################################################<br /> # Settings to configure liboozie<br /> ###########################################################################<br /> [liboozie]<br />  # The URL where the Oozie service runs on. This is required in order for<br />  # users to submit jobs. Empty value disables the config check.<br />  oozie_url=http://phd2.localdomain:11000/oozie<br /> ###########################################################################<br /> # Settings to configure Beeswax with Hive<br /> ###########################################################################<br /> [beeswax]<br />  # Host where HiveServer2 is running.<br />  # If Kerberos security is enabled, use fully-qualified domain name (FQDN).<br />  hive_server_host=phd1.localdomain<br />  # Port where HiveServer2 Thrift server runs on.<br />  hive_server_port=10000<br />  # Choose whether Hue uses the GetLog() thrift call to retrieve Hive logs.<br />  # If false, Hue will use the FetchResults() thrift call instead.<br />  use_get_log_api=false<br />  # Set a LIMIT clause when browsing a partitioned table.<br />  # A positive value will be set as the LIMIT. If 0 or negative, do not set any limit.<br />  browse_partitioned_table_limit=250<br />  # A limit to the number of rows that can be downloaded from a query.<br />  # A value of -1 means there will be no limit.<br />  # A maximum of 65,000 is applied to XLS downloads.<br />  download_row_limit=10000<br />  # Thrift version to use when communicating with HiveServer2<br />  thrift_version=5<br /> ###########################################################################<br /> # Settings to configure the Zookeeper application.<br /> ###########################################################################<br /> [zookeeper]<br />  [[clusters]]<br />    [[[default]]]<br />      # Zookeeper ensemble. Comma separated list of Host/Port.<br />      # e.g. localhost:2181,localhost:2182,localhost:2183<br />      host_ports=phd2.localdomain:2181<br />      # The URL of the REST contrib service (required for znode browsing)<br />      rest_url=http://phd2.localdomain:9998<br /> ###########################################################################<br /> # Settings to configure HBase Browser<br /> ###########################################################################<br /> [hbase]<br />  # Comma-separated list of HBase Thrift servers for clusters in the format of '(name|host:port)'.<br />  # Use full hostname with security.<br />  hbase_clusters=(Cluster|phd2.localdomain:9090)<br /> </code></pre>
  </p>

  <div id="appendixb" class="article-content entry-content">
    <p>
      <strong>Appendix B: RDBMS view doesn’t show tables workaround</strong>
    </p>

    <div dir="ltr">
      Credits to Scott Kahler for this workaround!
    </div>

    <div dir="ltr">
      <br class="kix-line-break" />Edit /usr/lib/hue/desktop/libs/librdbms/src/librdbms/server/postgresql_lib.py. Replace the cursor.execute() statements in the get_tables() and get_columns() methods as shown below
    </div>
  </div>

  <p>
    <pre><code class="python">def get_tables(self, database, table_names=[]):<br /> # Doesn’t use database and only retrieves tables for database currently in use.<br /> cursor =self.connection.cursor()<br /> #cursor.execute(“SELECT table_name FROM information_schema.tables WHERE table_schema=’%s'” % database)<br /> cursor.execute(“SELECT table_name FROM information_schema.tables WHERE table_schema NOT IN (‘hawq_toolkit’,’information_schema’,’madlib’,’pg_aoseg’,’pg_bitmapindex’,’pg_catalog’,’pg_toast’)”)<br /> self.connection.commit()<br /> return[row[0]for row in cursor.fetchall()]
  </p>

  <p>
    def get_columns(self, database, table):<br /> cursor =self.connection.cursor()<br /> #cursor.execute(“SELECT column_name FROM information_schema.columns WHERE table_schema=’%s’ and table_name=’%s'” % (database, table))<br /> cursor.execute(“SELECT column_name FROM information_schema.columns WHERE table_name=’%s’ AND table_schema NOT IN (‘hawq_toolkit’,’information_schema’,’madlib’,’pg_aoseg’,’pg_bitmapindex’,’pg_catalog’,’pg_toast’)”% table)<br /> self.connection.commit()<br /> return[row[0]for row in cursor.fetchall()]</code></pre>
  </p>
</div>

<div dir="ltr">
</div>

<div class="article-content entry-content">
  <div dir="ltr">
    You can automate the update like this:
  </div>
</div>

<div dir="ltr">
  <p>
    <pre><code class="bash"><br /> sudo sed -i “s/=’%s’\” % database/NOT IN (‘hawq_toolkit’,’information_schema’,’madlib’,’pg_aoseg’,’pg_bitmapindex’,’pg_catalog’,’pg_toast’)\”/g”/usr/lib/hue/desktop/libs/librdbms/src/librdbms/server/postgresql_lib.py<br /> sudo sed -i “s/table_schema=’%s’ and table_name=’%s’\” % (database, table)/table_name=’%s’ AND table_schema NOT IN (‘hawq_toolkit’,’information_schema’,’madlib’,’pg_aoseg’,’pg_bitmapindex’,’pg_catalog’,’pg_toast’)\” % table/g”/usr/lib/hue/desktop/libs/librdbms/src/librdbms/server/postgresql_lib.py</code></pre>
  </p>
</div>

<div dir="ltr">
</div>

<div class="article-content entry-content">
  <div class="article-content entry-content">
    <div dir="ltr">
      Restart Hue
    </div>

    <div dir="ltr">
      <p>
        <pre><code class="bash">sudo /etc/init.d/hue restart</code></pre>
      </p>
    </div>

    <h1 dir="ltr">
      Related links:
    </h1>

    <div dir="ltr">
      <a href="https://gethue.com/hadoop-hue-3-on-hdp-installation-tutorial/">https://gethue.com/hadoop-hue-3-on-hdp-installation-tutorial/</a>
    </div>
  </div>
</div>

 [1]: http://blog.tzolov.net/2015/06/install-hue-371-on-pivotal-hd-30.html
 [2]: http://blog.tzolov.net
 [3]: https://twitter.com/pivotal
