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

import Session from 'apps/notebook2/session';
import { Snippet, STATUS as SNIPPET_STATUS } from 'apps/notebook2/snippet';

const NOTEBOOK_MAPPING = {
  ignore: [
    'ace',
    'aceEditor',
    'aceMode',
    'autocompleter',
    'availableDatabases',
    'availableSnippets',
    'avoidClosing',
    'canWrite',
    'cleanedDateTimeMeta',
    'cleanedMeta',
    'cleanedNumericMeta',
    'cleanedStringMeta',
    'dependents',
    'errorLoadingQueries',
    'hasProperties',
    'history',
    'images',
    'inFocus',
    'parentNotebook',
    'parentVm',
    'queries',
    'saveResultsModalVisible',
    'selectedStatement',
    'snippetImage',
    'user',
    'positionStatement',
    'lastExecutedStatement',
    'downloadResultViewModel'
  ]
};

class Notebook {
  constructor(vm, notebook) {
    const self = this;

    self.parentVm = vm;

    self.id = ko.observable(notebook.id);
    self.uuid = ko.observable(notebook.uuid || hueUtils.UUID());
    self.name = ko.observable(notebook.name || 'My Notebook');
    self.description = ko.observable(notebook.description || '');
    self.type = ko.observable(notebook.type || 'notebook');
    self.initialType = self.type().replace('query-', '');
    self.coordinatorUuid = ko.observable(notebook.coordinatorUuid);
    self.isHistory = ko.observable(!!notebook.is_history);
    self.isManaged = ko.observable(!!notebook.isManaged);
    self.parentSavedQueryUuid = ko.observable(notebook.parentSavedQueryUuid); // History parent
    self.isSaved = ko.observable(!!notebook.isSaved);
    self.canWrite = ko.observable(notebook.can_write !== false);
    self.onSuccessUrl = ko.observable(notebook.onSuccessUrl);
    self.pubSubUrl = ko.observable(notebook.pubSubUrl);
    self.isPresentationModeDefault = ko.observable(!!notebook.isPresentationModeDefault);
    self.isPresentationMode = ko.observable(false);
    self.isPresentationModeInitialized = ko.observable(false);
    self.isPresentationMode.subscribe(newValue => {
      if (!newValue) {
        self.cancelExecutingAll();
      }
      huePubSub.publish('editor.presentation.operate.toggle', newValue); // Problem with headers / row numbers redraw on full screen results
      vm.togglePresentationMode();
      if (newValue) {
        hueAnalytics.convert('editor', 'presentation');
      }
    });
    self.presentationSnippets = ko.observable({});
    self.isHidingCode = ko.observable(!!notebook.isHidingCode);

    self.snippets = ko.observableArray();
    self.selectedSnippet = ko.observable(vm.editorType()); // Aka selectedSnippetType
    self.creatingSessionLocks = ko.observableArray();
    self.sessions = komapping.fromJS(notebook.sessions || [], {
      create: value => new Session(vm, value.data)
    });
    self.directoryUuid = ko.observable(notebook.directoryUuid);
    self.dependents = komapping.fromJS(notebook.dependents || []);
    self.dependentsCoordinator = ko.pureComputed(() =>
      self.dependents().filter(doc => doc.type() === 'oozie-coordinator2' && doc.is_managed())
    );
    if (self.dependentsCoordinator().length > 0 && !self.coordinatorUuid()) {
      self.coordinatorUuid(self.dependentsCoordinator()[0].uuid());
    }
    self.history = ko.observableArray(
      vm.selectedNotebook() &&
        vm.selectedNotebook().history().length > 0 &&
        vm.selectedNotebook().history()[0].type === self.type()
        ? vm.selectedNotebook().history()
        : []
    );
    self.history.subscribe(val => {
      if (
        self.id() == null &&
        val.length === 0 &&
        self.historyFilter() === '' &&
        !vm.isNotificationManager()
      ) {
        self
          .snippets()[0]
          .currentQueryTab(
            typeof window.IS_EMBEDDED !== 'undefined' && window.IS_EMBEDDED
              ? 'queryHistory'
              : 'savedQueries'
          );
      }
    });
    self.historyFilter = ko.observable('');
    self.historyFilterVisible = ko.observable(false);
    self.historyFilter.extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 900 } });
    self.historyFilter.subscribe(() => {
      if (self.historyCurrentPage() !== 1) {
        self.historyCurrentPage(1);
      } else {
        self.fetchHistory();
      }
    });
    self.loadingHistory = ko.observable(self.history().length === 0);
    self.historyInitialHeight = ko.observable(0).extend({ throttle: 1000 });
    self.forceHistoryInitialHeight = ko.observable(false);
    self.historyCurrentPage = ko.observable(
      vm.selectedNotebook() ? vm.selectedNotebook().historyCurrentPage() : 1
    );
    self.historyCurrentPage.subscribe(() => {
      self.fetchHistory();
    });
    self.historyTotalPages = ko.observable(
      vm.selectedNotebook() ? vm.selectedNotebook().historyTotalPages() : 1
    );

    self.schedulerViewModel = null;
    self.schedulerViewModelIsLoaded = ko.observable(false);
    self.schedulerViewerViewModel = ko.observable();
    self.isBatchable = ko.pureComputed(
      () => self.snippets().length > 0 && self.snippets().every(snippet => snippet.isBatchable())
    );

    self.isExecutingAll = ko.observable(!!notebook.isExecutingAll);

    self.executingAllIndex = ko.observable(notebook.executingAllIndex || 0);

    self.retryModalConfirm = null;
    self.retryModalCancel = null;

    self.avoidClosing = false;

    self.canSave = vm.canSave;

    self.unloaded = ko.observable(false);
    self.updateHistoryFailed = false;

    self.viewSchedulerId = ko.observable(notebook.viewSchedulerId || '');
    self.viewSchedulerId.subscribe(() => {
      self.save();
    });
    self.isSchedulerJobRunning = ko.observable();
    self.loadingScheduler = ko.observable(false);

    // Init
    if (notebook.snippets) {
      notebook.snippets.forEach(snippet => {
        self.addSnippet(snippet);
      });
      if (
        typeof notebook.presentationSnippets != 'undefined' &&
        notebook.presentationSnippets != null
      ) {
        // Load
        $.each(notebook.presentationSnippets, (key, snippet) => {
          snippet.status = 'ready'; // Protect from storm of check_statuses
          const _snippet = new Snippet(vm, self, snippet);
          _snippet.init();
          _snippet.previousChartOptions = vm.getPreviousChartOptions(_snippet);
          self.presentationSnippets()[key] = _snippet;
        });
      }
      if (vm.editorMode() && self.history().length === 0) {
        self.fetchHistory(() => {
          self.updateHistory(['starting', 'running'], 30000);
          self.updateHistory(['available'], 60000 * 5);
        });
      }
    }

    huePubSub.subscribeOnce(
      'assist.db.panel.ready',
      () => {
        if (self.type().indexOf('query') === 0) {
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

          if (self.snippets().length === 1) {
            whenSnippetAvailable(self.snippets()[0]);
          } else {
            const snippetsSub = self.snippets.subscribe(snippets => {
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

  addSession(session) {
    const self = this;
    const toRemove = self.sessions().filter(s => s.type() === session.type());

    toRemove.forEach(s => {
      self.sessions.remove(s);
    });

    self.sessions.push(session);
  }

  addSnippet(snippet, skipSession) {
    const self = this;
    const newSnippet = new Snippet(self.parentVm, self, snippet);
    self.snippets.push(newSnippet);

    if (self.getSession(newSnippet.type()) == null && typeof skipSession == 'undefined') {
      window.setTimeout(() => {
        newSnippet.status(SNIPPET_STATUS.loading);
        self.createSession(new Session(self.parentVm, { type: newSnippet.type() }));
      }, 200);
    }

    newSnippet.init();
    return newSnippet;
  }

  authSession() {
    const self = this;
    self.createSession(
      new Session(self.parentVm, {
        type: self.parentVm.authSessionType(),
        properties: [
          { name: 'user', value: self.parentVm.authSessionUsername() },
          { name: 'password', value: self.parentVm.authSessionPassword() }
        ]
      }),
      self.parentVm.authSessionCallback() // On new session we don't automatically execute the snippet after the aut. On session expiration we do or we refresh assist DB when login-in.
    );
  }

  cancelExecutingAll() {
    const self = this;
    const index = self.executingAllIndex();
    if (self.isExecutingAll() && self.snippets()[index]) {
      self.snippets()[index].cancel();
    }
  }

  clearHistory() {
    const self = this;
    hueAnalytics.log('notebook', 'clearHistory');
    $.post(
      '/notebook/api/clear_history',
      {
        notebook: komapping.toJSON(self.getContext(), NOTEBOOK_MAPPING),
        doc_type: self.selectedSnippet(),
        is_notification_manager: self.parentVm.isNotificationManager()
      },
      () => {
        self.history.removeAll();
        if (self.isHistory()) {
          self.id(null);
          self.uuid(hueUtils.UUID());
          self.parentVm.changeURL(
            self.parentVm.URLS.editor + '?type=' + self.parentVm.editorType()
          );
        }
      }
    ).fail(xhr => {
      if (xhr.status !== 502) {
        $(document).trigger('error', xhr.responseText);
      }
    });
    $(document).trigger('hideHistoryModal');
  }

  clearResults() {
    const self = this;
    self.snippets().forEach(snippet => {
      snippet.result.clear();
      snippet.status(SNIPPET_STATUS.ready);
    });
  }

  close() {
    const self = this;
    hueAnalytics.log('notebook', 'close');
    $.post('/notebook/api/notebook/close', {
      notebook: komapping.toJSON(self, NOTEBOOK_MAPPING),
      editorMode: self.parentVm.editorMode()
    });
  }

  closeAndRemoveSession(session) {
    const self = this;
    self.closeSession(session, false, () => {
      self.sessions.remove(session);
    });
  }

  closeSession(session, silent, callback) {
    $.post(
      '/notebook/api/close_session',
      {
        session: komapping.toJSON(session)
      },
      data => {
        if (!silent && data && data.status !== 0 && data.status !== -2 && data.message) {
          $(document).trigger('error', data.message);
        }

        if (callback) {
          callback();
        }
      }
    ).fail(xhr => {
      if (!silent && xhr.status !== 502) {
        $(document).trigger('error', xhr.responseText);
      }
    });
  }

  createSession(session, callback, failCallback) {
    const self = this;
    if (self.creatingSessionLocks().indexOf(session.type()) !== -1) {
      // Create one type of session max
      return;
    } else {
      self.creatingSessionLocks.push(session.type());
    }

    let compute = null;
    self.getSnippets(session.type()).forEach((snippet, index) => {
      snippet.status(SNIPPET_STATUS.loading);
      if (index === 0) {
        compute = snippet.compute();
      }
    });

    const fail = function(message) {
      self.getSnippets(session.type()).forEach(snippet => {
        snippet.status('failed');
      });
      $(document).trigger('error', message);
      if (failCallback) {
        failCallback();
      }
    };

    $.post(
      '/notebook/api/create_session',
      {
        notebook: komapping.toJSON(self.getContext(), NOTEBOOK_MAPPING),
        session: komapping.toJSON(session), // e.g. {'type': 'pyspark', 'properties': [{'name': driverCores', 'value', '2'}]}
        cluster: komapping.toJSON(compute ? compute : '')
      },
      data => {
        if (data.status === 0) {
          komapping.fromJS(data.session, {}, session);
          if (self.getSession(session.type()) == null) {
            self.addSession(session);
          } else {
            const _session = self.getSession(session.type());
            komapping.fromJS(data.session, {}, _session);
          }
          self.getSnippets(session.type()).forEach(snippet => {
            snippet.status('ready');
          });
          if (callback) {
            setTimeout(callback, 500);
          }
        } else if (data.status === 401) {
          $(document).trigger('showAuthModal', { type: session.type(), message: data.message });
        } else {
          fail(data.message);
        }
      }
    )
      .fail(xhr => {
        if (xhr.status !== 502) {
          fail(xhr.responseText);
        }
      })
      .always(() => {
        self.creatingSessionLocks.remove(session.type());
      });
  }

  executeAll() {
    const self = this;
    if (self.isExecutingAll() || self.snippets().length === 0) {
      return;
    }

    self.isExecutingAll(true);
    self.executingAllIndex(0);

    self.snippets()[self.executingAllIndex()].execute();
  }

  fetchHistory(callback) {
    const self = this;
    const QUERIES_PER_PAGE = 50;
    self.loadingHistory(true);

    $.get(
      '/notebook/api/get_history',
      {
        doc_type: self.selectedSnippet(),
        limit: QUERIES_PER_PAGE,
        page: self.historyCurrentPage(),
        doc_text: self.historyFilter(),
        is_notification_manager: self.parentVm.isNotificationManager()
      },
      data => {
        const parsedHistory = [];
        if (data && data.history) {
          data.history.forEach(nbk => {
            parsedHistory.push(
              self.makeHistoryRecord(
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
        self.history(parsedHistory);
        self.historyTotalPages(Math.ceil(data.count / QUERIES_PER_PAGE));
      }
    ).always(() => {
      self.loadingHistory(false);
      if (callback) {
        callback();
      }
    });
  }

  getContext() {
    const self = this;
    return {
      id: self.id,
      uuid: self.uuid,
      parentSavedQueryUuid: self.parentSavedQueryUuid,
      isSaved: self.isSaved,
      sessions: self.sessions,
      type: self.type,
      name: self.name
    };
  }

  getSession(session_type) {
    const self = this;
    let found = undefined;
    self.sessions().every(session => {
      if (session.type() === session_type) {
        found = session;
        return false;
      }
      return true;
    });
    return found;
  }

  getSnippets(type) {
    const self = this;
    return self.snippets().filter(snippet => snippet.type() === type);
  }

  loadScheduler() {
    const self = this;
    if (typeof self.parentVm.CoordinatorEditorViewModel !== 'undefined' && self.isBatchable()) {
      let action;
      if (self.coordinatorUuid()) {
        action = 'edit';
      } else {
        action = 'new';
      }
      hueAnalytics.log('notebook', 'schedule/' + action);

      const getCoordinator = function() {
        $.get(
          '/oozie/editor/coordinator/' + action + '/',
          {
            format: 'json',
            document: self.uuid(),
            coordinator: self.coordinatorUuid()
          },
          data => {
            if ($('#schedulerEditor').length > 0) {
              huePubSub.publish('hue4.process.headers', {
                response: data.layout,
                callback: function(r) {
                  const $schedulerEditor = $('#schedulerEditor');
                  $schedulerEditor.html(r);

                  self.schedulerViewModel = new self.parentVm.CoordinatorEditorViewModel(
                    data.coordinator,
                    data.credentials,
                    data.workflows,
                    data.can_edit
                  );

                  ko.cleanNode($schedulerEditor[0]);
                  ko.applyBindings(self.schedulerViewModel, $schedulerEditor[0]);
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

                  self.schedulerViewModel.coordinator.properties.cron_advanced.valueHasMutated(); // Update jsCron enabled status
                  self.schedulerViewModel.coordinator.tracker().markCurrentStateAsClean();
                  self.schedulerViewModel.isEditing(true);

                  self.schedulerViewModelIsLoaded(true);

                  if (action === 'new') {
                    self.schedulerViewModel.coordinator.properties.document(self.uuid()); // Expected for triggering the display
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
    const self = this;
    if (type) {
      self.selectedSnippet(type);
    }
    const snippet = self.addSnippet({
      type: self.selectedSnippet(),
      result: {}
    });

    window.setTimeout(() => {
      const lastSnippet = snippet;
      if (lastSnippet.ace() != null) {
        lastSnippet.ace().focus();
      }
    }, 100);

    hueAnalytics.log('notebook', 'add_snippet/' + (type ? type : self.selectedSnippet()));
    return snippet;
  }

  newSnippetAbove(id) {
    const self = this;
    self.newSnippet();
    let idx = 0;
    self.snippets().forEach((snippet, cnt) => {
      if (snippet.id() === id) {
        idx = cnt;
      }
    });
    self.snippets(self.snippets().move(self.snippets().length - 1, idx));
  }

  nextHistoryPage() {
    const self = this;
    if (self.historyCurrentPage() < self.historyTotalPages()) {
      self.historyCurrentPage(self.historyCurrentPage() + 1);
    }
  }

  prevHistoryPage() {
    const self = this;
    if (self.historyCurrentPage() !== 1) {
      self.historyCurrentPage(self.historyCurrentPage() - 1);
    }
  }

  restartSession(session, callback) {
    const self = this;
    if (session.restarting()) {
      return;
    }
    session.restarting(true);
    const snippets = self.getSnippets(session.type());

    snippets.forEach(snippet => {
      snippet.status(SNIPPET_STATUS.loading);
    });

    self.closeSession(session, true, () => {
      self.createSession(
        session,
        () => {
          snippets.forEach(snippet => {
            snippet.status(SNIPPET_STATUS.ready);
          });
          session.restarting(false);
          if (callback) {
            callback();
          }
        },
        () => {
          session.restarting(false);
        }
      );
    });
  }

  save(callback) {
    const self = this;
    hueAnalytics.log('notebook', 'save');

    // Remove the result data from the snippets
    // Also do it for presentation mode
    const cp = komapping.toJS(self, NOTEBOOK_MAPPING);
    cp.snippets
      .concat(Object.keys(cp.presentationSnippets).map(key => cp.presentationSnippets[key]))
      .forEach(snippet => {
        snippet.result.data.length = 0; // snippet.result.clear() does not work for some reason
        snippet.result.meta.length = 0;
        snippet.result.logs = '';
        snippet.result.fetchedOnce = false;
        snippet.progress = 0; // Remove progress
        snippet.jobs.length = 0;
      });
    if (cp.schedulerViewModel) {
      cp.schedulerViewModel.availableTimezones = [];
    }
    const editorMode =
      self.parentVm.editorMode() ||
      (self.isPresentationMode() && self.parentVm.editorType() !== 'notebook'); // Editor should not convert to Notebook in presentation mode

    $.post(
      '/notebook/api/notebook/save',
      {
        notebook: komapping.toJSON(cp, NOTEBOOK_MAPPING),
        editorMode: editorMode
      },
      data => {
        if (data.status === 0) {
          self.id(data.id);
          self.isSaved(true);
          const wasHistory = self.isHistory();
          self.isHistory(false);
          $(document).trigger('info', data.message);
          if (editorMode) {
            if (!data.save_as) {
              const existingQuery = self
                .snippets()[0]
                .queries()
                .filter(item => item.uuid() === data.uuid);
              if (existingQuery.length > 0) {
                existingQuery[0].name(data.name);
                existingQuery[0].description(data.description);
                existingQuery[0].last_modified(data.last_modified);
              }
            } else if (self.snippets()[0].queries().length > 0) {
              // Saved queries tab already loaded
              self.snippets()[0].queries.unshift(komapping.fromJS(data));
            }

            if (self.coordinatorUuid() && self.schedulerViewModel) {
              self.saveScheduler();
              self.schedulerViewModel.coordinator.refreshParameters();
            }
            if (wasHistory || data.save_as) {
              self.loadScheduler();
            }

            if (
              self.snippets()[0].downloadResultViewModel &&
              self
                .snippets()[0]
                .downloadResultViewModel()
                .saveTarget() === 'dashboard'
            ) {
              huePubSub.publish(
                'open.link',
                self.parentVm.URLS.report +
                  '&uuid=' +
                  data.uuid +
                  '&statement=' +
                  self.snippets()[0].result.handle().statement_id
              );
            } else {
              self.parentVm.changeURL(self.parentVm.URLS.editor + '?editor=' + data.id);
            }
          } else {
            self.parentVm.changeURL(self.parentVm.URLS.notebook + '?notebook=' + data.id);
          }
          if (typeof callback == 'function') {
            callback();
          }
        } else {
          $(document).trigger('error', data.message);
        }
      }
    ).fail(xhr => {
      if (xhr.status !== 502) {
        $(document).trigger('error', xhr.responseText);
      }
    });
  }

  saveDefaultUserProperties(session) {
    const self = this;
    apiHelper.saveConfiguration({
      app: session.type(),
      properties: session.properties,
      userId: self.parentVm.userId
    });
  }

  saveScheduler() {
    const self = this;
    if (
      self.isBatchable() &&
      (!self.coordinatorUuid() || self.schedulerViewModel.coordinator.isDirty())
    ) {
      self.schedulerViewModel.coordinator.isManaged(true);
      self.schedulerViewModel.coordinator.properties.document(self.uuid());
      self.schedulerViewModel.save(data => {
        if (!self.coordinatorUuid()) {
          self.coordinatorUuid(data.uuid);
          self.save();
        }
      });
    }
  }

  showSubmitPopup() {
    const self = this;
    $.get(
      '/oozie/editor/coordinator/submit/' + self.coordinatorUuid(),
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

  unload() {
    const self = this;
    self.unloaded(true);
    let currentQueries = null;
    self.snippets().forEach(snippet => {
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
    const self = this;
    let items = self
      .history()
      .filter(item => statuses.indexOf(item.status()) !== -1)
      .slice(0, 25);

    const updateHistoryCall = item => {
      $.post('/notebook/api/check_status', {
        notebook: komapping.toJSON({ id: item.uuid() })
      })
        .done(data => {
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
          self.updateHistoryFailed = true;
          console.warn('Lost connectivity to the Hue history refresh backend.');
        })
        .always(() => {
          if (items.length > 0) {
            window.setTimeout(() => {
              updateHistoryCall(items.pop());
            }, 1000);
          } else if (!self.updateHistoryFailed) {
            window.setTimeout(() => {
              self.updateHistory(statuses, interval);
            }, interval);
          }
        });
    };

    if (items.length > 0) {
      updateHistoryCall(items.pop());
    } else if (!self.updateHistoryFailed) {
      window.setTimeout(() => {
        self.updateHistory(statuses, interval);
      }, interval);
    }
  }
}

export { Notebook, NOTEBOOK_MAPPING };
