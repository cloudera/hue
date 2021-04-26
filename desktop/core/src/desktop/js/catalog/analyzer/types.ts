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
import { Connector } from '../../config/types';
import { SqlAnalyzerResponse } from '../dataCatalog';
import { SqlAnalyzerMeta } from '../DataCatalogEntry';
import { TopAggs, TopColumns, TopFilters, TopJoins } from '../MultiTableEntry';

export enum SqlAnalyzerMode {
  local = 'local',
  api = 'api',
  off = 'off'
}

export interface SqlAnalyzerProvider {
  getSqlAnalyzer(connector: Connector): SqlAnalyzer;
}

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

export interface AnalyzerRisk {
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

export interface SqlAnalyzer {
  analyzeRisk(options: RiskOptions): CancellablePromise<AnalyzerRisk>;
  analyzeSimilarity(options: SimilarityOptions): CancellablePromise<unknown>;
  analyzeCompatibility(options: CompatibilityOptions): CancellablePromise<unknown>;
  fetchPopularity(options: PopularityOptions): CancellablePromise<SqlAnalyzerResponse>;
  fetchTopAggs(options: PopularityOptions): CancellablePromise<TopAggs>;
  fetchTopColumns(options: PopularityOptions): CancellablePromise<TopColumns>;
  fetchTopFilters(options: PopularityOptions): CancellablePromise<TopFilters>;
  fetchTopJoins(options: PopularityOptions): CancellablePromise<TopJoins>;
  fetchSqlAnalyzerMeta(options: MetaOptions): CancellablePromise<SqlAnalyzerMeta>;
  predict(options: PredictOptions): CancellablePromise<PredictResponse>;
}
