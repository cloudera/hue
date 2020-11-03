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

import 'apps/notebook2/components/ko.executableLogs';
import 'apps/notebook2/components/ko.executableProgressBar';
import 'apps/notebook2/components/ko.snippetEditorActions';
import 'apps/notebook2/components/ko.snippetResults';
import 'apps/notebook2/components/ko.queryHistory';

import './components/ExecutableActionsKoBridge.vue';
import './components/aceEditor/AceEditorKoBridge.vue';

import AceAutocompleteWrapper from 'apps/notebook/aceAutocompleteWrapper';
import apiHelper from 'api/apiHelper';
import Executor from 'apps/notebook2/execution/executor';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import hueUtils, { defer } from 'utils/hueUtils';
import sessionManager from 'apps/notebook2/execution/sessionManager';
import SqlExecutable from 'apps/notebook2/execution/sqlExecutable';
import { HIDE_FIXED_HEADERS_EVENT, REDRAW_FIXED_HEADERS_EVENT } from 'apps/notebook2/events';
import {
  EXECUTABLE_STATUS_TRANSITION_EVENT,
  EXECUTABLE_UPDATED_EVENT,
  EXECUTION_STATUS
} from 'apps/notebook2/execution/executable';
import {
  ACTIVE_STATEMENT_CHANGED_EVENT,
  CURSOR_POSITION_CHANGED_EVENT,
  REFRESH_STATEMENT_LOCATIONS_EVENT
} from 'ko/bindings/ace/aceLocationHandler';
import { EXECUTE_ACTIVE_EXECUTABLE_EVENT } from './components/ExecutableActions.vue';
import { ADD_TO_HISTORY_EVENT } from 'apps/notebook2/components/ko.queryHistory';
import { findEditorConnector, getLastKnownConfig } from 'utils/hueConfig';
import { cancelActiveRequest } from 'api/apiUtils';
import { getOptimizer } from 'catalog/optimizer/optimizer';
import {
  ASSIST_GET_DATABASE_EVENT,
  ASSIST_GET_SOURCE_EVENT,
  ASSIST_SET_SOURCE_EVENT
} from 'ko/components/assist/events';
import { POST_FROM_LOCATION_WORKER_EVENT } from 'sql/sqlWorkerHandler';
import { VariableSubstitutionHandler } from './variableSubstitution';

// TODO: Remove for ENABLE_NOTEBOOK_2. Temporary here for debug
window.SqlExecutable = SqlExecutable;
window.Executor = Executor;

export const CURRENT_QUERY_TAB_SWITCHED_EVENT = 'current.query.tab.switched';

export const DIALECT = {
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
  hive: { name: 'Hive', value: DIALECT.hive },
  impala: { name: 'Impala', value: DIALECT.impala }
};

