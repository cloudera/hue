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
import ko from 'knockout';
import komapping from 'knockout.mapping';

import apiHelper from 'api/apiHelper';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import sessionManager from 'apps/notebook2/execution/sessionManager';

import Snippet, { STATUS as SNIPPET_STATUS } from 'apps/notebook2/snippet';

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
    this.isPresentationModeInitialized = ko.observable(false);
    this.isPresentationMode.subscribe(newValue => {
      if (!newValue) {
        this.cancelExecutingAll();
      }
      huePubSub.publish('editor.presentation.operate.toggle', newValue); // Problem with headers / row numbers redraw on full screen results
      vm.togglePresentationMode();
      if (newValue) {
        hueAnalytics.convert('editor', 'presentation');
      }
    });
    this.presentationSnippets = ko.observable({});
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

    // This is to keep the "Saved Query" tab selected when opening a doc from the left assist
    // TODO: Refactor code to reflect purpose
    this.history.subscribe(val => {
      if (
        this.id() == null &&
        val.length === 0 &&
        this.historyFilter() === '' &&
        !vm.isNotificationManager()
      ) {
        this.snippets()[0].currentQueryTab('savedQueries');
      }
    });

    this.historyFilter = ko.observable('');
    this.historyFilterVisible = ko.observable(false);
    this.historyFilter.extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 900 } });
    this.historyFilter.subscribe(() => {
      if (this.historyCurrentPage() !== 1) {
        this.historyCurrentPage(1);
      } else {
        this.fetchHistory();
      }
    });
    this.loadingHistory = ko.observable(this.history().length === 0);
    this.historyInitialHeight = ko.observable(0).extend({ throttle: 1000 });
    this.forceHistoryInitialHeight = ko.observable(false);
    this.historyCurrentPage = ko.observable(
      vm.selectedNotebook() ? vm.selectedNotebook().historyCurrentPage() : 1
    );
    this.historyCurrentPage.subscribe(() => {
      this.fetchHistory();
    });
    this.historyTotalPages = ko.observable(
      vm.selectedNotebook() ? vm.selectedNotebook().historyTotalPages() : 1
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
    this.updateHistoryFailed = false;

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
      if (
        typeof notebookRaw.presentationSnippets != 'undefined' &&
        notebookRaw.presentationSnippets != null
      ) {
        // Load
        $.each(notebookRaw.presentationSnippets, (key, snippet) => {
          snippet.status = 'ready'; // Protect from storm of check_statuses
          const _snippet = new Snippet(vm, this, snippet);
          _snippet.init();
          this.presentationSnippets()[key] = _snippet;
        });
      }
      if (vm.editorMode() && this.history().length === 0) {
        this.fetchHistory(() => {
          this.updateHistory(['starting', 'running'], 30000);
          this.updateHistory(['available'], 60000 * 5);
        });
      }
    }

    huePubSub.subscribeOnce(
      'assist.db.panel.ready',
      () => {
        if (this.type().indexOf('query') === 0) {
          const whenDatabaseAvailable = function(snippet) {
            huePubSub.publish('assist.set.database', {
              source: snippet.type(),
              namespace: snippet.namespace(),
              name: snippet.database()
            });
          };

          const whenNamespaceAvailable = function(snippet) {
            if (snippet.database()) {
              whenDatabaseAvailable(snippet);
            } else {
              const databaseSub = snippet.database.subscribe(() => {
                databaseSub.dispose();
                whenDatabaseAvailable(snippet);
              });
            }
          };

          const whenSnippetAvailable = function(snippet) {
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

    huePubSub.publish('assist.is.db.panel.ready');
  }

  addSnippet(snippetRaw) {
    const newSnippet = new Snippet(this.parentVm, this, snippetRaw);
    this.snippets.push(newSnippet);
    newSnippet.init();
    return newSnippet;
  }

  async clearHistory() {
    hueAnalytics.log('notebook', 'clearHistory');
    apiHelper
      .clearNotebookHistory({
        notebookJson: await this.toContextJson(),
        docType: this.selectedSnippet(),
        isNotificationManager: this.parentVm.isNotificationManager()
      })
      .then(() => {
        this.history.removeAll();
        if (this.isHistory()) {
          this.id(null);
          this.uuid(hueUtils.UUID());
          this.parentVm.changeURL(
            this.parentVm.URLS.editor + '?type=' + this.parentVm.editorType()
          );
        }
      })
      .fail(xhr => {
        if (xhr.status !== 502) {
          $(document).trigger('error', xhr.responseText);
        }
      });
    $(document).trigger('hideHistoryModal');
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

  fetchHistory(callback) {
    const QUERIES_PER_PAGE = 50;
    this.loadingHistory(true);

    $.get(
      '/notebook/api/get_history',
      {
        doc_type: this.selectedSnippet(),
        limit: QUERIES_PER_PAGE,
        page: this.historyCurrentPage(),
        doc_text: this.historyFilter(),
        is_notification_manager: this.parentVm.isNotificationManager()
      },
      data => {
        const parsedHistory = [];
        if (data && data.history) {
          data.history.forEach(nbk => {
            parsedHistory.push(
              this.makeHistoryRecord(
                nbk.absoluteUrl,
                nbk.data.statement,
                nbk.data.lastExecuted,
                nbk.data.status,
                nbk.name,
                nbk.uuid
              )
            );
          });
        }
        this.history(parsedHistory);
        this.historyTotalPages(Math.ceil(data.count / QUERIES_PER_PAGE));
      }
    ).always(() => {
      this.loadingHistory(false);
      if (callback) {
        callback();
      }
    });
  }

  getSnippets(type) {
    return this.snippets().filter(snippet => snippet.type() === type);
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

      const getCoordinator = function() {
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
                callback: function(r) {
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

  makeHistoryRecord(url, statement, lastExecuted, status, name, uuid) {
    return komapping.fromJS({
      url: url,
      query: statement.substring(0, 1000) + (statement.length > 1000 ? '...' : ''),
      lastExecuted: lastExecuted,
      status: status,
      name: name,
      uuid: uuid
    });
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

  nextHistoryPage() {
    if (this.historyCurrentPage() < this.historyTotalPages()) {
      this.historyCurrentPage(this.historyCurrentPage() + 1);
    }
  }

  prevHistoryPage() {
    if (this.historyCurrentPage() !== 1) {
      this.historyCurrentPage(this.historyCurrentPage() - 1);
    }
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
          if (!data.save_as) {
            const existingQuery = this.snippets()[0]
              .queries()
              .filter(item => item.uuid() === data.uuid);
            if (existingQuery.length > 0) {
              existingQuery[0].name(data.name);
              existingQuery[0].description(data.description);
              existingQuery[0].last_modified(data.last_modified);
            }
          } else if (this.snippets()[0].queries().length > 0) {
            // Saved queries tab already loaded
            this.snippets()[0].queries.unshift(komapping.fromJS(data));
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
            this.snippets()[0]
              .downloadResultViewModel()
              .saveTarget() === 'dashboard'
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
      presentationSnippets: this.presentationSnippets(),
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

  updateHistory(statuses, interval) {
    let items = this.history()
      .filter(item => statuses.indexOf(item.status()) !== -1)
      .slice(0, 25);

    const updateHistoryCall = item => {
      apiHelper
        .checkStatus({ notebookJson: JSON.stringify({ uuid: item.uuid() }) })
        .then(data => {
          const status =
            data.status === -3
              ? 'expired'
              : data.status === 0
              ? data.query_status.status
              : 'failed';
          if (status && item.status() !== status) {
            item.status(status);
          }
        })
        .fail(() => {
          items = [];
          this.updateHistoryFailed = true;
          console.warn('Lost connectivity to the Hue history refresh backend.');
        })
        .always(() => {
          if (items.length > 0) {
            window.setTimeout(() => {
              updateHistoryCall(items.pop());
            }, 1000);
          } else if (!this.updateHistoryFailed) {
            window.setTimeout(() => {
              this.updateHistory(statuses, interval);
            }, interval);
          }
        });
    };

    if (items.length > 0) {
      updateHistoryCall(items.pop());
    } else if (!this.updateHistoryFailed) {
      window.setTimeout(() => {
        this.updateHistory(statuses, interval);
      }, interval);
    }
  }
}
