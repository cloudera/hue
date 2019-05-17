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
import { markdown } from 'markdown';

import AceAutocompleteWrapper from 'apps/notebook/aceAutocompleteWrapper';
import apiHelper from 'api/apiHelper';
import dataCatalog from 'catalog/dataCatalog';
import { ExecutableStatement } from 'apps/notebook2/execution/executableStatement';
import Executor from 'apps/notebook2/execution/executor';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import { NOTEBOOK_MAPPING } from 'apps/notebook2/notebook';
import Result from 'apps/notebook2/result';
import Session from 'apps/notebook2/session';

// TODO: Remove. Temporary here for debug
window.ExecutableStatement = ExecutableStatement;
window.Executor = Executor;

const TYPE = {
  hive: 'hive',
  impala: 'impala',
  jar: 'jar',
  py: 'py',
  java: 'java',
  spark2: 'spark2',
  shell: 'shell',
  mapreduce: 'mapreduce',
  pig: 'pig',
  distcp: 'distcp',
  sqoop1: 'sqoop1'
};

const STATUS = {
  available: 'available',
  canceled: 'canceled',
  canceling: 'canceling',
  expired: 'expired',
  failed: 'failed',
  loading: 'loading',
  ready: 'ready',
  readyExecute: 'ready-execute',
  running: 'running',
  starting: 'starting',
  success: 'success',
  waiting: 'waiting',
  withOptimizerReport: 'with-optimizer-report'
};

const STATUS_FOR_BUTTONS = {
  canceled: 'canceled',
  canceling: 'canceling',
  executed: 'executed',
  executing: 'executing'
};

const COMPATIBILITY_SOURCE_PLATFORMS = {
  access: { name: 'Access', value: 'access' },
  ansisql: { name: 'ANSISQL', value: 'ansisql' },
  db2: { name: 'DB2', value: 'db2' },
  firebird: { name: 'Firebird', value: 'firebird' },
  generic: { name: 'Generic', value: 'generic' },
  greenplum: { name: 'Greenplum', value: 'greenplum' },
  hive: { name: 'Hive', value: 'hive' },
  impala: { name: 'Impala', value: 'impala' },
  informix: { name: 'Informix', value: 'informix' },
  mysql: { name: 'MySQL', value: 'mysql' },
  netezza: { name: 'Netezza', value: 'netezza' },
  oracle: { name: 'Oracle', value: 'oracle' },
  postgresql: { name: 'PostgreSQL', value: 'postgresql' },
  sqlserver: { name: 'SQL Server', value: 'sqlserver' },
  sybase: { name: 'Sybase', value: 'sybase' },
  teradata: { name: 'Teradata', value: 'teradata' }
};

const COMPATIBILITY_TARGET_PLATFORMS = {
  hive: { name: 'Hive', value: TYPE.hive },
  impala: { name: 'Impala', value: TYPE.impala }
};

const getDefaultSnippetProperties = function(snippetType) {
  const properties = {};

  if (snippetType === TYPE.jar || snippetType === TYPE.py) {
    properties['driverCores'] = '';
    properties['executorCores'] = '';
    properties['numExecutors'] = '';
    properties['queue'] = '';
    properties['archives'] = [];
    properties['files'] = [];
  } else if (snippetType === TYPE.java) {
    properties['archives'] = [];
    properties['files'] = [];
    properties['capture_output'] = false;
  } else if (snippetType === TYPE.shell) {
    properties['archives'] = [];
    properties['files'] = [];
  } else if (snippetType === TYPE.mapreduce) {
    properties['app_jar'] = '';
    properties['hadoopProperties'] = [];
    properties['jars'] = [];
    properties['files'] = [];
    properties['archives'] = [];
  } else if (snippetType === TYPE.spark2) {
    properties['app_name'] = '';
    properties['class'] = '';
    properties['jars'] = [];
    properties['spark_opts'] = [];
    properties['spark_arguments'] = [];
    properties['files'] = [];
  } else if (snippetType === TYPE.sqoop1) {
    properties['files'] = [];
  } else if (snippetType === TYPE.hive) {
    properties['settings'] = [];
    properties['files'] = [];
    properties['functions'] = [];
    properties['arguments'] = [];
  } else if (snippetType === TYPE.impala) {
    properties['settings'] = [];
  } else if (snippetType === TYPE.pig) {
    properties['parameters'] = [];
    properties['hadoopProperties'] = [];
    properties['resources'] = [];
  } else if (snippetType === TYPE.distcp) {
    properties['source_path'] = '';
    properties['destination_path'] = '';
  } else if (snippetType === TYPE.shell) {
    properties['command_path'] = '';
    properties['arguments'] = [];
    properties['env_var'] = [];
    properties['capture_output'] = true;
  }

  if (snippetType === TYPE.jar || snippetType === TYPE.java) {
    properties['app_jar'] = '';
    properties['class'] = '';
    properties['arguments'] = [];
  } else if (snippetType === TYPE.py) {
    properties['py_file'] = '';
    properties['arguments'] = [];
  }

  return properties;
};

const ERROR_REGEX = /line ([0-9]+)(:([0-9]+))?/i;

