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
import { markdown } from 'markdown';

import AceAutocompleteWrapper from 'apps/notebook/aceAutocompleteWrapper';
import apiHelper from 'api/apiHelper';
import dataCatalog from 'catalog/dataCatalog';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import Result from 'apps/notebook/result';
import Session from 'apps/notebook/session';
import sqlStatementsParser from 'parse/sqlStatementsParser';
import { SHOW_EVENT as SHOW_GIST_MODAL_EVENT } from 'ko/components/ko.shareGistModal';
import { cancelActiveRequest } from 'api/apiUtils';
import { ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT } from 'apps/notebook2/events';
import { findEditorConnector } from 'utils/hueConfig';
import {
  ASSIST_GET_DATABASE_EVENT,
  ASSIST_GET_SOURCE_EVENT,
  ASSIST_SET_SOURCE_EVENT
} from 'ko/components/assist/events';
import { POST_FROM_LOCATION_WORKER_EVENT } from 'sql/sqlWorkerHandler';
import {
  ACTIVE_STATEMENT_CHANGED_EVENT,
  CURSOR_POSITION_CHANGED_EVENT,
  REFRESH_STATEMENT_LOCATIONS_EVENT
} from 'ko/bindings/ace/aceLocationHandler';

const NOTEBOOK_MAPPING = {
  ignore: [
    'ace',
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

const COMPATIBILITY_SOURCE_PLATFORMS = {
  teradata: { name: 'Teradata', value: 'teradata' },
  oracle: { name: 'Oracle', value: 'oracle' },
  netezza: { name: 'Netezza', value: 'netezza' },
  impala: { name: 'Impala', value: 'impala' },
  hive: { name: 'Hive', value: 'hive' },
  db2: { name: 'DB2', value: 'db2' },
  greenplum: { name: 'Greenplum', value: 'greenplum' },
  mysql: { name: 'MySQL', value: 'mysql' },
  postgresql: { name: 'PostgreSQL', value: 'postgresql' },
  informix: { name: 'Informix', value: 'informix' },
  sqlserver: { name: 'SQL Server', value: 'sqlserver' },
  sybase: { name: 'Sybase', value: 'sybase' },
  access: { name: 'Access', value: 'access' },
  firebird: { name: 'Firebird', value: 'firebird' },
  ansisql: { name: 'ANSISQL', value: 'ansisql' },
  generic: { name: 'Generic', value: 'generic' }
};

const COMPATIBILITY_TARGET_PLATFORMS = {
  impala: { name: 'Impala', value: 'impala' },
  hive: { name: 'Hive', value: 'hive' }
};

const getDefaultSnippetProperties = function (snippetType) {
  const properties = {};

  if (snippetType == 'jar' || snippetType == 'py') {
    properties['driverCores'] = '';
    properties['executorCores'] = '';
    properties['numExecutors'] = '';
    properties['queue'] = '';
    properties['archives'] = [];
    properties['files'] = [];
  }

  if (snippetType == 'java') {
    properties['archives'] = [];
    properties['files'] = [];
    properties['capture_output'] = false;
  }

  if (snippetType == 'shell') {
    properties['archives'] = [];
    properties['files'] = [];
  }

  if (snippetType == 'mapreduce') {
    properties['app_jar'] = '';
    properties['hadoopProperties'] = [];
    properties['jars'] = [];
    properties['files'] = [];
    properties['archives'] = [];
  }

  if (snippetType == 'spark2') {
    properties['app_name'] = '';
    properties['class'] = '';
    properties['jars'] = [];
    properties['spark_opts'] = [];
    properties['spark_arguments'] = [];
    properties['files'] = [];
  }

  if (snippetType == 'sqoop1') {
    properties['files'] = [];
  }

  if (snippetType == 'jar' || snippetType == 'java') {
    properties['app_jar'] = '';
    properties['class'] = '';
    properties['arguments'] = [];
  } else if (snippetType == 'distcp') {
    properties['source_path'] = '';
    properties['destination_path'] = '';
  } else if (snippetType == 'shell') {
    properties['command_path'] = '';
    properties['arguments'] = [];
    properties['env_var'] = [];
    properties['capture_output'] = true;
  } else if (snippetType == 'py') {
    properties['py_file'] = '';
    properties['arguments'] = [];
  } else if (snippetType == 'hive') {
    properties['settings'] = [];
    properties['files'] = [];
    properties['functions'] = [];
    properties['arguments'] = [];
  } else if (snippetType == 'impala') {
    properties['settings'] = [];
  } else if (snippetType == 'pig') {
    properties['parameters'] = [];
    properties['hadoopProperties'] = [];
    properties['resources'] = [];
  }

  return properties;
};

const ERROR_REGEX = /line ([0-9]+)(\:([0-9]+))?/i;

class Snippet {
  constructor(vm, notebook, snippet) {
    const self = this;

    self.id = ko.observable(
      typeof snippet.id != 'undefined' && snippet.id != null ? snippet.id : hueUtils.UUID()
    );
    self.name = ko.observable(
      typeof snippet.name != 'undefined' && snippet.name != null ? snippet.name : ''
    );
    self.type = ko.observable(
      typeof snippet.type != 'undefined' && snippet.type != null ? snippet.type : 'hive'
    );

    self.connector = ko.observable();

    const updateConnector = id => {
      if (id) {
        self.connector(findEditorConnector(connector => connector.id === id));
      }
    };

    updateConnector(self.type());

    self.type.subscribe(type => {
      if (!self.connector() || self.connector().id !== type) {
        updateConnector(type);
      }
      self.status('ready');
    });

    self.isSqlDialect = ko.pureComputed(() => {
      return vm.getSnippetViewSettings(self.type()).sqlDialect;
    });

    self.connector = ko.pureComputed(() => {
      // To support optimizer changes in editor v2
      return {
        optimizer: self.type() === 'hive' || self.type() === 'impala' ? 'api' : 'off',
        type: self.type(),
        id: self.type(),
        dialect: self.type(),
        is_sql: self.isSqlDialect()
      };
    });

    self.dialect = ko.pureComputed(() => this.connector().dialect);

    self.isBatchable = ko.computed(() => {
      return (
        self.type() == 'hive' ||
        self.type() == 'impala' ||
        $.grep(vm.availableLanguages, language => {
          return (
            language.type == self.type() &&
            (language.interface == 'oozie' || language.interface == 'sqlalchemy')
          );
        }).length > 0
      );
    });

    self.autocompleteSettings = {
      temporaryOnly: false
    };

    // Ace stuff
    self.aceCursorPosition = ko.observable(notebook.isHistory() ? snippet.aceCursorPosition : null);

    let aceEditor = null;

    self.ace = function (newVal) {
      if (newVal) {
        aceEditor = newVal;
        if (!notebook.isPresentationMode()) {
          aceEditor.focus();
        }
      }
      return aceEditor;
    };
    self.errors = ko.observableArray([]);

    self.aceErrorsHolder = ko.observableArray([]);
    self.aceWarningsHolder = ko.observableArray([]);

    self.aceErrors = ko.pureComputed(() => {
      return self.showOptimizer() ? self.aceErrorsHolder() : [];
    });
    self.aceWarnings = ko.pureComputed(() => {
      return self.showOptimizer() ? self.aceWarningsHolder() : [];
    });

    self.availableSnippets = vm.availableSnippets();
    self.inFocus = ko.observable(false);

    self.inFocus.subscribe(newValue => {
      if (newValue) {
        huePubSub.publish(ACTIVE_SNIPPET_CONNECTOR_CHANGED_EVENT, self.connector());
      }
    });

    self.editorMode = vm.editorMode;

    self.getAceMode = function () {
      return vm.getSnippetViewSettings(self.type()).aceMode;
    };

    self.dbSelectionVisible = ko.observable(false);

    self.showExecutionAnalysis = ko.observable(false);

    self.getPlaceHolder = function () {
      return vm.getSnippetViewSettings(self.type()).placeHolder;
    };

    // namespace and compute might be initialized as empty object {}
    self.namespace = ko.observable(
      snippet.namespace && snippet.namespace.id ? snippet.namespace : undefined
    );
    self.compute = ko.observable(
      snippet.compute && snippet.compute.id ? snippet.compute : undefined
    );

    self.whenContextSet = function () {
      let namespaceSub;
      const namespaceDeferred = $.Deferred();
      if (self.namespace()) {
        namespaceDeferred.resolve(self.namespace());
      } else {
        namespaceSub = self.namespace.subscribe(newVal => {
          if (newVal) {
            namespaceDeferred.resolve(newVal);
            namespaceSub.dispose();
          }
        });
      }
      let computeSub;
      const computeDeferred = $.Deferred();
      if (self.compute()) {
        computeDeferred.resolve(self.compute());
      } else {
        computeSub = self.compute.subscribe(newVal => {
          if (newVal) {
            computeDeferred.resolve(newVal);
            computeSub.dispose();
          }
        });
      }

      const result = $.when(namespaceDeferred, computeDeferred);

      result.dispose = function () {
        if (namespaceSub) {
          namespaceSub.dispose();
        }
        if (computeSub) {
          computeSub.dispose();
        }
        namespaceDeferred.reject();
        computeDeferred.reject();
      };

      return result;
    };

    self.availableDatabases = ko.observableArray();
    self.database = ko.observable();
    let previousDatabase = null;

    self.database.subscribe(newValue => {
      if (newValue !== null) {
        apiHelper.setInTotalStorage('editor', 'last.selected.database', newValue);
        if (previousDatabase !== null && previousDatabase !== newValue) {
          huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, self.id());
        }
        previousDatabase = newValue;
      }
    });

    self.database(
      typeof snippet.database !== 'undefined' && snippet.database != null ? snippet.database : null
    );

    // History is currently in Notebook, same with saved queries by snippets, might be better in assist
    self.currentQueryTab = ko.observable(
      typeof snippet.currentQueryTab != 'undefined' && snippet.currentQueryTab != null
        ? snippet.currentQueryTab
        : 'queryHistory'
    );
    self.pinnedContextTabs = ko.observableArray(
      typeof snippet.pinnedContextTabs != 'undefined' && snippet.pinnedContextTabs != null
        ? snippet.pinnedContextTabs
        : []
    );

    self.removeContextTab = function (context) {
      if (context.tabId === self.currentQueryTab()) {
        self.currentQueryTab('queryHistory');
      }
      self.pinnedContextTabs.remove(context);
    };

    self.errorLoadingQueries = ko.observable(false);
    self.loadingQueries = ko.observable(false);

    self.queriesHasErrors = ko.observable(false);
    self.queriesCurrentPage = ko.observable(
      vm.selectedNotebook() && vm.selectedNotebook().snippets().length > 0
        ? vm.selectedNotebook().snippets()[0].queriesCurrentPage()
        : 1
    );
    self.queriesTotalPages = ko.observable(
      vm.selectedNotebook() && vm.selectedNotebook().snippets().length > 0
        ? vm.selectedNotebook().snippets()[0].queriesTotalPages()
        : 1
    );
    self.queries = ko.observableArray([]);

    self.queriesFilter = ko.observable('');
    self.queriesFilterVisible = ko.observable(false);
    self.queriesFilter.extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 900 } });
    self.queriesFilter.subscribe(val => {
      self.fetchQueries();
    });

    let lastFetchQueriesRequest = null;

    self.fetchQueries = function () {
      cancelActiveRequest(lastFetchQueriesRequest);

      const QUERIES_PER_PAGE = 50;
      lastQueriesPage = self.queriesCurrentPage();
      self.loadingQueries(true);
      self.queriesHasErrors(false);
      lastFetchQueriesRequest = apiHelper.searchDocuments({
        successCallback: function (result) {
          self.queriesTotalPages(Math.ceil(result.count / QUERIES_PER_PAGE));
          self.queries(komapping.fromJS(result.documents)());
          self.loadingQueries(false);
          self.queriesHasErrors(false);
        },
        errorCallback: function () {
          self.loadingQueries(false);
          self.queriesHasErrors(true);
        },
        page: self.queriesCurrentPage(),
        limit: QUERIES_PER_PAGE,
        type: 'query-' + self.type(),
        query: self.queriesFilter(),
        include_trashed: false
      });
    };

    let lastQueriesPage = 1;
    self.currentQueryTab.subscribe(newValue => {
      huePubSub.publish('redraw.fixed.headers');
      huePubSub.publish('current.query.tab.switched', newValue);
      if (
        newValue === 'savedQueries' &&
        (self.queries().length === 0 || lastQueriesPage !== self.queriesCurrentPage())
      ) {
        self.fetchQueries();
      }
    });

    self.prevQueriesPage = function () {
      if (self.queriesCurrentPage() !== 1) {
        self.queriesCurrentPage(self.queriesCurrentPage() - 1);
        self.fetchQueries();
      }
    };

    self.nextQueriesPage = function () {
      if (self.queriesCurrentPage() !== self.queriesTotalPages()) {
        self.queriesCurrentPage(self.queriesCurrentPage() + 1);
        self.fetchQueries();
      }
    };

    huePubSub.publish(ASSIST_GET_SOURCE_EVENT, source => {
      if (source !== self.type()) {
        huePubSub.publish(ASSIST_SET_SOURCE_EVENT, self.type());
      }
    });

    let ignoreNextAssistDatabaseUpdate = false;
    self.handleAssistSelection = function (entry) {
      if (ignoreNextAssistDatabaseUpdate) {
        ignoreNextAssistDatabaseUpdate = false;
      } else if (entry.getConnector().id === self.connector().id) {
        if (self.namespace() !== entry.namespace) {
          self.namespace(entry.namespace);
        }
        if (self.database() !== entry.name) {
          self.database(entry.name);
        }
      }
    };

    if (!self.database()) {
      huePubSub.publish(ASSIST_GET_DATABASE_EVENT, {
        connector: self.connector(),
        callback: entry => {
          self.handleAssistSelection(entry);
        }
      });
    }

    self.statementType = ko.observable(
      typeof snippet.statementType != 'undefined' && snippet.statementType != null
        ? snippet.statementType
        : 'text'
    );
    self.statementTypes = ko.observableArray(['text', 'file']); // Maybe computed later for Spark
    if (!vm.editorMode()) {
      self.statementTypes.push('document');
    }
    self.statementPath = ko.observable(
      typeof snippet.statementPath != 'undefined' && snippet.statementPath != null
        ? snippet.statementPath
        : ''
    );
    self.statementPath.subscribe(newVal => {
      self.getExternalStatement();
    });
    self.externalStatementLoaded = ko.observable(false);
    self.getExternalStatement = function () {
      self.externalStatementLoaded(false);
      $.post(
        '/notebook/api/get_external_statement',
        {
          notebook: komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext())
        },
        data => {
          if (data.status == 0) {
            self.externalStatementLoaded(true);
            self.statement_raw(data.statement);
            self.ace().setValue(self.statement_raw(), 1);
          } else {
            self._ajaxError(data);
          }
        }
      );
    };
    self.associatedDocumentLoading = ko.observable(true);
    self.associatedDocument = ko.observable();
    self.associatedDocumentUuid = ko.observable(
      typeof snippet.associatedDocumentUuid != 'undefined' && snippet.associatedDocumentUuid != null
        ? snippet.associatedDocumentUuid
        : null
    );
    self.associatedDocumentUuid.subscribe(val => {
      if (val !== '') {
        self.getExternalStatement();
      } else {
        self.statement_raw('');
        self.ace().setValue('', 1);
      }
    });
    self.statement_raw = ko.observable(
      typeof snippet.statement_raw != 'undefined' && snippet.statement_raw != null
        ? snippet.statement_raw
        : ''
    );
    self.selectedStatement = ko.observable('');
    self.positionStatement = ko.observable(null);
    self.lastExecutedStatement = ko.observable(null);
    self.statementsList = ko.observableArray();

    huePubSub.subscribe(CURSOR_POSITION_CHANGED_EVENT, details => {
      if (details.editorId === self.id()) {
        self.aceCursorPosition(details.position);
      }
    });

    huePubSub.subscribe(
      ACTIVE_STATEMENT_CHANGED_EVENT,
      statementDetails => {
        if (self.ace() && self.ace().container.id === statementDetails.id) {
          for (let i = statementDetails.precedingStatements.length - 1; i >= 0; i--) {
            if (statementDetails.precedingStatements[i].database) {
              self.availableDatabases().some(availableDatabase => {
                if (
                  availableDatabase.toLowerCase() ===
                  statementDetails.precedingStatements[i].database.toLowerCase()
                ) {
                  self.database(availableDatabase);
                  return true;
                }
              });
              break;
            }
          }
          if (statementDetails.activeStatement) {
            self.positionStatement(statementDetails.activeStatement);
          } else {
            self.positionStatement(null);
          }

          if (statementDetails.activeStatement) {
            const _statements = [];
            statementDetails.precedingStatements.forEach(statement => {
              _statements.push(statement.statement);
            });
            _statements.push(statementDetails.activeStatement.statement);
            statementDetails.followingStatements.forEach(statement => {
              _statements.push(statement.statement);
            });
            self.statementsList(_statements); // Or fetch on demand via editor.refresh.statement.locations and remove observableArray?
          } else {
            self.statementsList([]);
          }
          if (!notebook.isPresentationModeInitialized()) {
            if (notebook.isPresentationModeDefault()) {
              // When switching to presentation mode, the snippet in non presentation mode cannot get status notification.
              // On initiailization, status is set to loading and does not get updated, because we moved to presentation mode.
              self.status('ready');
            }
            // Changing to presentation mode requires statementsList to be initialized. statementsList is initialized asynchronously.
            // When presentation mode is default, we cannot change before statementsList has been calculated.
            // Cleaner implementation would be to make toggleEditorMode statementsList asynchronous
            // However this is currently impossible due to delete _notebook.presentationSnippets()[key];
            notebook.isPresentationModeInitialized(true);
            notebook.isPresentationMode(notebook.isPresentationModeDefault());
          }
        }
      },
      vm.huePubSubId
    );

    self.aceSize = ko.observable(
      typeof snippet.aceSize != 'undefined' && snippet.aceSize != null ? snippet.aceSize : 100
    );
    // self.statement_raw.extend({ rateLimit: 150 }); // Should prevent lag from typing but currently send the old query when using the key shortcut
    self.status = ko.observable(
      typeof snippet.status != 'undefined' && snippet.status != null ? snippet.status : 'loading'
    );
    self.statusForButtons = ko.observable('executed');

    self.properties = ko.observable(
      komapping.fromJS(
        typeof snippet.properties != 'undefined' && snippet.properties != null
          ? snippet.properties
          : getDefaultSnippetProperties(self.type())
      )
    );
    self.hasProperties = ko.computed(() => {
      return Object.keys(komapping.toJS(self.properties())).length > 0;
    });

    self.viewSettings = ko.computed(() => {
      return vm.getSnippetViewSettings(self.type());
    });

    const previousProperties = {};
    self.type.subscribe(
      oldValue => {
        previousProperties[oldValue] = self.properties();
      },
      null,
      'beforeChange'
    );

    self.type.subscribe(newValue => {
      if (typeof previousProperties[newValue] != 'undefined') {
        self.properties(previousProperties[newValue]);
      } else {
        self.properties(komapping.fromJS(getDefaultSnippetProperties(newValue)));
      }
      self.result.clear();
      window.setTimeout(() => {
        if (self.ace() !== null) {
          self.ace().focus();
        }
      }, 100);
    });
    if (snippet.variables) {
      snippet.variables.forEach(variable => {
        variable.meta = (typeof variable.defaultValue === 'object' && variable.defaultValue) || {
          type: 'text',
          placeholder: ''
        };
        variable.value = variable.value || '';
        variable.type = variable.type || 'text';
        variable.sample = [];
        variable.sampleUser = variable.sampleUser || [];
        variable.path = variable.path || '';
        variable.step = '';
        delete variable.defaultValue;
      });
    }
    self.variables = komapping.fromJS(
      typeof snippet.variables != 'undefined' && snippet.variables != null ? snippet.variables : []
    );
    self.variables.subscribe(newValue => {
      $(document).trigger('updateResultHeaders', self);
    });
    self.hasCurlyBracketParameters = ko.computed(() => {
      return self.type() != 'pig';
    });
    self.getPigParameters = function () {
      const params = {};
      const variables = self.statement_raw().match(/([^\\]|^)\$[^\d'"](\w*)/g);
      const declares = self.statement_raw().match(/%declare +([^ ])+/gi);
      const defaults = self.statement_raw().match(/%default +([^;])+/gi);
      const macro_defines = self.statement_raw().match(/define [^ ]+ *\(([^\)]*)\)/gi); // no multiline
      const macro_returns = self.statement_raw().match(/returns +([^\{]*)/gi); // no multiline

      if (variables) {
        $.each(variables, (index, param) => {
          const p = param.substring(param.indexOf('$') + 1);
          params[p] = '';
        });
      }
      if (declares) {
        $.each(declares, (index, param) => {
          param = param.match(/(\w+)/g);
          if (param && param.length >= 2) {
            delete params[param[1]];
          }
        });
      }
      if (defaults) {
        $.each(defaults, (index, param) => {
          const line = param.match(/(\w+)/g);
          if (line && line.length >= 2) {
            const name = line[1];
            params[name] = param.substring(param.indexOf(name) + name.length + 1);
          }
        });
      }
      if (macro_defines) {
        $.each(macro_defines, (index, params_line) => {
          const param_line = params_line.match(/(\w+)/g);
          if (param_line && param_line.length > 2) {
            $.each(param_line, (index, param) => {
              if (index >= 2) {
                // Skips define NAME
                delete params[param];
              }
            });
          }
        });
      }
      if (macro_returns) {
        $.each(macro_returns, (index, params_line) => {
          const param_line = params_line.match(/(\w+)/g);
          if (param_line) {
            $.each(param_line, (index, param) => {
              if (index >= 1) {
                // Skip returns
                delete params[param];
              }
            });
          }
        });
      }

      return params;
    };
    self.variableNames = ko.computed(() => {
      let match,
        matches = {},
        matchList;
      if (self.type() == 'pig') {
        matches = self.getPigParameters();
      } else {
        const re = /(?:^|\W)\${(\w*)\=?([^{}]*)}/g;
        const reComment = /(^\s*--.*)|(\/\*[\s\S]*?\*\/)/gm;
        const reList = /(?!\s*$)\s*(?:(?:([^,|()\\]*)\(\s*([^,|()\\]*)\)(?:\\[\S\s][^,|()\\]*)?)|([^,|\\]*(?:\\[\S\s][^,|\\]*)*))\s*(?:,|\||$)/g;
        const statement = self.statement_raw();
        let matchComment = reComment.exec(statement);
        // if re is n & reComment is m
        // finding variables is O(n+m)
        while ((match = re.exec(statement))) {
          while (matchComment && match.index > matchComment.index + matchComment[0].length) {
            // Comments before our match
            matchComment = reComment.exec(statement);
          }
          const isWithinComment = matchComment && match.index >= matchComment.index;
          if (isWithinComment) {
            continue;
          }

          // If 1 match, text value
          // If multiple matches, list value
          const value = { type: 'text', placeholder: '' };
          while ((matchList = reList.exec(match[2]))) {
            const option = {
              text: matchList[2] || matchList[3],
              value: matchList[3] || matchList[1]
            };
            option.text = option.text && option.text.trim();
            option.value =
              option.value &&
              option.value.trim().replace(',', ',').replace('(', '(').replace(')', ')');

            if (value.placeholder || matchList[2]) {
              if (!value.options) {
                value.options = [];
                value.type = 'select';
              }
              value.options.push(option);
            }
            if (!value.placeholder) {
              value.placeholder = option.value;
            }
          }
          const isPlaceholderInOptions =
            !value.options ||
            value.options.some(current => {
              return current.value == value.placeholder;
            });
          if (!isPlaceholderInOptions) {
            value.options.unshift({ text: value.placeholder, value: value.placeholder });
          }
          matches[match[1]] = matches[match[1]] || value;
        }
      }
      return $.map(matches, (match, key) => {
        const isMatchObject = typeof matches[key] === 'object';
        const meta = isMatchObject ? matches[key] : { type: 'text', placeholder: matches[key] };
        return { name: key, meta: meta };
      });
    });
    self.variableValues = {};
    self.variableNames.extend({ rateLimit: 150 });
    self.variableNames.subscribe(newVal => {
      const variablesLength = self.variables().length;
      const diffLengthVariables = variablesLength - newVal.length;
      const needsMore = diffLengthVariables < 0;
      const needsLess = diffLengthVariables > 0;
      self.variableValues = self.variables().reduce((variableValues, variable) => {
        if (!variableValues[variable.name()]) {
          variableValues[variable.name()] = { sampleUser: [] };
        }
        variableValues[variable.name()].value = variable.value();
        variableValues[variable.name()].sampleUser = variable.sampleUser();
        variableValues[variable.name()].catalogEntry = variable.catalogEntry;
        variableValues[variable.name()].path = variable.path();
        variableValues[variable.name()].type = variable.type();
        return variableValues;
      }, self.variableValues);
      if (needsMore) {
        for (let i = 0, length = Math.abs(diffLengthVariables); i < length; i++) {
          self.variables.push(
            komapping.fromJS({
              name: '',
              value: '',
              meta: { type: 'text', placeholder: '', options: [] },
              sample: [],
              sampleUser: [],
              type: 'text',
              step: '',
              path: ''
            })
          );
        }
      } else if (needsLess) {
        self.variables.splice(self.variables().length - diffLengthVariables, diffLengthVariables);
      }
      newVal.forEach((item, index) => {
        const variable = self.variables()[index];
        variable.name(item.name);
        setTimeout(() => {
          variable.value(
            self.variableValues[item.name]
              ? self.variableValues[item.name].value
              : (!needsMore && variable.value()) || ''
          );
        }, 0);
        variable.meta = komapping.fromJS(item.meta, {}, variable.meta);
        variable.sample(
          variable.meta.options
            ? variable.meta.options().concat(variable.sampleUser())
            : variable.sampleUser()
        );
        variable.sampleUser(
          self.variableValues[item.name] ? self.variableValues[item.name].sampleUser : []
        );
        variable.type(
          self.variableValues[item.name] ? self.variableValues[item.name].type || 'text' : 'text'
        );
        variable.path(
          self.variableValues[item.name] ? self.variableValues[item.name].path || '' : ''
        );
        variable.catalogEntry =
          self.variableValues[item.name] && self.variableValues[item.name].catalogEntry;
      });
    });

    const activeSourcePromises = [];
    huePubSub.subscribe(POST_FROM_LOCATION_WORKER_EVENT, e => {
      while (activeSourcePromises.length) {
        const promise = activeSourcePromises.pop();
        if (promise.cancel) {
          promise.cancel();
        }
      }
      const oLocations = e.data.locations
        .filter(location => {
          return location.type === 'variable' && location.colRef;
        })
        .reduce((variables, location) => {
          const re = /\${(\w*)\=?([^{}]*)}/g;
          const name = re.exec(location.value)[1];
          variables[name] = location;
          return variables;
        }, {});
      const updateVariableType = function (variable, sourceMeta) {
        let type;
        if (sourceMeta && sourceMeta.type) {
          type = sourceMeta.type.toLowerCase();
        } else {
          type = 'string';
        }
        const variablesValues = {};
        const value = variable.value();
        switch (type) {
          case 'timestamp':
            variablesValues.type = 'datetime-local';
            variablesValues.step = '1';
            variablesValues.value =
              (value && moment.utc(value).format('YYYY-MM-DD HH:mm:ss.S')) ||
              moment(Date.now()).format('YYYY-MM-DD 00:00:00.0');
            break;
          case 'decimal':
          case 'double':
          case 'float':
            variablesValues.type = 'number';
            variablesValues.step = 'any';
            break;
          case 'int':
          case 'smallint':
          case 'tinyint':
          case 'bigint':
            variablesValues.type = 'number';
            variablesValues.step = '1';
            break;
          case 'date':
            variablesValues.type = 'date';
            variablesValues.step = '';
            variablesValues.value =
              (value && moment.utc(value).format('YYYY-MM-DD')) ||
              moment(Date.now()).format('YYYY-MM-DD');
            break;
          case 'boolean':
            variablesValues.type = 'checkbox';
            variablesValues.step = '';
            break;
          default:
            variablesValues.type = 'text';
            variablesValues.step = '';
        }
        if (variablesValues.value) {
          setTimeout(() => {
            variable.value(variablesValues.value);
          }, 0);
        }
        variable.type(variablesValues.type);
        variable.step(variablesValues.step);
      };
      self.variables().forEach(variable => {
        if (oLocations[variable.name()]) {
          activeSourcePromises.push(
            oLocations[variable.name()].resolveCatalogEntry({ cancellable: true }).done(entry => {
              variable.path(entry.path.join('.'));
              variable.catalogEntry = entry;

              activeSourcePromises.push(
                entry
                  .getSourceMeta({
                    silenceErrors: true,
                    cancellable: true
                  })
                  .then(updateVariableType.bind(self, variable))
              );
            })
          );
        } else {
          updateVariableType(variable, {
            type: 'text'
          });
        }
      });
    });
    self.statement = ko.computed(() => {
      let statement = self.isSqlDialect()
        ? self.selectedStatement()
          ? self.selectedStatement()
          : self.positionStatement() !== null
          ? self.positionStatement().statement
          : self.statement_raw()
        : self.statement_raw();
      const variables = self.variables().reduce((variables, variable) => {
        variables[variable.name()] = variable;
        return variables;
      }, {});
      if (self.variables().length) {
        const variablesString = self
          .variables()
          .map(variable => {
            return variable.name();
          })
          .join('|');
        statement = statement.replace(
          RegExp(
            '([^\\\\])?\\$' +
              (self.hasCurlyBracketParameters() ? '{(' : '(') +
              variablesString +
              ')(=[^}]*)?' +
              (self.hasCurlyBracketParameters() ? '}' : ''),
            'g'
          ),
          (match, p1, p2) => {
            const variable = variables[p2];
            const pad =
              variable.type() == 'datetime-local' && variable.value().length == 16 ? ':00' : ''; // Chrome drops the seconds from the timestamp when it's at 0 second.
            const value = variable.value();
            const isValuePresent = //If value is string there is a need to check whether it is empty
              typeof value === 'string' ? value : value !== undefined && value !== null;
            return (
              p1 +
              (isValuePresent
                ? value + pad
                : variable.meta.placeholder && variable.meta.placeholder())
            );
          }
        );
      }
      return statement;
    });

    self.result = new Result(snippet, snippet.result);
    if (!self.result.hasSomeResults()) {
      self.currentQueryTab('queryHistory');
    }
    self.showGrid = ko.observable(
      typeof snippet.showGrid != 'undefined' && snippet.showGrid != null ? snippet.showGrid : true
    );
    self.showChart = ko.observable(
      typeof snippet.showChart != 'undefined' && snippet.showChart != null
        ? snippet.showChart
        : false
    );
    let defaultShowLogs = true;
    if (vm.editorMode() && $.totalStorage('hue.editor.showLogs')) {
      defaultShowLogs = $.totalStorage('hue.editor.showLogs');
    }
    self.showLogs = ko.observable(
      typeof snippet.showLogs !== 'undefined' && snippet.showLogs != null
        ? snippet.showLogs
        : defaultShowLogs
    );
    self.progress = ko.observable(
      typeof snippet.progress !== 'undefined' && snippet.progress != null ? snippet.progress : 0
    );
    self.jobs = ko.observableArray(
      typeof snippet.jobs !== 'undefined' && snippet.jobs != null ? snippet.jobs : []
    );

    self.executeNextTimeout = -1;
    const refreshTimeouts = {};
    self.onDdlExecute = function () {
      if (self.result.handle() && self.result.handle().has_more_statements) {
        window.clearTimeout(self.executeNextTimeout);
        const previousHash = self.result.handle().previous_statement_hash;
        self.executeNextTimeout = setTimeout(() => {
          // Don't execute if the handle has changed during the timeout
          if (previousHash === self.result.handle().previous_statement_hash) {
            self.execute(true); // Execute next, need to wait as we disabled fast click
          }
        }, 1000);
      }
      if (
        self.lastExecutedStatement() &&
        /CREATE|DROP/i.test(self.lastExecutedStatement().firstToken)
      ) {
        let match = self
          .statement()
          .match(
            /(?:CREATE|DROP)\s+TABLE\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?:`([^`]+)`|([^;\s]+))\..*/i
          );
        const path = [];
        if (match) {
          path.push(match[1] || match[2]); // group 1 backticked db name, group 2 regular db name
        } else {
          match = self
            .statement()
            .match(
              /(?:CREATE|DROP)\s+(?:DATABASE|SCHEMA)\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?:`([^`]+)`|([^;\s]+))/i
            );
          if (match) {
            path.push(match[1] || match[2]); // group 1 backticked db name, group 2 regular db name
          } else if (self.database()) {
            path.push(self.database());
          }
        }

        if (path.length) {
          window.clearTimeout(refreshTimeouts[path.join('.')]);
          refreshTimeouts[path.join('.')] = window.setTimeout(() => {
            ignoreNextAssistDatabaseUpdate = true;
            dataCatalog
              .getEntry({
                namespace: self.namespace(),
                compute: self.compute(),
                connector: self.connector(),
                path: path
              })
              .done(entry => {
                entry.clearCache({ refreshCache: true, cascade: true, silenceErrors: true });
              });
          }, 5000);
        }
      }
    };

    self.progress.subscribe(val => {
      $(document).trigger('progress', { data: val, snippet: self });
    });

    self.showGrid.subscribe(val => {
      if (val) {
        self.showChart(false);
        huePubSub.publish('editor.grid.shown', self);
      }
    });

    function prepopulateChart() {
      const type = self.chartType();
      hueAnalytics.log('notebook', 'chart/' + type);

      if (type === window.HUE_CHARTS.TYPES.MAP && self.result.cleanedNumericMeta().length >= 2) {
        if (self.chartX() === null || typeof self.chartX() === 'undefined') {
          let name = self.result.cleanedNumericMeta()[0].name;
          self.result.cleanedNumericMeta().forEach(fld => {
            if (
              fld.name.toLowerCase().indexOf('lat') > -1 ||
              fld.name.toLowerCase().indexOf('ltd') > -1
            ) {
              name = fld.name;
            }
          });
          self.chartX(name);
        }
        if (self.chartYSingle() === null || typeof self.chartYSingle() === 'undefined') {
          let name = self.result.cleanedNumericMeta()[1].name;
          self.result.cleanedNumericMeta().forEach(fld => {
            if (
              fld.name.toLowerCase().indexOf('lon') > -1 ||
              fld.name.toLowerCase().indexOf('lng') > -1
            ) {
              name = fld.name;
            }
          });
          self.chartYSingle(name);
        }
        return;
      }

      if (
        (self.chartX() === null || typeof self.chartX() === 'undefined') &&
        (type == window.HUE_CHARTS.TYPES.BARCHART ||
          type == window.HUE_CHARTS.TYPES.PIECHART ||
          type == window.HUE_CHARTS.TYPES.GRADIENTMAP) &&
        self.result.cleanedStringMeta().length >= 1
      ) {
        self.chartX(self.result.cleanedStringMeta()[0].name);
      }

      if (self.result.cleanedNumericMeta().length > 0) {
        if (
          self.chartYMulti().length === 0 &&
          (type === window.HUE_CHARTS.TYPES.BARCHART || type === window.HUE_CHARTS.TYPES.LINECHART)
        ) {
          self.chartYMulti.push(
            self.result.cleanedNumericMeta()[
              Math.min(self.result.cleanedNumericMeta().length - 1, 1)
            ].name
          );
        } else if (
          (self.chartYSingle() === null || typeof self.chartYSingle() === 'undefined') &&
          (type === window.HUE_CHARTS.TYPES.PIECHART ||
            type === window.HUE_CHARTS.TYPES.MAP ||
            type === window.HUE_CHARTS.TYPES.GRADIENTMAP ||
            type === window.HUE_CHARTS.TYPES.SCATTERCHART ||
            (type === window.HUE_CHARTS.TYPES.BARCHART && self.chartXPivot() !== null))
        ) {
          if (self.chartYMulti().length === 0) {
            self.chartYSingle(
              self.result.cleanedNumericMeta()[
                Math.min(self.result.cleanedNumericMeta().length - 1, 1)
              ].name
            );
          } else {
            self.chartYSingle(self.chartYMulti()[0]);
          }
        }
      }
    }

    self.showChart.subscribe(val => {
      if (val) {
        self.showGrid(false);
        self.isResultSettingsVisible(true);
        $(document).trigger('forceChartDraw', self);
        huePubSub.publish('editor.chart.shown', self);
        prepopulateChart();
      }
    });
    self.showLogs.subscribe(val => {
      huePubSub.publish('redraw.fixed.headers');
      if (val) {
        self.getLogs();
      }
      if (vm.editorMode()) {
        $.totalStorage('hue.editor.showLogs', val);
      }
    });

    self.isLoading = ko.computed(() => {
      return self.status() == 'loading';
    });

    self.resultsKlass = ko.computed(() => {
      return 'results ' + self.type();
    });

    self.errorsKlass = ko.computed(() => {
      return self.resultsKlass() + ' alert alert-error';
    });

    self.is_redacted = ko.observable(
      typeof snippet.is_redacted != 'undefined' && snippet.is_redacted != null
        ? snippet.is_redacted
        : false
    );

    self.chartType = ko.observable(
      typeof snippet.chartType != 'undefined' && snippet.chartType != null
        ? snippet.chartType
        : window.HUE_CHARTS.TYPES.BARCHART
    );
    self.chartType.subscribe(prepopulateChart);
    self.chartSorting = ko.observable(
      typeof snippet.chartSorting != 'undefined' && snippet.chartSorting != null
        ? snippet.chartSorting
        : 'none'
    );
    self.chartScatterGroup = ko.observable(
      typeof snippet.chartScatterGroup != 'undefined' && snippet.chartScatterGroup != null
        ? snippet.chartScatterGroup
        : null
    );
    self.chartScatterSize = ko.observable(
      typeof snippet.chartScatterSize != 'undefined' && snippet.chartScatterSize != null
        ? snippet.chartScatterSize
        : null
    );
    self.chartScope = ko.observable(
      typeof snippet.chartScope != 'undefined' && snippet.chartScope != null
        ? snippet.chartScope
        : 'world'
    );
    self.chartTimelineType = ko.observable(
      typeof snippet.chartTimelineType != 'undefined' && snippet.chartTimelineType != null
        ? snippet.chartTimelineType
        : 'bar'
    );
    self.chartLimits = ko.observableArray([5, 10, 25, 50, 100]);
    self.chartLimit = ko.observable(
      typeof snippet.chartLimit != 'undefined' && snippet.chartLimit != null
        ? snippet.chartLimit
        : null
    );
    self.chartLimit.extend({ notify: 'always' });
    self.chartX = ko.observable(
      typeof snippet.chartX != 'undefined' && snippet.chartX != null ? snippet.chartX : null
    );
    self.chartX.extend({ notify: 'always' });
    self.chartXPivot = ko.observable(
      typeof snippet.chartXPivot != 'undefined' && snippet.chartXPivot != null
        ? snippet.chartXPivot
        : null
    );
    self.chartXPivot.extend({ notify: 'always' });
    self.chartXPivot.subscribe(prepopulateChart);
    self.chartYSingle = ko.observable(
      typeof snippet.chartYSingle != 'undefined' && snippet.chartYSingle != null
        ? snippet.chartYSingle
        : null
    );
    self.chartYMulti = ko.observableArray(
      typeof snippet.chartYMulti != 'undefined' && snippet.chartYMulti != null
        ? snippet.chartYMulti
        : []
    );
    self.chartData = ko.observableArray(
      typeof snippet.chartData != 'undefined' && snippet.chartData != null ? snippet.chartData : []
    );
    self.chartMapType = ko.observable(
      typeof snippet.chartMapType != 'undefined' && snippet.chartMapType != null
        ? snippet.chartMapType
        : 'marker'
    );
    self.chartMapLabel = ko.observable(
      typeof snippet.chartMapLabel != 'undefined' && snippet.chartMapLabel != null
        ? snippet.chartMapLabel
        : null
    );
    self.chartMapHeat = ko.observable(
      typeof snippet.chartMapHeat != 'undefined' && snippet.chartMapHeat != null
        ? snippet.chartMapHeat
        : null
    );
    self.hideStacked = ko.computed(() => {
      return self.chartYMulti().length <= 1;
    });

    self.hasDataForChart = ko.computed(() => {
      if (
        self.chartType() == window.HUE_CHARTS.TYPES.BARCHART ||
        self.chartType() == window.HUE_CHARTS.TYPES.LINECHART ||
        self.chartType() == window.HUE_CHARTS.TYPES.TIMELINECHART
      ) {
        return (
          typeof self.chartX() != 'undefined' &&
          self.chartX() != null &&
          self.chartYMulti().length > 0
        );
      }
      return (
        typeof self.chartX() != 'undefined' &&
        self.chartX() != null &&
        typeof self.chartYSingle() != 'undefined' &&
        self.chartYSingle() != null
      );
    });

    self.hasDataForChart.subscribe(newValue => {
      self.chartX.notifySubscribers();
      self.chartX.valueHasMutated();
    });

    self.chartType.subscribe(val => {
      $(document).trigger('forceChartDraw', self);
    });

    self.previousChartOptions = {};

    function guessMetaField(field) {
      let _fld = null;
      if (field) {
        if (self.result.cleanedMeta().length > 0) {
          self.result.cleanedMeta().forEach(fld => {
            if (
              fld.name.toLowerCase() === field.toLowerCase() ||
              field.toLowerCase() === fld.name.toLowerCase()
            ) {
              _fld = fld.name;
            }
          });
        }
      }
      return _fld;
    }

    function guessMetaFields(fields) {
      const _fields = [];
      if (fields) {
        fields.forEach(fld => {
          const _field = guessMetaField(fld);
          if (_field) {
            _fields.push(_field);
          }
        });
      }
      return _fields;
    }

    self.result.meta.subscribe(newValue => {
      self.chartLimit(self.previousChartOptions.chartLimit);
      self.chartX(guessMetaField(self.previousChartOptions.chartX));
      self.chartXPivot(self.previousChartOptions.chartXPivot);
      self.chartYSingle(guessMetaField(self.previousChartOptions.chartYSingle));
      self.chartMapType(self.previousChartOptions.chartMapType);
      self.chartMapLabel(guessMetaField(self.previousChartOptions.chartMapLabel));
      self.chartMapHeat(self.previousChartOptions.chartMapHeat);
      self.chartYMulti(guessMetaFields(self.previousChartOptions.chartYMulti) || []);
      self.chartSorting(self.previousChartOptions.chartSorting);
      self.chartScatterGroup(self.previousChartOptions.chartScatterGroup);
      self.chartScatterSize(self.previousChartOptions.chartScatterSize);
      self.chartScope(self.previousChartOptions.chartScope);
      self.chartTimelineType(self.previousChartOptions.chartTimelineType);
    });

    self.isResultSettingsVisible = ko.observable(
      typeof snippet.isResultSettingsVisible != 'undefined' &&
        snippet.isResultSettingsVisible != null
        ? snippet.isResultSettingsVisible
        : false
    );
    self.toggleResultSettings = function () {
      self.isResultSettingsVisible(!self.isResultSettingsVisible());
    };
    self.isResultSettingsVisible.subscribe(() => {
      $(document).trigger('toggleResultSettings', self);
    });

    self.settingsVisible = ko.observable(
      typeof snippet.settingsVisible != 'undefined' && snippet.settingsVisible != null
        ? snippet.settingsVisible
        : false
    );
    self.saveResultsModalVisible = ko.observable(false);

    self.checkStatusTimeout = null;
    self.getLogsTimeout = null;

    self.getContext = function () {
      return {
        id: self.id,
        type: self.type,
        status: self.status,
        statementType: self.statementType,
        statement: self.statement,
        aceCursorPosition: self.aceCursorPosition,
        statementPath: self.statementPath,
        associatedDocumentUuid: self.associatedDocumentUuid,
        properties: self.properties,
        result: self.result.getContext(),
        database: self.database,
        compute: self.compute(),
        wasBatchExecuted: self.wasBatchExecuted()
      };
    };

    self.complexity = ko.observable();
    self.hasComplexity = ko.pureComputed(() => {
      return self.complexity() && Object.keys(self.complexity()).length > 0;
    });
    self.hasRisks = ko.pureComputed(() => {
      return (
        self.hasComplexity() && self.complexity()['hints'] && self.complexity()['hints'].length > 0
      );
    });
    self.topRisk = ko.pureComputed(() => {
      if (self.hasRisks()) {
        return self.complexity()['hints'][0];
      } else {
        return null;
      }
    });

    self.suggestion = ko.observable('');
    self.hasSuggestion = ko.observable(null);

    self.compatibilityCheckRunning = ko.observable(false);

    self.compatibilitySourcePlatforms = [];
    Object.keys(COMPATIBILITY_SOURCE_PLATFORMS).forEach(key => {
      self.compatibilitySourcePlatforms.push(COMPATIBILITY_SOURCE_PLATFORMS[key]);
    });

    self.compatibilitySourcePlatform = ko.observable(COMPATIBILITY_SOURCE_PLATFORMS[self.type()]);
    self.compatibilitySourcePlatform.subscribe(newValue => {
      if (newValue && newValue.value !== self.type()) {
        self.hasSuggestion(null);
        self.compatibilityTargetPlatform(COMPATIBILITY_TARGET_PLATFORMS[self.type()]);
        self.queryCompatibility();
      }
    });

    self.compatibilityTargetPlatforms = [];
    Object.keys(COMPATIBILITY_TARGET_PLATFORMS).forEach(key => {
      self.compatibilityTargetPlatforms.push(COMPATIBILITY_TARGET_PLATFORMS[key]);
    });
    self.compatibilityTargetPlatform = ko.observable(COMPATIBILITY_TARGET_PLATFORMS[self.type()]);

    self.showOptimizer = ko.observable(
      apiHelper.getFromTotalStorage('editor', 'show.optimizer', false)
    );
    self.showOptimizer.subscribe(newValue => {
      if (newValue !== null) {
        apiHelper.setInTotalStorage('editor', 'show.optimizer', newValue);
      }
    });

    if (HAS_OPTIMIZER && !vm.isNotificationManager()) {
      let lastComplexityRequest;
      let lastCheckedComplexityStatement;
      const knownResponses = [];

      self.delayedStatement = ko
        .pureComputed(self.statement)
        .extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 2000 } });

      const handleRiskResponse = function (data) {
        if (data.status == 0) {
          self.hasSuggestion('');
          self.complexity(data.query_complexity);
        } else {
          self.hasSuggestion('error');
          self.complexity({ hints: [] });
        }
        huePubSub.publish('editor.active.risks', {
          editor: self.ace(),
          risks: self.complexity() || {}
        });
        lastCheckedComplexityStatement = self.statement();
      };

      const clearActiveRisks = function () {
        if (self.hasSuggestion() !== null && typeof self.hasSuggestion() !== 'undefined') {
          self.hasSuggestion(null);
        }

        if (self.suggestion() !== '') {
          self.suggestion('');
        }

        if (self.complexity() !== {}) {
          self.complexity(undefined);
          huePubSub.publish('editor.active.risks', {
            editor: self.ace(),
            risks: {}
          });
        }
      };

      self.positionStatement.subscribe(newStatement => {
        if (newStatement) {
          const hash = newStatement.statement.hashCode();
          const unknownResponse = knownResponses.every(knownResponse => {
            if (knownResponse.hash === hash) {
              handleRiskResponse(knownResponse.data);
              return false;
            }
            return true;
          });
          if (unknownResponse) {
            clearActiveRisks();
          }
        }
      });

      self.checkComplexity = function () {
        if (!self.inFocus() || lastCheckedComplexityStatement === self.statement()) {
          return;
        }

        // The syntaxError property is only set if the syntax checker is active and has found an
        // error, see AceLocationHandler.
        if (self.positionStatement() && self.positionStatement().syntaxError) {
          return;
        }

        cancelActiveRequest(lastComplexityRequest);

        hueAnalytics.log('notebook', 'get_query_risk');
        clearActiveRisks();

        const changeSubscription = self.statement.subscribe(() => {
          changeSubscription.dispose();
          cancelActiveRequest(lastComplexityRequest);
        });

        const hash = self.statement().hashCode();

        const unknownResponse = knownResponses.every(knownResponse => {
          if (knownResponse.hash === hash) {
            handleRiskResponse(knownResponse.data);
            return false;
          }
          return true;
        });
        if (unknownResponse) {
          lastComplexityRequest = $.ajax({
            type: 'POST',
            url: '/notebook/api/optimizer/statement/risk',
            timeout: 30000, // 30 seconds
            data: {
              notebook: komapping.toJSON(notebook.getContext()),
              snippet: komapping.toJSON(self.getContext())
            },
            success: function (data) {
              knownResponses.unshift({
                hash: hash,
                data: data
              });
              if (knownResponses.length > 50) {
                knownResponses.pop();
              }
              handleRiskResponse(data);
            },
            always: function (data) {
              changeSubscription.dispose();
            }
          });
        }
      };

      if (self.type() === 'hive' || self.type() === 'impala') {
        if (self.statement_raw()) {
          window.setTimeout(() => {
            self.checkComplexity();
          }, 2000);
        }
        self.delayedStatement.subscribe(() => {
          self.checkComplexity();
        });
      }
    }

    self._ajaxError = function (data, callback) {
      if (data.status == -2) {
        // Session expired
        const existingSession = notebook.getSession(self.type());
        if (existingSession) {
          notebook.restartSession(existingSession, callback);
        } else {
          notebook.createSession(new Session(vm, { type: self.type() }), callback);
        }
      } else if (data.status == -3) {
        // Statement expired
        self.status('expired');
        if (data.message) {
          self.errors.push({ message: data.message, help: null, line: null, col: null });
          huePubSub.publish('editor.snippet.result.normal', self);
        }
      } else if (data.status == -4) {
        // Operation timed out
        notebook.retryModalCancel = function () {
          self.status('failed');
          huePubSub.publish('hide.retry.modal');
        };
        notebook.retryModalConfirm = function () {
          if (callback) {
            callback();
          }
          huePubSub.publish('hide.retry.modal');
        };
        huePubSub.publish('show.retry.modal');
      } else if (data.status == 401) {
        // Auth required
        self.status('expired');
        $(document).trigger('showAuthModal', {
          type: self.type(),
          callback: self.execute,
          message: data.message
        });
      } else if (data.status == 1 || data.status == -1) {
        self.status('failed');
        const match = ERROR_REGEX.exec(data.message);
        if (match) {
          let errorLine = parseInt(match[1]);
          let errorCol;
          if (typeof match[3] !== 'undefined') {
            errorCol = parseInt(match[3]);
          }
          if (self.positionStatement()) {
            if (errorCol && errorLine === 1) {
              errorCol += self.positionStatement().location.first_column;
            }
            errorLine += self.positionStatement().location.first_line - 1;
          }

          self.errors.push({
            message: data.message.replace(
              match[0],
              'line ' + errorLine + (errorCol !== null ? ':' + errorCol : '')
            ),
            help: null,
            line: errorLine - 1,
            col: errorCol
          });
        } else {
          self.errors.push({
            message: data.message,
            help: data.help,
            line: null,
            col: null
          });
        }
      } else {
        $(document).trigger('error', data.message);
        self.status('failed');
      }
    };

    self.wasBatchExecuted = ko.observable(
      typeof snippet.wasBatchExecuted != 'undefined' && snippet.wasBatchExecuted != null
        ? snippet.wasBatchExecuted
        : false
    );
    self.isReady = ko.computed(() => {
      return (
        (self.statementType() == 'text' &&
          ((self.isSqlDialect() && self.statement() !== '') ||
            (['jar', 'java', 'spark2', 'distcp'].indexOf(self.type()) == -1 &&
              self.statement() !== '') ||
            (['jar', 'java'].indexOf(self.type()) != -1 &&
              self.properties().app_jar() != '' &&
              self.properties().class() != '') ||
            (['spark2'].indexOf(self.type()) != -1 && self.properties().jars().length > 0) ||
            (['shell'].indexOf(self.type()) != -1 && self.properties().command_path().length > 0) ||
            (['mapreduce'].indexOf(self.type()) != -1 && self.properties().app_jar().length > 0) ||
            (['py'].indexOf(self.type()) != -1 && self.properties().py_file().length > 0) ||
            (['distcp'].indexOf(self.type()) != -1 &&
              self.properties().source_path().length > 0 &&
              self.properties().destination_path().length > 0))) ||
        (self.statementType() == 'file' && self.statementPath().length > 0) ||
        (self.statementType() == 'document' &&
          self.associatedDocumentUuid() &&
          self.associatedDocumentUuid().length > 0)
      );
    });
    self.lastExecuted = ko.observable(
      typeof snippet.lastExecuted != 'undefined' && snippet.lastExecuted != null
        ? snippet.lastExecuted
        : 0
    );
    self.lastAceSelectionRowOffset = ko.observable(snippet.lastAceSelectionRowOffset || 0);

    self.executingBlockingOperation = null; // A ExecuteStatement()
    self.showLongOperationWarning = ko.observable(false);
    self.showLongOperationWarning.subscribe(newValue => {
      if (newValue) {
        hueAnalytics.convert('editor', 'showLongOperationWarning');
      }
    });

    let longOperationTimeout = -1;

    function startLongOperationTimeout() {
      longOperationTimeout = window.setTimeout(() => {
        self.showLongOperationWarning(true);
      }, 2000);
    }

    function stopLongOperationTimeout() {
      window.clearTimeout(longOperationTimeout);
      self.showLongOperationWarning(false);
    }

    self.lastExecutedStatements = undefined;
    self.lastExecutedSelectionRange = undefined;

    self.execute = function (automaticallyTriggered) {
      self.clearActiveExecuteRequests();

      if (!automaticallyTriggered && self.ace()) {
        const selectionRange = self.ace().getSelectionRange();

        if (
          self.lastExecutedSelectionRange &&
          selectionRange.start.row !== selectionRange.end.row &&
          selectionRange.start.column !== selectionRange.end.column &&
          (selectionRange.start.row !== self.lastExecutedSelectionRange.start.row ||
            selectionRange.start.column !== self.lastExecutedSelectionRange.start.column ||
            selectionRange.end.row !== self.lastExecutedSelectionRange.end.row ||
            selectionRange.end.column !== self.lastExecutedSelectionRange.end.column)
        ) {
          // Manual execute and there is a selection that is different from the last execute
          self.result.cancelBatchExecution();
        }
        self.lastExecutedSelectionRange = selectionRange;
      }

      if (self.isCanceling()) {
        return;
      }
      const now = new Date().getTime();
      if (now - self.lastExecuted() < 1000 || !self.isReady()) {
        return; // Prevent fast clicks
      }

      if (!automaticallyTriggered) {
        // Do not cancel statements that are parts of a set of steps to execute (e.g. import). Only cancel statements as requested by user
        if (self.status() === 'running' || self.status() === 'loading') {
          self.cancel(); // TODO: Wait for cancel to finish
        } else {
          self.result.clear();
        }
      }

      if (self.type() === 'impala') {
        self.showExecutionAnalysis(false);
        huePubSub.publish('editor.clear.execution.analysis');
      }

      self.status('running');
      self.statusForButtons('executing');

      if (self.isSqlDialect()) {
        huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, self.id());
      }

      self.lastExecutedStatements = self.statement();

      if (self.ace()) {
        huePubSub.publish('ace.set.autoexpand', { autoExpand: false, snippet: self });
        const selectionRange = self.ace().getSelectionRange();
        self.lastAceSelectionRowOffset(Math.min(selectionRange.start.row, selectionRange.end.row));
      }

      self.previousChartOptions = vm.getPreviousChartOptions(self);
      $(document).trigger('executeStarted', { vm: vm, snippet: self });
      self.lastExecuted(now);
      $('.jHueNotify').remove();
      hueAnalytics.log('notebook', 'execute/' + self.type());

      notebook.forceHistoryInitialHeight(true);

      if (self.result.handle()) {
        self.close();
      }

      self.errors([]);
      huePubSub.publish('editor.clear.highlighted.errors', self.ace());
      self.result.clear();
      self.progress(0);
      self.jobs([]);
      self.result.logs('');
      self.result.statement_range({
        start: {
          row: 0,
          column: 0
        },
        end: {
          row: 0,
          column: 0
        }
      });
      notebook.historyCurrentPage(1);

      // TODO: rename startLongOperationTimeout to startBlockingOperationTimeout
      // TODO: stop blocking operation UI if there is one
      // TODO: offer to stop blocking submit or fetch operation UI if there is one (add a new call to function for cancelBlockingOperation)
      // TODO: stop current blocking operation if there is one
      // TODO: handle jquery.dataTables.1.8.2.min.js:150 Uncaught TypeError: Cannot read property 'asSorting' of undefined on some cancels
      // TODO: we should cancel blocking operation when leaving notebook (similar to unload())
      // TODO: we should test when we go back to a query history of a blocking operation that we left
      startLongOperationTimeout();

      self.currentQueryTab('queryHistory');

      self.executingBlockingOperation = $.post(
        '/notebook/api/execute/' + self.type(),
        {
          notebook: vm.editorMode()
            ? komapping.toJSON(notebook, NOTEBOOK_MAPPING)
            : komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext())
        },
        data => {
          try {
            if (self.isSqlDialect() && data && data.handle) {
              self.lastExecutedStatement(sqlStatementsParser.parse(data.handle.statement)[0]);
            } else {
              self.lastExecutedStatement(null);
            }
          } catch (e) {
            self.lastExecutedStatement(null);
          }
          self.statusForButtons('executed');
          huePubSub.publish('ace.set.autoexpand', { autoExpand: true, snippet: self });
          stopLongOperationTimeout();

          if (vm.editorMode() && data.history_id) {
            if (!vm.isNotificationManager()) {
              const url = vm.URLS.editor + '?editor=' + data.history_id;
              vm.changeURL(url);
            }
            notebook.id(data.history_id);
            notebook.uuid(data.history_uuid);
            notebook.isHistory(true);
            notebook.parentSavedQueryUuid(data.history_parent_uuid);
          }

          if (data.status === 0) {
            self.result.clear();
            self.result.handle(data.handle);
            self.result.hasResultset(data.handle.has_result_set);
            self.showLogs(true);
            if (data.handle.sync) {
              self.loadData(data.result, 100);
              self.status('available');
              self.progress(100);
              self.result.endTime(new Date());
            } else if (!notebook.unloaded()) {
              self.checkStatus();
            }
            if (vm.isOptimizerEnabled()) {
              huePubSub.publish('editor.upload.query', data.history_id);
            }
          } else {
            self._ajaxError(data, self.execute);
            notebook.isExecutingAll(false);
          }

          if (data.handle) {
            if (data.handle.session_id) {
              // Execute can update the session
              if (!notebook.sessions().length) {
                notebook.addSession(
                  new Session(vm, {
                    type: self.type(),
                    session_id: data.handle.session_guid,
                    id: data.handle.session_id,
                    properties: {}
                  })
                );
              } else {
                notebook.sessions()[0].session_id(data.handle.session_guid);
                notebook.sessions()[0].id(data.handle.session_id);
              }
            }
            if (vm.editorMode()) {
              if (vm.isNotificationManager()) {
                // Update task status
                const tasks = $.grep(notebook.history(), row => {
                  return row.uuid() == notebook.uuid();
                });
                if (tasks.length === 1) {
                  tasks[0].status(self.status());
                  self.result.logs(data.message);
                }
              } else {
                notebook.history.unshift(
                  notebook.makeHistoryRecord(
                    undefined,
                    data.handle.statement,
                    self.lastExecuted(),
                    self.status(),
                    notebook.name(),
                    notebook.uuid()
                  )
                );
              }
            }

            if (data.handle.statements_count != null) {
              self.result.statements_count(data.handle.statements_count);
              self.result.statement_id(data.handle.statement_id);
              self.result.previous_statement_hash(data.previous_statement_hash);

              if (
                data.handle.statements_count > 1 &&
                data.handle.start != null &&
                data.handle.end != null
              ) {
                self.result.statement_range({
                  start: data.handle.start,
                  end: data.handle.end
                });
              }
            }
          }
        }
      )
        .fail((xhr, textStatus, errorThrown) => {
          if (self.statusForButtons() != 'canceled' && xhr.status !== 502) {
            // No error when manually canceled
            $(document).trigger('error', xhr.responseText);
          }
          self.status('failed');
          self.statusForButtons('executed');
        })
        .always(() => {
          self.executingBlockingOperation = null;
        });
    };

    self.reexecute = function () {
      self.result.cancelBatchExecution();
      self.execute();
    };

    self.formatEnabled = ko.pureComputed(() => {
      return (
        self.statement_raw && self.statement_raw() != null && self.statement_raw().length < 400000
      ); // ie: 5000 lines at 80 chars per line
    });

    self.createGist = function () {
      if (self.isSqlDialect()) {
        apiHelper
          .createGist({
            statement:
              self.ace().getSelectedText() !== ''
                ? self.ace().getSelectedText()
                : self.statement_raw(),
            doc_type: self.type(),
            name: self.name(),
            description: ''
          })
          .done(data => {
            if (data.status === 0) {
              huePubSub.publish(SHOW_GIST_MODAL_EVENT, {
                link: data.link
              });
            } else {
              self._ajaxError(data);
            }
          });
      }
      hueAnalytics.log('gist', self.type());
    };

    self.format = function () {
      if (self.isSqlDialect()) {
        apiHelper
          .formatSql({
            statements:
              self.ace().getSelectedText() != ''
                ? self.ace().getSelectedText()
                : self.statement_raw()
          })
          .done(data => {
            if (data.status == 0) {
              if (self.ace().getSelectedText() != '') {
                self
                  .ace()
                  .session.replace(
                    self.ace().session.selection.getRange(),
                    data.formatted_statements
                  );
              } else {
                self.statement_raw(data.formatted_statements);
                self.ace().setValue(self.statement_raw(), 1);
              }
            } else {
              self._ajaxError(data);
            }
          });
      }
      hueAnalytics.log('notebook', 'format');
    };

    self.clear = function () {
      hueAnalytics.log('notebook', 'clear');
      self.ace().setValue('', 1);
      self.result.clear();
      self.status('ready');
    };

    self.explain = function () {
      hueAnalytics.log('notebook', 'explain');

      if (self.statement() == '' || self.status() == 'running' || self.status() === 'loading') {
        return;
      }

      self.result.explanation('');
      self.errors([]);
      self.progress(0);
      self.status('ready');

      $.post(
        '/notebook/api/explain',
        {
          notebook: komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext())
        },
        data => {
          if (data.status == 0) {
            self.currentQueryTab('queryExplain');
            self.result.fetchedOnce(true);
            self.result.explanation(data.explanation);
          } else {
            self._ajaxError(data);
          }
        }
      );
    };

    let lastCompatibilityRequest;

    self.checkCompatibility = function () {
      self.hasSuggestion(null);
      self.compatibilitySourcePlatform(COMPATIBILITY_SOURCE_PLATFORMS[self.type()]);
      self.compatibilityTargetPlatform(
        COMPATIBILITY_TARGET_PLATFORMS[self.type() === 'hive' ? 'impala' : 'hive']
      );
      self.queryCompatibility();
    };

    self.queryCompatibility = function (targetPlatform) {
      cancelActiveRequest(lastCompatibilityRequest);

      hueAnalytics.log('notebook', 'compatibility');
      self.compatibilityCheckRunning(targetPlatform != self.type());
      self.hasSuggestion(null);
      const positionStatement = self.positionStatement();

      lastCompatibilityRequest = $.post(
        '/notebook/api/optimizer/statement/compatibility',
        {
          notebook: komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext()),
          sourcePlatform: self.compatibilitySourcePlatform().value,
          targetPlatform: self.compatibilityTargetPlatform().value
        },
        data => {
          if (data.status === 0) {
            self.aceErrorsHolder([]);
            self.aceWarningsHolder([]);
            self.suggestion(komapping.fromJS(data.query_compatibility));
            if (self.suggestion().queryError && self.suggestion().queryError.errorString()) {
              const match = ERROR_REGEX.exec(self.suggestion().queryError.errorString());
              let line = null;
              if (match) {
                if (positionStatement) {
                  line = positionStatement.location.first_line + parseInt(match[1]) + 1;
                } else {
                  line = parseInt(match[1]) - 1;
                }
              }
              self.aceWarningsHolder.push({
                message: self.suggestion().queryError.errorString(),
                line: line,
                col:
                  match === null
                    ? null
                    : typeof match[3] !== 'undefined'
                    ? parseInt(match[3])
                    : null
              });
              self.status('with-optimizer-report');
            }
            if (self.suggestion().parseError()) {
              const match = ERROR_REGEX.exec(self.suggestion().parseError());
              self.aceErrorsHolder.push({
                message: self.suggestion().parseError(),
                line: match === null ? null : parseInt(match[1]) - 1,
                col:
                  match === null
                    ? null
                    : typeof match[3] !== 'undefined'
                    ? parseInt(match[3])
                    : null
              });
              self.status('with-optimizer-report');
            }
            self.showOptimizer(true);
            self.hasSuggestion(true);
          } else {
            $(document).trigger('error', data.message);
          }
        }
      )
        .fail((xhr, textStatus, errorThrown) => {
          if (xhr.status !== 502) {
            $(document).trigger('error', xhr.responseText);
          }
        })
        .always(() => {
          self.compatibilityCheckRunning(false);
        });
    };

    self.fetchResult = function (rows, startOver) {
      if (typeof startOver == 'undefined') {
        startOver = true;
      }
      self.fetchResultData(rows, startOver);
      //self.fetchResultMetadata(rows);
    };

    self.isFetchingData = false;

    self.fetchExecutionAnalysis = function () {
      if (self.type() === 'impala') {
        // TODO: Use real query ID
        huePubSub.publish('editor.update.execution.analysis', {
          analysisPossible: true,
          compute: self.compute(),
          queryId: notebook.getContext().id(),
          name: self.jobs()[0] && self.jobs()[0].name
        });
      } else {
        huePubSub.publish('editor.update.execution.analysis', {
          analysisPossible: false
        });
      }
    };

    self.fetchResultData = function (rows, startOver) {
      if (!self.isFetchingData) {
        if (self.status() === 'available') {
          startLongOperationTimeout();
          self.isFetchingData = true;
          hueAnalytics.log('notebook', 'fetchResult/' + rows + '/' + startOver);
          $.post(
            '/notebook/api/fetch_result_data',
            {
              notebook: komapping.toJSON(notebook.getContext()),
              snippet: komapping.toJSON(self.getContext()),
              rows: rows,
              startOver: startOver
            },
            data => {
              stopLongOperationTimeout();
              data = JSON.bigdataParse(data);
              if (data.status === 0) {
                self.showExecutionAnalysis(true);
                self.loadData(data.result, rows);
              } else {
                self._ajaxError(data, () => {
                  self.isFetchingData = false;
                  self.fetchResultData(rows, startOver);
                });
                $(document).trigger('renderDataError', { snippet: self });
              }
            },
            'text'
          )
            .fail((xhr, textStatus, errorThrown) => {
              if (xhr.status !== 502) {
                $(document).trigger('error', xhr.responseText);
              }
            })
            .always(() => {
              self.isFetchingData = false;
            });
        } else {
          huePubSub.publish('editor.snippet.result.normal', self);
        }
      }
    };

    self.loadData = function (result, rows) {
      rows -= result.data.length;

      if (result.data.length > 0) {
        self.currentQueryTab('queryResults');
      }

      const _initialIndex = self.result.data().length;
      const _tempData = [];
      $.each(result.data, (index, row) => {
        row.unshift(_initialIndex + index + 1);
        self.result.data.push(row);
        _tempData.push(row);
      });

      if (self.result.rows() == null || (self.result.rows() + '').indexOf('+') != -1) {
        self.result.rows(self.result.data().length + (result.has_more ? '+' : ''));
      }

      self.result.images(
        typeof result.images != 'undefined' && result.images != null ? result.images : []
      );

      huePubSub.publish('editor.render.data', {
        data: _tempData,
        snippet: self,
        initial: _initialIndex == 0
      });

      if (!self.result.fetchedOnce()) {
        result.meta.unshift({ type: 'INT_TYPE', name: '', comment: null });
        self.result.meta(result.meta);
        self.result.type(result.type);
        self.result.fetchedOnce(true);
      }

      self.result.meta().forEach(meta => {
        if (
          $.inArray(meta.type, [
            'TINYINT_TYPE',
            'SMALLINT_TYPE',
            'INT_TYPE',
            'BIGINT_TYPE',
            'FLOAT_TYPE',
            'DOUBLE_TYPE',
            'DECIMAL_TYPE'
          ]) > -1
        ) {
          meta.cssClass = 'sort-numeric';
        } else if ($.inArray(meta.type, ['TIMESTAMP_TYPE', 'DATE_TYPE', 'DATETIME_TYPE']) > -1) {
          meta.cssClass = 'sort-date';
        } else {
          meta.cssClass = 'sort-string';
        }
      });

      self.result.hasMore(result.has_more);

      if (result.has_more && rows > 0) {
        setTimeout(() => {
          self.fetchResultData(rows, false);
        }, 500);
      } else if (
        !vm.editorMode() &&
        !notebook.isPresentationMode() &&
        notebook.snippets()[notebook.snippets().length - 1] == self
      ) {
        notebook.newSnippet();
      }
    };

    self.fetchResultMetadata = function () {
      $.post(
        '/notebook/api/fetch_result_metadata',
        {
          notebook: komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext())
        },
        data => {
          if (data.status == 0) {
            self.result.meta(data.result.meta);
          } else {
            $(document).trigger('error', data.message);
          }
        }
      ).fail((xhr, textStatus, errorThrown) => {
        if (xhr.status !== 502) {
          $(document).trigger('error', xhr.responseText);
        }
        self.status('failed');
      });
    };

    self.fetchResultSize = function (n, query_id) {
      $.post(
        '/notebook/api/fetch_result_size',
        {
          notebook: komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext())
        },
        data => {
          if (query_id == notebook.id()) {
            // If still on the same result
            if (data.status == 0) {
              if (data.result.rows != null) {
                self.result.rows(data.result.rows);
              } else if (self.type() == 'impala' && n > 0) {
                setTimeout(() => {
                  self.fetchResultSize(n - 1, query_id);
                }, 1000);
              }
            } else if (data.status == 5) {
              // No supported yet for this snippet
            } else {
              //$(document).trigger("error", data.message);
            }
          }
        }
      ).fail((xhr, textStatus, errorThrown) => {
        //$(document).trigger("error", xhr.responseText);
      });
    };

    self.checkStatus = function () {
      const _checkStatus = function () {
        self.lastCheckStatusRequest = $.post(
          '/notebook/api/check_status',
          {
            notebook: komapping.toJSON(notebook.getContext()),
            snippet: komapping.toJSON(self.getContext())
          },
          data => {
            if (self.statusForButtons() == 'canceling' || self.status() == 'canceled') {
              // Query was canceled in the meantime, do nothing
            } else {
              self.result.endTime(new Date());

              if (data.status === 0) {
                self.status(data.query_status.status);
                if (self.result.handle() && data.query_status.has_result_set !== undefined) {
                  self.result.handle().has_result_set = data.query_status.has_result_set;
                  self.result.hasResultset(self.result.handle().has_result_set);
                }

                if (
                  self.status() == 'running' ||
                  self.status() == 'starting' ||
                  self.status() == 'waiting'
                ) {
                  const delay = self.result.executionTime() > 45000 ? 5000 : 1000; // 5s if more than 45s
                  if (!notebook.unloaded()) {
                    self.checkStatusTimeout = setTimeout(_checkStatus, delay);
                  }
                } else if (self.status() === 'available' || self.status() === 'success') {
                  if (self.status() === 'available') {
                    self.fetchResult(100);
                  }
                  self.progress(100);
                  if (self.isSqlDialect()) {
                    if (self.result.handle().has_result_set) {
                      const _query_id = notebook.id();
                      setTimeout(() => {
                        // Delay until we get IMPALA-5555
                        self.fetchResultSize(10, _query_id);
                      }, 2000);
                      self.checkDdlNotification(); // DDL CTAS with Impala
                    } else if (self.lastExecutedStatement()) {
                      self.checkDdlNotification();
                    } else {
                      self.onDdlExecute();
                    }
                  }
                  if (notebook.isExecutingAll()) {
                    notebook.executingAllIndex(notebook.executingAllIndex() + 1);
                    if (notebook.executingAllIndex() < notebook.snippets().length) {
                      notebook.snippets()[notebook.executingAllIndex()].execute();
                    } else {
                      notebook.isExecutingAll(false);
                    }
                  }
                  if (!self.result.handle().has_more_statements && vm.successUrl()) {
                    huePubSub.publish('open.link', vm.successUrl()); // Not used anymore in Hue 4
                  }
                }
              } else if (data.status === -3) {
                self.status('expired');
                notebook.isExecutingAll(false);
              } else {
                self._ajaxError(data);
                notebook.isExecutingAll(false);
              }
            }
          }
        ).fail((xhr, textStatus, errorThrown) => {
          if (xhr.stausText !== 'abort') {
            if (xhr.status !== 502) {
              $(document).trigger('error', xhr.responseText || textStatus);
            }
            self.status('failed');
            notebook.isExecutingAll(false);
          }
        });
      };
      const activeStatus = ['running', 'starting', 'waiting'];
      const _getLogs = function (isLastTime) {
        window.clearTimeout(self.getLogsTimeout);
        self.getLogs().then(() => {
          const lastTime = activeStatus.indexOf(self.status()) < 0; // We to run getLogs at least one time after status is terminated to make sure we have last logs
          if (lastTime && isLastTime) {
            return;
          }
          const delay = self.result.executionTime() > 45000 ? 5000 : 1000; // 5s if more than 45s
          self.getLogsTimeout = setTimeout(_getLogs.bind(self, lastTime), delay);
        });
      };
      _checkStatus();
      _getLogs(activeStatus.indexOf(self.status()) < 0);
    };

    self.checkDdlNotification = function () {
      if (
        self.lastExecutedStatement() &&
        /ALTER|CREATE|DELETE|DROP|GRANT|INSERT|INVALIDATE|LOAD|SET|TRUNCATE|UPDATE|UPSERT|USE/i.test(
          self.lastExecutedStatement().firstToken
        )
      ) {
        self.onDdlExecute();
      } else {
        window.clearTimeout(self.executeNextTimeout);
      }
    };

    self.isCanceling = ko.observable(false);

    self.cancel = function () {
      window.clearTimeout(self.executeNextTimeout);
      self.isCanceling(true);
      self.clearActiveExecuteRequests();
      hueAnalytics.log('notebook', 'cancel');

      if (self.executingBlockingOperation != null) {
        self.executingBlockingOperation.abort();
        self.executingBlockingOperation = null;
      }

      if ($.isEmptyObject(self.result.handle())) {
        // Query was not even submitted yet
        self.statusForButtons('canceled');
        self.status('failed');
        self.isCanceling(false);
        notebook.isExecutingAll(false);
      } else {
        self.statusForButtons('canceling');
        $.post(
          '/notebook/api/cancel_statement',
          {
            notebook: komapping.toJSON(notebook.getContext()),
            snippet: komapping.toJSON(self.getContext())
          },
          data => {
            self.statusForButtons('canceled');
            if (data.status == 0) {
              self.status('canceled');
              notebook.isExecutingAll(false);
            } else {
              self._ajaxError(data);
            }
          }
        )
          .fail((xhr, textStatus, errorThrown) => {
            if (xhr.status !== 502) {
              $(document).trigger('error', xhr.responseText);
            }
            self.statusForButtons('canceled');
            self.status('failed');
            notebook.isExecutingAll(false);
          })
          .always(() => {
            self.isCanceling(false);
          });
      }
    };

    self.close = function () {
      self.clearActiveExecuteRequests();

      $.post(
        '/notebook/api/close_statement',
        {
          notebook: komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext())
        },
        data => {
          if (data.status == 0) {
            // self.status('closed'); // Keep as 'running' as currently it happens before running a new query
          } else {
            // self._ajaxError(data);
          }
        }
      ).fail((xhr, textStatus, errorThrown) => {
        if (xhr.status !== 502) {
          // $(document).trigger("error", xhr.responseText);
        }
        // self.status('failed'); // Can conflict with slow close and new query execution
      });
    };

    self.clearActiveExecuteRequests = function () {
      cancelActiveRequest(self.lastGetLogsRequest);
      if (self.getLogsTimeout !== null) {
        window.clearTimeout(self.getLogsTimeout);
        self.getLogsTimeout = null;
      }

      cancelActiveRequest(self.lastCheckStatusRequest);
      if (self.checkStatusTimeout !== null) {
        window.clearTimeout(self.checkStatusTimeout);
        self.checkStatusTimeout = null;
      }
    };

    self.getLogs = function () {
      cancelActiveRequest(self.lastGetLogsRequest);

      self.lastGetLogsRequest = $.post(
        '/notebook/api/get_logs',
        {
          notebook: komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext()),
          from: self.result.logLines,
          jobs: komapping.toJSON(self.jobs, { ignore: ['percentJob'] }),
          full_log: self.result.logs
        },
        data => {
          if (data.status == 1) {
            // Append errors to the logs
            data.status = 0;
            data.logs = data.message;
          }
          if (data.status == 0) {
            if (data.logs.length > 0) {
              const logs = data.logs.split('\n');
              self.result.logLines += logs.length;
              const oldLogs = self.result.logs();
              if (
                data.logs &&
                (oldLogs === '' ||
                  (self.wasBatchExecuted() && data.logs.indexOf('Unable to locate') == -1) ||
                  data.isFullLogs)
              ) {
                self.result.logs(data.logs);
              } else {
                self.result.logs(oldLogs + '\n' + data.logs);
              }
            }

            self.jobs().forEach(job => {
              if (typeof job.percentJob === 'undefined') {
                job.percentJob = ko.observable(-1);
              }
            });

            if (data.jobs && data.jobs.length > 0) {
              data.jobs.forEach(job => {
                const _found = ko.utils.arrayFilter(self.jobs(), item => {
                  return item.name === job.name;
                });
                if (_found.length === 0) {
                  if (typeof job.percentJob === 'undefined') {
                    job.percentJob = ko.observable(-1);
                  } else {
                    job.percentJob = ko.observable(job.percentJob);
                  }
                  self.jobs.push(job);
                } else if (typeof job.percentJob !== 'undefined') {
                  for (let i = 0; i < _found.length; i++) {
                    _found[i].percentJob(job.percentJob);
                  }
                }
              });
              self.jobs().forEach(job => {
                const _found = ko.utils.arrayFilter(self.jobs(), item => {
                  return item.name === job.name;
                });
                if (_found.length === 0) {
                  self.jobs.remove(job);
                }
              });
            }
            if (self.status() == 'running') {
              // Maybe the query finished or failed in the meantime
              self.progress(data.progress);
            }
          } else {
            self._ajaxError(data);
          }
        }
      ).fail((xhr, textStatus, errorThrown) => {
        if (xhr.statusText !== 'abort') {
          if (xhr.status !== 502) {
            $(document).trigger('error', xhr.responseText || textStatus);
          }
          self.status('failed');
        }
      });

      return self.lastGetLogsRequest;
    };

    self.uploadQueryHistory = function (n) {
      hueAnalytics.log('notebook', 'upload_query_history');

      $.post(
        '/metadata/api/optimizer/upload/history',
        {
          n: typeof n != 'undefined' ? n : null,
          sourcePlatform: self.type()
        },
        data => {
          if (data.status == 0) {
            $(document).trigger(
              'info',
              data.upload_history[self.type()].count +
                ' queries uploaded successfully. Processing them...'
            );
            self.watchUploadStatus(data.upload_history[self.type()].status.workloadId);
          } else {
            $(document).trigger('error', data.message);
          }
        }
      );
    };

    self.uploadQuery = function (query_id) {
      $.post('/metadata/api/optimizer/upload/query', {
        query_id: query_id,
        sourcePlatform: self.type()
      });
    };

    self.uploadTableStats = function (options) {
      hueAnalytics.log('notebook', 'load_table_stats');
      if (options.showProgress) {
        $(document).trigger('info', 'Preparing table data...');
      }

      $.post(
        '/metadata/api/optimizer/upload/table_stats',
        {
          db_tables: komapping.toJSON(
            $.map(options.activeTables, table => {
              return table.databaseName + '.' + table.tableName;
            })
          ),
          sourcePlatform: komapping.toJSON(self.type()),
          with_ddl: komapping.toJSON(true),
          with_table_stats: komapping.toJSON(true),
          with_columns_stats: komapping.toJSON(true)
        },
        data => {
          if (data.status == 0) {
            if (options.showProgress) {
              $(document).trigger(
                'info',
                $.map(options.activeTables, table => {
                  return table.tableName;
                }) + ' stats sent to analyse'
              );
            }
            if (data.upload_table_ddl && options.showProgress) {
              // With showProgress only currently as can be very slow
              self.watchUploadStatus(data.upload_table_ddl.status.workloadId, options.showProgress);
            }
          } else if (options.showProgress) {
            $(document).trigger('error', data.message);
          }
        }
      ).always(() => {
        if (options.callback) {
          options.callback();
        }
      });
    };

    self.watchUploadStatus = function (workloadId, showProgress) {
      $.post(
        '/metadata/api/optimizer/upload/status',
        {
          workloadId: workloadId
        },
        data => {
          if (data.status == 0) {
            if (showProgress) {
              $(document).trigger('info', 'Query processing: ' + data.upload_status.status.state);
            }
            if (['WAITING', 'IN_PROGRESS'].indexOf(data.upload_status.status.state) != -1) {
              window.setTimeout(() => {
                self.watchUploadStatus(workloadId);
              }, 2000);
            } else if (showProgress) {
              $(document).trigger(
                'warn',
                data.upload_status.status.statusMsg +
                  (data.upload_status.status.failedQueries > 0
                    ? '. ' +
                      data.upload_status.status.failQueryDetails.map(query => {
                        return query.error;
                      })
                    : '')
              );
            }
          } else if (showProgress) {
            $(document).trigger('error', data.message);
          }
        }
      );
    };

    self.getSimilarQueries = function () {
      hueAnalytics.log('notebook', 'get_query_similarity');

      $.post(
        '/notebook/api/optimizer/statement/similarity',
        {
          notebook: komapping.toJSON(notebook.getContext()),
          snippet: komapping.toJSON(self.getContext()),
          sourcePlatform: self.type()
        },
        data => {
          if (data.status == 0) {
            // eslint-disable-next-line no-restricted-syntax
            console.log(data.statement_similarity);
          } else {
            $(document).trigger('error', data.message);
          }
        }
      );
    };

    self.autocompleter = new AceAutocompleteWrapper({
      snippet: self,
      user: vm.user,
      optEnabled: false,
      timeout: vm.autocompleteTimeout
    });

    self.init = function () {
      if ((self.status() == 'running' || self.status() == 'available') && notebook.isHistory()) {
        self.checkStatus();
      } else if (self.status() == 'loading') {
        self.status('failed');
        self.progress(0);
        self.jobs([]);
      } else if (self.status() == 'ready-execute') {
        self.execute();
      }
    };

    self.onKeydownInVariable = function (context, e) {
      if ((e.ctrlKey || e.metaKey) && e.which === 13) {
        // Ctrl-enter
        self.ace().commands.commands['execute'].exec();
      } else if ((e.ctrlKey || e.metaKey) && e.which === 83) {
        // Ctrl-s
        self.ace().commands.commands['save'].exec();
        e.preventDefault(); // Prevent browser page save dialog
      }
      return true;
    };

    self.refreshHistory = notebook.fetchHistory;
  }

  dashboardRedirect() {
    const statement =
      this.selectedStatement() ||
      (this.positionStatement() && this.positionStatement().statement) ||
      this.statement_raw();
    window.open(
      window.CUSTOM_DASHBOARD_URL +
        '?db=' +
        window.encodeURIComponent(this.database()) +
        '&query=' +
        window.encodeURIComponent(statement),
      '_blank'
    );
  }

  renderMarkdown() {
    return this.statement_raw().replace(/([^$]*)([$]+[^$]*[$]+)?/g, (a, textRepl, code) => {
      return markdown.toHTML(textRepl).replace(/^<p>|<\/p>$/g, '') + (code ? code : '');
    });
  }

  async exportHistory() {
    const historyResponse = await apiHelper.getHistory({ type: this.type(), limit: 500 });

    if (historyResponse && historyResponse.history) {
      window.location.href =
        window.HUE_BASE_URL +
        '/desktop/api2/doc/export?history=true&documents=[' +
        historyResponse.history.map(historyDoc => historyDoc.id).join(',') +
        ']';
    }
  }

  toggleAllResultColumns(linkElement) {
    const $t = $(linkElement).parents('.snippet').find('table.resultTable:eq(0)');
    const dt = $t.hueDataTable();
    dt.fnToggleAllCols(linkElement.checked);
    dt.fnDraw();
  }

  toggleResultColumn(linkElement, index) {
    const $t = $(linkElement).parents('.snippet').find('table.resultTable:eq(0)');
    const dt = $t.hueDataTable();
    dt.fnSetColumnVis(index, linkElement.checked);
  }
  scrollToResultColumn(linkElement) {
    const $resultTable = $(linkElement).parents('.snippet').find('table.resultTable:eq(0)');
    const _text = $.trim($(linkElement).text());
    const _col = $resultTable.find('th').filter(function () {
      return $.trim($(this).text()) === _text;
    });
    $resultTable.find('.columnSelected').removeClass('columnSelected');
    const _colSel = $resultTable.find('tr th:nth-child(' + (_col.index() + 1) + ')');
    if (_colSel.length > 0) {
      $resultTable.find('tr td:nth-child(' + (_col.index() + 1) + ')').addClass('columnSelected');
      $resultTable
        .parent()
        .scrollLeft(
          _colSel.position().left +
            $resultTable.parent().scrollLeft() -
            $resultTable.parent().offset().left -
            30
        );
      $resultTable.data('scrollToCol', _col.index());
      $resultTable.data('scrollToRow', null);
      $resultTable.data('scrollAnimate', true);
      $resultTable.parent().trigger('scroll');
    }
  }
}

export default Snippet;
