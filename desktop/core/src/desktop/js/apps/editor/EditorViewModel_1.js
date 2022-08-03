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
import {
  ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT,
  GET_ACTIVE_SNIPPET_CONNECTOR_EVENT
} from 'apps/editor/events';
import Notebook from 'apps/editor/notebook';
import ChartTransformers from 'apps/notebook/chartTransformers';
import { CONFIG_REFRESHED_TOPIC, GET_KNOWN_CONFIG_TOPIC } from 'config/events';
import { findEditorConnector, getLastKnownConfig } from 'config/hueConfig';
import huePubSub from 'utils/huePubSub';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
import UUID from 'utils/string/UUID';
import changeURL from 'utils/url/changeURL';
import changeURLParameter from 'utils/url/changeURLParameter';
import getParameter from 'utils/url/getParameter';

export default class EditorViewModel {
  constructor(editorId, notebooks, options, CoordinatorEditorViewModel, RunningCoordinatorModel) {
    // eslint-disable-next-line no-restricted-syntax
    console.log('Editor v2 enabled.');

    this.editorId = editorId;
    this.snippetViewSettings = options.snippetViewSettings;
    this.notebooks = notebooks;

    this.URLS = {
      editor: '/hue/editor',
      notebook: '/hue/notebook',
      report: '/hue/dashboard/new_search?engine=report'
    };

    this.huePubSubId = options.huePubSubId || 'editor';
    this.user = options.user;
    this.userId = options.userId;
    this.suffix = options.suffix;
    this.isNotificationManager = ko.observable(!!options.is_notification_manager);
    this.selectedNotebook = ko.observable();

    this.firstSnippet = ko.pureComputed(
      () => this.selectedNotebook() && this.selectedNotebook().snippets()[0]
    );

    this.editorMode = ko.observable(options.mode === 'editor');
    this.config = ko.observable();

    this.sharingEnabled = ko.pureComputed(
      () =>
        this.config() &&
        (this.config().hue_config.is_admin || this.config().hue_config.enable_sharing)
    );

    huePubSub.publish(GET_KNOWN_CONFIG_TOPIC, this.config);
    huePubSub.subscribe(CONFIG_REFRESHED_TOPIC, this.config);

    this.activeConnector = ko.pureComputed(() => {
      if (this.editorMode()) {
        const snippet = this.getActiveSnippet();
        if (snippet) {
          if (!snippet.connector()) {
            console.warn('Snippet connector is empty');
          }
          return snippet.connector();
        }
      } else if (this.config() && this.config().app_config && this.config().app_config.editor) {
        const interpreters = this.config().app_config.editor.interpreters;
        return interpreters.find(interpreter => interpreter.dialect === 'notebook');
      }
    });

    this.editorType = ko.pureComputed(() => this.activeConnector() && this.activeConnector().id);
    this.editorTitle = ko.pureComputed(
      () => this.activeConnector() && this.activeConnector().displayName
    );

    this.editorIcon = ko.pureComputed(() => {
      const dialect = this.activeConnector()?.dialect;
      return window.ENABLE_UNIFIED_ANALYTICS && dialect === 'hive'
        ? 'impala'
        : dialect || this.editorType();
    });

    this.activeConnector.subscribe(connector => {
      if (connector) {
        if (getParameter('type') !== connector.id) {
          changeURLParameter('type', connector.id);
        }
        this.notifyDialectChange(connector.dialect, connector.is_sql);
      }
    });

    this.autocompleteTimeout = options.autocompleteTimeout;
    this.lastNotifiedDialect = undefined;

    this.combinedContent = ko.observable();
    this.isPresentationModeEnabled = ko.pureComputed(
      () =>
        this.selectedNotebook() &&
        this.selectedNotebook().snippets().length === 1 &&
        this.selectedNotebook().snippets()[0].isSqlDialect()
    );

    this.bottomExpanded = ko.observable(false);
    this.topExpanded = ko.observable(false);

    this.bottomExpanded.subscribe(newVal => {
      if (newVal) {
        if (this.topExpanded()) {
          this.topExpanded(false);
        }
        huePubSub.publish('both.assists.hide', true);
      } else {
        huePubSub.publish('both.assists.revert', true);
      }
    });

    this.topExpanded.subscribe(newVal => {
      if (newVal) {
        if (this.bottomExpanded()) {
          this.bottomExpanded(false);
        }
        huePubSub.publish('left.assist.hide', true);
      } else {
        huePubSub.publish('both.assists.revert', true);
      }
    });

    this.isPresentationMode = ko.pureComputed(
      () => this.selectedNotebook() && this.selectedNotebook().isPresentationMode()
    );
    this.isHidingCode = ko.pureComputed(
      () => this.selectedNotebook() && this.selectedNotebook().isHidingCode()
    );
    this.successUrl = ko.observable(options.success_url); // Deprecated
    this.isSqlAnalyzerEnabled = ko.observable(options.is_optimizer_enabled);
    this.isNavigatorEnabled = ko.observable(options.is_navigator_enabled);

    this.CoordinatorEditorViewModel = CoordinatorEditorViewModel; // TODO: Remove usage of global variables
    this.RunningCoordinatorModel = RunningCoordinatorModel; // TODO: Remove usage of global variables

    // Saved query or history but history coming from a saved query
    this.canSave = ko.pureComputed(
      () =>
        this.selectedNotebook() &&
        this.selectedNotebook().canWrite() &&
        (this.selectedNotebook().isSaved() ||
          (this.selectedNotebook().isHistory() && this.selectedNotebook().parentSavedQueryUuid()))
    );

    this.ChartTransformers = ChartTransformers;

    this.isEditing = ko.observable(false);
    this.isEditing.subscribe(() => {
      $(document).trigger('editingToggled');
    });

    this.assistAvailable = ko.observable(options.assistAvailable);

    this.assistWithoutStorage = ko.observable(false);

    this.isLeftPanelVisible = ko.observable(
      getFromLocalStorage('assist.assist_panel_visible', true)
    );
    this.isLeftPanelVisible.subscribe(val => {
      if (!this.assistWithoutStorage()) {
        setInLocalStorage('assist.assist_panel_visible', val);
      }
    });

    this.isRightPanelAvailable = ko.observable(options.assistAvailable && window.HAS_SQL_ANALYZER);
    this.isRightPanelVisible = ko.observable(
      getFromLocalStorage('assist.right_assist_panel_visible', true)
    );
    this.isRightPanelVisible.subscribe(val => {
      if (!this.assistWithoutStorage()) {
        setInLocalStorage('assist.right_assist_panel_visible', val);
      }
    });

    huePubSub.subscribe('assist.highlight.risk.suggestions', () => {
      if (this.isRightPanelAvailable() && !this.isRightPanelVisible()) {
        this.isRightPanelVisible(true);
      }
    });

    huePubSub.subscribe(
      GET_ACTIVE_SNIPPET_CONNECTOR_EVENT,
      callback => {
        this.withActiveSnippet(activeSnippet => {
          callback(activeSnippet.connector());
        });
      },
      this.huePubSubId
    );

    huePubSub.subscribe(
      'save.snippet.to.file',
      () => {
        this.withActiveSnippet(activeSnippet => {
          const data = {
            path: activeSnippet.statementPath(),
            contents: activeSnippet.statement()
          };
          const options = {
            successCallback: result => {
              if (result && result.exists) {
                $(document).trigger('info', result.path + ' saved successfully.');
              }
            }
          };
          apiHelper.saveSnippetToFile(data, options);
        });
      },
      this.huePubSubId
    );

    huePubSub.subscribe(
      'sql.context.pin',
      contextData => {
        this.withActiveSnippet(activeSnippet => {
          contextData.tabId = 'context' + activeSnippet.pinnedContextTabs().length;
          activeSnippet.pinnedContextTabs.push(contextData);
          activeSnippet.currentQueryTab(contextData.tabId);
        });
      },
      this.huePubSubId
    );

    huePubSub.subscribe(
      'assist.database.set',
      entry => {
        this.withActiveSnippet(activeSnippet => {
          activeSnippet.handleAssistSelection(entry);
        });
      },
      this.huePubSubId
    );

    huePubSub.subscribe(
      'assist.database.selected',
      entry => {
        this.withActiveSnippet(activeSnippet => {
          activeSnippet.handleAssistSelection(entry);
        });
      },
      this.huePubSubId
    );

    this.availableSnippets = komapping.fromJS(options.languages);
  }

