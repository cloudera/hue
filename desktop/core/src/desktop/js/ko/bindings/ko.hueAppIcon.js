// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';
import * as ko from 'knockout';

const APP_ICON_INDEX = {
  abfs: `<svg class="hi hi-fw"><use xlink:href="#hi-adls"></use></svg>`,
  adls: `<svg class="hi hi-fw"><use xlink:href="#hi-adls"></use></svg>`,
  dashboard: `<svg class="hi hi-fw"><use xlink:href="#hi-dashboard"></use></svg>`,
  default: `<i class="fa fa-fw fa-database"></i>`,
  'dist-cp': `<i class="fa fa-fw fa-files-o"></i>`,
  documents: `<svg class="hi hi-fw"><use xlink:href="#hi-documents"></use></svg>`,
  editor: `<svg class="hi hi-fw"><use xlink:href="#hi-editor"></use></svg>`,
  hbase: `<i class="fa fa-fw fa-th-large"></i>`,
  hdfs: `<i class="fa fa-fw fa-files-o"></i>`,
  hive: `<svg class="hi hi-fw"><use xlink:href="#hi-hive"></use></svg>`,
  impala: `<svg class="hi hi-fw"><use xlink:href="#hi-impala"></use></svg>`,
  importer: `<i class="fa fa-fw fa-cloud-upload"></i>`,
  indexes: `<i class="fa fa-fw fa-search-plus"></i>`,
  jar: `<svg class="hi hi-fw"><use xlink:href="#hi-spark"></use></svg>`,
  java: `<i class="fa fa-fw fa-file-code-o"></i>`,
  'job-designer': `<svg class="hi hi-fw"><use xlink:href="#hi-job-designer"></use></svg>`,
  kafka: `<i class="fa fa-fw fa-sitemap"></i>`,
  mapreduce: `<i class="fa fa-fw fa-file-archive-o"></i>`,
  markdown: `<svg class="hi hi-fw"><use xlink:href="#hi-markdown"></use></svg>`,
  notebook: `<svg class="hi hi-fw"><use xlink:href="#hi-file-notebook"></use></svg>`,
  oozie: `<svg class="hi hi-fw"><use xlink:href="#hi-oozie"></use></svg>`,
  'oozie-bundle': `<svg class="hi hi-fw"><use xlink:href="#hi-oozie-bundle"></use></svg>`,
  'oozie-coordinator': `<svg class="hi hi-fw"><use xlink:href="#hi-oozie-coordinator"></use></svg>`,
  'oozie-workflow': `<svg class="hi hi-fw"><use xlink:href="#hi-oozie-workflow"></use></svg>`,
  pig: `<svg class="hi hi-fw"><use xlink:href="#hi-pig"></use></svg>`,
  py: `<svg class="hi hi-fw"><use xlink:href="#hi-py"></use></svg>`,
  pyspark: `<svg class="hi hi-fw"><use xlink:href="#hi-spark"></use></svg>`,
  queries: `<i class="fa fa-fw fa-tasks"></i>`,
  r: `<svg class="hi hi-fw"><use xlink:href="#hi-r"></use></svg>`,
  report: `<i class="fa fa-fw fa-area-chart"></i>`,
  s3: `<i class="fa fa-fw fa-cubes"></i>`,
  scala: `<svg class="hi hi-fw"><use xlink:href="#hi-scala"></use></svg>`,
  scheduler: `<svg class="hi hi-fw"><use xlink:href="#hi-oozie"></use></svg>`,
  security: `<i class="fa fa-fw fa-lock"></i>`,
  shell: `<i class="fa fa-fw fa-terminal"></i>`,
  solr: `<i class="fa fa-fw fa-search-plus"></i>`,
  spark2: `<svg class="hi hi-fw"><use xlink:href="#hi-spark"></use></svg>`,
  spark: `<svg class="hi hi-fw"><use xlink:href="#hi-spark"></use></svg>`,
  sqoop1: `<svg class="hi hi-fw"><use xlink:href="#hi-sqoop"></use></svg>`,
  sqoop: `<svg class="hi hi-fw"><use xlink:href="#hi-sqoop"></use></svg>`,
  support: `<svg class="hi hi-fw"><use xlink:href="#hi-support"></use></svg>`,
  tables: `<i class="fa fa-fw fa-database"></i>`,
  text: `<i class="fa fa-fw fa-i-cursor"></i>`,
  warehouses: `<i class="altus-icon altus-adb-cluster" style="margin: 0 1px 0 3px"></i>`,
  workflows: `<svg class="hi hi-fw"><use xlink:href="#hi-oozie"></use></svg>`,
  yarn: `<i class="fa fa-fw fa-tasks"></i>`
};

ko.bindingHandlers.hueAppIcon = {
  update: function (element, valueAccessor) {
    const options = ko.unwrap(valueAccessor());
    const iconName = options.icon ? ko.unwrap(options.icon) : options;
    $(element).html(APP_ICON_INDEX[iconName] || APP_ICON_INDEX.default);
  }
};
