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

    self.catalogEntry = ko.observable();

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

    self.filteredDatabases = ko.pureComputed(function () {
      if (self.databaseQuery() === '') {
        return self.databases();
      }
      return self.databases().filter(function (database) {
        return database.catalogEntry.name.toLowerCase().indexOf(self.databaseQuery().toLowerCase()) !== -1;
      });
    });

    self.database = ko.observable(null);

    self.loadDatabases();

    huePubSub.subscribe('data.catalog.entry.refreshed', function (details) {
      var refreshedEntry = details.entry;

      if (refreshedEntry.getSourceType() !== self.sourceType()) {
        return;
      }

      var prevDbName = null;
      var prevTableName = null;
      if (self.database()) {
        prevDbName = self.database().catalogEntry.name;
        if (self.database().table()) {
          prevTableName = self.database().table().catalogEntry.name;
        }
      }

      var setPrevious = function () {
        if (prevDbName) {
          self.setDatabaseByName(prevDbName, function () {
            if (self.database() && prevTableName) {
              self.database().setTableByName(prevTableName);
            }
          });
        }
      };

      var completeRefresh = function () {
        self.reloading(true);
        if (self.database() && self.database().table()) {
          self.database().table(null);
        }
        if (self.database()) {
          self.database(null);
        }
        self.loadDatabases().done(setPrevious).always(function () {
          self.reloading(false);
        });
      };

      if (refreshedEntry.isSource()) {
        completeRefresh();
      } else if (refreshedEntry.isDatabase()) {
        self.databases().some(function (database) {
          if (database.catalogEntry === refreshedEntry) {
            database.load(setPrevious, self.optimizerEnabled(), self.navigatorEnabled());
            return true;
          }
        })
      } else if (refreshedEntry.isTable()) {
        self.databases().some(function (database) {
          if (database.catalogEntry.name === refreshedEntry.path[0]) {
            database.tables().some(function (table) {
              if (table.catalogEntry.name === refreshedEntry.name) {
                table.load();
                return true;
              }
            });
            return true;
          }
        })
      }
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
        hueUtils.changeURL(prefix + 'table/' + self.database().table().catalogEntry.path.join('/'));
      }
      else if (self.database()) {
        hueUtils.changeURL(prefix + 'tables/' + self.database().catalogEntry.name);
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

  var lastLoadDatabasesPromise = null;

  MetastoreViewModel.prototype.reload = function () {
    var self = this;
    if (!self.reloading() && self.catalogEntry()) {
      self.reloading(true);
      // Clear will publish when done
      self.catalogEntry().clear(self.catalogEntry().getSourceType() === 'impala' ? 'invalidate' : 'cache');
    }
  };

  MetastoreViewModel.prototype.loadDatabases = function () {
    var self = this;
    if (self.loadingDatabases() && lastLoadDatabasesPromise) {
      return lastLoadDatabasesPromise;
    }

    self.loadingDatabases(true);
    var deferred = $.Deferred();
    lastLoadDatabasesPromise = deferred.promise();

    deferred.fail(function () {
      self.databases([]);
    }).always(function () {
      self.loadingDatabases(false);
    });

    DataCatalog.getEntry({ sourceType: self.sourceType(), path: [], definition: { type: 'source' } }).done(function (entry) {
      self.catalogEntry(entry);
      entry.getChildren().done(function (databaseEntries) {
        self.databases($.map(databaseEntries, function (databaseEntry) {
          return new MetastoreDatabase({ catalogEntry: databaseEntry, optimizerEnabled: self.optimizerEnabled });
        }));
        deferred.resolve();
      }).fail(deferred.reject);
    });

    return lastLoadDatabasesPromise;
  };

  MetastoreViewModel.prototype.loadTableDef = function (tableDef, callback) {
    var self = this;
    self.loadingTable(true);
    self.setDatabaseByName(tableDef.database, function () {
      if (self.database()) {
        if (self.database().table() && self.database().table().catalogEntry.name === tableDef.name) {
          self.loadingTable(false);
          if (callback) {
            callback();
          }
          return;
        }

        var setTableAfterLoad = function (clearDbCacheOnMissing) {
          var foundTables = self.database().tables().filter(function (table) {
            return table.catalogEntry.name === tableDef.name;
          });
          if (foundTables.length === 1) {
            self.loadingTable(false);
            self.database().setTable(foundTables[0], callback);
          } else if (clearDbCacheOnMissing) {
            self.database().catalogEntry.clear('invalidate').done(function () {
              self.database().load(function () {
                setTableAfterLoad(false);
              });
            });
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

    var whenLoaded = function (clearCacheOnMissing) {
      if (!databaseName) {
        databaseName = self.apiHelper.getFromTotalStorage('editor', 'last.selected.database') ||
            self.apiHelper.getFromTotalStorage('metastore', 'last.selected.database') || 'default';
        clearCacheOnMissing = false;
      }
      if (self.database() && self.database().catalogEntry.name === databaseName) {
        if (callback) {
          callback();
        }
        return;
      }
      var foundDatabases = self.databases().filter(function (database) {
        return database.catalogEntry.name === databaseName;
      });
      if (foundDatabases.length === 1) {
        self.setDatabase(foundDatabases[0], callback);
      } else if (clearCacheOnMissing) {
        self.catalogEntry().clear('invalidate').done(function () {
          self.loadDatabases().done(function () {
            whenLoaded(false)
          })
        })
      } else {
        foundDatabases = self.databases().filter(function (database) {
          return database.catalogEntry.name === 'default';
        });

        if (foundDatabases.length === 1) {
          self.setDatabase(foundDatabases[0], callback);
        } else {
        }
      }
    };

    if (self.loadingDatabases() && lastLoadDatabasesPromise !== null) {
      lastLoadDatabasesPromise.done(function () {
        whenLoaded(true);
      });
    } else {
      whenLoaded(true);
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
