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
import ChartTransformers from 'apps/notebook/chartTransformers';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';

import { Notebook } from 'apps/notebook2/notebook';
import { Snippet } from 'apps/notebook2/snippet';

class EditorViewModel {
  constructor(editorId, notebooks, options, CoordinatorEditorViewModel, RunningCoordinatorModel) {
    const self = this;

    console.log('Notebook 2 enabled.');

    self.editorId = editorId;
    self.sessionProperties = options.session_properties || [];
    self.snippetViewSettings = options.snippetViewSettings;
    self.notebooks = notebooks;

    self.URLS = {
      editor: '/hue/editor',
      notebook: '/hue/notebook',
      report: '/hue/dashboard/new_search?engine=report'
    };

    self.huePubSubId = options.huePubSubId || 'editor';
    self.user = options.user;
    self.userId = options.userId;
    self.suffix = options.suffix;
    self.isMobile = ko.observable(options.mobile);
    self.isNotificationManager = ko.observable(!!options.is_notification_manager);
    self.editorType = ko.observable(options.editor_type);
    self.editorType.subscribe(newVal => {
      self.editorMode(newVal !== 'notebook');
      hueUtils.changeURLParameter('type', newVal);
      if (self.editorMode()) {
        self.selectedNotebook().fetchHistory(); // Js error if notebook did not have snippets
      }
    });
    self.preEditorTogglingSnippet = ko.observable();

    self.editorTypeTitle = ko.pureComputed(() => {
      const foundInterpreters = options.languages.filter(
        interpreter => interpreter.type === self.editorType()
      );
      return foundInterpreters.length > 0 ? foundInterpreters[0].name : self.editorType();
    });

    self.autocompleteTimeout = options.autocompleteTimeout;
    self.selectedNotebook = ko.observable();

    self.combinedContent = ko.observable();
    self.isPresentationModeEnabled = ko.pureComputed(
      () =>
        self.selectedNotebook() &&
        self.selectedNotebook().snippets().length === 1 &&
        self
          .selectedNotebook()
          .snippets()[0]
          .isSqlDialect()
    );
    self.isResultFullScreenMode = ko.observable(false);
    self.isPresentationMode = ko.pureComputed(
      () => self.selectedNotebook() && self.selectedNotebook().isPresentationMode()
    );
    self.isHidingCode = ko.pureComputed(
      () => self.selectedNotebook() && self.selectedNotebook().isHidingCode()
    );
    self.successUrl = ko.observable(options.success_url); // Deprecated
    self.isOptimizerEnabled = ko.observable(options.is_optimizer_enabled);
    self.isNavigatorEnabled = ko.observable(options.is_navigator_enabled);

    self.CoordinatorEditorViewModel = CoordinatorEditorViewModel;
    self.RunningCoordinatorModel = RunningCoordinatorModel;

    // Saved query or history but history coming from a saved query
    self.canSave = ko.pureComputed(
      () =>
        self.selectedNotebook() &&
        self.selectedNotebook().canWrite() &&
        (self.selectedNotebook().isSaved() ||
          (self.selectedNotebook().isHistory() && self.selectedNotebook().parentSavedQueryUuid()))
    );

    self.ChartTransformers = ChartTransformers;

    // TODO: Drop the SQL source types from the notebook. They're now set in AssistDbPanel.
    self.sqlSourceTypes = [];
    self.availableLanguages = [];

    if (options.languages && self.snippetViewSettings) {
      options.languages.forEach(language => {
        self.availableLanguages.push({
          type: language.type,
          name: language.name,
          interface: language.interface
        });
        const viewSettings = self.snippetViewSettings[language.type];
        if (viewSettings && viewSettings.sqlDialect) {
          self.sqlSourceTypes.push({
            type: language.type,
            name: language.name
          });
        }
      });
    }

    const sqlSourceTypes = self.sqlSourceTypes.filter(
      language => language.type === self.editorType()
    );
    if (sqlSourceTypes.length > 0) {
      self.activeSqlSourceType = sqlSourceTypes[0].type;
    } else {
      self.activeSqlSourceType = null;
    }

    self.isEditing = ko.observable(false);
    self.isEditing.subscribe(() => {
      $(document).trigger('editingToggled');
    });

    self.authSessionUsername = ko.observable(); // UI popup
    self.authSessionPassword = ko.observable();
    self.authSessionMessage = ko.observable();
    self.authSessionType = ko.observable();
    self.authSessionCallback = ko.observable();

    self.removeSnippetConfirmation = ko.observable();

    self.assistAvailable = ko.observable(options.assistAvailable);

    self.assistWithoutStorage = ko.observable(false);

    self.isLeftPanelVisible = ko.observable(
      apiHelper.getFromTotalStorage('assist', 'assist_panel_visible', true)
    );
    self.isLeftPanelVisible.subscribe(val => {
      if (!self.assistWithoutStorage()) {
        apiHelper.setInTotalStorage('assist', 'assist_panel_visible', val);
      }
    });

    self.isRightPanelAvailable = ko.observable(options.assistAvailable && HAS_OPTIMIZER);
    self.isRightPanelVisible = ko.observable(
      apiHelper.getFromTotalStorage('assist', 'right_assist_panel_visible', true)
    );
    self.isRightPanelVisible.subscribe(val => {
      if (!self.assistWithoutStorage()) {
        apiHelper.setInTotalStorage('assist', 'right_assist_panel_visible', val);
      }
    });

    const withActiveSnippet = function(callback) {
      const notebook = self.selectedNotebook();
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
      }
    };

