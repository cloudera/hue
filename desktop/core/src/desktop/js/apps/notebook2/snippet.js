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

import 'apps/notebook2/components/ko.executableProgressBar';
import 'apps/notebook2/components/ko.snippetEditorActions';
import 'apps/notebook2/components/ko.snippetExecuteActions';
import 'apps/notebook2/components/resultChart/ko.resultChart';
import 'apps/notebook2/components/resultGrid/ko.resultGrid';

import AceAutocompleteWrapper from 'apps/notebook/aceAutocompleteWrapper';
import apiHelper from 'api/apiHelper';
import dataCatalog from 'catalog/dataCatalog';
import Executor from 'apps/notebook2/execution/executor';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import Result from 'apps/notebook2/result';
import sessionManager from 'apps/notebook2/execution/sessionManager';
import SqlExecutable from 'apps/notebook2/execution/sqlExecutable';
import { notebookToContextJSON, snippetToContextJSON } from 'apps/notebook2/notebookSerde';

// TODO: Remove. Temporary here for debug
window.SqlExecutable = SqlExecutable;
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

export const STATUS = {
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

const getDefaultSnippetProperties = snippetType => {
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

export default class Snippet {
  constructor(vm, notebook, snippet) {
    this.parentVm = vm;
    this.parentNotebook = notebook;

    this.id = ko.observable(snippet.id || hueUtils.UUID());
    this.name = ko.observable(snippet.name || '');
    this.type = ko.observable();
    this.type.subscribe(newValue => {
      // TODO: Add session disposal for ENABLE_NOTEBOOK_2
      // Pre-create a session to speed up execution
      sessionManager.getSession({ type: newValue }).then(() => {
        this.status(STATUS.ready);
      });
    });
    this.type(snippet.type || TYPE.hive);
    this.isBatchable = ko.pureComputed(
      () =>
        this.type() === this.hive ||
        this.type() === this.impala ||
        this.parentVm.availableLanguages.some(
          language =>
            language.type === self.type() &&
            (language.interface == 'oozie' || language.interface == 'sqlalchemy')
        )
    );

    this.autocompleteSettings = {
      temporaryOnly: false
    };

    // Ace stuff
    this.aceCursorPosition = ko.observable(
      this.parentNotebook.isHistory() ? snippet.aceCursorPosition : null
    );

    this.aceEditor = null;

    this.errors = ko.observableArray([]);

    this.executor = ko.observable();

    this.aceErrorsHolder = ko.observableArray([]);
    this.aceWarningsHolder = ko.observableArray([]);

    this.aceErrors = ko.pureComputed(() => (this.showOptimizer() ? this.aceErrorsHolder() : []));
    this.aceWarnings = ko.pureComputed(() =>
      this.showOptimizer() ? this.aceWarningsHolder() : []
    );

    this.availableSnippets = this.parentVm.availableSnippets();
    this.inFocus = ko.observable(false);

    this.inFocus.subscribe(newValue => {
      if (newValue) {
        huePubSub.publish('active.snippet.type.changed', {
          type: this.type(),
          isSqlDialect: this.isSqlDialect()
        });
      }
    });

    this.editorMode = this.parentVm.editorMode;

    this.getAceMode = () => this.parentVm.getSnippetViewSettings(this.type()).aceMode;

    this.dbSelectionVisible = ko.observable(false);

    this.showExecutionAnalysis = ko.observable(false);

    this.isSqlDialect = ko.pureComputed(
      () => this.parentVm.getSnippetViewSettings(this.type()).sqlDialect
    );

    // namespace and compute might be initialized as empty object {}
    this.namespace = ko.observable(
      snippet.namespace && snippet.namespace.id ? snippet.namespace : undefined
    );
    this.compute = ko.observable(
      snippet.compute && snippet.compute.id ? snippet.compute : undefined
    );

    this.availableDatabases = ko.observableArray();
    this.database = ko.observable();
    let previousDatabase = null;

    this.database.subscribe(newValue => {
      if (newValue !== null) {
        apiHelper.setInTotalStorage('editor', 'last.selected.database', newValue);
        if (previousDatabase !== null && previousDatabase !== newValue) {
          huePubSub.publish('editor.refresh.statement.locations', this);
        }
        previousDatabase = newValue;
      }
    });

    this.database(snippet.database);

    // History is currently in Notebook, same with saved queries by snippets, might be better in assist
    this.currentQueryTab = ko.observable(snippet.currentQueryTab || 'queryHistory');
    this.pinnedContextTabs = ko.observableArray(snippet.pinnedContextTabs || []);

    this.errorLoadingQueries = ko.observable(false);
    this.loadingQueries = ko.observable(false);

    this.queriesHasErrors = ko.observable(false);
    this.queriesCurrentPage = ko.observable(
      this.parentVm.selectedNotebook() && this.parentVm.selectedNotebook().snippets().length > 0
        ? this.parentVm
            .selectedNotebook()
            .snippets()[0]
            .queriesCurrentPage()
        : 1
    );
    this.queriesTotalPages = ko.observable(
      this.parentVm.selectedNotebook() && this.parentVm.selectedNotebook().snippets().length > 0
        ? this.parentVm
            .selectedNotebook()
            .snippets()[0]
            .queriesTotalPages()
        : 1
    );
    this.queries = ko.observableArray([]);

    this.queriesFilter = ko.observable('');
    this.queriesFilterVisible = ko.observable(false);
    this.queriesFilter.extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 900 } });
    this.queriesFilter.subscribe(() => {
      this.fetchQueries();
    });

    this.lastFetchQueriesRequest = null;

    this.lastQueriesPage = 1;
    this.currentQueryTab.subscribe(newValue => {
      huePubSub.publish('redraw.fixed.headers');
      huePubSub.publish('current.query.tab.switched', newValue);
      if (
        newValue === 'savedQueries' &&
        (this.queries().length === 0 || this.lastQueriesPage !== this.queriesCurrentPage())
      ) {
        this.fetchQueries();
      }
    });

    huePubSub.subscribeOnce(
      'assist.source.set',
      source => {
        if (source !== this.type()) {
          huePubSub.publish('assist.set.source', this.type());
        }
      },
      this.parentVm.huePubSubId
    );

    huePubSub.publish('assist.get.source');

    this.ignoreNextAssistDatabaseUpdate = false;

    if (!this.database()) {
      huePubSub.publish('assist.get.database.callback', {
        source: this.type(),
        callback: databaseDef => {
          this.handleAssistSelection(databaseDef);
        }
      });
    }

    this.statementType = ko.observable(snippet.statementType || 'text');
    this.statementTypes = ko.observableArray(['text', 'file']); // Maybe computed later for Spark
    if (!this.parentVm.editorMode()) {
      this.statementTypes.push('document');
    }
    this.statementPath = ko.observable(snippet.statementPath || '');
    this.externalStatementLoaded = ko.observable(false);

    this.statementPath.subscribe(() => {
      this.getExternalStatement();
    });

    this.associatedDocumentLoading = ko.observable(true);
    this.associatedDocument = ko.observable();
    this.associatedDocumentUuid = ko.observable(snippet.associatedDocumentUuid);
    this.associatedDocumentUuid.subscribe(val => {
      if (val !== '') {
        this.getExternalStatement();
      } else {
        this.statement_raw('');
        this.ace().setValue('', 1);
      }
    });
    this.statement_raw = ko.observable(snippet.statement_raw || '');
    this.selectedStatement = ko.observable('');
    this.positionStatement = ko.observable(null);
    this.lastExecutedStatement = ko.observable(null);
    this.statementsList = ko.observableArray();

    huePubSub.subscribe(
      'editor.active.statement.changed',
      statementDetails => {
        if (this.ace() && this.ace().container.id === statementDetails.id) {
          for (let i = statementDetails.precedingStatements.length - 1; i >= 0; i--) {
            if (statementDetails.precedingStatements[i].database) {
              this.availableDatabases().some(availableDatabase => {
                if (
                  availableDatabase.toLowerCase() ===
                  statementDetails.precedingStatements[i].database.toLowerCase()
                ) {
                  this.database(availableDatabase);
                  return true;
                }
              });
              break;
            }
          }
          if (statementDetails.activeStatement) {
            this.positionStatement(statementDetails.activeStatement);
          } else {
            this.positionStatement(null);
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
            this.statementsList(_statements); // Or fetch on demand via editor.refresh.statement.locations and remove observableArray?
          } else {
            this.statementsList([]);
          }
          if (!this.parentNotebook.isPresentationModeInitialized()) {
            if (this.parentNotebook.isPresentationModeDefault()) {
              // When switching to presentation mode, the snippet in non presentation mode cannot get status notification.
              // On initiailization, status is set to loading and does not get updated, because we moved to presentation mode.
              this.status(STATUS.ready);
            }
            // Changing to presentation mode requires statementsList to be initialized. statementsList is initialized asynchronously.
            // When presentation mode is default, we cannot change before statementsList has been calculated.
            // Cleaner implementation would be to make toggleEditorMode statementsList asynchronous
            // However this is currently impossible due to delete _notebook.presentationSnippets()[key];
            this.parentNotebook.isPresentationModeInitialized(true);
            this.parentNotebook.isPresentationMode(this.parentNotebook.isPresentationModeDefault());
          }
        }
      },
      this.parentVm.huePubSubId
    );

    this.aceSize = ko.observable(snippet.aceSize || 100);
    this.status = ko.observable(snippet.status || STATUS.loading);
    this.statusForButtons = ko.observable(STATUS_FOR_BUTTONS.executed);

    this.properties = ko.observable(
      komapping.fromJS(snippet.properties || getDefaultSnippetProperties(this.type()))
    );
    this.hasProperties = ko.pureComputed(
      () => Object.keys(komapping.toJS(this.properties())).length > 0
    );

    this.viewSettings = ko.pureComputed(() => this.parentVm.getSnippetViewSettings(this.type()));

    const previousProperties = {};
    this.type.subscribe(
      oldValue => {
        previousProperties[oldValue] = this.properties();
      },
      null,
      'beforeChange'
    );

    this.type.subscribe(newValue => {
      if (typeof previousProperties[newValue] !== 'undefined') {
        this.properties(previousProperties[newValue]);
      } else {
        this.properties(komapping.fromJS(getDefaultSnippetProperties(newValue)));
      }
      this.result.clear();
      window.setTimeout(() => {
        if (this.ace() !== null) {
          this.ace().focus();
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
    this.variables = komapping.fromJS(snippet.variables || []);
    this.variables.subscribe(() => {
      $(document).trigger('updateResultHeaders', this);
    });
    this.hasCurlyBracketParameters = ko.pureComputed(() => this.type() !== TYPE.pig);

    this.variableNames = ko.pureComputed(() => {
      let match,
        matches = {},
        matchList;
      if (this.type() === TYPE.pig) {
        matches = this.getPigParameters();
      } else {
        const re = /(?:^|\W)\${(\w*)=?([^{}]*)}/g;
        const reComment = /(^\s*--.*)|(\/\*[\s\S]*?\*\/)/gm;
        const reList = /(?!\s*$)\s*(?:(?:([^,|()\\]*)\(\s*([^,|()\\]*)\)(?:\\[\S\s][^,|()\\]*)?)|([^,|\\]*(?:\\[\S\s][^,|\\]*)*))\s*(?:,|\||$)/g;
        const statement = this.statement_raw();
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
    this.variableValues = {};
    this.variableNames.extend({ rateLimit: 150 });
    this.variableNames.subscribe(newVal => {
      const variablesLength = this.variables().length;
      const diffLengthVariables = variablesLength - newVal.length;
      const needsMore = diffLengthVariables < 0;
      const needsLess = diffLengthVariables > 0;
      this.variableValues = this.variables().reduce((variableValues, variable) => {
        if (!variableValues[variable.name()]) {
          variableValues[variable.name()] = { sampleUser: [] };
        }
        variableValues[variable.name()].value = variable.value();
        variableValues[variable.name()].sampleUser = variable.sampleUser();
        variableValues[variable.name()].catalogEntry = variable.catalogEntry;
        variableValues[variable.name()].path = variable.path();
        variableValues[variable.name()].type = variable.type();
        return variableValues;
      }, this.variableValues);
      if (needsMore) {
        for (let i = 0, length = Math.abs(diffLengthVariables); i < length; i++) {
          this.variables.push(
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
        this.variables.splice(this.variables().length - diffLengthVariables, diffLengthVariables);
      }
      newVal.forEach((item, index) => {
        const variable = this.variables()[index];
        variable.name(item.name);
        window.setTimeout(() => {
          variable.value(
            this.variableValues[item.name]
              ? this.variableValues[item.name].value
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
          this.variableValues[item.name] ? this.variableValues[item.name].sampleUser : []
        );
        variable.type(
          this.variableValues[item.name] ? this.variableValues[item.name].type || 'text' : 'text'
        );
        variable.path(
          this.variableValues[item.name] ? this.variableValues[item.name].path || '' : ''
        );
        variable.catalogEntry =
          this.variableValues[item.name] && this.variableValues[item.name].catalogEntry;
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
      const updateVariableType = (variable, sourceMeta) => {
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
      this.variables().forEach(variable => {
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
                  .then(updateVariableType.bind(this, variable))
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

    this.statement = ko.pureComputed(() => {
      let statement = this.isSqlDialect()
        ? this.selectedStatement()
          ? this.selectedStatement()
          : this.positionStatement() !== null
          ? this.positionStatement().statement
          : this.statement_raw()
        : this.statement_raw();
      const variables = this.variables().reduce((variables, variable) => {
        variables[variable.name()] = variable;
        return variables;
      }, {});
      if (this.variables().length) {
        const variablesString = this.variables()
          .map(variable => {
            return variable.name();
          })
          .join('|');
        statement = statement.replace(
          RegExp(
            '([^\\\\])?\\$' +
              (this.hasCurlyBracketParameters() ? '{(' : '(') +
              variablesString +
              ')(=[^}]*)?' +
              (this.hasCurlyBracketParameters() ? '}' : ''),
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

    this.result = new Result(snippet.result || {}, this);
    if (!this.result.hasSomeResults()) {
      this.currentQueryTab('queryHistory');
    }
    this.showGrid = ko.observable(snippet.showGrid !== false);
    this.showChart = ko.observable(!!snippet.showChart);
    if (!this.showGrid() && !this.showChart()) {
      this.showGrid(true);
    }
    let defaultShowLogs = true;
    if (this.parentVm.editorMode() && $.totalStorage('hue.editor.showLogs')) {
      defaultShowLogs = $.totalStorage('hue.editor.showLogs');
    }
    this.showLogs = ko.observable(snippet.showLogs || defaultShowLogs);
    this.progress = ko.observable(snippet.progress || 0);
    this.jobs = ko.observableArray(snippet.jobs || []);

    this.executeNextTimeout = -1;
    this.refreshTimeouts = {};

    this.progress.subscribe(val => {
      $(document).trigger('progress', { data: val, snippet: this });
    });

    this.showGrid.subscribe(val => {
      if (val) {
        this.showChart(false);
        huePubSub.publish('editor.grid.shown', this);
      }
    });

    this.showChart.subscribe(val => {
      if (val) {
        this.showGrid(false);
        this.isResultSettingsVisible(true);
        $(document).trigger('forceChartDraw', this);
        huePubSub.publish('editor.chart.shown', this);
        this.prepopulateChart();
      }
    });
    this.showLogs.subscribe(val => {
      huePubSub.publish('redraw.fixed.headers');
      if (val) {
        this.getLogs();
      }
      if (this.parentVm.editorMode()) {
        $.totalStorage('hue.editor.showLogs', val);
      }
    });

    this.isLoading = ko.pureComputed(() => this.status() === STATUS.loading);

    this.resultsKlass = ko.pureComputed(() => 'results ' + this.type());

    this.errorsKlass = ko.pureComputed(() => this.resultsKlass() + ' alert alert-error');

    this.is_redacted = ko.observable(!!snippet.is_redacted);

    this.chartType = ko.observable(snippet.chartType || window.HUE_CHARTS.TYPES.BARCHART);
    this.chartType.subscribe(this.prepopulateChart.bind(this));
    this.chartSorting = ko.observable(snippet.chartSorting || 'none');
    this.chartScatterGroup = ko.observable(snippet.chartScatterGroup);
    this.chartScatterSize = ko.observable(snippet.chartScatterSize);
    this.chartScope = ko.observable(snippet.chartScope || 'world');
    this.chartTimelineType = ko.observable(snippet.chartTimelineType || 'bar');
    this.chartLimits = ko.observableArray([5, 10, 25, 50, 100]); // To Delete
    this.chartLimit = ko.observable(snippet.chartLimit);
    this.chartLimit.extend({ notify: 'always' });
    this.chartX = ko.observable(snippet.chartX);
    this.chartX.extend({ notify: 'always' });
    this.chartXPivot = ko.observable(snippet.chartXPivot);
    this.chartXPivot.extend({ notify: 'always' });
    this.chartXPivot.subscribe(this.prepopulateChart.bind(this));
    this.chartYSingle = ko.observable(snippet.chartYSingle);
    this.chartYMulti = ko.observableArray(snippet.chartYMulti || []);
    this.chartData = ko.observableArray(snippet.chartData || []);
    this.chartMapType = ko.observable(snippet.chartMapType || 'marker');
    this.chartMapLabel = ko.observable(snippet.chartMapLabel);
    this.chartMapHeat = ko.observable(snippet.chartMapHeat);
    this.hideStacked = ko.pureComputed(() => this.chartYMulti().length <= 1); // To delete

    this.hasDataForChart = ko.pureComputed(() => { // To delete
      if (
        this.chartType() === window.HUE_CHARTS.TYPES.BARCHART ||
        this.chartType() === window.HUE_CHARTS.TYPES.LINECHART ||
        this.chartType() === window.HUE_CHARTS.TYPES.TIMELINECHART
      ) {
        return (
          typeof this.chartX() !== 'undefined' &&
          this.chartX() !== null &&
          this.chartYMulti().length > 0
        );
      }
      return (
        typeof this.chartX() !== 'undefined' &&
        this.chartX() !== null &&
        typeof this.chartYSingle() !== 'undefined' &&
        this.chartYSingle() !== null
      );
    });

    this.hasDataForChart.subscribe(() => { // To delete
      this.chartX.notifySubscribers();
      this.chartX.valueHasMutated();
    });

    this.chartType.subscribe(() => {
      $(document).trigger('forceChartDraw', this);
    });

    this.previousChartOptions = {};

    this.result.meta.subscribe(() => {
      this.chartLimit(this.previousChartOptions.chartLimit);
      this.chartX(this.guessMetaField(this.previousChartOptions.chartX));
      this.chartXPivot(this.previousChartOptions.chartXPivot);
      this.chartYSingle(this.guessMetaField(this.previousChartOptions.chartYSingle));
      this.chartMapType(this.previousChartOptions.chartMapType);
      this.chartMapLabel(this.guessMetaField(this.previousChartOptions.chartMapLabel));
      this.chartMapHeat(this.previousChartOptions.chartMapHeat);
      this.chartYMulti(this.guessMetaFields(this.previousChartOptions.chartYMulti) || []);
      this.chartSorting(this.previousChartOptions.chartSorting);
      this.chartScatterGroup(this.previousChartOptions.chartScatterGroup);
      this.chartScatterSize(this.previousChartOptions.chartScatterSize);
      this.chartScope(this.previousChartOptions.chartScope);
      this.chartTimelineType(this.previousChartOptions.chartTimelineType);
    });

    this.isResultSettingsVisible = ko.observable(!!snippet.isResultSettingsVisible);

    this.isResultSettingsVisible.subscribe(() => {
      $(document).trigger('toggleResultSettings', this);
    });

    this.settingsVisible = ko.observable(!!snippet.settingsVisible);
    this.saveResultsModalVisible = ko.observable(false);

    this.checkStatusTimeout = null;
    this.getLogsTimeout = null;

    this.complexity = ko.observable();
    this.hasComplexity = ko.pureComputed(
      () => this.complexity() && Object.keys(this.complexity()).length > 0
    );
    this.hasRisks = ko.pureComputed(
      () =>
        this.hasComplexity() && this.complexity()['hints'] && this.complexity()['hints'].length > 0
    );
    this.topRisk = ko.pureComputed(() =>
      this.hasRisks() ? this.complexity()['hints'][0] : undefined
    );

    this.suggestion = ko.observable('');
    this.hasSuggestion = ko.observable(null);

    this.compatibilityCheckRunning = ko.observable(false);

    this.compatibilitySourcePlatforms = [];
    Object.keys(COMPATIBILITY_SOURCE_PLATFORMS).forEach(key => {
      this.compatibilitySourcePlatforms.push(COMPATIBILITY_SOURCE_PLATFORMS[key]);
    });

    this.compatibilitySourcePlatform = ko.observable(COMPATIBILITY_SOURCE_PLATFORMS[this.type()]);
    this.compatibilitySourcePlatform.subscribe(newValue => {
      if (newValue && newValue.value !== this.type()) {
        this.hasSuggestion(null);
        this.compatibilityTargetPlatform(COMPATIBILITY_TARGET_PLATFORMS[this.type()]);
        this.queryCompatibility();
      }
    });

    this.compatibilityTargetPlatforms = [];
    Object.keys(COMPATIBILITY_TARGET_PLATFORMS).forEach(key => {
      this.compatibilityTargetPlatforms.push(COMPATIBILITY_TARGET_PLATFORMS[key]);
    });
    this.compatibilityTargetPlatform = ko.observable(COMPATIBILITY_TARGET_PLATFORMS[this.type()]);

    this.showOptimizer = ko.observable(
      apiHelper.getFromTotalStorage('editor', 'show.optimizer', false)
    );
    this.showOptimizer.subscribe(newValue => {
      if (newValue !== null) {
        apiHelper.setInTotalStorage('editor', 'show.optimizer', newValue);
      }
    });

    if (HAS_OPTIMIZER && !this.parentVm.isNotificationManager()) {
      let lastComplexityRequest;
      let lastCheckedComplexityStatement;
      const knownResponses = [];

      this.delayedStatement = ko
        .pureComputed(this.statement)
        .extend({ rateLimit: { method: 'notifyWhenChangesStop', timeout: 2000 } });

      const handleRiskResponse = data => {
        if (data.status === 0) {
          this.hasSuggestion('');
          this.complexity(data.query_complexity);
        } else {
          this.hasSuggestion('error');
          this.complexity({ hints: [] });
        }
        huePubSub.publish('editor.active.risks', {
          editor: this.ace(),
          risks: this.complexity() || {}
        });
        lastCheckedComplexityStatement = this.statement();
      };

      const clearActiveRisks = () => {
        if (this.hasSuggestion() !== null && typeof this.hasSuggestion() !== 'undefined') {
          this.hasSuggestion(null);
        }

        if (this.suggestion() !== '') {
          this.suggestion('');
        }

        if (this.complexity() !== {}) {
          this.complexity(undefined);
          huePubSub.publish('editor.active.risks', {
            editor: this.ace(),
            risks: {}
          });
        }
      };

      this.positionStatement.subscribe(newStatement => {
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

      this.checkComplexity = () => {
        if (!this.inFocus() || lastCheckedComplexityStatement === this.statement()) {
          return;
        }

        // The syntaxError property is only set if the syntax checker is active and has found an
        // error, see AceLocationHandler.
        if (this.positionStatement() && this.positionStatement().syntaxError) {
          return;
        }

        apiHelper.cancelActiveRequest(lastComplexityRequest);

        hueAnalytics.log('notebook', 'get_query_risk');
        clearActiveRisks();

        const changeSubscription = this.statement.subscribe(() => {
          changeSubscription.dispose();
          apiHelper.cancelActiveRequest(lastComplexityRequest);
        });

        const hash = this.statement().hashCode();

        const unknownResponse = knownResponses.every(knownResponse => {
          if (knownResponse.hash === hash) {
            handleRiskResponse(knownResponse.data);
            return false;
          }
          return true;
        });
        if (unknownResponse) {
          lastComplexityRequest = apiHelper
            .statementRisk({
              notebookJson: notebookToContextJSON(this.parentNotebook),
              snippetJson: snippetToContextJSON(this)
            })
            .then(data => {
              knownResponses.unshift({
                hash: hash,
                data: data
              });
              if (knownResponses.length > 50) {
                knownResponses.pop();
              }
              handleRiskResponse(data);
            })
            .always(() => {
              changeSubscription.dispose();
            });
        }
      };

      if (this.type() === TYPE.hive || this.type() === TYPE.impala) {
        if (this.statement_raw()) {
          window.setTimeout(() => {
            this.checkComplexity();
          }, 2000);
        }
        this.delayedStatement.subscribe(() => {
          this.checkComplexity();
        });
      }
    }

    this.wasBatchExecuted = ko.observable(!!snippet.wasBatchExecuted);
    this.isReady = ko.pureComputed(
      () =>
        (this.statementType() === 'text' &&
          ((this.isSqlDialect() && this.statement() !== '') ||
            ([TYPE.jar, TYPE.java, TYPE.spark2, TYPE.distcp].indexOf(this.type()) === -1 &&
              this.statement() !== '') ||
            ([TYPE.jar, TYPE.java].indexOf(this.type()) !== -1 &&
              (this.properties().app_jar() !== '' && this.properties().class() !== '')) ||
            (TYPE.spark2 === this.type() && this.properties().jars().length > 0) ||
            (TYPE.shell === this.type() && this.properties().command_path().length > 0) ||
            (TYPE.mapreduce === this.type() && this.properties().app_jar().length > 0) ||
            (TYPE.distcp === this.type() &&
              this.properties().source_path().length > 0 &&
              this.properties().destination_path().length > 0))) ||
        (this.statementType() === 'file' && this.statementPath().length > 0) ||
        (this.statementType() === 'document' &&
          this.associatedDocumentUuid() &&
          this.associatedDocumentUuid().length > 0)
    );
    this.lastExecuted = ko.observable(snippet.lastExecuted || 0);
    this.lastAceSelectionRowOffset = ko.observable(snippet.lastAceSelectionRowOffset || 0);

    this.executingBlockingOperation = null; // A ExecuteStatement()
    this.showLongOperationWarning = ko.observable(false);
    this.showLongOperationWarning.subscribe(newValue => {
      if (newValue) {
        hueAnalytics.convert('editor', 'showLongOperationWarning');
      }
    });

    this.longOperationTimeout = -1;

    this.lastExecutedStatements = undefined;
    this.lastExecutedSelectionRange = undefined;

    this.lastCompatibilityRequest = undefined;

    this.isFetchingData = false;

    this.isCanceling = ko.observable(false);

    this.autocompleter = new AceAutocompleteWrapper({
      snippet: this,
      user: this.parentVm.user,
      optEnabled: false,
      timeout: this.parentVm.autocompleteTimeout
    });

    huePubSub.subscribe('hue.executor.updated', details => {
      const executable = details.executable;

      if (details.executor === this.executor()) {
        this.status(executable.status);
        this.progress(executable.progress);
      }
    });

    this.refreshHistory = notebook.fetchHistory;
  }

  ace(newVal) {
    if (newVal) {
      this.aceEditor = newVal;
      if (!this.parentNotebook.isPresentationMode()) {
        this.aceEditor.focus();
      }
    }
    return this.aceEditor;
  }

  cancel() {
    window.clearTimeout(this.executeNextTimeout);
    this.isCanceling(true);
    if (this.checkStatusTimeout != null) {
      clearTimeout(this.checkStatusTimeout);
      this.checkStatusTimeout = null;
      clearTimeout(this.getLogsTimeout);
      this.getLogsTimeout = null;
    }
    hueAnalytics.log('notebook', 'cancel');

    if (this.executingBlockingOperation != null) {
      this.executingBlockingOperation.abort();
      this.executingBlockingOperation = null;
    }

    if ($.isEmptyObject(this.result.handle())) {
      // Query was not even submitted yet
      this.statusForButtons(STATUS_FOR_BUTTONS.canceled);
      this.status(STATUS.failed);
      this.isCanceling(false);
      this.parentNotebook.isExecutingAll(false);
    } else {
      this.statusForButtons(STATUS_FOR_BUTTONS.canceling);
      apiHelper
        .cancelNotebookStatement({
          notebookJson: notebookToContextJSON(this.parentNotebook),
          snippetJson: snippetToContextJSON(this)
        })
        .then(data => {
          this.statusForButtons(STATUS_FOR_BUTTONS.canceled);
          if (data.status === 0) {
            this.status(STATUS.canceled);
            this.parentNotebook.isExecutingAll(false);
          } else {
            this.handleAjaxError(data);
          }
        })
        .fail(xhr => {
          if (xhr.status !== 502) {
            $(document).trigger('error', xhr.responseText);
          }
          this.statusForButtons(STATUS_FOR_BUTTONS.canceled);
          this.status(STATUS.failed);
          this.parentNotebook.isExecutingAll(false);
        })
        .always(() => {
          this.isCanceling(false);
        });
    }
  }

  checkCompatibility() {
    this.hasSuggestion(null);
    this.compatibilitySourcePlatform(COMPATIBILITY_SOURCE_PLATFORMS[this.type()]);
    this.compatibilityTargetPlatform(
      COMPATIBILITY_TARGET_PLATFORMS[this.type() === TYPE.hive ? TYPE.impala : TYPE.hive]
    );
    this.queryCompatibility();
  }

  checkDdlNotification() {
    if (
      this.lastExecutedStatement() &&
      /ALTER|CREATE|DELETE|DROP|GRANT|INSERT|INVALIDATE|LOAD|SET|TRUNCATE|UPDATE|UPSERT|USE/i.test(
        this.lastExecutedStatement().firstToken
      )
    ) {
      this.onDdlExecute();
    } else {
      window.clearTimeout(this.executeNextTimeout);
    }
  }

  checkStatus() {
    const _checkStatus = () => {
      $.post('/notebook/api/check_status', {
        notebook: notebookToContextJSON(this.parentNotebook),
        snippet: snippetToContextJSON(this)
      })
        .then(data => {
          if (
            this.statusForButtons() === STATUS_FOR_BUTTONS.canceling ||
            this.status() === STATUS.canceled
          ) {
            // Query was canceled in the meantime, do nothing
          } else {
            this.result.endTime(new Date());

            if (data.status === 0) {
              this.status(data.query_status.status);

              if (
                this.status() === STATUS.running ||
                this.status() === STATUS.starting ||
                this.status() === STATUS.waiting
              ) {
                const delay = this.result.executionTime() > 45000 ? 5000 : 1000; // 5s if more than 45s
                if (!this.parentNotebook.unloaded()) {
                  this.checkStatusTimeout = setTimeout(_checkStatus, delay);
                }
              } else if (this.status() === STATUS.available) {
                this.fetchResult(100);
                this.progress(100);
                if (this.isSqlDialect()) {
                  if (this.result.handle().has_result_set) {
                    const _query_id = this.parentNotebook.id();
                    setTimeout(() => {
                      // Delay until we get IMPALA-5555
                      this.fetchResultSize(10, _query_id);
                    }, 2000);
                    this.checkDdlNotification(); // DDL CTAS with Impala
                  } else if (this.lastExecutedStatement()) {
                    this.checkDdlNotification();
                  } else {
                    this.onDdlExecute();
                  }
                }
                if (this.parentNotebook.isExecutingAll()) {
                  this.parentNotebook.executingAllIndex(
                    this.parentNotebook.executingAllIndex() + 1
                  );
                  if (
                    this.parentNotebook.executingAllIndex() < this.parentNotebook.snippets().length
                  ) {
                    this.parentNotebook
                      .snippets()
                      [this.parentNotebook.executingAllIndex()].execute();
                  } else {
                    this.parentNotebook.isExecutingAll(false);
                  }
                }
                if (!this.result.handle().has_more_statements && this.parentVm.successUrl()) {
                  huePubSub.publish('open.link', this.parentVm.successUrl()); // Not used anymore in Hue 4
                }
              } else if (this.status() === STATUS.success) {
                this.progress(99);
              }
            } else if (data.status === -3) {
              this.status(STATUS.expired);
              this.parentNotebook.isExecutingAll(false);
            } else {
              this.handleAjaxError(data);
              this.parentNotebook.isExecutingAll(false);
            }
          }
        })
        .fail((xhr, textStatus) => {
          if (xhr.status !== 502) {
            $(document).trigger('error', xhr.responseText || textStatus);
          }
          this.status(STATUS.failed);
          this.parentNotebook.isExecutingAll(false);
        });
    };
    const activeStatus = ['running', 'starting', 'waiting'];
    const _getLogs = isLastTime => {
      this.getLogs().then(() => {
        const lastTime = activeStatus.indexOf(this.status()) < 0; // We to run getLogs at least one time after status is terminated to make sure we have last logs
        if (lastTime && isLastTime) {
          return;
        }
        const delay = this.result.executionTime() > 45000 ? 5000 : 1000; // 5s if more than 45s
        this.getLogsTimeout = setTimeout(_getLogs.bind(this, lastTime), delay);
      });
    };
    _checkStatus();
    _getLogs(activeStatus.indexOf(this.status()) < 0);
  }

  close() {
    if (this.checkStatusTimeout != null) {
      clearTimeout(this.checkStatusTimeout);
      this.checkStatusTimeout = null;
      clearTimeout(this.getLogsTimeout);
      this.getLogsTimeout = null;
    }

    $.post('/notebook/api/close_statement', {
      notebook: notebookToContextJSON(this.parentNotebook),
      snippet: snippetToContextJSON(this)
    });
  }

  async execute(automaticallyTriggered) {
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

    if (this.executor() && this.executor().isRunning()) {
      this.executor().cancel();
    }

    this.executor(
      new Executor({
        compute: this.compute(),
        database: this.database(),
        sourceType: this.type(),
        namespace: this.namespace(),
        statement: this.statement(),
        isSqlEngine: this.isSqlDialect()
      })
    );

    try {
      const result = await this.executor().executeNext();

      this.stopLongOperationTimeout();
      this.result.clear();

      await this.result.update(result);

      if (this.result.data().length) {
        this.currentQueryTab('queryResults');
      }
    } catch (error) {
      this.stopLongOperationTimeout();
    }
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

  fetchExecutionAnalysis() {
    if (this.type() === TYPE.impala) {
      // TODO: Use real query ID
      huePubSub.publish('editor.update.execution.analysis', {
        analysisPossible: true,
        compute: this.compute(),
        queryId: this.parentNotebook.id(),
        name: this.jobs()[0] && this.jobs()[0].name
      });
    } else {
      huePubSub.publish('editor.update.execution.analysis', {
        analysisPossible: false
      });
    }
  }

  fetchQueries() {
    apiHelper.cancelActiveRequest(this.lastFetchQueriesRequest);

    const QUERIES_PER_PAGE = 50;
    this.lastQueriesPage = this.queriesCurrentPage();
    this.loadingQueries(true);
    this.queriesHasErrors(false);
    this.lastFetchQueriesRequest = apiHelper.searchDocuments({
      successCallback: result => {
        this.queriesTotalPages(Math.ceil(result.count / QUERIES_PER_PAGE));
        this.queries(komapping.fromJS(result.documents)());
        this.loadingQueries(false);
        this.queriesHasErrors(false);
      },
      errorCallback: () => {
        this.loadingQueries(false);
        this.queriesHasErrors(true);
      },
      page: this.queriesCurrentPage(),
      limit: QUERIES_PER_PAGE,
      type: 'query-' + this.type(),
      query: this.queriesFilter(),
      include_trashed: false
    });
  }

  // TODO: Switch to result.fetchMoreRows in ko mako
  fetchResult(rows, startOver) {
    this.result.fetchMoreRows(rows, startOver);
  }

  // fetchResultData(rows, startOver) {
  //   console.log('fetchResultData');
  //   if (!this.isFetchingData) {
  //     if (this.status() === STATUS.available) {
  //       this.startLongOperationTimeout();
  //       this.isFetchingData = true;
  //       hueAnalytics.log('notebook', 'fetchResult/' + rows + '/' + startOver);
  //       $.post(
  //         '/notebook/api/fetch_result_data',
  //         {
  //           notebook: notebookContextToJSON(this.parentNotebook),
  //           snippet: snippetContextToJSON(this),
  //           rows: rows,
  //           startOver: startOver
  //         },
  //         data => {
  //           this.stopLongOperationTimeout();
  //           data = JSON.bigdataParse(data);
  //           if (data.status === 0) {
  //             this.showExecutionAnalysis(true);
  //             this.loadData(data.result, rows);
  //           } else {
  //             this.handleAjaxError(data, () => {
  //               this.isFetchingData = false;
  //               this.fetchResultData(rows, startOver);
  //             });
  //             $(document).trigger('renderDataError', { snippet: this });
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
  //           this.isFetchingData = false;
  //         });
  //     } else {
  //       huePubSub.publish('editor.snippet.result.normal', this);
  //     }
  //   }
  // }

  fetchResultMetadata() {
    $.post('/notebook/api/fetch_result_metadata', {
      notebook: notebookToContextJSON(this.parentNotebook),
      snippet: snippetToContextJSON(this)
    })
      .then(data => {
        if (data.status === 0) {
          this.result.meta(data.result.meta);
        } else {
          $(document).trigger('error', data.message);
        }
      })
      .fail(xhr => {
        if (xhr.status !== 502) {
          $(document).trigger('error', xhr.responseText);
        }
        this.status(STATUS.failed);
      });
  }

  fetchResultSize(n, query_id) {
    apiHelper
      .fetchResultSize({
        notebookJson: notebookToContextJSON(this.parentNotebook),
        snippetJson: snippetToContextJSON(this)
      })
      .then(data => {
        if (query_id === this.parentNotebook.id()) {
          // If still on the same result
          if (data.status === 0) {
            if (data.result.rows != null) {
              this.result.rows(data.result.rows);
            } else if (this.type() === TYPE.impala && n > 0) {
              setTimeout(() => {
                this.fetchResultSize(n - 1, query_id);
              }, 1000);
            }
          } else if (data.status === 5) {
            // No supported yet for this snippet
          } else {
            //$(document).trigger("error", data.message);
          }
        }
      });
  }

  getExternalStatement() {
    this.externalStatementLoaded(false);
    apiHelper
      .getExternalStatement({
        notebookJson: notebookToContextJSON(this.parentNotebook),
        snippetJson: snippetToContextJSON(this)
      })
      .then(data => {
        if (data.status === 0) {
          this.externalStatementLoaded(true);
          this.statement_raw(data.statement);
          this.ace().setValue(this.statement_raw(), 1);
        } else {
          this.handleAjaxError(data);
        }
      });
  }

  getLogs() {
    apiHelper
      .getLogs({
        notebookJson: notebookToContextJSON(this.parentNotebook),
        snippetJson: snippetToContextJSON(this),
        from: this.result.logLines,
        jobsJson: komapping.toJSON(this.jobs, { ignore: ['percentJob'] }),
        fullLog: this.result.logs
      })
      .then(data => {
        if (data.status === 1) {
          // Append errors to the logs
          data.status = 0;
          data.logs = data.message;
        }
        if (data.status === 0) {
          if (data.logs.length > 0) {
            const logs = data.logs.split('\n');
            this.result.logLines += logs.length;
            const oldLogs = this.result.logs();
            if (
              data.logs &&
              (oldLogs === '' ||
                (this.wasBatchExecuted() && data.logs.indexOf('Unable to locate') === -1) ||
                data.isFullLogs)
            ) {
              this.result.logs(data.logs);
            } else {
              this.result.logs(oldLogs + '\n' + data.logs);
            }
          }

          this.jobs().forEach(job => {
            if (typeof job.percentJob === 'undefined') {
              job.percentJob = ko.observable(-1);
            }
          });

          if (data.jobs && data.jobs.length > 0) {
            data.jobs.forEach(job => {
              const _found = ko.utils.arrayFilter(this.jobs(), item => {
                return item.name === job.name;
              });
              if (_found.length === 0) {
                if (typeof job.percentJob === 'undefined') {
                  job.percentJob = ko.observable(-1);
                } else {
                  job.percentJob = ko.observable(job.percentJob);
                }
                this.jobs.push(job);
              } else if (typeof job.percentJob !== 'undefined') {
                for (let i = 0; i < _found.length; i++) {
                  _found[i].percentJob(job.percentJob);
                }
              }
            });
            this.jobs().forEach(job => {
              const _found = ko.utils.arrayFilter(this.jobs(), item => {
                return item.name === job.name;
              });
              if (_found.length === 0) {
                this.jobs.remove(job);
              }
            });
          }
          if (this.status() === STATUS.running) {
            // Maybe the query finished or failed in the meantime
            this.progress(data.progress);
          }
        } else {
          this.handleAjaxError(data);
        }
      })
      .fail((xhr, textStatus) => {
        if (xhr.status !== 502) {
          $(document).trigger('error', xhr.responseText || textStatus);
        }
        this.status(STATUS.failed);
      });
  }

  getPigParameters() {
    const params = {};
    const variables = this.statement_raw().match(/([^\\]|^)\$[^\d'"](\w*)/g);
    const declares = this.statement_raw().match(/%declare +([^ ])+/gi);
    const defaults = this.statement_raw().match(/%default +([^;])+/gi);
    const macro_defines = this.statement_raw().match(/define [^ ]+ *\(([^)]*)\)/gi); // no multiline
    const macro_returns = this.statement_raw().match(/returns +([^{]*)/gi); // no multiline

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
    return this.parentVm.getSnippetViewSettings(this.type()).placeHolder;
  }

  getSimilarQueries() {
    hueAnalytics.log('notebook', 'get_query_similarity');

    apiHelper
      .statementSimilarity({
        notebookJson: notebookToContextJSON(this.parentNotebook),
        snippetJson: snippetToContextJSON(this),
        sourcePlatform: this.type()
      })
      .then(data => {
        if (data.status === 0) {
          // eslint-disable-next-line no-restricted-syntax
          console.log(data.statement_similarity);
        } else {
          $(document).trigger('error', data.message);
        }
      });
  }

  guessMetaField(field) {
    let _fld = null;
    if (field) {
      if (this.result.cleanedMeta().length > 0) {
        this.result.cleanedMeta().forEach(fld => {
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
    const _fields = [];
    if (fields) {
      fields.forEach(fld => {
        const _field = this.guessMetaField(fld);
        if (_field) {
          _fields.push(_field);
        }
      });
    }
    return _fields;
  }

  handleAjaxError(data, callback) {
    if (data.status === -2) {
      // TODO: Session expired, check if handleAjaxError is used for ENABLE_NOTEBOOK_2
    } else if (data.status === -3) {
      // Statement expired
      this.status(STATUS.expired);
      if (data.message) {
        this.errors.push({ message: data.message, help: null, line: null, col: null });
        huePubSub.publish('editor.snippet.result.normal', this);
      }
    } else if (data.status === -4) {
      // Operation timed out
      this.parentNotebook.retryModalCancel = () => {
        this.status(STATUS.failed);
        huePubSub.publish('hide.retry.modal');
      };
      this.parentNotebook.retryModalConfirm = () => {
        if (callback) {
          callback();
        }
        huePubSub.publish('hide.retry.modal');
      };
      huePubSub.publish('show.retry.modal');
    } else if (data.status === 401) {
      // Auth required
      this.status(STATUS.expired);
      $(document).trigger('showAuthModal', {
        type: this.type(),
        callback: this.execute,
        message: data.message
      });
    } else if (data.status === 1 || data.status === -1) {
      this.status(STATUS.failed);
      const match = ERROR_REGEX.exec(data.message);
      if (match) {
        let errorLine = parseInt(match[1]);
        let errorCol;
        if (typeof match[3] !== 'undefined') {
          errorCol = parseInt(match[3]);
        }
        if (this.positionStatement()) {
          if (errorCol && errorLine === 1) {
            errorCol += this.positionStatement().location.first_column;
          }
          errorLine += this.positionStatement().location.first_line - 1;
        }

        this.errors.push({
          message: data.message.replace(
            match[0],
            'line ' + errorLine + (errorCol !== null ? ':' + errorCol : '')
          ),
          help: null,
          line: errorLine - 1,
          col: errorCol
        });
      } else {
        this.errors.push({
          message: data.message,
          help: data.help,
          line: null,
          col: null
        });
      }
    } else {
      $(document).trigger('error', data.message);
      this.status(STATUS.failed);
    }
  }

  handleAssistSelection(databaseDef) {
    if (this.ignoreNextAssistDatabaseUpdate) {
      this.ignoreNextAssistDatabaseUpdate = false;
    } else if (databaseDef.sourceType === this.type()) {
      if (this.namespace() !== databaseDef.namespace) {
        this.namespace(databaseDef.namespace);
      }
      if (this.database() !== databaseDef.name) {
        this.database(databaseDef.name);
      }
    }
  }

  init() {
    if (
      (this.status() === STATUS.running || this.status() === STATUS.available) &&
      this.parentNotebook.isHistory()
    ) {
      this.checkStatus();
    } else if (this.status() === STATUS.loading) {
      this.status(STATUS.failed);
      this.progress(0);
      this.jobs([]);
    } else if (this.status() === STATUS.readyExecute) {
      this.execute();
    }
  }

  // loadData(result, rows) {
  //   rows -= result.data.length;
  //
  //   if (result.data.length > 0) {
  //     this.currentQueryTab('queryResults');
  //   }
  //
  //   if (result.has_more && rows > 0) {
  //     setTimeout(() => {
  //       this.fetchResultData(rows, false);
  //     }, 500);
  //   } else if (
  //     !this.parentVm.editorMode() &&
  //     !this.parentNotebook.isPresentationMode() &&
  //     this.parentNotebook.snippets()[this.parentNotebook.snippets().length - 1] === this
  //   ) {
  //     this.parentNotebook.newSnippet();
  //   }
  // }

  nextQueriesPage() {
    if (this.queriesCurrentPage() !== this.queriesTotalPages()) {
      this.queriesCurrentPage(this.queriesCurrentPage() + 1);
      this.fetchQueries();
    }
  }

  onDdlExecute() {
    if (this.result.handle() && this.result.handle().has_more_statements) {
      window.clearTimeout(this.executeNextTimeout);
      this.executeNextTimeout = setTimeout(() => {
        this.execute(true); // Execute next, need to wait as we disabled fast click
      }, 1000);
    }
    if (
      this.lastExecutedStatement() &&
      /CREATE|DROP/i.test(this.lastExecutedStatement().firstToken)
    ) {
      let match = this.statement().match(
        /(?:CREATE|DROP)\s+TABLE\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?:`([^`]+)`|([^;\s]+))\..*/i
      );
      const path = [];
      if (match) {
        path.push(match[1] || match[2]); // group 1 backticked db name, group 2 regular db name
      } else {
        match = this.statement().match(
          /(?:CREATE|DROP)\s+(?:DATABASE|SCHEMA)\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?:`([^`]+)`|([^;\s]+))/i
        );
        if (match) {
          path.push(match[1] || match[2]); // group 1 backticked db name, group 2 regular db name
        } else if (this.database()) {
          path.push(this.database());
        }
      }

      if (path.length) {
        window.clearTimeout(this.refreshTimeouts[path.join('.')]);
        this.refreshTimeouts[path.join('.')] = window.setTimeout(() => {
          this.ignoreNextAssistDatabaseUpdate = true;
          dataCatalog
            .getEntry({
              sourceType: this.type(),
              namespace: this.namespace(),
              compute: this.compute(),
              path: path
            })
            .done(entry => {
              entry.clearCache({ refreshCache: true, cascade: true, silenceErrors: true });
            });
        }, 5000);
      }
    }
  }

  onKeydownInVariable(context, e) {
    if ((e.ctrlKey || e.metaKey) && e.which === 13) {
      // Ctrl-enter
      this.ace().commands.commands['execute'].exec();
    } else if ((e.ctrlKey || e.metaKey) && e.which === 83) {
      // Ctrl-s
      this.ace().commands.commands['save'].exec();
      e.preventDefault(); // Prevent browser page save dialog
    }
    return true;
  }

  prepopulateChart() {
    const type = this.chartType();
    hueAnalytics.log('notebook', 'chart/' + type);

    if (type === window.HUE_CHARTS.TYPES.MAP && this.result.cleanedNumericMeta().length >= 2) {
      if (this.chartX() === null || typeof this.chartX() === 'undefined') {
        let name = this.result.cleanedNumericMeta()[0].name;
        this.result.cleanedNumericMeta().forEach(fld => {
          if (
            fld.name.toLowerCase().indexOf('lat') > -1 ||
            fld.name.toLowerCase().indexOf('ltd') > -1
          ) {
            name = fld.name;
          }
        });
        this.chartX(name);
      }
      if (this.chartYSingle() === null || typeof this.chartYSingle() === 'undefined') {
        let name = this.result.cleanedNumericMeta()[1].name;
        this.result.cleanedNumericMeta().forEach(fld => {
          if (
            fld.name.toLowerCase().indexOf('lon') > -1 ||
            fld.name.toLowerCase().indexOf('lng') > -1
          ) {
            name = fld.name;
          }
        });
        this.chartYSingle(name);
      }
      return;
    }

    if (
      (this.chartX() === null || typeof this.chartX() === 'undefined') &&
      (type === window.HUE_CHARTS.TYPES.BARCHART ||
        type === window.HUE_CHARTS.TYPES.PIECHART ||
        type === window.HUE_CHARTS.TYPES.GRADIENTMAP) &&
      this.result.cleanedStringMeta().length >= 1
    ) {
      this.chartX(this.result.cleanedStringMeta()[0].name);
    }

    if (this.result.cleanedNumericMeta().length > 0) {
      if (
        this.chartYMulti().length === 0 &&
        (type === window.HUE_CHARTS.TYPES.BARCHART || type === window.HUE_CHARTS.TYPES.LINECHART)
      ) {
        this.chartYMulti.push(
          this.result.cleanedNumericMeta()[Math.min(this.result.cleanedNumericMeta().length - 1, 1)]
            .name
        );
      } else if (
        (this.chartYSingle() === null || typeof this.chartYSingle() === 'undefined') &&
        (type === window.HUE_CHARTS.TYPES.PIECHART ||
          type === window.HUE_CHARTS.TYPES.MAP ||
          type === window.HUE_CHARTS.TYPES.GRADIENTMAP ||
          type === window.HUE_CHARTS.TYPES.SCATTERCHART ||
          (type === window.HUE_CHARTS.TYPES.BARCHART && this.chartXPivot() !== null))
      ) {
        if (this.chartYMulti().length === 0) {
          this.chartYSingle(
            this.result.cleanedNumericMeta()[
              Math.min(this.result.cleanedNumericMeta().length - 1, 1)
            ].name
          );
        } else {
          this.chartYSingle(this.chartYMulti()[0]);
        }
      }
    }
  }

  prevQueriesPage() {
    if (this.queriesCurrentPage() !== 1) {
      this.queriesCurrentPage(this.queriesCurrentPage() - 1);
      this.fetchQueries();
    }
  }

  queryCompatibility(targetPlatform) {
    apiHelper.cancelActiveRequest(this.lastCompatibilityRequest);

    hueAnalytics.log('notebook', 'compatibility');
    this.compatibilityCheckRunning(targetPlatform !== this.type());
    this.hasSuggestion(null);
    const positionStatement = this.positionStatement();

    this.lastCompatibilityRequest = apiHelper
      .statementCompatibility({
        notebookJson: notebookToContextJSON(this.parentNotebook),
        snippetJson: snippetToContextJSON(this),
        sourcePlatform: this.compatibilitySourcePlatform().value,
        targetPlatform: this.compatibilityTargetPlatform().value
      })
      .then(data => {
        if (data.status === 0) {
          this.aceErrorsHolder([]);
          this.aceWarningsHolder([]);
          this.suggestion(komapping.fromJS(data.query_compatibility));
          if (this.suggestion().queryError && this.suggestion().queryError.errorString()) {
            const match = ERROR_REGEX.exec(this.suggestion().queryError.errorString());
            let line = null;
            if (match) {
              if (positionStatement) {
                line = positionStatement.location.first_line + parseInt(match[1]) + 1;
              } else {
                line = parseInt(match[1]) - 1;
              }
            }
            this.aceWarningsHolder.push({
              message: this.suggestion().queryError.errorString(),
              line: line,
              col:
                match === null ? null : typeof match[3] !== 'undefined' ? parseInt(match[3]) : null
            });
            this.status(STATUS.withOptimizerReport);
          }
          if (this.suggestion().parseError()) {
            const match = ERROR_REGEX.exec(this.suggestion().parseError());
            this.aceErrorsHolder.push({
              message: this.suggestion().parseError(),
              line: match === null ? null : parseInt(match[1]) - 1,
              col:
                match === null ? null : typeof match[3] !== 'undefined' ? parseInt(match[3]) : null
            });
            this.status(STATUS.withOptimizerReport);
          }
          this.showOptimizer(true);
          this.hasSuggestion(true);
        } else {
          $(document).trigger('error', data.message);
        }
      })
      .fail(xhr => {
        if (xhr.status !== 502) {
          $(document).trigger('error', xhr.responseText);
        }
      })
      .always(() => {
        this.compatibilityCheckRunning(false);
      });
  }

  reexecute() {
    this.result.cancelBatchExecution();
    this.execute();
  }

  removeContextTab(context) {
    if (context.tabId === this.currentQueryTab()) {
      this.currentQueryTab('queryHistory');
    }
    this.pinnedContextTabs.remove(context);
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
    this.longOperationTimeout = window.setTimeout(() => {
      this.showLongOperationWarning(true);
    }, 2000);
  }

  stopLongOperationTimeout() {
    window.clearTimeout(this.longOperationTimeout);
    this.showLongOperationWarning(false);
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
    this.isResultSettingsVisible(!this.isResultSettingsVisible());
  }

  uploadQuery(query_id) {
    $.post('/metadata/api/optimizer/upload/query', {
      query_id: query_id,
      sourcePlatform: this.type()
    });
  }

  uploadQueryHistory(n) {
    hueAnalytics.log('notebook', 'upload_query_history');

    $.post('/metadata/api/optimizer/upload/history', {
      n: typeof n != 'undefined' ? n : null,
      sourcePlatform: this.type()
    }).then(data => {
      if (data.status === 0) {
        $(document).trigger(
          'info',
          data.upload_history[this.type()].count +
            ' queries uploaded successfully. Processing them...'
        );
        this.watchUploadStatus(data.upload_history[this.type()].status.workloadId);
      } else {
        $(document).trigger('error', data.message);
      }
    });
  }

  uploadTableStats(options) {
    hueAnalytics.log('notebook', 'load_table_stats');
    if (options.showProgress) {
      $(document).trigger('info', 'Preparing table data...');
    }

    $.post(
      '/metadata/api/optimizer/upload/table_stats',
      {
        db_tables: JSON.stringify(
          options.activeTables.map(table => table.databaseName + '.' + table.tableName)
        ),
        sourcePlatform: JSON.stringify(this.type()),
        with_ddl: JSON.stringify(true),
        with_table_stats: JSON.stringify(true),
        with_columns_stats: JSON.stringify(true)
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
            this.watchUploadStatus(data.upload_table_ddl.status.workloadId, options.showProgress);
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
    $.post('/metadata/api/optimizer/upload/status', {
      workloadId: workloadId
    }).then(data => {
      if (data.status === 0) {
        if (showProgress) {
          $(document).trigger('info', 'Query processing: ' + data.upload_status.status.state);
        }
        if (['WAITING', 'IN_PROGRESS'].indexOf(data.upload_status.status.state) !== -1) {
          window.setTimeout(() => {
            this.watchUploadStatus(workloadId);
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
    });
  }

  whenContextSet() {
    let namespaceSub;
    const namespaceDeferred = $.Deferred();
    if (this.namespace()) {
      namespaceDeferred.resolve(this.namespace());
    } else {
      namespaceSub = this.namespace.subscribe(newVal => {
        if (newVal) {
          namespaceDeferred.resolve(newVal);
          namespaceSub.dispose();
        }
      });
    }
    let computeSub;
    const computeDeferred = $.Deferred();
    if (this.compute()) {
      computeDeferred.resolve(this.compute());
    } else {
      computeSub = this.compute.subscribe(newVal => {
        if (newVal) {
          computeDeferred.resolve(newVal);
          computeSub.dispose();
        }
      });
    }

    const result = $.when(namespaceDeferred, computeDeferred);

    result.dispose = () => {
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
