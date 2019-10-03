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

import komapping from 'knockout.mapping';

export const snippetToContextJSON = snippet =>
  JSON.stringify({
    id: snippet.id(),
    type: snippet.type(),
    status: snippet.status(),
    statementType: snippet.statementType(),
    statement: snippet.statement(),
    aceCursorPosition: snippet.aceCursorPosition(),
    statementPath: snippet.statementPath(),
    associatedDocumentUuid: snippet.associatedDocumentUuid(),
    properties: komapping.toJS(snippet.properties), // TODO: Drop komapping
    result: {}, // TODO: Moved to executor but backend requires it
    database: snippet.database(),
    compute: snippet.compute(),
    wasBatchExecuted: snippet.wasBatchExecuted()
  });

export const notebookToContextJSON = notebook =>
  JSON.stringify({
    id: notebook.id(),
    isSaved: notebook.isSaved(),
    name: notebook.name(),
    parentSavedQueryUuid: notebook.parentSavedQueryUuid(),
    type: notebook.type(),
    uuid: notebook.uuid()
  });

export const notebookToJSON = notebook =>
  JSON.stringify({
    coordinatorUuid: notebook.coordinatorUuid(),
    description: notebook.description(),
    directoryUuid: notebook.directoryUuid(),
    executingAllIndex: notebook.executingAllIndex(),
    id: notebook.id(),
    isExecutingAll: notebook.isExecutingAll(),
    isHidingCode: notebook.isHidingCode(),
    isHistory: notebook.isHistory(),
    isManaged: notebook.isManaged(),
    isPresentationModeDefault: notebook.isPresentationModeDefault(),
    isSaved: notebook.isSaved(),
    name: notebook.name(),
    onSuccessUrl: notebook.onSuccessUrl(),
    parentSavedQueryUuid: notebook.parentSavedQueryUuid(),
    presentationSnippets: notebook.presentationSnippets(),
    pubSubUrl: notebook.pubSubUrl(),
    result: {}, // TODO: Moved to executor but backend requires it
    sessions: [], // TODO: Moved to executor but backend requires it
    snippets: notebook.snippets().map(snippet => ({
      aceCursorPosition: snippet.aceCursorPosition(),
      aceSize: snippet.aceSize(),
      associatedDocumentUuid: snippet.associatedDocumentUuid(),
      // chartLimit: snippet.chartLimit(), // TODO: Move somewhere else
      // chartMapHeat: snippet.chartMapHeat(), // TODO: Move somewhere else
      // chartMapLabel: snippet.chartMapLabel(), // TODO: Move somewhere else
      // chartMapType: snippet.chartMapType(), // TODO: Move somewhere else
      // chartScatterGroup: snippet.chartScatterGroup(), // TODO: Move somewhere else
      // chartScatterSize: snippet.chartScatterSize(), // TODO: Move somewhere else
      // chartScope: snippet.chartScope(), // TODO: Move somewhere else
      // chartSorting: snippet.chartSorting(), // TODO: Move somewhere else
      // chartTimelineType: snippet.chartTimelineType(), // TODO: Move somewhere else
      //
      // $.extend(
      //   snippet,
      //   snippet.chartType === 'lines' && {
      //     // Retire line chart
      //     chartType: 'bars',
      //     chartTimelineType: 'line'
      //   }
      // );
      //
      // chartType: snippet.chartType(), // TODO: Move somewhere else
      // chartX: snippet.chartX(), // TODO: Move somewhere else
      // chartXPivot: snippet.chartXPivot(), // TODO: Move somewhere else
      // chartYMulti: snippet.chartYMulti(), // TODO: Move somewhere else
      // chartYSingle: snippet.chartYSingle(), // TODO: Move somewhere else
      compute: snippet.compute(),
      currentQueryTab: snippet.currentQueryTab(),
      database: snippet.database(),
      id: snippet.id(),
      is_redacted: snippet.is_redacted(),
      //isResultSettingsVisible: snippet.isResultSettingsVisible(), // TODO: Move somewhere else
      lastAceSelectionRowOffset: snippet.lastAceSelectionRowOffset(),
      lastExecuted: snippet.lastExecuted(),
      name: snippet.name(),
      namespace: snippet.namespace(),
      pinnedContextTabs: snippet.pinnedContextTabs(),
      properties: komapping.toJS(snippet.properties), // TODO: Drop komapping
      // result: ...,
      settingsVisible: snippet.settingsVisible(),
      // schedulerViewModel: ?
      // showChart: snippet.showChart(), // TODO: Move somewhere else
      // showGrid: snippet.showGrid(), // TODO: Move somewhere else
      showLogs: snippet.showLogs(),
      statement_raw: snippet.statement_raw(),
      statementPath: snippet.statementPath(),
      statementType: snippet.statementType(),
      status: snippet.status(),
      type: snippet.type(),
      variables: snippet.variables().map(variable => ({
        meta: variable.meta && {
          options: variable.meta.options && variable.meta.options(), // TODO: Map?
          placeHolder: variable.meta.placeHolder && variable.meta.placeHolder(),
          type: variable.meta.type && variable.meta.type()
        },
        name: variable.name(),
        path: variable.path(),
        sample: variable.sample(),
        sampleUser: variable.sampleUser(),
        step: variable.step(),
        type: variable.type(),
        value: variable.value()
      })),
      wasBatchExecuted: snippet.wasBatchExecuted()
    })),
    type: notebook.type(),
    uuid: notebook.uuid(),
    viewSchedulerId: notebook.viewSchedulerId()
  });
