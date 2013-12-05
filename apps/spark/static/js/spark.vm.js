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


function sparkViewModel() {
  var self = this;

  self.appNames = ko.observableArray(); // List of jars
  self.selectedAppName = ko.observable(0);
  self.autoContext = ko.observable(true);
  self.contexts = ko.observableArray(); // List of contexts
  self.selectedContext = ko.observable(0);
  self.classPathes = ko.observableArray(); // Read from upload or edit manually or better API
  self.classPath = ko.observable('spark.jobserver.WordCountExample');
  self.query = ko.mapping.fromJS({
    'id': -1,
    'jobId': null,
    'context': null,
    'query': '', // query == params
    'name': null,
    'description': null,
    'errors': []
  });
  self.rows = ko.observableArray();
  self.resultsEmpty = ko.observable(false);

  self.appName = ko.computed({
    'read': function() {
      if (self.appNames().length > 0) {
        return self.appNames()[self.selectedAppName()];
      } else{
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
      } else{
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
    $.each(results, function(key, value) {
      newRows.push([key, value]);
    });
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

    var last = $.totalStorage('hueSparkLastAppName') || (newAppNames.length > 0 ? newAppNames[0].name() : null);
    if (last) {
      self.appName(last);
    }
  };

  self.updateContexts = function(contexts) {
    var newContexts = [];
    $.each(contexts, function(index, value) {
      newContexts.push(createDropdownItem(value));
    });
    self.contexts(newContexts);

    var last = $.totalStorage('hueSparkLastContext') || (newContexts.length > 0 ? newContexts[0].name() : null);
    if (last) {
      self.context(last);
    }
  };

  function createDropdownItem(item) {
    return {
      'name': ko.observable(item),
      'nice_name': ko.observable(item)
    };
  };

  self.updateQuery = function(design) {
    self.query.query(design.query);
    self.query.id(design.id);
    self.query.name(design.name);
    self.query.description(design.desc);
    self.server(design.server);
  };

  self.chooseAppName = function(value, e) {
    $.each(self.appNames(), function(index, appName) {
      if (appName.name() == value.name()) {
        self.selectedAppName(index);
      }
    });
    $.totalStorage('hueSparkLastAppName', self.appName().name());
  };

  self.chooseContext = function(value, e) {
    $.each(self.contexts(), function(index, context) {
      if (context.name() == value.name()) {
        self.selectedContext(index);
      }
    });
    $.totalStorage('hueSparkLastContext', self.context().name());
  };

  var error_fn = function(jqXHR, status, errorThrown) {
    try {
      $(document).trigger('server.error', $.parseJSON(jqXHR.responseText));
    } catch(e) {
      $(document).trigger('server.unmanageable_error', jqXHR.responseText);
    }
  };

  self.fetchQuery = function(id) {
    var _id = id || self.query.id();
    if (_id && _id != -1) {
      var request = {
        url: '/spark/api/query/' + _id + '/get',
        dataType: 'json',
        type: 'GET',
        success: function(data) {
          self.updateQuery(data.design);
        },
        error: error_fn
      };
      $.ajax(request);
    }
  };

  self.saveQuery = function() {
    var self = this;
    if (self.query.query() && self.query.name()) {
      var data = ko.mapping.toJS(self.query);
      data['desc'] = data['description'];
      data['server'] = self.server().name();
      var url = '/spark/api/query/';
      if (self.query.id() && self.query.id() != -1) {
        url += self.query.id() + '/';
      }
      var request = {
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function(data) {
          $(document).trigger('saved.query', data);
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
    data.context = self.context().name;
    var request = {
      url: '/spark/api/execute',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.query.errors.removeAll();
        if (data.status == 0) {
          $(document).trigger('execute.query', data);
          self.query.id(data.design);
          self.query.jobId(data.results.result.jobId);
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
      url: '/spark/api/job/' + self.query.jobId(),
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

  self.fetchAppNames = function() {
    var request = {
      url: '/spark/api/jars',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateAppNames(data.jars);
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.fetchContexts = function() {
    var request = {
      url: '/spark/api/contexts',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateContexts(data.contexts);
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.createContext = function() {
    var data = $("#createContextForm").serialize(); // Not koified
    var request = {
      url: '/spark/api/create_context',
      dataType: 'json',
      type: 'POST',
      success: function(result) {
        self.query.errors.removeAll();
        if (result.status == 'OK') {
      	  self.contexts().push(createDropdownItem(result.name));
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
}
