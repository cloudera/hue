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

import 'apps/notebook2/components/ko.executableActions';
import 'apps/notebook2/components/ko.executableLogs';
import 'apps/notebook2/components/ko.executableProgressBar';
import 'apps/notebook2/components/ko.snippetEditorActions';
import 'apps/notebook2/components/ko.savedQueries';
import 'apps/notebook2/components/ko.snippetResults';
import 'apps/notebook2/components/ko.queryHistory';

import AceAutocompleteWrapper from 'apps/notebook/aceAutocompleteWrapper';
import apiHelper from 'api/apiHelper';
import Executor from 'apps/notebook2/execution/executor';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import sessionManager from 'apps/notebook2/execution/sessionManager';
import SqlExecutable from 'apps/notebook2/execution/sqlExecutable';
import { REDRAW_FIXED_HEADERS_EVENT } from 'apps/notebook2/events';
import { EXECUTABLE_UPDATED_EVENT, EXECUTION_STATUS } from 'apps/notebook2/execution/executable';
import {
  ACTIVE_STATEMENT_CHANGED_EVENT,
  REFRESH_STATEMENT_LOCATIONS_EVENT
} from 'ko/bindings/ace/aceLocationHandler';
import { EXECUTE_ACTIVE_EXECUTABLE_EVENT } from 'apps/notebook2/components/ko.executableActions';
import { UPDATE_HISTORY_EVENT } from 'apps/notebook2/components/ko.queryHistory';

// TODO: Remove for ENABLE_NOTEBOOK_2. Temporary here for debug
window.SqlExecutable = SqlExecutable;
window.Executor = Executor;

