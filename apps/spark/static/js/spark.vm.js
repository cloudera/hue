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


var Snippet = function (notebook, snippet) {
  var self = this;
  
  self.id = ko.observable(typeof snippet.id != "undefined" && snippet.id != null ? snippet.id : UUID());
  self.type = ko.observable('hive-sql');
  self.statement = ko.observable('');
  self.status = ko.observable('finished');
  
  self.result = new Result(snippet, snippet.result);
  
  // init()
  // checkStatus()
  
  
  self.execute = function() {
	$(".jHueNotify").hide();
	logGA('/execute/' + self.type());	  
    
	self.result.clear();
    
    $.post("/spark/api/execute", {
        notebook: ko.mapping.toJSON(notebook),
        snippet: ko.mapping.toJSON(self)
      }, function (data) {
        if (data.status == 0) {
          $.each(data.handle, function(key, val) {
        	 self.result.handle()[key] = val;
          });

          self.status('running');
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
          self.status(data.query_status);
            
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
	  
  }
  
  self.cancel = function() {

  };
}



var Notebook = function (vm, notebook) {
  var self = this;

  self.id = ko.observable(typeof notebook.id != "undefined" && notebook.id != null ? notebook.id : UUID());
  self.snippets = ko.observableArray();

  self.addSnippet = function(snippet) {
	self.snippets.push(new Snippet(self, snippet));
  }  

  self.newSnippet = function() {
    self.snippets.push(new Snippet(self, {}));
  }  
  
  if (notebook.snippets) {
    $.each(notebook.snippets, function(index, snippet) {
      self.addSnippet(snippet);
    });
  }
}


function EditorViewModel(notebooks) {
  var self = this;

  self.notebooks = ko.observableArray();
  
  self.init = function() {
	$.each(notebooks, function(index, notebook) {
	  self.loadNotebook(notebook);
	});
  }

  self.loadNotebook = function(notebook) {
    self.notebooks.push(new Notebook(self, notebook));
  }

  self.newNotebook = function() {
	self.notebooks.push(new Notebook(self, {}));
  }
  
  self.save = function() {

  };
}


function logGA(page) {
  if (typeof trackOnGA == 'function') {
    trackOnGA('editor/' + page);
  }
}