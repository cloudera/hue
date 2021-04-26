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
import MixedSqlAnalyzer from './MixedSqlAnalyzer';
import { Connector } from 'config/types';
import { hueWindow } from 'types/types';
import { SqlAnalyzer, SqlAnalyzerProvider, SqlAnalyzerMode } from './types';

const sqlAnalyzerInstances: { [connectorId: string]: SqlAnalyzer | undefined } = {};

const createSqlAnalyzer = (connector: Connector): SqlAnalyzer => {
  // TODO: Remove window.SQL_ANALYZER_MODE and hardcoded { optimizer: 'api' } when 'connector.optimizer_mode' works.
  if (
    (<hueWindow>window).SQL_ANALYZER_MODE === SqlAnalyzerMode.local ||
    (<hueWindow>window).SQL_ANALYZER_MODE === SqlAnalyzerMode.api
  ) {
    return new MixedSqlAnalyzer(connector);
  }
  return new NoopSqlAnalyzer();
};

export const sqlAnalyzerRepository: SqlAnalyzerProvider = {
  getSqlAnalyzer: (connector: Connector): SqlAnalyzer => {
    let sqlAnalyzer = sqlAnalyzerInstances[connector.id];
    if (!sqlAnalyzer) {
      sqlAnalyzer = createSqlAnalyzer(connector);
      sqlAnalyzerInstances[connector.id] = sqlAnalyzer;
    }
    return sqlAnalyzer;
  }
};
