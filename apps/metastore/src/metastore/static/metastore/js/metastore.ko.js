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

var MetastoreViewModel = (function () {

  /**
   * @param {Object} options
   * @param {string} options.user
   * @constructor
   */
  function MetastoreViewModel(options) {
    var self = this;
    self.partitionsLimit = options.partitionsLimit;
    self.assistAvailable = ko.observable(true);
    self.apiHelper = ApiHelper.getInstance();
    self.isHue4 = ko.observable(options.hue4);
    self.isLeftPanelVisible = ko.observable();
    self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);
    self.optimizerEnabled = ko.observable(options.optimizerEnabled || false);
    self.navigatorEnabled = ko.observable(options.navigatorEnabled || false);

    self.navigatorEnabled.subscribe(function (newValue) {
      huePubSub.publish('meta.navigator.enabled', newValue);
    });

    self.optimizerUrl = ko.observable(options.optimizerUrl);
    self.navigatorUrl = ko.observable(options.navigatorUrl);

    huePubSub.subscribe("assist.db.panel.ready", function () {
      huePubSub.publish('assist.set.database', {
        source: 'hive',
        name: null
      });
    });

    self.reloading = ko.observable(false);
    self.loading = ko.observable(false);
    self.databases = ko.observableArray();

    self.selectedDatabases = ko.observableArray();

    self.databaseQuery = ko.observable('').extend({ rateLimit: 150 });

    self.currentTab = ko.observable('');

    self.filteredDatabases = ko.computed(function () {
      if (self.databaseQuery() === '') {
        return self.databases();
      }
      return $.grep(self.databases(), function (database) {
        return database.name.toLowerCase().indexOf(self.databaseQuery()) > -1;
      });
    });

    self.database = ko.observable(null);

    self.loadDatabases();

    huePubSub.subscribe('assist.db.refresh', function (options) {
      if (options.sourceType !== 'hive') {
        return;
      }
      self.reloading(true);
      huePubSub.publish('assist.clear.db.cache', {
        sourceType: 'hive',
        clearAll: true
      });
      var currentDatabase = null;
      var currentTable = null;
      if (self.database()) {
        currentDatabase = self.database().name;
        if (self.database().table()) {
          currentTable = self.database().table().name;
          self.database().table(null);
        }
        self.database(null);
      }
      self.loadDatabases(function () {
        if (currentDatabase) {
          self.setDatabaseByName(currentDatabase, function () {
            if (self.database() && currentTable) {
              self.database().setTableByName(currentTable);
            }
            self.reloading(false);
          });
        } else {
          self.reloading(false);
        }
      });
    });

    huePubSub.subscribe("assist.table.selected", function (tableDef) {
      self.loadTableDef(tableDef, function () {
        huePubSub.publish('metastore.url.change')
      });
    });

    huePubSub.subscribe("assist.database.selected", function (databaseDef) {
      if (self.database()) {
        self.database().table(null);
      }
      self.setDatabaseByName(databaseDef.name, function () {
        huePubSub.publish('metastore.url.change')
      });
    });

    huePubSub.subscribe('metastore.url.change', function () {
      var prefix = '/metastore/';
      if (self.isHue4()){
        prefix = '/hue' + prefix;
      }
      if (self.database() && self.database().table()) {
        hueUtils.changeURL(prefix + 'table/' + self.database().name + '/' + self.database().table().name);
      }
      else if (self.database()) {
        hueUtils.changeURL(prefix + 'tables/' + self.database().name);
      }
      else {
        hueUtils.changeURL(prefix + 'databases');
      }
    });

    self.loadURL();

    window.onpopstate = function () {
      if (window.location.pathname.indexOf('/metastore') > -1) {
        self.loadURL();
      }
    };

    self.databasesBreadcrumb = function () {
      if (self.database()) {
        self.database().table(null);
      }
      self.database(null);
      huePubSub.publish('metastore.url.change');
    };

    self.tablesBreadcrumb = function () {
      self.database().table(null);
      huePubSub.publish('metastore.url.change')
    }
  }

  var lastLoadDatabasesDeferred = null;

  MetastoreViewModel.prototype.loadDatabases = function (successCallback) {
    var self = this;
    if (self.loading()) {
      if (lastLoadDatabasesDeferred !== null) {
        lastLoadDatabasesDeferred.done(successCallback);
      }
      return;
    }

    lastLoadDatabasesDeferred = $.Deferred();
    lastLoadDatabasesDeferred.done(successCallback);

    self.loading(true);
    self.apiHelper.loadDatabases({
      sourceType: 'hive',
      successCallback: function (databaseNames) {
        self.databases($.map(databaseNames, function (name) {
          return new MetastoreDatabase({
            name: name,
            optimizerEnabled: self.optimizerEnabled,
            navigatorEnabled: self.navigatorEnabled
          })
        }));
        self.loading(false);
        lastLoadDatabasesDeferred.resolve();
      },
      errorCallback: function () {
        self.databases([]);
        lastLoadDatabasesDeferred.reject();
      }
    });
  };

  MetastoreViewModel.prototype.loadTableDef = function (tableDef, callback) {
    var self = this;
    self.setDatabaseByName(tableDef.database, function () {
      if (self.database()) {
        if (self.database().table() && self.database().table().name == tableDef.name) {
          if (callback) {
            callback();
          }
          return;
        }

        var setTableAfterLoad = function (clearDbCacheOnMissing) {
          var foundTables = $.grep(self.database().tables(), function (table) {
            return table.name === tableDef.name;
          });
          if (foundTables.length === 1) {
            self.database().setTable(foundTables[0], callback);
          } else if (clearDbCacheOnMissing) {
            huePubSub.publish('assist.clear.db.cache', {
              sourceType: 'hive',
              clearAll: false,
              databaseName: self.database().name
            });
            self.database().load(function () {
              setTableAfterLoad(false);
            }, self.optimizerEnabled(), self.navigatorEnabled());
          }
        };

        if (!self.database().loaded()) {
          var doOnce = self.database().loaded.subscribe(function () {
            setTableAfterLoad(true);
            doOnce.dispose();
          });
        } else {
          setTableAfterLoad(true);
        }
      }
    });
  };

  MetastoreViewModel.prototype.setDatabaseByName = function (databaseName, callback) {
    var self = this;

    var whenLoaded = function () {
      if (databaseName === '') {
        databaseName = self.apiHelper.getFromTotalStorage('editor', 'last.selected.database') ||
            self.apiHelper.getFromTotalStorage('metastore', 'last.selected.database') || 'default';
      }
      if (self.database() && self.database().name == databaseName) {
        if (callback) {
          callback();
        }
        return;
      }
      var foundDatabases = $.grep(self.databases(), function (database) {
        return database.name === databaseName;
      });
      if (foundDatabases.length === 1) {
        self.setDatabase(foundDatabases[0], callback);
      } else {
        foundDatabases = $.grep(self.databases(), function (database) {
          return database.name === 'default';
        });

        if (foundDatabases.length === 1) {
          self.setDatabase(foundDatabases[0], callback);
        } else {
        }
      }
    };

    if (self.loading() && lastLoadDatabasesDeferred !== null) {
      lastLoadDatabasesDeferred.done(whenLoaded);
    } else {
      whenLoaded();
    }
  };

  MetastoreViewModel.prototype.loadURL = function () {
    var self = this;

    var path = (IS_HUE_4 ? window.location.pathname.substr(4) : window.location.pathname);
    if (!path) {
      path = '/metastore/tables';
    }
    path = path.split('/');
    if (path[0] === '') {
      path.shift();
    }
    if (path[0] === 'metastore') {
      path.shift();
    }
    switch (path[0]) {
      case 'databases':
        if (self.database()) {
          self.database().table(null);
          self.database(null);
        }
        break;
      case 'tables':
        if (self.database()) {
          self.database().table(null);
        }
        self.setDatabaseByName(path[1]);
        break;
      case 'table':
        self.loadTableDef({
          name: path[2],
          database: path[1]
        });
    }
  };

  MetastoreViewModel.prototype.setDatabase = function (metastoreDatabase, callback) {
    var self = this;
    huePubSub.publish('metastore.scroll.to.top');
    self.database(metastoreDatabase);

    if (!metastoreDatabase.loaded()) {
      metastoreDatabase.load(callback, self.optimizerEnabled(), self.navigatorEnabled());
    } else if (callback) {
      callback();
    }
  };

  return MetastoreViewModel;
})();
