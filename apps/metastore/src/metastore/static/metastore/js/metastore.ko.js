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
    self.sourceType = ko.observable(options.sourceType || 'hive');

    self.navigatorEnabled.subscribe(function (newValue) {
      huePubSub.publish('meta.navigator.enabled', newValue);
    });

    self.optimizerUrl = ko.observable(options.optimizerUrl);
    self.navigatorUrl = ko.observable(options.navigatorUrl);

    huePubSub.subscribe("assist.db.panel.ready", function () {
      huePubSub.publish('assist.set.database', {
        source: self.sourceType(),
        name: null
      });
    });

    self.reloading = ko.observable(false);
    self.loadingDatabases = ko.observable(false);
    self.loadingTable = ko.observable(false);

    self.loading = ko.pureComputed(function () {
      return self.loadingDatabases() || self.loadingTable() || self.reloading();
    });

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

    self.refresh = function () {
      if (self.sourceType() === 'impala') {
        huePubSub.publish('assist.invalidate.on.refresh');
      }
      huePubSub.publish('assist.db.refresh', { sourceTypes: [ self.sourceType() ] });
    };

    huePubSub.subscribe('assist.db.refresh', function (options) {
      if (typeof options.sourceTypes !== 'undefined' && options.sourceTypes.indexOf('hive') === -1 && options.sourceTypes.indexOf('impala') === -1 ) {
        return;
      }
      self.reloading(true);
      huePubSub.publish('assist.clear.db.cache', {
        sourceType: 'hive',
        clearAll: true
      });
      huePubSub.publish('assist.clear.db.cache', {
        sourceType: 'impala',
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
      if (self.isHue4() && !IS_EMBEDDED){
        prefix = '/hue' + prefix;
      }
      var newUrl;
      if (self.database() && self.database().table()) {
        newUrl = prefix + 'table/' + self.database().name + '/' + self.database().table().name;
      } else if (self.database()) {
        newUrl = prefix + 'tables/' + self.database().name;
      } else {
        newUrl = prefix + 'databases';
      }

      if (IS_EMBEDDED) {
        hueUtils.changeURLParameter('app', newUrl);
      } else {
        hueUtils.changeURL(newUrl);
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
    if (self.loadingDatabases()) {
      if (lastLoadDatabasesDeferred !== null) {
        lastLoadDatabasesDeferred.done(successCallback);
      }
      return;
    }

    lastLoadDatabasesDeferred = $.Deferred();
    lastLoadDatabasesDeferred.done(successCallback);

    self.loadingDatabases(true);
    self.apiHelper.loadDatabases({
      sourceType: self.sourceType(),
      successCallback: function (databaseNames) {
        self.databases($.map(databaseNames, function (name) {
          return new MetastoreDatabase({
            name: name,
            optimizerEnabled: self.optimizerEnabled,
            navigatorEnabled: self.navigatorEnabled,
            sourceType: self.sourceType
          })
        }));
        self.loadingDatabases(false);
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
    self.loadingTable(true);
    self.setDatabaseByName(tableDef.database, function () {
      if (self.database()) {
        if (self.database().table() && self.database().table().name == tableDef.name) {
          self.loadingTable(false);
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
            self.loadingTable(false);
            self.database().setTable(foundTables[0], callback);
          } else if (clearDbCacheOnMissing) {
            huePubSub.publish('assist.clear.db.cache', {
              sourceType: self.sourceType(),
              clearAll: false,
              databaseName: self.database().name
            });
            self.database().load(function () {
              setTableAfterLoad(false);
            }, self.optimizerEnabled(), self.navigatorEnabled(), self.sourceType());
          } else {
            self.loadingTable(false);
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

    if (self.loadingDatabases() && lastLoadDatabasesDeferred !== null) {
      lastLoadDatabasesDeferred.done(whenLoaded);
    } else {
      whenLoaded();
    }
  };

  MetastoreViewModel.prototype.loadURL = function () {
    var self = this;

    var path;

    if (IS_EMBEDDED) {
      var appMatch = location.search.match(/app=\/?([^&#]+)/);
      if (appMatch) {
        path = '/' + appMatch[1];
      }
    } else {
      path = (IS_HUE_4 ? window.location.pathname.substr(4) : window.location.pathname);
    }
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
        huePubSub.subscribe('metastore.loaded.table', function(){
          hueUtils.waitForRendered('a[href="#overview"]', function(el){ return el.is(':visible') }, function(){
            $('a[href="#overview"]').click();
          });
        }, 'metastore');
        self.loadTableDef({
          name: path[2],
          database: path[1]
        }, function(){
          if (path.length > 3 && path[3] === 'partitions'){
            huePubSub.subscribe('metastore.loaded.partitions', function(){
              $('a[href="#partitions"]').click();
            }, 'metastore');
          }
        });
    }
  };

  MetastoreViewModel.prototype.setDatabase = function (metastoreDatabase, callback) {
    var self = this;
    huePubSub.publish('metastore.scroll.to.top');
    self.database(metastoreDatabase);

    if (!metastoreDatabase.loaded()) {
      metastoreDatabase.load(callback, self.optimizerEnabled(), self.navigatorEnabled(), self.sourceType());
    } else if (callback) {
      callback();
    }
  };

  return MetastoreViewModel;
})();
