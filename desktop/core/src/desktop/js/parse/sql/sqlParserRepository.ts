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

import { AutocompleteParser, SqlParserProvider, SyntaxParser } from 'parse/types';

const AUTOCOMPLETE_MODULES = {
  calcite: () =>
    import(/* webpackChunkName: "calcite-parser" */ './calcite/calciteAutocompleteParser'),
  dasksql: () =>
    import(/* webpackChunkName: "dasksql-parser" */ './dasksql/dasksqlAutocompleteParser'),
  flink: () => import(/* webpackChunkName: "flink-parser" */ './flink/flinkAutocompleteParser'),
  generic: () =>
    import(/* webpackChunkName: "generic-parser" */ './generic/genericAutocompleteParser'),
  hive: () => import(/* webpackChunkName: "hive-parser" */ './hive/hiveAutocompleteParser'),
  impala: () => import(/* webpackChunkName: "impala-parser" */ './impala/impalaAutocompleteParser'),
  ksql: () => import(/* webpackChunkName: "ksql-parser" */ './ksql/ksqlAutocompleteParser'),
  phoenix: () =>
    import(/* webpackChunkName: "phoenix-parser" */ './phoenix/phoenixAutocompleteParser'),
  presto: () => import(/* webpackChunkName: "presto-parser" */ './presto/prestoAutocompleteParser'),
  sparksql: () =>
    import(/* webpackChunkName: "sparksql-parser" */ './sparksql/sparksqlAutocompleteParser')
};
const SYNTAX_MODULES = {
  calcite: () => import(/* webpackChunkName: "calcite-parser" */ './calcite/calciteSyntaxParser'),
  dasksql: () => import(/* webpackChunkName: "dasksql-parser" */ './dasksql/dasksqlSyntaxParser'),
  flink: () => import(/* webpackChunkName: "flink-parser" */ './flink/flinkSyntaxParser'),
  generic: () => import(/* webpackChunkName: "generic-parser" */ './generic/genericSyntaxParser'),
  hive: () => import(/* webpackChunkName: "hive-parser" */ './hive/hiveSyntaxParser'),
  impala: () => import(/* webpackChunkName: "impala-parser" */ './impala/impalaSyntaxParser'),
  ksql: () => import(/* webpackChunkName: "ksql-parser" */ './ksql/ksqlSyntaxParser'),
  phoenix: () => import(/* webpackChunkName: "phoenix-parser" */ './phoenix/phoenixSyntaxParser'),
  presto: () => import(/* webpackChunkName: "presto-parser" */ './presto/prestoSyntaxParser'),
  sparksql: () =>
    import(/* webpackChunkName: "sparksql-parser" */ './sparksql/sparksqlSyntaxParser')
};

export class SqlParserRepository implements SqlParserProvider {
  modulePromises: { [dialect: string]: Promise<AutocompleteParser | SyntaxParser> } = {};

  async getParser(dialect: string, parserType: string): Promise<AutocompleteParser | SyntaxParser> {
    if (!this.modulePromises[dialect + parserType]) {
      const modules = <{ [dialect: string]: () => unknown }>(
        (parserType === 'Autocomplete' ? AUTOCOMPLETE_MODULES : SYNTAX_MODULES)
      );
      const targetModule = <() => Promise<{ default: SyntaxParser | AutocompleteParser }>>(
        (modules[dialect] || modules.generic)
      );

      this.modulePromises[dialect + parserType] = new Promise((resolve, reject) => {
        targetModule()
          .then(module => resolve(module.default))
          .catch(reject);
      });
    }
    return this.modulePromises[dialect + parserType];
  }

  async getAutocompleteParser(dialect: string): Promise<AutocompleteParser> {
    const autocompleteParser = await this.getParser(dialect, 'Autocomplete');
    return <AutocompleteParser>autocompleteParser;
  }

  async getSyntaxParser(dialect: string): Promise<SyntaxParser> {
    const syntaxParser = await this.getParser(dialect, 'Syntax');
    return <SyntaxParser>syntaxParser;
  }
}

const sqlParserRepository = new SqlParserRepository();

export default sqlParserRepository;
