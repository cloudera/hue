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

import Notebook from 'apps/notebook/notebook';
import Snippet from 'apps/notebook/snippet';
import {
  ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT,
  GET_ACTIVE_SNIPPET_CONNECTOR_EVENT
} from 'apps/editor/events';
import { CONFIG_REFRESHED_TOPIC } from 'config/events';
import { findEditorConnector, getLastKnownConfig } from 'config/hueConfig';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';
import huePubSub from 'utils/huePubSub';
import changeURL from 'utils/url/changeURL';
import changeURLParameter from 'utils/url/changeURLParameter';
import getParameter from 'utils/url/getParameter';
import UUID from 'utils/string/UUID';
import { GLOBAL_ERROR_TOPIC, GLOBAL_INFO_TOPIC } from 'reactComponents/GlobalAlert/events';

export default class NotebookViewModel {
  constructor(options, CoordinatorEditorViewModel, RunningCoordinatorModel) {
    const self = this;

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
    self.isNotificationManager = ko.observable(options.is_notification_manager || false);
    self.editorType = ko.observable(options.editor_type);
    self.editorIcon = ko.pureComputed(() => {
      const foundInterpreter = options.languages.find(
        interpreter => interpreter.type === self.editorType()
      );
      return window.ENABLE_UNIFIED_ANALYTICS && foundInterpreter?.dialect === 'hive'
        ? 'impala'
        : self.editorType();
    });
    self.activeConnector = ko.observable();
    // Observable to hold the editor instance
    self.editorInstance = ko.observable();

    // Method to initialize the editor
    self.initializeEditor = function(element) {
      const editor = ace.edit(element);
      console.log("initializeEditor", editor);
      self.editorInstance(editor);
    };

    const updateConnector = id => {
      if (id) {
        self.activeConnector(findEditorConnector(connector => connector.id === id));
      }
    };

    updateConnector(self.editorType());

    self.sharingEnabled = ko.observable(false);

    const updateFromConfig = hueConfig => {
      self.sharingEnabled(
        hueConfig && (hueConfig.hue_config.is_admin || hueConfig.hue_config.enable_sharing)
      );
    };

    updateFromConfig(getLastKnownConfig());
    huePubSub.subscribe(CONFIG_REFRESHED_TOPIC, updateFromConfig);

    self.editorType.subscribe(newVal => {
      if (!this.activeConnector() || this.activeConnector().id !== newVal) {
        updateConnector(newVal);
      }

      self.editorMode(newVal !== 'notebook');
      changeURLParameter('type', newVal);
      if (self.editorMode()) {
        self.selectedNotebook().fetchHistory(); // Js error if notebook did not have snippets
      }
    });

    self.preEditorTogglingSnippet = ko.observable();
    self.toggleEditorMode = function () {
      const notebook = self.selectedNotebook();
      const newSnippets = [];

      if (self.editorType() !== 'notebook') {
        self.editorType('notebook');
        const sourceSnippet = notebook.snippets()[0];
        self.preEditorTogglingSnippet(sourceSnippet);
        const variables = sourceSnippet.variables();
        const statementKeys = [];
        // Split statements
        notebook.type('notebook');
        const database = sourceSnippet.database();
        sourceSnippet.statementsList().forEach(sql_statement => {
          let presentationSnippet;
          const statementKey = sql_statement.hashCode() + database;
          if (statementKey in notebook.presentationSnippets()) {
            presentationSnippet = notebook.presentationSnippets()[statementKey]; // Persist result
            presentationSnippet.variables(variables);
          } else {
            const titleLines = [];
            const statementLines = [];
            sql_statement
              .trim()
              .split('\n')
              .forEach(line => {
                if (line.trim().startsWith('--') && statementLines.length === 0) {
                  titleLines.push(line.substr(2));
                } else {
                  statementLines.push(line);
                }
              });
            presentationSnippet = new Snippet(self, notebook, {
              type: notebook.initialType,
              database: database,
              statement_raw: statementLines.join('\n'),
              result: {},
              name: titleLines.join('\n'),
              variables: komapping.toJS(variables)
            });
            presentationSnippet.variables = sourceSnippet.variables;
            presentationSnippet.init();
            notebook.presentationSnippets()[statementKey] = presentationSnippet;
          }
          statementKeys.push(statementKey);
          newSnippets.push(presentationSnippet);
        });
        $.each(notebook.presentationSnippets(), key => {
          // Dead statements
          if ((!key) in statementKeys) {
            delete notebook.presentationSnippets()[key];
          }
        });
      } else {
        self.editorType(notebook.initialType);
        // Revert to one statement
        newSnippets.push(self.preEditorTogglingSnippet());
        notebook.type('query-' + notebook.initialType);
      }
      notebook.snippets(newSnippets);
      newSnippets.forEach(snippet => {
        huePubSub.publish('editor.redraw.data', { snippet: snippet });
      });
    };
    self.togglePresentationMode = function () {
      if (self.selectedNotebook().initialType !== 'notebook') {
        self.toggleEditorMode();
      }
    };
    self.editorTypeTitle = ko.pureComputed(() => {
      const foundInterpreter = options.languages.find(
        interpreter => interpreter.type === self.editorType()
      );
      return foundInterpreter?.displayName || foundInterpreter?.name || self.editorType();
    });
    self.selectedNotebook = ko.observable();

    
    this.maxLines = ko.pureComputed(() => {
      return self.editorMode() ? null : 25;
    });
  
    this.minLines = ko.pureComputed(() => {
      return self.editorMode() ? null : 3;
    });
        // Initialize currentSnippetData as a Knockout observable
        this.currentSnippetData = ko.observable();

        // Method to update the current snippet data
        this.updateSnippetData = function(data) {
          this.currentSnippetData(data);
        };

        

    this.getAceEditorConfigs = ko.pureComputed(() => {
      console.log(data)
      return {
        contextTooltip: I18n('Right-click for details'),
        expandStar: I18n('Right-click to expand with columns'),

      }
      // return {
      //   snippet: data,
      //   contextTooltip: self.i18ns.contextTooltip,
      //   expandStar: self.i18ns.expandStar,
      //   highlightedRange: result.statement_range,
      //   readOnly: self.isPresentationMode(),
      //   aceOptions: self.getAceOptions()
      // };
    });


    this.aceEditorConfig = ko.computed(() => {
      const data = this.currentSnippetData();
      if (!data) {
        return {};
      }

      const aceOptions = {
        showLineNumbers: true, // Example option
        showGutter: true,      // Example option
        maxLines: 25,          // Example option
        minLines: 3            // Example option
      };

      return {
        aceEditor: {
          snippet: data,
          aceOptions: aceOptions
        },
        contextTooltip: I18n('Right-click for details'),
        expandStar: I18n('Right-click to expand with columns'),
        highlightedRange: data.result.statement_range,
        readOnly: self.isPresentationMode()
      };
    });

    this.getAceOptions = ko.pureComputed(() => {
      const options = {
        showLineNumbers: self.editorMode(),
        showGutter: self.editorMode()
      };
  
      if (self.editorMode()) {
        options.maxLines = null;
        options.minLines = null;
      } else {
        options.maxLines = 25;
        options.minLines = 3;
      }
  
      return options;
    });

    self.combinedContent = ko.observable();
    self.isPresentationModeEnabled = ko.pureComputed(() => {
      return (
        self.selectedNotebook() &&
        self.selectedNotebook().snippets().length === 1 &&
        self.selectedNotebook().snippets()[0].isSqlDialect()
      );
    });
    self.isResultFullScreenMode = ko.observable(false);



    self.isPresentationMode = ko.computed(() => {
      return self.selectedNotebook() && self.selectedNotebook().isPresentationMode();
    });
    self.isHidingCode = ko.computed(() => {
      return self.selectedNotebook() && self.selectedNotebook().isHidingCode();
    });
    self.successUrl = ko.observable(options.success_url); // Deprecated
    self.isSqlAnalyzerEnabled = ko.observable(options.is_optimizer_enabled);
    self.isNavigatorEnabled = ko.observable(options.is_navigator_enabled);

    self.CoordinatorEditorViewModel = CoordinatorEditorViewModel;
    self.RunningCoordinatorModel = RunningCoordinatorModel;

    self.handleScrollEvent = () => {
      const $mainScrollable = $(MAIN_SCROLLABLE); // Replace MAIN_SCROLLABLE with the actual selector
      const lastScrollTop = $mainScrollable.data('lastScroll');
      const currentScrollTop = $mainScrollable.scrollTop();
  
      if (lastScrollTop && lastScrollTop !== currentScrollTop) {
        $(document).trigger('hideAutocomplete');
      }
      
      $mainScrollable.data('lastScroll', currentScrollTop);
    }

    self.canSave = ko.computed(() => {
      // Saved query or history but history coming from a saved query
      return (
        self.selectedNotebook() &&
        self.selectedNotebook().canWrite() &&
        (self.selectedNotebook().isSaved() ||
          (self.selectedNotebook().isHistory() && self.selectedNotebook().parentSavedQueryUuid()))
      );
    });

    self.ChartTransformers = ChartTransformers;

    // TODO: Drop the SQL source types from the notebook. They're now set in AssistDbPanel.
    self.sqlSourceTypes = [];
    self.availableLanguages = [];

    if (options.languages && options.snippetViewSettings) {
      $.each(options.languages, (idx, language) => {
        self.availableLanguages.push({
          type: language.type,
          name: language.name,
          interface: language.interface
        });
        const viewSettings = options.snippetViewSettings[language.type];
        if (viewSettings && viewSettings.sqlDialect) {
          self.sqlSourceTypes.push({
            type: language.type,
            name: language.name
          });
        }
      });
    }

    const sqlSourceTypes = $.grep(self.sqlSourceTypes, language => {
      return language.type == self.editorType();
    });
    if (sqlSourceTypes.length > 0) {
      self.activeSqlSourceType = sqlSourceTypes[0].type;
    } else {
      self.activeSqlSourceType = null;
    }

    self.displayCombinedContent = function () {
      if (!self.selectedNotebook()) {
        self.combinedContent('');
      } else {
        let statements = '';
        $.each(self.selectedNotebook().snippets(), (index, snippet) => {
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
    };

    self.hideAceEditor = function () {
      $('.ace-filechooser').hide();
    }

    self.connect_auth_session = function() {
      self.selectedNotebook().authSession();
    }

    self.clearNotebookHistory = function() {
      self.selectedNotebook().clearHistory();
    }

    self.isEditing = ko.observable(false);
    self.isEditing.subscribe(() => {
      $(document).trigger('editingToggled');
    });
    self.toggleEditing = function () {
      self.isEditing(!self.isEditing());
    };

    // Define the stop function
    self.handleStop = function (event, ui) {
      const $element = $(event.target);
      console.log("handleStop");
      $element.find('.snippet-body').slideDown('fast', function () {
        console.log("handleStop slideDown");
        $(MAIN_SCROLLABLE).scrollTop(lastWindowScrollPosition);
      });
    }


    self.sortableOptions = {
      template: 'snippet', // Ensure this is a valid template name
      data: self.snippets,
      isEnabled: true,
      options: {
        handle: '.move-widget',
        axis: 'y',
        opacity: 0.8,
        placeholder: 'snippet-move-placeholder',
        greedy: true,
        stop: self.handleStop,
        helper: self.handleHelper
      },
      dragged: self.onSnippetDragged
    };

    self.onSnippetDragged = function(widget) {
      $('.snippet-body').slideDown('fast', function () {
        $(MAIN_SCROLLABLE).scrollTop(lastWindowScrollPosition);
      });
    };
    // Define the helper function
    self.handleHelper = function (event) {
      lastWindowScrollPosition = $(MAIN_SCROLLABLE).scrollTop();
      const $element = $(event.target);
      console.log("handleHelper");
      $element.find('.snippet-body').slideUp('fast', function () {
        console.log("handleHelper slideUp");
        $('.sortable-snippets').sortable('refreshPositions');
      });
      const _par = $('<div>')
        .css('overflow', 'hidden')
        .addClass('card-widget snippet-move-helper')
        .width($element.parents('.snippet').width());
      $('<h2>')
        .addClass('card-heading')
        .html($element.parents('h2').html())
        .appendTo(_par)
        .find('.hover-actions, .snippet-actions')
        .removeClass('hover-actions')
        .removeClass('snippet-actions');
      $('<pre>')
        .addClass('dragging-pre muted')
        .html(ko.dataFor($element.parents('.card-widget')[0]).statement())
        .appendTo(_par);
      _par.css('height', '100px');
      return _par;
    }
    self.authSessionUsername = ko.observable(); // UI popup
    self.authSessionPassword = ko.observable();
    self.authSessionMessage = ko.observable();
    self.authSessionType = ko.observable();
    self.authSessionCallback = ko.observable();

    self.removeSnippetConfirmation = ko.observable();

    self.removeSnippet = function (notebook, snippet) {
      let hasContent = snippet.statement_raw().length > 0;
      if (!hasContent) {
        $.each(snippet.properties(), (key, value) => {
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
    };

    self.assistAvailable = ko.observable(options.assistAvailable);

    self.assistWithoutStorage = ko.observable(false);

    self.isLeftPanelVisible = ko.observable(
      getFromLocalStorage('assist.assist_panel_visible', true)
    );
    self.isLeftPanelVisible.subscribe(val => {
      if (!self.assistWithoutStorage()) {
        setInLocalStorage('assist.assist_panel_visible', val);
      }
    });

    self.isRightPanelAvailable = ko.observable(options.assistAvailable && window.HAS_SQL_ANALYZER);
    self.isRightPanelVisible = ko.observable(
      getFromLocalStorage('assist.right_assist_panel_visible', true)
    );
    self.isRightPanelVisible.subscribe(val => {
      if (!self.assistWithoutStorage()) {
        setInLocalStorage('assist.right_assist_panel_visible', val);
      }
    });

    this.withActiveSnippet = function (callback) {
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

    huePubSub.subscribe(
      GET_ACTIVE_SNIPPET_CONNECTOR_EVENT,
      callback => {
        this.withActiveSnippet(activeSnippet => {
          callback(activeSnippet.connector());
        });
      },
      self.huePubSubId
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
            successCallback: function (result) {
              if (result && result.exists) {
                huePubSub.publish(GLOBAL_INFO_TOPIC, {
                  message: result.path + ' saved successfully.'
                });
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
        this.withActiveSnippet(activeSnippet => {
          contextData.tabId = 'context' + activeSnippet.pinnedContextTabs().length;
          activeSnippet.pinnedContextTabs.push(contextData);
          activeSnippet.currentQueryTab(contextData.tabId);
        });
      },
      self.huePubSubId
    );

    huePubSub.subscribe(
      'assist.database.set',
      entry => {
        this.withActiveSnippet(activeSnippet => {
          activeSnippet.handleAssistSelection(entry);
        });
      },
      self.huePubSubId
    );

    huePubSub.subscribe(
      'assist.database.selected',
      entry => {
        this.withActiveSnippet(activeSnippet => {
          activeSnippet.handleAssistSelection(entry);
        });
      },
      self.huePubSubId
    );

    self.availableSnippets = komapping.fromJS(options.languages);

    self.editorMode = ko.observable(options.mode === 'editor');

    self.getSnippetViewSettings = function (snippetType) {
      if (options.snippetViewSettings[snippetType]) {
        return options.snippetViewSettings[snippetType];
      }
      return options.snippetViewSettings.default;
    };


    self.getEditorCssClasses = function() {
      return {
        'single-snippet-editor ace-container-resizable': self.editorMode()
      };
    };

    self.getEditorStyles = function() {
      const styles = {};
      if (self.selectedNotebook().statementType() !== 'text' || self.selectedNotebook().isPresentationMode()) {
        styles.opacity = '0.75';
      } else {
        styles.opacity = '1';
      }
      if (self.selectedNotebook().editorMode()) {
        styles['min-height'] = '0';
      } else {
        styles['min-height'] = '48px';
      }
      if (self.selectedNotebook().editorMode() && self.selectedNotebook().statementType() !== 'text') {
        styles.top = '60px';
      } else {
        styles.top = '0';
      }
      return styles;
    };
    
    self.isEditorVisible = function() {
      return !self.isResultFullScreenMode() && !(self.isPresentationMode() && self.isHidingCode());
    };


    self.availableSessionProperties = ko.computed(() => {
      // Only Spark
      return ko.utils.arrayFilter(options.session_properties, item => {
        return item.name != ''; // Could filter out the ones already selected + yarn only or not
      });
    });
    self.getSessionProperties = function (name) {
      let _prop = null;
      $.each(options.session_properties, (index, prop) => {
        if (prop.name == name) {
          _prop = prop;
          return;
        }
      });
      return _prop;
    };

    self.getSnippetName = function (snippetType) {
      const availableSnippets = self.availableSnippets();
      for (let i = 0; i < availableSnippets.length; i++) {
        if (availableSnippets[i].type() === snippetType) {
          return availableSnippets[i].name();
        }
      }
      return '';
    };

    self.changeURL = function (url) {
      if (!self.isNotificationManager()) {
        changeURL(url);
      }
    };

    self.init = function () {
      const editorId = options?.editorId || getParameter('editor');
      if (editorId) {
        self.openNotebook(editorId);
      } else if (getParameter('gist') !== '') {
        self.newNotebook(getParameter('type'));
      } else if (getParameter('editor') !== '') {
        self.openNotebook(getParameter('editor'));
      } else if (getParameter('type') !== '') {
        self.newNotebook(getParameter('type'));
      } else {
        self.newNotebook();
      }
    };

    self.loadNotebook = function (notebookRaw, queryTab) {
      let currentQueries;
      if (self.selectedNotebook() != null) {
        self.selectedNotebook().close();
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
    };

    self.getPreviousChartOptions = function (snippet) {
      return {
        chartLimit:
          typeof snippet.chartLimit() !== 'undefined'
            ? snippet.chartLimit()
            : snippet.previousChartOptions.chartLimit,
        chartX:
          typeof snippet.chartX() !== 'undefined'
            ? snippet.chartX()
            : snippet.previousChartOptions.chartX,
        chartXPivot:
          typeof snippet.chartXPivot() !== 'undefined'
            ? snippet.chartXPivot()
            : snippet.previousChartOptions.chartXPivot,
        chartYSingle:
          typeof snippet.chartYSingle() !== 'undefined'
            ? snippet.chartYSingle()
            : snippet.previousChartOptions.chartYSingle,
        chartMapType:
          typeof snippet.chartMapType() !== 'undefined'
            ? snippet.chartMapType()
            : snippet.previousChartOptions.chartMapType,
        chartMapLabel:
          typeof snippet.chartMapLabel() !== 'undefined'
            ? snippet.chartMapLabel()
            : snippet.previousChartOptions.chartMapLabel,
        chartMapHeat:
          typeof snippet.chartMapHeat() !== 'undefined'
            ? snippet.chartMapHeat()
            : snippet.previousChartOptions.chartMapHeat,
        chartYMulti:
          typeof snippet.chartYMulti() !== 'undefined'
            ? snippet.chartYMulti()
            : snippet.previousChartOptions.chartYMulti,
        chartScope:
          typeof snippet.chartScope() !== 'undefined'
            ? snippet.chartScope()
            : snippet.previousChartOptions.chartScope,
        chartTimelineType:
          typeof snippet.chartTimelineType() !== 'undefined'
            ? snippet.chartTimelineType()
            : snippet.previousChartOptions.chartTimelineType,
        chartSorting:
          typeof snippet.chartSorting() !== 'undefined'
            ? snippet.chartSorting()
            : snippet.previousChartOptions.chartSorting,
        chartScatterGroup:
          typeof snippet.chartScatterGroup() !== 'undefined'
            ? snippet.chartScatterGroup()
            : snippet.previousChartOptions.chartScatterGroup,
        chartScatterSize:
          typeof snippet.chartScatterSize() !== 'undefined'
            ? snippet.chartScatterSize()
            : snippet.previousChartOptions.chartScatterSize
      };
    };

    self.openNotebook = function (uuid, queryTab, skipUrlChange, callback, session) {
      const deferredOpen = new $.Deferred();
      $.get(
        '/desktop/api2/doc/',
        {
          uuid: uuid,
          data: true,
          dependencies: true
        },
        data => {
          if (data.status == 0) {
            data.data.dependents = data.dependents;
            data.data.can_write = data.user_perms.can_write;
            if (session) {
              // backend doesn't store session, but can reuse an opened one.
              data.data.sessions = [session];
            }
            const notebook = data.data;
            self.loadNotebook(notebook, queryTab);
            if (typeof skipUrlChange === 'undefined' && !self.isNotificationManager()) {
              if (self.editorMode()) {
                self.editorType(data.document.type.substring('query-'.length));
                if (!self.isNotificationManager()) {
                  huePubSub.publish(ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT, self.activeConnector());
                }
                self.changeURL(
                  self.URLS.editor + '?editor=' + data.document.id + '&type=' + self.editorType()
                );
              } else {
                self.changeURL(self.URLS.notebook + '?notebook=' + data.document.id);
              }
            }
            if (callback) {
              callback();
            }
            deferredOpen.resolve();
          } else {
            huePubSub.publish(GLOBAL_ERROR_TOPIC, { message: data.message });
            deferredOpen.reject();
            self.newNotebook();
          }
        }
      );
      return deferredOpen.promise();
    };

    self.newNotebook = function (editorType, callback, queryTab) {
      const connectorId = editorType || options.editor_type;

      if (!self.isNotificationManager()) {
        self.activeConnector(findEditorConnector(connector => connector.id === connectorId));
        huePubSub.publish(ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT, self.activeConnector());
      }

      $.post(
        '/notebook/api/create_notebook',
        {
          type: connectorId,
          directory_uuid: getParameter('directory_uuid'),
          gist: self.isNotificationManager() ? undefined : getParameter('gist')
        },
        data => {
          self.loadNotebook(data.notebook);
          if (self.editorMode() && !self.isNotificationManager()) {
            const snippet =
              self.selectedNotebook().snippets().length === 0
                ? self.selectedNotebook().newSnippet(self.editorType())
                : self.selectedNotebook().snippets()[0];
            if (
              queryTab &&
              ['queryHistory', 'savedQueries', 'queryBuilderTab'].indexOf(queryTab) > -1
            ) {
              snippet.currentQueryTab(queryTab);
            }
            huePubSub.publish('detach.scrolls', self.selectedNotebook().snippets()[0]);
            if (getParameter('type') === '') {
              changeURLParameter('type', self.editorType());
            }
            if (!self.isNotificationManager()) {
              huePubSub.publish(ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT, self.activeConnector());
            }
          }

          if (callback) {
            callback();
          }
        }
      );
    };

        // New method created to handle the click event
    self.createNewDocument = function() {
          hueUtils.removeURLParameter('editor');
  
          // Assuming newNotebook is a function available in self context
          // and selectedNotebook and editorType are observables in the ViewModel
          var currentQueryTab = self.selectedNotebook() ? 
              self.selectedNotebook().snippets()[0].currentQueryTab() : 
              null;
              
          newNotebook(self.editorType(), null, currentQueryTab);
      };
  
      self.handlePublish = function() {
        var mode = self.editorMode();
        var topic = mode ? 'query-' + self.editorType() : self.editorType();
        huePubSub.publish('assist.show.documents', topic);
    };

    self.editorDisplayText = ko.computed(function() {
      return self.editorMode() ? I18n('Queries') : I18n('Notebooks');
  });
  self.handleSaveButtonClick = ko.pureComputed(() => {
    // self.handleSaveButtonClick = () => {
      if (self.canSave()) {
          this.saveNotebook();
      } else {
          $('#saveAsModal' + suffix).modal('show');
      }
    });


    self.openNewNotebook = function() {
      self.openNotebook(self.selectedNotebook().parentSavedQueryUuid());
    };

    self.handleDocumentShow = function() {
      // The logic to execute when the event is triggered.
      var mode = self.editorMode() ? 'query-' + self.editorType() : self.editorType();
      huePubSub.publish("assist.show.documents", mode)
      // Perform actions with mode
        console.log('Document show with mode:', mode);
    };

    self.saveNotebook = function () {
      self.selectedNotebook().save();
    };

    self.saveAsNotebook = function () {
      self.selectedNotebook().id(null);
      self.selectedNotebook().uuid(UUID());
      self.selectedNotebook().parentSavedQueryUuid(null);
      self.selectedNotebook().save(() => {
        huePubSub.publish('assist.document.refresh');
      });
    };

    self.showContextPopover = function (field, event) {
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
    };
  }

  snippetContainerCssClasses() {
    return {
      'is-editing': self.isEditing(),
      'margin-left-10': self.isPresentationMode()
    };
  };

  prepareShareModal() {
    const selectedNotebookUuid = this.selectedNotebook() && this.selectedNotebook().uuid();
    if (selectedNotebookUuid) {
      huePubSub.publish('doc.show.share.modal', selectedNotebookUuid);
    }
  }
}
