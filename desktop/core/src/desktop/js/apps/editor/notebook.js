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

import $ from 'jquery';
import * as ko from 'knockout';
import komapping from 'knockout.mapping';

import apiHelper from 'api/apiHelper';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import sessionManager from 'apps/editor/execution/sessionManager';

import Snippet, { STATUS as SNIPPET_STATUS } from 'apps/editor/snippet';
import { HISTORY_CLEARED_EVENT } from 'apps/editor/components/ko.queryHistory';
import { UPDATE_SAVED_QUERIES_EVENT } from 'apps/editor/components/ko.savedQueries';
import {
  ASSIST_DB_PANEL_IS_READY_EVENT,
  ASSIST_IS_DB_PANEL_READY_EVENT,
  ASSIST_SET_DATABASE_EVENT
} from 'ko/components/assist/events';

export default class Notebook {
  constructor(vm, notebookRaw) {
    this.parentVm = vm;
    this.id = ko.observable(notebookRaw.id);
    this.uuid = ko.observable(notebookRaw.uuid || hueUtils.UUID());
    this.name = ko.observable(notebookRaw.name || '');
    this.description = ko.observable(notebookRaw.description || '');
    this.type = ko.observable(notebookRaw.type || 'notebook');
    this.initialType = this.type().replace('query-', '');
    this.coordinatorUuid = ko.observable(notebookRaw.coordinatorUuid);
    this.isHistory = ko.observable(!!notebookRaw.is_history);
    this.isManaged = ko.observable(!!notebookRaw.isManaged);
    this.parentSavedQueryUuid = ko.observable(notebookRaw.parentSavedQueryUuid); // History parent
    this.isSaved = ko.observable(!!notebookRaw.isSaved);
    this.canWrite = ko.observable(notebookRaw.can_write !== false);
    this.onSuccessUrl = ko.observable(notebookRaw.onSuccessUrl);
    this.pubSubUrl = ko.observable(notebookRaw.pubSubUrl);

    this.isPresentationModeDefault = ko.observable(!!notebookRaw.isPresentationModeDefault);
    this.isPresentationMode = ko.observable(false);

    this.isHidingCode = ko.observable(!!notebookRaw.isHidingCode);

    this.snippets = ko.observableArray();
    this.selectedSnippet = ko.observable(vm.editorType()); // Aka selectedSnippetType
    this.directoryUuid = ko.observable(notebookRaw.directoryUuid);
    this.dependents = komapping.fromJS(notebookRaw.dependents || []);
    this.dependentsCoordinator = ko.pureComputed(() =>
      this.dependents().filter(doc => doc.type() === 'oozie-coordinator2' && doc.is_managed())
    );
    if (this.dependentsCoordinator().length > 0 && !this.coordinatorUuid()) {
      this.coordinatorUuid(this.dependentsCoordinator()[0].uuid());
    }
    this.history = ko.observableArray(
      vm.selectedNotebook() &&
        vm.selectedNotebook().history().length > 0 &&
        vm.selectedNotebook().history()[0].type === this.type()
        ? vm.selectedNotebook().history()
        : []
    );

    this.schedulerViewModel = null;
    this.schedulerViewModelIsLoaded = ko.observable(false);
    this.schedulerViewerViewModel = ko.observable();
    this.isBatchable = ko.pureComputed(
      () => this.snippets().length > 0 && this.snippets().every(snippet => snippet.isBatchable())
    );

    this.isExecutingAll = ko.observable(!!notebookRaw.isExecutingAll);

    this.executingAllIndex = ko.observable(notebookRaw.executingAllIndex || 0);

    this.retryModalConfirm = null;
    this.retryModalCancel = null;

    this.avoidClosing = false;

    this.canSave = vm.canSave;

    this.unloaded = ko.observable(false);

    this.viewSchedulerId = ko.observable(notebookRaw.viewSchedulerId || '');
    this.viewSchedulerId.subscribe(() => {
      this.save();
    });
    this.isSchedulerJobRunning = ko.observable();
    this.loadingScheduler = ko.observable(false);

    // Init
    if (notebookRaw.snippets) {
      notebookRaw.snippets.forEach(snippetRaw => {
        this.addSnippet(snippetRaw);
      });
    }

    huePubSub.subscribe(HISTORY_CLEARED_EVENT, () => {
      if (this.isHistory()) {
        this.id(null);
        this.uuid(hueUtils.UUID());
        this.parentVm.changeURL(this.parentVm.URLS.editor + '?type=' + this.parentVm.editorType());
      }
    });

    huePubSub.subscribeOnce(
      ASSIST_DB_PANEL_IS_READY_EVENT,
      () => {
        if (this.type().indexOf('query') === 0) {
          const whenDatabaseAvailable = snippet => {
            huePubSub.publish(ASSIST_SET_DATABASE_EVENT, {
              connector: snippet.connector(),
              namespace: snippet.namespace(),
              name: snippet.database()
            });
          };

          const whenNamespaceAvailable = snippet => {
            if (snippet.database()) {
              whenDatabaseAvailable(snippet);
            } else {
              const databaseSub = snippet.database.subscribe(() => {
                databaseSub.dispose();
                whenDatabaseAvailable(snippet);
              });
            }
          };

          const whenSnippetAvailable = snippet => {
            if (snippet.namespace()) {
              whenNamespaceAvailable(snippet);
            } else {
              const namespaceSub = snippet.namespace.subscribe(() => {
                namespaceSub.dispose();
                whenNamespaceAvailable(snippet);
              });
            }
          };

          if (this.snippets().length === 1) {
            whenSnippetAvailable(this.snippets()[0]);
          } else {
            const snippetsSub = this.snippets.subscribe(snippets => {
              if (snippets.length === 1) {
                whenSnippetAvailable(snippets[0]);
              }
              snippetsSub.dispose();
            });
          }
        }
      },
      vm.huePubSubId
    );

    huePubSub.publish(ASSIST_IS_DB_PANEL_READY_EVENT);
  }