    huePubSub.subscribe('assist.highlight.risk.suggestions', () => {
      if (self.isRightPanelAvailable() && !self.isRightPanelVisible()) {
        self.isRightPanelVisible(true);
      }
    });

    self.isContextPanelVisible = ko.observable(false);
    self.isContextPanelVisible.subscribe(newValue => {
      huePubSub.publish('context.panel.visible', newValue);
    });

    huePubSub.subscribe('context.panel.visible.editor', self.isContextPanelVisible);

    huePubSub.subscribe(
      'get.active.snippet.type',
      () => {
        withActiveSnippet(activeSnippet => {
          huePubSub.publish('set.active.snippet.type', activeSnippet.type());
        });
      },
      self.huePubSubId
    );

    huePubSub.subscribe(
      'save.snippet.to.file',
      () => {
        withActiveSnippet(activeSnippet => {
          const data = {
            path: activeSnippet.statementPath(),
            contents: activeSnippet.statement()
          };
          const options = {
            successCallback: function(result) {
              if (result && result.exists) {
                $(document).trigger('info', result.path + ' saved successfully.');
              } else {
                self._ajaxError(result);
              }
            }
          };
          apiHelper.saveSnippetToFile(data, options);
        });
      },
      self.huePubSubId
    );

    huePubSub.subscribe(
      'sql.context.pin',
      contextData => {
        withActiveSnippet(activeSnippet => {
          contextData.tabId = 'context' + activeSnippet.pinnedContextTabs().length;
          activeSnippet.pinnedContextTabs.push(contextData);
          activeSnippet.currentQueryTab(contextData.tabId);
        });
      },
      self.huePubSubId
    );

    huePubSub.subscribe(
      'assist.database.set',
      databaseDef => {
        withActiveSnippet(activeSnippet => {
          activeSnippet.handleAssistSelection(databaseDef);
        });
      },
      self.huePubSubId
    );

    huePubSub.subscribe(
      'assist.database.selected',
      databaseDef => {
        withActiveSnippet(activeSnippet => {
          activeSnippet.handleAssistSelection(databaseDef);
        });
      },
      self.huePubSubId
    );

    self.availableSnippets = komapping.fromJS(options.languages);

    self.editorMode = ko.observable(options.mode === 'editor');

