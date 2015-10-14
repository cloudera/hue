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
  var NOTEBOOK_API_PREFIX = "/notebook/api/autocomplete/";

  /**
   * @param options {object}
   * @param options.notebook
   * @param options.user
   * @param options.activeDatabase
   *
   * @constructor
   */
  function AssistHelper (options) {
    var self = this;
    self.activeDatabase = ko.observable();
    self.initialDatabase = options.activeDatabase;
    self.notebook = options.notebook;
    self.user = options.user;
    self.availableDatabases = ko.observableArray();
    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.type = null;
    self.activeDatabase.subscribe(function (newValue) {
      if (self.loaded()) {
        $.totalStorage("hue.assist.lastSelectedDb." + self.getTotalStorageUserPrefix(), newValue);
      }
    });
  }

  AssistHelper.prototype.load = function (snippet, callback) {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.type = snippet.type();
    self.loading(true);
    self.loaded(false);
    self.fetchAssistData(snippet, NOTEBOOK_API_PREFIX, function(data) {

      var databases = data.databases || [];
      // Blacklist of system databases
      self.availableDatabases($.grep(databases, function(database) { return database !== "_impala_builtins" }));

      if ($.inArray(self.activeDatabase(), self.availableDatabases()) === -1) {
        // Defer this, select2 will update the activeDatabase to undefined when loading so this should make sure we set
        // it afterwards.
        window.setTimeout(function() {
          var lastSelectedDb = $.totalStorage("hue.assist.lastSelectedDb." + self.getTotalStorageUserPrefix());
          if ($.inArray(self.initialDatabase, self.availableDatabases()) > -1) {
            self.activeDatabase(self.initialDatabase);
          } else if ($.inArray(lastSelectedDb, self.availableDatabases()) > -1) {
            self.activeDatabase(lastSelectedDb);
          } else if ($.inArray("default", self.availableDatabases()) > -1) {
            self.activeDatabase("default");
          } else if (self.availableDatabases().length > 0) {
            self.activeDatabase(self.availableDatabases()[0]);
          }
        }, 1);
      }

      self.loaded(true);
      self.loading(false);
      if (callback) {
        callback();
      }
    }, function (message) {
      self.loaded(true);
      self.loading(false);
      if (message.status == 401) {
        $(document).trigger("showAuthModal", {'type': self.type, 'callback': function() { self.load(snippet, callback) }});
      } else if (message.statusText) {
        $(document).trigger("error", "There was a problem loading the databases:" + message.statusText);
      } else if (message) {
        $(document).trigger("error", message);
      } else {
        $(document).trigger("error", "There was a problem loading the databases");
      }
      if (callback) {
        callback();
      }
    });
  };

  AssistHelper.prototype.hasExpired = function (timestamp) {
    return (new Date()).getTime() - timestamp > TIME_TO_LIVE_IN_MILLIS;
  };

  AssistHelper.prototype.getTotalStorageUserPrefix = function () {
    var self = this;
    return self.type + "_" + self.user;
  };

  AssistHelper.prototype.fetchTableHtmlPreview = function(snippet, tableName, successCallback, errorCallback) {
    var self = this;
    var app = snippet.type() == "hive" ? "beeswax" : snippet.type();
    $.ajax({
      url: "/" + app + "/api/table/" + self.activeDatabase() + "/" + tableName,
      data: { "sample": true },
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      dataType: "html",
      success: successCallback,
      error: errorCallback
    });
  };

  AssistHelper.prototype.refreshTableStats = function(snippet, tableName, columnName, successCallback, errorCallback) {
    var self = this;
    var pollRefresh = function (url) {
      $.post(url, function (data) {
        if (data.isSuccess) {
          successCallback(data);
        } else if (data.isFailure) {
          errorCallback(data.message);
        } else {
          window.setTimeout(function () {
            pollRefresh(url);
          }, 1000);
        }
      }).fail(errorCallback);
    };

    var app = snippet.type() == "hive" ? "beeswax" : snippet.type();
    $.post("/" + app + "/api/analyze/" + self.activeDatabase() + "/" + tableName + "/"  + (columnName || ""), function (data) {
      if (data.status == 0 && data.watch_url) {
        pollRefresh(data.watch_url);
      } else {
        errorCallback(data.message);
      }
    }).fail(errorCallback);
  };

  AssistHelper.prototype.fetchStats = function(snippet, tableName, columnName, successCallback, errorCallback) {
    var self = this;
    var app = snippet.type() == "hive" ? "beeswax" : snippet.type();
    $.ajax({
      url: "/" + app + "/api/table/" + self.activeDatabase() + "/" + tableName + "/stats/" + (columnName || ""),
      data: {},
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      dataType: "json",
      success: successCallback,
      error: errorCallback
    });
  };

  AssistHelper.prototype.fetchTerms = function(snippet, tableName, columnName, prefixFilter, successCallback, errorCallback) {
    var self = this;
    var app = snippet.type() == "hive" ? "beeswax" : snippet.type();
    $.ajax({
      url: "/" + app + "/api/table/" + self.activeDatabase() + "/" + tableName + "/terms/" + columnName + "/" + (prefixFilter || ""),
      data: {},
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-Requested-With", "Hue");
      },
      dataType: "json",
      success: successCallback,
      error: errorCallback
    });
  };

  AssistHelper.prototype.fetchTables = function(snippet, successCallback, errorCallback) {
    var self = this;
    self.fetchAssistData(snippet, NOTEBOOK_API_PREFIX + self.activeDatabase(), successCallback, errorCallback);
  };

  AssistHelper.prototype.fetchFields = function(snippet, tableName, fields, successCallback, errorCallback, editor) {
    var self = this;

    var fieldPart = fields.length > 0 ? "/" + fields.join("/") : "";
    self.fetchAssistData(snippet, NOTEBOOK_API_PREFIX + self.activeDatabase() + "/" + tableName + fieldPart, successCallback, errorCallback, editor);
  };

  AssistHelper.prototype.clearCache = function(snippet) {
    var self = this;
    $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(), {});
  };

  AssistHelper.prototype.fetchPanelData = function (snippet, hierarchy, successCallback, errorCallback) {
    var self = this;
    self.fetchAssistData(snippet, NOTEBOOK_API_PREFIX + hierarchy.join("/"), successCallback, errorCallback);
  };

  AssistHelper.prototype.fetchAssistData = function (snippet, url, successCallback, errorCallback, editor) {
    var self = this;
    var cachedData = $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix()) || {};

    if (typeof cachedData[url] == "undefined" || self.hasExpired(cachedData[url].timestamp)) {
      if (editor) {
        editor.showSpinner();
      }
      $.post(url, {
        notebook: ko.mapping.toJSON(self.notebook.getContext()),
        snippet: ko.mapping.toJSON(snippet.getContext())
      }, function (data) {
        if (data.status == 0) {
          cachedData[url] = {
            timestamp: (new Date()).getTime(),
            data: data
          };
          $.totalStorage("hue.assist." + self.getTotalStorageUserPrefix(), cachedData);
          successCallback(data);
        } else {
          errorCallback(data);
        }
      }).fail(errorCallback).always(function () {
        if (editor) {
          editor.hideSpinner();
        }
      });
    } else {
      successCallback(cachedData[url].data);
    }
  };

  return AssistHelper;
}));
