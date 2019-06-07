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

import I18n from 'utils/i18n';

const DOCUMENT_TYPE_I18n = {
  all: I18n('All'),
  directory: I18n('Directory'),
  'link-pigscript': I18n('Pig Design'),
  'link-workflow': I18n('Job Design'),
  notebook: I18n('Notebook'),
  'oozie-bundle2': I18n('Oozie Bundle'),
  'oozie-coordinator2': I18n('Oozie Schedule'),
  'oozie-workflow2': I18n('Oozie Workflow'),
  'query-hive': I18n('Hive Query'),
  'query-impala': I18n('Impala Query'),
  'search-dashboard': I18n('Search Dashboard'),
  'query-mapreduce': I18n('MapReduce Job'),
  'query-sqoop1': I18n('Import Job'),
  'query-spark2': I18n('Spark Job'),
  'query-java': I18n('Java Job'),
  'query-pig': I18n('Pig Script'),
  'query-shell': I18n('Shell Script'),
  'query-distcp': I18n('DistCp Job')
};

const DOCUMENT_TYPES = [];

Object.keys(DOCUMENT_TYPE_I18n).forEach(key => {
  if (key !== 'all') {
    DOCUMENT_TYPES.push({ type: key, label: DOCUMENT_TYPE_I18n[key] });
  }
});

DOCUMENT_TYPES.sort((a, b) => a.label.localeCompare(b.label));
DOCUMENT_TYPES.unshift({ type: 'all', label: DOCUMENT_TYPE_I18n['all'] });

export { DOCUMENT_TYPE_I18n, DOCUMENT_TYPES };
