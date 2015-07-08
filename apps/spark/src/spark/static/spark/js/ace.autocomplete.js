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

  var TIME_TO_LIVE_IN_MILLIS = 86400000; // 1 day

  var hasExpired = function(timestamp){
    return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
  };


  /**
   *
   * @param options {object}
   * @param options.autocompleteBaseURL
   * @param options.autocompleteApp
   * @param options.autocompleteUser
   * @param options.autocompleteGlobalCallback
   * @param options.autocompleteFailsSilentlyOn
   * @param options.autocompleteFailsQuietlyOn
   *
   * @constructor
   */
  function Autocomplete (options) {
    this.options = options;
  }

  Autocomplete.prototype.jsonCalls = function (options) {
    var _url = typeof options.autocompleteBaseURL != "undefined" ? options.autocompleteBaseURL : this.options.autocompleteBaseURL;
    if (_url != ""){
      if (options.database != null) {
        _url += options.database
      }
      if (options.table != null) {
        _url += "/" + options.table
      }

      $.ajax({
        type: "GET",
        url: _url + "?" + Math.random(),
        success: options.onDataReceived,
        async: typeof options.sync == "undefined"
      });
    }
  };

  Autocomplete.prototype.getTableAliases = function (textScanned) {
    var _aliases = {};
    var _val = textScanned.split("\n").join(" ");
    var _from = _val.toUpperCase().indexOf("FROM ");
    if (_from > -1) {
      var _match = _val.toUpperCase().substring(_from).match(/ ON| LIMIT| WHERE| GROUP| SORT| ORDER BY|;/);
      var _to = _val.length;
      if (_match) {
        _to = _match.index;
      }
      var _found = _val.substr(_from, _to).replace(/(\r\n|\n|\r)/gm, "").replace(/from/gi, "").replace(/join/gi, ",").split(",");
      for (var i = 0; i < _found.length; i++) {
        var _tablealias = $.trim(_found[i]).split(" ");
        if (_tablealias.length > 1) {
          _aliases[_tablealias[1]] = _tablealias[0];
        }
      }
    }
    return _aliases;
  };

  Autocomplete.prototype.getTotalStorageUserPrefix = function () {
    var _app = "";
    if (typeof this.options.autocompleteApp != "undefined") {
      _app = this.options.autocompleteApp;
    }
    if (typeof this.options.autocompleteUser != "undefined") {
      return _app + "_" + this.options.autocompleteUser + "_";
    }
    return (_app != "" ? _app + "_" : "");
  };

  Autocomplete.prototype.getTableColumns = function (databaseName, tableName, textScanned, callback) {
    var self = this;
    if (tableName.indexOf("(") > -1) {
      tableName = tableName.substr(tableName.indexOf("(") + 1);
    }

    var _aliases = self.getTableAliases(textScanned);
    if (_aliases[tableName]) {
      tableName = _aliases[tableName];
    }

    if ($.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName) != null && $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName) != null) {
      callback($.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName), $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName));
      if ($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName) == null || hasExpired($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName))){
        self.jsonCalls({
          database: databaseName,
          table: tableName,
          onDataReceived: function (data) {
            if (typeof self.options.autocompleteGlobalCallback == "function") {
              self.options.autocompleteGlobalCallback(data);
            }
            if (data.error) {
              self.errorHandler(data);
            }
            else {
              $.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName, (data.columns ? "* " + data.columns.join(" ") : "*"));
              $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName, (data.extended_columns ? data.extended_columns : []));
              $.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName, (new Date()).getTime());
            }
          }
        });
      }
    }
    else {
      self.jsonCalls({
        database: databaseName,
        table: tableName,
        onDataReceived: function (data) {
          if (typeof self.options.autocompleteGlobalCallback == "function") {
            self.options.autocompleteGlobalCallback(data);
          }
          if (data.error) {
            self.errorHandler(data);
          }
          else {
            $.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName, (data.columns ? "* " + data.columns.join(" ") : "*"));
            $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName, (data.extended_columns ? data.extended_columns : []));
            $.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName, (new Date()).getTime());
            callback($.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName), $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName));
          }
        }
      });
    }
  };

  Autocomplete.prototype.tableHasAlias = function (tableName, textScanned) {
    var self = this;
    var _aliases = self.getTableAliases(textScanned);
    for (var alias in _aliases) {
      if (_aliases[alias] == tableName) {
        return true;
      }
    }
    return false;
  };

  Autocomplete.prototype.getTables = function (databaseName, callback) {
    var self = this;
    if ($.totalStorage(self.getTotalStorageUserPrefix() + 'tables_' + databaseName) != null) {
      callback($.totalStorage(self.getTotalStorageUserPrefix() + 'tables_' + databaseName));
      if ($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName) == null || hasExpired($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName))){
        self.jsonCalls({
          database: databaseName,
          onDataReceived: function (data) {
            if (typeof self.options.autocompleteGlobalCallback == "function") {
              self.options.autocompleteGlobalCallback(data);
            }
            if (data.error) {
              self.errorHandler(data);
            }
            else {
              $.totalStorage(self.getTotalStorageUserPrefix() + 'tables_' + databaseName, data.tables.join(" "));
              $.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName, (new Date()).getTime());
            }
          }
        });
      }
    }
    else {
      self.jsonCalls({
        database: databaseName,
        onDataReceived: function (data) {
          if (typeof self.options.autocompleteGlobalCallback == "function") {
            self.options.autocompleteGlobalCallback(data);
          }
          if (data.error) {
            self.errorHandler(data);
          }
          else {
            if (data.tables) {
              $.totalStorage(self.getTotalStorageUserPrefix() + 'tables_' + databaseName, data.tables.join(" "));
              $.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName, (new Date()).getTime());
              callback($.totalStorage(self.getTotalStorageUserPrefix() + 'tables_' + databaseName));
            }
          }
        }
      });
    }
  };

  Autocomplete.prototype.getDatabases = function (callback) {
    var self = this;
    if ($.totalStorage(self.getTotalStorageUserPrefix() + 'databases') != null) {
      if (callback) {
        callback($.totalStorage(self.getTotalStorageUserPrefix() + 'databases'));
      }
      if ($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_databases') == null || hasExpired($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_databases'))){
        this.jsonCalls({
          onDataReceived: function (data) {
            if (typeof self.options.autocompleteGlobalCallback == "function") {
              self.options.autocompleteGlobalCallback(data);
            }
            if (data.error) {
              self.errorHandler(data);
            }
            else {
              $.totalStorage(self.getTotalStorageUserPrefix() + 'databases', data.databases);
              $.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_databases', (new Date()).getTime());
            }
          }
        });
      }
    }
    else {
      this.jsonCalls({
        onDataReceived: function (data) {
          if (typeof self.options.autocompleteGlobalCallback == "function") {
            self.options.autocompleteGlobalCallback(data);
          }
          if (data.error) {
            self.errorHandler(data);
          }
          else {
            if (data.databases) {
              $.totalStorage(self.getTotalStorageUserPrefix() + 'databases', data.databases);
              $.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_databases', (new Date()).getTime());
              if (callback) {
                callback($.totalStorage(self.getTotalStorageUserPrefix() + 'databases'));
              }
            }
          }
        }
      });
    }
  };

  Autocomplete.prototype.errorHandler = function (data) {
    var self = this;
    $(document).trigger('error.autocomplete');
    if (typeof self.options.autocompleteFailsSilentlyOn == "undefined" || data.code == null || self.options.autocompleteFailsSilentlyOn.indexOf(data.code) == -1){
      if (typeof self.options.autocompleteFailsQuietlyOn  != "undefined" && self.options.autocompleteFailsQuietlyOn.indexOf(data.code) > -1){
        $(document).trigger('info', data.error);
      }
      else {
        $(document).trigger('error', data.error);
      }
    }
  }















