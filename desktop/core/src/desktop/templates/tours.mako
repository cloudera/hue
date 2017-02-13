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
        "name": "genericapp00",
        "desc": "${_("Read more on the Hue blog")}",
        "path": "/(home|home2|jobsub|useradmin|help|about)",
        "video": "",
        "blog": "http://gethue.com/blog/"
      },
      {
        "name": "beeswaxapp00",
        "desc": "${_("Hue blog: Hive")}",
        "path": "/(editor|beeswax|metastore)",
        "video": "",
        "blog": "http://gethue.com/category/hive/"
      },
      {
        "name": "impalaapp00",
        "desc": "${_("Hue blog: Impala")}",
        "path": "/(editor|impala|metastore)",
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