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


// Hive

function hac_jsoncalls(options) {
  if (typeof HIVE_AUTOCOMPLETE_BASE_URL != "undefined") {
    if (options.database == null) {
      $.getJSON(HIVE_AUTOCOMPLETE_BASE_URL, options.onDataReceived);
    }
    if (options.database != null) {
      if (options.table != null) {
        $.getJSON(HIVE_AUTOCOMPLETE_BASE_URL + options.database + "/" + options.table, options.onDataReceived);
      }
      else {
        $.getJSON(HIVE_AUTOCOMPLETE_BASE_URL + options.database + "/", options.onDataReceived);
      }
    }
  }
  else {
    try {
      console.error("You need to specify a HIVE_AUTOCOMPLETE_BASE_URL to use the autocomplete")
    }
    catch (e) {
    }
  }
}

function hac_hasExpired(timestamp){
  var TIME_TO_LIVE_IN_MILLIS = 86400000; // 1 day
  return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
}

function hac_getTableAliases(textScanned) {
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
}

function hac_getTotalStorageUserPrefix(){
  if (typeof HIVE_AUTOCOMPLETE_USER != "undefined") {
    return HIVE_AUTOCOMPLETE_USER + "_";
  }
  return "";
}

function hac_getTableColumns(databaseName, tableName, textScanned, callback) {
  if (tableName.indexOf("(") > -1) {
    tableName = tableName.substr(tableName.indexOf("(") + 1);
  }

  var _aliases = hac_getTableAliases(textScanned);
  if (_aliases[tableName]) {
    tableName = _aliases[tableName];
  }

  if ($.totalStorage(hac_getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName) != null && $.totalStorage(hac_getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName) != null) {
    callback($.totalStorage(hac_getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName), $.totalStorage(hac_getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName));
    if ($.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName) == null || hac_hasExpired($.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName))){
      hac_jsoncalls({
        database: databaseName,
        table: tableName,
        onDataReceived: function (data) {
          if (typeof HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
            HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
          }
          if (data.error) {
            hac_errorHandler(data);
          }
          else {
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName, (data.columns ? "* " + data.columns.join(" ") : "*"));
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName, (data.extended_columns ? data.extended_columns : []));
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName, (new Date()).getTime());
          }
        }
      });
    }
  }
  else {
    hac_jsoncalls({
      database: databaseName,
      table: tableName,
      onDataReceived: function (data) {
        if (typeof HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
          HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
        }
        if (data.error) {
          hac_errorHandler(data);
        }
        else {
          $.totalStorage(hac_getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName, (data.columns ? "* " + data.columns.join(" ") : "*"));
          $.totalStorage(hac_getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName, (data.extended_columns ? data.extended_columns : []));
          $.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName, (new Date()).getTime());
          callback($.totalStorage(hac_getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName), $.totalStorage(hac_getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName));
        }
      }
    });
  }
}

function hac_tableHasAlias(tableName, textScanned) {
  var _aliases = hac_getTableAliases(textScanned);
  for (var alias in _aliases) {
    if (_aliases[alias] == tableName) {
      return true;
    }
  }
  return false;
}

function hac_getTables(databaseName, callback) {
  if ($.totalStorage(hac_getTotalStorageUserPrefix() + 'tables_' + databaseName) != null) {
    callback($.totalStorage(hac_getTotalStorageUserPrefix() + 'tables_' + databaseName));
    if ($.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName) == null || hac_hasExpired($.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName))){
      hac_jsoncalls({
        database: databaseName,
        onDataReceived: function (data) {
          if (typeof HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
            HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
          }
          if (data.error) {
            hac_errorHandler(data);
          }
          else {
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'tables_' + databaseName, data.tables.join(" "));
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName, (new Date()).getTime());
          }
        }
      });
    }
  }
  else {
    hac_jsoncalls({
      database: databaseName,
      onDataReceived: function (data) {
        if (typeof HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
          HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
        }
        if (data.error) {
          hac_errorHandler(data);
        }
        else {
          if (data.tables) {
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'tables_' + databaseName, data.tables.join(" "));
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName, (new Date()).getTime());
            callback($.totalStorage(hac_getTotalStorageUserPrefix() + 'tables_' + databaseName));
          }
        }
      }
    });
  }
}