class Snippet {
  constructor(vm, notebook, snippet) {
    const self = this;

    self.parentVm = vm;
    self.parentNotebook = notebook;

    self.id = ko.observable(snippet.id || hueUtils.UUID());
    self.name = ko.observable(snippet.name || '');
    self.type = ko.observable(snippet.type || TYPE.hive);
    self.type.subscribe(() => {
      self.status(STATUS.ready);
    });

    self.isBatchable = ko.pureComputed(
      () =>
        self.type() === TYPE.hive ||
        self.type() === TYPE.impala ||
        self.parentVm.availableLanguages.some(
          language => language.type === self.type() && language.interface === 'oozie'
        )
    );

    self.autocompleteSettings = {
      temporaryOnly: false
    };

    // Ace stuff
    self.aceCursorPosition = ko.observable(
      self.parentNotebook.isHistory() ? snippet.aceCursorPosition : null
    );

    self.aceEditor = null;

    self.errors = ko.observableArray([]);

    self.aceErrorsHolder = ko.observableArray([]);
    self.aceWarningsHolder = ko.observableArray([]);

    self.aceErrors = ko.pureComputed(() => (self.showOptimizer() ? self.aceErrorsHolder() : []));
    self.aceWarnings = ko.pureComputed(() =>
      self.showOptimizer() ? self.aceWarningsHolder() : []
    );

    self.availableSnippets = self.parentVm.availableSnippets();
    self.inFocus = ko.observable(false);

    self.inFocus.subscribe(newValue => {
      if (newValue) {
        huePubSub.publish('active.snippet.type.changed', {
          type: self.type(),
          isSqlDialect: self.isSqlDialect()
        });
      }
    });

    self.editorMode = self.parentVm.editorMode;

    self.getAceMode = () => self.parentVm.getSnippetViewSettings(self.type()).aceMode;

    self.dbSelectionVisible = ko.observable(false);

    self.showExecutionAnalysis = ko.observable(false);

    self.isSqlDialect = ko.pureComputed(
      () => self.parentVm.getSnippetViewSettings(self.type()).sqlDialect
    );

    // namespace and compute might be initialized as empty object {}
    self.namespace = ko.observable(
      snippet.namespace && snippet.namespace.id ? snippet.namespace : undefined
    );
    self.compute = ko.observable(
      snippet.compute && snippet.compute.id ? snippet.compute : undefined
    );

    self.availableDatabases = ko.observableArray();
    self.database = ko.observable();
    let previousDatabase = null;

    self.database.subscribe(newValue => {
      if (newValue !== null) {
        apiHelper.setInTotalStorage('editor', 'last.selected.database', newValue);
        if (previousDatabase !== null && previousDatabase !== newValue) {
          huePubSub.publish('editor.refresh.statement.locations', self);
        }
        previousDatabase = newValue;
      }
    });

    self.database(snippet.database);

    // History is currently in Notebook, same with saved queries by snippets, might be better in assist
    self.currentQueryTab = ko.observable(snippet.currentQueryTab || 'queryHistory');
    self.pinnedContextTabs = ko.observableArray(snippet.pinnedContextTabs || []);

    self.errorLoadingQueries = ko.observable(false);
    self.loadingQueries = ko.observable(false);

    self.queriesHasErrors = ko.observable(false);
    self.queriesCurrentPage = ko.observable(
      self.parentVm.selectedNotebook() && self.parentVm.selectedNotebook().snippets().length > 0
        ? self.parentVm
            .selectedNotebook()
            .snippets()[0]
            .queriesCurrentPage()
        : 1
    );
    self.queriesTotalPages = ko.observable(
      self.parentVm.selectedNotebook() && self.parentVm.selectedNotebook().snippets().length > 0
        ? self.parentVm
            .selectedNotebook()
            .snippets()[0]
            .queriesTotalPages()
        : 1
    );
    self.queries = ko.observableArray([]);

    self.queriesFilter = ko.observable('');
    self.queriesFilterVisible = ko.observable(false);
    self.queriesFilter.extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 900 } });
    self.queriesFilter.subscribe(() => {
      self.fetchQueries();
    });

    self.lastFetchQueriesRequest = null;

    self.lastQueriesPage = 1;
    self.currentQueryTab.subscribe(newValue => {
      huePubSub.publish('redraw.fixed.headers');
      huePubSub.publish('current.query.tab.switched', newValue);
      if (
        newValue === 'savedQueries' &&
        (self.queries().length === 0 || self.lastQueriesPage !== self.queriesCurrentPage())
      ) {
        self.fetchQueries();
      }
    });

    huePubSub.subscribeOnce(
      'assist.source.set',
      source => {
        if (source !== self.type()) {
          huePubSub.publish('assist.set.source', self.type());
        }
      },
      self.parentVm.huePubSubId
    );

    huePubSub.publish('assist.get.source');

    self.ignoreNextAssistDatabaseUpdate = false;

    if (!self.database()) {
      huePubSub.publish('assist.get.database.callback', {
        source: self.type(),
        callback: function(databaseDef) {
          self.handleAssistSelection(databaseDef);
        }
      });
    }

    self.statementType = ko.observable(snippet.statementType || 'text');
    self.statementTypes = ko.observableArray(['text', 'file']); // Maybe computed later for Spark
    if (!self.parentVm.editorMode()) {
      self.statementTypes.push('document');
    }
    self.statementPath = ko.observable(snippet.statementPath || '');
    self.externalStatementLoaded = ko.observable(false);

    self.statementPath.subscribe(() => {
      self.getExternalStatement();
    });

    self.associatedDocumentLoading = ko.observable(true);
    self.associatedDocument = ko.observable();
    self.associatedDocumentUuid = ko.observable(snippet.associatedDocumentUuid);
    self.associatedDocumentUuid.subscribe(val => {
      if (val !== '') {
        self.getExternalStatement();
      } else {
        self.statement_raw('');
        self.ace().setValue('', 1);
      }
    });
    self.statement_raw = ko.observable(snippet.statement_raw || '');
    self.selectedStatement = ko.observable('');
    self.positionStatement = ko.observable(null);
    self.lastExecutedStatement = ko.observable(null);
    self.statementsList = ko.observableArray();

    huePubSub.subscribe(
      'editor.active.statement.changed',
      statementDetails => {
        if (self.ace() && self.ace().container.id === statementDetails.id) {
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
          if (!self.parentNotebook.isPresentationModeInitialized()) {
            if (self.parentNotebook.isPresentationModeDefault()) {
              // When switching to presentation mode, the snippet in non presentation mode cannot get status notification.
              // On initiailization, status is set to loading and does not get updated, because we moved to presentation mode.
              self.status(STATUS.ready);
            }
            // Changing to presentation mode requires statementsList to be initialized. statementsList is initialized asynchronously.
            // When presentation mode is default, we cannot change before statementsList has been calculated.
            // Cleaner implementation would be to make toggleEditorMode statementsList asynchronous
            // However this is currently impossible due to delete _notebook.presentationSnippets()[key];
            self.parentNotebook.isPresentationModeInitialized(true);
            self.parentNotebook.isPresentationMode(self.parentNotebook.isPresentationModeDefault());
          }
        }
      },
      self.parentVm.huePubSubId
    );

    self.aceSize = ko.observable(snippet.aceSize || 100);
    self.status = ko.observable(snippet.status || STATUS.loading);
    self.statusForButtons = ko.observable(STATUS_FOR_BUTTONS.executed);

    self.properties = ko.observable(
      komapping.fromJS(snippet.properties || getDefaultSnippetProperties(self.type()))
    );
    self.hasProperties = ko.pureComputed(
      () => Object.keys(komapping.toJS(self.properties())).length > 0
    );

    self.viewSettings = ko.pureComputed(() => self.parentVm.getSnippetViewSettings(self.type()));

    const previousProperties = {};
    self.type.subscribe(
      oldValue => {
        previousProperties[oldValue] = self.properties();
      },
      null,
      'beforeChange'
    );

    self.type.subscribe(newValue => {
      if (typeof previousProperties[newValue] !== 'undefined') {
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
    self.variables = komapping.fromJS(snippet.variables || []);
    self.variables.subscribe(() => {
      $(document).trigger('updateResultHeaders', self);
    });
    self.hasCurlyBracketParameters = ko.pureComputed(() => self.type() !== TYPE.pig);

    self.variableNames = ko.pureComputed(() => {
      let match,
        matches = {},
        matchList;
      if (self.type() === TYPE.pig) {
        matches = self.getPigParameters();
      } else {
        const re = /(?:^|\W)\${(\w*)=?([^{}]*)}/g;
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
              option.value
                .trim()
                .replace(',', ',')
                .replace('(', '(')
                .replace(')', ')');

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
            !value.options || value.options.some(current => current.value === value.placeholder);
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
        window.setTimeout(() => {
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
    huePubSub.subscribe('ace.sql.location.worker.message', e => {
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
          const re = /\${(\w*)=?([^{}]*)}/g;
          const name = re.exec(location.value)[1];
          variables[name] = location;
          return variables;
        }, {});
      const updateVariableType = function(variable, sourceMeta) {
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

    self.statement = ko.pureComputed(() => {
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
              variable.type() === 'datetime-local' && variable.value().length === 16 ? ':00' : ''; // Chrome drops the seconds from the timestamp when it's at 0 second.
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

    $.extend(
      snippet,
      snippet.chartType === 'lines' && {
        // Retire line chart
        chartType: 'bars',
        chartTimelineType: 'line'
      }
    );

    self.result = new Result(snippet.result, self);
    if (!self.result.hasSomeResults()) {
      self.currentQueryTab('queryHistory');
    }
    self.showGrid = ko.observable(snippet.showGrid !== false);
    self.showChart = ko.observable(!!snippet.showChart);
    if (!self.showGrid() && !self.showChart()) {
      self.showGrid(true);
    }
    let defaultShowLogs = true;
    if (self.parentVm.editorMode() && $.totalStorage('hue.editor.showLogs')) {
      defaultShowLogs = $.totalStorage('hue.editor.showLogs');
    }
    self.showLogs = ko.observable(snippet.showLogs || defaultShowLogs);
    self.progress = ko.observable(snippet.progress || 0);
    self.jobs = ko.observableArray(snippet.jobs || []);

    self.executeNextTimeout = -1;
    self.refreshTimeouts = {};

    self.progress.subscribe(val => {
      $(document).trigger('progress', { data: val, snippet: self });
    });

    self.showGrid.subscribe(val => {
      if (val) {
        self.showChart(false);
        huePubSub.publish('editor.grid.shown', self);
      }
    });

    self.showChart.subscribe(val => {
      if (val) {
        self.showGrid(false);
        self.isResultSettingsVisible(true);
        $(document).trigger('forceChartDraw', self);
        huePubSub.publish('editor.chart.shown', self);
        self.prepopulateChart();
      }
    });
    self.showLogs.subscribe(val => {
      huePubSub.publish('redraw.fixed.headers');
      if (val) {
        self.getLogs();
      }
      if (self.parentVm.editorMode()) {
        $.totalStorage('hue.editor.showLogs', val);
      }
    });

    self.isLoading = ko.pureComputed(() => self.status() === STATUS.loading);

    self.resultsKlass = ko.pureComputed(() => 'results ' + self.type());

    self.errorsKlass = ko.pureComputed(() => self.resultsKlass() + ' alert alert-error');

    self.is_redacted = ko.observable(!!snippet.is_redacted);

    self.chartType = ko.observable(snippet.chartType || window.HUE_CHARTS.TYPES.BARCHART);
    self.chartType.subscribe(self.prepopulateChart.bind(self));
    self.chartSorting = ko.observable(snippet.chartSorting || 'none');
    self.chartScatterGroup = ko.observable(snippet.chartScatterGroup);
    self.chartScatterSize = ko.observable(snippet.chartScatterSize);
    self.chartScope = ko.observable(snippet.chartScope || 'world');
    self.chartTimelineType = ko.observable(snippet.chartTimelineType || 'bar');
    self.chartLimits = ko.observableArray([5, 10, 25, 50, 100]);
    self.chartLimit = ko.observable(snippet.chartLimit);
    self.chartLimit.extend({ notify: 'always' });
    self.chartX = ko.observable(snippet.chartX);
    self.chartX.extend({ notify: 'always' });
    self.chartXPivot = ko.observable(snippet.chartXPivot);
    self.chartXPivot.extend({ notify: 'always' });
    self.chartXPivot.subscribe(self.prepopulateChart.bind(self));
    self.chartYSingle = ko.observable(snippet.chartYSingle);
    self.chartYMulti = ko.observableArray(snippet.chartYMulti || []);
    self.chartData = ko.observableArray(snippet.chartData || []);
    self.chartMapType = ko.observable(snippet.chartMapType || 'marker');
    self.chartMapLabel = ko.observable(snippet.chartMapLabel);
    self.chartMapHeat = ko.observable(snippet.chartMapHeat);
    self.hideStacked = ko.pureComputed(() => self.chartYMulti().length <= 1);

    self.hasDataForChart = ko.pureComputed(() => {
      if (
        self.chartType() === window.HUE_CHARTS.TYPES.BARCHART ||
        self.chartType() === window.HUE_CHARTS.TYPES.LINECHART ||
        self.chartType() === window.HUE_CHARTS.TYPES.TIMELINECHART
      ) {
        return (
          typeof self.chartX() !== 'undefined' &&
          self.chartX() !== null &&
          self.chartYMulti().length > 0
        );
      }
      return (
        typeof self.chartX() !== 'undefined' &&
        self.chartX() !== null &&
        typeof self.chartYSingle() !== 'undefined' &&
        self.chartYSingle() !== null
      );
    });

    self.hasDataForChart.subscribe(() => {
      self.chartX.notifySubscribers();
      self.chartX.valueHasMutated();
    });

    self.chartType.subscribe(() => {
      $(document).trigger('forceChartDraw', self);
    });

    self.previousChartOptions = {};

    self.result.meta.subscribe(() => {
      self.chartLimit(self.previousChartOptions.chartLimit);
      self.chartX(self.guessMetaField(self.previousChartOptions.chartX));
      self.chartXPivot(self.previousChartOptions.chartXPivot);
      self.chartYSingle(self.guessMetaField(self.previousChartOptions.chartYSingle));
      self.chartMapType(self.previousChartOptions.chartMapType);
      self.chartMapLabel(self.guessMetaField(self.previousChartOptions.chartMapLabel));
      self.chartMapHeat(self.previousChartOptions.chartMapHeat);
      self.chartYMulti(self.guessMetaFields(self.previousChartOptions.chartYMulti) || []);
      self.chartSorting(self.previousChartOptions.chartSorting);
      self.chartScatterGroup(self.previousChartOptions.chartScatterGroup);
      self.chartScatterSize(self.previousChartOptions.chartScatterSize);
      self.chartScope(self.previousChartOptions.chartScope);
      self.chartTimelineType(self.previousChartOptions.chartTimelineType);
    });

    self.isResultSettingsVisible = ko.observable(!!snippet.isResultSettingsVisible);

    self.isResultSettingsVisible.subscribe(() => {
      $(document).trigger('toggleResultSettings', self);
    });

    self.settingsVisible = ko.observable(!!snippet.settingsVisible);
    self.saveResultsModalVisible = ko.observable(false);

    self.checkStatusTimeout = null;
    self.getLogsTimeout = null;

    self.complexity = ko.observable();
    self.hasComplexity = ko.pureComputed(
      () => self.complexity() && Object.keys(self.complexity()).length > 0
    );
    self.hasRisks = ko.pureComputed(
      () =>
        self.hasComplexity() && self.complexity()['hints'] && self.complexity()['hints'].length > 0
    );
    self.topRisk = ko.pureComputed(() =>
      self.hasRisks() ? self.complexity()['hints'][0] : undefined
    );

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

    if (HAS_OPTIMIZER && !self.parentVm.isNotificationManager()) {
      let lastComplexityRequest;
      let lastCheckedComplexityStatement;
      const knownResponses = [];

      self.delayedStatement = ko
        .pureComputed(self.statement)
        .extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 2000 } });

      const handleRiskResponse = function(data) {
        if (data.status === 0) {
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

      const clearActiveRisks = function() {
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

      self.checkComplexity = function() {
        if (!self.inFocus() || lastCheckedComplexityStatement === self.statement()) {
          return;
        }

        // The syntaxError property is only set if the syntax checker is active and has found an
        // error, see AceLocationHandler.
        if (self.positionStatement() && self.positionStatement().syntaxError) {
          return;
        }

        apiHelper.cancelActiveRequest(lastComplexityRequest);

        hueAnalytics.log('notebook', 'get_query_risk');
        clearActiveRisks();

        const changeSubscription = self.statement.subscribe(() => {
          changeSubscription.dispose();
          apiHelper.cancelActiveRequest(lastComplexityRequest);
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
              notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
              snippet: komapping.toJSON(self.getContext())
            },
            success: data => {
              knownResponses.unshift({
                hash: hash,
                data: data
              });
              if (knownResponses.length > 50) {
                knownResponses.pop();
              }
              handleRiskResponse(data);
            },
            always: () => {
              changeSubscription.dispose();
            }
          });
        }
      };

      if (self.type() === TYPE.hive || self.type() === TYPE.impala) {
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

    self.wasBatchExecuted = ko.observable(!!snippet.wasBatchExecuted);
    self.isReady = ko.pureComputed(
      () =>
        (self.statementType() === 'text' &&
          ((self.isSqlDialect() && self.statement() !== '') ||
            ([TYPE.jar, TYPE.java, TYPE.spark2, TYPE.distcp].indexOf(self.type()) === -1 &&
              self.statement() !== '') ||
            ([TYPE.jar, TYPE.java].indexOf(self.type()) !== -1 &&
              (self.properties().app_jar() !== '' && self.properties().class() !== '')) ||
            (TYPE.spark2 === self.type() && self.properties().jars().length > 0) ||
            (TYPE.shell === self.type() && self.properties().command_path().length > 0) ||
            (TYPE.mapreduce === self.type() && self.properties().app_jar().length > 0) ||
            (TYPE.distcp === self.type() &&
              self.properties().source_path().length > 0 &&
              self.properties().destination_path().length > 0))) ||
        (self.statementType() === 'file' && self.statementPath().length > 0) ||
        (self.statementType() === 'document' &&
          self.associatedDocumentUuid() &&
          self.associatedDocumentUuid().length > 0)
    );
    self.lastExecuted = ko.observable(snippet.lastExecuted || 0);
    self.lastAceSelectionRowOffset = ko.observable(snippet.lastAceSelectionRowOffset || 0);

    self.executingBlockingOperation = null; // A ExecuteStatement()
    self.showLongOperationWarning = ko.observable(false);
    self.showLongOperationWarning.subscribe(newValue => {
      if (newValue) {
        hueAnalytics.convert('editor', 'showLongOperationWarning');
      }
    });

    self.longOperationTimeout = -1;

    self.lastExecutedStatements = undefined;
    self.lastExecutedSelectionRange = undefined;

    self.formatEnabled = ko.pureComputed(
      () =>
        self.statement_raw && self.statement_raw() != null && self.statement_raw().length < 400000
    );

    self.lastCompatibilityRequest = undefined;

    self.isFetchingData = false;

    self.isCanceling = ko.observable(false);

    self.autocompleter = new AceAutocompleteWrapper({
      snippet: self,
      user: self.parentVm.user,
      optEnabled: false,
      timeout: self.parentVm.autocompleteTimeout
    });

    self.executor = undefined;

    huePubSub.subscribe('hue.executor.updated', details => {
      const executable = details.executable;

      if (details.executor === self.executor) {
        self.status(executable.status);
        self.progress(executable.progress);
      }
    });
  }

  ace(newVal) {
    const self = this;
    if (newVal) {
      self.aceEditor = newVal;
      if (!self.parentNotebook.isPresentationMode()) {
        self.aceEditor.focus();
      }
    }
    return self.aceEditor;
  }

  cancel() {
    const self = this;
    window.clearTimeout(self.executeNextTimeout);
    self.isCanceling(true);
    if (self.checkStatusTimeout != null) {
      clearTimeout(self.checkStatusTimeout);
      self.checkStatusTimeout = null;
      clearTimeout(self.getLogsTimeout);
      self.getLogsTimeout = null;
    }
    hueAnalytics.log('notebook', 'cancel');

    if (self.executingBlockingOperation != null) {
      self.executingBlockingOperation.abort();
      self.executingBlockingOperation = null;
    }

    if ($.isEmptyObject(self.result.handle())) {
      // Query was not even submitted yet
      self.statusForButtons(STATUS_FOR_BUTTONS.canceled);
      self.status(STATUS.failed);
      self.isCanceling(false);
      self.parentNotebook.isExecutingAll(false);
    } else {
      self.statusForButtons(STATUS_FOR_BUTTONS.canceling);
      $.post(
        '/notebook/api/cancel_statement',
        {
          notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
          snippet: komapping.toJSON(self.getContext())
        },
        data => {
          self.statusForButtons(STATUS_FOR_BUTTONS.canceled);
          if (data.status === 0) {
            self.status(STATUS.canceled);
            self.parentNotebook.isExecutingAll(false);
          } else {
            self.handleAjaxError(data);
          }
        }
      )
        .fail(xhr => {
          if (xhr.status !== 502) {
            $(document).trigger('error', xhr.responseText);
          }
          self.statusForButtons(STATUS_FOR_BUTTONS.canceled);
          self.status(STATUS.failed);
          self.parentNotebook.isExecutingAll(false);
        })
        .always(() => {
          self.isCanceling(false);
        });
    }
  }

  checkCompatibility() {
    const self = this;
    self.hasSuggestion(null);
    self.compatibilitySourcePlatform(COMPATIBILITY_SOURCE_PLATFORMS[self.type()]);
    self.compatibilityTargetPlatform(
      COMPATIBILITY_TARGET_PLATFORMS[self.type() === TYPE.hive ? TYPE.impala : TYPE.hive]
    );
    self.queryCompatibility();
  }

  checkDdlNotification() {
    const self = this;
    if (
      self.lastExecutedStatement() &&
      /ALTER|CREATE|DELETE|DROP|GRANT|INSERT|LOAD|SET|TRUNCATE|UPDATE|UPSERT|USE/i.test(
        self.lastExecutedStatement().firstToken
      )
    ) {
      self.onDdlExecute();
    } else {
      window.clearTimeout(self.executeNextTimeout);
    }
  }

  checkStatus() {
    const self = this;
    const _checkStatus = function() {
      $.post(
        '/notebook/api/check_status',
        {
          notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
          snippet: komapping.toJSON(self.getContext())
        },
        data => {
          if (
            self.statusForButtons() === STATUS_FOR_BUTTONS.canceling ||
            self.status() === STATUS.canceled
          ) {
            // Query was canceled in the meantime, do nothing
          } else {
            self.result.endTime(new Date());

            if (data.status === 0) {
              self.status(data.query_status.status);

              if (
                self.status() === STATUS.running ||
                self.status() === STATUS.starting ||
                self.status() === STATUS.waiting
              ) {
                const delay = self.result.executionTime() > 45000 ? 5000 : 1000; // 5s if more than 45s
                if (!self.parentNotebook.unloaded()) {
                  self.checkStatusTimeout = setTimeout(_checkStatus, delay);
                }
              } else if (self.status() === STATUS.available) {
                self.fetchResult(100);
                self.progress(100);
                if (self.isSqlDialect()) {
                  if (self.result.handle().has_result_set) {
                    const _query_id = self.parentNotebook.id();
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
                if (self.parentNotebook.isExecutingAll()) {
                  self.parentNotebook.executingAllIndex(
                    self.parentNotebook.executingAllIndex() + 1
                  );
                  if (
                    self.parentNotebook.executingAllIndex() < self.parentNotebook.snippets().length
                  ) {
                    self.parentNotebook
                      .snippets()
                      [self.parentNotebook.executingAllIndex()].execute();
                  } else {
                    self.parentNotebook.isExecutingAll(false);
                  }
                }
                if (!self.result.handle().has_more_statements && self.parentVm.successUrl()) {
                  huePubSub.publish('open.link', self.parentVm.successUrl()); // Not used anymore in Hue 4
                }
              } else if (self.status() === STATUS.success) {
                self.progress(99);
              }
            } else if (data.status === -3) {
              self.status(STATUS.expired);
              self.parentNotebook.isExecutingAll(false);
            } else {
              self.handleAjaxError(data);
              self.parentNotebook.isExecutingAll(false);
            }
          }
        }
      ).fail((xhr, textStatus) => {
        if (xhr.status !== 502) {
          $(document).trigger('error', xhr.responseText || textStatus);
        }
        self.status(STATUS.failed);
        self.parentNotebook.isExecutingAll(false);
      });
    };
    const activeStatus = ['running', 'starting', 'waiting'];
    const _getLogs = function(isLastTime) {
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
  }

  clear() {
    const self = this;
    hueAnalytics.log('notebook', 'clear');
    self.ace().setValue('', 1);
    self.result.clear();
    self.status(STATUS.ready);
  }

  close() {
    const self = this;
    if (self.checkStatusTimeout != null) {
      clearTimeout(self.checkStatusTimeout);
      self.checkStatusTimeout = null;
      clearTimeout(self.getLogsTimeout);
      self.getLogsTimeout = null;
    }

    $.post('/notebook/api/close_statement', {
      notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
      snippet: komapping.toJSON(self.getContext())
    });
  }

  execute(automaticallyTriggered) {
    hueAnalytics.log('notebook', 'execute/' + this.type());

    const now = new Date().getTime();
    if (now - this.lastExecuted() < 1000) {
      return; // Prevent fast clicks
    }
    this.lastExecuted(now);

    if (this.type() === TYPE.impala) {
      this.showExecutionAnalysis(false);
      huePubSub.publish('editor.clear.execution.analysis');
    }

    // Editor based execution
    if (this.ace()) {
      const selectionRange = this.ace().getSelectionRange();

      if (this.isSqlDialect()) {
        huePubSub.publish('editor.refresh.statement.locations', this);
      }

      huePubSub.publish('ace.set.autoexpand', { autoExpand: false, snippet: this });
      this.lastAceSelectionRowOffset(Math.min(selectionRange.start.row, selectionRange.end.row));
    }

    this.previousChartOptions = this.parentVm.getPreviousChartOptions(this);
    $(document).trigger('executeStarted', { vm: this.parentVm, snippet: this });
    $('.jHueNotify').remove();
    this.parentNotebook.forceHistoryInitialHeight(true);
    this.errors([]);
    huePubSub.publish('editor.clear.highlighted.errors', this.ace());
    this.result.clear();
    this.progress(0);
    this.jobs([]);

    this.parentNotebook.historyCurrentPage(1);

    this.startLongOperationTimeout();

    this.currentQueryTab('queryHistory');

    if (this.executor && this.executor.isRunning()) {
      this.executor.cancel();
    }

    this.executor = new Executor({
      compute: this.compute(),
      database: this.database(),
      sourceType: this.type(),
      namespace: this.namespace(),
      statement: this.statement(),
      isSqlEngine: this.isSqlDialect(),
      sessions: komapping.toJS(this.parentNotebook.sessions)
    });

    this.executor.executeNext().then(executionResult => {
      this.stopLongOperationTimeout();
      this.result.update(executionResult).then(() => {
        if (this.result.data().length) {
          this.currentQueryTab('queryResults');
        }
      });
    });
  }

  explain() {
    const self = this;
    hueAnalytics.log('notebook', 'explain');

    if (
      self.statement() === '' ||
      self.status() === STATUS.running ||
      self.status() === STATUS.loading
    ) {
      return;
    }

    self.result.explanation('');
    self.errors([]);
    self.progress(0);
    self.status(STATUS.ready);

    $.post(
      '/notebook/api/explain',
      {
        notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
        snippet: komapping.toJSON(self.getContext())
      },
      data => {
        if (data.status === 0) {
          self.currentQueryTab('queryExplain');
          self.result.fetchedOnce(true);
          self.result.explanation(data.explanation);
        } else {
          self.handleAjaxError(data);
        }
      }
    );
  }

  fetchExecutionAnalysis() {
    const self = this;
    if (self.type() === TYPE.impala) {
      // TODO: Use real query ID
      huePubSub.publish('editor.update.execution.analysis', {
        analysisPossible: true,
        compute: self.compute(),
        queryId: self.parentNotebook.getContext().id(),
        name: self.jobs()[0] && self.jobs()[0].name
      });
    } else {
      huePubSub.publish('editor.update.execution.analysis', {
        analysisPossible: false
      });
    }
  }

  fetchQueries() {
    const self = this;
    apiHelper.cancelActiveRequest(self.lastFetchQueriesRequest);

    const QUERIES_PER_PAGE = 50;
    self.lastQueriesPage = self.queriesCurrentPage();
    self.loadingQueries(true);
    self.queriesHasErrors(false);
    self.lastFetchQueriesRequest = apiHelper.searchDocuments({
      successCallback: function(result) {
        self.queriesTotalPages(Math.ceil(result.count / QUERIES_PER_PAGE));
        self.queries(komapping.fromJS(result.documents)());
        self.loadingQueries(false);
        self.queriesHasErrors(false);
      },
      errorCallback: function() {
        self.loadingQueries(false);
        self.queriesHasErrors(true);
      },
      page: self.queriesCurrentPage(),
      limit: QUERIES_PER_PAGE,
      type: 'query-' + self.type(),
      query: self.queriesFilter(),
      include_trashed: false
    });
  }

  // TODO: Switch to result.fetchMoreRows in ko mako
  fetchResult(rows, startOver) {
    this.result.fetchMoreRows(rows, startOver);
  }

  // fetchResultData(rows, startOver) {
  //   console.log('fetchResultData');
  //   const self = this;
  //   if (!self.isFetchingData) {
  //     if (self.status() === STATUS.available) {
  //       self.startLongOperationTimeout();
  //       self.isFetchingData = true;
  //       hueAnalytics.log('notebook', 'fetchResult/' + rows + '/' + startOver);
  //       $.post(
  //         '/notebook/api/fetch_result_data',
  //         {
  //           notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
  //           snippet: komapping.toJSON(self.getContext()),
  //           rows: rows,
  //           startOver: startOver
  //         },
  //         data => {
  //           self.stopLongOperationTimeout();
  //           data = JSON.bigdataParse(data);
  //           if (data.status === 0) {
  //             self.showExecutionAnalysis(true);
  //             self.loadData(data.result, rows);
  //           } else {
  //             self.handleAjaxError(data, () => {
  //               self.isFetchingData = false;
  //               self.fetchResultData(rows, startOver);
  //             });
  //             $(document).trigger('renderDataError', { snippet: self });
  //           }
  //         },
  //         'text'
  //       )
  //         .fail(xhr => {
  //           if (xhr.status !== 502) {
  //             $(document).trigger('error', xhr.responseText);
  //           }
  //         })
  //         .always(() => {
  //           self.isFetchingData = false;
  //         });
  //     } else {
  //       huePubSub.publish('editor.snippet.result.normal', self);
  //     }
  //   }
  // }

  fetchResultMetadata() {
    const self = this;
    $.post(
      '/notebook/api/fetch_result_metadata',
      {
        notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
        snippet: komapping.toJSON(self.getContext())
      },
      data => {
        if (data.status === 0) {
          self.result.meta(data.result.meta);
        } else {
          $(document).trigger('error', data.message);
        }
      }
    ).fail(xhr => {
      if (xhr.status !== 502) {
        $(document).trigger('error', xhr.responseText);
      }
      self.status(STATUS.failed);
    });
  }

  fetchResultSize(n, query_id) {
    const self = this;
    $.post(
      '/notebook/api/fetch_result_size',
      {
        notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
        snippet: komapping.toJSON(self.getContext())
      },
      data => {
        if (query_id === self.parentNotebook.id()) {
          // If still on the same result
          if (data.status === 0) {
            if (data.result.rows != null) {
              self.result.rows(data.result.rows);
            } else if (self.type() === TYPE.impala && n > 0) {
              setTimeout(() => {
                self.fetchResultSize(n - 1, query_id);
              }, 1000);
            }
          } else if (data.status === 5) {
            // No supported yet for this snippet
          } else {
            //$(document).trigger("error", data.message);
          }
        }
      }
    );
  }

  format() {
    const self = this;
    console.log(self);
    if (self.isSqlDialect()) {
      apiHelper
        .formatSql({
          statements:
            self.ace().getSelectedText() !== ''
              ? self.ace().getSelectedText()
              : self.statement_raw()
        })
        .done(data => {
          if (data.status === 0) {
            if (self.ace().getSelectedText() !== '') {
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
            self.handleAjaxError(data);
          }
        });
    }
    hueAnalytics.log('notebook', 'format');
  }

  getContext() {
    const self = this;
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
  }

  getExternalStatement() {
    const self = this;
    self.externalStatementLoaded(false);
    $.post(
      '/notebook/api/get_external_statement',
      {
        notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
        snippet: komapping.toJSON(self.getContext())
      },
      data => {
        if (data.status === 0) {
          self.externalStatementLoaded(true);
          self.statement_raw(data.statement);
          self.ace().setValue(self.statement_raw(), 1);
        } else {
          self.handleAjaxError(data);
        }
      }
    );
  }

  getLogs() {
    const self = this;
    return $.post(
      '/notebook/api/get_logs',
      {
        notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
        snippet: komapping.toJSON(self.getContext()),
        from: self.result.logLines,
        jobs: komapping.toJSON(self.jobs, { ignore: ['percentJob'] }),
        full_log: self.result.logs
      },
      data => {
        if (data.status === 1) {
          // Append errors to the logs
          data.status = 0;
          data.logs = data.message;
        }
        if (data.status === 0) {
          if (data.logs.length > 0) {
            const logs = data.logs.split('\n');
            self.result.logLines += logs.length;
            const oldLogs = self.result.logs();
            if (
              data.logs &&
              (oldLogs === '' ||
                (self.wasBatchExecuted() && data.logs.indexOf('Unable to locate') === -1) ||
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
          if (self.status() === STATUS.running) {
            // Maybe the query finished or failed in the meantime
            self.progress(data.progress);
          }
        } else {
          self.handleAjaxError(data);
        }
      }
    ).fail((xhr, textStatus) => {
      if (xhr.status !== 502) {
        $(document).trigger('error', xhr.responseText || textStatus);
      }
      self.status(STATUS.failed);
    });
  }

  getPigParameters() {
    const self = this;
    const params = {};
    const variables = self.statement_raw().match(/([^\\]|^)\$[^\d'"](\w*)/g);
    const declares = self.statement_raw().match(/%declare +([^ ])+/gi);
    const defaults = self.statement_raw().match(/%default +([^;])+/gi);
    const macro_defines = self.statement_raw().match(/define [^ ]+ *\(([^)]*)\)/gi); // no multiline
    const macro_returns = self.statement_raw().match(/returns +([^{]*)/gi); // no multiline

    if (variables) {
      variables.forEach(param => {
        const p = param.substring(param.indexOf('$') + 1);
        params[p] = '';
      });
    }
    if (declares) {
      declares.forEach(param => {
        param = param.match(/(\w+)/g);
        if (param && param.length >= 2) {
          delete params[param[1]];
        }
      });
    }
    if (defaults) {
      defaults.forEach(param => {
        const line = param.match(/(\w+)/g);
        if (line && line.length >= 2) {
          const name = line[1];
          params[name] = param.substring(param.indexOf(name) + name.length + 1);
        }
      });
    }
    if (macro_defines) {
      macro_defines.forEach(params_line => {
        const param_line = params_line.match(/(\w+)/g);
        if (param_line && param_line.length > 2) {
          param_line.forEach((param, index) => {
            if (index >= 2) {
              // Skips define NAME
              delete params[param];
            }
          });
        }
      });
    }
    if (macro_returns) {
      macro_returns.forEach(params_line => {
        const param_line = params_line.match(/(\w+)/g);
        if (param_line) {
          param_line.forEach((param, index) => {
            if (index >= 1) {
              // Skip returns
              delete params[param];
            }
          });
        }
      });
    }

    return params;
  }

  getPlaceHolder() {
    const self = this;
    return self.parentVm.getSnippetViewSettings(self.type()).placeHolder;
  }

  getSimilarQueries() {
    const self = this;
    hueAnalytics.log('notebook', 'get_query_similarity');

    $.post(
      '/notebook/api/optimizer/statement/similarity',
      {
        notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
        snippet: komapping.toJSON(self.getContext()),
        sourcePlatform: self.type()
      },
      data => {
        if (data.status === 0) {
          console.log(data.statement_similarity);
        } else {
          $(document).trigger('error', data.message);
        }
      }
    );
  }

  guessMetaField(field) {
    const self = this;
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

  guessMetaFields(fields) {
    const self = this;
    const _fields = [];
    if (fields) {
      fields.forEach(fld => {
        const _field = self.guessMetaField(fld);
        if (_field) {
          _fields.push(_field);
        }
      });
    }
    return _fields;
  }

  handleAjaxError(data, callback) {
    const self = this;
    if (data.status === -2) {
      // Session expired
      const existingSession = self.parentNotebook.getSession(self.type());
      if (existingSession) {
        self.parentNotebook.restartSession(existingSession, callback);
      } else {
        self.parentNotebook.createSession(
          new Session(self.parentVm, { type: self.type() }),
          callback
        );
      }
    } else if (data.status === -3) {
      // Statement expired
      self.status(STATUS.expired);
      if (data.message) {
        self.errors.push({ message: data.message, help: null, line: null, col: null });
        huePubSub.publish('editor.snippet.result.normal', self);
      }
    } else if (data.status === -4) {
      // Operation timed out
      self.parentNotebook.retryModalCancel = function() {
        self.status(STATUS.failed);
        huePubSub.publish('hide.retry.modal');
      };
      self.parentNotebook.retryModalConfirm = function() {
        if (callback) {
          callback();
        }
        huePubSub.publish('hide.retry.modal');
      };
      huePubSub.publish('show.retry.modal');
    } else if (data.status === 401) {
      // Auth required
      self.status(STATUS.expired);
      $(document).trigger('showAuthModal', {
        type: self.type(),
        callback: self.execute,
        message: data.message
      });
    } else if (data.status === 1 || data.status === -1) {
      self.status(STATUS.failed);
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
      self.status(STATUS.failed);
    }
  }

  handleAssistSelection(databaseDef) {
    const self = this;
    if (self.ignoreNextAssistDatabaseUpdate) {
      self.ignoreNextAssistDatabaseUpdate = false;
    } else if (databaseDef.sourceType === self.type()) {
      if (self.namespace() !== databaseDef.namespace) {
        self.namespace(databaseDef.namespace);
      }
      if (self.database() !== databaseDef.name) {
        self.database(databaseDef.name);
      }
    }
  }

  init() {
    const self = this;
    if (
      (self.status() === STATUS.running || self.status() === STATUS.available) &&
      self.parentNotebook.isHistory()
    ) {
      self.checkStatus();
    } else if (self.status() === STATUS.loading) {
      self.status(STATUS.failed);
      self.progress(0);
      self.jobs([]);
    } else if (self.status() === STATUS.readyExecute) {
      self.execute();
    }
  }

  // loadData(result, rows) {
  //   const self = this;
  //   rows -= result.data.length;
  //
  //   if (result.data.length > 0) {
  //     self.currentQueryTab('queryResults');
  //   }
  //
  //   if (result.has_more && rows > 0) {
  //     setTimeout(() => {
  //       self.fetchResultData(rows, false);
  //     }, 500);
  //   } else if (
  //     !self.parentVm.editorMode() &&
  //     !self.parentNotebook.isPresentationMode() &&
  //     self.parentNotebook.snippets()[self.parentNotebook.snippets().length - 1] === self
  //   ) {
  //     self.parentNotebook.newSnippet();
  //   }
  // }

  nextQueriesPage() {
    const self = this;
    if (self.queriesCurrentPage() !== self.queriesTotalPages()) {
      self.queriesCurrentPage(self.queriesCurrentPage() + 1);
      self.fetchQueries();
    }
  }

  onDdlExecute() {
    const self = this;
    if (self.result.handle() && self.result.handle().has_more_statements) {
      window.clearTimeout(self.executeNextTimeout);
      self.executeNextTimeout = setTimeout(() => {
        self.execute(true); // Execute next, need to wait as we disabled fast click
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
        window.clearTimeout(self.refreshTimeouts[path.join('.')]);
        self.refreshTimeouts[path.join('.')] = window.setTimeout(() => {
          self.ignoreNextAssistDatabaseUpdate = true;
          dataCatalog
            .getEntry({
              sourceType: self.type(),
              namespace: self.namespace(),
              compute: self.compute(),
              path: path
            })
            .done(entry => {
              entry.clearCache({ invalidate: 'invalidate', cascade: true, silenceErrors: true });
            });
        }, 5000);
      }
    }
  }

  onKeydownInVariable(context, e) {
    const self = this;
    if ((e.ctrlKey || e.metaKey) && e.which === 13) {
      // Ctrl-enter
      self.ace().commands.commands['execute'].exec();
    } else if ((e.ctrlKey || e.metaKey) && e.which === 83) {
      // Ctrl-s
      self.ace().commands.commands['save'].exec();
      e.preventDefault(); // Prevent browser page save dialog
    }
    return true;
  }

  prepopulateChart() {
    const self = this;
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
      (type === window.HUE_CHARTS.TYPES.BARCHART ||
        type === window.HUE_CHARTS.TYPES.PIECHART ||
        type === window.HUE_CHARTS.TYPES.GRADIENTMAP) &&
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
          self.result.cleanedNumericMeta()[Math.min(self.result.cleanedNumericMeta().length - 1, 1)]
            .name
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

  prevQueriesPage() {
    const self = this;
    if (self.queriesCurrentPage() !== 1) {
      self.queriesCurrentPage(self.queriesCurrentPage() - 1);
      self.fetchQueries();
    }
  }

  queryCompatibility(targetPlatform) {
    const self = this;
    apiHelper.cancelActiveRequest(self.lastCompatibilityRequest);

    hueAnalytics.log('notebook', 'compatibility');
    self.compatibilityCheckRunning(targetPlatform !== self.type());
    self.hasSuggestion(null);
    const positionStatement = self.positionStatement();

    self.lastCompatibilityRequest = $.post(
      '/notebook/api/optimizer/statement/compatibility',
      {
        notebook: komapping.toJSON(self.parentNotebook.getContext(), NOTEBOOK_MAPPING),
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
                match === null ? null : typeof match[3] !== 'undefined' ? parseInt(match[3]) : null
            });
            self.status(STATUS.withOptimizerReport);
          }
          if (self.suggestion().parseError()) {
            const match = ERROR_REGEX.exec(self.suggestion().parseError());
            self.aceErrorsHolder.push({
              message: self.suggestion().parseError(),
              line: match === null ? null : parseInt(match[1]) - 1,
              col:
                match === null ? null : typeof match[3] !== 'undefined' ? parseInt(match[3]) : null
            });
            self.status(STATUS.withOptimizerReport);
          }
          self.showOptimizer(true);
          self.hasSuggestion(true);
        } else {
          $(document).trigger('error', data.message);
        }
      }
    )
      .fail(xhr => {
        if (xhr.status !== 502) {
          $(document).trigger('error', xhr.responseText);
        }
      })
      .always(() => {
        self.compatibilityCheckRunning(false);
      });
  }

  reexecute() {
    const self = this;
    self.result.cancelBatchExecution();
    self.execute();
  }

  removeContextTab(context) {
    const self = this;
    if (context.tabId === self.currentQueryTab()) {
      self.currentQueryTab('queryHistory');
    }
    self.pinnedContextTabs.remove(context);
  }

  renderMarkdown() {
    return this.statement_raw().replace(/([^$]*)([$]+[^$]*[$]+)?/g, (a, textRepl, code) => {
      return markdown.toHTML(textRepl).replace(/^<p>|<\/p>$/g, '') + (code ? code : '');
    });
  }

  scrollToResultColumn(linkElement) {
    const $resultTable = $(linkElement)
      .parents('.snippet')
      .find('table.resultTable:eq(0)');
    const _text = $.trim($(linkElement).text());
    const _col = $resultTable.find('th').filter(function() {
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

  startLongOperationTimeout() {
    const self = this;
    self.longOperationTimeout = window.setTimeout(() => {
      self.showLongOperationWarning(true);
    }, 2000);
  }

  stopLongOperationTimeout() {
    const self = this;
    window.clearTimeout(self.longOperationTimeout);
    self.showLongOperationWarning(false);
  }

  toggleAllResultColumns(linkElement) {
    const $t = $(linkElement)
      .parents('.snippet')
      .find('table.resultTable:eq(0)');
    const dt = $t.hueDataTable();
    dt.fnToggleAllCols(linkElement.checked);
    dt.fnDraw();
  }

  toggleResultColumn(linkElement, index) {
    const $t = $(linkElement)
      .parents('.snippet')
      .find('table.resultTable:eq(0)');
    const dt = $t.hueDataTable();
    dt.fnSetColumnVis(index, linkElement.checked);
  }

  toggleResultSettings() {
    const self = this;
    self.isResultSettingsVisible(!self.isResultSettingsVisible());
  }

  uploadQuery(query_id) {
    const self = this;
    $.post('/metadata/api/optimizer/upload/query', {
      query_id: query_id,
      sourcePlatform: self.type()
    });
  }

  uploadQueryHistory(n) {
    const self = this;
    hueAnalytics.log('notebook', 'upload_query_history');

    $.post(
      '/metadata/api/optimizer/upload/history',
      {
        n: typeof n != 'undefined' ? n : null,
        sourcePlatform: self.type()
      },
      data => {
        if (data.status === 0) {
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
  }

  uploadTableStats(options) {
    const self = this;
    hueAnalytics.log('notebook', 'load_table_stats');
    if (options.showProgress) {
      $(document).trigger('info', 'Preparing table data...');
    }

    $.post(
      '/metadata/api/optimizer/upload/table_stats',
      {
        db_tables: komapping.toJSON(
          options.activeTables.map(table => table.databaseName + '.' + table.tableName)
        ),
        sourcePlatform: komapping.toJSON(self.type()),
        with_ddl: komapping.toJSON(true),
        with_table_stats: komapping.toJSON(true),
        with_columns_stats: komapping.toJSON(true)
      },
      data => {
        if (data.status === 0) {
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
  }

  watchUploadStatus(workloadId, showProgress) {
    const self = this;
    $.post(
      '/metadata/api/optimizer/upload/status',
      {
        workloadId: workloadId
      },
      data => {
        if (data.status === 0) {
          if (showProgress) {
            $(document).trigger('info', 'Query processing: ' + data.upload_status.status.state);
          }
          if (['WAITING', 'IN_PROGRESS'].indexOf(data.upload_status.status.state) !== -1) {
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
  }

  whenContextSet() {
    const self = this;
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

    result.dispose = function() {
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
  }
}

export { Snippet, STATUS };
