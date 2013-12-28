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


var connections = (function($) {
  var ConnectionModel = koify.Model.extend({
    'id': -1,
    'name': null,
    'connector': [],
    'connector_id': 0,
    'creation_date': null,
    'creation_user': null,
    'update_date': null,
    'update_user': null,
    'framework': [],
    'initialize': function(attrs) {
      var self = this;
      var _attrs = $.extend(true, {}, attrs);
      _attrs = transform_keys(_attrs, {
        'connector-id': 'connector_id'
      });
      _attrs = transform_values(_attrs, {
        'connector': to_forms,
        'framework': to_forms
      });
      return _attrs;
    }
  });

  var Connection = koify.Node.extend({
    'identifier': 'connection',
    'persists': true,
    'model_class': ConnectionModel,
    'base_url': '/sqoop/api/connections/',
    'initialize': function(options) {
      var self = this;
      self.parent.initialize.apply(self, arguments);
      self.selected = ko.observable();
      self.persisted = ko.computed(function() {
        return self.id() > -1;
      });
      self.connectionString = ko.computed(function() {
        var connection_string = null;
        $.each(self.connector(), function(index, form) {
          if (form.name() == 'connection') {
            $.each(form.inputs(), function(index, input) {
              if (input.name() == 'connection.connectionString') {
                connection_string = input.value();
              }
            });
          }
        });
        return connection_string;
      });
      self.jdbcDriver = ko.computed(function() {
        var jdbc_driver = null;
        $.each(self.connector(), function(index, form) {
          if (form.name() == 'connection') {
            $.each(form.inputs(), function(index, input) {
              if (input.name() == 'connection.jdbcDriver') {
                jdbc_driver = input.value();
              }
            });
          }
        });
        return jdbc_driver;
      });
      self.host = ko.computed(function() {
        var pattern = null;
        switch (self.jdbcDriver()) {
          case 'com.mysql.jdbc.Driver':
          pattern = /jdbc:mysql:\/\/([^\:\/]+).*/;
          break;
          case 'org.postgresql.Driver':
          pattern = /jdbc:postgresql:\/\/([^\:\/]+).*/;
          break;
          case 'oracle.jdbc.OracleDriver':
          pattern = /jdbc:oracle:thin:@([^\:\/]+).*/;
          break;
        }
        if (pattern) {
          var res = self.connectionString().match(pattern);
          if (res) {
            return res[1];
          } else {
            return null;
          }
        }
      });
      self.port = ko.computed(function() {
        var pattern = null;
        switch (self.jdbcDriver()) {
          case 'com.mysql.jdbc.Driver':
          pattern = /jdbc:mysql:\/\/[^\:\/]+:(\d+)\/.*/;
          break;
          case 'org.postgresql.Driver':
          pattern = /jdbc:postgresql:\/\/[^\:\/]+:(\d+)\/.*/;
          break;
          case 'oracle.jdbc.OracleDriver':
          pattern = /jdbc:oracle:thin:@[^\:\/]+:(\d+):.*/;
          break;
        }
        if (pattern) {
          var res = self.connectionString().match(pattern);
          if (res) {
            return res[1];
          } else {
            return null;
          }
        }
      });
      self.hostAndPort = ko.computed(function() {
        if (self.host()) {
          if (self.port()) {
            return self.host() + ":" + self.port();
          } else {
            return self.host();
          }
        } else {
          return null;
        }
      });
      self.database = ko.computed(function() {
        var pattern = null;
        switch (self.jdbcDriver()) {
          case 'com.mysql.jdbc.Driver':
          pattern = /jdbc:mysql:\/\/.*?\/(.*)/;
          break;
          case 'org.postgresql.Driver':
          pattern = /jdbc:postgresql:\/\/.*?\/(.*)/;
          break;
          case 'oracle.jdbc.OracleDriver':
          pattern = /jdbc:oracle:thin:@.*?:.*?:(.*)/;
          break;
        }
        if (pattern) {
          var res = self.connectionString().match(pattern);
          if (res) {
            return res[1];
          } else {
            return null;
          }
        }
      });
      self.username = ko.computed(function() {
        var username = null;
        $.each(self.connector(), function(index, form) {
          if (form.name() == 'connection') {
            $.each(form.inputs(), function(index, input) {
              if (input.name() == 'connection.username') {
                username = input.value();
              }
            });
          }
        });
        return username;
      });
      self.password = ko.computed(function() {
        var password = null;
        $.each(self.connector(), function(index, form) {
          if (form.name() == 'connection') {
            $.each(form.inputs(), function(index, input) {
              if (input.name() == 'connection.password') {
                password = input.value();
              }
            });
          }
        });
        return password;
      });
      self.type = ko.computed(function() {
        var conn_string = self.connectionString();
        if (!conn_string) {
          return "unknown";
        }

        var parts = conn_string.split(':');
        if (parts.length < 2) {
          return "unknown";
        }

        return parts[1];
      });
    },
    'map': function() {
      var self = this;
      var mapping_options = $.extend(true, {
        'ignore': ['parent', 'initialize']
      }, forms.MapProperties);
      if ('__ko_mapping__' in self) {
        ko.mapping.fromJS(self.model, mapping_options, self);
      } else {
        var mapped = ko.mapping.fromJS(self.model, mapping_options);
        $.extend(self, mapped);
      }
    },
  });

  function fetch_connections(options) {
    $(document).trigger('load.connections', [options]);
    var request = $.extend({
      url: '/sqoop/api/connections/',
      dataType: 'json',
      type: 'GET',
      success: fetcher_success('connections', Connection, options),
      error: fetcher_error('connections', Connection, options)
    }, options || {});
    $.ajax(request);
  }

  return {
    'ConnectionModel': ConnectionModel,
    'Connection': Connection,
    'fetchConnections': fetch_connections
  }
})($);