function hac_getDatabases(callback) {
  if ($.totalStorage(hac_getTotalStorageUserPrefix() + 'databases') != null) {
    callback($.totalStorage(hac_getTotalStorageUserPrefix() + 'databases'));
    if ($.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_databases') == null || hac_hasExpired($.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_databases'))){
      hac_jsoncalls({
        onDataReceived: function (data) {
          if (typeof HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
            HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
          }
          if (data.error) {
            hac_errorHandler(data);
          }
          else {
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'databases', data.databases);
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_databases', (new Date()).getTime());
          }
        }
      });
    }
  }
  else {
    hac_jsoncalls({
      onDataReceived: function (data) {
        if (typeof HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
          HIVE_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
        }
        if (data.error) {
          hac_errorHandler(data);
        }
        else {
          if (data.databases) {
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'databases', data.databases);
            $.totalStorage(hac_getTotalStorageUserPrefix() + 'timestamp_databases', (new Date()).getTime());
            callback($.totalStorage(hac_getTotalStorageUserPrefix() + 'databases'));
          }
        }
      }
    });
  }
}

function hac_errorHandler(data) {
  $(document).trigger('error.autocomplete');
  if (typeof HIVE_AUTOCOMPLETE_FAILS_SILENTLY_ON == "undefined" || data.code == null || HIVE_AUTOCOMPLETE_FAILS_SILENTLY_ON.indexOf(data.code) == -1){
    if (typeof HIVE_AUTOCOMPLETE_FAILS_QUIETLY_ON != "undefined" && HIVE_AUTOCOMPLETE_FAILS_QUIETLY_ON.indexOf(data.code) > -1){
      $(document).trigger('info', data.error);
    }
    else {
      $(document).trigger('error', data.error);
    }
  }
}


// Sentry

function sac_getTotalStorageUserPrefix(){
  if (typeof SENTRY_AUTOCOMPLETE_USER != "undefined") {
    return SENTRY_AUTOCOMPLETE_USER + "_";
  }
  return "";
}

function sac_jsoncalls(options) {
  if (typeof SENTRY_AUTOCOMPLETE_BASE_URL != "undefined") {
    $.getJSON(SENTRY_AUTOCOMPLETE_BASE_URL + '/roles', options.onDataReceived);
  }
  else {
    try {
      console.error("You need to specify a SENTRY_AUTOCOMPLETE_BASE_URL to use the autocomplete");
    }
    catch (e) {
    }
  }
}

function sac_hasExpired(timestamp){
  var TIME_TO_LIVE_IN_MILLIS = 600000; // 10 minutes
  return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
}

function sac_errorHandler(data) {
  $(document).trigger('error.autocomplete');
  if (typeof SENTRY_AUTOCOMPLETE_FAILS_QUIETLY_ON == "undefined" || data.code == null || SENTRY_AUTOCOMPLETE_FAILS_QUIETLY_ON.indexOf(data.code) == -1){
    if (typeof SENTRY_AUTOCOMPLETE_FAILS_QUIETLY_ON != "undefined" && SENTRY_AUTOCOMPLETE_FAILS_QUIETLY_ON.indexOf(data.code) > -1){
      $(document).trigger('info', data.error);
    }
    else {
      $(document).trigger('error', data.error);
    }
  }
}

function sac_getRoles(callback) {
  var key = sac_getTotalStorageUserPrefix() + 'roles';
  var timestamp_key = sac_getTotalStorageUserPrefix() + 'timestamp_roles';

  if ($.totalStorage(key) != null) {
    if ($.totalStorage(timestamp_key) == null || sac_hasExpired($.totalStorage(timestamp_key))){
      sac_jsoncalls({
        onDataReceived: function (data) {
          if (typeof SENTRY_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
            SENTRY_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
          }
          if (data.error) {
            sac_errorHandler(data);
          }
          else {
            if (data.roles) {
              $.totalStorage(key, JSON.stringify(data.roles));
              $.totalStorage(timestamp_key, (new Date()).getTime());
              callback($.parseJSON($.totalStorage(key)));
            }
          }
        }
      });
    } else {
      callback($.parseJSON($.totalStorage(key)));
    }
  } else {
    console.log('here4');
    sac_jsoncalls({
      onDataReceived: function (data) {
        if (typeof SENTRY_AUTOCOMPLETE_GLOBAL_CALLBACK == "function") {
          SENTRY_AUTOCOMPLETE_GLOBAL_CALLBACK(data);
        }
        if (data.error) {
          sac_errorHandler(data);
        } else {
          if (data.roles) {
            $.totalStorage(key, JSON.stringify(data.roles));
            $.totalStorage(timestamp_key, (new Date()).getTime());
            callback($.parseJSON($.totalStorage(key)));
          }
        }
      }
    });
  }
}
