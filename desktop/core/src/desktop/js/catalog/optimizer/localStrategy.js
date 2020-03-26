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

import BaseStrategy from './baseStrategy';
import dataCatalog from 'catalog/dataCatalog';
import sqlAutocompleteParser from 'parse/sql/hive/hiveAutocompleteParser';

export default class LocalStrategy extends BaseStrategy {
  analyzeRisk(options) {
    const snippet = JSON.parse(options.snippetJson);

    const beforeCursor = snippet.statement + ' '; // Note trailing space
    const afterCursor = '';
    const dialect = snippet.dialect;
    const debug = false;

    const hasLimit =
      sqlAutocompleteParser
        .parseSql(beforeCursor, afterCursor, dialect, debug)
        .locations.filter(token => {
          return token.type == 'limitClause' && !token.missing;
        }).length > 0;

    const deferred = $.Deferred();

    deferred.resolve({
      status: 0,
      message: '',
      query_complexity: {
        hints: !hasLimit
          ? [
              {
                riskTables: [],
                riskAnalysis: 'Query has no limits',
                riskId: 22, // To change
                risk: 'low',
                riskRecommendation: 'Append a limit clause to reduce size of the result set'
              }
            ]
          : [],
        noStats: true,
        noDDL: false
      }
    });

    return deferred.promise();
  }

  fetchTopJoins(options) {
    const path = options.paths[0].join('.');
    const deferred = $.Deferred();

    dataCatalog
      .getEntry({
        sourceType: self.connector ? self.connector.type : '9',
        connector: self.connector,
        path: path,
        namespace: { id: 'default' }
      })
      .then(entry => {
        if (!entry.sourceMeta) {
          entry.sourceMeta = { foreign_keys: [] };
        }
        const data = {
          values: entry.sourceMeta.foreign_keys.map(key => ({
            totalTableCount: 22,
            totalQueryCount: 3,
            joinCols: [{ columns: [path + '.' + key.name, key.to] }],
            tables: [path].concat(key.to.split('.', 2).join('.')),
            joinType: 'join'
          }))
        };
        deferred.resolve(data);
      });
    return deferred.promise();
  }
}
