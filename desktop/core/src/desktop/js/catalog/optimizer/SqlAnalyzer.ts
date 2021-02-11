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
import { TopAggs, TopColumns, TopFilters, TopJoins, TopJoinValue } from 'catalog/MultiTableEntry';
import ApiStrategy from 'catalog/optimizer/ApiStrategy';
import {
  API_STRATEGY,
  CompatibilityOptions,
  MetaOptions,
  Optimizer,
  OptimizerRisk,
  PopularityOptions,
  PredictOptions,
  PredictResponse,
  RiskHint,
  RiskOptions,
  SimilarityOptions
} from 'catalog/optimizer/optimizer';

import dataCatalog, { OptimizerResponse } from 'catalog/dataCatalog';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { Connector, Namespace } from 'types/config';
import { hueWindow } from 'types/types';
import I18n from 'utils/i18n';

export default class SqlAnalyzer implements Optimizer {
  apiStrategy: ApiStrategy;
  connector: Connector;

  constructor(connector: Connector) {
    this.apiStrategy = new ApiStrategy(connector);
    this.connector = connector;
  }

  analyzeRisk(options: RiskOptions): CancellablePromise<OptimizerRisk> {
    return new CancellablePromise<OptimizerRisk>(async (resolve, reject, onCancel) => {
      if (!this.connector.dialect) {
        reject();
        return;
      }

      const apiPromise = this.apiStrategy.analyzeRisk({ ...options, silenceErrors: true });

      onCancel(() => {
        apiPromise.cancel();
      });

      const snippet = JSON.parse(options.snippetJson);
      const missingLimit = await this.checkMissingLimit(snippet.statement, this.connector.dialect);

      const hints: RiskHint[] = missingLimit
        ? [
            {
              riskTables: [],
              riskAnalysis: I18n('Query has no limit'),
              riskId: 17,
              risk: 'low',
              riskRecommendation: I18n('Append a limit clause to reduce the size of the result set')
            }
          ]
        : [];

      const isSelectStar = await this.checkSelectStar(snippet.statement, this.connector.dialect);
      if (isSelectStar) {
        hints.push({
          riskTables: [],
          riskAnalysis: I18n('Query doing a SELECT *'), // Could be triggered only if column number > 10 (todo in Validator API)
          riskId: 18,
          risk: 'low',
          riskRecommendation: I18n('Select only a subset of columns instead of all of them')
        });
      }

      try {
        const apiResponse = await apiPromise;
        if (apiResponse.query_complexity && apiResponse.query_complexity.hints) {
          hints.push(...apiResponse.query_complexity.hints);
        }
      } catch (err) {}

      resolve({
        status: 0,
        message: '',
        query_complexity: {
          hints,
          noStats: true,
          noDDL: false
        }
      });
    });
  }

  async checkMissingLimit(statement: string, dialect: string): Promise<boolean> {
    const autocompleter = await sqlParserRepository.getAutocompleteParser(dialect);
    let parsedStatement;
    try {
      parsedStatement = autocompleter.parseSql(statement + ' ', '');
    } catch (err) {
      return false;
    }

    return (
      parsedStatement.locations.some(
        location => location.type === 'statementType' && location.identifier === 'SELECT'
      ) &&
      parsedStatement.locations.some(location => location.type === 'table') &&
      parsedStatement.locations.some(
        location => location.type === 'limitClause' && location.missing
      )
    );
  }

  async checkSelectStar(statement: string, dialect: string): Promise<boolean> {
    const autocompleter = await sqlParserRepository.getAutocompleteParser(dialect);
    let parsedStatement;
    try {
      parsedStatement = autocompleter.parseSql(statement + ' ', '');
    } catch (err) {
      return false;
    }

    return (
      parsedStatement.locations.some(
        location => location.type === 'statementType' && location.identifier === 'SELECT'
      ) &&
      parsedStatement.locations.some(
        location => location.type === 'selectList' && !location.missing
      ) &&
      parsedStatement.locations.some(location => location.type === 'asterisk')
    );
  }

