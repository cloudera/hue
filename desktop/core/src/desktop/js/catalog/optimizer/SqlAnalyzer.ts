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
import { OptimizerMeta } from 'catalog/DataCatalogEntry';
import { TopAggs, TopColumns, TopFilters, TopJoins } from 'catalog/MultiTableEntry';
import ApiStrategy from 'catalog/optimizer/ApiStrategy';
import {
  API_STRATEGY,
  CompatibilityOptions,
  MetaOptions,
  Optimizer,
  OptimizerRisk,
  PopularityOptions,
  RiskOptions,
  SimilarityOptions
} from 'catalog/optimizer/optimizer';

import { OptimizerResponse } from 'catalog/dataCatalog';
import sqlParserRepository from 'parse/sql/sqlParserRepository';
import { Connector } from 'types/config';
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

  fetchTopJoins(options: PopularityOptions): CancellablePromise<TopJoins> {
    return this.apiStrategy.fetchTopJoins(options);
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
}