  addSnippet(snippetRaw) {
    const newSnippet = new Snippet(this.parentVm, this, snippetRaw);
    this.snippets.push(newSnippet);
    newSnippet.init();
    return newSnippet;
  }

  clearResults() {
    this.snippets().forEach(snippet => {
      snippet.result.clear();
      snippet.status(SNIPPET_STATUS.ready);
    });
  }

  async close() {
    hueAnalytics.log('notebook', 'close');
    apiHelper.closeNotebook({
      notebookJson: await this.toJson(),
      editorMode: this.parentVm.editorMode()
    });
  }

  executeAll() {
    if (this.isExecutingAll() || this.snippets().length === 0) {
      return;
    }

    this.isExecutingAll(true);
    this.executingAllIndex(0);

    this.snippets()[this.executingAllIndex()].execute();
  }

  getSnippets(type) {
    return this.snippets().filter(snippet => snippet.dialect() === type);
  }

  loadScheduler() {
    if (typeof this.parentVm.CoordinatorEditorViewModel !== 'undefined' && this.isBatchable()) {
      let action;
      if (this.coordinatorUuid()) {
        action = 'edit';
      } else {
        action = 'new';
      }
      hueAnalytics.log('notebook', 'schedule/' + action);

      const getCoordinator = () => {
        $.get(
          '/scheduler/api/schedule/' + action + '/',
          {
            format: 'json',
            document: this.uuid(),
            coordinator: this.coordinatorUuid()
          },
          data => {
            if ($('#schedulerEditor').length > 0) {
              huePubSub.publish('hue4.process.headers', {
                response: data.layout,
                callback: r => {
                  const $schedulerEditor = $('#schedulerEditor');
                  $schedulerEditor.html(r);

                  this.schedulerViewModel = new this.parentVm.CoordinatorEditorViewModel(
                    data.coordinator,
                    data.credentials,
                    data.workflows,
                    data.can_edit
                  );

                  ko.cleanNode($schedulerEditor[0]);
                  ko.applyBindings(this.schedulerViewModel, $schedulerEditor[0]);
                  $(document).off('showSubmitPopup');
                  $(document).on('showSubmitPopup', (event, data) => {
                    const $submitModalEditor = $('.submit-modal-editor');
                    $submitModalEditor.html(data);
                    $submitModalEditor.modal('show');
                    $submitModalEditor.on('hidden', () => {
                      huePubSub.publish('hide.datepicker');
                    });
                    const _sel = $('.submit-form .control-group[rel!="popover"]:visible');
                    if (_sel.length > 0) {
                      const $submitModalEditorBody = $('.submit-modal-editor .modal-body');
                      $submitModalEditorBody.height($submitModalEditorBody.height() + 60);
                    }
                  });

                  huePubSub.publish('render.jqcron');

                  this.schedulerViewModel.coordinator.properties.cron_advanced.valueHasMutated(); // Update jsCron enabled status
                  this.schedulerViewModel.coordinator.tracker().markCurrentStateAsClean();
                  this.schedulerViewModel.isEditing(true);

                  this.schedulerViewModelIsLoaded(true);

                  if (action === 'new') {
                    this.schedulerViewModel.coordinator.properties.document(this.uuid()); // Expected for triggering the display
                  }
                }
              });
            }
          }
        ).fail(xhr => {
          if (xhr.status !== 502) {
            $(document).trigger('error', xhr.responseText);
          }
        });
      };

      getCoordinator();
    }
  }

  newSnippet(type) {
    if (type) {
      this.selectedSnippet(type);
    }
    const snippet = this.addSnippet({
      type: this.selectedSnippet(),
      result: {}
    });

    window.setTimeout(() => {
      const lastSnippet = snippet;
      if (lastSnippet.ace() != null) {
        lastSnippet.ace().focus();
      }
    }, 100);

    hueAnalytics.log('notebook', 'add_snippet/' + (type ? type : this.selectedSnippet()));
    return snippet;
  }

