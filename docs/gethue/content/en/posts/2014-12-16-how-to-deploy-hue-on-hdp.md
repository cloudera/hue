---
title: How to deploy Hue on HDP
author: admin
type: post
date: 2014-12-16T19:36:47+00:00
url: /how-to-deploy-hue-on-hdp/
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
slide_template:
  - default
categories:

---
_Guest post from <a href="http://andrewmo.com" target="_blank" rel="noopener noreferrer">Andrew</a> that we regularly update (Dec 19th 2014)_

&nbsp;

I decided to deploy <a href="https://gethue.com/hue-3-7-with-sentry-app-and-new-search-widgets-are-out/" target="_blank" rel="noopener noreferrer">Hue 3.7</a>, from <a href="https://gethue.com/category/release/" target="_blank" rel="noopener noreferrer">tarballs</a> (note, other sources like packages from the 'Install' menu above would work too), on [HDP 2.2][1] recently and wanted to document some notes for anyone else looking to do the same.

Deployment Background:

  * Node Operating System:  CentOS 6.6 - 64bit
  * Cluster Manager:  Ambari 1.7
  * Distribution:  HDP 2.2
  * Install Path (default):  /usr/local/hue
  * HUE User:  hue

After compiling (some <a href="https://gethue.com/how-to-build-hue-on-ubuntu-14-04-trusty/" target="_blank" rel="noopener noreferrer">hints there</a>), you may run into out of the box/post-compile startup issues.

  * Be sure to set the appropriate Hue proxy user/groups properties in your Hadoop service configurations (e.g. WebHDFS/WebHCat/Oozie/etc)

  * Don't forget to configure your <a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank" rel="noopener noreferrer">Hue configuration file</a> ('/usr/local/hue/desktop/conf/<wbr />hue.ini') to use FQDN hostnames in the appropriate places

&nbsp;

[<img src="https://cdn.gethue.com/uploads/2014/12/beeswax-editor-1024x584.png" />][2]

&nbsp;

# Startup

Hue uses an SQLite database by default and you may find the following error when attempting to connect to HUE at its default port (e.g. fqdn:8888)

  * **_..._** _File "/usr/local/hue/build/env/lib/<wbr />python2.6/site-packages/Django<wbr />-1.4.5-py2.6.egg/django/db/<wbr />backends/sqlite3/base.py", line 344, in execute return Database.Cursor.execute(self, query, params) DatabaseError: unable to open database file_

  * SQLlite uses a file to store its databases, so this error most likely occurs due to invalid ownership settings for HUE-related files.
      * We can fix this with the command 'chown hue:hue -R /usr/local/hue'
  * For non development usage, we recommend to startup with MySql instead of SqlLite: <a href="https://github.com/cloudera/hue/blob/master/desktop/conf.dist/hue.ini#L292" target="_blank" rel="noopener noreferrer">https://github.com/cloudera/<wbr />hue/blob/master/desktop/conf.<wbr />dist/hue.ini#L292</a>

&nbsp;

# Removing apps

<div>
  <div>
    <div>
      <div>
        For Impala (or any other app), the easiest way to remove them is to just black list them in the <a href="https://gethue.com/how-to-configure-hue-in-your-hadoop-cluster/" target="_blank" rel="noopener noreferrer">hue.ini</a>. The second best alternative way is to remove the <a href="https://gethue.com/how-to-manage-permissions-in-hue/" target="_blank" rel="noopener noreferrer">Hue permissions</a> to the groups of some users.
      </div>
    </div>

    <div>
      <p>
        <pre><code class="bash">[desktop]<br /> app_blacklist=impala<br /> </code></pre>
      </p>
    </div>
  </div>

  <div>
  </div>

  <div>
    For Sentry, you will need to use 'security', but it will also hide the HDFS ACLs editor for now.
  </div>

  <div>
  </div>
</div>

# HDFS

