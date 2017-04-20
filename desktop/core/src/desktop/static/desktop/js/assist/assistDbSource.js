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

var AssistDbSource = (function () {

  var sortFunctions = {
    alpha: function (a, b) {
      return a.definition.name.localeCompare(b.definition.name);
    },
    creation: function (a, b) {
      if (a.definition.isColumn || a.definition.isComplex) {
        return a.definition.index - b.definition.index;
      }
      return sortFunctions.alpha(a, b);
    },
    popular: function (a, b) {
      if (a.popularity() === b.popularity()) {
        return sortFunctions.creation(a, b);
      }
      return b.popularity() - a.popularity();
    }
  };

  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {ApiHelper} options.apiHelper
   * @param {string} options.type
   * @param {string} options.name
   * @param {Object} options.navigationSettings
   * @constructor
   */
  function AssistDbSource (options) {

    var self = this;
    self.i18n = options.i18n;
    self.navigationSettings = options.navigationSettings;
    self.apiHelper = options.apiHelper;
    self.sourceType = options.type;
    self.name = options.name;

    self.hasErrors = ko.observable(false);
    self.simpleStyles = ko.observable(false);
    self.isSearchVisible = ko.observable(false);
    self.editingSearch = ko.observable(false);

    self.highlight = ko.observable(false);

    self.invalidateOnRefresh = ko.observable('cache');

    self.activeSort = ko.observable('creation');

    self.activeSort.subscribe(function (newSort) {
      if (newSort === 'popular') {
        // TODO: Sort popular databases
        self.databases.sort(sortFunctions.alpha)
      } else {
        self.databases.sort(sortFunctions[newSort]);
      }
    });

    self.filter = {
      query: ko.observable("").extend({ rateLimit: 150 })
    };

    self.filterActive = ko.pureComputed(function () {
      return self.filter.query().length !== 0;
    });

    var storageSearchVisible = $.totalStorage(self.sourceType + ".assist.searchVisible");
    self.searchVisible = ko.observable(storageSearchVisible || false);

    self.searchVisible.subscribe(function (newValue) {
      $.totalStorage(self.sourceType + ".assist.searchVisible", newValue);
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
        if (database.definition.name.toLowerCase().indexOf(self.filter.query().toLowerCase()) > -1) {
          result.push(database);
        }
      });
      return result;
    });

    self.selectedDatabase = ko.observable();

    self.selectedDatabase.subscribe(function () {
      var db = self.selectedDatabase();
      if (HAS_OPTIMIZER && db && !db.popularityIndexSet) {
        self.apiHelper.fetchNavOptTopTables({
          sourceType: self.sourceType,
          database: db.definition.name,
          silenceErrors: true,
          timeout: AUTOCOMPLETE_TIMEOUT,
          successCallback: function (data) {
            var popularityIndex = {};
            data.top_tables.forEach(function (topTable) {
              popularityIndex[topTable.name] = topTable.popularity;
            });
            var applyPopularity = function () {
              db.entries().forEach(function (entry) {
                if (popularityIndex[entry.definition.name]) {
                  entry.popularity(popularityIndex[entry.definition.name]);
                }
              });
              if (self.activeSort() === 'popular') {
                db.entries.sort(sortFunctions.popular);
              }
            };

            if (db.loading()) {
              var subscription = db.loading.subscribe(function () {
                if (subscription) {
                  subscription.dispose();
                }
                applyPopularity();
              });
            } else {
              applyPopularity();
            }
          }
        });
      }
    });

    huePubSub.subscribe('assist.database.get', function (callback) {
      callback(self.selectedDatabase());
    });

    self.reloading = ko.observable(false);

    self.loadingTables = ko.pureComputed(function() {
      return typeof self.selectedDatabase() != "undefined" && self.selectedDatabase() !== null && self.selectedDatabase().loading();
    });

    self.loadingSamples = ko.observable(true);
    self.samples = ko.observable();

    self.selectedDatabaseChanged = function () {
      if (self.selectedDatabase()) {
        if (!self.selectedDatabase().hasEntries() && !self.selectedDatabase().loading()) {
          self.selectedDatabase().loadEntries()
        }
        self.apiHelper.setInTotalStorage('assist_' + self.sourceType, 'lastSelectedDb', self.selectedDatabase().definition.name)
        huePubSub.publish("assist.database.set", {
          source: self.sourceType,
          name: self.selectedDatabase().definition.name
        })
      }
    };

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    var dbIndex = {};
    var nestedFilter = {
      query: ko.observable("").extend({ rateLimit: { timeout: 250, method: 'notifyWhenChangesStop' } }),
      showTables: ko.observable(true),
      showViews: ko.observable(true),
      activeEditorTables: ko.observableArray([])
    };

    huePubSub.subscribe('editor.active.locations', function (activeLocations) {
      var activeTables = [];
      // TODO: Test multiple snippets
      if (self.sourceType !== activeLocations.type) {
        return;
      }
      activeLocations.locations.forEach(function (location) {
        if (location.type === 'table') {
          activeTables.push(location.identifierChain.length == 2 ? { table: location.identifierChain[1].name, db: location.identifierChain[0].name} : { table: location.identifierChain[0].name });
        }
      });
      nestedFilter.activeEditorTables(activeTables);
    });

    var updateDatabases = function (names, lastSelectedDb) {
      dbIndex = {};
      var dbs = $.map(names, function(name) {
        var database = new AssistDbEntry({
          name: name,
          displayName: name,
          title: name,
          isDatabase: true
        }, null, self, nestedFilter, self.i18n, self.navigationSettings, sortFunctions);
        dbIndex[name] = database;
        if (name === lastSelectedDb) {
          self.selectedDatabase(database);
          self.selectedDatabaseChanged();
        }
        return database;
      });

      dbs.sort(sortFunctions[self.activeSort()]);
      self.databases(dbs);
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
        self.selectedDatabaseChanged();
        return;
      }
      var lastSelectedDb = self.apiHelper.getFromTotalStorage('assist_' + self.sourceType, 'lastSelectedDb', 'default');
      if (lastSelectedDb && dbIndex[lastSelectedDb]) {
        self.selectedDatabase(dbIndex[lastSelectedDb]);
        self.selectedDatabaseChanged();
      } else if (self.databases().length > 0) {
        self.selectedDatabase(self.databases()[0]);
        self.selectedDatabaseChanged();
      }
    };

    self.initDatabases = function (callback) {
      if (self.loading()) {
        return;
      }
      self.loading(true);
      var lastSelectedDb = self.selectedDatabase() ? self.selectedDatabase().definition.name : null;
      self.selectedDatabase(null);
      self.databases([]);
      self.apiHelper.loadDatabases({
        sourceType: self.sourceType,
        successCallback: function(data) {
          self.hasErrors(false);
          updateDatabases(data, lastSelectedDb);
          if (typeof callback === 'function') {
            callback();
          }
        },
        errorCallback: function() {
          self.hasErrors(true);
          updateDatabases([]);
        },
        database: lastSelectedDb
      });
    };

    self.modalItem = ko.observable();

    self.repositionActions = function(data, event) {
      var $container = $(event.target);
      $container.find(".assist-actions, .assist-db-header-actions").css('right', -$container.scrollLeft() + 'px');
    };

    self.reload = function(allCacheTypes) {
      self.reloading(true);
      huePubSub.publish('assist.clear.db.cache', {
        sourceType: self.sourceType,
        clearAll: true,
        invalidateImpala: self.invalidateOnRefresh()
      });
      if (allCacheTypes) {
        huePubSub.publish('assist.clear.db.cache', {
          sourceType: self.sourceType,
          cacheType: 'optimizer',
          clearAll: true
        });
      }
      self.invalidateOnRefresh('cache');
      self.initDatabases();
    };

    huePubSub.subscribe('assist.db.refresh', function (options) {
      if (self.sourceType === options.sourceType) {
        self.reload(options.allCacheTypes);
      }
    });
  }

  AssistDbSource.prototype.highlightInside = function (path) {
    var self = this;

    var foundDb;
    var index;

    var findDatabase = function () {
      $.each(self.databases(), function (idx, db) {
        db.highlight(false);
        if (db.databaseName === path[0]) {
          foundDb = db;
          index = idx;
        }
      });

      if (foundDb) {
        var whenLoaded = function () {
          if (self.selectedDatabase() !== foundDb) {
            self.selectedDatabase(foundDb);
          }
          if (!foundDb.open()) {
            foundDb.open(true);
          }
          window.setTimeout(function () {
            huePubSub.subscribeOnce('assist.db.scrollToComplete', function () {
              foundDb.highlight(true);
              // Timeout is for animation effect
              window.setTimeout(function () {
                foundDb.highlight(false);
              }, 1800);
            });
            if (path.length > 1) {
              foundDb.highlightInside(path.slice(1), []);
            } else {
              huePubSub.publish('assist.db.scrollTo', foundDb);
            }
          }, 0);
        };

        if (foundDb.hasEntries()) {
          whenLoaded();
        } else {
          foundDb.loadEntries(whenLoaded);
        }
      }
    };

    if (!self.loaded()) {
      self.initDatabases(findDatabase);
    } else {
      findDatabase();
    }
  };

  AssistDbSource.prototype.toggleSearch = function () {
    var self = this;
    self.isSearchVisible(!self.isSearchVisible());
    self.editingSearch(self.isSearchVisible());
  };

  AssistDbSource.prototype.triggerRefresh = function (data, event) {
    var self = this;
    huePubSub.publish('assist.db.refresh', { sourceType: self.sourceType, allCacheTypes: event.shiftKey });
  };

  return AssistDbSource;
})();
