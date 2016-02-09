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
    define(['knockout', 'desktop/js/assist/assistDbEntry'], factory);
  } else {
    root.AssistDbSource = factory(ko, AssistDbEntry);
  }
}(this, function (ko, AssistDbEntry) {

  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {AssistHelper} options.assistHelper
   * @param {string} options.type
   * @param {string} options.name
   * @param {Object} options.navigationSettings
   * @constructor
   */
  function AssistDbSource (options) {

    var self = this;
    self.i18n = options.i18n;
    self.navigationSettings = options.navigationSettings;
    self.assistHelper = options.assistHelper;
    self.type = options.type;
    self.name = options.name;

    self.hasErrors = ko.observable(false);
    self.simpleStyles = ko.observable(false);
    self.isSearchVisible = ko.observable(false);
    self.editingSearch = ko.observable(false);

    self.filter = {
      query: ko.observable("").extend({ rateLimit: 150 })
    };

    self.filterActive = ko.pureComputed(function () {
      return self.filter.query().length !== 0;
    });

    var storageSearchVisible = $.totalStorage(self.type + ".assist.searchVisible");
    self.searchVisible = ko.observable(storageSearchVisible || false);

    self.searchVisible.subscribe(function (newValue) {
      $.totalStorage(self.type + ".assist.searchVisible", newValue);
    });

    self.databases = ko.observableArray();

    self.hasEntries = ko.pureComputed(function() {
      return self.databases().length > 0;
    });

    self.filteredEntries = ko.pureComputed(function () {
      if (self.filter.query().length === 0) {
        return self.databases();
      }
      var result = [];
      $.each(self.databases(), function (index, database) {
        if (database.definition.name.toLowerCase().indexOf(self.filter.query()) > -1) {
          result.push(database);
        }
      });
      return result;
    });

    self.selectedDatabase = ko.observable();

    self.reloading = ko.observable(false);

    self.loadingTables = ko.pureComputed(function() {
      return typeof self.selectedDatabase() != "undefined" && self.selectedDatabase() !== null && self.selectedDatabase().loading();
    });

    self.loadingSamples = ko.observable(true);
    self.samples = ko.observable();

    self.selectedDatabase.subscribe(function (newValue) {
      if (newValue) {
        if (self.selectedDatabase() && self.selectedDatabase().definition.name === newValue) {
          return;
        }
        if (!newValue.hasEntries() && !newValue.loading()) {
          newValue.loadEntries()
        }
        $.totalStorage("hue.assist.lastSelectedDb." + self.assistHelper.getTotalStorageUserPrefix(), newValue.definition.name);
        huePubSub.publish("assist.database.set", {
          source: self.type,
          name: newValue.definition.name
        })
      }
    });

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    var dbIndex = {};
    var nestedFilter = {
      query: ko.observable("").extend({ rateLimit: { timeout: 250, method: 'notifyWhenChangesStop' } }),
      showTables: ko.observable(true),
      showViews: ko.observable(true)
    };
    var updateDatabases = function (names) {
      var lastSelectedDb = self.selectedDatabase() ? self.selectedDatabase().definition.name : null;
      dbIndex = {};
      self.databases($.map(names, function(name) {
        var database = new AssistDbEntry({
          name: name,
          displayName: name,
          title: name,
          isDatabase: true
        }, null, self, nestedFilter, self.i18n, self.navigationSettings);
        dbIndex[name] = database;
        if (name === lastSelectedDb) {
          self.selectedDatabase(database);
        }
        return database;
      }));
      self.reloading(false);
      self.loading(false);
      self.loaded(true);
    };

    self.setDatabase = function (databaseName) {
      if (databaseName && self.selectedDatabase() && databaseName === self.selectedDatabase().definition.name) {
        return;
      }
      if (databaseName && dbIndex[databaseName]) {
        self.selectedDatabase(dbIndex[databaseName]);
        return;
      }
      var lastSelectedDb = $.totalStorage("hue.assist.lastSelectedDb." + self.assistHelper.getTotalStorageUserPrefix());
      if (lastSelectedDb && dbIndex[lastSelectedDb]) {
        self.selectedDatabase(dbIndex[lastSelectedDb]);
      } else if (dbIndex["default"]) {
        self.selectedDatabase(dbIndex["default"]);
      }
    };

    self.initDatabases = function () {
      if (self.loading()) {
        return;
      }
      self.loading(true);
      self.assistHelper.loadDatabases({
        sourceType: self.type,
        successCallback: function(data) {
          self.hasErrors(false);
          updateDatabases(data)
        },
        errorCallback: function() {
          self.hasErrors(true);
          updateDatabases([]);
        }
      });
    };

    self.modalItem = ko.observable();

    self.repositionActions = function(data, event) {
      var $container = $(event.target);
      $container.find(".assist-actions, .assist-db-header-actions").css('right', -$container.scrollLeft() + 'px');
    };

    self.reload = function() {
      self.reloading(true);
      huePubSub.publish('assist.clear.db.cache', {
        sourceType: self.type,
        clearAll: true
      });
      self.initDatabases();
    };

    huePubSub.subscribe('assist.db.refresh', function (type) {
      if (self.type === type) {
        self.reload();
      }
    });
  }

  AssistDbSource.prototype.toggleSearch = function() {
    var self = this;
    self.isSearchVisible(!self.isSearchVisible());
    self.editingSearch(self.isSearchVisible());
  };

  AssistDbSource.prototype.triggerRefresh = function () {
    var self = this;
    huePubSub.publish('assist.db.refresh', self.type);
  };

  return AssistDbSource;
}));