  changeURL(url) {
    if (!this.isNotificationManager()) {
      changeURL(url);
    }
  }

  displayCombinedContent() {
    if (!this.selectedNotebook()) {
      this.combinedContent('');
    } else {
      let statements = '';
      this.selectedNotebook()
        .snippets()
        .forEach(snippet => {
          if (snippet.statement()) {
            if (statements) {
              statements += '\n\n';
            }
            statements += snippet.statement();
          }
        });
      this.combinedContent(statements);
    }
    $('#editorCombinedContentModal').modal('show');
  }

  getSnippetName(snippetType) {
    const availableSnippets = this.availableSnippets();
    for (let i = 0; i < availableSnippets.length; i++) {
      if (availableSnippets[i].dialect() === snippetType) {
        return availableSnippets[i].name();
      }
    }
    return '';
  }

  getSnippetViewSettings(snippetType) {
    if (this.snippetViewSettings[snippetType]) {
      return this.snippetViewSettings[snippetType];
    }
    return this.snippetViewSettings.default;
  }

  async init() {
    if (this.editorId) {
      await this.openNotebook(this.editorId);
    } else if (getParameter('gist') !== '' || getParameter('type') !== '') {
      await this.newNotebook(getParameter('type'));
    } else if (getParameter('editor') !== '') {
      await this.openNotebook(getParameter('editor'));
    } else if (this.notebooks.length > 0) {
      this.loadNotebook(this.notebooks[0]); // Old way of loading json for /browse
    } else {
      await this.newNotebook();
    }
  }

