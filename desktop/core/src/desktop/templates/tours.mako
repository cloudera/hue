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
      {"name": "huehomedoc", "desc": "${_("Get started!")}", "path": "/home", "steps": [
        {"arrowOn": ".currentApp", "expose": ".navbar-fixed-top", "title": "${_("Your new home.")}", "content": "${_("This is where you can access all your documents and you can tag them per project. Your home is always reachable from any part of Hue, just click on the house icon on the top navigator bar.")}", "placement": "bottom", "onShown": "", "waitForAction": false, "left": 90},
        {"arrowOn": ".sidebar-nav", "expose": ".sidebar-nav", "title": "${_("Actions and projects")}", "content": "${_("From here you can create new documents or see a specific project or any trashed document for instance.")}", "placement": "right", "onShown": "", "waitForAction": false},
        {"arrowOn": ".tag-mine-header:eq(0)", "expose": ".tag-mine-header:eq(0)", "title": "${_("Organize!")}", "content": "${_("You can organize your documents in projects and filter them out in this area. It's a smart and fast way to focus on a specific project you are currently tackling.")}", "placement": "right", "onShown": "", "waitForAction": false},
        {"arrowOn": ".card-home", "expose": ".card-home", "title": "${_("Your documents")}", "content": "${_("You can always have a glance at your hard work. This is the list of all your documents, The first column tells you the kind of document that is, then you can find its name, a description and some other fields.")}", "placement": "left", "onShown": "", "waitForAction": false, "top": "60px", "left": 40},
        {"arrowOn": "#documents > tbody > tr:nth-child(1) > td:nth-child(5)", "expose": "#documents > tbody > tr:nth-child(1) > td:nth-child(5)", "title": "${_("Projects")}", "content": "${_("You can assign one or more projects to a document just by clicking in this cell.")}", "placement": "top", "onShown": "", "waitForAction": false, "top": -20},
        {"arrowOn": "#documents > tbody > tr:nth-child(1) > td:nth-child(6)", "title": "${_("Share your documents")}", "content": "${_("You can also share a document you have worked on with a specific user or a group of users. Just click on the icon in this column on every document you want to share and choose users and groups from the popup.")}", "placement": "left", "onShown": "", "waitForAction": false, "top": -20},
        {"arrowOn": "#searchInput", "expose": "#searchInput", "title": "${_("Search your documents")}", "content": "${_("You can always filter out the documents by name, description or even owner. Enjoy your new home!")}", "placement": "left", "onShown": "", "waitForAction": false, "top": -10}
      ]
      },
      {
        "name": "genericapp00",
        "desc": "${_("Read more on the Hue blog")}",
        "path": "/(jobsub|useradmin|help|about)",
        "video": "",
        "blog": "http://gethue.com/blog/"
      },
      {
        "name": "beeswaxapp00",
        "desc": "${_("Hue blog: Hive")}",
        "path": "/(beeswax|metastore)",
        "video": "",
        "blog": "http://gethue.com/category/hive/"
      },
      {
        "name": "impalaapp00",
        "desc": "${_("Hue blog: Impala")}",
        "path": "/(impala|metastore)",
        "video": "",
        "blog": "http://gethue.com/category/impala/"
      },
      {
        "name": "beeswaxapp00",
        "desc": "${_("Hue blog: DB Query")}",
        "path": "/(rdbms)",
        "video": "",
        "blog": "http://gethue.com/category/dbquery/"
      },
      {
        "name": "pigapp00",
        "desc": "${_("Hue blog: Pig")}",
        "path": "/(pig)",
        "video": "",
        "blog": "http://gethue.com/category/pig/"
      },
      {
        "name": "sparkapp00",
        "desc": "${_("Hue blog: Spark")}",
        "path": "/(spark)",
        "video": "",
        "blog": "http://gethue.com/category/spark/"
      },
      {
        "name": "hbaseapp00",
        "desc": "${_("Hue blog: HBase")}",
        "path": "/(hbase)",
        "video": "",
        "blog": "http://gethue.com/category/hbase/"
      },
      {
        "name": "sqoopapp00",
        "desc": "${_("Hue blog: Sqoop")}",
        "path": "/(sqoop)",
        "video": "",
        "blog": "http://gethue.com/category/sqoop/"
      },
      {
        "name": "zookeeperapp00",
        "desc": "${_("Hue blog: Zookeeper")}",
        "path": "/(zookeeper)",
        "video": "",
        "blog": "http://gethue.com/category/zookeeper/"
      },
      {
        "name": "oozieapp00",
        "desc": "${_("Hue blog: Oozie")}",
        "path": "/(oozie)",
        "video": "",
        "blog": "http://gethue.com/category/oozie/"
      },
      {
        "name": "oozieapp00",
        "desc": "${_("Hue blog: Search")}",
        "path": "/(search)",
        "video": "",
        "blog": "http://gethue.com/category/search/"
      },
      {
        "name": "sentryapp00",
        "desc": "${_("Hue blog: Security")}",
        "path": "/(security)",
        "video": "",
        "blog": "http://gethue.com/category/security/"
      },
      {
        "name": "fbapp00",
        "desc": "${_("Hue blog: HDFS")}",
        "path": "/(filebrowser)",
        "video": "",
        "blog": "http://gethue.com/category/hdfs/"
      },
      {
        "name": "jbapp00",
        "desc": "${_("Hue blog: Job Browser")}",
        "path": "/(jobbrowser)",
        "video": "",
        "blog": "http://gethue.com/category/jobbrowser/"
      }
    ]
  });

</script>