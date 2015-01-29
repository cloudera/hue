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


var Result = function (snippet, result) {
  var self = this;

  self.id = ko.observable(typeof result.id != "undefined" && result.id != null ? result.id : UUID());
  self.type = ko.observable(typeof result.type != "undefined" && result.type != null ? result.type : 'table');
  self.hasResultset = ko.observable(typeof result.hasResultset != "undefined" && result.hasResultset != null ? result.hasResultset : true);
  self.handle = ko.observable({});
  self.meta = ko.observableArray(typeof result.meta != "undefined" && result.meta != null ? result.meta : []);
  self.meta.extend({ rateLimit: 50 });
  self.cleanedMeta = ko.computed(function(){
    return ko.utils.arrayFilter(self.meta(), function(item) {
      return item.name != ''
    });
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

  self.cleanedNumericMeta = ko.computed(function(){
    return ko.utils.arrayFilter(self.meta(), function(item) {
      return item.name != '' && isNumericColumn(item.type)
    });
  });

  self.cleanedStringMeta = ko.computed(function(){
    return ko.utils.arrayFilter(self.meta(), function(item) {
      return item.name != '' && isStringColumn(item.type)
    });
  });

  self.cleanedDateTimeMeta = ko.computed(function(){
    return ko.utils.arrayFilter(self.meta(), function(item) {
      return item.name != '' && isDateTimeColumn(item.type)
    });
  });

  self.data = ko.observableArray(typeof result.data != "undefined" && result.data != null ? result.data : []);
  self.data.extend({ rateLimit: 50 });
  self.logs = ko.observable('');
  self.errors = ko.observable('');
  self.hasSomeResults = ko.computed(function(){
    return self.hasResultset() && self.data().length > 0; // status() == 'available'
  });
  
  if (typeof result.handle != "undefined" && result.handle != null) {
    $.each(result.handle, function(key, val) {
      self.handle()[key] = val;
    });
  }
  
  self.clear = function() {
    $.each(self.handle, function(key, val) {
      delete self.handle()[key];
    });
    self.meta.removeAll();
    self.data.removeAll();
    self.logs('');
    self.errors('');
  };  
}

var TYPE_EDITOR_MAP = {
  'hive': 'text/x-hiveql',
  'impala': 'text/x-impalaql',
  'python': 'text/x-python',
  'scala': 'text/x-scala',
  'pig': 'text/x-pig'
}

var Snippet = function (vm, notebook, snippet) {
  var self = this;
  
  self.id = ko.observable(typeof snippet.id != "undefined" && snippet.id != null ? snippet.id : UUID());
  self.name = ko.observable(typeof snippet.name != "undefined" && snippet.name != null ? snippet.name : '');
  self.type = ko.observable(typeof snippet.type != "undefined" && snippet.type != null ? snippet.type : "hive");
  self.editorMode = ko.observable(TYPE_EDITOR_MAP[self.type()]);
  self.statement_raw = ko.observable(typeof snippet.statement_raw != "undefined" && snippet.statement_raw != null ? snippet.statement_raw : vm.snippetPlaceholders[self.type()]);
  self.codemirrorSize = ko.observable(typeof snippet.codemirrorSize != "undefined" && snippet.codemirrorSize != null ? snippet.codemirrorSize : 100);
  //self.statement_raw.extend({ rateLimit: 150 });
  self.status = ko.observable(typeof snippet.status != "undefined" && snippet.status != null ? snippet.status : 'loading');
  self.settings = ko.mapping.fromJS(typeof snippet.settings != "undefined" && snippet.settings != null ? snippet.settings : {});
  self.variables = ko.observableArray([]);
  self.variableNames = ko.computed(function () {
    var matches = [];
    var myRegexp = /(?:[^\\]\$)([^\d'" ]\w*)/g;
    var match = myRegexp.exec(self.statement_raw());

    while (match != null) {
      matches.push(match[1]);
      match = myRegexp.exec(self.statement());
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
    var statement = self.statement_raw();
    $.each(self.variables(), function (index, variable) {
      statement = statement.replace(RegExp("([^\\\\])\\$" + variable.name(), "g"), "$1" + variable.value());
    });
    return statement;
  });
  self.result = new Result(snippet, snippet.result);
  self.showGrid = ko.observable(typeof snippet.showGrid != "undefined" && snippet.showGrid != null ? snippet.showGrid : true);
  self.showChart = ko.observable(typeof snippet.showChart != "undefined" && snippet.showChart != null ? snippet.showChart : false);
  self.showLogs = ko.observable(typeof snippet.showLogs != "undefined" && snippet.showLogs != null ? snippet.showLogs : false);
  self.progress =  ko.observable(typeof snippet.progress != "undefined" && snippet.progress != null ? snippet.progress : 0);
  
  self.progress.subscribe(function (val){
    $(document).trigger("progress", {data: val, snippet: self});
  });
  
  self.showGrid.subscribe(function (val){
    if (val){
      self.showChart(false);
    }
  });
  self.showChart.subscribe(function (val){
    if (val){
      self.showGrid(false);
      self.isLeftPanelVisible(true);
      $(document).trigger("forceChartDraw", self);
    }
  });
  self.showLogs.subscribe(function (val){
    if (val){
      self.getLogs();
    }
  });
  self.size = ko.observable(typeof snippet.size != "undefined" && snippet.size != null ? snippet.size : 12).extend({ numeric: 0 });
  self.offset = ko.observable(typeof snippet.offset != "undefined" && snippet.offset != null ? snippet.offset : 0).extend({ numeric: 0 });
  self.isLoading = ko.computed(function(){
    return self.status() == "loading";
  });
  self.klass = ko.computed(function () {
    return "snippet card card-widget";
  });

  self.editorKlass = ko.computed(function(){
    return "editor span" + self.size() + (self.offset() * 1 > 0 ? " offset" + self.offset() : "");
  });

  self.resultsKlass = ko.computed(function(){
    return "results " + self.type();
  });

  self.chartType = ko.observable(typeof snippet.chartType != "undefined" && snippet.chartType != null ? snippet.chartType : ko.HUE_CHARTS.TYPES.BARCHART);
  self.chartSorting = ko.observable(typeof snippet.chartSorting != "undefined" && snippet.chartSorting != null ? snippet.chartSorting : "none");
  self.chartScatterGroup = ko.observable(typeof snippet.chartScatterGroup != "undefined" && snippet.chartScatterGroup != null ? snippet.chartScatterGroup : null);
  self.chartScatterSize = ko.observable(typeof snippet.chartScatterSize != "undefined" && snippet.chartScatterSize != null ? snippet.chartScatterSize : null);
  self.chartX = ko.observable(typeof snippet.chartX != "undefined" && snippet.chartX != null ? snippet.chartX : null);
  self.chartYSingle = ko.observable(typeof snippet.chartYSingle != "undefined" && snippet.chartYSingle != null ? snippet.chartYSingle : null);
  self.chartYMulti = ko.observableArray(typeof snippet.chartYMulti != "undefined" && snippet.chartYMulti != null ? snippet.chartYMulti : []);
  self.chartData = ko.observableArray(typeof snippet.chartData != "undefined" && snippet.chartData != null ? snippet.chartData : []);
  self.chartMapLabel = ko.observable(typeof snippet.chartMapLabel != "undefined" && snippet.chartMapLabel != null ? snippet.chartMapLabel : null);

  self.chartType.subscribe(function(val){
    $(document).trigger("forceChartDraw", self);
  });

  self.tempChartOptions = {};

  self.isLeftPanelVisible = ko.observable(typeof snippet.isLeftPanelVisible != "undefined" && snippet.isLeftPanelVisible != null ? snippet.isLeftPanelVisible : false);
  self.toggleLeftPanel = function () {
    self.isLeftPanelVisible(! self.isLeftPanelVisible());
    $(document).trigger("toggleLeftPanel", self);
  };

  self.expand = function () {
    self.size(self.size() + 1);
    $("#snippet_" + self.id()).trigger("resize");
  }

  self.compress = function () {
    self.size(self.size() - 1);
    $("#snippet_" + self.id()).trigger("resize");
  }

  self.moveLeft = function () {
    self.offset(self.offset() - 1);
  }

  self.moveRight = function () {
    self.offset(self.offset() + 1);
  }

  self.remove = function (notebook, snippet) {
    notebook.snippets.remove(snippet);
  }
  
  self.checkStatusTimeout = null;
  
  self._ajax_error = function(data) {
    if (data.status == -2) {
      self.create_session();
    }
    else if (data.status == -3) {
      self.status('expired');
    } 
    else if (data.status == 1) {
      self.status('failed');
      self.result.errors(data.message);
    } else {
      $(document).trigger("error", data.message);
      self.status('failed');
    }
  };
  
  self.create_session = function() {
    $.post("/spark/api/create_session", {
    	notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self)
	  }, function (data) {
	    if (data.status == 0) {
		  notebook.addSession(ko.mapping.fromJS(data.session));
	      self.status('ready');
	    }
	    else {
	      $(document).trigger("error", data.message);
	    }
	}).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    }); 
  };

  self.execute = function () {
    $(document).trigger("executeStarted", self);
    $(".jHueNotify").hide();
    logGA('/execute/' + self.type());

    if (self.result.meta().length > 0) {
      self.close();
    }
    
    self.result.clear();
    self.progress(0);
    self.status('running');

    $.post("/spark/api/execute", {
      notebook: ko.mapping.toJSON(notebook),
      snippet: ko.mapping.toJSON(self)
    }, function (data) {
      if (data.status == 0) {
        $.each(data.handle, function (key, val) {
          self.result.handle()[key] = val;
        });

        self.result.hasResultset(data.handle.has_result_set);
        self.checkStatus();
      } else {
        self._ajax_error(data);
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
      self.status('failed');
    });
  };
  
  self.fetchResult = function(rows, startOver) {
    if (typeof startOver == "undefined") {
      startOver = true;
    }
    self.fetchResultData(rows, startOver);
    //self.fetchResultMetadata(rows); 
  };

  self.fetchResultData = function(rows, startOver) {
    $.post("/spark/api/fetch_result_data", {
      notebook: ko.mapping.toJSON(notebook),
      snippet: ko.mapping.toJSON(self),
      rows: rows,
      startOver: startOver
    }, function (data) {
      if (data.status == 0) {
        rows -= data.result.data.length;

        if (self.result.meta().length == 0) {
   	      data.result.meta.unshift({type: "INT_TYPE", name: "", comment: null});
   	      self.result.meta(data.result.meta);
        }

        var _initialIndex = self.result.data().length;
        var _tempData = [];
        $.each(data.result.data, function (index, row) {
          row.unshift(_initialIndex + index);
          self.result.data.push(row);
          _tempData.push(row);
        });

        $(document).trigger("renderData", {data: _tempData, snippet: self, initial: _initialIndex == 0});

        if (data.result.has_more && rows > 0) {
          setTimeout(function () {
            self.fetchResultData(rows, false);
          }, 500);
        }
      } else {
    	 self._ajax_error(data);
       $(document).trigger("renderDataError", {snippet: self});
      }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.fetchResultMetadata = function () {
    $.post("/spark/api/fetch_result_metadata", {
        notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self),
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

  self.checkStatus = function() {	  
    $.post("/spark/api/check_status", {
       notebook: ko.mapping.toJSON(notebook),
       snippet: ko.mapping.toJSON(self)
	  }, function (data) {
	    if (data.status == 0) {
          self.status(data.query_status.status);
          self.getLogs();

          if (self.status() == 'running') {
        	self.checkStatusTimeout = setTimeout(self.checkStatus, 1000);        	
          } 
          else if (self.status() == 'available') {
        	self.fetchResult(100);
        	self.progress(100);
          }
	    } else {
	      self._ajax_error(data);
	    }
	}).fail(function (xhr, textStatus, errorThrown) {
     $(document).trigger("error", xhr.responseText);
     self.status('failed');
    });
  };
  
  self.cancel = function() {
	if (self.checkStatusTimeout != null) {
	  clearTimeout(self.checkStatusTimeout);
	  self.checkStatusTimeout = null;
	}
	
    $.post("/spark/api/cancel_statement", {
        notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self)
 	  }, function (data) {
 	    if (data.status == 0) {
 	      self.status('canceled'); 
 	    } else {
 	      self._ajax_error(data);
 	    }
 	}).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
      self.status('failed');
    });
  };
  
  self.close = function() {
	if (self.checkStatusTimeout != null) {
	  clearTimeout(self.checkStatusTimeout);
	  self.checkStatusTimeout = null;
	}
	
    $.post("/spark/api/close_statement", {
        notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self)
 	  }, function (data) {
 	    if (data.status == 0) {
 	      self.status('closed'); 
 	    } else {
 	      self._ajax_error(data);
 	    }
 	}).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
      self.status('failed');
    });
  };
  
  self.getLogs = function() {
    $.post("/spark/api/get_logs", {
        notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self)
 	  }, function (data) {
 	    if (data.status == 0) {
 	      self.result.logs(data.logs); // Way to append?
 	      self.progress(data.progress);
 	    } else {
 	      self._ajax_error(data);
 	    }
 	}).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
      self.status('failed');
    });
  };
  
  self.init = function() {
	if (self.status() == 'running') {
	  self.checkStatus();
	} 
	
	if (self.status() != 'loading' && self.status() != 'ready') {
	  self.getLogs();	
	}
  };
}



