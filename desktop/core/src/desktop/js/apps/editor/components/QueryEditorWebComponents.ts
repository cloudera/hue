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

import ExecutableProgressBar from './ExecutableProgressBar.vue';
import QueryHistoryTable from './QueryHistoryTable.vue';
import AceEditor from './aceEditor/AceEditor.vue';
import ResultTable from './result/ResultTable.vue';
import Executor, { ExecutorOptions } from '../execution/executor';
import { setBaseUrl, setBearerToken } from 'api/utils';
import ExecuteButton from 'apps/editor/components/ExecuteButton.vue';
import ExecuteLimitInput from 'apps/editor/components/ExecuteLimitInput.vue';
import SqlAssistPanel from 'components/assist/SqlAssistPanel.vue';
import HueIcons from 'components/icons/HueIcons.vue';
import SqlContextSelector from 'components/SqlContextSelector.vue';
import { getNamespaces } from 'catalog/contextCatalog';
import dataCatalog from 'catalog/dataCatalog';
import { findEditorConnector, refreshConfig } from 'config/hueConfig';
import { Connector } from 'config/types';
import { wrap } from 'vue/webComponentWrap';
import 'utils/json.bigDataParse';

wrap('hue-icons', HueIcons);
wrap('query-editor', AceEditor);
wrap('query-editor-execute-button', ExecuteButton);
wrap('query-editor-history-table', QueryHistoryTable);
wrap('query-editor-limit-input', ExecuteLimitInput);
wrap('query-editor-progress-bar', ExecutableProgressBar);
wrap('query-editor-result-table', ResultTable);
wrap('sql-assist-panel', SqlAssistPanel);
wrap('sql-context-selector', SqlContextSelector);

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

export default {
  clearContextCatalogCache,
  configure,
  createExecutor,
  dataCatalog,
  findEditorConnector,
  getNamespaces,
  refreshConfig,
  setBaseUrl,
  setBearerToken
};
