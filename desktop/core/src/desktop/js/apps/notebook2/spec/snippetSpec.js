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

import Notebook from '../notebook';
import sessionManager from 'apps/notebook2/execution/sessionManager';

describe('snippet.js', () => {
  const viewModel = {
    editorType: () => 'notebook',
    selectedNotebook: () => undefined,
    availableSnippets: () => ({}),
    editorMode: () => false,
    getSnippetViewSettings: () => ({ sqlDialect: true }),
    isOptimizerEnabled: () => false
  };

  window.HUE_CHARTS = {
    TYPES: {
      BARCHART: 'barchart'
    }
  };

  beforeEach(() => {
    spyOn(sessionManager, 'getSession').and.callFake(() => Promise.resolve());
  });

  it('should serialize a snippet context to JSON', async () => {
    const notebook = new Notebook(viewModel, {});
    const snippet = notebook.addSnippet({ type: 'hive' });

    const snippetContextJSON = snippet.toContextJson();

    const snippetContextRaw = JSON.parse(snippetContextJSON);

    expect(snippetContextRaw.id).toEqual(snippet.id());
    expect(snippetContextRaw.type).toEqual('hive');
  });
});