var Notebook = function (vm, notebook) {
  var self = this;

  self.id = ko.observable(typeof notebook.id != "undefined" && notebook.id != null ? notebook.id : null);
  self.uuid = ko.observable(typeof notebook.uuid != "undefined" && notebook.uuid != null ? notebook.uuid : UUID());
  self.name = ko.observable(typeof notebook.name != "undefined" && notebook.name != null ? notebook.name : 'My Notebook');
  self.snippets = ko.observableArray();
  self.selectedSnippet = ko.observable(vm.availableSnippets()[0].type());
  self.sessions = ko.mapping.fromJS(typeof notebook.sessions != "undefined" && notebook.sessions != null ? notebook.sessions : []); 

  self.getSession = function(session_type) {
    var _s = null;
    $.each(self.sessions(), function (index, s) {
      if (s.type() == session_type) {
        _s = s;
        return false;
      }
    });
    return _s;
  };
  
  self.addSession = function(session) {
	var toRemove = []
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
  
  self.addSnippet = function(snippet) {
	var _snippet = new Snippet(vm, self, snippet);
	self.snippets.push(_snippet);
	
	if (self.getSession(_snippet.type()) == null) {
	  _snippet.create_session();	  
    } else {
      _snippet.status('ready');
    }

	_snippet.init();
  };  

  self.newSnippet = function() {
	 var _snippet = new Snippet(vm, self, {type: self.selectedSnippet(), result: {}});	  
	 self.snippets.push(_snippet);
	  
  	if (self.getSession(self.selectedSnippet()) == null) {
  	  _snippet.create_session();
  	}
    else {
      _snippet.status('ready');
    }
    $(document).trigger("snippetAdded", _snippet);
  };  
  
  if (notebook.snippets) {
    $.each(notebook.snippets, function(index, snippet) {
      self.addSnippet(snippet);
    });
  } 
  
  self.save = function () {
    $.post("/spark/api/notebook/save", {
        "notebook": ko.mapping.toJSON(self)
    }, function (data) {
      if (data.status == 0) {
        self.id(data.id);
        $(document).trigger("info", data.message);
        if (window.location.search.indexOf("notebook") == -1) {
          window.location.hash = '#notebook=' + data.id;
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
    $.post("/spark/api/notebook/close", {
        "notebook": ko.mapping.toJSON(self)
    }, function (data) {
   }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };
}


function EditorViewModel(notebooks, options) {
  var self = this;

  self.notebooks = ko.observableArray();
  self.selectedNotebook = ko.observable();

  self.isEditing = ko.observable(false);
  self.isEditing.subscribe(function(newVal){
    $(document).trigger("editingToggled");
  });
  self.toggleEditing = function () {
    self.isEditing(! self.isEditing());
  };

  self.isAssistVisible = ko.observable(options.assistVisible);
  self.toggleAssist = function () {
    self.isAssistVisible(! self.isAssistVisible());
    $(document).trigger("toggleAssist");
  };
  self.isAssistVisible = ko.observable(options.assistVisible);

  self.assistContent = ko.observable();
  self.assistSelectedMainObject = ko.observable();

  self.availableSnippets = ko.mapping.fromJS(options.languages);
  self.snippetPlaceholders = options.snippet_placeholders;
  
  self.init = function() {
    $.each(notebooks, function(index, notebook) {
      self.loadNotebook(notebook);
      if (self.selectedNotebook() == null){
        self.selectedNotebook(self.notebooks()[0]);
      }
    });
  };

  self.loadNotebook = function(notebook) {
    var _n = new Notebook(self, notebook);
    self.notebooks.push(_n);
    if (_n.snippets().length > 0){
      _n.selectedSnippet(_n.snippets()[_n.snippets().length - 1].type());
    }
  };

  self.newNotebook = function() {
	self.notebooks.push(new Notebook(self, {}));
    self.selectedNotebook(self.notebooks()[self.notebooks().length - 1]);
  };

  self.saveNotebook = function() {
    self.selectedNotebook().save();
  };
}


function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('editor/' + page);
  }
}
