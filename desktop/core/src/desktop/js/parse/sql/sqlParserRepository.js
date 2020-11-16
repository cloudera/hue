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

/* eslint-disable */
/**
 * AUTOCOMPLETE_MODULES and SYNTAX_MODULES are generated, do not edit manually, see tools/jison/generateParsers.js
 */
const AUTOCOMPLETE_MODULES = {
  calcite: () => import(/* webpackChunkName: "calcite-parser" */ 'parse/sql/calcite/calciteAutocompleteParser'),
  druid: () => import(/* webpackChunkName: "druid-parser" */ 'parse/sql/druid/druidAutocompleteParser'),
  elasticsearch: () => import(/* webpackChunkName: "elasticsearch-parser" */ 'parse/sql/elasticsearch/elasticsearchAutocompleteParser'),
  flink: () => import(/* webpackChunkName: "flink-parser" */ 'parse/sql/flink/flinkAutocompleteParser'),
  generic: () => import(/* webpackChunkName: "generic-parser" */ 'parse/sql/generic/genericAutocompleteParser'),
  hive: () => import(/* webpackChunkName: "hive-parser" */ 'parse/sql/hive/hiveAutocompleteParser'),
  impala: () => import(/* webpackChunkName: "impala-parser" */ 'parse/sql/impala/impalaAutocompleteParser'),
  ksql: () => import(/* webpackChunkName: "ksql-parser" */ 'parse/sql/ksql/ksqlAutocompleteParser'),
  phoenix: () => import(/* webpackChunkName: "phoenix-parser" */ 'parse/sql/phoenix/phoenixAutocompleteParser'),
  presto: () => import(/* webpackChunkName: "presto-parser" */ 'parse/sql/presto/prestoAutocompleteParser')
};
const SYNTAX_MODULES = {
  calcite: () => import(/* webpackChunkName: "calcite-parser" */ 'parse/sql/calcite/calciteSyntaxParser'),
  druid: () => import(/* webpackChunkName: "druid-parser" */ 'parse/sql/druid/druidSyntaxParser'),
  elasticsearch: () => import(/* webpackChunkName: "elasticsearch-parser" */ 'parse/sql/elasticsearch/elasticsearchSyntaxParser'),
  flink: () => import(/* webpackChunkName: "flink-parser" */ 'parse/sql/flink/flinkSyntaxParser'),
  generic: () => import(/* webpackChunkName: "generic-parser" */ 'parse/sql/generic/genericSyntaxParser'),
  hive: () => import(/* webpackChunkName: "hive-parser" */ 'parse/sql/hive/hiveSyntaxParser'),
  impala: () => import(/* webpackChunkName: "impala-parser" */ 'parse/sql/impala/impalaSyntaxParser'),
  ksql: () => import(/* webpackChunkName: "ksql-parser" */ 'parse/sql/ksql/ksqlSyntaxParser'),
  phoenix: () => import(/* webpackChunkName: "phoenix-parser" */ 'parse/sql/phoenix/phoenixSyntaxParser'),
  presto: () => import(/* webpackChunkName: "presto-parser" */ 'parse/sql/presto/prestoSyntaxParser')
};
/* eslint-enable */

class SqlParserRepository {
  constructor() {
    this.modulePromises = {};
  }

  async getParser(dialect, parserType) {
    if (!this.modulePromises[dialect + parserType]) {
      const modules = parserType === 'Autocomplete' ? AUTOCOMPLETE_MODULES : SYNTAX_MODULES;
      this.modulePromises[dialect + parserType] = new Promise((resolve, reject) => {
        const targetModule = modules[dialect] || modules.generic;
        targetModule()
          .then(module => resolve(module.default))
          .catch(reject);
      });
    }
    return this.modulePromises[dialect + parserType];
  }

  /**
   * @param dialect
   * @return {Promise<*>}
   */
  async getAutocompleter(dialect) {
    return this.getParser(dialect, 'Autocomplete');
  }

  async getSyntaxParser(dialect) {
    return this.getParser(dialect, 'Syntax');
  }
}

const sqlParserRepository = new SqlParserRepository();

export default sqlParserRepository;
