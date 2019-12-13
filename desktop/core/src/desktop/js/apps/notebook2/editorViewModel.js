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
import ChartTransformers from 'apps/notebook/chartTransformers';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';

import Notebook from 'apps/notebook2/notebook';
import Snippet from 'apps/notebook2/snippet';

class EditorViewModel {
  constructor(editorId, notebooks, options, CoordinatorEditorViewModel, RunningCoordinatorModel) {
    // eslint-disable-next-line no-restricted-syntax
    console.log('Notebook 2 enabled.');

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
    this.isMobile = ko.observable(options.mobile);
    this.isNotificationManager = ko.observable(!!options.is_notification_manager);
    this.editorType = ko.observable(options.editor_type);
    this.editorType.subscribe(newVal => {
      this.editorMode(newVal !== 'notebook');
      hueUtils.changeURLParameter('type', newVal);
      if (this.editorMode()) {
        this.selectedNotebook().fetchHistory(); // Js error if notebook did not have snippets
      }
    });
    this.preEditorTogglingSnippet = ko.observable();

    this.editorTypeTitle = ko.pureComputed(() => {
      const foundInterpreters = options.languages.filter(
        interpreter => interpreter.type === this.editorType()
      );
      return foundInterpreters.length > 0 ? foundInterpreters[0].name : this.editorType();
    });

    this.autocompleteTimeout = options.autocompleteTimeout;
    this.selectedNotebook = ko.observable();

    this.combinedContent = ko.observable();
    this.isPresentationModeEnabled = ko.pureComputed(
      () =>
        this.selectedNotebook() &&
        this.selectedNotebook().snippets().length === 1 &&
        this.selectedNotebook()
          .snippets()[0]
          .isSqlDialect()
    );
    this.isResultFullScreenMode = ko.observable(false);
    this.isPresentationMode = ko.pureComputed(
      () => this.selectedNotebook() && this.selectedNotebook().isPresentationMode()
    );
    this.isHidingCode = ko.pureComputed(
      () => this.selectedNotebook() && this.selectedNotebook().isHidingCode()
    );
    this.successUrl = ko.observable(options.success_url); // Deprecated
    this.isOptimizerEnabled = ko.observable(options.is_optimizer_enabled);
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

    // TODO: Drop the SQL source types from the notebook. They're now set in AssistDbPanel.
    this.sqlSourceTypes = [];
    this.availableLanguages = [];

    if (options.languages && this.snippetViewSettings) {
      options.languages.forEach(language => {
        this.availableLanguages.push({
          type: language.type,
          name: language.name,
          interface: language.interface
        });
        const viewSettings = this.snippetViewSettings[language.type];
        if (viewSettings && viewSettings.sqlDialect) {
          this.sqlSourceTypes.push({
            type: language.type,
            name: language.name
          });
        }
      });
    }

    const sqlSourceTypes = this.sqlSourceTypes.filter(
      language => language.type === this.editorType()
    );
    if (sqlSourceTypes.length > 0) {
      this.activeSqlSourceType = sqlSourceTypes[0].type;
    } else {
      this.activeSqlSourceType = null;
    }

    this.isEditing = ko.observable(false);
    this.isEditing.subscribe(() => {
      $(document).trigger('editingToggled');
    });

    this.removeSnippetConfirmation = ko.observable();

    this.assistAvailable = ko.observable(options.assistAvailable);

    this.assistWithoutStorage = ko.observable(false);

    this.isLeftPanelVisible = ko.observable(
      apiHelper.getFromTotalStorage('assist', 'assist_panel_visible', true)
    );
    this.isLeftPanelVisible.subscribe(val => {
      if (!this.assistWithoutStorage()) {
        apiHelper.setInTotalStorage('assist', 'assist_panel_visible', val);
      }
    });

    this.isRightPanelAvailable = ko.observable(options.assistAvailable && HAS_OPTIMIZER);
    this.isRightPanelVisible = ko.observable(
      apiHelper.getFromTotalStorage('assist', 'right_assist_panel_visible', true)
    );
    this.isRightPanelVisible.subscribe(val => {
      if (!this.assistWithoutStorage()) {
        apiHelper.setInTotalStorage('assist', 'right_assist_panel_visible', val);
      }
    });

    huePubSub.subscribe('assist.highlight.risk.suggestions', () => {
      if (this.isRightPanelAvailable() && !this.isRightPanelVisible()) {
        this.isRightPanelVisible(true);
      }
    });

    huePubSub.subscribe(
      'get.active.snippet.type',
      callback => {
        this.withActiveSnippet(activeSnippet => {
          if (callback) {
            callback(activeSnippet.type());
          } else {
            huePubSub.publish('set.active.snippet.type', activeSnippet.type());
          }
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
            successCallback: function(result) {
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
      databaseDef => {
        this.withActiveSnippet(activeSnippet => {
          activeSnippet.handleAssistSelection(databaseDef);
        });
      },
      this.huePubSubId
    );

    huePubSub.subscribe(
      'assist.database.selected',
      databaseDef => {
        this.withActiveSnippet(activeSnippet => {
          activeSnippet.handleAssistSelection(databaseDef);
        });
      },
      this.huePubSubId
    );

    this.availableSnippets = komapping.fromJS(options.languages);

    this.editorMode = ko.observable(options.mode === 'editor');
  }

  changeURL(url) {
    if (!this.isNotificationManager()) {
      hueUtils.changeURL(url);
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
    $('#combinedContentModal' + this.suffix).modal('show');
  }

  getSnippetName(snippetType) {
    const availableSnippets = this.availableSnippets();
    for (let i = 0; i < availableSnippets.length; i++) {
      if (availableSnippets[i].type() === snippetType) {
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

  init() {
    if (this.editorId) {
      this.openNotebook(this.editorId);
    } else if (
      window.location.getParameter('gist') !== '' ||
      window.location.getParameter('type') !== ''
    ) {
      this.newNotebook(window.location.getParameter('type'));
    } else if (window.location.getParameter('editor') !== '') {
      this.openNotebook(window.location.getParameter('editor'));
    } else if (this.notebooks.length > 0) {
      this.loadNotebook(this.notebooks[0]); // Old way of loading json for /browse
    } else {
      this.newNotebook();
    }
  }

  loadNotebook(notebookRaw, queryTab) {
    const notebook = new Notebook(this, notebookRaw);

    if (notebook.snippets().length > 0) {
      huePubSub.publish('detach.scrolls', notebook.snippets()[0]);
      notebook.selectedSnippet(notebook.snippets()[notebook.snippets().length - 1].type());
      notebook.snippets().forEach(snippet => {
        snippet.aceAutoExpand = false;
        snippet.statement_raw.valueHasMutated();
        // if (
        //   snippet.result.handle().statements_count > 1 &&
        //   snippet.result.handle().start != null &&
        //   snippet.result.handle().end != null
        // ) {
        //   const aceLineOffset = snippet.result.handle().aceLineOffset || 0;
        //   snippet.result.statement_range({
        //     start: {
        //       row: snippet.result.handle().start.row + aceLineOffset,
        //       column: snippet.result.handle().start.column
        //     },
        //     end: {
        //       row: snippet.result.handle().end.row + aceLineOffset,
        //       column: snippet.result.handle().end.column
        //     }
        //   });
        //   snippet.result.statement_range.valueHasMutated();
        // }
      });

      // if (notebook.snippets()[0].result.data().length > 0) {
      //   $(document).trigger('redrawResults');
      // } else
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

  async newNotebook(editorType, callback, queryTab) {
    return new Promise((resolve, reject) => {
      huePubSub.publish('active.snippet.type.changed', {
        type: editorType,
        isSqlDialect: editorType ? this.getSnippetViewSettings(editorType).sqlDialect : undefined
      });
      $.post('/notebook/api/create_notebook', {
        type: editorType || this.editorType(),
        directory_uuid: window.location.getParameter('directory_uuid'),
        gist: window.location.getParameter('gist')
      })
        .then(data => {
          this.loadNotebook(data.notebook);
          if (this.editorMode() && !this.isNotificationManager()) {
            const snippet =
              this.selectedNotebook().snippets().length == 0
                ? this.selectedNotebook().newSnippet(this.editorType())
                : this.selectedNotebook().snippets()[0];
            if (
              queryTab &&
              ['queryHistory', 'savedQueries', 'queryBuilderTab'].indexOf(queryTab) > -1
            ) {
              snippet.currentQueryTab(queryTab);
            }
            huePubSub.publish('detach.scrolls', this.selectedNotebook().snippets()[0]);
            if (window.location.getParameter('type') === '') {
              hueUtils.changeURLParameter('type', this.editorType());
            }
            huePubSub.publish('active.snippet.type.changed', {
              type: editorType,
              isSqlDialect: editorType
                ? this.getSnippetViewSettings(editorType).sqlDialect
                : undefined
            });
          }

          if (typeof callback !== 'undefined' && callback !== null) {
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
          this.editorType(docData.document.type.substring('query-'.length));
          huePubSub.publish('active.snippet.type.changed', {
            type: this.editorType(),
            isSqlDialect: this.getSnippetViewSettings(this.editorType()).sqlDialect
          });
          this.changeURL(
            this.URLS.editor + '?editor=' + docData.document.id + '&type=' + this.editorType()
          );
        } else {
          this.changeURL(this.URLS.notebook + '?notebook=' + docData.document.id);
        }
      }
      if (typeof callback !== 'undefined') {
        callback();
      }
    } catch (err) {
      console.error(err);
      await this.newNotebook();
    }
  }

  prepareShareModal() {
    const selectedNotebookUuid = this.selectedNotebook() && this.selectedNotebook().uuid();
    if (selectedNotebookUuid) {
      huePubSub.publish('doc.show.share.modal', selectedNotebookUuid);
    }
  }

  removeSnippet(notebook, snippet) {
    let hasContent = snippet.statement_raw().length > 0;
    if (!hasContent) {
      Object.keys(snippet.properties()).forEach(key => {
        const value = snippet.properties()[key];
        hasContent = hasContent || (ko.isObservable(value) && value().length > 0);
      });
    }
    if (hasContent) {
      this.removeSnippetConfirmation({ notebook: notebook, snippet: snippet });
      $('#removeSnippetModal' + this.suffix).modal('show');
    } else {
      notebook.snippets.remove(snippet);
      window.setTimeout(() => {
        $(document).trigger('editorSizeChanged');
      }, 100);
    }
  }

  saveAsNotebook() {
    this.selectedNotebook().id(null);
    this.selectedNotebook().uuid(hueUtils.UUID());
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
        huePubSub.publish('session.panel.show', snippet.type());
      },
      () => {
        huePubSub.publish('session.panel.show');
      }
    );
  }

  toggleEditing() {
    this.isEditing(!this.isEditing());
  }

  toggleEditorMode() {
    const selectedNotebook = this.selectedNotebook();
    const newSnippets = [];

    if (this.editorType() !== 'notebook') {
      this.editorType('notebook');
      this.preEditorTogglingSnippet(selectedNotebook.snippets()[0]);
      const variables = selectedNotebook.snippets()[0].variables();
      const statementKeys = [];
      // Split statements
      selectedNotebook.type('notebook');
      selectedNotebook
        .snippets()[0]
        .statementsList()
        .forEach(sqlStatement => {
          let presentationSnippet;
          if (sqlStatement.hashCode() in selectedNotebook.presentationSnippets()) {
            presentationSnippet = selectedNotebook.presentationSnippets()[sqlStatement.hashCode()]; // Persist result
            presentationSnippet.variables(variables);
          } else {
            const titleParts = [];
            const statementParts = [];
            sqlStatement
              .trim()
              .split('\n')
              .forEach(line => {
                if (line.trim().startsWith('--') && statementParts.length === 0) {
                  titleParts.push(line.substr(2));
                } else {
                  statementParts.push(line);
                }
              });
            presentationSnippet = new Snippet(this, selectedNotebook, {
              type: selectedNotebook.initialType,
              statement_raw: statementParts.join('\n'),
              name: titleParts.join('\n'),
              variables: komapping.toJS(variables)
            });
            presentationSnippet.variables = selectedNotebook.snippets()[0].variables;
            presentationSnippet.init();
            selectedNotebook.presentationSnippets()[sqlStatement.hashCode()] = presentationSnippet;
          }
          statementKeys.push(sqlStatement.hashCode());
          newSnippets.push(presentationSnippet);
        });
      $.each(selectedNotebook.presentationSnippets(), key => {
        // Dead statements
        if (!key in statementKeys) {
          delete selectedNotebook.presentationSnippets()[key];
        }
      });
    } else {
      this.editorType(selectedNotebook.initialType);
      // Revert to one statement
      newSnippets.push(this.preEditorTogglingSnippet());
      selectedNotebook.type('query-' + selectedNotebook.initialType);
    }
    selectedNotebook.snippets(newSnippets);
    newSnippets.forEach(snippet => {
      huePubSub.publish('editor.redraw.data', { snippet: snippet });
    });
  }

  togglePresentationMode() {
    if (this.selectedNotebook().initialType !== 'notebook') {
      this.toggleEditorMode();
    }
  }

  withActiveSnippet(callback, notFoundCallback) {
    const notebook = this.selectedNotebook();
    let foundSnippet;
    if (notebook) {
      if (notebook.snippets().length === 1) {
        foundSnippet = notebook.snippets()[0];
      } else {
        notebook.snippets().every(snippet => {
          if (snippet.inFocus()) {
            foundSnippet = snippet;
            return false;
          }
          return true;
        });
      }
    }
    if (foundSnippet) {
      callback(foundSnippet);
    } else if (notFoundCallback) {
      notFoundCallback();
    }
  }
}

export default EditorViewModel;
