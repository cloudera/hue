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

import NoopSqlAnalyzer from './NoopSqlAnalyzer';
import SqlAnalyzer from 'catalog/optimizer/SqlAnalyzer';
import { CancellablePromise } from 'api/cancellablePromise';
import { OptimizerResponse } from 'catalog/dataCatalog';
import { OptimizerMeta } from 'catalog/DataCatalogEntry';
import { TopAggs, TopColumns, TopFilters, TopJoins } from 'catalog/MultiTableEntry';
import { Connector } from 'types/config';
import { hueWindow } from 'types/types';

export interface CompatibilityOptions {
  notebookJson: string;
  snippetJson: string;
  sourcePlatform: string;
  targetPlatform: string;
  silenceErrors?: boolean;
}

export interface RiskOptions {
  notebookJson: string;
  snippetJson: string;
  silenceErrors?: boolean;
}

export interface RiskHint {
  riskTables: unknown[];
  riskAnalysis: string;
  riskId: number;
  risk: string;
  riskRecommendation: string;
}

export interface OptimizerRisk {
  status: number;
  message: string;
  query_complexity: {
    hints: RiskHint[];
    noStats: boolean;
    noDDL: boolean;
  };
}

export interface SimilarityOptions {
  notebookJson: string;
  snippetJson: string;
  sourcePlatform: string;
  silenceErrors?: boolean;
}

export interface PopularityOptions {
  paths: string[][];
  silenceErrors?: boolean;
}

export interface MetaOptions {
  path: string[];
  silenceErrors?: boolean;
}

export interface PredictOptions {
  beforeCursor: string;
  afterCursor: string;
}

export interface PredictResponse {
  prediction?: string;
}

export interface Optimizer {
  analyzeRisk(options: RiskOptions): CancellablePromise<OptimizerRisk>;
  analyzeSimilarity(options: SimilarityOptions): CancellablePromise<unknown>;
  analyzeCompatibility(options: CompatibilityOptions): CancellablePromise<unknown>;
  fetchPopularity(options: PopularityOptions): CancellablePromise<OptimizerResponse>;
  fetchTopAggs(options: PopularityOptions): CancellablePromise<TopAggs>;
  fetchTopColumns(options: PopularityOptions): CancellablePromise<TopColumns>;
  fetchTopFilters(options: PopularityOptions): CancellablePromise<TopFilters>;
  fetchTopJoins(options: PopularityOptions): CancellablePromise<TopJoins>;
  fetchOptimizerMeta(options: MetaOptions): CancellablePromise<OptimizerMeta>;
  predict(options: PredictOptions): CancellablePromise<PredictResponse>;
}

const optimizerInstances: { [connectorId: string]: Optimizer | undefined } = {};

export const LOCAL_STRATEGY = 'local';
export const API_STRATEGY = 'api';

const createOptimizer = (connector: Connector): Optimizer => {
  // TODO: Remove window.OPTIMIZER_MODE and hardcoded { optimizer: 'api' } when 'connector.optimizer_mode' works.
  if (
    (<hueWindow>window).OPTIMIZER_MODE === LOCAL_STRATEGY ||
    (<hueWindow>window).OPTIMIZER_MODE === API_STRATEGY
  ) {
    return new SqlAnalyzer(connector);
  }
  return new NoopSqlAnalyzer();
};

export const getOptimizer = (connector: Connector): Optimizer => {
  let optimizer = optimizerInstances[connector.id];
  if (!optimizer) {
    optimizer = createOptimizer(connector);
    optimizerInstances[connector.id] = optimizer;
  }
  return optimizer;
};
