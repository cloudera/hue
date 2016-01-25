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

(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define(['knockout', 'desktop/js/assist/assistHelper', 'desktop/js/autocompleter', 'knockout-mapping', 'ko.charts'], factory);
  } else {
    root.EditorViewModel = factory(ko, AssistHelper, Autocompleter);
  }
}(this, function (ko, AssistHelper, Autocompleter) {

  var SPARK_MAPPING = {
    ignore: ["ace", "images", "autocompleter", "selectedStatement", "assistHelpers", "user", "inFocus", "history", "availableSnippets"]
  };

  var Result = function (snippet, result) {
    var self = this;

    self.id = ko.observable(typeof result.id != "undefined" && result.id != null ? result.id : UUID());
    self.type = ko.observable(typeof result.type != "undefined" && result.type != null ? result.type : 'table');
    self.hasResultset = ko.observable(typeof result.hasResultset != "undefined" && result.hasResultset != null ? result.hasResultset : true)
      .extend("throttle", 100);
    self.handle = ko.observable(typeof result.handle != "undefined" && result.handle != null ? result.handle : {});
    self.meta = ko.observableArray(typeof result.meta != "undefined" && result.meta != null ? result.meta : []);
    self.hasMore = ko.observable(typeof result.hasMore != "undefined" && result.hasMore != null ? result.hasMore : false);
    self.cleanedMeta = ko.computed(function () {
      return ko.utils.arrayFilter(self.meta(), function (item) {
        return item.name != ''
      });
    });
    self.fetchedOnce = ko.observable(typeof result.fetchedOnce != "undefined" && result.fetchedOnce != null ? result.fetchedOnce : false);
    self.startTime = ko.observable(typeof result.startTime != "undefined" && result.startTime != null ? new Date(result.startTime) : new Date());
    self.endTime = ko.observable(typeof result.endTime != "undefined" && result.endTime != null ? new Date(result.endTime) : new Date());
    self.executionTime = ko.computed(function () {
      return self.endTime().getTime() - self.startTime().getTime();
    });

    function isNumericColumn(type) {
      return $.inArray(type, ['TINYINT_TYPE', 'SMALLINT_TYPE', 'INT_TYPE', 'BIGINT_TYPE', 'FLOAT_TYPE', 'DOUBLE_TYPE', 'DECIMAL_TYPE', 'TIMESTAMP_TYPE', 'DATE_TYPE']) > -1;
    }

    function isDateTimeColumn(type) {
      return $.inArray(type, ['TIMESTAMP_TYPE', 'DATE_TYPE']) > -1;
    }

    function isStringColumn(type) {
      return !isNumericColumn(type) && !isDateTimeColumn(type);
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
      self.startTime(new Date());
      self.endTime(new Date());
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

    if (snippetType == 'jar') {
      properties['app_jar'] = '';
      properties['class'] = '';
      properties['arguments'] = [];
    }
    else if (snippetType == 'py') {
      properties['py_file'] = '';
      properties['arguments'] = [];
    }
    else if (snippetType == 'hive') {
      properties['settings'] = [];
      properties['files'] = [];
      properties['functions'] = [];
    }
    else if (snippetType == 'impala') {
      properties['settings'] = [];
    }
    else if (snippetType == 'pig') {
      properties['parameters'] = [];
      properties['hadoopProperties'] = [];
      properties['resources'] = [];
    }

    return properties;
  };

  var ERROR_REGEX = /line ([0-9]+)/i;

  var Snippet = function (vm, notebook, snippet) {
    var self = this;

    self.id = ko.observable(typeof snippet.id != "undefined" && snippet.id != null ? snippet.id : UUID());
    self.name = ko.observable(typeof snippet.name != "undefined" && snippet.name != null ? snippet.name : '');
    self.type = ko.observable(typeof snippet.type != "undefined" && snippet.type != null ? snippet.type : 'hive');

    //Ace stuff
    self.ace = ko.observable(null);
    self.errors = ko.observableArray([]);

    self.availableSnippets = vm.availableSnippets();
    self.inFocus = ko.observable(false);

    self.getAceMode = function() {
      return vm.getSnippetViewSettings(self.type()).aceMode;
    };

    self.isSqlDialect = ko.pureComputed(function () {
      return vm.getSnippetViewSettings(self.type()).sqlDialect;
    });

    self.getPlaceHolder = function() {
      return vm.getSnippetViewSettings(self.type()).placeHolder;
    };

    self.getAssistHelper = function() {
      return AssistHelper.getInstance(vm);
    };

    self.database = ko.observable(typeof snippet.database != "undefined" && snippet.database != null ? snippet.database : null);

    self.availableDatabases = ko.observableArray();

    var updateDatabases = function () {
      if (self.isSqlDialect()) {
        self.getAssistHelper().loadDatabases({
          sourceType: self.type(),
          silenceErrors: true,
          successCallback: self.availableDatabases
        });
      } else {
        self.availableDatabases([]);
      }
    };

    self.isSqlDialect.subscribe(updateDatabases);
    updateDatabases();

    var handleAssistSelection = function (databaseDef) {
      if (databaseDef.source === self.type() && self.database() !== databaseDef.name) {
        self.database(databaseDef.name);
      }
    };

    huePubSub.subscribe("assist.database.set", handleAssistSelection);
    huePubSub.subscribe("assist.database.selected", handleAssistSelection);

    if (! self.database()) {
      huePubSub.publish("assist.get.database", self.type());
    }

    self.statement_raw = ko.observable(typeof snippet.statement_raw != "undefined" && snippet.statement_raw != null ? snippet.statement_raw : '');
    self.selectedStatement = ko.observable('');
    self.aceSize = ko.observable(typeof snippet.aceSize != "undefined" && snippet.aceSize != null ? snippet.aceSize : 100);
    // self.statement_raw.extend({ rateLimit: 150 }); // Should prevent lag from typing but currently send the old query when using the key shortcut
    self.status = ko.observable(typeof snippet.status != "undefined" && snippet.status != null ? snippet.status : 'loading');

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

    self.variables = ko.observableArray([]);
    self.variableNames = ko.computed(function () {
      var re = /(?:^|\W)\${(\w+)(?!\w)}/g;

      var match, matches = [];
      while (match = re.exec(self.statement_raw())) {
        matches.push(match[1]);
      }
      return matches;
    });
    self.variableNames.extend({ rateLimit: 150 });
    self.variableNames.subscribe(function (newVal) {
      var toDelete = [];
      var toAdd = [];

      $.each(newVal, function (key, name) {
        var match = ko.utils.arrayFirst(self.variables(), function (_var) {
          return _var.name() == name;
        });
        if (!match) {
          toAdd.push(name);
        }
      });
      $.each(self.variables(), function (key, _var) {
        var match = ko.utils.arrayFirst(newVal, function (name) {
          return _var.name() == name;
        });
        if (!match) {
          toDelete.push(_var);
        }
      });

      $.each(toDelete, function (index, item) {
        self.variables.remove(item);
      });
      $.each(toAdd, function (index, item) {
        self.variables.push(ko.mapping.fromJS({'name': item, 'value': ''}));
      });

      self.variables.sort(function (left, right) {
        var leftIndex = newVal.indexOf(left.name());
        var rightIndex = newVal.indexOf(right.name());
        return leftIndex == rightIndex ? 0 : (leftIndex < rightIndex ? -1 : 1);
      });
    });
    self.statement = ko.computed(function () {
      var statement = self.isSqlDialect() && self.selectedStatement() ? self.selectedStatement() : self.statement_raw();
      $.each(self.variables(), function (index, variable) {
        statement = statement.replace(RegExp("([^\\\\])?\\${" + variable.name() + "}", "g"), "$1" + variable.value());
      });
      return statement;
    });
    self.result = new Result(snippet, snippet.result);
    self.showGrid = ko.observable(typeof snippet.showGrid != "undefined" && snippet.showGrid != null ? snippet.showGrid : true);
    self.showChart = ko.observable(typeof snippet.showChart != "undefined" && snippet.showChart != null ? snippet.showChart : false);
    self.showLogs = ko.observable(typeof snippet.showLogs != "undefined" && snippet.showLogs != null ? snippet.showLogs : false);
    self.progress = ko.observable(typeof snippet.progress != "undefined" && snippet.progress != null ? snippet.progress : 0);
    self.jobs = ko.observableArray(typeof snippet.jobs != "undefined" && snippet.jobs != null ? snippet.jobs : []);

    self.progress.subscribe(function (val) {
      $(document).trigger("progress", {data: val, snippet: self});
    });

    self.showGrid.subscribe(function (val) {
      if (val) {
        self.showChart(false);
        $(document).trigger("gridShown", self);
      }
    });
    self.showChart.subscribe(function (val) {
      if (val) {
        self.showGrid(false);
        self.isResultSettingsVisible(true);
        $(document).trigger("forceChartDraw", self);
        $(document).trigger("chartShown", self);
      }
    });
    self.showLogs.subscribe(function (val) {
      if (val) {
        self.getLogs();
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

    self.chartType = ko.observable(typeof snippet.chartType != "undefined" && snippet.chartType != null ? snippet.chartType : ko.HUE_CHARTS.TYPES.BARCHART);
    self.chartSorting = ko.observable(typeof snippet.chartSorting != "undefined" && snippet.chartSorting != null ? snippet.chartSorting : "none");
    self.chartScatterGroup = ko.observable(typeof snippet.chartScatterGroup != "undefined" && snippet.chartScatterGroup != null ? snippet.chartScatterGroup : null);
    self.chartScatterSize = ko.observable(typeof snippet.chartScatterSize != "undefined" && snippet.chartScatterSize != null ? snippet.chartScatterSize : null);
    self.chartScope = ko.observable(typeof snippet.chartScope != "undefined" && snippet.chartScope != null ? snippet.chartScope : "world");
    self.chartX = ko.observable(typeof snippet.chartX != "undefined" && snippet.chartX != null ? snippet.chartX : null);
    self.chartYSingle = ko.observable(typeof snippet.chartYSingle != "undefined" && snippet.chartYSingle != null ? snippet.chartYSingle : null);
    self.chartYMulti = ko.observableArray(typeof snippet.chartYMulti != "undefined" && snippet.chartYMulti != null ? snippet.chartYMulti : []);
    self.chartData = ko.observableArray(typeof snippet.chartData != "undefined" && snippet.chartData != null ? snippet.chartData : []);
    self.chartMapLabel = ko.observable(typeof snippet.chartMapLabel != "undefined" && snippet.chartMapLabel != null ? snippet.chartMapLabel : null);

    self.hasDataForChart = ko.computed(function () {
      if (self.chartType() == ko.HUE_CHARTS.TYPES.BARCHART || self.chartType() == ko.HUE_CHARTS.TYPES.LINECHART) {
        return typeof self.chartX() != "undefined" && self.chartX() != null && self.chartYMulti().length > 0;
      }
      return typeof self.chartX() != "undefined" && self.chartX() != null && typeof self.chartYSingle() != "undefined" && self.chartYSingle() != null ;
    });

    self.hasDataForChart.subscribe(function(newValue) {
      if (!newValue) {
        self.isResultSettingsVisible(true);
      }
      self.chartX.notifySubscribers();
      self.chartX.valueHasMutated();
    });

    self.chartType.subscribe(function (val) {
      $(document).trigger("forceChartDraw", self);
    });

    self.previousChartOptions = {};

    self.result.meta.subscribe(function(newValue) {
      self.chartX(self.previousChartOptions.chartX);
      self.chartYSingle(self.previousChartOptions.chartYSingle);
      self.chartMapLabel(self.previousChartOptions.chartMapLabel);
      self.chartYMulti(self.previousChartOptions.chartYMulti || []);
    });

    self.isResultSettingsVisible = ko.observable(typeof snippet.isResultSettingsVisible != "undefined" && snippet.isResultSettingsVisible != null ? snippet.isResultSettingsVisible : false);
    self.toggleResultSettings = function () {
      self.isResultSettingsVisible(!self.isResultSettingsVisible());
    };
    self.isResultSettingsVisible.subscribe(function(){
      $(document).trigger("toggleResultSettings", self);
    });

    self.settingsVisible = ko.observable(typeof snippet.settingsVisible != "undefined" && snippet.settingsVisible != null ? snippet.settingsVisible : false);

    self.checkStatusTimeout = null;

    self.getContext = function() {
      return {
        id: self.id,
        type: self.type,
        status: self.status,
        statement: self.statement,
        properties: self.properties,
        result: self.result.getContext()
      };
    };

    self._ajaxError = function (data, callback) {
      if (data.status == -2) { // Session expired
        var existingSession = notebook.getSession(self.type());
        if (existingSession) {
          notebook.restartSession(existingSession, callback);
        } else {
          notebook.createSession(new Session(vm, {'type': self.type()}), callback);
        }
      }
      else if (data.status == -3) { // Statement expired
        self.status('expired');
      }
      else if (data.status == 401) { // Auth required
        self.status('expired');
        $(document).trigger("showAuthModal", {'type': self.type(), 'callback': self.execute});
      }
      else if (data.status == 1 || data.status == -1) {
        self.status('failed');
        var match = ERROR_REGEX.exec(data.message);
        self.errors.push({
          message: data.message,
          line: match === null ? null : parseInt(match[1]) - 1
        });
      } else {
        $(document).trigger("error", data.message);
        self.status('failed');
      }
    };

    self.lastExecuted = 0;

    self.execute = function () {
      var now = (new Date()).getTime(); // We don't allow fast clicks
      if (self.status() == 'running' || self.status() == 'loading' || now - self.lastExecuted < 1000 || self.statement() == '') {
        return;
      }

      notebook.showHistory(false);

      self.previousChartOptions = {
        chartScope: typeof self.chartScope() !== "undefined" ? self.chartX() : self.previousChartOptions.chartX,
        chartX: typeof self.chartX() !== "undefined" ? self.chartX() : self.previousChartOptions.chartX,
        chartYSingle: typeof self.chartYSingle() !== "undefined" ? self.chartYSingle() : self.previousChartOptions.chartYSingle,
        chartMapLabel: typeof self.chartMapLabel() !== "undefined" ? self.chartMapLabel() : self.previousChartOptions.chartMapLabel,
        chartYMulti: typeof self.chartYMulti() !== "undefined" ? self.chartYMulti() : self.previousChartOptions.chartYMulti
      };
      $(document).trigger("executeStarted", self);
      self.lastExecuted = now;
      $(".jHueNotify").hide();
      logGA('/execute/' + self.type());

      self.status('running');
      self.errors([]);
      self.result.logLines = 0;
      self.progress(0);
      self.jobs([]);
      self.result.logs('');

      if (self.result.fetchedOnce()) {
        self.close();
      }

      $.post("/notebook/api/execute", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function (data) {
        if (data.status == 0) {
          self.result.clear();
          self.result.handle(data.handle);
          self.result.hasResultset(data.handle.has_result_set);
          if (data.handle.sync) {
            self.loadData(data.handle, 100);
            self.status('success');
            self.progress(100);
          } else {
            self.checkStatus();
          }
        } else {
          self._ajaxError(data, self.execute);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
        self.status('failed');
      })
      .always(function() {
        if (notebook.type() != 'notebook') {
          $.post("/notebook/api/historify", {
            notebook: ko.mapping.toJSON(notebook, SPARK_MAPPING)
          }, function(data){
            if (vm.editorMode && data && data.status == 0 && data.id){
              hueUtils.changeURL('/notebook/editor?editor=' + data.id);
            }
          });
        }
      });
    };

    self.reexecute = function () {
      self.result.handle()['statement_id'] = 0;
      self.result.handle()['has_more_statements'] = false;

      self.execute();
    };

    self.format = function () {
      if (self.isSqlDialect() && vkbeautify) {
        if (self.ace().getSelectedText() != '') {
          self.ace().session.replace(self.ace().session.selection.getRange(), vkbeautify.sql(self.ace().getSelectedText(), 2));
        }
        else {
          self.statement_raw(vkbeautify.sql(self.statement_raw(), 2));
          self.ace().setValue(self.statement_raw(), 1);
        }
      }
    };

    self.fetchResult = function (rows, startOver) {
      if (typeof startOver == "undefined") {
        startOver = true;
      }
      self.fetchResultData(rows, startOver);
      //self.fetchResultMetadata(rows);
    };

    self.fetchResultData = function (rows, startOver) {
      $.post("/notebook/api/fetch_result_data", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext()),
        rows: rows,
        startOver: startOver
      }, function (data) {
        if (data.status == 0) {
          self.loadData(data, rows);
        } else {
          self._ajaxError(data);
          $(document).trigger("renderDataError", {snippet: self});
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.loadData = function (data, rows) {
      rows -= data.result.data.length;

      var _initialIndex = self.result.data().length;
      var _tempData = [];
      $.each(data.result.data, function (index, row) {
        row.unshift(_initialIndex + index + 1);
        self.result.data.push(row);
        _tempData.push(row);
      });

      self.result.images(typeof data.result.images != "undefined" && data.result.images != null ? data.result.images : []);

      $(document).trigger("renderData", {data: _tempData, snippet: self, initial: _initialIndex == 0});

      if (! self.result.fetchedOnce()) {
        data.result.meta.unshift({type: "INT_TYPE", name: "", comment: null});
        self.result.meta(data.result.meta);
        self.result.type(data.result.type);
        self.result.fetchedOnce(true);
      }

      self.result.hasMore(data.result.has_more);

      if (data.result.has_more && rows > 0) {
        setTimeout(function () {
          self.fetchResultData(rows, false);
        }, 500);
      } else if (! self.isSqlDialect() && notebook.snippets()[notebook.snippets().length - 1] == self) {
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
        $(document).trigger("error", xhr.responseText);
        self.status('failed');
      });
    };

    self.checkStatus = function () {
      $.post("/notebook/api/check_status", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function (data) {
        if (data.status == 0) {
          self.status(data.query_status.status);
          self.getLogs();

          if (self.status() == 'running' || self.status() == 'starting') {
            self.result.endTime(new Date());
            self.checkStatusTimeout = setTimeout(self.checkStatus, 1000);
          }
          else if (self.status() == 'available') {
            self.fetchResult(100);
            self.progress(100);
            if (self.isSqlDialect() && ! self.result.handle().has_result_set) { // DDL
              huePubSub.publish('assist.refresh');
              if (self.result.handle().has_more_statements) {
                setTimeout(function () {
                  self.execute(); // Execute next, need to wait as we disabled fast click
                }, 1000);
              }
            }
          }
          else if (self.status() == 'success') {
            self.progress(99);
          }
        } else if (data.status == -3) {
          self.status('expired');
        } else {
          self._ajaxError(data);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
        self.status('failed');
      });
    };

    self.cancel = function () {
      if (self.checkStatusTimeout != null) {
        clearTimeout(self.checkStatusTimeout);
        self.checkStatusTimeout = null;
      }

      $.post("/notebook/api/cancel_statement", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext())
      }, function (data) {
        if (data.status == 0) {
          self.status('canceled');
        } else {
          self._ajaxError(data);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
        self.status('failed');
      });
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
          self._ajaxError(data);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
        self.status('failed');
      });
    };

    self.getLogs = function () {
      $.post("/notebook/api/get_logs", {
        notebook: ko.mapping.toJSON(notebook.getContext()),
        snippet: ko.mapping.toJSON(self.getContext()),
        from: self.result.logLines,
        jobs: ko.mapping.toJSON(self.jobs),
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
            if (oldLogs === "") {
              self.result.logs(data.logs);
            } else {
              self.result.logs(oldLogs + "\n" + data.logs);
            }
          }
          if (data.jobs.length > 0) {
            self.jobs(data.jobs);
          }
          self.progress(data.progress);
        } else {
          self._ajaxError(data);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
        self.status('failed');
      });
    };

    self.autocompleter = new Autocompleter({
      snippet: self,
      user: vm.user
    });

    self.init = function () {
      if (self.status() == 'running') {
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
        addedIndex[property.key()] = true;
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
    self.snippets = ko.observableArray();
    self.selectedSnippet = ko.observable(vm.availableSnippets().length > 0 ? vm.availableSnippets()[0].type() : 'NO_SNIPPETS');
    self.creatingSessionLocks = ko.observableArray();
    self.sessions = ko.mapping.fromJS(typeof notebook.sessions != "undefined" && notebook.sessions != null ? notebook.sessions : [], {
      create: function(value) {
        return new Session(vm, value.data);
      }
    });

    self.history = ko.observableArray([]);
    self.showHistory = ko.observable(typeof notebook.showHistory != "undefined" && notebook.showHistory != null ? notebook.showHistory : false);
    self.showHistory.subscribe(function (val) {
      if (val) {
        self.fetchHistory();
      }
    });

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
        session: ko.mapping.toJSON(session) // e.g. {'type': 'hive', 'properties': [{'name': driverCores', 'value', '2'}]}
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
          fail(xhr.responseText);
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

      logGA('/add_snippet/' + type);
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
         sessions: self.sessions
      };
    };

    // Init
    if (notebook.snippets) {
      $.each(notebook.snippets, function (index, snippet) {
        self.addSnippet(snippet);
      });
      if (vm.editorMode && notebook.snippets.length == 0) {
        self.showHistory(true); // Show history when new query
      }
    }

    self.save = function () {
      $.post("/notebook/api/notebook/save", {
        "notebook": ko.mapping.toJSON(self, SPARK_MAPPING),
        "editorMode": vm.editorMode
      }, function (data) {
        if (data.status == 0) {
          self.id(data.id);
          $(document).trigger("info", data.message);
          if (vm.editorMode){
            hueUtils.changeURL('/notebook/editor?editor=' + data.id);
          }
          else {
            hueUtils.changeURL('/notebook/notebook?notebook=' + data.id);
          }
        }
        else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    };

    self.close = function () {
      $.post("/notebook/api/notebook/close", {
        "notebook": ko.mapping.toJSON(self, SPARK_MAPPING),
        "editorMode": vm.editorMode
      });
    };

    self.clearResults = function () {
      $.each(self.snippets(), function (index, snippet) {
        snippet.result.clear();
        snippet.status('ready');
      });
    };

    self.executeAll = function () {
      if (self.snippets().length < 1) {
        return;
      }

      var index = 0;
      self.snippets()[index].execute();
      var clock = setInterval(next, 100);

      function next() {
        if (self.snippets()[index].status() == 'available' || self.snippets()[index].status() == 'failed') {
          index = index + 1;
          if (self.snippets().length > index) {
            self.snippets()[index].execute();
          } else {
            clearInterval(clock);
          }
        }
      }
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
        if (! silent && data.status != 0 && data.status != -2) {
          $(document).trigger("error", data.message);
        }

        if (callback) {
          callback();
        }
      }).fail(function (xhr) {
        if (! silent) {
          $(document).trigger("error", xhr.responseText);
        }
      });
    };

    self.fetchHistory = function () {
      $.get("/notebook/api/get_history", {
        doc_type: self.selectedSnippet()
      }, function(data) {
        var parsedHistory = [];
        if (data && data.history){
          data.history.forEach(function(nbk){
            parsedHistory.push({
              url: nbk.absoluteUrl,
              query: nbk.data.snippets[0].statement_raw,
              lastExecuted: nbk.data.snippets[0].lastExecuted,
              status: nbk.data.snippets[0].status
            });
          });
        }
        self.history(parsedHistory);
      });
    };

    self.clearHistory = function (type) {
      $.post("/notebook/api/clear_history", {
        notebook: ko.mapping.toJSON(self.getContext()),
        doc_type: self.selectedSnippet()
      }, function (data) {
          self.history.removeAll();
          self.showHistory(false);
        }).fail(function (xhr) {
           $(document).trigger("error", xhr.responseText);
        });
      $(document).trigger("hideHistoryModal");
    };

    self.exportJupyterNotebook = function () {
      function addCell(type, code) {
        var cell = {
          cell_type: type,
          source: [
            code
          ],
          metadata: {
            collapsed: false
          }
        };
        if (type == "code") {
          cell.outputs = [];
          cell.execution_count = 0;
        }
        return cell;
      }

      var jupyterNotebook = {
        nbformat: 4,
        nbformat_minor: 0,
        cells: [],
        metadata: {}
      };

      self.snippets().forEach(function (snippet) {
        if (snippet.type() == "pyspark") {
          jupyterNotebook.cells.push(addCell("code", snippet.statement_raw()));
        }
        if (snippet.type() == "markdown") {
          jupyterNotebook.cells.push(addCell("markdown",snippet.statement_raw()));
        }
      });

      download(JSON.stringify(jupyterNotebook), self.name() + ".ipynb", "text/plain");
    }

    huePubSub.subscribe("assist.db.panel.ready", function () {
      if (self.type() == 'query' && self.snippets().length == 1) {
        huePubSub.publish('assist.set.database', {
          source: self.snippets()[0].type(),
          name: self.snippets()[0].database()
        });
      }
    });
  };


  function EditorViewModel(notebooks, options, i18n) {
    var self = this;
    self.i18n = i18n;
    self.user = options.user;
    self.notebooks = ko.observableArray();
    self.selectedNotebook = ko.observable();
    self.combinedContent = ko.observable();
    self.isPlayerMode = ko.observable(false);

    self.sqlSourceTypes = [];

    $.each(options.languages, function (idx, language) {
      var viewSettings = options.snippetViewSettings[language.type];
      if (viewSettings && viewSettings.sqlDialect) {
        self.sqlSourceTypes.push({
          type: language.type,
          name: language.name
        })
      }
    });

    if (self.sqlSourceTypes.length === 1) {
      self.activeSqlSourceType = self.sqlSourceTypes[0].type;
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
      $("#combinedContentModal").modal("show");
    };

    self.isEditing = ko.observable(false);
    self.isEditing.subscribe(function (newVal) {
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
        $("#removeSnippetModal").modal("show");
      }
      else {
        notebook.snippets.remove(snippet);
        window.setTimeout(function () {
          $(document).trigger("editorSizeChanged");
        }, 100);
      }
    };

    self.assistAvailable = ko.observable(options.assistAvailable);

    self.isLeftPanelVisible = ko.observable();
    AssistHelper.getInstance(self).withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);

    self.availableSnippets = ko.mapping.fromJS(options.languages);

    self.editorMode = options.mode == 'editor';

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

    self.init = function () {
      $.each(notebooks, function (index, notebook) {
        self.loadNotebook(notebook);
        if (self.selectedNotebook() == null) {
          self.selectedNotebook(self.notebooks()[0]);
        }
      });
      if (self.selectedNotebook().snippets().length === 0 && self.editorMode) { // Add snippet in new Editor
        self.selectedNotebook().newSnippet();
      }
    };

    self.loadNotebook = function (notebook) {
      var notebook = new Notebook(self, notebook);
      self.notebooks.push(notebook);
      if (notebook.snippets().length > 0) {
        notebook.selectedSnippet(notebook.snippets()[notebook.snippets().length - 1].type());
        notebook.snippets().forEach(function(snippet){
          snippet.statement_raw.valueHasMutated();
        });
      }
    };

    self.newNotebook = function () {
      var notebook = new Notebook(self, {});
      self.notebooks.push(notebook);
      self.selectedNotebook(notebook);
      return notebook;
    };

    self.saveNotebook = function () {
      self.selectedNotebook().save();
    };

    self.saveAsNotebook = function () {
      self.selectedNotebook().id(null);
      self.selectedNotebook().uuid(UUID());
      self.saveNotebook();
    };
  }


  function logGA(page) {
    if (typeof trackOnGA == 'function') {
      trackOnGA('notebook/' + page);
    }
  }

  return EditorViewModel;
}));