  newSnippetAbove(id) {
    this.newSnippet();
    let idx = 0;
    this.snippets().forEach((snippet, cnt) => {
      if (snippet.id() === id) {
        idx = cnt;
      }
    });
    this.snippets(this.snippets().move(this.snippets().length - 1, idx));
  }

  async save(callback) {
    hueAnalytics.log('notebook', 'save');

    const editorMode =
      this.parentVm.editorMode() ||
      (this.isPresentationMode() && this.parentVm.editorType() !== 'notebook'); // Editor should not convert to Notebook in presentation mode

    try {
      const data = await apiHelper.saveNotebook({
        notebookJson: await this.toJson(),
        editorMode: editorMode
      });

      if (data.status === 0) {
        this.id(data.id);
        this.isSaved(true);
        const wasHistory = this.isHistory();
        this.isHistory(false);
        $(document).trigger('info', data.message);
        if (editorMode) {
          huePubSub.publish(UPDATE_SAVED_QUERIES_EVENT, data);

          if (data.save_as) {
            huePubSub.publish('assist.document.refresh');
          }
          if (this.coordinatorUuid() && this.schedulerViewModel) {
            this.saveScheduler();
            this.schedulerViewModel.coordinator.refreshParameters();
          }
          if (wasHistory || data.save_as) {
            this.loadScheduler();
          }

          if (
            this.snippets()[0].downloadResultViewModel &&
            this.snippets()[0].downloadResultViewModel().saveTarget() === 'dashboard'
          ) {
            huePubSub.publish(
              'open.link',
              this.parentVm.URLS.report +
                '&uuid=' +
                data.uuid +
                '&statement=' +
                this.snippets()[0].result.handle().statement_id
            );
          } else {
            this.parentVm.changeURL(this.parentVm.URLS.editor + '?editor=' + data.id);
          }
        } else {
          this.parentVm.changeURL(this.parentVm.URLS.notebook + '?notebook=' + data.id);
        }
        if (typeof callback == 'function') {
          callback();
        }
      } else {
        $(document).trigger('error', data.message);
      }
    } catch (err) {
      console.error(err);
      if (err && err.status !== 502) {
        $(document).trigger('error', err.responseText);
      }
    }
  }

  saveScheduler() {
    if (
      this.isBatchable() &&
      (!this.coordinatorUuid() || this.schedulerViewModel.coordinator.isDirty())
    ) {
      this.schedulerViewModel.coordinator.isManaged(true);
      this.schedulerViewModel.coordinator.properties.document(this.uuid());
      this.schedulerViewModel.save(data => {
        if (!this.coordinatorUuid()) {
          this.coordinatorUuid(data.uuid);
          this.save();
        }
      });
    }
  }

  showSubmitPopup() {
    $.get(
      '/scheduler/api/submit/' + this.coordinatorUuid(),
      {
        format: 'json'
      },
      data => {
        $(document).trigger('showSubmitPopup', data);
      }
    ).fail(xhr => {
      if (xhr.status !== 502) {
        $(document).trigger('error', xhr.responseText);
      }
    });
  }

  async toContextJson() {
    return JSON.stringify({
      id: this.id(),
      isSaved: this.isSaved(),
      name: this.name(),
      parentSavedQueryUuid: this.parentSavedQueryUuid(),
      sessions: await sessionManager.getAllSessions(),
      type: this.type(),
      uuid: this.uuid()
    });
  }

  async toJs() {
    return {
      coordinatorUuid: this.coordinatorUuid(),
      description: this.description(),
      directoryUuid: this.directoryUuid(),
      executingAllIndex: this.executingAllIndex(),
      id: this.id(),
      isExecutingAll: this.isExecutingAll(),
      isHidingCode: this.isHidingCode(),
      isHistory: this.isHistory(),
      isManaged: this.isManaged(),
      isPresentationModeDefault: this.isPresentationModeDefault(),
      isSaved: this.isSaved(),
      name: this.name(),
      onSuccessUrl: this.onSuccessUrl(),
      parentSavedQueryUuid: this.parentSavedQueryUuid(),
      pubSubUrl: this.pubSubUrl(),
      result: {}, // TODO: Moved to executor but backend requires it
      sessions: await sessionManager.getAllSessions(),
      snippets: this.snippets().map(snippet => snippet.toJs()),
      type: this.type(),
      uuid: this.uuid(),
      viewSchedulerId: this.viewSchedulerId()
    };
  }

  async toJson() {
    return JSON.stringify(await this.toJs());
  }

  unload() {
    this.unloaded(true);
    let currentQueries = null;
    this.snippets().forEach(snippet => {
      if (snippet.checkStatusTimeout != null) {
        clearTimeout(snippet.checkStatusTimeout);
        snippet.checkStatusTimeout = null;
      }
      if (currentQueries == null) {
        currentQueries = snippet.queries();
      }
    });
    return currentQueries;
  }
}