  loadNotebook(notebookRaw, queryTab) {
    const notebook = new Notebook(this, notebookRaw);

    if (notebook.snippets().length > 0) {
      huePubSub.publish('detach.scrolls', notebook.snippets()[0]);
      notebook.selectedSnippet(notebook.snippets()[notebook.snippets().length - 1].dialect());
      notebook.snippets().forEach(snippet => {
        snippet.aceAutoExpand = false;
        snippet.statement_raw.valueHasMutated();
      });

      if (queryTab) {
        notebook.snippets()[0].currentQueryTab(queryTab);
      }

      if (notebook.isSaved()) {
        notebook.snippets()[0].currentQueryTab('savedQueries');
      }
    }

    this.selectedNotebook(notebook);
    huePubSub.publish('check.job.browser');
    huePubSub.publish('recalculate.name.description.width');
  }

  async newNotebook(connectorId, callback, queryTab, blank) {
    if (!connectorId) {
      connectorId = getLastKnownConfig().default_sql_interpreter;
    }
    let connector;
    if (connectorId) {
      connector = findEditorConnector(connector => connector.id === connectorId);
    } else {
      const connectors = getLastKnownConfig().app_config.editor.interpreters;
      if (connectors.length) {
        connector = connectors[0];
      }
    }
    if (!connector) {
      console.warn('No connector found for ID ' + connectorId);
    } else {
      huePubSub.publish(ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT, connector);
    }

    return new Promise((resolve, reject) => {
      $.post('/notebook/api/create_notebook', {
        type: connectorId,
        directory_uuid: getParameter('directory_uuid'),
        gist: this.isNotificationManager() ? undefined : getParameter('gist'),
        blank: typeof blank !== 'undefined'
      })
        .then(data => {
          this.loadNotebook(data.notebook);
          if (this.editorMode() && !this.isNotificationManager()) {
            const snippet =
              this.selectedNotebook().snippets().length === 0
                ? this.selectedNotebook().newSnippet(connectorId)
                : this.selectedNotebook().snippets()[0];
            if (
              queryTab &&
              ['queryHistory', 'savedQueries', 'queryBuilderTab'].indexOf(queryTab) > -1
            ) {
              snippet.currentQueryTab(queryTab);
            }
            huePubSub.publish('detach.scrolls', this.selectedNotebook().snippets()[0]);
          }

          if (callback) {
            callback();
          }
          resolve();
        })
        .catch(reject);
    });
  }

