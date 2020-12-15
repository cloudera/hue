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

import { CancellablePromise } from 'api/cancellablePromise';
import contextCatalog from 'catalog/contextCatalog';
import { OptimizerMeta, TableSourceMeta } from 'catalog/DataCatalogEntry';
import { TopAggs, TopColumns, TopFilters, TopJoins } from 'catalog/MultiTableEntry';
import {
  CompatibilityOptions,
  MetaOptions,
  Optimizer,
  OptimizerRisk,
  PopularityOptions,
  RiskOptions,
  SimilarityOptions
} from 'catalog/optimizer/optimizer';

import dataCatalog, { OptimizerResponse } from 'catalog/dataCatalog';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { Connector, Namespace } from 'types/config';
import I18n from 'utils/i18n';

export default class LocalStrategy implements Optimizer {
  connector: Connector;

  constructor(connector: Connector) {
    this.connector = connector;
  }

  analyzeRisk(options: RiskOptions): CancellablePromise<OptimizerRisk> {
    const snippet = JSON.parse(options.snippetJson);

    return new CancellablePromise<OptimizerRisk>(async (resolve, reject) => {
      if (!this.connector.dialect) {
        reject();
        return;
      }
      const autocompleter = await sqlParserRepository.getAutocompleteParser(this.connector.dialect);

      const sqlParseResult = autocompleter.parseSql(snippet.statement + ' ', '');

      const hasLimit = sqlParseResult.locations.some(
        location => location.type === 'limitClause' && !location.missing
      );

      resolve({
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
    });
  }

  fetchTopJoins({ paths, silenceErrors }: PopularityOptions): CancellablePromise<TopJoins> {
    const path = paths[0].join('.');

    return new CancellablePromise<TopJoins>((resolve, reject, onCancel) => {
      contextCatalog
        .getNamespaces({ connector: this.connector, silenceErrors: !silenceErrors })
        .then(async (result: { namespaces: Namespace[] }) => {
          if (!result.namespaces.length || !result.namespaces[0].computes.length) {
            reject('No namespace or compute found');
            console.warn(result);
            return;
          }
          const entry = await dataCatalog.getEntry({
            connector: this.connector,
            path: path,
            namespace: result.namespaces[0],
            compute: result.namespaces[0].computes[0]
          });

          const sourceMetaPromise = entry.getSourceMeta({ silenceErrors });

          onCancel(() => {
            sourceMetaPromise.cancel();
          });

          const sourceMeta = await sourceMetaPromise;

          resolve({
            values: ((<TableSourceMeta>sourceMeta).foreign_keys || []).map(key => ({
              totalTableCount: 22,
              totalQueryCount: 3,
              joinCols: [{ columns: [path + '.' + key.name, key.to] }],
              tables: [path].concat(key.to.split('.', 2).join('.')),
              joinType: 'join'
            }))
          });
        })
        .catch(reject);
    });
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  analyzeCompatibility(options: CompatibilityOptions): CancellablePromise<unknown> {
    return CancellablePromise.reject('analyzeCompatibility is not Implemented');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  analyzeSimilarity(options: SimilarityOptions): CancellablePromise<unknown> {
    return CancellablePromise.reject('analyzeSimilarity is not Implemented');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  fetchOptimizerMeta(options: MetaOptions): CancellablePromise<OptimizerMeta> {
    return CancellablePromise.reject('fetchOptimizerMeta is not Implemented');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  fetchPopularity(options: PopularityOptions): CancellablePromise<OptimizerResponse> {
    return CancellablePromise.reject('fetchPopularity is not Implemented');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  fetchTopAggs(options: PopularityOptions): CancellablePromise<TopAggs> {
    return CancellablePromise.reject('fetchTopAggs is not Implemented');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  fetchTopColumns(options: PopularityOptions): CancellablePromise<TopColumns> {
    return CancellablePromise.reject('fetchTopColumns is not Implemented');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  fetchTopFilters(options: PopularityOptions): CancellablePromise<TopFilters> {
    return CancellablePromise.reject('fetchTopFilters is not Implemented');
  }
}
