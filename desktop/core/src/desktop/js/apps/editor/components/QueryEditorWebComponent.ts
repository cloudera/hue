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
import { wrap } from 'vue/webComponentWrap';

const registerBaseUrl = (element: HTMLElement): void => {
  const hueBaseUrl = element.getAttribute('hue-base-url');
  if (hueBaseUrl) {
    axios.defaults.baseURL = hueBaseUrl;
  }
};

const components = [
  { tag: 'query-editor', component: AceEditor },
  { tag: 'query-editor-actions', component: ExecutableActions },
  { tag: 'query-editor-progress-bar', component: ExecutableProgressBar },
  { tag: 'query-editor-result-table', component: ResultTable }
];

components.forEach(({ tag, component }) => {
  wrap(tag, component, {
    connectedCallback() {
      registerBaseUrl(this as HTMLElement);
    }
  });
});
