// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'ext/ace/ace'
import 'ext/ace/ext-language_tools';
import 'ext/ace/ext-searchbox';
import 'ext/ace/ext-settings_menu';
import 'ext/ace/mode-bigquery';
import 'ext/ace/mode-dasksql';
import 'ext/ace/mode-druid';
import 'ext/ace/mode-elasticsearch';
import 'ext/ace/mode-flink';
import 'ext/ace/mode-hive';
import 'ext/ace/mode-hplsql';
import 'ext/ace/mode-impala';
import 'ext/ace/mode-ksql';
import 'ext/ace/mode-markdown';
import 'ext/ace/mode-mysql';
import 'ext/ace/mode-pgsql'
import 'ext/ace/mode-phoenix';
import 'ext/ace/mode-presto';
import 'ext/ace/mode-solr';
import 'ext/ace/mode-sparksql';
import 'ext/ace/mode-sql';
import 'ext/ace/mode-text';
import 'ext/ace/snippets/bigquery';
import 'ext/ace/snippets/druid';
import 'ext/ace/snippets/elasticsearch';
import 'ext/ace/snippets/flink';
import 'ext/ace/snippets/hive';
import 'ext/ace/snippets/hplsql';
import 'ext/ace/snippets/impala';
import 'ext/ace/snippets/ksql';
import 'ext/ace/snippets/markdown';
import 'ext/ace/snippets/mysql';
import 'ext/ace/snippets/pgsql';
import 'ext/ace/snippets/phoenix';
import 'ext/ace/snippets/presto';
import 'ext/ace/snippets/dasksql';
import 'ext/ace/snippets/solr';
import 'ext/ace/snippets/sql';
import 'ext/ace/snippets/text';
import 'ext/ace/theme-hue';
import 'ext/ace/theme-hue_dark';
import './aceExtensions';

export default (window as any).ace;

const DIALECT_ACE_MODE_MAPPING: { [dialect: string]: string } = {
  'bigquery': 'ace/mode/bigquery',
  'druid': 'ace/mode/druid',
  'elasticsearch': 'ace/mode/elasticsearch',
  'flink': 'ace/mode/flink',
  'dasksql': 'ace/mode/dasksql',
  'hive': 'ace/mode/hive',
  'hplsql': 'ace/mode/hplsql',
  'impala': 'ace/mode/impala',
  'ksql': 'ace/mode/ksql',
  'mysql': 'ace/mode/mysql',
  'pgsq': 'ace/mode/pgsql',
  'phoenix': 'ace/mode/phoenix',
  'presto': 'ace/mode/presto',
  'solr': 'ace/mode/solr',
  'sql': 'ace/mode/sql'
};

export const getAceMode = (dialect?: string): string =>
  (dialect && DIALECT_ACE_MODE_MAPPING[dialect]) || DIALECT_ACE_MODE_MAPPING.sql;
