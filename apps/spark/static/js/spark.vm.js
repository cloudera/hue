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

function s4() {
  return Math.floor((1 + Math.random()) * 0x10000)
      .toString(16)
      .substring(1);
}

function UUID() {
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}


var Result = function (snippet, result) {
  var self = this;

  self.id = ko.observable(typeof result != "undefined" && result.id != "undefined" && result.id != null ? result.id : UUID());
  self.type = ko.observable('table');
  self.handle = ko.observable({});
  self.meta = ko.observableArray();
  self.data = ko.observableArray();
  
  self.clear = function() {
	//self.handle = ko.observable({});
    self.meta.removeAll();
    self.data.removeAll();
  };  
}

var TYPE_EDITOR_MAP = {
  'hive': 'text/x-hiveql',
  'impala': 'text/x-impalaql',
  'python': 'text/x-python',
  'scala': 'text/x-scala',
  'pig': 'text/x-pig'
}

var Snippet = function (notebook, snippet) {
  var self = this;
  
  self.id = ko.observable(typeof snippet.id != "undefined" && snippet.id != null ? snippet.id : UUID());
  self.type = ko.observable(typeof snippet.type != "undefined" && snippet.type != null ? snippet.type : "hive");
  self.editorMode = ko.observable(TYPE_EDITOR_MAP[self.type()]);
  self.statement = ko.observable(typeof snippet.statement != "undefined" && snippet.statement != null ? snippet.statement : '');
  self.statement = ko.observable("");
  self.status = ko.observable("loading");

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


  self.result = new Result(snippet, snippet.result);
  
  // init()
  // checkStatus()

  self.create_session = function() {

    $.post("/spark/api/create_session", {
    	notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self)
	  }, function (data) {
	    if (data.status == 0) {
		  notebook.sessions.push(ko.mapping.fromJS(data.session));
	      self.status('ready');
	    }
	    else {
	      $(document).trigger("error", data.message);
	    }
	}).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
    
    
  };
  
  self.execute = function() {
	$(".jHueNotify").hide();
	logGA('/execute/' + self.type());	  
    
	self.result.clear();
	self.status('running');
    
    $.post("/spark/api/execute", {
        notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self)
      }, function (data) {
        if (data.status == 0) {
          $.each(data.handle, function(key, val) {
        	 self.result.handle()[key] = val;
          });

          self.checkStatus();
        }
        else {
          $(document).trigger("error", data.message);
        }
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });    
  };

  self.checkStatus = function() {
    $.post("/spark/api/check_status", {
       notebook: ko.mapping.toJSON(notebook),
       snippet: ko.mapping.toJSON(self)
	  }, function (data) {
	    if (data.status == 0) {
          self.status(data.query_status.status);
            
          if (self.status() == 'running') {
            setTimeout(self.checkStatus, 1000);            	
          } else {
        	self.fetchResult();
          }
	    }
	    else {
	      $(document).trigger("error", data.message);
	    }
	}).fail(function (xhr, textStatus, errorThrown) {
     $(document).trigger("error", xhr.responseText);
    });
  };

  self.fetchResult = function() {
    $.post("/spark/api/fetch_result", {
        notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self)
 	  }, function (data) {
 	    if (data.status == 0) {
 	      self.result.meta(data.result.meta);           
          self.result.data(data.result.data);

          // move resultsets to n rows
          // check if N rows fetched...
 	    }
 	    else {
 	      $(document).trigger("error", data.message);
 	    }
 	}).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  self.fetchResultMetadata = function() {
	  
  };
  
  self.cancel = function() {

  };
}



var Notebook = function (vm, notebook) {
  var self = this;

  self.id = ko.observable(typeof notebook.id != "undefined" && notebook.id != null ? notebook.id : null);
  self.uuid = ko.observable(typeof notebook.uuid != "undefined" && notebook.uuid != null ? notebook.uuid : UUID());
  self.name = ko.observable(typeof notebook.name != "undefined" && notebook.name != null ? notebook.name : 'My Notebook');
  self.snippets = ko.observableArray();
  self.selectedSnippet = ko.observable('scala');
  self.availableSnippets = ko.observableArray(['hive', 'scala', 'sql', 'python', 'pig', 'impala']); // presto, mysql, oracle, sqlite, postgres, phoenix
  self.sessions = ko.observableArray(); // [{'hive': {...}, 'scala': {...}]

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
  
  self.addSnippet = function(snippet) {
	var _snippet = new Snippet(self, snippet);
	self.snippets.push(_snippet);
	
	if (self.getSession(self.selectedSnippet()) == null) {
	  _snippet.create_session();
    }	
  };  

  self.newSnippet = function() {
	var snippet = new Snippet(self, {type: self.selectedSnippet()});	  
	self.snippets.push(snippet);
	  
	if (self.getSession(self.selectedSnippet()) == null) {
	  snippet.create_session();
	}
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
}


function EditorViewModel(notebooks) {
  var self = this;

  self.notebooks = ko.observableArray();
  self.selectedNotebook = ko.observable();

  self.isEditing = ko.observable(true);
  self.isEditing.subscribe(function(newVal){
    $(document).trigger("editingToggled");
  });
  self.toggleEditing = function () {
    self.isEditing(! self.isEditing());
  };


  self.init = function() {
    $.each(notebooks, function(index, notebook) {
      self.loadNotebook(notebook);
      if (self.selectedNotebook() == null){
        self.selectedNotebook(self.notebooks()[0]);
      }
    });
  };

  self.loadNotebook = function(notebook) {
    self.notebooks.push(new Notebook(self, notebook));
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