  async openNotebook(uuid, queryTab, skipUrlChange, callback) {
    try {
      const docData = await apiHelper.fetchDocumentAsync({
        uuid: uuid,
        fetchContents: true,
        dependencies: true
      });

      docData.data.dependents = docData.dependents;
      docData.data.can_write = docData.user_perms.can_write;

      const notebookRaw = docData.data;

      this.loadNotebook(notebookRaw, queryTab);

      if (typeof skipUrlChange === 'undefined' && !this.isNotificationManager()) {
        if (this.editorMode()) {
          if (!this.editorType()) {
            console.warn('Snippet connector type or dialect is empty');
          }
          this.changeURL(
            this.URLS.editor + '?editor=' + docData.document.id + '&type=' + this.editorType()
          );
        } else {
          this.changeURL(this.URLS.notebook + '?notebook=' + docData.document.id);
        }
      }
      if (callback) {
        callback();
      }
    } catch (err) {
      console.error(err);
      await this.newNotebook();
    }
  }

  notifyDialectChange(dialect) {
    if (dialect && this.lastNotifiedDialect !== dialect) {
      huePubSub.publish(ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT, this.activeConnector());
      this.lastNotifiedDialect = dialect;
    }
  }

  prepareShareModal() {
    const selectedNotebookUuid = this.selectedNotebook() && this.selectedNotebook().uuid();
    if (selectedNotebookUuid) {
      huePubSub.publish('doc.show.share.modal', selectedNotebookUuid);
    }
  }

  saveAsNotebook() {
    this.selectedNotebook().id(null);
    this.selectedNotebook().uuid(UUID());
    this.selectedNotebook().parentSavedQueryUuid(null);
    this.selectedNotebook().save(() => {
      huePubSub.publish('assist.document.refresh');
    });
  }

  async saveNotebook() {
    await this.selectedNotebook().save();
  }

  showContextPopover(field, event) {
    const $source = $(
      event.target && event.target.nodeName !== 'A' ? event.target.parentElement : event.target
    );
    const offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: field.catalogEntry
      },
      onSampleClick: field.value,
      showInAssistEnabled: true,
      sourceType: this.editorType(),
      orientation: 'bottom',
      defaultDatabase: 'default',
      pinEnabled: false,
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 3,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 3
      }
    });
  }

  showSessionPanel() {
    this.withActiveSnippet(
      snippet => {
        huePubSub.publish('session.panel.show', snippet.dialect());
      },
      () => {
        huePubSub.publish('session.panel.show');
      }
    );
  }

  getActiveSnippet() {
    const notebook = this.selectedNotebook();
    let foundSnippet;
    if (notebook) {
      if (notebook.snippets().length === 1) {
        foundSnippet = notebook.snippets()[0];
      } else {
        notebook.snippets().some(snippet => {
          if (snippet.inFocus()) {
            foundSnippet = snippet;
            return true;
          }
        });
      }
    }
    return foundSnippet;
  }

  withActiveSnippet(callback, notFoundCallback) {
    const foundSnippet = this.getActiveSnippet();
    if (foundSnippet) {
      callback(foundSnippet);
    } else if (notFoundCallback) {
      notFoundCallback();
    }
  }
}