  fetchTopJoins(options: PopularityOptions): CancellablePromise<TopJoins> {
    const apiPromise = this.apiStrategy.fetchTopJoins(options);

    const path = options.paths[0].join('.');

    return new CancellablePromise<TopJoins>((resolve, reject, onCancel) => {
      contextCatalog
        .getNamespaces({ connector: this.connector, silenceErrors: !options.silenceErrors })
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

          const sourceMetaPromise = entry.getSourceMeta(options);

          onCancel(() => {
            apiPromise.cancel();
            sourceMetaPromise.cancel();
          });

          try {
            const sourceMeta = await sourceMetaPromise;
            const values: TopJoinValue[] = ((<TableSourceMeta>sourceMeta).foreign_keys || []).map(
              key => ({
                totalTableCount: 22,
                totalQueryCount: 3,
                joinCols: [{ columns: [path + '.' + key.name, key.to] }],
                tables: [path].concat(key.to.split('.', 2).join('.')),
                joinType: 'join'
              })
            );

            try {
              const apiResponse = await apiPromise;
              values.push(...apiResponse.values);
            } catch (err) {}

            resolve({ values });
          } catch (err) {
            reject(err);
          }
        })
        .catch(reject);
    });
  }

  analyzeCompatibility(options: CompatibilityOptions): CancellablePromise<unknown> {
    if ((<hueWindow>window).OPTIMIZER_MODE === API_STRATEGY) {
      return this.apiStrategy.analyzeCompatibility(options);
    }
    return CancellablePromise.reject('analyzeCompatibility is not Implemented');
  }

  analyzeSimilarity(options: SimilarityOptions): CancellablePromise<unknown> {
    if ((<hueWindow>window).OPTIMIZER_MODE === API_STRATEGY) {
      return this.apiStrategy.analyzeSimilarity(options);
    }
    return CancellablePromise.reject('analyzeSimilarity is not Implemented');
  }

  fetchOptimizerMeta(options: MetaOptions): CancellablePromise<OptimizerMeta> {
    if ((<hueWindow>window).OPTIMIZER_MODE === API_STRATEGY) {
      return this.apiStrategy.fetchOptimizerMeta(options);
    }
    return CancellablePromise.reject('fetchOptimizerMeta is not Implemented');
  }

  fetchPopularity(options: PopularityOptions): CancellablePromise<OptimizerResponse> {
    if ((<hueWindow>window).OPTIMIZER_MODE === API_STRATEGY) {
      return this.apiStrategy.fetchPopularity(options);
    }
    return CancellablePromise.reject('fetchPopularity is not Implemented');
  }

  fetchTopAggs(options: PopularityOptions): CancellablePromise<TopAggs> {
    if ((<hueWindow>window).OPTIMIZER_MODE === API_STRATEGY) {
      return this.apiStrategy.fetchTopAggs(options);
    }
    return CancellablePromise.reject('fetchTopAggs is not Implemented');
  }

  fetchTopColumns(options: PopularityOptions): CancellablePromise<TopColumns> {
    if ((<hueWindow>window).OPTIMIZER_MODE === API_STRATEGY) {
      return this.apiStrategy.fetchTopColumns(options);
    }
    return CancellablePromise.reject('fetchTopColumns is not Implemented');
  }

  fetchTopFilters(options: PopularityOptions): CancellablePromise<TopFilters> {
    if ((<hueWindow>window).OPTIMIZER_MODE === API_STRATEGY) {
      return this.apiStrategy.fetchTopFilters(options);
    }
    return CancellablePromise.reject('fetchTopFilters is not Implemented');
  }

  predict(options: PredictOptions): CancellablePromise<PredictResponse> {
    return this.apiStrategy.predict(options);
  }
}
