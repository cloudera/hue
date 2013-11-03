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

  self.selectedServer = ko.observable();
  self.servers = ko.observable({});
  self.selectedDatabase = ko.observable(0);
  self.databases = ko.observableArray([]);
  self.query = ko.mapping.fromJS({
    'id': -1,
    'query': '',
    'name': null,
    'description': null,
    'errors': []
  });
  self.rows = ko.observableArray();
  self.columns = ko.observableArray();

  self.filter = ko.observable("");
  self.isLoading = ko.observable(false);
  self.isReady = ko.observable(false);

  self.server = ko.computed({
    'read': function() {
      if (self.servers() && self.selectedServer()) {
        return self.servers()[self.selectedServer()];
      } else{
        return "";
      }
    },
    'write': function(value) {
      self.selectedServer(value);
    }
  });

  self.database = ko.computed({
    'read': function() {
      if (self.databases) {
        return self.databases()[self.selectedDatabase()];
      } else{
        return "";
      }
    },
    'write': function(value) {
      self.selectedDatabase(self.databases.indexOf(value));
    }
  });

  self.selectedServer.subscribe(function(value) {
    self.fetchDatabases();
  });

  self.updateResults = function(results) {
    var rows = [];
    self.columns(results.columns);
    $.each(results.rows, function(i, result_row) {
      var row = [];
      $.each(self.columns(), function(j, column) {
        row.push(result_row[column]);
      });
      rows.push(row);
    });
    self.rows(rows);
  };

  self.updateServers = function(servers) {
    self.servers(servers);
    if (servers) {
      self.selectedServer(Object.keys(servers)[0]);
    }
  };

  self.updateDatabases = function(databases) {
    self.databases(databases);
    self.selectedDatabase.valueHasMutated();
  };

  self.updateQuery = function(design) {
    self.query.query(design.query);
    self.query.id(design.id);
    self.query.name(design.name);
    self.query.description(design.desc);
    self.database(design.database);
    self.server(design.server);
  };

  self.chooseServer = function(value, e) {
    self.selectedServer(value);
  };

  self.chooseDatabase = function(value, e) {
    self.selectedDatabase(self.databases.indexOf(value));
  };

  self.explainQuery = function() {
    var data = ko.mapping.toJS(self.query);
    data.database = self.database();
    data.server = self.selectedServer();
    var request = {
      url: '/rdbms/api/explain/',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        if (data.status === 0) {
          $(document).trigger('explain.query', data);
          self.updateResults(data.results);
          self.query.id(data.design);
          $(document).trigger('explained.query', data);
        } else {
          self.query.errors.removeAll();
          self.query.errors.push(data.message);
        }
      },
      error: $.noop,
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
        error: $.noop
      };
      $.ajax(request);
    }
  };

  self.saveQuery = function() {
    var self = this;
    if (self.query.query() && self.query.name()) {
      var data = ko.mapping.toJS(self.query);
      data['desc'] = data['description'];
      data['server'] = self.selectedServer();
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
    var data = ko.mapping.toJS(self.query);
    data.database = self.database();
    data.server = self.selectedServer();
    var request = {
      url: '/rdbms/api/execute/',
      dataType: 'json',
      type: 'POST',
      success: function(data) {
        if (data.status === 0) {
          $(document).trigger('execute.query', data);
          self.updateResults(data.results);
          self.query.id(data.design);
          $(document).trigger('executed.query', data);
        } else {
          self.query.errors.removeAll();
          self.query.errors.push(data.message);
        }
      },
      error: $.noop,
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
      error: $.noop
    };
    $.ajax(request);
  };

  self.fetchDatabases = function() {
    if (self.selectedServer()) {
      var request = {
        url: '/rdbms/api/servers/' + self.selectedServer() + '/databases/',
        dataType: 'json',
        type: 'GET',
        success: function(data) {
          self.updateDatabases(data.databases);
        },
        error: $.noop
      };
      $.ajax(request);
    }
  };
}
