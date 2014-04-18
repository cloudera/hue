## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
from django.utils.translation import ugettext as _
%>

<script type="text/javascript">
$.jHueTour({
  "tours": [
    {
      "name": "thehueblog",
      "desc": "${_("The Hue Blog")}",
      "path": "/",
      "video": "",
      "blog": "http://gethue.com/blog/"
    },
    {"name": "huehomedoc", "desc": "${_("Get started!")}", "path": "/home", "steps": [
      {"arrowOn": ".currentApp", "expose": ".navbar-fixed-top", "title": "${_("Your new home.")}", "content": "${_("This is where you can access all your documents and you can tag them per project. Your home is always reachable from any part of Hue, just click on the house icon on the top navigator bar.")}", "placement": "bottom", "onShown": "", "waitForAction": false, "left": 90},
      {"arrowOn": ".sidebar-nav", "expose": ".sidebar-nav", "title": "${_("Actions and projects")}", "content": "${_("From here you can create new documents or see a specific project or any trashed document for instance.")}", "placement": "right", "onShown": "", "waitForAction": false},
      {"arrowOn": ".tag-header:eq(0)", "expose": ".tag-header:eq(0)", "title": "${_("Organize!")}", "content": "${_("You can organize your documents in projects and filter them out in this area. It's a smart and fast way to focus on a specific project you are currently tackling.")}", "placement": "right", "onShown": "", "waitForAction": false},
      {"arrowOn": ".card-home", "expose": ".card-home", "title": "${_("Your documents")}", "content": "${_("You can always have a glance at your hard work. This is the list of all your documents, The first column tells you the kind of document that is, then you can find its name, a description and some other fields.")}", "placement": "left", "onShown": "", "waitForAction": false, "top": "60px", "left": 40},
      {"arrowOn": ".datatables tr th:nth-child(4)", "expose": ".datatables tr td:nth-child(4)", "title": "${_("Projects")}", "content": "${_("You can assign one or more projects to a document just by clicking in this cell.")}", "placement": "top", "onShown": "", "waitForAction": false, "top": -20},
      {"arrowOn": ".datatables tr th:nth-child(7)", "expose": ".datatables tr td:nth-child(7)", "title": "${_("Share your documents")}", "content": "${_("You can also share a document you have worked on with a specific user or a group of users. Just click on the icon in this column on every document you want to share and choose users and groups from the popup.")}", "placement": "left", "onShown": "", "waitForAction": false, "top": -20},
      {"arrowOn": "#filterInput", "expose": "#filterInput", "title": "${_("Search your documents")}", "content": "${_("You can always filter out the documents by name, description or even owner. Enjoy your new home!")}", "placement": "left", "onShown": "", "waitForAction": false, "top": -10}
    ]
    },
    {
      "name": "hiveheaders",
      "desc": "${_("Create Hive tables and load quoted")}<br/>${_("CSV data")}",
      "path": "/beeswax",
      "video": "http://player.vimeo.com/video/80460405",
      "blog": "http://gethue.com/hadoop-tutorial-create-hive-tables-with-headers-and/"
    },
    {
      "name": "fbooziesubmit",
      "desc": "${_("Submit any Oozie jobs directly")}<br/>${_("from HDFS")}",
      "path": "/(oozie|filebrowser)",
      "video": "http://player.vimeo.com/video/80749790",
      "blog": "http://gethue.com/hadoop-tutorial-submit-any-oozie-jobs-directly-from/"
    },
    {
      "name": "zookeeper",
      "desc": "${_("ZooKeeper Browser")}",
      "path": "/zookeeper",
      "video": "http://player.vimeo.com/video/79795356",
      "blog": "http://gethue.com/new-zookeeper-browser-app/"
    },
    {
      "name": "dbquery",
      "desc": "${_("Query your Databases")}",
      "path": "/rdbms",
      "video": "http://player.vimeo.com/video/79020016",
      "blog": "http://gethue.com/dbquery-app-mysql-postgresql-oracle-and-sqlite-query/"
    },
    {
      "name": "searchgraph",
      "desc": "${_("Graphical facets")}",
      "path": "/search",
      "video": "http://player.vimeo.com/video/78887745",
      "blog": "http://gethue.com/new-search-feature-graphical-facets/"
    },
    {
      "name": "impalasentry",
      "desc": "${_("Use Impala with Sentry")}",
      "path": "/impala",
      "video": "",
      "blog": "http://gethue.com/use-the-impala-app-with-sentry-for-real-security/"
    },
    {
      "name": "ooziefb",
      "desc": "${_("Submit Oozie jobs directly from HDFS")}",
      "path": "/(oozie|filebrowser)",
      "video": "http://player.vimeo.com/video/80749790",
      "blog": "http://gethue.tumblr.com/post/68781982681/hadoop-tutorial-submit-any-oozie-jobs-directly-from"
    },
    {
      "name": "jbyarn",
      "desc": "${_("A Job Browser for Yarn")}",
      "path": "/jobbrowser",
      "video": "http://player.vimeo.com/video/84027054",
      "blog": "http://gethue.com/using-hadoop-mr2-and-yarn-with-an-alternative-job/"
    },
    {
      "name": "jbyarnsecurity",
      "desc": "${_("Security with Yarn")}",
      "path": "/jobbrowser",
      "video": "http://player.vimeo.com/video/85922379",
      "blog": "http://gethue.com/secure-your-yarn-cluster-and-access-the-jobs/"
    },
    {
      "name": "sentry",
      "desc": "${_("Hive Query editor with HiveServer2")}<br/>${_("and Sentry")}",
      "path": "/(beeswax|impala)",
      "video": "http://player.vimeo.com/video/79883574",
      "blog": "http://gethue.com/hadoop-tutorial-hive-query-editor-with-hiveserver2-and/"
    },
    {
      "name": "superproxy",
      "desc": "${_("Integrate external Web applications in")}<br/>${_("any language")}",
      "path": "/about",
      "video": "http://player.vimeo.com/video/79178858",
      "blog": "http://gethue.com/integrate-external-web-applications-in-any-language/"
    },
    {
      "name": "season2",
      "desc": "${_("Season 2 of Hadoop Video Tutorials")}",
      "path": "/",
      "video": "",
      "blog": "http://gethue.com/category/season2/"
    },
    {
      "name": "twitter",
      "desc": "${_("Analyze Twitter data")}",
      "path": "/home",
      "video": "",
      "blog": "http://gethue.com/how-to-analyze-twitter-data-with-hue/"
    },
    {
      "name": "pigudf",
      "desc": "${_("Preparing Yelp data for analysis with")}<br/>${_("Pig and Python UDF")}",
      "path": "/(home|pig|filebrowser|metastore)",
      "video": "http://player.vimeo.com/video/73849021",
      "blog": "http://gethue.com/hadoop-tutorials-ii-1-prepare-the-data-for-analysis/"
    },
    {
      "name": "hue35",
      "desc": "${_("What's new in Hue 3.5")}",
      "path": "/(about|home)",
      "video": "",
      "blog": "http://gethue.com/hue-3-5-and-its-redesign-are-out/"
    },
    {
      "name": "saml",
      "desc": "${_("SSO with SAML")}",
      "path": "/(useradmin|about)",
      "video": "http://player.vimeo.com/video/76063637",
      "blog": "http://gethue.com/sso-with-hue-new-saml-backend/"
    },
    {
      "name": "ldaphowto",
      "desc": "${_("Integrating your company with LDAP: How To")}",
      "path": "/(useradmin|about)",
      "video": "",
      "blog": "http://gethue.com/making-hadoop-accessible-to-your-employees-with-ldap/"
    },
    {
      "name": "sparkapp",
      "desc": "${_("A new Spark UI")}",
      "path": "/(spark)",
      "video": "http://player.vimeo.com/video/78887745",
      "blog": "http://gethue.com/a-new-spark-web-ui-spark-app/"
    },
    {
      "name": "impalavshive",
      "desc": "${_("Fast SQL with Impala")}",
      "path": "/impala",
      "video": "http://player.vimeo.com/video/75493693",
      "blog": "http://gethue.com/fast-sql-with-the-impala-query-editor/"
    },
    {
      "name": "pigeditor",
      "desc": "${_("The Pig Editor")}",
      "path": "/pig",
      "video": "http://player.vimeo.com/video/66661052",
      "blog": "http://gethue.com/tutorial-apache-pig-editor-in-hue-2-3/"
    },
    {
      "name": "hiveudf",
      "desc": "${_("Build and use Hive UDF in 1 minute!")}",
      "path": "/beeswax",
      "video": "http://player.vimeo.com/video/72200781",
      "blog": "http://gethue.com/hadoop-tutorial-hive-udf-in-1-minute/"
    },
    {
      "name": "hcatalog",
      "desc": "${_("How to use HCatalog in Hue with Pig")}",
      "path": "/(metastore|pig)",
      "video": "http://player.vimeo.com/video/71024770",
      "blog": "http://gethue.com/hadoop-tutorial-how-to-access-hive-in-pig-with/"
    },
    {
      "name": "hbasebrowser",
      "desc": "${_("HBase Browser")}",
      "path": "/hbase",
      "video": "http://player.vimeo.com/video/72357888",
      "blog": "http://gethue.com/the-web-ui-for-hbase-hbase-browser/"
    },
    {
      "name": "hbasetables",
      "desc": "${_("Create HBase tables")}",
      "path": "/hbase",
      "video": "http://player.vimeo.com/video/72200782",
      "blog": "http://gethue.com/hadoop-tutorial-how-to-create-example-tables-in-hbase/"
    },
    {
      "name": "oozieworkflows",
      "desc": "${_("Oozie Workflow")}",
      "path": "/(oozie|beeswax)",
      "video": "http://player.vimeo.com/video/73849021",
      "blog": "http://gethue.com/hadoop-tutorials-ii-2-execute-hive-queries-and/"
    },
    {
      "name": "ooziecoordinator",
      "desc": "${_("Oozie Coordinator")}",
      "path": "/oozie",
      "video": "http://player.vimeo.com/video/74215175",
      "blog": "http://gethue.com/hadoop-tutorials-ii-3-schedule-hive-queries-with/"
    },
    {
      "name": "search",
      "desc": "${_("The search app with Solr")}",
      "path": "/search",
      "video": "http://player.vimeo.com/video/68257054",
      "blog": "http://gethue.com/tutorial-search-hadoop-in-hue/"
    },
    {
      "name": "filebrowser",
      "desc": "${_("HDFS File Operations Made Easy")}",
      "path": "/filebrowser",
      "video": "http://player.vimeo.com/video/63343487",
      "blog": "http://gethue.com/demo-hdfs-file-operations-made-easy-with-hue/"
    },
    {
      "name": "hueha",
      "desc": "${_("High availability in Hue")}",
      "path": "/about",
      "video": "http://player.vimeo.com/video/71813732",
      "blog": "http://gethue.com/hadoop-tutorial-high-availability-of-hue/"
    },
    {
      "name": "hue25",
      "desc": "${_("What's new in Hue 2.5")}",
      "path": "/(about|home)",
      "video": "http://player.vimeo.com/video/70955652",
      "blog": "http://gethue.com/hue-2-5-and-its-hbase-app-is-out/"
    },
    {
      "name": "hueperms",
      "desc": "${_("Manage users and group permissions")}",
      "path": "/useradmin",
      "video": "",
      "blog": "http://gethue.com/how-to-manage-permissions-in-hue/"
    },
    {
      "name": "huesqoop",
      "desc": "${_("Transfering data with Sqoop")}",
      "path": "/sqoop",
      "video": "http://player.vimeo.com/video/76063637",
      "blog": "http://gethue.com/move-data-in-out-your-hadoop-cluster-with-the-sqoop/"
    },
    {
      "name": "newimpala",
      "desc": "${_("New Impala and Hive Editors")}",
      "path": "/(beeswax|impala)",
      "video": "http://player.vimeo.com/video/90961050",
      "blog": "http://gethue.com/hadoop-tutorial-new-impala-and-hive-editors/"
    },
    {
      "name": "oozieslas",
      "desc": "${_("Oozie SLAs")}",
      "path": "/oozie",
      "video": "http://player.vimeo.com/video/90898437",
      "blog": "http://gethue.com/hadoop-tutorial-monitor-and-get-alerts-for-your-workflows-with-the-oozie-slas/"
    },
    {
      "name": "ooziecrontab",
      "desc": "${_("The new Oozie Crontab")}",
      "path": "/oozie",
      "video": "http://player.vimeo.com/video/85922380",
      "blog": "http://gethue.com/hadoop-tutorial-schedule-your-hadoop-jobs-intuitively/"
    },
    {
      "name": "secureyarn",
      "desc": "${_("Secure your YARN cluster")}",
      "path": "/jobbrowser",
      "video": "http://player.vimeo.com/video/85922379",
      "blog": "http://gethue.com/secure-your-yarn-cluster-and-access-the-jobs/"
    },
    {
      "name": "alternativejb",
      "desc": "${_("MR2 and YARN alternative Job Browser")}",
      "path": "/jobbrowser",
      "video": "http://player.vimeo.com/video/84027054",
      "blog": "http://gethue.com/using-hadoop-mr2-and-yarn-with-an-alternative-job/"
    }
  ]
});

</script>