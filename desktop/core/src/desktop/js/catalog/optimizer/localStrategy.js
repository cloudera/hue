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
import I18n from 'utils/i18n';

export default class LocalStrategy extends BaseStrategy {
  analyzeRisk(options) {
    const snippet = JSON.parse(options.snippetJson);

    // TODO: Get parser from repository, need to extract SqlFunctions dep first
    // to reduce size of main hue bundle
    // const parser = await sqlParserRepository.getAutocompleter(snippet.dialect);
    const sqlParseResult = sqlAutocompleteParser.parseSql(snippet.statement + ' ', '');

    const hasLimit = sqlParseResult.locations.some(
      location => location.type === 'limitClause' && !location.missing
    );

    const deferred = $.Deferred();
    deferred.resolve({
      status: 0,
      message: '',
      query_complexity: {
        hints: !hasLimit
          ? [
              {
                riskTables: [],
                riskAnalysis: I18n('Query has no limit'),
                riskId: 22, // To change
                risk: 'low',
                riskRecommendation: I18n(
                  'Append a limit clause to reduce the size of the result set'
                )
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
        connector: this.connector,
        path: path,
        namespace: { id: 'default' }
      })
      .then(entry => {
        entry
          .getSourceMeta({ silenceErrors: true })
          .then(() => {
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
          })
          .fail(deferred.reject);
      })
      .fail(deferred.reject);

    return deferred.promise();
  }
}