    // Only Spark
    // Could filter out the ones already selected + yarn only or not
    self.availableSessionProperties = ko.pureComputed(() =>
      self.sessionProperties.filter(item => item.name !== '')
    );
  }

  changeURL(url) {
    const self = this;
    if (!self.isNotificationManager()) {
      hueUtils.changeURL(url);
    }
  }

  displayCombinedContent() {
    const self = this;
    if (!self.selectedNotebook()) {
      self.combinedContent('');
    } else {
      let statements = '';
      self
        .selectedNotebook()
        .snippets()
        .forEach(snippet => {
          if (snippet.statement()) {
            if (statements) {
              statements += '\n\n';
            }
            statements += snippet.statement();
          }
        });
      self.combinedContent(statements);
    }
    $('#combinedContentModal' + self.suffix).modal('show');
  }

  getPreviousChartOptions(snippet) {
    return {
      chartLimit: snippet.chartLimit() || snippet.previousChartOptions.chartLimit,
      chartX: snippet.chartX() || snippet.previousChartOptions.chartX,
      chartXPivot: snippet.chartXPivot() || snippet.previousChartOptions.chartXPivot,
      chartYSingle: snippet.chartYSingle() || snippet.previousChartOptions.chartYSingle,
      chartMapType: snippet.chartMapType() || snippet.previousChartOptions.chartMapType,
      chartMapLabel: snippet.chartMapLabel() || snippet.previousChartOptions.chartMapLabel,
      chartMapHeat: snippet.chartMapHeat() || snippet.previousChartOptions.chartMapHeat,
      chartYMulti: snippet.chartYMulti() || snippet.previousChartOptions.chartYMulti,
      chartScope: snippet.chartScope() || snippet.previousChartOptions.chartScope,
      chartTimelineType:
        snippet.chartTimelineType() || snippet.previousChartOptions.chartTimelineType,
      chartSorting: snippet.chartSorting() || snippet.previousChartOptions.chartSorting,
      chartScatterGroup:
        snippet.chartScatterGroup() || snippet.previousChartOptions.chartScatterGroup,
      chartScatterSize: snippet.chartScatterSize() || snippet.previousChartOptions.chartScatterSize
    };
  }

  getSessionProperties(name) {
    const self = this;
    let result = null;
    self.sessionProperties.some(prop => {
      if (prop.name === name) {
        result = prop;
        return true;
      }
    });
    return result;
  }

  getSnippetName(snippetType) {
    const self = this;
    const availableSnippets = self.availableSnippets();
    for (let i = 0; i < availableSnippets.length; i++) {
      if (availableSnippets[i].type() === snippetType) {
        return availableSnippets[i].name();
      }
    }
    return '';
  }

  getSnippetViewSettings(snippetType) {
    const self = this;
    if (self.snippetViewSettings[snippetType]) {
      return self.snippetViewSettings[snippetType];
    }
    return self.snippetViewSettings.default;
  }

  init() {
    const self = this;
    if (self.editorId) {
      self.openNotebook(self.editorId);
    } else if (window.location.getParameter('editor') !== '') {
      self.openNotebook(window.location.getParameter('editor'));
    } else if (self.notebooks.length > 0) {
      self.loadNotebook(self.notebooks[0]); // Old way of loading json for /browse
    } else if (window.location.getParameter('type') !== '') {
      self.newNotebook(window.location.getParameter('type'));
    } else {
      self.newNotebook();
    }
  }

  loadNotebook(notebookRaw, queryTab) {
    const self = this;
    let currentQueries;
    if (self.selectedNotebook() != null) {
      currentQueries = self.selectedNotebook().unload();
    }

    const notebook = new Notebook(self, notebookRaw);

    if (notebook.snippets().length > 0) {
      huePubSub.publish('detach.scrolls', notebook.snippets()[0]);
      notebook.selectedSnippet(notebook.snippets()[notebook.snippets().length - 1].type());
      if (currentQueries != null) {
        notebook.snippets()[0].queries(currentQueries);
      }
      notebook.snippets().forEach(snippet => {
        snippet.aceAutoExpand = false;
        snippet.statement_raw.valueHasMutated();
        if (
          snippet.result.handle().statements_count > 1 &&
          snippet.result.handle().start != null &&
          snippet.result.handle().end != null
        ) {
          const aceLineOffset = snippet.result.handle().aceLineOffset || 0;
          snippet.result.statement_range({
            start: {
              row: snippet.result.handle().start.row + aceLineOffset,
              column: snippet.result.handle().start.column
            },
            end: {
              row: snippet.result.handle().end.row + aceLineOffset,
              column: snippet.result.handle().end.column
            }
          });
          snippet.result.statement_range.valueHasMutated();
        }

        snippet.previousChartOptions = self.getPreviousChartOptions(snippet);
      });

      if (notebook.snippets()[0].result.data().length > 0) {
        $(document).trigger('redrawResults');
      } else if (queryTab) {
        notebook.snippets()[0].currentQueryTab(queryTab);
      }

      if (notebook.isSaved()) {
        notebook.snippets()[0].currentQueryTab('savedQueries');
        if (notebook.snippets()[0].queries().length === 0) {
          notebook.snippets()[0].fetchQueries(); // Subscribe not updating yet
        }
      }
    }

    self.selectedNotebook(notebook);
    huePubSub.publish('check.job.browser');
    huePubSub.publish('recalculate.name.description.width');
  }

  newNotebook(editorType, callback, queryTab) {
    const self = this;
    huePubSub.publish('active.snippet.type.changed', {
      type: editorType,
      isSqlDialect: editorType ? self.getSnippetViewSettings(editorType).sqlDialect : undefined
    });
    $.post(
      '/notebook/api/create_notebook',
      {
        type: editorType || self.editorType(),
        directory_uuid: window.location.getParameter('directory_uuid')
      },
      data => {
        self.loadNotebook(data.notebook);
        if (self.editorMode() && !self.isNotificationManager()) {
          const snippet = self.selectedNotebook().newSnippet(self.editorType());
          if (
            queryTab &&
            ['queryHistory', 'savedQueries', 'queryBuilderTab'].indexOf(queryTab) > -1
          ) {
            snippet.currentQueryTab(queryTab);
          }
          huePubSub.publish('detach.scrolls', self.selectedNotebook().snippets()[0]);
          if (window.location.getParameter('type') === '') {
            hueUtils.changeURLParameter('type', self.editorType());
          }
          huePubSub.publish('active.snippet.type.changed', {
            type: editorType,
            isSqlDialect: editorType
              ? self.getSnippetViewSettings(editorType).sqlDialect
              : undefined
          });
        }

        if (typeof callback !== 'undefined' && callback !== null) {
          callback();
        }
      }
    );
  }

  openNotebook(uuid, queryTab, skipUrlChange, callback) {
    const self = this;
    const deferredOpen = new $.Deferred();
    $.get(
      '/desktop/api2/doc/',
      {
        uuid: uuid,
        data: true,
        dependencies: true
      },
      data => {
        if (data.status === 0) {
          data.data.dependents = data.dependents;
          data.data.can_write = data.user_perms.can_write;
          const notebook = data.data;
          self.loadNotebook(notebook, queryTab);
          if (typeof skipUrlChange === 'undefined' && !self.isNotificationManager()) {
            if (self.editorMode()) {
              self.editorType(data.document.type.substring('query-'.length));
              huePubSub.publish('active.snippet.type.changed', {
                type: self.editorType(),
                isSqlDialect: self.getSnippetViewSettings(self.editorType()).sqlDialect
              });
              self.changeURL(
                self.URLS.editor + '?editor=' + data.document.id + '&type=' + self.editorType()
              );
            } else {
              self.changeURL(self.URLS.notebook + '?notebook=' + data.document.id);
            }
          }
          if (typeof callback !== 'undefined') {
            callback();
          }
          deferredOpen.resolve();
        } else {
          $(document).trigger('error', data.message);
          deferredOpen.reject();
          self.newNotebook();
        }
      }
    );
    return deferredOpen.promise();
  }

  prepareShareModal() {
    const self = this;
    const selectedNotebookUuid = self.selectedNotebook() && self.selectedNotebook().uuid();
    window.shareViewModel.setDocUuid(selectedNotebookUuid);
    window.openShareModal();
  }

  removeSnippet(notebook, snippet) {
    const self = this;
    let hasContent = snippet.statement_raw().length > 0;
    if (!hasContent) {
      snippet.properties().forEach(value => {
        hasContent = hasContent || (ko.isObservable(value) && value().length > 0);
      });
    }
    if (hasContent) {
      self.removeSnippetConfirmation({ notebook: notebook, snippet: snippet });
      $('#removeSnippetModal' + self.suffix).modal('show');
    } else {
      notebook.snippets.remove(snippet);
      window.setTimeout(() => {
        $(document).trigger('editorSizeChanged');
      }, 100);
    }
  }

  saveAsNotebook() {
    const self = this;
    self.selectedNotebook().id(null);
    self.selectedNotebook().uuid(hueUtils.UUID());
    self.selectedNotebook().parentSavedQueryUuid(null);
    self.selectedNotebook().save(() => {
      huePubSub.publish('assist.document.refresh');
    });
  }

  saveNotebook() {
    const self = this;
    self.selectedNotebook().save();
  }

  showContextPopover(field, event) {
    const self = this;
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
      sourceType: self.editorType(),
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

  toggleEditing() {
    const self = this;
    self.isEditing(!self.isEditing());
  }

  toggleEditorMode() {
    const self = this;
    const _notebook = self.selectedNotebook();
    const _newSnippets = [];

    if (self.editorType() !== 'notebook') {
      self.editorType('notebook');
      self.preEditorTogglingSnippet(_notebook.snippets()[0]);
      const _variables = _notebook.snippets()[0].variables();
      const _statementKeys = [];
      // Split statements
      _notebook.type('notebook');
      _notebook
        .snippets()[0]
        .statementsList()
        .forEach(sql_statement => {
          let _snippet;
          if (sql_statement.hashCode() in _notebook.presentationSnippets()) {
            _snippet = _notebook.presentationSnippets()[sql_statement.hashCode()]; // Persist result
            _snippet.variables(_variables);
          } else {
            const _title = [];
            const _statement = [];
            sql_statement
              .trim()
              .split('\n')
              .forEach(line => {
                if (line.trim().startsWith('--') && _statement.length === 0) {
                  _title.push(line.substr(2));
                } else {
                  _statement.push(line);
                }
              });
            _snippet = new Snippet(self, _notebook, {
              type: _notebook.initialType,
              statement_raw: _statement.join('\n'),
              result: {},
              name: _title.join('\n'),
              variables: komapping.toJS(_variables)
            });
            _snippet.variables = _notebook.snippets()[0].variables;
            _snippet.init();
            _notebook.presentationSnippets()[sql_statement.hashCode()] = _snippet;
          }
          _statementKeys.push(sql_statement.hashCode());
          _newSnippets.push(_snippet);
        });
      $.each(_notebook.presentationSnippets(), key => {
        // Dead statements
        if (!key in _statementKeys) {
          delete _notebook.presentationSnippets()[key];
        }
      });
    } else {
      self.editorType(_notebook.initialType);
      // Revert to one statement
      _newSnippets.push(self.preEditorTogglingSnippet());
      _notebook.type('query-' + _notebook.initialType);
    }
    _notebook.snippets(_newSnippets);
    _newSnippets.forEach(snippet => {
      huePubSub.publish('editor.redraw.data', { snippet: snippet });
    });
  }

  togglePresentationMode() {
    const self = this;
    if (self.selectedNotebook().initialType !== 'notebook') {
      self.toggleEditorMode();
    }
  }
}

export default EditorViewModel;
