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


var autocomplete = (function($) {
  function cas(server_type, database, table, value) {
    var key = '';
    if (server_type) {
      if (database) {
        if (table) {
          key = 'sqoop_' + server_type + "_" + database + "_" + table;
        } else {
          key = 'sqoop_' + server_type + "_" + database;
        }
      } else {
        key = 'sqoop_' + server_type;
      }
    }
    var val = $.totalStorage(key) || [];
    if (value) {
      $.totalStorage(key, value);
    }
    return val;
  }

  var loading = {
    'databases': false,
    'tables': false,
    'columns': false
  };

  return {
    'databases': function(server_type) {
      if (!loading.databases && server_type) {
        loading.databases = true;
        $(document).trigger('fetch.databases', []);
        var request = {
          url: '/sqoop/api/autocomplete/databases/?server_type=' + server_type,
          dataType: 'json',
          type: 'GET',
          success: function(data) {
            var databases = cas(server_type, null, null, data.databases);
            $(document).trigger('fetched.databases', [databases]);
          },
          error: function() {},
          always: function() {
            loading.databases = false;
          }
        };
        $.ajax(request);
      }
      return cas(server_type);
    },
    'tables': function(server_type, database) {
      if (!loading.tables && server_type && database) {
        loading.tables = true;
        $(document).trigger('fetch.tables', []);
        var request = {
          url: '/sqoop/api/autocomplete/databases/' + database + '/tables?server_type=' + server_type,
          dataType: 'json',
          type: 'GET',
          success: function(data) {
            var tables = cas(server_type, database, null, data.tables);
            $(document).trigger('fetched.tables', [tables]);
          },
          error: function() {},
          always: function() {
            loading.tables = false;
          }
        };
        $.ajax(request);
      }
      return cas(server_type, database);
    },
    'columns': function(server_type, database, table) {
      if (!loading.columns && server_type && database && table) {
        loading.columns = true;
        $(document).trigger('fetch.columns', []);
        var request = {
          url: '/sqoop/api/autocomplete/databases/' + database + '/tables/' + table + '/columns?server_type=' + server_type,
          dataType: 'json',
          type: 'GET',
          success: function(data) {
            var columns = cas(server_type, database, table, data.columns);
            $(document).trigger('fetched.columns', [columns]);
          },
          error: function() {},
          always: function() {
            loading.columns = false;
          }
        };
        $.ajax(request);
      }
      return cas(server_type, database, table);
    }
  };
})($);