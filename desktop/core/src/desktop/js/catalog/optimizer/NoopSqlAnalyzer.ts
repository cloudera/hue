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
import {
  CompatibilityOptions,
  MetaOptions,
  Optimizer,
  OptimizerRisk,
  PopularityOptions,
  PredictOptions,
  PredictResponse,
  RiskOptions,
  SimilarityOptions
} from 'catalog/optimizer/optimizer';

import { OptimizerResponse } from 'catalog/dataCatalog';

export default class NoopSqlAnalyzer implements Optimizer {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  analyzeCompatibility(options: CompatibilityOptions): CancellablePromise<unknown> {
    return CancellablePromise.reject('analyzeCompatibility is not Implemented');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  analyzeRisk(options: RiskOptions): CancellablePromise<OptimizerRisk> {
    return CancellablePromise.reject('analyzeRisk is not Implemented');
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
    return CancellablePromise.reject('analyzeCompatibility is not Implemented');
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

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  fetchTopJoins(options: PopularityOptions): CancellablePromise<TopJoins> {
    return CancellablePromise.reject('fetchTopJoins is not Implemented');
  }

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  predict(options: PredictOptions): CancellablePromise<PredictResponse> {
    return CancellablePromise.reject('predict is not Implemented');
  }
}
