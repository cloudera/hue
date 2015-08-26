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

var hasExpired = function (timestamp) {
  return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
};


/**
 * @param options {object}
 * @param options.baseUrl
 * @param options.app
 * @param options.user
 *
 * @constructor
 */
function Autocomplete(options) {
  this.options = options;
  this.currentDB = "";
  this.currentTables = [];
}

Autocomplete.prototype.jsonCalls = function (options) {
  var _url = typeof options.autocompleteBaseURL != "undefined" ? options.autocompleteBaseURL : this.options.autocompleteBaseURL;
  if (_url != "") {
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
      error: options.onError ? options.onError : $.noop,
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
  var app = "";
  if (typeof this.options.app != "undefined") {
    app = this.options.app;
  }
  if (typeof this.options.user != "undefined") {
    return app + "_" + this.options.user;
  }
  return app;
};

Autocomplete.prototype.getTableColumns = function (databaseName, tableName, textScanned, callback, failCallback) {
  var self = this;
  if (tableName.indexOf("(") > -1) {
    tableName = tableName.substr(tableName.indexOf("(") + 1);
  }

  var _aliases = self.getTableAliases(textScanned);
  if (_aliases[tableName]) {
    tableName = _aliases[tableName];
  }

  var fetchData = function (successCallback) {
    self.jsonCalls({
      database: databaseName,
      table: tableName,
      onDataReceived: function (data) {
        if (typeof self.options.autocompleteGlobalCallback == "function") {
          self.options.autocompleteGlobalCallback(data);
        }
        if (data.error) {
          if (failCallback) {
            failCallback();
          } else {
            self.errorHandler(data);
          }
        } else {
          $.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName, (data.columns ? "* " + data.columns.join(" ") : "*"));
          $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName, (data.extended_columns ? data.extended_columns : []));
          $.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName, (new Date()).getTime());
          if (successCallback) {
            successCallback();
          }
        }
      },
      onError: failCallback
    });
  };

  if ($.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName) != null && $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName) != null) {
    callback($.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName), $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName));
    if ($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName) == null || hasExpired($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_columns_' + databaseName + '_' + tableName))) {
      fetchData();
    }
  } else {
    fetchData(function() {
      callback($.totalStorage(self.getTotalStorageUserPrefix() + 'columns_' + databaseName + '_' + tableName), $.totalStorage(self.getTotalStorageUserPrefix() + 'extended_columns_' + databaseName + '_' + tableName));
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
    if ($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName) == null || hasExpired($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_tables_' + databaseName))) {
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
    if ($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_databases') == null || hasExpired($.totalStorage(self.getTotalStorageUserPrefix() + 'timestamp_databases'))) {
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

var SQL_TERMS = /\b(FROM|TABLE|STATS|REFRESH|METADATA|DESCRIBE|ORDER BY|ON|WHERE|SELECT|LIMIT|GROUP|SORT)\b/g;

var getTableReferenceIndex = function (statement) {
  var result = {};
  var fromMatch = statement.match(/\s*from\s*([^;]*).*$/i);
  if (fromMatch) {
    var tableRefsRaw = fromMatch[1];
    upToMatch = tableRefsRaw.match(/\bON|LIMIT|WHERE|GROUP|SORT|ORDER BY\b/i);
    if (upToMatch) {
      tableRefsRaw = $.trim(tableRefsRaw.substring(0, upToMatch.index));
    }
    var tableRefs = tableRefsRaw.split(",");
    $.each(tableRefs, function(index, tableRefRaw) {
      var tableMatch = tableRefRaw.match(/ *([^ ]*) ?([^ ]*)? */);
      result[tableMatch[2] || tableMatch[1]] = tableMatch[1];
    })
  }
  return result;
};

var extractFields = function(data, valuePrefix, includeStar) {
  var fields = [];
  var type;
  var fieldNames = [];
  if (data.type == "struct") {
    type = "struct";
    fieldNames = $.map(data.fields, function(field) {
      return field.name;
    });
  } else if (typeof data.columns != "undefined") {
    type = "column";
    fieldNames = data.columns;
    if (includeStar) {
      fields.push({value: '*', score: 10000, meta: type});
    }
  } else if (typeof data.tables != "undefined") {
    type = "table";
    fieldNames = data.tables;
  }

  fieldNames.sort();
  fieldNames.forEach(function(name, idx) {
    if (name != "") {
      fields.push({value: typeof valuePrefix != "undefined" ? valuePrefix + name : name, score: 1000 - idx, meta: type});
    }
  });
  return fields;
};

var fetchAssistData = function(assist, url, successCallback, errorCallback) {
  var cachedData = $.totalStorage("hue.assist." + assist.getTotalStorageUserPrefix()) || {};

  if (typeof cachedData[url] == "undefined" || hasExpired(cachedData[url].timestamp)) {
    $.ajax({
      type: "GET",
      url: url + "?" + Math.random(),
      success: function (data) {
        cachedData[url] = {
          timestamp: (new Date()).getTime(),
          data: data
        };
        $.totalStorage("hue.assist." + assist.getTotalStorageUserPrefix(), cachedData);
        successCallback(data);
      },
      error: errorCallback
    });
  } else {
    successCallback(cachedData[url].data);
  }
};

Autocomplete.prototype.autocomplete = function(beforeCursor, afterCursor, callback) {
  var self = this;
  var beforeCursorU = beforeCursor.toUpperCase();
  var afterCursorU = afterCursor.toUpperCase();

  var beforeMatcher = beforeCursorU.match(SQL_TERMS);
  var afterMatcher = afterCursorU.match(SQL_TERMS);

  var tableNameAutoComplete = beforeMatcher != null && (
    beforeMatcher[beforeMatcher.length - 1] === "FROM" ||
    beforeMatcher[beforeMatcher.length - 1] === "TABLE" ||
    beforeMatcher[beforeMatcher.length - 1] === "STATS" ||
    beforeMatcher[beforeMatcher.length - 1] === "REFRESH" ||
    beforeMatcher[beforeMatcher.length - 1] === "METADATA" ||
    beforeMatcher[beforeMatcher.length - 1] === "DESCRIBE");

  var selectBefore = beforeMatcher != null &&
    beforeMatcher[beforeMatcher.length - 1] === "SELECT";

  var fromAfter = afterMatcher != null &&
    afterMatcher[0] === "FROM";

  var fieldTermBefore = beforeMatcher != null && (
    beforeMatcher[beforeMatcher.length - 1] === "WHERE" ||
    beforeMatcher[beforeMatcher.length - 1] === "ON" ||
    beforeMatcher[beforeMatcher.length - 1] === "ORDER BY");


  if (tableNameAutoComplete || (selectBefore && !fromAfter)) {
    var url = self.options.autocompleteBaseURL + self.getDatabase();
    fetchAssistData(self, url, function(data) {
      var fromKeyword = "";
      if (selectBefore) {
        if (beforeCursor.indexOf("SELECT") > -1) {
          fromKeyword = "FROM";
        } else {
          fromKeyword = "from";
        }
        if (!beforeCursor.match(/\*\s*$/)) {
          fromKeyword = "? " + fromKeyword;
        } else if (!beforeCursor.match(/\s+$/)) {
          fromKeyword = " " + fromKeyword;
        }
        fromKeyword += " ";
      }
      callback(extractFields(data, fromKeyword));
    }, function() {
      callback([]);
    });
  } else if ((selectBefore && fromAfter) || fieldTermBefore) {
    var partialTermsMatch = beforeCursor.match(/([^ \-\+\<\>\,]*)$/);
    var parts = partialTermsMatch ? partialTermsMatch[0].split(".") : [];

    if (parts.length > 0 && parts[parts.length - 1] != '') {
      // SELECT tablename.colu
      parts.pop();
    }

    var tableReferences = getTableReferenceIndex(beforeCursor + afterCursor);
    var tableName = "";
    if (parts.length > 0 && tableReferences[parts[0]]) {
      // SELECT tablename.column.
      tableName = tableReferences[parts[0]];
      parts.shift();
    } else if (Object.keys(tableReferences).length == 1) {
      // SELECT column.
      // We use first and only table reference
      tableName = tableReferences[Object.keys(tableReferences)[0]];
    } else {
      // No table refs
      callback([]);
      return;
    }
    var url = self.options.autocompleteBaseURL + self.getDatabase() + "/" + tableName;
    $.each(parts, function(index, part) {
      if (part != '' && (index > 0 || part !== tableName)) {
        url += "/" + part;
      }
    });

    fetchAssistData(self, url, function(data) {
      callback(extractFields(data, "", !fieldTermBefore));
    }, function() {
      callback([]);
    });
  } else {
    callback([]);
  }
};

Autocomplete.prototype.errorHandler = function (data) {
  var self = this;
  $(document).trigger('error.autocomplete');
  if (typeof self.options.autocompleteFailsSilentlyOn == "undefined" || data.code == null || self.options.autocompleteFailsSilentlyOn.indexOf(data.code) == -1) {
    if (typeof self.options.autocompleteFailsQuietlyOn != "undefined" && self.options.autocompleteFailsQuietlyOn.indexOf(data.code) > -1) {
      $(document).trigger('info', data.error);
    }
    else {
      $(document).trigger('error', data.error);
    }
  }
};

Autocomplete.prototype.setDatabase = function (db) {
  this.currentDB = db;
};

Autocomplete.prototype.getDatabase = function () {
  return this.currentDB;
};

Autocomplete.prototype.setCurrentTables = function (tables) {
  this.currentTables = tables;
};

Autocomplete.prototype.getCurrentTables = function () {
  return this.currentTables;
};