<div>
  <div>
    <div>
      <div>
        <div>
          <div>
            <div>
              <div>
                Check your HDFS configuration settings and ensure that the service is active and healthy.
              </div>

              <div>
              </div>

              <div>
                <div>
                  <div>
                    Did you remember to configure proxy user hosts and groups for your HDFS service configuration?
                  </div>

                  <p>
                    With Ambari, you can review your cluster's HDFS configuration, specifically under the "Custom core-site.xml" subsection:
                  </p>
                </div>

                <p>
                  There should be two (2) new/custom properties added to support the HUE File Browser:
                </p>

                <p>
                  <pre><code class="xml"><property><br /> <name>hadoop.proxyuser.hue.hosts</name><br /> <value>*</value><br /> </property><br /> <property><br /> <name>hadoop.proxyuser.hue.groups</name><br /> <value>*</value><br /> </property><br /> </code></pre>
                </p>

                <p>
                  With Ambari, you can go to the HDFS service settings and find this under "General"
                </p>
              </div>

              <p>
                - The property name is dfs.webhdfs.enabled ("WebHDFS enabled), and should be set to "true" by default.
              </p>
            </div>

            <p>
              - If a change is required, save the change and start/restart the service with the updated configuration.
            </p>

            <p>
              Ensure the HDFS service is started and operating normally.
            </p>
          </div>

          <p>
            - You could quickly check some things, such as HDFS and WebHDFS by checking the WebHDFS page:
          </p>
        </div>

        <p>
          - http://<NAMENODE-FQDN>:50070/ in a web browser or 'curl <NAMENODE-FQDN>:50070
        </p>
      </div>
    </div>

    <p>
      Check if the processes are running using a shell command on your NameNode:
    </p>
  </div>

  <p>
    - 'ps -ef | grep "NameNode"
  </p>

  <div>
    <div>
      <div>
        <div>
          <div>
            <div>
              <div>
                <div>
                  <div>
                  </div>

                  <div>
                    By default your HDFS service(s) may not be configured to start automatically (e.g. upon boot/reboot).
                  </div>

                  <div>
                    Check the HDFS logs to see if the namenode service had trouble starting or started successfully:
                  </div>

                  <div>
                    - These are typically found at '/var/log/hadoop/hdfs/'
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <p>
    &nbsp;
  </p>

  <h1>
    Hive Editor
  </h1>

  <div>
    By default, HUE appears to connect to the Hiveserver2 service using NOSASL authentication; Hive 0.14 ships with HDP 2.2 but is not configured by default to use authentication.
  </div>

  <ul>
    <li>
      We'll need to change the properties of our Hive configuration to work with the HUE Hive Editor ('hive.server2.authentication=<wbr />'NOSASL').
    </li>
  </ul>

  <div id=":16x" class="ajR" tabindex="0" data-tooltip="Show trimmed content">
    HDP 2.1 (Hive 0.13) continues to carry forward the GetLog() issue with Hue's Hive Editor.e.g.
  </div>

  <div class="ajR" tabindex="0" data-tooltip="Show trimmed content">
    <div>
    </div>

    <div>
      <p>
        <pre><code class="bash">"Server does not support GetLog()"</code></pre>
      </p>
    </div>

    <div>
    </div>

    <div>
      In HDP 2.2, that includes Hive 0.14 and <a href="https://issues.apache.org/jira/browse/HIVE-4629">HIVE-4629</a>, you will need this <a href="https://github.com/cloudera/hue/commit/6a0246710f7deeb0fd2e1f2b3b209ad119c30b72">commit</a> from Hue 3.8 (coming-up at the end of Q1 2015) or use master, and enable it in the hue.ini:
    </div>

    <div>
      <div>
        <div>
          <p>
            <pre><code class="bash">[beeswax]<br /> # Choose whether Hue uses the GetLog() thrift call to retrieve Hive logs.<br /> # If false, Hue will use the FetchResults() thrift call instead.<br /> use_get_log_api=false<br /> </code></pre>
          </p>
        </div>
      </div>
    </div>
  </div>

  <h1>
    Security - HDFS ACLs Editor
  </h1>

  <p>
    By default, Hadoop 2.4.0 does not enable HDFS file access control lists (FACLs)
  </p>

  <ul>
    <li>
      <i>AclException: The ACL operation has been rejected.  Support for ACLs has been disabled by setting dfs.namenode.acls.enabled to false. (error 403)</i> <ul>
        <li>
          Reference: <a href="http://hadoop.apache.org/docs/r2.4.0/hadoop-project-dist/hadoop-hdfs/HdfsPermissionsGuide.html" target="_blank" rel="noopener noreferrer">http://hadoop.apache.org/docs/<wbr />r2.4.0/hadoop-project-dist/had<wbr />oop-hdfs/HdfsPermissionsGuide.<wbr />html</a>
        </li>
      </ul>
    </li>
  </ul>

  <ul>
    <li>
      We'll need to change the properties of our HDFS namenode service to enable FACLs ('dfs.namenode.acls.enabled'='<wbr />true')
    </li>
  </ul>

  <div>
    <div>
      <h1>
        Spark
      </h1>

      <div>
         We are improving the Spark Editor and might change the Job Server and stuff is still pretty manual/not recommend for now.
      </div>
    </div>

    <div>
    </div>

    <h1>
      HBase
    </h1>

    <p>
      Currently not tested (should work with <a href="https://gethue.com/the-web-ui-for-hbase-hbase-browser/" target="_blank" rel="noopener noreferrer">Thrift Server 1</a>)
    </p>
  </div>

  <div class="yj6qo ajU">
    <div id=":16x" class="ajR" tabindex="0" data-tooltip="Show trimmed content">
    </div>

    <div class="ajR" tabindex="0" data-tooltip="Show trimmed content">
      <h1>
        Job Browser
      </h1>

      <div>
        Progress has never been entirely accurate for Map/Reduce completions - always shows the percentage for Mappers vs Reducers as a job progresses. "Kill" feature works correctly.
      </div>

      <div>
      </div>

      <div>
        <h1>
          Oozie Editor/Dashboard
        </h1>

        <p>
          <strong>Note</strong>: when Oozie is deployed via Ambari 1.7, for HDP 2.2, the sharelib files typically found at /usr/lib/oozie/ are missing, and in turn are not staged at hdfs:/user/oozie/share/lib/ ...
        </p>

        <div>
        </div>

        <div>
          I'll check this against an HDP 2.1 deployment and write the guys at Hortonworks an email to see if this is something they've seen as well.
        </div>

        <div>
        </div>
      </div>
    </div>

    <h1>
      Pig Editor
    </h1>

    <div>
       Make sure you have at least 2 nodes or tweak YARN to be able to launch two apps at the same time (<a href="http://blog.cloudera.com/blog/2014/04/apache-hadoop-yarn-avoiding-6-time-consuming-gotchas/">gotcha #5</a>) and Oozie is configured correctly.
    </div>

    <div>
    </div>

    <div>
      The Pig/Oozie log looks like this:
    </div>

    <div>
    </div>

    <div>
      <div>
        <p>
          <pre><code class="bash">2014-12-15 23:32:17,626  INFO ActionStartXCommand:543 - SERVER[hdptest.construct.dev] USER[amo] GROUP[-] TOKEN[] APP[pig-app-hue-script] JOB[0000001-141215230246520-<wbr />oozie-oozi-W] ACTION[0000001-<wbr />141215230246520-oozie-oozi-W@:<wbr />start:] Start action [0000001-141215230246520-<wbr />oozie-oozi-W@:start:] with user-retry state : userRetryCount [0], userRetryMax [0], userRetryInterval [10]
        </p>

        <p>
          2014-12-15 23:32:17,627  INFO ActionStartXCommand:543 - SERVER[hdptest.construct.dev] USER[amo] GROUP[-] TOKEN[] APP[pig-app-hue-script] JOB[0000001-141215230246520-<wbr />oozie-oozi-W] ACTION[0000001-<wbr />141215230246520-oozie-oozi-W@:<wbr />start:] [***0000001-141215230246520-<wbr />oozie-oozi-W@:start:***]Action status=DONE
        </p>

        <p>
          2014-12-15 23:32:17,627  INFO ActionStartXCommand:543 - SERVER[hdptest.construct.dev] USER[amo] GROUP[-] TOKEN[] APP[pig-app-hue-script] JOB[0000001-141215230246520-<wbr />oozie-oozi-W] ACTION[0000001-<wbr />141215230246520-oozie-oozi-W@:<wbr />start:] [***0000001-141215230246520-<wbr />oozie-oozi-W@:start:***]Action updated in DB!
        </p>

        <p>
          2014-12-15 23:32:17,873  INFO ActionStartXCommand:543 - SERVER[hdptest.construct.dev] USER[amo] GROUP[-] TOKEN[] APP[pig-app-hue-script] JOB[0000001-141215230246520-<wbr />oozie-oozi-W] ACTION[0000001-<wbr />141215230246520-oozie-oozi-W@<wbr />pig] Start action [0000001-141215230246520-<wbr />oozie-oozi-W@pig] with user-retry state : userRetryCount [0], userRetryMax [0], userRetryInterval [10]<br /> </code></pre>
        </p>
      </div>
    </div>
  </div>
</div>

 [1]: http://docs.hortonworks.com/HDPDocuments/HDP2/HDP-2.0.6.0/bk_installing_manually_book/content/rpm-chap-hue.html
 [2]: https://cdn.gethue.com/uploads/2014/12/beeswax-editor.png
