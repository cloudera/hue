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

var SparkParameter = function (property) {
  var self = this;

  self.name = ko.observable(property.name);
  self.value = ko.observable(property.value);
};

function sparkViewModel() {
  var self = this;

  self.appNames = ko.observableArray(); // List of jars
  self.selectedAppName = ko.observable(0);
  self.autoContext = ko.observable(true);
  self.contexts = ko.observableArray(); // List of contexts
  self.selectedContext = ko.observable(0);
  self.classPath = ko.observable('');

  self.autoContext.forEditing = ko.computed({
    read: function() {
        return this.autoContext().toString();
    },
    write: function(newValue) {
         this.autoContext(newValue === "true");
    },
    owner: this
  });

  self.query = ko.mapping.fromJS({
    'id': -1,
    'jobId': null,
    'name': null,
    'description': null,
    'errors': [],
    'appName': '',
    'classPath': '',
    'context': '',
    'autoContext': true,
    'params': []
  });

  self.rows = ko.observableArray();
  self.resultsEmpty = ko.observable(false);

  self.appName = ko.computed({
    'read': function() {
      if (self.appNames().length > 0) {
        return self.appNames()[self.selectedAppName()];
      } else {
        return null;
      }
    },
    'write': function(value) {
      var filtered = $.each(self.appNames(), function(index, appName) {
        if (appName.name() == value) {
          self.selectedAppName(index);
        }
      });
    }
  });

  self.context = ko.computed({
    'read': function() {
      if (self.contexts().length > 0) {
        return self.contexts()[self.selectedContext()];
      } else {
        return null;
      }
    },
    'write': function(value) {
      var filtered = $.each(self.contexts(), function(index, context) {
        if (context.name() == value) {
          self.selectedContext(index);
        }
      });
    }
  });

  self.updateResults = function(results) {
    self.rows.removeAll();
    var newRows = [];
    // Is a list of map
    if ($.inArray($.type(results), ['array', 'object']) != -1) {
      $.each(results, function(key, value) {
        newRows.push([key, value]);
      });
    } else {
      newRows.push([0, results]);
    }
    self.rows(newRows);
  };

  self.updateAppNames = function(appNames) {
    var newAppNames = [];
    $.each(appNames, function(key, value) {
      newAppNames.push({
        'name': ko.observable(key),
        'nice_name': ko.observable(key)
      });
    });
    self.appNames(newAppNames);

    // Load back appName or guess
    if (self.query.appName()) {
      viewModel.setAppName( self.query.appName());
    }
  };

  self.updateContexts = function(contexts) {
    var newContexts = [];
    $.each(contexts, function(index, value) {
      newContexts.push(createDropdownItem(value));
    });
    self.contexts(newContexts);

    var last = newContexts.length > 0 ? newContexts[0].name() : null;
    if (last) {
      self.context(last);
    }
  };

  self.addParam = function() {
    self.query.params.push(new SparkParameter({name: "", value: ""}));
  };

  self.removeParam = function() {
    self.query.params.remove(this);
  };

  function createDropdownItem(item) {
    return {
      'name': ko.observable(item),
      'nice_name': ko.observable(item)
    };
  };

  self.loadDesign = function(design) {
    self.query.id(design.id);
    self.query.name(design.name);
    self.query.description(design.desc);

    self.query.appName(design.appName);
    self.query.classPath(design.classPath);
    self.query.autoContext(design.autoContext);
    self.query.params(design.params);

    self.appName(design.appName);
    self.chooseAppName(self.appName());
    self.autoContext(design.autoContext);
    self.context(design.context);
    self.chooseContext(design.context);
    self.classPath(design.classPath);
  };

  self.chooseAppName = function(value, e) {
    $.each(self.appNames(), function(index, appName) {
      if (appName.name() == value.name()) {
        self.selectedAppName(index);
      }
    });
  };

  self.setAppName = function(name) {
    $.each(self.appNames(), function(index, appName) {
      if (appName.name() == name) {
        self.appName(name);
        self.selectedAppName(index);
      }
    });
  };

  self.chooseContext = function(value, e) {
    $.each(self.contexts(), function(index, context) {
      if (context.name() == value.name()) {
        self.selectedContext(index);
      }
    });
  };

  var error_fn = function(jqXHR, status, errorThrown) {
    try {
      $(document).trigger('server.error', $.parseJSON(jqXHR.responseText));
    } catch(e) {
      $(document).trigger('server.unmanageable_error', jqXHR.responseText);
    }
  };

  self.saveQuery = function() {
    var self = this;
    if (self.query.name()) {
      var data = ko.mapping.toJS(self.query);
      data['saveform-name'] = data['name'];
      data['saveform-desc'] = data['description'];
      data['query-appName'] = self.appName().name;
      data['query-classPath'] = self.classPath();
      data['query-autoContext'] = self.autoContext();
      data['query-context'] = self.context() ? self.context().name : '';
      data['query-params'] = ko.toJSON(self.query.params());

      var url = '/spark/api/save_query/';
      if (self.query.id() && self.query.id() != -1) {
        url += self.query.id() + '/';
      }
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          if (data.status == 0) {
            $(document).trigger('saved.query', data);
          } else {
        	self.query.errors.push(data.message);
          }
        },
        error: function() {
          $(document).trigger('error.query');
        },
        data: data
      };
      $.ajax(request);
    }
  };

  self.executeQuery = function() {
    var data = ko.mapping.toJS(self.query);
    data.appName = self.appName().name;
    data.classPath = self.classPath();
    data.autoContext = self.autoContext();
    data.context = self.context() ? self.context().name : '';
    data.params = ko.toJSON(self.query.params());
    var request = {
      url: '/spark/api/execute',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.query.errors.removeAll();
        self.rows.removeAll();
        if (data.status == 0) {
          $(document).trigger('execute.query', data);
          self.query.id(data.design);
          self.query.jobId(data.results.result.jobId);
          window.location.hash = 'jobId=' + data.results.result.jobId;
          self.query.context(data.results.result.context);
          self.checkQueryStatus();
        } else {
          self.query.errors.push(data.message);
        }
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.checkQueryStatus = function() {
  var timerId = 0;

    var request = {
      url: '/spark/api/job/' + self.query.jobId() + '?' + Math.random(),
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        // Script finished
        if (data.results.status == 'OK' || data.results.status == 'ERROR') {
          clearInterval(timerId);
          self.updateResults(data.results.result);
          self.resultsEmpty($.isEmptyObject(data.results.result));
          $(document).trigger('executed.query', data);
        }
      },
      error: error_fn
    };

    timerId = setInterval(function(){
      $.ajax(request);
    }, 1000);
  };

  self.openQuery = function(jobId) {
    self.query.jobId(jobId);
    $(document).trigger('execute.query');
    self.checkQueryStatus();
  };

  self.fetchAppNames = function() {
    var request = {
      url: '/spark/api/jars?' + Math.random(),
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        if (data.error != null) {
          $.jHueNotify.error(data.error);
        }
        else {
          self.updateAppNames(data.jars);
        }
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.fetchContexts = function() {
    var request = {
      url: '/spark/api/contexts?' + Math.random(),
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        if (data.error != null) {
          $.jHueNotify.error(data.error);
        }
        else {
          self.updateContexts(data.contexts);
        }
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.createContext = function() {
    var data = $("#createContextForm").serialize(); // Not koified
    $("#createContextBtn").attr("data-loading-text", $("#createContextBtn").text() + " ...");
    $("#createContextBtn").button("loading");
    var request = {
      url: '/spark/api/create_context',
      dataType: 'json',
      type: 'POST',
      success: function(result) {
        self.query.errors.removeAll();
        if (result.status == 'OK') {
          self.contexts.push(createDropdownItem(result.name));
          self.context(result.name);
          self.autoContext(false);
          $(document).trigger('created.context', data);
        } else {
          $(document).trigger('error', result.result);
        }
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.showFileChooser = function() {
    var inputPath = this;
    var path = inputPath.value().substr(0, inputPath.value().lastIndexOf("/"));
    $("#filechooser").jHueFileChooser({
      initialPath: path,
      onFileChoose: function (filePath) {
        inputPath.value(filePath);
        $("#chooseFile").modal("hide");
      },
      createFolder: false
    });
    $("#chooseFile").modal("show");
  };
}