const getDefaultSnippetProperties = snippetType => {
  const properties = {};

  if (snippetType === DIALECT.jar || snippetType === DIALECT.py) {
    properties['driverCores'] = '';
    properties['executorCores'] = '';
    properties['numExecutors'] = '';
    properties['queue'] = '';
    properties['archives'] = [];
    properties['files'] = [];
  } else if (snippetType === DIALECT.java) {
    properties['archives'] = [];
    properties['files'] = [];
    properties['capture_output'] = false;
  } else if (snippetType === DIALECT.shell) {
    properties['archives'] = [];
    properties['files'] = [];
  } else if (snippetType === DIALECT.mapreduce) {
    properties['app_jar'] = '';
    properties['hadoopProperties'] = [];
    properties['jars'] = [];
    properties['files'] = [];
    properties['archives'] = [];
  } else if (snippetType === DIALECT.spark2) {
    properties['app_name'] = '';
    properties['class'] = '';
    properties['jars'] = [];
    properties['spark_opts'] = [];
    properties['spark_arguments'] = [];
    properties['files'] = [];
  } else if (snippetType === DIALECT.sqoop1) {
    properties['files'] = [];
  } else if (snippetType === DIALECT.hive) {
    properties['settings'] = [];
    properties['files'] = [];
    properties['functions'] = [];
    properties['arguments'] = [];
  } else if (snippetType === DIALECT.impala) {
    properties['settings'] = [];
  } else if (snippetType === DIALECT.pig) {
    properties['parameters'] = [];
    properties['hadoopProperties'] = [];
    properties['resources'] = [];
  } else if (snippetType === DIALECT.distcp) {
    properties['source_path'] = '';
    properties['destination_path'] = '';
  } else if (snippetType === DIALECT.shell) {
    properties['command_path'] = '';
    properties['arguments'] = [];
    properties['env_var'] = [];
    properties['capture_output'] = true;
  }

  if (snippetType === DIALECT.jar || snippetType === DIALECT.java) {
    properties['app_jar'] = '';
    properties['class'] = '';
    properties['arguments'] = [];
  } else if (snippetType === DIALECT.py) {
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

    this.connector = ko.observable();

    this.connector.subscribe(connector => {
      sessionManager.getSession({ type: connector.id }).then(() => {
        this.status(STATUS.ready);
      });
    });

    this.initializeConnector(snippetRaw);

    this.dialect = ko.pureComputed(() => this.connector() && this.connector().dialect);
    this.connectorType = ko.pureComputed(() => this.connector() && this.connector().id);

    this.isSqlDialect = ko.pureComputed(() => this.connector() && this.connector().is_sql);
    this.defaultLimit = ko.observable(snippetRaw.defaultLimit);

    if (!this.defaultLimit()) {
      const lastKnownConfig = getLastKnownConfig();
      if (lastKnownConfig && lastKnownConfig.app_config && lastKnownConfig.app_config.editor) {
        this.defaultLimit(lastKnownConfig.app_config.editor.default_limit);
      }
    }

    this.isBatchable = ko.pureComputed(() => this.connector() && this.connector().is_batchable);

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
      if (newValue && this.dialect()) {
        this.parentVm.notifyDialectChange(this.dialect(), this.isSqlDialect());
      }
    });

    this.editorMode = this.parentVm.editorMode;

    this.explanation = ko.observable();

    this.getAceMode = () => this.parentVm.getSnippetViewSettings(this.dialect()).aceMode;

    this.dbSelectionVisible = ko.observable(false);

    this.showExecutionAnalysis = ko.observable(false);

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
          huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, this.id());
        }
        previousDatabase = newValue;
      }
    });

    this.database(snippetRaw.database);

    // History is currently in Notebook, same with saved queries by snippets, might be better in assist
    this.currentQueryTab = ko.observable(snippetRaw.currentQueryTab || 'queryHistory');

    this.currentQueryTab.subscribe(newVal => {
      huePubSub.publish(HIDE_FIXED_HEADERS_EVENT);
      if (newVal === 'queryResults') {
        defer(() => {
          huePubSub.publish(REDRAW_FIXED_HEADERS_EVENT);
        });
      }
    });

    this.pinnedContextTabs = ko.observableArray(snippetRaw.pinnedContextTabs || []);

    huePubSub.publish(ASSIST_GET_SOURCE_EVENT, source => {
      if (source !== this.dialect()) {
        huePubSub.publish(ASSIST_SET_SOURCE_EVENT, this.dialect());
      }
    });

    this.ignoreNextAssistDatabaseUpdate = false;

    if (!this.database()) {
      huePubSub.publish(ASSIST_GET_DATABASE_EVENT, {
        connector: this.connector(),
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

    huePubSub.subscribe(CURSOR_POSITION_CHANGED_EVENT, details => {
      if (details.editorId === this.id()) {
        this.aceCursorPosition(details.position);
      }
    });

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
          this.activeExecutable(this.executor.update(statementDetails, beforeExecute, this));
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
      komapping.fromJS(snippetRaw.properties || getDefaultSnippetProperties(this.dialect()))
    );
    this.hasProperties = ko.pureComputed(
      () => Object.keys(komapping.toJS(this.properties())).length > 0
    );

    this.viewSettings = ko.pureComputed(() => this.parentVm.getSnippetViewSettings(this.dialect()));

    const previousProperties = {};
    this.dialect.subscribe(
      oldValue => {
        previousProperties[oldValue] = this.properties();
      },
      null,
      'beforeChange'
    );

    this.dialect.subscribe(newValue => {
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

    this.variableSubstitutionHandler = new VariableSubstitutionHandler(
      this.connector,
      this.statement_raw,
      snippetRaw.variables
    );

    this.variableSubstitutionHandler.variables.subscribe(() => {
      $(document).trigger('updateResultHeaders', this);
    });

    huePubSub.subscribe(POST_FROM_LOCATION_WORKER_EVENT, e => {
      this.variableSubstitutionHandler.cancelRunningRequests();
      this.variableSubstitutionHandler.updateFromLocations(e.data.locations);
    });

    this.statement = ko.pureComputed(() => {
      let statement = this.statement_raw();
      if (this.isSqlDialect()) {
        if (this.activeExecutable()) {
          statement = this.activeExecutable().getStatement();
        } else if (this.selectedStatement()) {
          statement = this.selectedStatement();
        } else if (this.positionStatement()) {
          statement = this.positionStatement().statement;
        }
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

    this.resultsKlass = ko.pureComputed(() => 'results ' + this.dialect());

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

    this.compatibilitySourcePlatform = ko.observable(
      COMPATIBILITY_SOURCE_PLATFORMS[this.dialect()]
    );
    this.compatibilitySourcePlatform.subscribe(newValue => {
      if (newValue && newValue.value !== this.dialect()) {
        this.hasSuggestion(null);
        this.compatibilityTargetPlatform(COMPATIBILITY_TARGET_PLATFORMS[this.dialect()]);
        this.queryCompatibility();
      }
    });

    this.compatibilityTargetPlatforms = [];
    Object.keys(COMPATIBILITY_TARGET_PLATFORMS).forEach(key => {
      this.compatibilityTargetPlatforms.push(COMPATIBILITY_TARGET_PLATFORMS[key]);
    });
    this.compatibilityTargetPlatform = ko.observable(
      COMPATIBILITY_TARGET_PLATFORMS[this.dialect()]
    );

    this.showOptimizer = ko.observable(
      apiHelper.getFromTotalStorage('editor', 'show.optimizer', false)
    );
    this.showOptimizer.subscribe(newValue => {
      if (newValue !== null) {
        apiHelper.setInTotalStorage('editor', 'show.optimizer', newValue);
      }
    });

    this.wasBatchExecuted = ko.observable(!!snippetRaw.wasBatchExecuted);
    this.isReady = ko.pureComputed(
      () =>
        (this.statementType() === 'text' &&
          ((this.isSqlDialect() && this.statement() !== '') ||
            ([DIALECT.jar, DIALECT.java, DIALECT.spark2, DIALECT.distcp].indexOf(this.dialect()) ===
              -1 &&
              this.statement() !== '') ||
            ([DIALECT.jar, DIALECT.java].indexOf(this.dialect()) !== -1 &&
              this.properties().app_jar() !== '' &&
              this.properties().class() !== '') ||
            (DIALECT.spark2 === this.dialect() && this.properties().jars().length > 0) ||
            (DIALECT.shell === this.dialect() && this.properties().command_path().length > 0) ||
            (DIALECT.mapreduce === this.dialect() && this.properties().app_jar().length > 0) ||
            (DIALECT.distcp === this.dialect() &&
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

    // TODO: User connector instead of compute, namespace, sourceType, isOptimizerEnabled, isSqlEngine
    this.executor = new Executor({
      compute: this.compute,
      database: this.database,
      connector: this.connector,
      namespace: this.namespace,
      defaultLimit: this.defaultLimit,
      isOptimizerEnabled: this.parentVm.isOptimizerEnabled(),
      snippet: this,
      isSqlEngine: this.isSqlDialect,
      variableSubstitionHandler: this.variableSubstitutionHandler
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

    huePubSub.subscribe(EXECUTABLE_STATUS_TRANSITION_EVENT, transitionDetails => {
      if (this.activeExecutable() === transitionDetails.executable) {
        if (
          (transitionDetails.newStatus === EXECUTION_STATUS.available ||
            transitionDetails.newStatus === EXECUTION_STATUS.failed ||
            transitionDetails.newStatus === EXECUTION_STATUS.success) &&
          this.activeExecutable().history &&
          this.activeExecutable().handle
        ) {
          huePubSub.publish(ADD_TO_HISTORY_EVENT, {
            absoluteUrl: undefined,
            statement: this.activeExecutable().handle.statement,
            lastExecuted: this.activeExecutable().executeStarted,
            status: this.activeExecutable().status,
            name: this.parentNotebook.name(),
            uuid: this.activeExecutable().history.uuid
          });
        }
      }
    });

    this.activeExecutable.subscribe(this.updateFromExecutable.bind(this));

    this.refreshHistory = notebook.fetchHistory;

    huePubSub.publish(REFRESH_STATEMENT_LOCATIONS_EVENT, this);

    // TODO: Add optimizer check per connector?
    if (window.HAS_OPTIMIZER && !this.parentVm.isNotificationManager()) {
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

        cancelActiveRequest(lastComplexityRequest);

        hueAnalytics.log('notebook', 'get_query_risk');
        clearActiveRisks();

        const changeSubscription = this.statement.subscribe(() => {
          changeSubscription.dispose();
          cancelActiveRequest(lastComplexityRequest);
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
          lastComplexityRequest = getOptimizer(this.connector())
            .analyzeRisk({
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

  changeDialect(dialect) {
    const connector = findEditorConnector(connector => connector.dialect === dialect);
    if (!connector) {
      throw new Error('No connector found for dialect ' + dialect);
    }
    // TODO: Switch changeDialect to changeType
    this.connector(connector);
  }

  updateFromExecutable(executable) {
    if (executable) {
      this.lastExecuted(executable.executeStarted);
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
    this.compatibilitySourcePlatform(COMPATIBILITY_SOURCE_PLATFORMS[this.dialect()]);
    this.compatibilityTargetPlatform(
      COMPATIBILITY_TARGET_PLATFORMS[
        this.dialect() === DIALECT.hive ? DIALECT.impala : DIALECT.hive
      ]
    );
    this.queryCompatibility();
  }

  async close() {
    $.post('/notebook/api/close_statement', {
      notebook: await this.parentNotebook.toContextJson(),
      snippet: this.toContextJson()
    });
  }

  execute() {
    // From ctrl + enter
    huePubSub.publish(EXECUTE_ACTIVE_EXECUTABLE_EVENT, this.activeExecutable());
  }

  fetchExecutionAnalysis() {
    if (this.dialect() === DIALECT.impala) {
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

  getPlaceHolder() {
    return this.parentVm.getSnippetViewSettings(this.dialect()).placeHolder;
  }

  async getSimilarQueries() {
    hueAnalytics.log('notebook', 'get_query_similarity');

    getOptimizer(this.connector())
      .analyzeSimilarity({
        notebookJson: await this.parentNotebook.toContextJson(),
        snippetJson: this.toContextJson(),
        sourcePlatform: this.dialect()
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
        type: this.dialect(),
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

  handleAssistSelection(entry) {
    if (this.ignoreNextAssistDatabaseUpdate) {
      this.ignoreNextAssistDatabaseUpdate = false;
    } else if (entry.getConnector().id === this.connector().id) {
      if (this.namespace() !== entry.namespace) {
        this.namespace(entry.namespace);
      }
      if (this.database() !== entry.name) {
        this.database(entry.name);
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

  initializeConnector(snippetRaw) {
    const connectorIdToFind = (snippetRaw.connector && snippetRaw.connector.id) || snippetRaw.type;
    let foundConnector = findEditorConnector(connector => connector.id === connectorIdToFind);

    if (!foundConnector) {
      // If not found by type pick the first by dialect
      const connectorDialectToFind =
        (snippetRaw.connector && snippetRaw.connector.dialect) || snippetRaw.type;
      foundConnector = findEditorConnector(
        connector => connector.dialect === connectorDialectToFind
      );
    }

    if (!foundConnector && snippetRaw.connector) {
      // This could happen when the connector has been removed completely
      foundConnector = snippetRaw.connector;
    }

    this.connector(foundConnector);
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
    cancelActiveRequest(this.lastCompatibilityRequest);

    hueAnalytics.log('notebook', 'compatibility');
    this.compatibilityCheckRunning(targetPlatform !== this.dialect());
    this.hasSuggestion(null);
    const positionStatement = this.positionStatement();

    this.lastCompatibilityRequest = getOptimizer(this.connector())
      .analyzeCompatibility({
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
      type: this.dialect(),
      connector: this.connector(),
      defaultLimit: this.defaultLimit(),
      status: this.status(),
      statementType: this.statementType(),
      statement: this.statement(),
      aceCursorPosition: this.aceCursorPosition(),
      lastExecuted: this.lastExecuted(),
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
      connector: this.connector(),
      currentQueryTab: this.currentQueryTab(),
      database: this.database(),
      defaultLimit: this.defaultLimit(),
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
      type: this.dialect(), // TODO: Drop once connectors are stable
      variables: this.variableSubstitutionHandler.variables().map(variable => variable.toJs()),
      wasBatchExecuted: this.wasBatchExecuted()
    };
  }

  uploadQuery(query_id) {
    $.post('/metadata/api/optimizer/upload/query', {
      query_id: query_id,
      sourcePlatform: this.dialect()
    });
  }

  uploadQueryHistory(n) {
    hueAnalytics.log('notebook', 'upload_query_history');

    $.post('/metadata/api/optimizer/upload/history', {
      n: typeof n != 'undefined' ? n : null,
      sourcePlatform: this.dialect()
    }).then(data => {
      if (data.status === 0) {
        $(document).trigger(
          'info',
          data.upload_history[this.dialect()].count +
            ' queries uploaded successfully. Processing them...'
        );
        this.watchUploadStatus(data.upload_history[this.dialect()].status.workloadId);
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
        sourcePlatform: JSON.stringify(this.dialect()),
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
