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

import axios from 'axios';

import AceEditor from './aceEditor/AceEditor.vue';
import ExecutableActions from './ExecutableActions.vue';
import ExecutableProgressBar from './ExecutableProgressBar.vue';
import ResultTable from './result/ResultTable.vue';
import Executor, { ExecutorOptions } from '../execution/executor';
import 'utils/json.bigDataParse';
import { wrap } from 'vue/webComponentWrap';

wrap('query-editor', AceEditor);
wrap('query-editor-actions', ExecutableActions);
wrap('query-editor-progress-bar', ExecutableProgressBar);
wrap('query-editor-result-table', ResultTable);

export interface HueComponentConfig {
  baseUrl?: string;
}

const configure = (config: HueComponentConfig): void => {
  if (config.baseUrl) {
    axios.defaults.baseURL = config.baseUrl;
  }
};

const createExecutor = (options: ExecutorOptions): Executor => new Executor(options);

export default { configure, createExecutor };
