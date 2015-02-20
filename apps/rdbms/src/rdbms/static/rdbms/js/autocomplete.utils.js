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

function rdbms_jsoncalls(options) {
  if (typeof RDBMS_AUTOCOMPLETE_BASE_URL != "undefined") {
    if (options.database === null) {
      $.getJSON(RDBMS_AUTOCOMPLETE_BASE_URL, options.onDataReceived);
    }
    if (options.database) {
      if (options.table) {
        $.getJSON(RDBMS_AUTOCOMPLETE_BASE_URL + "/servers/" + options.server + "/databases/" + options.database + "/tables/" + options.table + "/columns", options.onDataReceived);
      }
      else {
        $.getJSON(RDBMS_AUTOCOMPLETE_BASE_URL + "/servers/" + options.server + "/databases/" + options.database + "/tables", options.onDataReceived);
      }
    }
  }
  else {
    try {
      console.error("You need to specify a RDBMS_AUTOCOMPLETE_BASE_URL to use the autocomplete");
    }
    catch (e) {
    }
  }
}

function rdbms_hasExpired(timestamp){
  var TIME_TO_LIVE_IN_MILLIS = 600000; // 10 minutes
  return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
}

function rdbms_getTableAliases(textScanned) {
  var _aliases = {};
  var _val = textScanned; //codeMirror.getValue();
  var _from = _val.toUpperCase().indexOf("FROM ");
  if (_from > -1) {
    var _match = _val.toUpperCase().substring(_from).match(/ON|WHERE|GROUP|SORT|ORDER/);
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
}

function rdbms_tableHasAlias(tableName, textScanned) {
  var _aliases = rdbms_getTableAliases(textScanned);
  for (var alias in _aliases) {
    if (_aliases[alias] == tableName) {
      return true;
    }
  }
  return false;
}

function rdbms_getTableColumns(serverName, databaseName, tableName, textScanned, callback) {
  if (tableName.indexOf("(") > -1) {
    tableName = tableName.substr(tableName.indexOf("(") + 1);
  }

  var _aliases = rdbms_getTableAliases(textScanned);
  if (_aliases[tableName]) {
    tableName = _aliases[tableName];
  }

  if ($.totalStorage('rdbms_columns_' + serverName + '_' + databaseName + '_' + tableName) && $.totalStorage('rdbms_extended_columns_' + serverName + '_' + databaseName + '_' + tableName)) {
    callback($.totalStorage('rdbms_columns_' + serverName + '_' + databaseName + '_' + tableName), $.totalStorage('rdbms_extended_columns_' + serverName + '_' + databaseName + '_' + tableName));
    if ($.totalStorage('rdbms_timestamp_columns_' + serverName + '_' + databaseName + '_' + tableName) === null || rdbms_hasExpired($.totalStorage('rdbms_timestamp_columns_' + serverName + '_' + databaseName + '_' + tableName))){
      rdbms_jsoncalls({
        server: serverName,
        database: databaseName,
        table: tableName,
        onDataReceived: function (data) {
          if (typeof RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
            RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
          }
          if (data.error) {
            if (typeof RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON == "undefined" || data.code === null || RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON.indexOf(data.code) == -1){
              $(document).trigger('error', data.error);
            }
          }
          else {
            $.totalStorage('rdbms_columns_' + serverName + '_' + databaseName + '_' + tableName, (data.columns ? "* " + data.columns.join(" ") : "*"));
            $.totalStorage('rdbms_extended_columns_' + serverName + '_' + databaseName + '_' + tableName, (data.extended_columns ? data.extended_columns : []));
            $.totalStorage('rdbms_timestamp_columns_' + serverName + '_' + databaseName + '_' + tableName, (new Date()).getTime());
          }
        }
      });
    }
  }
  else {
    rdbms_jsoncalls({
      server: serverName,
      database: databaseName,
      table: tableName,
      onDataReceived: function (data) {
        if (typeof RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
          RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
        }
        if (data.error) {
          if (typeof RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON == "undefined" || data.code === null || RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON.indexOf(data.code) == -1){
            $(document).trigger('error', data.error);
          }
        }
        else {
          $.totalStorage('rdbms_columns_' + serverName + '_' + databaseName + '_' + tableName, (data.columns ? "* " + data.columns.join(" ") : "*"));
          $.totalStorage('rdbms_extended_columns_' + serverName + '_' + databaseName + '_' + tableName, (data.extended_columns ? data.extended_columns : []));
          $.totalStorage('rdbms_timestamp_columns_' + serverName + '_' + databaseName + '_' + tableName, (new Date()).getTime());
          callback($.totalStorage('rdbms_columns_' + serverName + '_' + databaseName + '_' + tableName), $.totalStorage('rdbms_extended_columns_' + serverName + '_' + databaseName + '_' + tableName));
        }
      }
    });
  }
}

function rdbms_getTables(serverName, databaseName, callback) {
  if ($.totalStorage('rdbms_tables_' + serverName + '_' + databaseName)) {
    callback($.totalStorage('rdbms_tables_' + serverName + '_' + databaseName));
    if ($.totalStorage('rdbms_timestamp_tables_' + serverName + '_' + databaseName) === null || rdbms_hasExpired($.totalStorage('rdbms_timestamp_tables_' + serverName + '_' + databaseName))){
      rdbms_jsoncalls({
        server: serverName,
        database: databaseName,
        onDataReceived: function (data) {
          if (typeof RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
            RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
          }
          if (data.error) {
            if (typeof RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON == "undefined" || data.code === null || RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON.indexOf(data.code) == -1){
              $(document).trigger('error', data.error);
            }
          }
          else {
            $.totalStorage('rdbms_tables_' + serverName + '_' + databaseName, data.tables.join(" "));
            $.totalStorage('rdbms_timestamp_tables_' + serverName + '_' + databaseName, (new Date()).getTime());
          }
        }
      });
    }
  }
  else {
    rdbms_jsoncalls({
      server: serverName,
      database: databaseName,
      onDataReceived: function (data) {
        if (typeof RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
          RDBMS_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
        }
        if (data.error) {
          if (typeof RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON == "undefined" || data.code === null || RDBMS_AUTOCOMPLETE_FAILS_SILENTLY_ON.indexOf(data.code) == -1){
            $(document).trigger('error', data.error);
          }
        }
        else {
          $.totalStorage('rdbms_tables_' + serverName + '_' + databaseName, data.tables.join(" "));
          $.totalStorage('rdbms_timestamp_tables_' + serverName + '_' + databaseName, (new Date()).getTime());
          callback($.totalStorage('rdbms_tables_' + serverName + '_' + databaseName));
        }
      }
    });
  }
}