export const CURRENT_QUERY_TAB_SWITCHED_EVENT = 'current.query.tab.switched';

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
  constructor(vm, notebook, snippetRaw) {
    this.parentVm = vm;
    this.parentNotebook = notebook;

    this.id = ko.observable(snippetRaw.id || hueUtils.UUID());
    this.name = ko.observable(snippetRaw.name || '');
    this.type = ko.observable();
    this.type.subscribe(newValue => {
      // TODO: Add session disposal for ENABLE_NOTEBOOK_2
      // Pre-create a session to speed up execution
      sessionManager.getSession({ type: newValue }).then(() => {
        this.status(STATUS.ready);
      });
    });
    this.type(snippetRaw.type || TYPE.hive);
    this.isBatchable = ko.pureComputed(
      () =>
        this.type() === this.hive ||
        this.type() === this.impala ||
        this.parentVm.availableLanguages.some(
          language =>
            language.type === this.type() &&
            (language.interface == 'oozie' || language.interface == 'sqlalchemy')
        )
    );

    this.autocompleteSettings = {
      temporaryOnly: false
    };

    // Ace stuff
    this.aceCursorPosition = ko.observable(
      this.parentNotebook.isHistory() ? snippetRaw.aceCursorPosition : null
    );

    this.aceEditor = null;

    this.errors = ko.observableArray([]);

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

    this.explanation = ko.observable();

    this.getAceMode = () => this.parentVm.getSnippetViewSettings(this.type()).aceMode;

    this.dbSelectionVisible = ko.observable(false);

    this.showExecutionAnalysis = ko.observable(false);

    this.isSqlDialect = ko.pureComputed(
      () => this.parentVm.getSnippetViewSettings(this.type()).sqlDialect
    );

    // namespace and compute might be initialized as empty object {}
    this.namespace = ko.observable(
      snippetRaw.namespace && snippetRaw.namespace.id ? snippetRaw.namespace : undefined
    );
    this.compute = ko.observable(
      snippetRaw.compute && snippetRaw.compute.id ? snippetRaw.compute : undefined
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

    this.database(snippetRaw.database);

    // History is currently in Notebook, same with saved queries by snippets, might be better in assist
    this.currentQueryTab = ko.observable(snippetRaw.currentQueryTab || 'queryHistory');
    this.pinnedContextTabs = ko.observableArray(snippetRaw.pinnedContextTabs || []);

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

    this.statementType = ko.observable(snippetRaw.statementType || 'text');
    this.statementTypes = ko.observableArray(['text', 'file']); // Maybe computed later for Spark
    if (!this.parentVm.editorMode()) {
      this.statementTypes.push('document');
    }
    this.statementPath = ko.observable(snippetRaw.statementPath || '');
    this.externalStatementLoaded = ko.observable(false);

    this.statementPath.subscribe(() => {
      this.getExternalStatement();
    });

    this.associatedDocumentLoading = ko.observable(true);
    this.associatedDocument = ko.observable();
    this.associatedDocumentUuid = ko.observable(snippetRaw.associatedDocumentUuid);
    this.associatedDocumentUuid.subscribe(val => {
      if (val !== '') {
        this.getExternalStatement();
      } else {
        this.statement_raw('');
        this.ace().setValue('', 1);
      }
    });
    this.statement_raw = ko.observable(snippetRaw.statement_raw || '');
    this.selectedStatement = ko.observable('');
    this.positionStatement = ko.observable(null);
    this.lastExecutedStatement = ko.observable(null);
    this.statementsList = ko.observableArray();

    let beforeExecute = false;
    this.beforeExecute = () => {
      beforeExecute = true;
      huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, this);
    };

    huePubSub.subscribe(
      ACTIVE_STATEMENT_CHANGED_EVENT,
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
          this.positionStatement(statementDetails.activeStatement);
          this.activeExecutable(this.executor.update(statementDetails, beforeExecute));
          beforeExecute = false;
          if (statementDetails.activeStatement) {
            const statementsList = [];
            statementDetails.precedingStatements.forEach(statement => {
              statementsList.push(statement.statement);
            });
            statementsList.push(statementDetails.activeStatement.statement);
            statementDetails.followingStatements.forEach(statement => {
              statementsList.push(statement.statement);
            });
            this.statementsList(statementsList); // Or fetch on demand via editor.refresh.statement.locations and remove observableArray?
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

    this.aceSize = ko.observable(snippetRaw.aceSize || 100);
    this.status = ko.observable(snippetRaw.status || STATUS.loading);
    this.statusForButtons = ko.observable(STATUS_FOR_BUTTONS.executed);

    this.properties = ko.observable(
      komapping.fromJS(snippetRaw.properties || getDefaultSnippetProperties(this.type()))
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
      window.setTimeout(() => {
        if (this.ace() !== null) {
          this.ace().focus();
        }
      }, 100);
    });
    if (snippetRaw.variables) {
      snippetRaw.variables.forEach(variable => {
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
    this.variables = komapping.fromJS(snippetRaw.variables || []);
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

    let defaultShowLogs = true;
    if (this.parentVm.editorMode() && $.totalStorage('hue.editor.showLogs')) {
      defaultShowLogs = $.totalStorage('hue.editor.showLogs');
    }
    this.showLogs = ko.observable(snippetRaw.showLogs || defaultShowLogs);
    this.jobs = ko.observableArray(snippetRaw.jobs || []);

    this.executeNextTimeout = -1;
    this.refreshTimeouts = {};

    this.showLogs.subscribe(val => {
      huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
      if (this.parentVm.editorMode()) {
        $.totalStorage('hue.editor.showLogs', val);
      }
    });

    this.isLoading = ko.pureComputed(() => this.status() === STATUS.loading);

    this.resultsKlass = ko.pureComputed(() => 'results ' + this.type());

    this.errorsKlass = ko.pureComputed(() => this.resultsKlass() + ' alert alert-error');

    this.is_redacted = ko.observable(!!snippetRaw.is_redacted);

    this.settingsVisible = ko.observable(!!snippetRaw.settingsVisible);
    this.saveResultsModalVisible = ko.observable(false);

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

      this.checkComplexity = async () => {
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
              notebookJson: await this.parentNotebook.toContextJson(),
              snippetJson: this.toContextJson()
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

    this.wasBatchExecuted = ko.observable(!!snippetRaw.wasBatchExecuted);
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
    this.lastExecuted = ko.observable(snippetRaw.lastExecuted || 0);
    this.lastAceSelectionRowOffset = ko.observable(snippetRaw.lastAceSelectionRowOffset || 0);

    this.executingBlockingOperation = null; // A ExecuteStatement()
    this.showLongOperationWarning = ko.observable(false);
    this.showLongOperationWarning.subscribe(newValue => {
      if (newValue) {
        hueAnalytics.convert('editor', 'showLongOperationWarning');
      }
    });

    this.longOperationTimeout = -1;

    this.lastCompatibilityRequest = undefined;

    this.isFetchingData = false;

    this.isCanceling = ko.observable(false);

    this.autocompleter = new AceAutocompleteWrapper({
      snippet: this,
      user: this.parentVm.user,
      optEnabled: false,
      timeout: this.parentVm.autocompleteTimeout
    });

    this.activeExecutable = ko.observable();

    this.executor = new Executor({
      compute: this.compute,
      database: this.database,
      sourceType: this.type,
      namespace: this.namespace,
      isOptimizerEnabled: this.parentVm.isOptimizerEnabled(),
      snippet: this,
      isSqlEngine: this.isSqlDialect
    });

    if (snippetRaw.executor) {
      try {
        this.executor.executables = snippetRaw.executor.executables.map(executableRaw => {
          switch (executableRaw.type) {
            case 'sqlExecutable': {
              return SqlExecutable.fromJs(this.executor, executableRaw);
            }
            default: {
              throw new Error('Failed to created executable of type ' + executableRaw.type);
            }
          }
        });

        this.executor.executables.forEach(async executable => {
          if (executable.status !== EXECUTION_STATUS.ready) {
            await executable.checkStatus();
          } else {
            executable.notify();
          }
        });
      } catch (err) {
        console.error(err); // TODO: Move up
      }
    }

    huePubSub.subscribe(EXECUTABLE_UPDATED_EVENT, executable => {
      if (this.activeExecutable() === executable) {
        this.updateFromExecutable(executable);
      }
    });

    this.activeExecutable.subscribe(this.updateFromExecutable.bind(this));

    this.refreshHistory = notebook.fetchHistory;

    huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, this);
  }

  updateFromExecutable(executable) {
    if (executable) {
      if (
        executable.status === EXECUTION_STATUS.available ||
        executable.status === EXECUTION_STATUS.failed ||
        executable.status === EXECUTION_STATUS.success
      ) {
        huePubSub.publish(UPDATE_HISTORY_EVENT);
      }
      this.status(executable.status);
      if (executable.result) {
        this.currentQueryTab('queryResults');
      }
      if (this.parentVm.editorMode() && executable.history) {
        this.parentNotebook.id(executable.history.id);
        this.parentNotebook.uuid(executable.history.uuid);
        this.parentNotebook.isHistory(true);
        this.parentNotebook.parentSavedQueryUuid(executable.history.parentId);
        if (!this.parentVm.isNotificationManager()) {
          const url = this.parentVm.URLS.editor + '?editor=' + executable.history.id;
          this.parentVm.changeURL(url);
        }
      }
    }
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

  checkCompatibility() {
    this.hasSuggestion(null);
    this.compatibilitySourcePlatform(COMPATIBILITY_SOURCE_PLATFORMS[this.type()]);
    this.compatibilityTargetPlatform(
      COMPATIBILITY_TARGET_PLATFORMS[this.type() === TYPE.hive ? TYPE.impala : TYPE.hive]
    );
    this.queryCompatibility();
  }

  async close() {
    $.post('/notebook/api/close_statement', {
      notebook: await this.parentNotebook.toContextJson(),
      snippet: this.toContextJson()
    });
  }

  // async executeNext() {
  //   hueAnalytics.log('notebook', 'execute/' + this.type());
  //
  //   const now = new Date().getTime();
  //   if (now - this.lastExecuted() < 1000) {
  //     return; // Prevent fast clicks
  //   }
  //   this.lastExecuted(now);
  //
  //   if (this.type() === TYPE.impala) {
  //     this.showExecutionAnalysis(false);
  //     huePubSub.publish('editor.clear.execution.analysis');
  //   }
  //
  //   // Editor based execution
  //   if (this.ace()) {
  //     const selectionRange = this.ace().getSelectionRange();
  //
  //     huePubSub.publish('ace.set.autoexpand', { autoExpand: false, snippet: this });
  //     this.lastAceSelectionRowOffset(Math.min(selectionRange.start.row, selectionRange.end.row));
  //   }
  //
  //   const $snip = $('#snippet_' + this.id());
  //   $snip.find('.progress-snippet').animate(
  //     {
  //       height: '3px'
  //     },
  //     100
  //   );
  //
  //   $('.jHueNotify').remove();
  //   this.parentNotebook.forceHistoryInitialHeight(true);
  //   this.errors([]);
  //   huePubSub.publish('editor.clear.highlighted.errors', this.ace());
  //   this.jobs([]);
  //
  //   this.parentNotebook.historyCurrentPage(1);
  //
  //   this.startLongOperationTimeout();
  //
  //   try {
  //     await this.executor.executeNext();
  //   } catch (error) {}
  //   this.stopLongOperationTimeout();
  // }

  execute() {
    // From ctrl + enter
    huePubSub.publish(EXECUTE_ACTIVE_EXECUTABLE_EVENT, this.activeExecutable());
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

  async getExternalStatement() {
    this.externalStatementLoaded(false);
    apiHelper
      .getExternalStatement({
        notebookJson: await this.parentNotebook.toContextJson(),
        snippetJson: this.toContextJson()
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

  async getSimilarQueries() {
    hueAnalytics.log('notebook', 'get_query_similarity');

    apiHelper
      .statementSimilarity({
        notebookJson: await this.parentNotebook.toContextJson(),
        snippetJson: this.toContextJson(),
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
      // this.checkStatus();
    } else if (this.status() === STATUS.loading) {
      this.status(STATUS.failed);
      this.jobs([]);
    } else if (this.status() === STATUS.readyExecute) {
      this.execute();
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

  async queryCompatibility(targetPlatform) {
    apiHelper.cancelActiveRequest(this.lastCompatibilityRequest);

    hueAnalytics.log('notebook', 'compatibility');
    this.compatibilityCheckRunning(targetPlatform !== this.type());
    this.hasSuggestion(null);
    const positionStatement = this.positionStatement();

    this.lastCompatibilityRequest = apiHelper
      .statementCompatibility({
        notebookJson: await this.parentNotebook.toContextJson(),
        snippetJson: this.toContextJson(),
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

  startLongOperationTimeout() {
    this.longOperationTimeout = window.setTimeout(() => {
      this.showLongOperationWarning(true);
    }, 2000);
  }

  stopLongOperationTimeout() {
    window.clearTimeout(this.longOperationTimeout);
    this.showLongOperationWarning(false);
  }

  toContextJson() {
    return JSON.stringify({
      id: this.id(),
      type: this.type(),
      status: this.status(),
      statementType: this.statementType(),
      statement: this.statement(),
      aceCursorPosition: this.aceCursorPosition(),
      statementPath: this.statementPath(),
      associatedDocumentUuid: this.associatedDocumentUuid(),
      properties: komapping.toJS(this.properties), // TODO: Drop komapping
      result: {}, // TODO: Moved to executor but backend requires it
      database: this.database(),
      compute: this.compute(),
      wasBatchExecuted: this.wasBatchExecuted(),
      editorWsChannel: window.WS_CHANNEL
    });
  }

  toJs() {
    return {
      aceCursorPosition: this.aceCursorPosition(),
      aceSize: this.aceSize(),
      associatedDocumentUuid: this.associatedDocumentUuid(),
      executor: this.executor.toJs(),
      compute: this.compute(),
      currentQueryTab: this.currentQueryTab(),
      database: this.database(),
      id: this.id(),
      is_redacted: this.is_redacted(),
      lastAceSelectionRowOffset: this.lastAceSelectionRowOffset(),
      lastExecuted: this.lastExecuted(),
      name: this.name(),
      namespace: this.namespace(),
      pinnedContextTabs: this.pinnedContextTabs(),
      properties: komapping.toJS(this.properties), // TODO: Drop komapping
      settingsVisible: this.settingsVisible(),
      showLogs: this.showLogs(),
      statement_raw: this.statement_raw(),
      statementPath: this.statementPath(),
      statementType: this.statementType(),
      status: this.status(),
      type: this.type(),
      variables: this.variables().map(variable => ({
        meta: variable.meta && {
          options: variable.meta.options && variable.meta.options(), // TODO: Map?
          placeHolder: variable.meta.placeHolder && variable.meta.placeHolder(),
          type: variable.meta.type && variable.meta.type()
        },
        name: variable.name(),
        path: variable.path(),
        sample: variable.sample(),
        sampleUser: variable.sampleUser(),
        step: variable.step(),
        type: variable.type(),
        value: variable.value()
      })),
      wasBatchExecuted: this.wasBatchExecuted()
    };
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

    const contextSetPromise = $.when(namespaceDeferred, computeDeferred);

    contextSetPromise.dispose = () => {
      if (namespaceSub) {
        namespaceSub.dispose();
      }
      if (computeSub) {
        computeSub.dispose();
      }
      namespaceDeferred.reject();
      computeDeferred.reject();
    };

    return contextSetPromise;
  }
}
