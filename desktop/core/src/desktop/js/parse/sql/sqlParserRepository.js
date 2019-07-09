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
  generic: () => import(/* webpackChunkName: "generic-parser" */ 'parse/sql/generic/genericAutocompleteParser'),
  hive: () => import(/* webpackChunkName: "hive-parser" */ 'parse/sql/hive/hiveAutocompleteParser'),
  impala: () => import(/* webpackChunkName: "impala-parser" */ 'parse/sql/impala/impalaAutocompleteParser')
};
const SYNTAX_MODULES = {
  generic: () => import(/* webpackChunkName: "generic-parser" */ 'parse/sql/generic/genericSyntaxParser'),
  hive: () => import(/* webpackChunkName: "hive-parser" */ 'parse/sql/hive/hiveSyntaxParser'),
  impala: () => import(/* webpackChunkName: "impala-parser" */ 'parse/sql/impala/impalaSyntaxParser')
};
/* eslint-enable */

class SqlParserRepository {
  constructor() {
    this.modulePromises = {};
  }

  async getParser(sourceType, parserType) {
    if (!this.modulePromises[sourceType + parserType]) {
      const modules = parserType === 'Autocomplete' ? AUTOCOMPLETE_MODULES : SYNTAX_MODULES;
      this.modulePromises[sourceType + parserType] = new Promise((resolve, reject) => {
        const targetModule = modules[sourceType] || modules.generic;
        targetModule()
          .then(module => resolve(module.default))
          .catch(reject);
      });
    }
    return this.modulePromises[sourceType + parserType];
  }

  async getAutocompleter(sourceType) {
    return this.getParser(sourceType, 'Autocomplete');
  }

  async getSyntaxParser(sourceType) {
    return this.getParser(sourceType, 'Syntax');
  }
}

const sqlParserRepository = new SqlParserRepository();

export default sqlParserRepository;
