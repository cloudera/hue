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

var EditorViewModel = (function() {

  var NOTEBOOK_MAPPING = {
    ignore: [
      'ace', 'aceMode', 'autocompleter', 'availableDatabases', 'availableSnippets', 'avoidClosing', 'canWrite',
      'cleanedDateTimeMeta', 'cleanedMeta', 'cleanedNumericMeta', 'cleanedStringMeta', 'dependents', 'errorLoadingQueries',
      'hasProperties', 'history', 'images', 'inFocus', 'queries', 'saveResultsModalVisible', 'selectedStatement',
      'snippetImage', 'user', 'positionStatement', 'lastExecutedStatement', 'downloadResultViewModel'
    ]
  };

  var COMPATIBILITY_SOURCE_PLATFORMS ={
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

  var COMPATIBILITY_TARGET_PLATFORMS ={
    impala: { name: 'Impala', value: 'impala' },
    hive: { name: 'Hive', value: 'hive' }
  };

  var Result = function (snippet, result) {
    var self = this;

    snippet = $.extend(snippet, snippet.chartType == 'lines' && { // Retire line chart
        chartType: 'bars',
        chartTimelineType: 'line'
    });
    self.id = ko.observable(typeof result.id != "undefined" && result.id != null ? result.id : UUID());
    self.type = ko.observable(typeof result.type != "undefined" && result.type != null ? result.type : 'table');
    self.hasResultset = ko.observable(typeof result.hasResultset != "undefined" && result.hasResultset != null ? result.hasResultset : true)
      .extend("throttle", 100);
    self.handle = ko.observable(typeof result.handle != "undefined" && result.handle != null ? result.handle : {});
    self.meta = ko.observableArray(typeof result.meta != "undefined" && result.meta != null ? result.meta : []);

    var adaptMeta = function () {
      var i = 0;
      self.meta().forEach(function (item) {
        if (typeof item.checked === 'undefined') {
          item.checked = ko.observable(true);
          item.checked.subscribe(function () {
            self.filteredMetaChecked(self.filteredMeta().some(function (item) { return item.checked(); }));
          });
        }
        item.type = item.type.replace(/_type/i, '').toLowerCase();
        if (typeof item.originalIndex === 'undefined') {
          item.originalIndex = i;
        }
        i++;
      })
    };

    adaptMeta();
    self.meta.subscribe(adaptMeta);


    self.rows = ko.observable(typeof result.rows != "undefined" && result.rows != null ? result.rows : null);
    self.hasMore = ko.observable(typeof result.hasMore != "undefined" && result.hasMore != null ? result.hasMore : false);
    self.statement_id = ko.observable(typeof result.statement_id != "undefined" && result.statement_id != null ? result.statement_id : 0);
    self.statement_range = ko.observable(typeof result.statement_range != "undefined" && result.statement_range != null ? result.statement_range : {
      start: {
        row: 0,
        column: 0
      },
      end: {
        row: 0,
        column: 0
      }
    });
    self.statements_count = ko.observable(typeof result.statements_count != "undefined" && result.statements_count != null ? result.statements_count : 1);
    self.previous_statement_hash = ko.observable(typeof result.previous_statement_hash != "undefined" && result.previous_statement_hash != null ? result.previous_statement_hash : null);
    self.cleanedMeta = ko.computed(function () {
      return ko.utils.arrayFilter(self.meta(), function (item) {
        return item.name != ''
      });
    });
    self.metaFilter = ko.observable();

    self.isMetaFilterVisible = ko.observable(false);
    self.filteredMetaChecked = ko.observable(true);
    self.filteredMeta = ko.pureComputed(function () {
      if (!self.metaFilter() || self.metaFilter().query === '') {
        return self.meta();
      }

      return self.meta().filter(function (item) {
        var facets = self.metaFilter().facets;
        var isFacetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
        var isTextMatch = !self.metaFilter().text || self.metaFilter().text.length === 0;
        var match = true;

        if (!isFacetMatch) {
          match = !!facets['type'][item.type];
        }

        if (match && !isTextMatch) {
          match = self.metaFilter().text.every(function (text) {
            return item.name.toLowerCase().indexOf(text.toLowerCase()) !== -1;
          });
        }
        return match;
      });
    });

    self.autocompleteFromEntries = function (nonPartial, partial) {
      var result = [];
      var partialLower = partial.toLowerCase();
      self.meta().forEach(function (column) {
        if (column.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + column.name.substring(partial.length))
        } else if (column.name.toLowerCase().indexOf('.' + partialLower) !== -1) {
          result.push(nonPartial + partial + column.name.substring(partial.length + column.name.toLowerCase().indexOf('.' + partialLower) + 1))
        }
      });

      return result;
    };
    self.clickFilteredMetaCheck = function () {
      self.filteredMeta().forEach(function (item) {
        item.checked(self.filteredMetaChecked());
      });
    };

    self.fetchedOnce = ko.observable(typeof result.fetchedOnce != "undefined" && result.fetchedOnce != null ? result.fetchedOnce : false);
    self.startTime = ko.observable(typeof result.startTime != "undefined" && result.startTime != null ? new Date(result.startTime) : new Date());
    self.endTime = ko.observable(typeof result.endTime != "undefined" && result.endTime != null ? new Date(result.endTime) : new Date());
    self.executionTime = ko.computed(function () {
      return self.endTime().getTime() - self.startTime().getTime();
    });

    function isNumericColumn(type) {
      return $.inArray(type, ['tinyint', 'smallint', 'int', 'bigint', 'float', 'double', 'decimal', 'real']) > -1;
    }

    function isDateTimeColumn(type) {
      return $.inArray(type, ['timestamp', 'date', 'datetime']) > -1;
    }

    function isComplexColumn(type) {
      return $.inArray(type, ['array', 'map', 'struct']) > -1;
    }

    function isStringColumn(type) {
      return !isNumericColumn(type) && !isDateTimeColumn(type) && !isComplexColumn(type);
    }

    self.cleanedNumericMeta = ko.computed(function () {
      return ko.utils.arrayFilter(self.meta(), function (item) {
        return item.name != '' && isNumericColumn(item.type)
      });
    });

    self.cleanedStringMeta = ko.computed(function () {
      return ko.utils.arrayFilter(self.meta(), function (item) {
        return item.name != '' && isStringColumn(item.type)
      });
    });

    self.cleanedDateTimeMeta = ko.computed(function () {
      return ko.utils.arrayFilter(self.meta(), function (item) {
        return item.name != '' && isDateTimeColumn(item.type)
      });
    });

    self.data = ko.observableArray(typeof result.data != "undefined" && result.data != null ? result.data : []);
    self.data.extend({ rateLimit: 50 });
    self.explanation = ko.observable(typeof result.explanation != "undefined" && result.explanation != null ? result.explanation : '');
    self.images = ko.observableArray(typeof result.images != "undefined" && result.images != null ? result.images : []);
    self.images.extend({ rateLimit: 50 });
    self.logs = ko.observable('');
    self.logLines = 0;
    self.hasSomeResults = ko.computed(function () {
      return self.hasResultset() && self.data().length > 0; // status() == 'available'
    });

    self.getContext = function() {
      return {
          id: self.id,
          type: self.type,
          handle: self.handle
      };
    };

    self.clear = function () {
      self.fetchedOnce(false);
      self.hasMore(false);
      self.meta.removeAll();
      self.data.removeAll();
      self.images.removeAll();
      self.logs('');
      self.handle({ // Keep multiquery indexing
          has_more_statements: self.handle()['has_more_statements'],
          statement_id: self.handle()['statement_id'],
          statements_count: self.handle()['statements_count'],
          previous_statement_hash: self.handle()['previous_statement_hash'],
      });
      self.startTime(new Date());
      self.endTime(new Date());
      self.explanation('');
      self.logLines = 0;
      self.rows(null);
    };
  };

  var getDefaultSnippetProperties = function (snippetType) {
    var properties = {};

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

  var ERROR_REGEX = /line ([0-9]+)(\:([0-9]+))?/i;

  var Snippet = function (vm, notebook, snippet) {
    var self = this;

    self.id = ko.observable(typeof snippet.id != "undefined" && snippet.id != null ? snippet.id : UUID());
    self.name = ko.observable(typeof snippet.name != "undefined" && snippet.name != null ? snippet.name : '');
    self.type = ko.observable(typeof snippet.type != "undefined" && snippet.type != null ? snippet.type : 'hive');
    self.type.subscribe(function(newVal) {
      self.status('ready');
    });

    self.isBatchable = ko.computed(function() {
      return self.type() == 'hive'
          || self.type() == 'impala'
          || $.grep(vm.availableLanguages, function(language) { return language.type == self.type() && language.interface == 'oozie'; }).length > 0;
    });

    // Ace stuff
    self.aceCursorPosition = ko.observable(notebook.isHistory() ? snippet.aceCursorPosition : null);

    var aceEditor = null;

    self.ace = function (newVal) {
      if (newVal) {
        aceEditor = newVal;
        if (!notebook.isPresentationMode()) {
          aceEditor.focus();
        }
      }
      return aceEditor
    };
    self.errors = ko.observableArray([]);

    self.aceErrorsHolder = ko.observableArray([]);
    self.aceWarningsHolder = ko.observableArray([]);

    self.aceErrors = ko.pureComputed(function(){
      return self.showOptimizer() ? self.aceErrorsHolder() : [];
    });
    self.aceWarnings = ko.pureComputed(function(){
      return self.showOptimizer() ? self.aceWarningsHolder() : [];
    });

    self.availableSnippets = vm.availableSnippets();
    self.inFocus = ko.observable(false);

    self.inFocus.subscribe(function (newValue) {
      if (newValue) {
        huePubSub.publish('active.snippet.type.changed', self.type());
      }
    });

    self.editorMode = vm.editorMode;

    self.getAceMode = function() {
      return vm.getSnippetViewSettings(self.type()).aceMode;
    };

    self.dbSelectionVisible = ko.observable(false);

    self.isSqlDialect = ko.pureComputed(function () {
      return vm.getSnippetViewSettings(self.type()).sqlDialect;
    });

    self.getPlaceHolder = function() {
      return vm.getSnippetViewSettings(self.type()).placeHolder;
    };

    self.getApiHelper = function() {
      return ApiHelper.getInstance(vm);
    };

    self.namespace = ko.observable(snippet.namespace);

    self.compute = ko.observable(snippet.compute);

    self.availableDatabases = ko.observableArray();
    self.database = ko.observable();
    var previousDatabase = null;

    self.database.subscribe(function (newValue) {
      if (newValue !== null) {
        self.getApiHelper().setInTotalStorage('editor', 'last.selected.database', newValue);
        if (previousDatabase !== null && previousDatabase !== newValue) {
          huePubSub.publish('editor.refresh.statement.locations', self);
        }
        previousDatabase = newValue;
      }
    });

    self.database(typeof snippet.database !== "undefined" && snippet.database != null ? snippet.database : null);

    // History is currently in Notebook, same with saved queries by snippets, might be better in assist
    self.currentQueryTab = ko.observable(typeof snippet.currentQueryTab != "undefined" && snippet.currentQueryTab != null ? snippet.currentQueryTab : 'queryHistory');
    self.pinnedContextTabs = ko.observableArray(typeof snippet.pinnedContextTabs != "undefined" && snippet.pinnedContextTabs != null ? snippet.pinnedContextTabs : []);

    self.removeContextTab = function (context) {
      if (context.tabId === self.currentQueryTab()) {
        self.currentQueryTab('queryHistory');
      }
      self.pinnedContextTabs.remove(context);
    };

    self.errorLoadingQueries = ko.observable(false);
    self.loadingQueries = ko.observable(false);

    self.queriesHasErrors = ko.observable(false);
    self.queriesCurrentPage = ko.observable(vm.selectedNotebook() && vm.selectedNotebook().snippets().length > 0 ? vm.selectedNotebook().snippets()[0].queriesCurrentPage() : 1);
    self.queriesTotalPages = ko.observable(vm.selectedNotebook() && vm.selectedNotebook().snippets().length > 0 ? vm.selectedNotebook().snippets()[0].queriesTotalPages() : 1);
    self.queries = ko.observableArray([]);

    self.queriesFilter = ko.observable('');
    self.queriesFilterVisible = ko.observable(false);
    self.queriesFilter.extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 900 } });
    self.queriesFilter.subscribe(function(val){
      self.fetchQueries();
    });

    var lastFetchQueriesRequest = null;

    self.fetchQueries = function () {
      self.getApiHelper().cancelActiveRequest(lastFetchQueriesRequest);

      var QUERIES_PER_PAGE = 50;
      lastQueriesPage = self.queriesCurrentPage();
      self.loadingQueries(true);
      self.queriesHasErrors(false);
      lastFetchQueriesRequest = self.getApiHelper().searchDocuments({
        successCallback: function (result) {
          self.queriesTotalPages(Math.ceil(result.count / QUERIES_PER_PAGE));
          self.queries(ko.mapping.fromJS(result.documents)());
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

    var lastQueriesPage = 1;
    self.currentQueryTab.subscribe(function (newValue) {
      huePubSub.publish('redraw.fixed.headers');
      huePubSub.publish('tab.switched', newValue);
      if (newValue === 'savedQueries' && (self.queries().length === 0 || lastQueriesPage !== self.queriesCurrentPage())) {
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

    huePubSub.subscribeOnce('assist.source.set', function (source) {
      if (source !== self.type()) {
        huePubSub.publish('assist.set.source', self.type());
      }
    }, vm.huePubSubId);

    huePubSub.publish('assist.get.source');

    var ignoreNextAssistDatabaseUpdate = false;
    self.handleAssistSelection = function (databaseDef) {
      if (ignoreNextAssistDatabaseUpdate) {
        ignoreNextAssistDatabaseUpdate = false;
      } else if (databaseDef.sourceType === self.type()) {
        if (self.namespace() !== databaseDef.namespace) {
          self.namespace(databaseDef.namespace)
        }
        if (self.database() !== databaseDef.name) {
          self.database(databaseDef.name);
        }
      }
    };

    if (!self.database()) {
      huePubSub.publish('assist.get.database.callback', { source: self.type(), callback: function (databaseDef) {
        self.handleAssistSelection(databaseDef);
      }});
    }

    self.statementType = ko.observable(typeof snippet.statementType != "undefined" && snippet.statementType != null ? snippet.statementType : 'text');
    self.statementTypes = ko.observableArray(['text', 'file']); // Maybe computed later for Spark
    if (! vm.editorMode()) {
      self.statementTypes.push('document');
    }
    self.statementPath = ko.observable(typeof snippet.statementPath != "undefined" && snippet.statementPath != null ? snippet.statementPath : '');
    self.statementPath.subscribe(function(newVal) {
      self.getExternalStatement();
    });
    self.externalStatementLoaded = ko.observable(false);
    self.getExternalStatement = function() {
      self.externalStatementLoaded(false);
      $.post("/notebook/api/get_external_statement", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function(data) {
        if (data.status == 0) {
          self.externalStatementLoaded(true);
          self.statement_raw(data.statement);
          self.ace().setValue(self.statement_raw(), 1);
        } else {
          self._ajaxError(data);
        }
      });
    };
    self.associatedDocumentLoading = ko.observable(true);
    self.associatedDocument = ko.observable();
    self.associatedDocumentUuid = ko.observable(typeof snippet.associatedDocumentUuid != "undefined" && snippet.associatedDocumentUuid != null ? snippet.associatedDocumentUuid : null);
    self.associatedDocumentUuid.subscribe(function(val){
      if (val !== ''){
        self.getExternalStatement();
      }
      else {
        self.statement_raw('');
        self.ace().setValue('', 1);
      }
    });
    self.statement_raw = ko.observable(typeof snippet.statement_raw != "undefined" && snippet.statement_raw != null ? snippet.statement_raw : '');
    self.selectedStatement = ko.observable('');
    self.positionStatement = ko.observable(null);
    self.lastExecutedStatement = ko.observable(null);
    self.statementsList = ko.observableArray();

    huePubSub.subscribe('editor.active.statement.changed', function (statementDetails) {
      if (self.ace() && self.ace().container.id === statementDetails.id) {
        if (statementDetails.activeStatement) {
          self.positionStatement(statementDetails.activeStatement);
        } else {
          self.positionStatement(null);
        }

        if (statementDetails.activeStatement) {
          var _statements = [];
           statementDetails.precedingStatements.forEach(function (statement) {
             _statements.push(statement.statement);
           });
           _statements.push(statementDetails.activeStatement.statement);
           statementDetails.followingStatements.forEach(function (statement) {
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

    }, vm.huePubSubId);

    self.aceSize = ko.observable(typeof snippet.aceSize != "undefined" && snippet.aceSize != null ? snippet.aceSize : 100);
    // self.statement_raw.extend({ rateLimit: 150 }); // Should prevent lag from typing but currently send the old query when using the key shortcut
    self.status = ko.observable(typeof snippet.status != "undefined" && snippet.status != null ? snippet.status : 'loading');
    self.statusForButtons = ko.observable('executed');

    self.properties = ko.observable(ko.mapping.fromJS(typeof snippet.properties != "undefined" && snippet.properties != null ? snippet.properties : getDefaultSnippetProperties(self.type())));
    self.hasProperties = ko.computed(function() {
      return Object.keys(ko.mapping.toJS(self.properties())).length > 0;
    });

    self.viewSettings = ko.computed(function() {
      return vm.getSnippetViewSettings(self.type());
    });

    var previousProperties = {};
    self.type.subscribe(function(oldValue) {
      previousProperties[oldValue] = self.properties();
    }, null, "beforeChange");

    self.type.subscribe(function (newValue) {
      if (typeof previousProperties[newValue] != "undefined") {
        self.properties(previousProperties[newValue]);
      } else {
        self.properties(ko.mapping.fromJS(getDefaultSnippetProperties(newValue)));
      }
      self.result.clear();
      window.setTimeout(function () {
        if (self.ace() !== null) {
          self.ace().focus();
        }
      }, 100);
    });
    if (snippet.variables) {
      snippet.variables.forEach(function (variable) {
        variable.meta = (typeof variable.defaultValue === "object" && variable.defaultValue) || {type: "text", placeholder: ""};
        variable.value = variable.value || '';
        variable.type = variable.type || 'text';
        variable.sample = [];
        variable.sampleUser = variable.sampleUser || [];
        variable.path = variable.path || '';
        variable.step = '';
        delete variable.defaultValue;
      });
    }
    self.variables = ko.mapping.fromJS(typeof snippet.variables != "undefined" && snippet.variables != null ? snippet.variables : []);
    self.variables.subscribe(function (newValue) {
      $(document).trigger("updateResultHeaders", self);
    });
    self.hasCurlyBracketParameters = ko.computed(function() {
      return self.type() != 'pig';
    });
    self.getPigParameters = function() {
      var params = {};
      var variables = self.statement_raw().match(/([^\\]|^)\$[^\d'"](\w*)/g);
      var declares = self.statement_raw().match(/%declare +([^ ])+/gi);
      var defaults = self.statement_raw().match(/%default +([^;])+/gi);
      var macro_defines = self.statement_raw().match(/define [^ ]+ *\(([^\)]*)\)/gi); // no multiline
      var macro_returns = self.statement_raw().match(/returns +([^\{]*)/gi); // no multiline

      if (variables) {
        $.each(variables, function(index, param) {
          var p = param.substring(param.indexOf('$') + 1);
          params[p] = '';
        });
      }
      if (declares) {
        $.each(declares, function(index, param) {
          param = param.match(/(\w+)/g);
          if (param && param.length >= 2) {
            delete params[param[1]];
          }
        });
      }
      if (defaults) {
        $.each(defaults, function(index, param) {
          var line = param.match(/(\w+)/g);
          if (line && line.length >= 2) {
            var name = line[1];
            params[name] = param.substring(param.indexOf(name) + name.length + 1);
          }
        });
      }
      if (macro_defines) {
        $.each(macro_defines, function(index, params_line) {
          var param_line = params_line.match(/(\w+)/g);
          if (param_line && param_line.length > 2) {
            $.each(param_line, function(index, param) {
              if (index >= 2) { // Skips define NAME
                delete params[param];
              }
            });
          }
        });
      }
      if (macro_returns) {
        $.each(macro_returns, function(index, params_line) {
          var param_line = params_line.match(/(\w+)/g);
          if (param_line) {
            $.each(param_line, function(index, param) {
              if (index >= 1) { // Skip returns
                delete params[param];
              }
            });
          }
        });
      }

      return params;
    };
    self.variableNames = ko.computed(function () {
      var match, matches = {}, matchList;
      if (self.type() == 'pig') {
        matches = self.getPigParameters();
      } else {
        var re = /(?:^|\W)\${(\w*)\=?([^{}]*)}/g;
        var reComment = /(^\s*--.*)|(\/\*[\s\S]*?\*\/)/gm;
        var reList = /(?!\s*$)\s*(?:(?:([^,|()\\]*)\(\s*([^,|()\\]*)\)(?:\\[\S\s][^,|()\\]*)?)|([^,|\\]*(?:\\[\S\s][^,|\\]*)*))\s*(?:,|\||$)/g
        var statement = self.statement_raw();
        var matchComment = reComment.exec(statement);
        // if re is n & reComment is m
        // finding variables is O(n+m)
        while (match = re.exec(statement)) {
          while (matchComment && match.index > matchComment.index + matchComment[0].length) { // Comments before our match
            matchComment = reComment.exec(statement);
          }
          var isWithinComment = matchComment && match.index >= matchComment.index;
          if (isWithinComment) continue;

          // If 1 match, text value
          // If multiple matches, list value
          var value = { type: 'text', placeholder: '' };
          while (matchList = reList.exec(match[2])) {
            var option = {text:matchList[2] || matchList[3], value:matchList[3] || matchList[1]};
            option.text = option.text && option.text.trim();
            option.value = option.value && option.value.trim().replace('\,', ',').replace('\(', '(').replace('\)', ')');

            if (value.placeholder || matchList[2]) {
              if (!value.options) {
                value.options = [];
                value.type = 'select';
              }
              value.options.push(option);
            }
            if (!value.placeholder) value.placeholder = option.value;
          }
          var isPlaceholderInOptions = !value.options || value.options.some(function (current){
            return current.value == value.placeholder;
          });
          if (!isPlaceholderInOptions) {
            value.options.unshift({ text: value.placeholder, value: value.placeholder });
          }
          matches[match[1]] = matches[match[1]] || value;
        }
      }
      return $.map(matches, function (match, key) {
        var isMatchObject = typeof matches[key] === 'object';
        var meta = isMatchObject ? matches[key] : { type: 'text', placeholder: matches[key] };
        return { name: key, meta: meta };
      });
    });
    self.variableValues = {};
    self.variableNames.extend({ rateLimit: 150 });
    self.variableNames.subscribe(function (newVal) {
      var variablesLength = self.variables().length;
      var diffLengthVariables = variablesLength - newVal.length;
      var needsMore = diffLengthVariables < 0;
      var needsLess = diffLengthVariables > 0;
      self.variableValues = self.variables().reduce(function (variableValues, variable) {
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
        for (var i = 0, length = Math.abs(diffLengthVariables); i < length; i++) {
          self.variables.push(ko.mapping.fromJS({ name: '', value: '', meta: { type: 'text', placeholder: '', options: [] }, sample: [], sampleUser: [], type: 'text', step: '', path: ''}));
        }
      } else if (needsLess) {
        self.variables.splice(self.variables().length - diffLengthVariables, diffLengthVariables);
      }
      newVal.forEach(function (item, index) {
        var variable = self.variables()[index];
        variable.name(item.name);
        setTimeout(function(){
          variable.value(self.variableValues[item.name] ? self.variableValues[item.name].value : (!needsMore && variable.value()) || '');
        },0);
        variable.meta = ko.mapping.fromJS(item.meta, {}, variable.meta);
        variable.sample(variable.meta.options ? variable.meta.options().concat(variable.sampleUser()) : variable.sampleUser())
        variable.sampleUser(self.variableValues[item.name] ? self.variableValues[item.name].sampleUser : []);
        variable.type(self.variableValues[item.name] ? self.variableValues[item.name].type || 'text' : 'text');
        variable.path(self.variableValues[item.name] ? self.variableValues[item.name].path || '' : '');
        variable.catalogEntry = self.variableValues[item.name] && self.variableValues[item.name].catalogEntry;
      });
    });

    var activeSourcePromises = [];
    huePubSub.subscribe('ace.sql.location.worker.message', function (e) {
      while (activeSourcePromises.length) {
        var promise = activeSourcePromises.pop();
        if (promise.cancel) {
          promise.cancel();
        }
      }
      var sourceType = self.type();
      var oLocations = e.data.locations
      .filter(function (location) {
        return location.type === 'variable' && location.colRef;
      })
      .reduce(function (variables, location) {
        var re = /\${(\w*)\=?([^{}]*)}/g;
        var name = re.exec(location.value)[1];
        variables[name] = location;
        return variables;
      }, {});
      var updateVariableType = function (variable, sourceMeta) {
        var type;
        if (sourceMeta && sourceMeta.type) {
          type = sourceMeta.type.toLowerCase();
        } else {
          type = 'string';
        }
        var variablesValues = {};
        var value = variable.value();
        switch (type) {
          case 'timestamp':
            variablesValues.type = 'datetime-local';
            variablesValues.step = '1';
            variablesValues.value = value && moment.utc(value).format("YYYY-MM-DD HH:mm:ss.S") || moment(Date.now()).format("YYYY-MM-DD 00:00:00.0");
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
            variablesValues.value = value && moment.utc(value).format("YYYY-MM-DD") || moment(Date.now()).format("YYYY-MM-DD");
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
          setTimeout(function () {
            variable.value(variablesValues.value);
          }, 0);
        }
        variable.type(variablesValues.type);
        variable.step(variablesValues.step);
      };
      self.variables().forEach(function (variable) {
        if (oLocations[variable.name()]) {
          activeSourcePromises.push(oLocations[variable.name()].resolveCatalogEntry({ cancellable: true }).done(function (entry) {
            variable.path(entry.path.join('.'));
            variable.catalogEntry = entry;

            activeSourcePromises.push(entry.getSourceMeta({
              silenceErrors: true,
              cancellable: true
            }).then(updateVariableType.bind(self, variable)));
          }));
        } else {
          updateVariableType(variable, {
            type: 'text'
          });
        }
      });
    });
    self.statement = ko.computed(function () {
      var statement = self.isSqlDialect() ? (self.selectedStatement() ? self.selectedStatement() : (self.positionStatement() !== null ? self.positionStatement().statement : self.statement_raw())) : self.statement_raw();
      var variables = self.variables().reduce(function (variables, variable) {
        variables[variable.name()] = variable;
        return variables;
      }, {});
      if (self.variables().length) {
        var variablesString = self.variables().map(function(variable) { return variable.name(); }).join("|");
        statement = statement.replace(RegExp("([^\\\\])?\\$" + (self.hasCurlyBracketParameters() ? "{(" : "(") + variablesString + ")(=[^}]*)?" + (self.hasCurlyBracketParameters() ? "}" : ""), "g"), function(match, p1, p2){
          var variable = variables[p2];
          var pad = variable.type() == 'datetime-local' && variable.value().length == 16 ? ':00' : ''; // Chrome drops the seconds from the timestamp when it's at 0 second.
          var value = variable.value();
          return p1 + (value !== undefined && value !== null ? value + pad : variable.meta.placeholder && variable.meta.placeholder());
        });
      }
      return statement;
    });

    self.result = new Result(snippet, snippet.result);
    if (! self.result.hasSomeResults()) {
      self.currentQueryTab('queryHistory');
    }
    self.showGrid = ko.observable(typeof snippet.showGrid != "undefined" && snippet.showGrid != null ? snippet.showGrid : true);
    self.showChart = ko.observable(typeof snippet.showChart != "undefined" && snippet.showChart != null ? snippet.showChart : false);
    var defaultShowLogs = true;
    if (vm.editorMode() && $.totalStorage('hue.editor.showLogs')) {
      defaultShowLogs = $.totalStorage('hue.editor.showLogs');
    }
    self.showLogs = ko.observable(typeof snippet.showLogs !== "undefined" && snippet.showLogs != null ? snippet.showLogs : defaultShowLogs);
    self.progress = ko.observable(typeof snippet.progress !== "undefined" && snippet.progress != null ? snippet.progress : 0);
    self.jobs = ko.observableArray(typeof snippet.jobs !== "undefined" && snippet.jobs != null ? snippet.jobs : []);

    var executeNextTimeout = -1;
    var refreshTimeouts = {};
    self.onDdlExecute = function () {
      if (self.result.handle() && self.result.handle().has_more_statements) {
        window.clearTimeout(executeNextTimeout);
        executeNextTimeout = setTimeout(function () {
          self.execute(true); // Execute next, need to wait as we disabled fast click
        }, 1000);
      }
      var match = self.statement().match(/(?:CREATE|DROP)\s+TABLE\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?:`([^`]+)`|([^;\s]+))\..*/i);
      var path = [];
      if (match) {
        path.push(match[1] || match[2]); // group 1 backticked db name, group 2 regular db name
      } else {
        match = self.statement().match(/(?:CREATE|DROP)\s+(?:DATABASE|SCHEMA)\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?(?:`([^`]+)`|([^;\s]+))/i);
        if (match) {
          path.push(match[1] || match[2]); // group 1 backticked db name, group 2 regular db name
        } else if (self.database()) {
          path.push(self.database());
        }
      }

      if (path.length) {
        window.clearTimeout(refreshTimeouts[path.join('.')]);
        refreshTimeouts[path.join('.')] = window.setTimeout(function () {
          ignoreNextAssistDatabaseUpdate = true;
          DataCatalog.getEntry({ sourceType: self.type(), namespace: self.namespace(), compute: self.compute(), path: path }).done(function (entry) {
            entry.clearCache({ invalidate: 'invalidate', cascade: true, silenceErrors: true });
          });
        }, 5000);
      }
    };

    self.progress.subscribe(function (val) {
      $(document).trigger("progress", {data: val, snippet: self});
    });

    self.showGrid.subscribe(function (val) {
      if (val) {
        self.showChart(false);
        huePubSub.publish('editor.grid.shown', self);
      }
    });

    function prepopulateChart() {
      var type = self.chartType();
      hueAnalytics.log('notebook', 'chart/' + type);

      if (type === ko.HUE_CHARTS.TYPES.MAP && self.result.cleanedNumericMeta().length >= 2) {
        if ((self.chartX() === null || typeof self.chartX() === 'undefined')) {
          var name = self.result.cleanedNumericMeta()[0].name;
          self.result.cleanedNumericMeta().forEach(function (fld) {
            if (fld.name.toLowerCase().indexOf('lat') > -1 || fld.name.toLowerCase().indexOf('ltd') > -1) {
              name = fld.name;
            }
          });
          self.chartX(name);
        }
        if ((self.chartYSingle() === null || typeof self.chartYSingle() === 'undefined')) {
          var name = self.result.cleanedNumericMeta()[1].name;
          self.result.cleanedNumericMeta().forEach(function (fld) {
            if (fld.name.toLowerCase().indexOf('lon') > -1 || fld.name.toLowerCase().indexOf('lng') > -1) {
              name = fld.name;
            }
          });
          self.chartYSingle(name);
        }
        return;
      }

      if ((self.chartX() === null || typeof self.chartX() === 'undefined') && (type == ko.HUE_CHARTS.TYPES.BARCHART || type == ko.HUE_CHARTS.TYPES.PIECHART || type == ko.HUE_CHARTS.TYPES.GRADIENTMAP) && self.result.cleanedStringMeta().length >= 1) {
        self.chartX(self.result.cleanedStringMeta()[0].name);
      }

      if (self.result.cleanedNumericMeta().length > 0) {
        if (self.chartYMulti().length === 0 && (type === ko.HUE_CHARTS.TYPES.BARCHART || type === ko.HUE_CHARTS.TYPES.LINECHART)) {
          self.chartYMulti.push(self.result.cleanedNumericMeta()[Math.min(self.result.cleanedNumericMeta().length - 1, 1)].name);
        } else if ((self.chartYSingle() === null || typeof self.chartYSingle() === 'undefined') && (type === ko.HUE_CHARTS.TYPES.PIECHART || type === ko.HUE_CHARTS.TYPES.MAP || type === ko.HUE_CHARTS.TYPES.GRADIENTMAP || type === ko.HUE_CHARTS.TYPES.SCATTERCHART || (type === ko.HUE_CHARTS.TYPES.BARCHART && self.chartXPivot() !== null))) {
          if (self.chartYMulti().length === 0) {
            self.chartYSingle(self.result.cleanedNumericMeta()[Math.min(self.result.cleanedNumericMeta().length - 1, 1)].name);
          }
          else {
            self.chartYSingle(self.chartYMulti()[0]);
          }
        }
      }
    }

    self.showChart.subscribe(function (val) {
      if (val) {
        self.showGrid(false);
        self.isResultSettingsVisible(true);
        $(document).trigger("forceChartDraw", self);
        huePubSub.publish('editor.chart.shown', self);
        prepopulateChart();
      }
    });
    self.showLogs.subscribe(function (val) {
      huePubSub.publish('redraw.fixed.headers');
      if (val) {
        self.getLogs();
      }
      if (vm.editorMode()) {
        $.totalStorage('hue.editor.showLogs', val);
      }
    });

    self.isLoading = ko.computed(function () {
      return self.status() == "loading";
    });

    self.resultsKlass = ko.computed(function () {
      return "results " + self.type();
    });

    self.errorsKlass = ko.computed(function () {
      return self.resultsKlass() + " alert alert-error";
    });

    self.is_redacted = ko.observable(typeof snippet.is_redacted != "undefined" && snippet.is_redacted != null ? snippet.is_redacted : false);

    self.chartType = ko.observable(typeof snippet.chartType != "undefined" && snippet.chartType != null ? snippet.chartType : ko.HUE_CHARTS.TYPES.BARCHART);
    self.chartType.subscribe(prepopulateChart);
    self.chartSorting = ko.observable(typeof snippet.chartSorting != "undefined" && snippet.chartSorting != null ? snippet.chartSorting : "none");
    self.chartScatterGroup = ko.observable(typeof snippet.chartScatterGroup != "undefined" && snippet.chartScatterGroup != null ? snippet.chartScatterGroup : null);
    self.chartScatterSize = ko.observable(typeof snippet.chartScatterSize != "undefined" && snippet.chartScatterSize != null ? snippet.chartScatterSize : null);
    self.chartScope = ko.observable(typeof snippet.chartScope != "undefined" && snippet.chartScope != null ? snippet.chartScope : "world");
    self.chartTimelineType = ko.observable(typeof snippet.chartTimelineType != "undefined" && snippet.chartTimelineType != null ? snippet.chartTimelineType : "bar");
    self.chartLimits = ko.observableArray([5, 10, 25, 50, 100]);
    self.chartLimit = ko.observable(typeof snippet.chartLimit != "undefined" && snippet.chartLimit != null ? snippet.chartLimit : null);
    self.chartLimit.extend({notify: 'always'});
    self.chartX = ko.observable(typeof snippet.chartX != "undefined" && snippet.chartX != null ? snippet.chartX : null);
    self.chartX.extend({notify: 'always'});
    self.chartXPivot = ko.observable(typeof snippet.chartXPivot != "undefined" && snippet.chartXPivot != null ? snippet.chartXPivot : null);
    self.chartXPivot.extend({notify: 'always'});
    self.chartXPivot.subscribe(prepopulateChart);
    self.chartYSingle = ko.observable(typeof snippet.chartYSingle != "undefined" && snippet.chartYSingle != null ? snippet.chartYSingle : null);
    self.chartYMulti = ko.observableArray(typeof snippet.chartYMulti != "undefined" && snippet.chartYMulti != null ? snippet.chartYMulti : []);
    self.chartData = ko.observableArray(typeof snippet.chartData != "undefined" && snippet.chartData != null ? snippet.chartData : []);
    self.chartMapType = ko.observable(typeof snippet.chartMapType != "undefined" && snippet.chartMapType != null ? snippet.chartMapType : 'marker');
    self.chartMapLabel = ko.observable(typeof snippet.chartMapLabel != "undefined" && snippet.chartMapLabel != null ? snippet.chartMapLabel : null);
    self.chartMapHeat = ko.observable(typeof snippet.chartMapHeat != "undefined" && snippet.chartMapHeat != null ? snippet.chartMapHeat : null);
    self.hideStacked = ko.computed(function() {
      return self.chartYMulti().length <= 1;
    });

    self.hasDataForChart = ko.computed(function () {
      if (self.chartType() == ko.HUE_CHARTS.TYPES.BARCHART || self.chartType() == ko.HUE_CHARTS.TYPES.LINECHART || self.chartType() == ko.HUE_CHARTS.TYPES.TIMELINECHART) {
        return typeof self.chartX() != "undefined" && self.chartX() != null && self.chartYMulti().length > 0;
      }
      return typeof self.chartX() != "undefined" && self.chartX() != null && typeof self.chartYSingle() != "undefined" && self.chartYSingle() != null;
    });

    self.hasDataForChart.subscribe(function(newValue) {
      self.chartX.notifySubscribers();
      self.chartX.valueHasMutated();
    });

    self.chartType.subscribe(function (val) {
      $(document).trigger("forceChartDraw", self);
    });

    self.previousChartOptions = {};

    function guessMetaField(field) {
      var _fld = null;
      if (field) {
        if (self.result.cleanedMeta().length > 0) {
          self.result.cleanedMeta().forEach(function (fld) {
            if (fld.name.toLowerCase() === field.toLowerCase() || field.toLowerCase() === fld.name.toLowerCase()) {
              _fld = fld.name;
            }
          });
        }
      }
      return _fld;
    }

    function guessMetaFields(fields) {
      var _fields = [];
      if (fields) {
        fields.forEach(function (fld) {
          var _field = guessMetaField(fld);
          if (_field) {
            _fields.push(_field);
          }
        });
      }
      return _fields;
    }

    self.result.meta.subscribe(function (newValue) {
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

    self.isResultSettingsVisible = ko.observable(typeof snippet.isResultSettingsVisible != "undefined" && snippet.isResultSettingsVisible != null ? snippet.isResultSettingsVisible : false);
    self.toggleResultSettings = function () {
      self.isResultSettingsVisible(!self.isResultSettingsVisible());
    };
    self.isResultSettingsVisible.subscribe(function(){
      $(document).trigger("toggleResultSettings", self);
    });

    self.settingsVisible = ko.observable(typeof snippet.settingsVisible != "undefined" && snippet.settingsVisible != null ? snippet.settingsVisible : false);
    self.saveResultsModalVisible = ko.observable(false);

    self.checkStatusTimeout = null;

    self.getContext = function() {
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
    self.hasComplexity = ko.pureComputed(function () {
      return self.complexity() && Object.keys(self.complexity()).length > 0;
    });
    self.hasRisks = ko.pureComputed(function () {
      return self.hasComplexity() && self.complexity()['hints'] && self.complexity()['hints'].length > 0;
    });
    self.topRisk = ko.pureComputed(function () {
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
    Object.keys(COMPATIBILITY_SOURCE_PLATFORMS).forEach(function (key) {
      self.compatibilitySourcePlatforms.push(COMPATIBILITY_SOURCE_PLATFORMS[key]);
    });

    self.compatibilitySourcePlatform = ko.observable(COMPATIBILITY_SOURCE_PLATFORMS[self.type()]);
    self.compatibilitySourcePlatform.subscribe(function(newValue) {
      if (newValue && newValue.value !== self.type()) {
        self.hasSuggestion(null);
        self.compatibilityTargetPlatform(COMPATIBILITY_TARGET_PLATFORMS[self.type()]);
        self.queryCompatibility();
      }
    });

    self.compatibilityTargetPlatforms = [];
    Object.keys(COMPATIBILITY_TARGET_PLATFORMS).forEach(function (key) {
      self.compatibilityTargetPlatforms.push(COMPATIBILITY_TARGET_PLATFORMS[key]);
    });
    self.compatibilityTargetPlatform = ko.observable(COMPATIBILITY_TARGET_PLATFORMS[self.type()]);

    self.showOptimizer = ko.observable(self.getApiHelper().getFromTotalStorage('editor', 'show.optimizer', false));
    self.showOptimizer.subscribe(function (newValue) {
      if (newValue !== null) {
        self.getApiHelper().setInTotalStorage('editor', 'show.optimizer', newValue);
      }
    });

    if (HAS_OPTIMIZER && ! vm.isNotificationManager()) {
      var lastComplexityRequest;
      var lastCheckedComplexityStatement;
      var knownResponses = [];

      self.delayedStatement = ko.pureComputed(self.statement).extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 2000 } });

      var handleRiskResponse = function(data) {
        if (data.status == 0) {
          self.hasSuggestion('');
          self.complexity(data.query_complexity);
        } else {
          self.hasSuggestion('error');
          self.complexity({'hints': []});
        }
        huePubSub.publish('editor.active.risks', {
          editor: self.ace(),
          risks: self.complexity() || {}
        });
        lastCheckedComplexityStatement = self.statement();
      };

      var clearActiveRisks = function () {
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

      self.positionStatement.subscribe(function (newStatement) {
        if (newStatement) {
          var hash = newStatement.statement.hashCode();
          var unknownResponse = knownResponses.every(function (knownResponse) {
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

        self.getApiHelper().cancelActiveRequest(lastComplexityRequest);

        hueAnalytics.log('notebook', 'get_query_risk');
        clearActiveRisks();

        var changeSubscription = self.statement.subscribe(function () {
          changeSubscription.dispose();
          self.getApiHelper().cancelActiveRequest(lastComplexityRequest);
        });

        var hash = self.statement().hashCode();

        var unknownResponse = knownResponses.every(function (knownResponse) {
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
              notebook: ko.mapping.toJSON(notebook.getContext()),
              snippet: ko.mapping.toJSON(self.getContext())
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
            always: function(data) {
              changeSubscription.dispose();
            }
          });
        }
      };

      if (self.type() === 'hive' || self.type() === 'impala') {
        if (self.statement_raw()) {
          window.setTimeout(function(){
            self.checkComplexity();
          }, 2000);
        }
        self.delayedStatement.subscribe(function () {
          self.checkComplexity();
        });
      }
    }

    self._ajaxError = function (data, callback) {
      if (data.status == -2) { // Session expired
        var existingSession = notebook.getSession(self.type());
        if (existingSession) {
          notebook.restartSession(existingSession, callback);
        } else {
          notebook.createSession(new Session(vm, {'type': self.type()}), callback);
        }
      } else if (data.status == -3) { // Statement expired
        self.status('expired');
        if (data.message) {
          self.errors.push({message: data.message, help: null, line: null, col: null});
          huePubSub.publish('editor.snippet.result.normal', self);
        }
      } else if (data.status == -4) { // Operation timed out
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
      } else if (data.status == 401) { // Auth required
        self.status('expired');
        $(document).trigger("showAuthModal", {'type': self.type(), 'callback': self.execute});
      } else if (data.status == 1 || data.status == -1) {
        self.status('failed');
        var match = ERROR_REGEX.exec(data.message);
        if (match) {
          var errorLine = parseInt(match[1]);
          var errorCol;
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
            message: data.message.replace(match[0], 'line ' + errorLine + (errorCol !== null ? ':' + errorCol : '')),
            help: null,
            line: errorLine - 1,
            col: errorCol
          })
        } else {
          self.errors.push({
            message: data.message,
            help: data.help,
            line: null,
            col: null
          });
        }
      } else {
        $(document).trigger("error", data.message);
        self.status('failed');
      }
    };

    self.wasBatchExecuted = ko.observable(typeof snippet.wasBatchExecuted != "undefined" && snippet.wasBatchExecuted != null ? snippet.wasBatchExecuted : false);
    self.isReady = ko.computed(function() {
      return (self.statementType() == 'text' && (
          (self.isSqlDialect() && self.statement() !== '') ||
          (['jar', 'java', 'spark2', 'distcp'].indexOf(self.type()) == -1 && self.statement() !== '') ||
          (['jar', 'java'].indexOf(self.type()) != -1 && (self.properties().app_jar() != '' && self.properties().class() != '')) ||
          (['spark2'].indexOf(self.type()) != -1 && self.properties().jars().length > 0) ||
          (['shell'].indexOf(self.type()) != -1 && self.properties().command_path().length > 0) ||
          (['mapreduce'].indexOf(self.type()) != -1 && self.properties().app_jar().length > 0) ||
          (['distcp'].indexOf(self.type()) != -1 && self.properties().source_path().length > 0 && self.properties().destination_path().length > 0))) ||
        (self.statementType() == 'file' && self.statementPath().length > 0) ||
        (self.statementType() == 'document' && self.associatedDocumentUuid() && self.associatedDocumentUuid().length > 0);
    });
    self.lastExecuted = ko.observable(typeof snippet.lastExecuted != "undefined" && snippet.lastExecuted != null ? snippet.lastExecuted : 0);
    self.lastAceSelectionRowOffset = ko.observable(snippet.lastAceSelectionRowOffset || 0);

    self.executingBlockingOperation = null; // A ExecuteStatement()
    self.showLongOperationWarning = ko.observable(false);
    self.showLongOperationWarning.subscribe(function(newValue) {
      if (newValue) {
        hueAnalytics.convert('editor', 'showLongOperationWarning');
      }
    });

    var longOperationTimeout = -1;

    function startLongOperationTimeout() {
      longOperationTimeout = window.setTimeout(function () {
        self.showLongOperationWarning(true);
      }, 2000);
    }

    function stopLongOperationTimeout() {
      window.clearTimeout(longOperationTimeout);
      self.showLongOperationWarning(false);
    }

    self.execute = function (automaticallyTriggered) {
      var now = (new Date()).getTime(); // We don't allow fast clicks
      if (!automaticallyTriggered && (self.status() === 'running' || self.status() === 'loading')) { // Do not cancel statements that are parts of a set of steps to execute (e.g. import). Only cancel statements as requested by user
        self.cancel();
      } else if (now - self.lastExecuted() < 1000 || ! self.isReady()) {
        return;
      }

      if (self.type() === 'impala') {
        huePubSub.publish('assist.clear.execution.analysis');
      }

      self.status('running');
      self.statusForButtons('executing');

      if (self.isSqlDialect()) {
        huePubSub.publish('editor.refresh.statement.locations', self);
      }

      if (self.ace()) {
        huePubSub.publish('ace.set.autoexpand', { autoExpand: false, snippet: self });
        var selectionRange = self.ace().getSelectionRange();
        self.lastAceSelectionRowOffset(Math.min(selectionRange.start.row, selectionRange.end.row));
      }

      self.previousChartOptions = vm._getPreviousChartOptions(self);
      $(document).trigger("executeStarted", {vm: vm, snippet: self});
      self.lastExecuted(now);
      $(".jHueNotify").remove();
      hueAnalytics.log('notebook', 'execute/' + self.type());

      notebook.forceHistoryInitialHeight(true);

      if (self.result.handle()) {
        self.close();
      }

      if (self.isSqlDialect() && self.positionStatement()) {
        self.lastExecutedStatement(self.positionStatement());
      } else {
        self.lastExecutedStatement(null);
      }

      self.errors([]);
      huePubSub.publish('editor.clear.highlighted.errors', self.ace());
      self.result.clear();
      self.progress(0);
      self.jobs([]);
      self.result.logs('');
      self.result.statement_range ({
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

      self.executingBlockingOperation = $.post("/notebook/api/execute/" + self.type(), {
        notebook: vm.editorMode() ? ko.mapping.toJSON(notebook, NOTEBOOK_MAPPING) : ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function (data) {
        self.statusForButtons('executed');
        huePubSub.publish('ace.set.autoexpand', { autoExpand: true, snippet: self });
        stopLongOperationTimeout();

        if (vm.editorMode() && data.history_id) {
          if (! vm.isNotificationManager()) {
            var url = '/notebook/editor' + (vm.isMobile() ? '_m' : '') + '?editor=' + data.history_id;
            if (vm.isHue4()){
              url = vm.URLS.hue4 + '?editor=' + data.history_id;
            }
            vm.changeURL(url);
          }
          notebook.id(data.history_id);
          notebook.uuid(data.history_uuid);
          notebook.isHistory(true);
          notebook.parentSavedQueryUuid(data.history_parent_uuid);
        }

        if (data.status === 0) {
          self.result.handle(data.handle);
          self.result.hasResultset(data.handle.has_result_set);
          if (data.handle.sync) {
            self.loadData(data.result, 100);
            self.status('available');
            self.progress(100);
            self.result.endTime(new Date());
          } else {
            if (! notebook.unloaded()) {
              self.checkStatus();
            }
          }
          if (vm.isOptimizerEnabled()) {
            huePubSub.publish('editor.upload.query', data.history_id);
          }
        } else {
          self._ajaxError(data, self.execute);
          notebook.isExecutingAll(false);
        }

        if (data.handle) {
          if (vm.editorMode()) {
            if (vm.isNotificationManager()) { // Update task status
              var tasks = $.grep(notebook.history(), function(row) { return row.uuid() == notebook.uuid()});
              if (tasks.length === 1) {
                tasks[0].status(self.status());
                self.result.logs(data.message);
              }
            } else {
              notebook.history.unshift(
                notebook._makeHistoryRecord(
                  url,
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

            if (data.handle.statements_count > 1 && data.handle.start != null && data.handle.end != null) {
              self.result.statement_range({
                start: data.handle.start,
                end: data.handle.end
              });
            }
          }
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        if (self.statusForButtons() != 'canceled' && xhr.status !== 502) { // No error when manually canceled
          $(document).trigger("error", xhr.responseText);
        }
        self.status('failed');
        self.statusForButtons('executed');
      }).always(function () {
        self.executingBlockingOperation = null;
      });
    };

    self.reexecute = function () {
      self.result.handle()['statement_id'] = 0;
      self.result.handle()['start'] = {
        row: 0,
        column: 0
      };
      self.result.handle()['end'] = {
        row: 0,
        column: 0
      };
      self.result.handle()['has_more_statements'] = false;
      self.result.handle()['previous_statement_hash'] = '';

      self.execute();
    };

    self.formatEnabled = ko.pureComputed(function () {
      return self.statement_raw && self.statement_raw() != null && self.statement_raw().length < 400000; // ie: 5000 lines at 80 chars per line
    });

    self.format = function () {
      if (self.isSqlDialect()) {
        self.getApiHelper().formatSql({ statements: self.ace().getSelectedText() != '' ? self.ace().getSelectedText() : self.statement_raw() }).done(function (data) {
          if (data.status == 0) {
            if (self.ace().getSelectedText() != '') {
              self.ace().session.replace(self.ace().session.selection.getRange(), data.formatted_statements);
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

      $.post("/notebook/api/explain", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function(data) {
        if (data.status == 0) {
          self.currentQueryTab('queryExplain');
          self.result.fetchedOnce(true);
          self.result.explanation(data.explanation);
        } else {
          self._ajaxError(data);
        }
      });
    };

    var lastCompatibilityRequest;

    self.checkCompatibility = function () {
      self.hasSuggestion(null);
      self.compatibilitySourcePlatform(COMPATIBILITY_SOURCE_PLATFORMS[self.type()]);
      self.compatibilityTargetPlatform(COMPATIBILITY_TARGET_PLATFORMS[self.type() === 'hive' ? 'impala' : 'hive']);
      self.queryCompatibility();
    };

    self.queryCompatibility = function (targetPlatform) {
      self.getApiHelper().cancelActiveRequest(lastCompatibilityRequest);

      hueAnalytics.log('notebook', 'compatibility');
      self.compatibilityCheckRunning(targetPlatform != self.type());
      self.hasSuggestion(null);
      var positionStatement = self.positionStatement();

      lastCompatibilityRequest = $.post("/notebook/api/optimizer/statement/compatibility", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext()),
        sourcePlatform: self.compatibilitySourcePlatform().value,
        targetPlatform: self.compatibilityTargetPlatform().value
      }, function (data) {
        if (data.status === 0) {
          self.aceErrorsHolder([]);
          self.aceWarningsHolder([]);
          self.suggestion(ko.mapping.fromJS(data.query_compatibility));
          if (self.suggestion().queryError && self.suggestion().queryError.errorString()) {
            var match = ERROR_REGEX.exec(self.suggestion().queryError.errorString());
            var line = null;
            if (match) {
              if (positionStatement) {
                line = positionStatement.location.first_line + parseInt(match[1]) + 1;
              } else {
                line = parseInt(match[1]) - 1
              }
            }
            self.aceWarningsHolder.push({
              message: self.suggestion().queryError.errorString(),
              line: line,
              col: match === null ? null : (typeof match[3] !== 'undefined' ? parseInt(match[3]) : null)
            });
            self.status('with-optimizer-report');
          }
          if (self.suggestion().parseError()) {
            var match = ERROR_REGEX.exec(self.suggestion().parseError());
            self.aceErrorsHolder.push({
              message: self.suggestion().parseError(),
              line: match === null ? null : parseInt(match[1]) - 1,
              col: match === null ? null : (typeof match[3] !== 'undefined' ? parseInt(match[3]) : null)
            });
            self.status('with-optimizer-report');
          }
          self.showOptimizer(true);
          self.hasSuggestion(true);
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        if (xhr.status !== 502) {
          $(document).trigger("error", xhr.responseText);
        }
      }).always(function () {
        self.compatibilityCheckRunning(false);
      });
    };

    self.fetchResult = function (rows, startOver) {
      if (typeof startOver == "undefined") {
        startOver = true;
      }
      self.fetchResultData(rows, startOver);
      //self.fetchResultMetadata(rows);
    };

    self.isFetchingData = false;

    self.fetchResultData = function (rows, startOver) {
      if (! self.isFetchingData) {
        if (self.status() === 'available') {
          startLongOperationTimeout();
          self.isFetchingData = true;
          hueAnalytics.log('notebook', 'fetchResult/' + rows + '/' + startOver);
          $.post("/notebook/api/fetch_result_data", {
            notebook: ko.mapping.toJSON(notebook.getContext()),
            snippet: ko.mapping.toJSON(self.getContext()),
            rows: rows,
            startOver: startOver
          }, function (data) {
            stopLongOperationTimeout();
            data = JSON.bigdataParse(data);
            if (data.status === 0) {
              self.loadData(data.result, rows);
            } else {
              self._ajaxError(data, function() {self.isFetchingData = false; self.fetchResultData(rows, startOver); });
              $(document).trigger("renderDataError", {snippet: self});
            }
          }, 'text').fail(function (xhr, textStatus, errorThrown) {
            if (xhr.status !== 502) {
              $(document).trigger("error", xhr.responseText);
            }
          }).always(function () {
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

      var _initialIndex = self.result.data().length;
      var _tempData = [];
      $.each(result.data, function (index, row) {
        row.unshift(_initialIndex + index + 1);
        self.result.data.push(row);
        _tempData.push(row);
      });

      if (self.result.rows() == null || (self.result.rows() + '').indexOf('+') != -1) {
        self.result.rows(self.result.data().length + (result.has_more ? '+' : ''));
      }

      self.result.images(typeof result.images != "undefined" && result.images != null ? result.images : []);

      huePubSub.publish('editor.render.data', {data: _tempData, snippet: self, initial: _initialIndex == 0});

      if (! self.result.fetchedOnce()) {
        result.meta.unshift({type: "INT_TYPE", name: "", comment: null});
        self.result.meta(result.meta);
        self.result.type(result.type);
        self.result.fetchedOnce(true);
      }

      self.result.meta().forEach(function (meta) {
        if ($.inArray(meta.type, ['TINYINT_TYPE', 'SMALLINT_TYPE', 'INT_TYPE', 'BIGINT_TYPE', 'FLOAT_TYPE', 'DOUBLE_TYPE', 'DECIMAL_TYPE']) > -1) {
          meta.cssClass = 'sort-numeric';
        } else if ($.inArray(meta.type, ['TIMESTAMP_TYPE', 'DATE_TYPE', 'DATETIME_TYPE']) > -1) {
          meta.cssClass = 'sort-date';
        } else {
          meta.cssClass = 'sort-string';
        }
      });

      self.result.hasMore(result.has_more);

      if (result.has_more && rows > 0) {
        setTimeout(function () {
          self.fetchResultData(rows, false);
        }, 500);
      } else if (! vm.editorMode() && ! notebook.isPresentationMode() && notebook.snippets()[notebook.snippets().length - 1] == self) {
        notebook.newSnippet();
      }
    };

    self.fetchResultMetadata = function () {
      $.post("/notebook/api/fetch_result_metadata", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function (data) {
        if (data.status == 0) {
          self.result.meta(data.result.meta);
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        if (xhr.status !== 502) {
          $(document).trigger("error", xhr.responseText);
        }
        self.status('failed');
      });
    };

    self.fetchResultSize = function(n, query_id) {
      $.post("/notebook/api/fetch_result_size", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function (data) {
        if (query_id == notebook.id()) { // If still on the same result
          if (data.status == 0) {
            if (data.result.rows != null) {
              self.result.rows(data.result.rows);
            } else if (self.type() == 'impala' && n > 0) {
              setTimeout(function () {
                self.fetchResultSize(n - 1, query_id);
              }, 1000);
            }
          } else if (data.status == 5) {
            // No supported yet for this snippet
          } else {
            //$(document).trigger("error", data.message);
          }
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        //$(document).trigger("error", xhr.responseText);
      });
    };

    self.checkStatus = function () {
      $.post("/notebook/api/check_status", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function (data) {
        if (self.statusForButtons() == 'canceling' || self.status() == 'canceled') {
          // Query was canceled in the meantime, do nothing
        } else {
          self.result.endTime(new Date());

          if (data.status === 0) {
            self.status(data.query_status.status);

            if (self.status() == 'running' || self.status() == 'starting' || self.status() == 'waiting') {
              var delay = self.result.executionTime() > 45000 ? 5000 : 1000; // 5s if more than 45s
              if (! notebook.unloaded()) {
                self.checkStatusTimeout = setTimeout(self.checkStatus, delay);
              }
            } else if (self.status() === 'available') {
              if (self.type() === 'impala' && self.compute() && self.compute().crn && self.compute().crn.indexOf('altus') !== -1) {

                // TODO: Use real query ID
                huePubSub.publish('assist.update.execution.analysis', {
                  compute: self.compute(),
                  queryId: '56433486cd84d475:3a86f97000000000'
                });

              }
              self.fetchResult(100);
              self.progress(100);
              if (self.isSqlDialect()) {
                if (self.result.handle().has_result_set) {
                  var _query_id = notebook.id();
                  setTimeout(function () { // Delay until we get IMPALA-5555
                    self.fetchResultSize(10, _query_id);
                  }, 2000);
                  self.checkDdlNotification(); // DDL CTAS with Impala
                } else {
                  // Is DDL
                  if (self.lastExecutedStatement()) {
                    self.checkDdlNotification();
                  } else {
                    self.onDdlExecute();
                  }
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
              if (! self.result.handle().has_more_statements && vm.successUrl()) {
                window.location.href = vm.successUrl(); // Not used anymore in Hue 4
              }
            } else if (self.status() === 'success') {
              self.progress(99);
            }
          } else if (data.status === -3) {
            self.status('expired');
            notebook.isExecutingAll(false);
          } else {
            self._ajaxError(data);
            notebook.isExecutingAll(false);
          }
          self.getLogs(); // Need to execute at the end, because updating the status impacts log progress results
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        if (xhr.status !== 502) {
          $(document).trigger("error", xhr.responseText || textStatus);
        }
        self.status('failed');
        notebook.isExecutingAll(false);
      });
    };

    self.checkDdlNotification = function() {
      if (self.lastExecutedStatement() && /CREATE|DROP|ALTER/i.test(self.lastExecutedStatement().firstToken)) {
        self.onDdlExecute();
      }
    };

    self.isCanceling = ko.observable(false);

    self.cancel = function () {
      self.isCanceling(true);
      if (self.checkStatusTimeout != null) {
        clearTimeout(self.checkStatusTimeout);
        self.checkStatusTimeout = null;
      }
      hueAnalytics.log('notebook', 'cancel');

      if ($.isEmptyObject(self.result.handle())) { // Query was not even submitted yet
        if (self.executingBlockingOperation != null) {
          self.executingBlockingOperation.abort();
          self.executingBlockingOperation = null;
        }
        self.statusForButtons('canceled');
        self.status('failed');
        self.isCanceling(false);
        notebook.isExecutingAll(false);
      } else {
        self.statusForButtons('canceling');
        $.post("/notebook/api/cancel_statement", {
          notebook: ko.mapping.toJSON(notebook.getContext()),
          snippet: ko.mapping.toJSON(self.getContext())
        }, function (data) {
          self.statusForButtons('canceled');
          if (data.status == 0) {
            self.status('canceled');
            notebook.isExecutingAll(false);
          } else {
            self._ajaxError(data);
          }
        }).fail(function (xhr, textStatus, errorThrown) {
          if (xhr.status !== 502) {
            $(document).trigger("error", xhr.responseText);
          }
          self.statusForButtons('canceled');
          self.status('failed');
          notebook.isExecutingAll(false);
        }).always(function (){
          self.isCanceling(false);
        });
      }
    };

    self.close = function () {
      if (self.checkStatusTimeout != null) {
        clearTimeout(self.checkStatusTimeout);
        self.checkStatusTimeout = null;
      }

      $.post("/notebook/api/close_statement", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function (data) {
        if (data.status == 0) {
          // self.status('closed'); // Keep as 'running' as currently it happens before running a new query
        } else {
          // self._ajaxError(data);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        if (xhr.status !== 502) {
          // $(document).trigger("error", xhr.responseText);
        }
        // self.status('failed'); // Can conflict with slow close and new query execution
      });
    };

    self.getLogs = function () {
      $.post("/notebook/api/get_logs", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext()),
        from: self.result.logLines,
        jobs: ko.mapping.toJSON(self.jobs, { ignore: ['percentJob'] }),
        full_log: self.result.logs
      }, function (data) {
        if (data.status == 1) { // Append errors to the logs
          data.status = 0;
          data.logs = data.message;
        }
        if (data.status == 0) {
          if (data.logs.length > 0) {
            var logs = data.logs.split("\n");
            self.result.logLines += logs.length;
            var oldLogs = self.result.logs();
            if (data.logs && (
                oldLogs === "" || (self.wasBatchExecuted() && data.logs.indexOf('Unable to locate') == -1) || data.isFullLogs)) {
              self.result.logs(data.logs);
            } else {
              self.result.logs(oldLogs + "\n" + data.logs);
            }
          }

          self.jobs().forEach(function(job){
            if (typeof job.percentJob === 'undefined'){
              job.percentJob = ko.observable(-1);
            }
          });

          if (data.jobs && data.jobs.length > 0) {
            data.jobs.forEach(function (job) {
              var _found = ko.utils.arrayFilter(self.jobs(), function (item) {
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
                for (var i = 0; i < _found.length; i++) {
                  _found[i].percentJob(job.percentJob)
                }
              }
            });
            self.jobs().forEach(function (job) {
              var _found = ko.utils.arrayFilter(self.jobs(), function (item) {
                return item.name === job.name;
              });
              if (_found.length === 0) {
                self.jobs.remove(job);
              }
            });
          }
          if (self.status() == 'running') { // Maybe the query finished or failed in the meantime
            self.progress(data.progress)
          };
        } else {
          self._ajaxError(data);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        if (xhr.status !== 502) {
          $(document).trigger("error", xhr.responseText || textStatus);
        }
        self.status('failed');
      });
    };

    self.uploadQueryHistory = function (n) {
      hueAnalytics.log('notebook', 'upload_query_history');

      $.post("/metadata/api/optimizer/upload/history", {
        n: typeof n != "undefined" ? n : null,
        sourcePlatform: self.type()
      }, function(data) {
        if (data.status == 0) {
          $(document).trigger("info", data.upload_history[self.type()].count + " queries uploaded successfully. Processing them...");
          self.watchUploadStatus(data.upload_history[self.type()].status.workloadId);
        } else {
          $(document).trigger("error", data.message);
        }
      });
    };

    self.uploadQuery = function (query_id) {
      $.post("/metadata/api/optimizer/upload/query", {
        query_id: query_id,
        sourcePlatform: self.type()
      });
    };

    self.uploadTableStats = function (options) {
      hueAnalytics.log('notebook', 'load_table_stats');
      if (options.showProgress) {
        $(document).trigger("info", "Preparing table data...");
      }

      $.post("/metadata/api/optimizer/upload/table_stats", {
        db_tables: ko.mapping.toJSON($.map(options.activeTables, function(table) {
          return table.databaseName + '.' + table.tableName;
        })),
        sourcePlatform: ko.mapping.toJSON(self.type()),
        with_ddl: ko.mapping.toJSON(true),
        with_table_stats: ko.mapping.toJSON(true),
        with_columns_stats: ko.mapping.toJSON(true)
      }, function(data) {
        if (data.status == 0) {
          if (options.showProgress) {
            $(document).trigger("info", $.map(options.activeTables, function(table) { return table.tableName; }) + " stats sent to analyse");
          }
          if (data.upload_table_ddl && options.showProgress) { // With showProgress only currently as can be very slow
            self.watchUploadStatus(data.upload_table_ddl.status.workloadId, options.showProgress);
          }
        } else {
          if (options.showProgress) {
            $(document).trigger("error", data.message);
          }
        }
      }).always(function () {
        if (options.callback) {
          options.callback();
        }
      });
    };

    self.watchUploadStatus = function (workloadId, showProgress) {
      $.post("/metadata/api/optimizer/upload/status", {
        workloadId: workloadId
      }, function(data) {
        if (data.status == 0) {
          if (showProgress) {
            $(document).trigger("info", "Query processing: " + data.upload_status.status.state);
          }
          if (['WAITING', 'IN_PROGRESS'].indexOf(data.upload_status.status.state) != -1) {
            window.setTimeout(function () {
              self.watchUploadStatus(workloadId);
            }, 2000);
          } else {
            if (showProgress) {
              $(document).trigger("warn", data.upload_status.status.statusMsg + (data.upload_status.status.failedQueries > 0 ? '. ' + data.upload_status.status.failQueryDetails.map(function(query) { return query.error; }) : ''));
            }
          }
        } else {
          if (showProgress) {
            $(document).trigger("error", data.message);
          }
        }
      });
    };

    self.getSimilarQueries = function () {
      hueAnalytics.log('notebook', 'get_query_similarity');

      $.post("/notebook/api/optimizer/statement/similarity", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext()),
        sourcePlatform: self.type()
      }, function(data) {
        if (data.status == 0) {
          console.log(data.statement_similarity);
        } else {
          $(document).trigger("error", data.message);
        }
      });
    };

    self.autocompleter = new Autocompleter({
      snippet: self,
      user: vm.user,
      optEnabled: false,
      timeout: vm.autocompleteTimeout,
      useNewAutocompleter: vm.useNewAutocompleter
    });

    self.init = function () {
      if ((self.status() == 'running' || self.status() == 'available') && notebook.isHistory()) {
        self.checkStatus();
      }
      else if (self.status() == 'loading') {
        self.status('failed');
        self.progress(0);
        self.jobs([]);
      }
      else if (self.status() == 'ready-execute') {
        self.execute();
      }
    };

    self.onKeydownInVariable = function (context, e) {
      if ((e.ctrlKey || e.metaKey) && e.which === 13) { // Ctrl-enter
        self.ace().commands.commands['execute'].exec();
      } else if ((e.ctrlKey || e.metaKey) && e.which === 83) { // Ctrl-s
        self.ace().commands.commands['save'].exec();
        e.preventDefault(); // Prevent browser page save dialog
      }
      return true;
    };
  };

  var Session = function(vm, session) {
    var self = this;
    ko.mapping.fromJS(session, {}, self);

    self.selectedSessionProperty = ko.observable('');

    self.restarting = ko.observable(false);

    if (! ko.isObservable(self.properties)) {
      self.properties = ko.observableArray();
    }

    self.availableNewProperties = ko.computed(function() {
      var addedIndex = {};
      $.each(self.properties(), function(index, property) {
        addedIndex[property.key] = true;
      });
      var result = $.grep(vm.availableSessionProperties(), function(property) {
        return ! addedIndex[property.name];
      });
      return result;
    });
  };

  var Notebook = function (vm, notebook) {
    var self = this;

    self.id = ko.observable(typeof notebook.id != "undefined" && notebook.id != null ? notebook.id : null);
    self.uuid = ko.observable(typeof notebook.uuid != "undefined" && notebook.uuid != null ? notebook.uuid : UUID());
    self.name = ko.observable(typeof notebook.name != "undefined" && notebook.name != null ? notebook.name : 'My Notebook');
    self.description = ko.observable(typeof notebook.description != "undefined" && notebook.description != null ? notebook.description: '');
    self.type = ko.observable(typeof notebook.type != "undefined" && notebook.type != null ? notebook.type : 'notebook');
    self.initialType = self.type().replace('query-', '');
    self.coordinatorUuid = ko.observable(typeof notebook.coordinatorUuid != "undefined" && notebook.coordinatorUuid != null ? notebook.coordinatorUuid : null);
    self.isHistory = ko.observable(typeof notebook.is_history != "undefined" && notebook.is_history != null ? notebook.is_history : false);
    self.isManaged = ko.observable(typeof notebook.isManaged != "undefined" && notebook.isManaged != null ? notebook.isManaged : false);
    self.parentSavedQueryUuid = ko.observable(typeof notebook.parentSavedQueryUuid != "undefined" && notebook.parentSavedQueryUuid != null ? notebook.parentSavedQueryUuid : null); // History parent
    self.isSaved = ko.observable(typeof notebook.isSaved != "undefined" && notebook.isSaved != null ? notebook.isSaved : false);
    self.canWrite = ko.observable(typeof notebook.can_write != "undefined" && notebook.can_write != null ? notebook.can_write : true);
    self.onSuccessUrl = ko.observable(typeof notebook.onSuccessUrl != "undefined" && notebook.onSuccessUrl != null ? notebook.onSuccessUrl : null);
    self.pubSubUrl = ko.observable(typeof notebook.pubSubUrl != "undefined" && notebook.pubSubUrl != null ? notebook.pubSubUrl : null);
    self.isPresentationModeDefault = ko.observable(typeof notebook.isPresentationModeDefault != "undefined" && notebook.isPresentationModeDefault != null ? notebook.isPresentationModeDefault : false);
    self.isPresentationMode = ko.observable(false);
    self.isPresentationModeInitialized = ko.observable(false);
    self.isPresentationMode.subscribe(function(newValue) {
      if (! newValue) {
        self.cancelExecutingAll();
      }
      huePubSub.publish('editor.presentation.operate.toggle', newValue); // Problem with headers / row numbers redraw on full screen results
      vm.togglePresentationMode();
      if (newValue) {
        hueAnalytics.convert('editor', 'presentation');
      }
    });
    self.presentationSnippets = ko.observable({});
    self.isHidingCode = ko.observable(typeof notebook.isHidingCode != "undefined" && notebook.isHidingCode != null ? notebook.isHidingCode : false);

    self.snippets = ko.observableArray();
    self.selectedSnippet = ko.observable(vm.editorType()); // Aka selectedSnippetType
    self.creatingSessionLocks = ko.observableArray();
    self.sessions = ko.mapping.fromJS(typeof notebook.sessions != "undefined" && notebook.sessions != null ? notebook.sessions : [], {
      create: function(value) {
        return new Session(vm, value.data);
      }
    });
    self.directoryUuid = ko.observable(typeof notebook.directoryUuid != "undefined" && notebook.directoryUuid != null ? notebook.directoryUuid : null);
    self.dependents = ko.mapping.fromJS(typeof notebook.dependents != "undefined" && notebook.dependents != null ? notebook.dependents : []);
    self.dependentsCoordinator = ko.computed(function() {
      return $.grep(self.dependents(), function(doc) { return doc.type() == 'oozie-coordinator2' && doc.is_managed() == true ;})
    });
    if (self.dependentsCoordinator().length > 0 && ! self.coordinatorUuid()) {
      self.coordinatorUuid(self.dependentsCoordinator()[0].uuid());
    }
    self.history = ko.observableArray(vm.selectedNotebook() && vm.selectedNotebook().history().length > 0 && vm.selectedNotebook().history()[0].type == self.type() ? vm.selectedNotebook().history() : []);
    self.history.subscribe(function(val) {
      if (self.id() == null && val.length == 0 && self.historyFilter() === '' && ! vm.isNotificationManager()) {
        self.snippets()[0].currentQueryTab((typeof IS_EMBEDDED !== 'undefined' && IS_EMBEDDED) ? 'queryHistory' : 'savedQueries');
      }
    });
    self.historyFilter = ko.observable('');
    self.historyFilterVisible = ko.observable(false);
    self.historyFilter.extend({ rateLimit: { method: "notifyWhenChangesStop", timeout: 900 } });
    self.historyFilter.subscribe(function(val){
      if (self.historyCurrentPage() != 1) {
        self.historyCurrentPage(1);
      } else {
        self.fetchHistory();
      }
    });
    self.loadingHistory = ko.observable(self.history().length == 0);
    self.historyInitialHeight = ko.observable(0).extend({ throttle: 1000 });
    self.forceHistoryInitialHeight = ko.observable(false);
    self.historyCurrentPage = ko.observable(vm.selectedNotebook() ? vm.selectedNotebook().historyCurrentPage() : 1);
    self.historyCurrentPage.subscribe(function(val) {
      self.fetchHistory();
    });
    self.historyTotalPages = ko.observable(vm.selectedNotebook() ? vm.selectedNotebook().historyTotalPages() : 1);

    self.schedulerViewModel = null;
    self.schedulerViewModelIsLoaded = ko.observable(false);
    self.schedulerViewerViewModel = ko.observable();
    self.isBatchable = ko.computed(function() {
      return self.snippets().length > 0
        && $.grep(self.snippets(), function (snippet) {
          return snippet.isBatchable();
        }).length == self.snippets().length;
    });

    self.isExecutingAll = ko.observable(!! notebook.isExecutingAll);
    self.cancelExecutingAll = function() {
      var index = self.executingAllIndex();
      if (self.isExecutingAll() && self.snippets()[index]) {
        self.snippets()[index].cancel();
      }
    };
    self.executingAllIndex = ko.observable(notebook.executingAllIndex || 0);

    self.retryModalConfirm = null;
    self.retryModalCancel = null;

    self.avoidClosing = false;

    self.canSave = vm.canSave;


    self.getSession = function (session_type) {
      var _s = null;
      $.each(self.sessions(), function (index, s) {
        if (s.type() == session_type) {
          _s = s;
          return false;
        }
      });
      return _s;
    };

    self.getSnippets = function(type) {
      return $.grep(self.snippets(), function (snippet) {
        return snippet.type() == type;
      });
    };

    self.unloaded = ko.observable(false);
    self.unload = function() {
      self.unloaded(true);
      var currentQueries = null;
      self.snippets().forEach(function(snippet){
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

    self.restartSession = function (session, callback) {
      if (session.restarting()) {
        return;
      }
      session.restarting(true);
      var snippets = self.getSnippets(session.type());

      $.each(snippets, function(index, snippet) {
        snippet.status('loading');
      });

      var sessionJson = ko.mapping.toJSON(session);

      self.closeSession (session, true, function() {
        self.createSession(session, function () {
          $.each(snippets, function(index, snippet) {
            snippet.status('ready');
          });
          session.restarting(false);
          if (callback) {
            callback();
          }
        }, function () {
          session.restarting(false);
        });
      });
    };

    self.addSession = function (session) {
      var toRemove = [];
      $.each(self.sessions(), function (index, s) {
        if (s.type() == session.type()) {
          toRemove.push(s);
        }
      });

      $.each(toRemove, function (index, s) {
        self.sessions.remove(s);
      });

      self.sessions.push(session);
    };

    self.addSnippet = function (snippet, skipSession) {
      var _snippet = new Snippet(vm, self, snippet);
      self.snippets.push(_snippet);

      if (self.getSession(_snippet.type()) == null && typeof skipSession == "undefined") {
        window.setTimeout(function() {
          _snippet.status('loading');
          self.createSession(new Session(vm, {'type': _snippet.type()}));
        }, 200);
      }

      _snippet.init();
      return _snippet;
    };

    self.createSession = function (session, callback, failCallback) {
      if (self.creatingSessionLocks().indexOf(session.type()) != -1) { // Create one type of session max
        return;
      } else {
        self.creatingSessionLocks.push(session.type());
      }

      $.each(self.getSnippets(session.type()), function(index, snippet) {
        snippet.status('loading');
      });

      var fail = function (message) {
        $.each(self.getSnippets(session.type()), function(index, snippet) {
          snippet.status('failed');
        });
        $(document).trigger("error", message);
        if (failCallback) {
          failCallback();
        }
      };

      $.post("/notebook/api/create_session", {
        notebook: ko.mapping.toJSON(self.getContext()),
        session: ko.mapping.toJSON(session) // e.g. {'type': 'pyspark', 'properties': [{'name': driverCores', 'value', '2'}]}
      }, function (data) {
        if (data.status == 0) {
          ko.mapping.fromJS(data.session, {}, session);
          if (self.getSession(session.type()) == null) {
            self.addSession(session);
          }
          $.each(self.getSnippets(session.type()), function(index, snippet) {
            snippet.status('ready');
          });
          if (callback) {
            setTimeout(callback, 500);
          }
        } else if (data.status == 401) {
          $(document).trigger("showAuthModal", {'type': session.type()});
        }
        else {
          fail(data.message);
        }
      }).fail(function (xhr) {
        if (xhr.status !== 502) {
          fail(xhr.responseText);
        }
      }).complete(function(xhr, status) {
        self.creatingSessionLocks.remove(session.type());
      })
    };

    self.authSession = function () {
      self.createSession(new Session(vm, {
          'type': vm.authSessionType(),
          'properties': [
            {'name': 'user', 'value': vm.authSessionUsername()},
            {'name': 'password', 'value': vm.authSessionPassword()}
          ]
        }),
        vm.authSessionCallback()  // On new session we don't automatically execute the snippet after the aut. On session expiration we do or we refresh assist DB when login-in.
      );
    };

    self.newSnippet = function (type) {
      if (type) {
        self.selectedSnippet(type);
      }
      var snippet = self.addSnippet({
        type: self.selectedSnippet(),
        result: {}
      });

      window.setTimeout(function () {
        var lastSnippet = snippet;
        if (lastSnippet.ace() != null) {
          lastSnippet.ace().focus();
        }
      }, 100);

      hueAnalytics.log('notebook', 'add_snippet/' + (type ? type : self.selectedSnippet()));
      return snippet;
    };

    self.newSnippetAbove = function (id) {
      self.newSnippet();
      var idx = 0;
      self.snippets().forEach(function (snippet, cnt) {
        if (snippet.id() == id) idx = cnt;
      });
      self.snippets(self.snippets().move(self.snippets().length - 1, idx));
    };

    self.getContext = function() {
     return {
         id: self.id,
         uuid: self.uuid,
         parentSavedQueryUuid: self.parentSavedQueryUuid,
         isSaved: self.isSaved,
         sessions: self.sessions,
         type: self.type,
         name: self.name
      };
    };

    self.save = function (callback) {
      hueAnalytics.log('notebook', 'save');

      // Remove the result data from the snippets
      // Also do it for presentation mode
      var cp = ko.mapping.toJS(self, NOTEBOOK_MAPPING);
      $.each(cp.snippets.concat(Object.keys(cp.presentationSnippets).map(function(key){
          return cp.presentationSnippets[key];
        })), function(index, snippet) {
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
      var editorMode = vm.editorMode() || (self.isPresentationMode() && vm.editorType() != 'notebook'); // Editor should not convert to Notebook in presentation mode

      $.post("/notebook/api/notebook/save", {
        "notebook": ko.mapping.toJSON(cp, NOTEBOOK_MAPPING),
        "editorMode": editorMode
      }, function (data) {
        if (data.status == 0) {
          self.id(data.id);
          self.isSaved(true);
          var wasHistory = self.isHistory();
          self.isHistory(false);
          $(document).trigger("info", data.message);
          if (editorMode) {
            if (! data.save_as) {
              var existingQuery = self.snippets()[0].queries().filter(function (item) {
                return item.uuid() === data.uuid
              });
              if (existingQuery.length > 0) {
                existingQuery[0].name(data.name);
                existingQuery[0].description(data.description);
                existingQuery[0].last_modified(data.last_modified);
              }
            } else if (self.snippets()[0].queries().length > 0) { // Saved queries tab already loaded
              self.snippets()[0].queries.unshift(ko.mapping.fromJS(data));
            }

            if (self.coordinatorUuid() && self.schedulerViewModel) {
              self.saveScheduler();
              self.schedulerViewModel.coordinator.refreshParameters();
            }
            if (wasHistory || data.save_as) {
              self.loadScheduler();
            }

            if (self.snippets()[0].downloadResultViewModel && self.snippets()[0].downloadResultViewModel().saveTarget() === 'dashboard') {
              huePubSub.publish('open.link', vm.URLS.report + '&uuid=' + data.uuid + '&statement=' + self.snippets()[0].result.handle().statement_id);
            }
            else {
              if (vm.isHue4()){
                vm.changeURL(vm.URLS.hue4 + '?editor=' + data.id);
              } else {
                vm.changeURL('/notebook/editor' + (vm.isMobile() ? '_m' : '') + '?editor=' + data.id);
              }
            }
          } else {
            if (vm.isHue4()){
              vm.changeURL(vm.URLS.hue4_notebook + '?notebook=' + data.id);
            } else {
              vm.changeURL('/notebook/notebook?notebook=' + data.id);
            }
          }
          if (typeof callback == "function") {
            callback();
          }
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        if (xhr.status !== 502) {
          $(document).trigger("error", xhr.responseText);
        }
      });
    };

    self.close = function () {
      hueAnalytics.log('notebook', 'close');
      $.post("/notebook/api/notebook/close", {
        "notebook": ko.mapping.toJSON(self, NOTEBOOK_MAPPING),
        "editorMode": vm.editorMode()
      });
    };

    self.clearResults = function () {
      $.each(self.snippets(), function (index, snippet) {
        snippet.result.clear();
        snippet.status('ready');
      });
    };

    self.executeAll = function () {
      if (self.isExecutingAll() || self.snippets().length === 0) {
        return;
      }

      self.isExecutingAll(true);
      self.executingAllIndex(0);

      self.snippets()[self.executingAllIndex()].execute();
    };

    self.saveDefaultUserProperties = function (session) {
      var apiHelper = ApiHelper.getInstance();
      apiHelper.saveConfiguration({
        app: session.type(),
        properties: session.properties,
        userId: vm.userId
      });
    };

    self.closeAndRemoveSession = function (session) {
      self.closeSession(session, false, function() {
        self.sessions.remove(session);
      });
    };

    self.closeSession = function (session, silent, callback) {
      $.post("/notebook/api/close_session", {
        session: ko.mapping.toJSON(session)
      }, function (data) {
        if (! silent && data && data.status != 0 && data.status != -2 && data.message) {
          $(document).trigger("error", data.message);
        }

        if (callback) {
          callback();
        }
      }).fail(function (xhr) {
        if (!silent && xhr.status !== 502) {
          $(document).trigger("error", xhr.responseText);
        }
      });
    };

    self.fetchHistory = function (callback) {
      var QUERIES_PER_PAGE = 50;
      self.loadingHistory(true);

      $.get("/notebook/api/get_history", {
        doc_type: self.selectedSnippet(),
        limit: QUERIES_PER_PAGE,
        page: self.historyCurrentPage(),
        doc_text: self.historyFilter(),
        is_notification_manager: vm.isNotificationManager()
      }, function(data) {
        var parsedHistory = [];
        if (data && data.history){
          data.history.forEach(function(nbk){
            parsedHistory.push(
              self._makeHistoryRecord(
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
      }).always(function(){
        self.loadingHistory(false);
        if (callback) {
          callback();
        }
      });
    };

    self.prevHistoryPage = function () {
      if (self.historyCurrentPage() !== 1) {
        self.historyCurrentPage(self.historyCurrentPage() - 1);
      }
    };

    self.nextHistoryPage = function () {
      if (self.historyCurrentPage() < self.historyTotalPages()) {
        self.historyCurrentPage(self.historyCurrentPage() + 1);
      }
    };


    self.updateHistoryFailed = false;
    self.updateHistory = function (statuses, interval) {
      var items = $.grep(self.history(), function (item) {
        return statuses.indexOf(item.status()) != -1;
      }).slice(0, 25);

      function updateHistoryCall(item) {
        $.post("/notebook/api/check_status", {
          notebook: ko.mapping.toJSON({id: item.uuid()}),
        }).done(function (data) {
            var status = data.status == -3 ? 'expired' : (data.status == 0 ? data.query_status.status : 'failed');
            if (status && item.status() != status) {
              item.status(status);
            }
          }).fail(function (xhr) {
            items = [];
            self.updateHistoryFailed = true;
            console.warn('Lost connectivity to the Hue history refresh backend.');
          }).always(function () {
            if (items.length > 0) {
              window.setTimeout(function () {
                updateHistoryCall(items.pop());
              }, 1000);
            } else {
              if (!self.updateHistoryFailed){
                window.setTimeout(function () {
                  self.updateHistory(statuses, interval);
                }, interval);
              }
            }
          });
      }

      if (items.length > 0) {
        updateHistoryCall(items.pop());
      } else {
        if (!self.updateHistoryFailed) {
          window.setTimeout(function () {
            self.updateHistory(statuses, interval);
          }, interval);
        }
      }
    };

    self._makeHistoryRecord = function(url, statement, lastExecuted, status, name, uuid) {
      return ko.mapping.fromJS({
          url: url,
          query: statement.substring(0, 1000) + (statement.length > 1000 ? '...' : ''),
          lastExecuted: lastExecuted,
          status: status,
          name: name,
          uuid: uuid
      });
    };

    self.clearHistory = function (type) {
      hueAnalytics.log('notebook', 'clearHistory');
      $.post("/notebook/api/clear_history", {
        notebook: ko.mapping.toJSON(self.getContext()),
        doc_type: self.selectedSnippet(),
        is_notification_manager: vm.isNotificationManager(),
      }, function (data) {
        self.history.removeAll();
        if (self.isHistory()) {
          self.id(null);
          self.uuid(UUID());
          if (vm.isHue4()) {
            vm.changeURL(vm.URLS.hue4 + '?type=' + vm.editorType());
          }
          else {
            vm.changeURL('/notebook/editor' + (vm.isMobile() ? '_m' : '') + '?type=' + vm.editorType());
          }
        }
      }).fail(function (xhr) {
        if (xhr.status !== 502) {
          $(document).trigger("error", xhr.responseText);
        }
      });
      $(document).trigger("hideHistoryModal");
    };

    self.loadScheduler = function () {
      if (typeof vm.CoordinatorEditorViewModel !== 'undefined' && self.isBatchable()) {
        var _action;
        if (self.coordinatorUuid()) {
          _action = 'edit';
        } else {
          _action = 'new';
        }
        hueAnalytics.log('notebook', 'schedule/' + _action);

        function getCoordinator() {
          $.get('/oozie/editor/coordinator/' + _action + '/', {
            format: 'json',
            document: self.uuid(),
            coordinator: self.coordinatorUuid()
          }, function (data) {
            if ($("#schedulerEditor").length > 0) {
              huePubSub.publish('hue4.process.headers', {
                response: data.layout,
                callback: function (r) {
                  $("#schedulerEditor").html(r);

                  self.schedulerViewModel = new vm.CoordinatorEditorViewModel(data.coordinator, data.credentials, data.workflows, data.can_edit);

                  ko.cleanNode($("#schedulerEditor")[0]);
                  ko.applyBindings(self.schedulerViewModel, $("#schedulerEditor")[0]);
                  $(document).off("showSubmitPopup");
                  $(document).on("showSubmitPopup", function (event, data) {
                    $('.submit-modal-editor').html(data);
                    $('.submit-modal-editor').modal('show');
                    $('.submit-modal-editor').on('hidden', function () {
                      huePubSub.publish('hide.datepicker');
                    });
                    var _sel = $('.submit-form .control-group[rel!="popover"]:visible');
                    if (_sel.length > 0) {
                      $('.submit-modal-editor .modal-body').height($('.submit-modal-editor .modal-body').height() + 60);
                    }
                  });

                  huePubSub.publish('render.jqcron');

                  self.schedulerViewModel.coordinator.properties.cron_advanced.valueHasMutated(); // Update jsCron enabled status
                  self.schedulerViewModel.coordinator.tracker().markCurrentStateAsClean();
                  self.schedulerViewModel.isEditing(true);

                  self.schedulerViewModelIsLoaded(true);

                  if (_action == 'new') {
                    self.schedulerViewModel.coordinator.properties.document(self.uuid()); // Expected for triggering the display
                  }
                }
              });

            }
          }).fail(function (xhr) {
            if (xhr.status !== 502) {
              $(document).trigger("error", xhr.responseText);
            }
          });
        }

        if (!IS_HUE_4) {
          huePubSub.subscribe('hue4.process.headers', function (opts) {
            opts.callback(opts.response);
          }, vm.huePubSubId);
        }

        getCoordinator();
      }
    };

    self.saveScheduler = function() {
      if (self.isBatchable() && (! self.coordinatorUuid() || self.schedulerViewModel.coordinator.isDirty())) {
        self.schedulerViewModel.coordinator.isManaged(true);
        self.schedulerViewModel.coordinator.properties.document(self.uuid());
        self.schedulerViewModel.save(function(data) {
          if (! self.coordinatorUuid()) {
            self.coordinatorUuid(data.uuid);
            self.save();
          }
        });
      }
    };

    self.showSubmitPopup = function () {
      $.get('/oozie/editor/coordinator/submit/' + self.coordinatorUuid(), {
        format: 'json'
      }, function (data) {
        $(document).trigger("showSubmitPopup", data);
      }).fail(function (xhr, textStatus, errorThrown) {
        if (xhr.status !== 502) {
          $(document).trigger("error", xhr.responseText);
        }
      });
    };

    self.viewSchedulerId = ko.observable(typeof notebook.viewSchedulerId != "undefined" && notebook.viewSchedulerId != null ? notebook.viewSchedulerId : '');
    self.viewSchedulerId.subscribe(function(newVal) {
      self.save();
    });
    self.isSchedulerJobRunning = ko.observable();
    self.loadingScheduler = ko.observable(false);


    // Init
    if (notebook.snippets) {
      $.each(notebook.snippets, function (index, snippet) {
        self.addSnippet(snippet);
      });
      if (typeof notebook.presentationSnippets != "undefined" && notebook.presentationSnippets != null) { // Load
        $.each(notebook.presentationSnippets, function(key, snippet) {
          snippet.status = 'ready' // Protect from storm of check_statuses
          var _snippet = new Snippet(vm, self, snippet);
          _snippet.init();
          _snippet.previousChartOptions = vm._getPreviousChartOptions(_snippet);
          self.presentationSnippets()[key] = _snippet;
        });
      }
      if (vm.editorMode() && self.history().length == 0) {
        self.fetchHistory(function() {
          self.updateHistory(['starting', 'running'], 30000);
          self.updateHistory(['available'], 60000 * 5);
        });
      }
    }

    huePubSub.subscribeOnce('assist.db.panel.ready', function () {
      if (self.type().indexOf('query') === 0) {

        var whenDatabaseAvailable = function (snippet) {
          huePubSub.publish('assist.set.database', {
            source: snippet.type(),
            namespace: snippet.namespace(),
            name: snippet.database()
          });
        };

        var whenNamespaceAvailable = function (snippet) {
          if (snippet.database()) {
            whenDatabaseAvailable(snippet);
          } else {
            var databaseSub = snippet.database.subscribe(function () {
              databaseSub.dispose();
              whenDatabaseAvailable(snippet);
            })
          }
        };

        var whenSnippetAvailable = function (snippet) {
          if (snippet.namespace()) {
            whenNamespaceAvailable(snippet);
          } else {
            var namespaceSub = snippet.namespace.subscribe(function () {
              namespaceSub.dispose();
              whenNamespaceAvailable(snippet);
            })
          }
        };

        if (self.snippets().length === 1) {
          whenSnippetAvailable(self.snippets()[0]);
        } else {
          var snippetsSub = self.snippets.subscribe(function (snippets) {
            if (snippets.length === 1) {
              whenSnippetAvailable(snippets[0])
            }
            snippetsSub.dispose();
          })
        }
      }
    }, vm.huePubSubId);

    huePubSub.publish('assist.is.db.panel.ready');
  };

  function EditorViewModel(editor_id, notebooks, options, CoordinatorEditorViewModel, RunningCoordinatorModel) {
    var self = this;

    self.URLS = {
      editor: '/notebook/editor',
      editorMobile: '/notebook/editor_m',
      notebook: '/notebook/notebook',
      hue4: '/hue/editor',
      hue4_notebook: '/hue/notebook',
      report: '/hue/dashboard/new_search?engine=report'
    };

    self.huePubSubId = options.huePubSubId || 'editor';
    self.user = options.user;
    self.userId = options.userId;
    self.suffix = options.suffix;
    self.isMobile = ko.observable(options.mobile);
    self.isHue4 = ko.observable(options.hue4);
    self.isNotificationManager = ko.observable(options.is_notification_manager || false);
    self.editorType = ko.observable(options.editor_type);
    self.editorType.subscribe(function(newVal) {
      self.editorMode(newVal != 'notebook');
      hueUtils.changeURLParameter('type', newVal);
      if (self.editorMode()) {
        self.selectedNotebook().fetchHistory(); // Js error if notebook did not have snippets
      }
    });
    self.preEditorTogglingSnippet = ko.observable();
    self.toggleEditorMode = function() {
      var _notebook = self.selectedNotebook();
      var _newSnippets = [];

      if (self.editorType() != 'notebook') {
        self.editorType('notebook');
        self.preEditorTogglingSnippet(_notebook.snippets()[0]);
        var _variables = _notebook.snippets()[0].variables();
        var _statementKeys = [];
        // Split statements
        _notebook.type('notebook');
        _notebook.snippets()[0].statementsList().forEach(function (sql_statement) {
          var _snippet;
          if (sql_statement.hashCode() in _notebook.presentationSnippets()) {
            _snippet = _notebook.presentationSnippets()[sql_statement.hashCode()]; // Persist result
            _snippet.variables(_variables);
          } else {
            var _title = [];
            var _statement = [];
            sql_statement.trim().split('\n').forEach(function(line) {
              if (line.trim().startsWith('--') && _statement.length == 0) {
                _title.push(line.substr(2));
              } else {
                _statement.push(line);
              }
            });
            _snippet = new Snippet(self, _notebook, {type: _notebook.initialType, statement_raw: _statement.join('\n'), result: {}, name: _title.join('\n'), variables: ko.mapping.toJS(_variables)}, skipSession=true);
            _snippet.variables = _notebook.snippets()[0].variables;
            _snippet.init();
            _notebook.presentationSnippets()[sql_statement.hashCode()] = _snippet;
          }
          _statementKeys.push(sql_statement.hashCode());
          _newSnippets.push(_snippet);
        });
        $.each(_notebook.presentationSnippets(), function(key, statement) { // Dead statements
          if (! key in _statementKeys) {
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
      _newSnippets.forEach(function (snippet) {
        huePubSub.publish('editor.redraw.data', {snippet: snippet});
      });
    };
    self.togglePresentationMode = function() {
      if (self.selectedNotebook().initialType != 'notebook') {
        self.toggleEditorMode();
      }
    };
    self.editorTypeTitle = ko.pureComputed(function () {
      var foundInterpreter = $.grep(options.languages, function (interpreter) {
        return interpreter.type === self.editorType();
      });
      return foundInterpreter.length > 0 ? foundInterpreter[0].name : self.editorType();
    });
    self.useNewAutocompleter = options.useNewAutocompleter || false;
    self.autocompleteTimeout = options.autocompleteTimeout;
    self.selectedNotebook = ko.observable();

    self.combinedContent = ko.observable();
    self.isPresentationModeEnabled = ko.pureComputed(function () {
      return self.selectedNotebook() && self.selectedNotebook().snippets().length === 1 && self.selectedNotebook().snippets()[0].isSqlDialect()
    });
    self.isResultFullScreenMode = ko.observable(false);
    self.isPresentationMode = ko.computed(function() {
      return self.selectedNotebook() && self.selectedNotebook().isPresentationMode();
    });
    self.isHidingCode = ko.computed(function() {
      return self.selectedNotebook() && self.selectedNotebook().isHidingCode();
    })
    self.successUrl = ko.observable(options.success_url); // Deprecated
    self.isOptimizerEnabled = ko.observable(options.is_optimizer_enabled);
    self.isNavigatorEnabled = ko.observable(options.is_navigator_enabled);

    self.CoordinatorEditorViewModel = CoordinatorEditorViewModel;
    self.RunningCoordinatorModel = RunningCoordinatorModel;

    self.canSave = ko.computed(function() {
      // Saved query or history but history coming from a saved query
      return self.selectedNotebook() && self.selectedNotebook().canWrite() && (
          self.selectedNotebook().isSaved() ||
          (self.selectedNotebook().isHistory() && self.selectedNotebook().parentSavedQueryUuid())
      );
    });

    // TODO: Drop the SQL source types from the notebook. They're now set in AssistDbPanel.
    self.sqlSourceTypes = [];
    self.availableLanguages = [];

    if (options.languages && options.snippetViewSettings) {
      $.each(options.languages, function (idx, language) {
        self.availableLanguages.push({
          type: language.type,
          name: language.name,
          interface: language.interface
        });
        var viewSettings = options.snippetViewSettings[language.type];
        if (viewSettings && viewSettings.sqlDialect) {
          self.sqlSourceTypes.push({
            type: language.type,
            name: language.name
          })
        }
      });
    }

    var sqlSourceTypes = $.grep(self.sqlSourceTypes, function(language) { return language.type == self.editorType(); });
    if (sqlSourceTypes.length > 0) {
      self.activeSqlSourceType = sqlSourceTypes[0].type;
    } else {
      self.activeSqlSourceType = null;
    }

    self.displayCombinedContent = function () {
      if (! self.selectedNotebook()) {
        self.combinedContent('');
      } else {
        var statements = '';
        $.each(self.selectedNotebook().snippets(), function (index, snippet) {
          if (snippet.statement()) {
            if (statements) {
              statements += '\n\n';
            }
            statements += snippet.statement();
          }
        });
        self.combinedContent(statements);
      }
      $("#combinedContentModal" + self.suffix).modal("show");
    };

    self.isEditing = ko.observable(false);
    self.isEditing.subscribe(function () {
      $(document).trigger("editingToggled");
    });
    self.toggleEditing = function () {
      self.isEditing(! self.isEditing());
    };

    self.authSessionUsername = ko.observable(); // UI popup
    self.authSessionPassword = ko.observable();
    self.authSessionType = ko.observable();
    self.authSessionCallback = ko.observable();

    self.removeSnippetConfirmation = ko.observable();

    self.removeSnippet = function (notebook, snippet) {
      var hasContent = snippet.statement_raw().length > 0;
      if (!hasContent) {
        $.each(snippet.properties(), function (key, value) {
          hasContent = hasContent || (ko.isObservable(value) && value().length > 0);
        });
      }
      if (hasContent) {
        self.removeSnippetConfirmation({ notebook: notebook, snippet: snippet });
        $("#removeSnippetModal" + self.suffix).modal("show");
      }
      else {
        notebook.snippets.remove(snippet);
        window.setTimeout(function () {
          $(document).trigger("editorSizeChanged");
        }, 100);
      }
    };

    self.assistAvailable = ko.observable(options.assistAvailable);

    self.assistWithoutStorage = ko.observable(false);

    self.isLeftPanelVisible = ko.observable(ApiHelper.getInstance().getFromTotalStorage('assist', 'assist_panel_visible', true));
    self.isLeftPanelVisible.subscribe(function (val) {
      if (!self.assistWithoutStorage()){
        ApiHelper.getInstance().setInTotalStorage('assist', 'assist_panel_visible', val);
      }
    });

    self.isRightPanelAvailable = ko.observable(options.assistAvailable && HAS_OPTIMIZER);
    self.isRightPanelVisible = ko.observable(ApiHelper.getInstance().getFromTotalStorage('assist', 'right_assist_panel_visible', true));
    self.isRightPanelVisible.subscribe(function (val) {
      if (!self.assistWithoutStorage()){
        ApiHelper.getInstance().setInTotalStorage('assist', 'right_assist_panel_visible', val);
      }
    });

    var withActiveSnippet = function (callback) {
      var notebook = self.selectedNotebook();
      var foundSnippet;
      if (notebook) {
        if (notebook.snippets().length === 1) {
          foundSnippet = notebook.snippets()[0];
        } else {
          notebook.snippets().every(function (snippet) {
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

    huePubSub.subscribe('assist.highlight.risk.suggestions', function () {
      if (self.isRightPanelAvailable() && !self.isRightPanelVisible()) {
        self.isRightPanelVisible(true);
      }
    });

    self.isContextPanelVisible = ko.observable(false);
    self.isContextPanelVisible.subscribe(function (newValue) {
      huePubSub.publish('context.panel.visible', newValue);
    });

    huePubSub.subscribe('context.panel.visible.editor', self.isContextPanelVisible);

    huePubSub.subscribe('get.active.snippet.type', function () {
      withActiveSnippet(function (activeSnippet) {
        huePubSub.publish('set.active.snippet.type', activeSnippet.type());
      })
    }, self.huePubSubId);

    huePubSub.subscribe('save.snippet.to.file', function() {
      withActiveSnippet(function (activeSnippet) {
        var data = {
          path: activeSnippet.statementPath(),
          contents: activeSnippet.statement()
        };
        var options = {
          successCallback: function (result) {
            if (result && result.exists) {
              $(document).trigger("info", result.path + ' saved successfully.');
            } else {
              self._ajaxError(result);
            }
          }
        };
        ApiHelper.getInstance().saveSnippetToFile(data, options);
      });
    }, self.huePubSubId);

    huePubSub.subscribe('sql.context.pin', function (contextData) {
      withActiveSnippet(function (activeSnippet) {
        contextData.tabId = 'context' + activeSnippet.pinnedContextTabs().length;
        activeSnippet.pinnedContextTabs.push(contextData);
        activeSnippet.currentQueryTab(contextData.tabId);
      });
    }, self.huePubSubId);

    huePubSub.subscribe("assist.database.set", function (databaseDef) {
      withActiveSnippet(function (activeSnippet) {
        activeSnippet.handleAssistSelection(databaseDef);
      });
    }, self.huePubSubId);

    huePubSub.subscribe("assist.database.selected", function (databaseDef) {
      withActiveSnippet(function (activeSnippet) {
        activeSnippet.handleAssistSelection(databaseDef);
      });
    }, self.huePubSubId);

    self.availableSnippets = ko.mapping.fromJS(options.languages);

    self.editorMode = ko.observable(options.mode == 'editor');

    self.getSnippetViewSettings = function (snippetType) {
      if (options.snippetViewSettings[snippetType]) {
        return options.snippetViewSettings[snippetType];
      }
      return options.snippetViewSettings.default;
    };

    self.availableSessionProperties = ko.computed(function () { // Only Spark
      return ko.utils.arrayFilter(options.session_properties, function (item) {
        return item.name != ''; // Could filter out the ones already selected + yarn only or not
      });
    });
    self.getSessionProperties = function(name) {
      var _prop = null;
      $.each(options.session_properties, function(index, prop) {
        if (prop.name == name) {
          _prop = prop;
          return;
        }
      });
      return _prop;
    };

    self.getSnippetName = function(snippetType)  {
      var availableSnippets = self.availableSnippets();
      for (var i = 0; i < availableSnippets.length; i++) {
        if (availableSnippets[i].type() === snippetType) {
          return availableSnippets[i].name();
        }
      }
      return '';
    };

    self.changeURL = function (url) {
      if (!self.isNotificationManager()) {
        hueUtils.changeURL(url);
      }
    };

    self.init = function () {
      if (editor_id) {
        self.openNotebook(editor_id);
      } else if (window.location.getParameter('editor') !== ''){
        self.openNotebook(window.location.getParameter('editor'));
      } else if (notebooks.length > 0) {
        self.loadNotebook(notebooks[0]); // Old way of loading json for /browse
      } else if (window.location.getParameter('type') !== '') {
        self.newNotebook(window.location.getParameter('type'));
      } else {
        self.newNotebook();
      }
    };

    self.loadNotebook = function (notebook, queryTab) {
      var currentQueries;
      if (self.selectedNotebook() != null) {
        currentQueries = self.selectedNotebook().unload();
      }

      var notebook = new Notebook(self, notebook);

      if (notebook.snippets().length > 0) {
        huePubSub.publish('detach.scrolls', notebook.snippets()[0]);
        notebook.selectedSnippet(notebook.snippets()[notebook.snippets().length - 1].type());
        if (currentQueries != null) {
          notebook.snippets()[0].queries(currentQueries);
        }
        notebook.snippets().forEach(function (snippet) {
          snippet.aceAutoExpand = false;
          snippet.statement_raw.valueHasMutated();
          if (snippet.result.handle().statements_count > 1 && snippet.result.handle().start != null && snippet.result.handle().end != null) {
            var aceLineOffset = snippet.result.handle().aceLineOffset || 0;
            snippet.result.statement_range({
              start: { row: snippet.result.handle().start.row + aceLineOffset, column: snippet.result.handle().start.column },
              end: { row: snippet.result.handle().end.row + aceLineOffset, column: snippet.result.handle().end.column }
            });
            snippet.result.statement_range.valueHasMutated();
          }

          snippet.previousChartOptions = self._getPreviousChartOptions(snippet);
        });

        if (notebook.snippets()[0].result.data().length > 0) {
          $(document).trigger("redrawResults");
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

    self._getPreviousChartOptions = function(snippet) {
      return {
          chartLimit: typeof snippet.chartLimit() !== "undefined" ? snippet.chartLimit() : snippet.previousChartOptions.chartLimit,
          chartX: typeof snippet.chartX() !== "undefined" ? snippet.chartX() : snippet.previousChartOptions.chartX,
          chartXPivot: typeof snippet.chartXPivot() !== "undefined" ? snippet.chartXPivot() : snippet.previousChartOptions.chartXPivot,
          chartYSingle: typeof snippet.chartYSingle() !== "undefined" ? snippet.chartYSingle() : snippet.previousChartOptions.chartYSingle,
          chartMapType: typeof snippet.chartMapType() !== "undefined" ? snippet.chartMapType() : snippet.previousChartOptions.chartMapType,
          chartMapLabel: typeof snippet.chartMapLabel() !== "undefined" ? snippet.chartMapLabel() : snippet.previousChartOptions.chartMapLabel,
          chartMapHeat: typeof snippet.chartMapHeat() !== "undefined" ? snippet.chartMapHeat() : snippet.previousChartOptions.chartMapHeat,
          chartYMulti: typeof snippet.chartYMulti() !== "undefined" ? snippet.chartYMulti() : snippet.previousChartOptions.chartYMulti,
          chartScope: typeof snippet.chartScope() !== "undefined" ? snippet.chartScope() : snippet.previousChartOptions.chartScope,
          chartTimelineType: typeof snippet.chartTimelineType() !== "undefined" ? snippet.chartTimelineType() : snippet.previousChartOptions.chartTimelineType,
          chartSorting: typeof snippet.chartSorting() !== "undefined" ? snippet.chartSorting() : snippet.previousChartOptions.chartSorting,
          chartScatterGroup: typeof snippet.chartScatterGroup() !== "undefined" ? snippet.chartScatterGroup() : snippet.previousChartOptions.chartScatterGroup,
          chartScatterSize: typeof snippet.chartScatterSize() !== "undefined" ? snippet.chartScatterSize() : snippet.previousChartOptions.chartScatterSize
        };
    };

    self.openNotebook = function (uuid, queryTab, skipUrlChange, callback) {
      var deferredOpen = new $.Deferred();
      $.get('/desktop/api2/doc/', {
        uuid: uuid,
        data: true,
        dependencies: true
      }, function (data) {
        if (data.status == 0) {
          data.data.dependents = data.dependents;
          data.data.can_write = data.user_perms.can_write;
          var notebook = data.data;
          self.loadNotebook(notebook, queryTab);
          if (typeof skipUrlChange === 'undefined' && ! self.isNotificationManager()){
            if (self.editorMode()) {
              self.editorType(data.document.type.substring('query-'.length));
              huePubSub.publish('active.snippet.type.changed', self.editorType());
              if (self.isHue4()){
                self.changeURL(self.URLS.hue4 + '?editor=' + data.document.id + '&type=' + self.editorType());
              } else {
                self.changeURL((self.isMobile() ? self.URLS.editorMobile : self.URLS.editor) + '?editor=' + data.document.id + '&type=' + self.editorType());
              }
            } else {
              if (self.isHue4()){
                self.changeURL(self.URLS.hue4_notebook + '?notebook=' + data.document.id);
              } else {
                self.changeURL(self.URLS.notebook + '?notebook=' + data.document.id);
              }
            }
          }
          if (typeof callback !== 'undefined'){
            callback();
          }
          deferredOpen.resolve();
        }
        else {
          $(document).trigger("error", data.message);
          deferredOpen.reject();
          self.newNotebook();
        }
      });
      return deferredOpen.promise();
    };

    self.newNotebook = function (editorType, callback, queryTab) {
      huePubSub.publish('active.snippet.type.changed', editorType);
      $.post("/notebook/api/create_notebook", {
        type: editorType || options.editor_type,
        directory_uuid: window.location.getParameter('directory_uuid')
      }, function (data) {
        self.loadNotebook(data.notebook);
        if (self.editorMode() && !self.isNotificationManager()) {
          var snippet = self.selectedNotebook().newSnippet(self.editorType());
          if (queryTab && ['queryHistory', 'savedQueries', 'queryBuilderTab'].indexOf(queryTab) > -1) {
            snippet.currentQueryTab(queryTab);
          }
          huePubSub.publish('detach.scrolls', self.selectedNotebook().snippets()[0]);
          if (window.location.getParameter('type') === '') {
            hueUtils.changeURLParameter('type', self.editorType());
          }
          huePubSub.publish('active.snippet.type.changed', editorType);
        }

        if (typeof callback !== 'undefined' && callback !== null){
          callback();
        }
      });
    };

    self.saveNotebook = function () {
      self.selectedNotebook().save();
    };

    self.saveAsNotebook = function () {
      self.selectedNotebook().id(null);
      self.selectedNotebook().uuid(UUID());
      self.selectedNotebook().parentSavedQueryUuid(null);
      self.selectedNotebook().save(function () {
        huePubSub.publish('assist.document.refresh');
      });
    };

    self.showContextPopover = function (field, event) {
      var $source = $(event.target && event.target.nodeName !== 'A' ? event.target.parentElement : event.target);
      var offset = $source.offset();
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

  return EditorViewModel;
})();
