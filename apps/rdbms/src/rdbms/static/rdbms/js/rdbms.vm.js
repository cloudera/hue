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


function RdbmsViewModel() {
  var self = this;

  self.servers = ko.observableArray();
  self.selectedServer = ko.observable(0);
  self.databases = ko.observableArray();
  self.selectedDatabase = ko.observable(0);
  self.query = ko.mapping.fromJS({
    'id': -1,
    'query': '',
    'name': null,
    'description': null,
    'errors': []
  });
  self.rows = ko.observableArray();
  self.columns = ko.observableArray();
  self.resultsEmpty = ko.observable(false);
  self.isExecuting = ko.observable(false);

  self.server = ko.computed({
    'read': function() {
      if (self.servers().length > 0) {
        return self.servers()[self.selectedServer()];
      } else{
        return null;
      }
    },
    'write': function(value) {
      var filtered = $.each(self.servers(), function(index, server) {
        if (server.name() == value) {
          self.selectedServer(index);
        }
      });
    }
  });

  self.database = ko.computed({
    'read': function() {
      if (self.databases()) {
        return self.databases()[self.selectedDatabase()];
      } else{
        return "";
      }
    },
    'write': function(value) {
      self.selectedDatabase(self.databases.indexOf(value));
    }
  });

  self.getFirstDatabase = function() {
    if (self.databases()) {
      return self.databases()[0];
    } else {
      return null;
    }
  };

  self.getServerNiceName = function(value) {
    return self.servers[value];
  };

  self.updateResults = function(results) {
    var rows = [];
    self.columns.removeAll();  // Needed for datatables to refresh properly.
    if (results.columns != null) {
      results.columns.unshift("");
    }
    self.columns(results.columns ? results.columns : []);
    self.rows.removeAll();
    self.rows(results.rows);
  };

  self.updateServers = function(servers) {
    var newServers = [];
    $.each(servers, function(name, nice_name) {
      newServers.push({
        'name': ko.observable(name),
        'nice_name': ko.observable(nice_name)
      });
    });
    self.servers(newServers);

    var last = $.totalStorage('hueRdbmsLastServer') || ((newServers[0].length > 0) ? newServers[0].name() : null);
    if (last) {
      self.server(last);
      $.each(self.servers(), function(index, server) {
        if (server.name() == last) {
          self.chosenServer(server);
        }
      });
    }

    $(document).trigger("update.chosen");
  };

  self.updateDatabases = function(databases) {
    self.databases(databases);

    var key = 'hueRdbmsLastDatabase-' + self.server().name();
    var last = $.totalStorage(key) || ((databases.length > 0) ? databases[0] : null);
    if (last) {
      self.database(last);
      self.chosenDatabase(last);
    }

    $(document).trigger("update.chosen");
  };

  self.updateQuery = function(design) {
    self.query.query(design.query);
    self.query.id(design.id);
    self.query.name(design.name);
    self.query.description(design.desc);
    self.database(design.database);
    self.server(design.server);
  };

  self.chosenServer = ko.observable();

  self.initialChoose = true;
  self.chosenServer.subscribe(function(value){
    $.each(self.servers(), function(index, server) {
      if (server.name() == value.name()) {
        self.selectedServer(index);
      }
    });
    if (self.initialChoose){
      self.initialChoose = false;
    }
    else {
      $.totalStorage('hueRdbmsLastServer', self.server().name());
    }
    self.fetchDatabases();
  });

  self.chosenDatabase = ko.observable();

  var error_fn = function(jqXHR, status, errorThrown) {
    self.isExecuting(false);
    try {
      $(document).trigger('server.error', JSON.parse(jqXHR.responseText));
    } catch(e) {
      $(document).trigger('server.unmanageable_error', jqXHR.responseText);
    }
  };

  self.explainQuery = function() {
    var data = ko.mapping.toJS(self.query);
    data.database = self.database();
    data.server = self.server().name();
    var request = {
      url: '/rdbms/api/explain/',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        self.query.errors.removeAll();
        if (data.status === 0) {
          $(document).trigger('explain.query', data);
          self.updateResults(data.results);
          self.query.id(data.design);
          self.resultsEmpty(data.results.rows.length === 0);
          $(document).trigger('explained.query', data);
        } else {
          self.query.errors.push(data.message);
        }
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.fetchQuery = function(id) {
    var _id = id || self.query.id();
    if (_id && _id != -1) {
      var request = {
        url: '/rdbms/api/query/' + _id + '/get',
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
      data['database'] = self.database();
      var url = '/rdbms/api/query/';
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
    $(document).trigger('start_execution.query');
    self.isExecuting(true);
    var data = ko.mapping.toJS(self.query);
    data.database = self.database();
    data.server = self.server().name();
    var request = {
      url: '/rdbms/api/execute/',
      dataType: 'text',
      type: 'POST',
      success: function(data) {
        data = JSON.bigdataParse(data);
        self.query.errors.removeAll();
        if (data.status === 0) {
          $(document).trigger('execute.query', data);
          self.updateResults(data.results);
          self.query.id(data.design);
          self.resultsEmpty(data.results.rows.length === 0);
          self.isExecuting(false);
          $(document).trigger('executed.query', data);
        } else {
          self.isExecuting(false);
          self.query.errors.push(data.message);
        }
      },
      error: error_fn,
      data: data
    };
    $.ajax(request);
  };

  self.fetchServers = function() {
    var request = {
      url: '/rdbms/api/servers/',
      dataType: 'json',
      type: 'GET',
      success: function(data) {
        self.updateServers(data.servers);
        self.fetchDatabases();
      },
      error: error_fn
    };
    $.ajax(request);
  };

  self.fetchDatabases = function() {
    if (self.server()) {
      var request = {
        url: '/rdbms/api/servers/' + self.server().name() + '/databases/',
        dataType: 'json',
        type: 'GET',
        success: function(data) {
          self.updateDatabases(data.databases);
        },
        error: error_fn
      };
      $.ajax(request);
    }
  };
}
