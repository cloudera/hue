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

(function (root, factory) {
  if(typeof define === "function" && define.amd) {
    define(['knockout'], factory);
  } else {
    root.AssistHelper = factory(ko);
  }
}(this, function (ko) {

  var TIME_TO_LIVE_IN_MILLIS = 86400000; // 1 day
  var AUTOCOMPLETE_API_PREFIX = "/notebook/api/autocomplete/";
  var HDFS_API_PREFIX = "/filebrowser/view=";
  var HDFS_PARAMETERS = "?pagesize=100&format=json";


  /**
   * @param {Object} i18n
   * @param {string} i18n.errorLoadingDatabases
   * @param {string} i18n.errorLoadingTablePreview
   * @param {string} user
   *
   * @constructor
   */
  function AssistHelper (i18n, user) {
    var self = this;
    self.i18n = i18n;
    self.user = user;
    self.lastKnownDatabases = [];
  }

  AssistHelper.prototype.hasExpired = function (timestamp) {
    return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
  };

  /**
   * @param {string} sourceType
   * @returns {string}
   */
  AssistHelper.prototype.getTotalStorageUserPrefix = function (sourceType) {
    var self = this;
    return sourceType + "_" + self.user;
  };

  /**
   * @param {string[]} pathParts
   * @param {function} successCallback
   * @param {function} errorCallback
   * @param {Object} [editor] - Ace editor
   */
  AssistHelper.prototype.fetchHdfsPath = function (pathParts, successCallback, errorCallback, editor) {
    var self = this;
    var url = HDFS_API_PREFIX + "/" + pathParts.join("/") + HDFS_PARAMETERS;

    var fetchFunction = function (successCallback) {
      $.ajax({
        dataType: "json",
        url: url,
        success: function (data) {
          if (!data.error) {
            successCallback(data);
          } else {
            errorCallback();
          }
        }
      }).fail(function () {
        errorCallback();
      }).always(function () {
        if (editor) {
          editor.hideSpinner();
        }
      });
    };

    self.fetchCached('hdfs', url, fetchFunction, successCallback, editor);
  };

  /**
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} [options.databaseName]
   * @param {string} [options.tableName]
   * @param {string[]} [options.fields]
   * @param {boolean} [options.clearAll]
   */
  AssistHelper.prototype.clearCache = function (options) {
    var self = this;
    if (options.clearAll) {
      $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType), {});
    } else {
      var url = AUTOCOMPLETE_API_PREFIX;
      if (options.databaseName) {
        url += options.databaseName;
      }
      if (options.tableName) {
        url += "/" + options.tableName;
      }
      if (options.fields) {
        url += options.fields.length > 0 ? "/" + options.fields.join("/") : "";
      }
      var cachedData = $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType)) || {};
      delete cachedData[url];
      $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(options.sourceType), cachedData);
    }
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {function} options.callback
   */
  AssistHelper.prototype.loadDatabases = function (options) {
    var self = this;

    self.fetchAssistData(options.sourceType, AUTOCOMPLETE_API_PREFIX, function(data) {
      var databases = data.databases || [];
      // Blacklist of system databases
      self.lastKnownDatabases = $.grep(databases, function(database) {
        return database !== "_impala_builtins";
      });
      options.callback(self.lastKnownDatabases);
    }, function (message) {
      if (message.status == 401) {
        $(document).trigger("showAuthModal", {'type': options.sourceType, 'callback': function() {
          self.loadDatabases(options);
        }});
      } else if (message.statusText) {
        $(document).trigger("error", self.i18n.errorLoadingDatabases + ":" + message.statusText);
      } else if (message.message) {
        $(document).trigger("error", self.i18n.errorLoadingDatabases + ":" + message.message);
      } else if (message) {
        $(document).trigger("error", message);
      } else {
        $(document).trigger("error", self.i18n.errorLoadingDatabases + ".");
      }
      self.lastKnownDatabases = [];
      options.callback([]);
    });
  };

  /**
   * @param {Object} options
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   */
  AssistHelper.prototype.fetchPartitions = function (options) {
    // http://127.0.0.1:8000/metastore/table/default/blog/partitions?format=json
    $.ajax({
      url: "/metastore/table/" + options.databaseName + "/" + options.tableName + "/partitions",
      data: {
        "format" : 'json'
      },
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      success: options.successCallback,
      error: options.errorCallback
    });
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   */
  AssistHelper.prototype.fetchTableDetails = function (options) {
    $.ajax({
      url: "/" + (options.sourceType == "hive" ? "beeswax" : options.sourceType) + "/api/table/" + options.databaseName + "/" + options.tableName,
      data: {
        "format" : 'json'
      },
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      success: options.successCallback,
      error: options.errorCallback
    });
  };


  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string} options.dataType - html or json
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   */
  AssistHelper.prototype.fetchTableSample = function (options) {
    $.ajax({
      url: "/" + (options.sourceType == "hive" ? "beeswax" : options.sourceType) + "/api/table/" + options.databaseName + "/" + options.tableName + "/sample",
      data: {},
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      success: options.successCallback,
      error: options.errorCallback
    });
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string} options.columnName
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   */
  AssistHelper.prototype.refreshTableStats = function (options) {
    var pollRefresh = function (url) {
      $.post(url, function (data) {
        if (data.isSuccess) {
          options.successCallback(data);
        } else if (data.isFailure) {
          options.errorCallback(data.message);
        } else {
          window.setTimeout(function () {
            pollRefresh(url);
          }, 1000);
        }
      }).fail(options.errorCallback);
    };

    $.post("/" + (options.sourceType == "hive" ? "beeswax" : options.sourceType) + "/api/analyze/" + options.databaseName + "/" + options.tableName + "/"  + (options.columnName || ""), function (data) {
      if (data.status == 0 && data.watch_url) {
        pollRefresh(data.watch_url);
      } else {
        options.errorCallback(data.message);
      }
    }).fail(options.errorCallback);
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string} options.columnName
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   */
  AssistHelper.prototype.fetchStats = function (options) {
    $.ajax({
      url: "/" + options.sourceType + "/api/table/" + options.databaseName + "/" + options.tableName + "/stats/" + ( options.columnName || ""),
      data: {},
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      dataType: "json",
      success: options.successCallback,
      error: options.errorCallback
    });
  };

  /**
   * @param {Object} options
   * @param {Object} [options.prefixFilter]
   * @param {string} options.sourceType
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string} options.columnName
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   */
  AssistHelper.prototype.fetchTerms = function (options) {
    $.ajax({
      url: "/" + options.sourceType + "/api/table/" + options.databaseName + "/" + options.tableName + "/terms/" + options.columnName + "/" + (options.prefixFilter || ""),
      data: {},
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      dataType: "json",
      success: options.successCallback,
      error: options.errorCallback
    });
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.databaseName
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   * @param {Object} [options.editor] - Ace editor
   */
  AssistHelper.prototype.fetchTables = function (options) {
    var self = this;
    self.fetchAssistData(options.sourceType, AUTOCOMPLETE_API_PREFIX + options.databaseName, options.successCallback, options.errorCallback, options.editor);
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string} options.databaseName
   * @param {string} options.tableName
   * @param {string[]} options.fields
   * @param {Object} [options.editor] - Ace editor
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   */
  AssistHelper.prototype.fetchFields = function (options) {
    var self = this;
    var fieldPart = options.fields.length > 0 ? "/" + options.fields.join("/") : "";
    self.fetchAssistData(options.sourceType, AUTOCOMPLETE_API_PREFIX + options.databaseName + "/" + options.tableName + fieldPart, options.successCallback, options.errorCallback, options.editor);
  };

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {string[]} options.hierarchy
   * @param {function} options.successCallback
   * @param {function} options.errorCallback
   */
  AssistHelper.prototype.fetchPanelData = function (options) {
    var self = this;
    self.fetchAssistData(options.sourceType, AUTOCOMPLETE_API_PREFIX + options.hierarchy.join("/"), options.successCallback, options.errorCallback);
  };

  /**
   * @param {string} sourceType
   * @param {string} url
   * @param {function} successCallback
   * @param {function} errorCallback
   * @param {Object} [editor] - Ace editor
   */
  AssistHelper.prototype.fetchAssistData = function (sourceType, url, successCallback, errorCallback, editor) {
    var self = this;
    if (!sourceType) {
      return
    }

    var fetchFunction = function (successCallback) {
      $.post(url, {
        notebook: {},
        snippet: ko.mapping.toJSON({
          type: sourceType
        })
      }, function (data) {
        if (data.status == 0) {
          successCallback(data);
        } else {
          errorCallback(data);
        }
      }).fail(errorCallback).always(function () {
        if (editor) {
          editor.hideSpinner();
        }
      });
    };

    self.fetchCached(sourceType, url, fetchFunction, successCallback, editor);
  };

  AssistHelper.prototype.fetchCached = function (sourceType, url, fetchFunction, successCallback, editor) {
    var self = this;
    var cachedData = $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(sourceType)) || {};

    if (typeof cachedData[url] == "undefined" || self.hasExpired(cachedData[url].timestamp)) {
      if (editor) {
        editor.showSpinner();
      }

      fetchFunction(function (data) {
        cachedData[url] = {
          timestamp: (new Date()).getTime(),
          data: data
        };
        $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(sourceType), cachedData);
        successCallback(data);
      });
    } else {
      successCallback(cachedData[url].data);
    }
  };

  return AssistHelper;
}));
