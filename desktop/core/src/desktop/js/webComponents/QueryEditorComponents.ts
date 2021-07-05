// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import 'regenerator-runtime/runtime';

import hueIconsDefined from './HueIcons';
import queryEditorDefined from './QueryEditor';
import queryEditorHistoryTableDefined from './QueryEditorHistoryTable';
import queryEditorExecuteButtonDefined from './QueryEditorExecuteButton';
import queryEditorLimitInputDefined from './QueryEditorLimitInput';
import queryEditorResultTableDefined from './QueryEditorResultTable';
import queryEditorProgressBarDefined from './QueryEditorProgressBar';
import sqlContextSelectorDefined from './SqlContextSelector';
import { setBaseUrl, setBearerToken } from 'api/utils';
import Executor, { ExecutorOptions } from 'apps/editor/execution/executor';
import { getNamespaces } from 'catalog/contextCatalog';
import dataCatalog from 'catalog/dataCatalog';
import { findEditorConnector, refreshConfig } from 'config/hueConfig';
import { Connector } from 'config/types';

export interface HueComponentConfig {
  baseUrl?: string;
  bearerToken?: string;
}

const configure = ({ baseUrl, bearerToken }: HueComponentConfig): void => {
  baseUrl && setBaseUrl(baseUrl);
  bearerToken && setBearerToken(bearerToken);
};

const createExecutor = (options: ExecutorOptions): Executor => new Executor(options);

const clearContextCatalogCache = async (connector: Connector): Promise<void> => {
  await getNamespaces({ connector, clearCache: true });
};

const isQueryEditorComponentsDefined = async (): Promise<void> => {
  await Promise.all([
    hueIconsDefined(),
    queryEditorDefined(),
    queryEditorHistoryTableDefined(),
    queryEditorExecuteButtonDefined(),
    queryEditorLimitInputDefined(),
    queryEditorResultTableDefined(),
    queryEditorProgressBarDefined(),
    sqlContextSelectorDefined()
  ]);
};

export default {
  clearContextCatalogCache,
  configure,
  createExecutor,
  dataCatalog,
  findEditorConnector,
  getNamespaces,
  isQueryEditorComponentsDefined,
  refreshConfig,
  setBaseUrl,
  setBearerToken
};
