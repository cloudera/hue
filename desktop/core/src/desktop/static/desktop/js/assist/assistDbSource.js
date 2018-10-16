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
  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {string} options.type
   * @param {ContextNamespace} [options.initialNamespace] - Optional initial namespace to use
   * @param {ContextCompute} [options.initialCompute] - Optional initial compute to use
   * @param {string} options.name
   * @param {boolean} options.nonSqlType - Optional, default false
   * @param {Object} options.navigationSettings
   * @constructor
   */
  function AssistDbSource (options) {
    var self = this;

    self.sourceType = options.type;
    self.name = options.name;
    self.i18n = options.i18n;
    self.nonSqlType = options.nonSqlType;
    self.navigationSettings = options.navigationSettings;
    var apiHelper = ApiHelper.getInstance();
    self.initialNamespace = options.initialNamespace || apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedNamespace');
    self.initialCompute = options.initialCompute || apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedCompute');

    self.selectedNamespace = ko.observable();
    self.namespaces = ko.observableArray();

    self.loadedDeferred = $.Deferred();
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);

    self.filter = {
      querySpec: ko.observable({}).extend({ rateLimit: 300 })
    };

    self.filteredNamespaces = ko.pureComputed(function () {
      if (!self.filter.querySpec() || typeof self.filter.querySpec().query === 'undefined' || !self.filter.querySpec().query) {
        return self.namespaces();
      }
      return self.namespaces().filter(function (namespace) {
        return namespace.name.toLowerCase().indexOf(self.filter.querySpec().query.toLowerCase()) !== -1
      });
    });

    self.autocompleteFromNamespaces = function (nonPartial, partial) {
      var result = [];
      var partialLower = partial.toLowerCase();
      self.namespaces().forEach(function (namespace) {
        if (namespace.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + namespace.name.substring(partial.length))
        }
      });
      return result;
    };

    var ensureDbSet = function () {
      if (self.nonSqlType) {
        if (!self.selectedNamespace().selectedDatabase()) {
          self.selectedNamespace().selectedDatabase(self.selectedNamespace().databases()[0]);
          self.selectedNamespace().selectedDatabaseChanged();
        }
      }
    };

    self.selectedNamespace.subscribe(function (namespace) {
      if (namespace && !namespace.loaded() && !namespace.loading()) {
        namespace.initDatabases(ensureDbSet);
      } else {
        ensureDbSet();
      }
    });

    self.hasNamespaces = ko.pureComputed(function () {
      return self.namespaces().length > 0;
    });

    huePubSub.subscribe('context.catalog.namespaces.refreshed', function (sourceType) {
      if (self.sourceType !== sourceType) {
        return;
      }

      self.loading(true);
      ContextCatalog.getNamespaces({ sourceType: self.sourceType }).done(function (context) {
        var newNamespaces = [];
        var existingNamespaceIndex = {};
        self.namespaces().forEach(function (assistNamespace) {
          existingNamespaceIndex[assistNamespace.namespace.id] = assistNamespace;
        });
        context.namespaces.forEach(function(newNamespace) {
          if (existingNamespaceIndex[newNamespace.id]) {
            existingNamespaceIndex[newNamespace.id].namespace = newNamespace;
            existingNamespaceIndex[newNamespace.id].name = newNamespace.name;
            newNamespaces.push(existingNamespaceIndex[newNamespace.id]);
          } else {
            newNamespaces.push(new AssistDbNamespace({
              sourceType: self.sourceType,
              namespace: newNamespace,
              i18n: self.i18n,
              nonSqlType: self.nonSqlType,
              navigationSettings: self.navigationSettings
            }));
          }
        });
        self.namespaces(newNamespaces);
      }).always(function () {
        self.loading(false);
      })
    });
  }

  AssistDbSource.prototype.whenLoaded = function (callback) {
    var self = this;
    self.loadedDeferred.done(callback);
  };

  AssistDbSource.prototype.loadNamespaces = function (refresh) {
    var self = this;
    self.loading(true);

    if (refresh) {
      ContextCatalog.getComputes({ sourceType: self.sourceType, clearCache: true });
    }

    return ContextCatalog.getNamespaces({ sourceType: self.sourceType, clearCache: refresh }).done(function (context) {
      var assistNamespaces = [];
      var activeNamespace;
      var activeCompute;
      context.namespaces.forEach(function (namespace) {
        var assistNamespace = new AssistDbNamespace({
          sourceType: self.sourceType,
          namespace: namespace,
          i18n: self.i18n,
          nonSqlType: self.nonSqlType,
          navigationSettings: self.navigationSettings
        });

        if (self.initialNamespace && namespace.id === self.initialNamespace.id) {
          activeNamespace = assistNamespace;
          if (self.initialCompute) {
            activeNamespace.namespace.computes.some(function (compute) {
              if (compute.id === self.initialCompute.id) {
                activeCompute = compute;
              }
            })
          }
        }
        assistNamespaces.push(assistNamespace);
      });
      self.namespaces(assistNamespaces);
      if (!refresh && activeNamespace) {
        self.selectedNamespace(activeNamespace);
      } else if (!refresh && assistNamespaces.length) {
        self.selectedNamespace(assistNamespaces[0]);
      }
      if (!refresh && activeCompute) {
        self.selectedNamespace().compute(activeCompute);
      }
    }).fail(function () {
      self.hasErrors(true);
    }).always(function () {
      self.loadedDeferred.resolve();
      self.loading(false);
    })
  };

  AssistDbSource.prototype.highlightInside = function (catalogEntry) {
    var self = this;
    if (self.navigationSettings.rightAssist) {
      return;
    }

    var whenLoaded = function () {
      self.namespaces().some(function (namespace) {
        if (namespace.namespace.id === catalogEntry.namespace.id) {
          if (self.selectedNamespace() !== namespace) {
            self.selectedNamespace(namespace);
          }
          if (self.selectedNamespace().hasEntries()) {
            self.selectedNamespace().highlightInside(catalogEntry);
          } else {
            self.selectedNamespace().initDatabases(function () {
              self.selectedNamespace().highlightInside(catalogEntry);
            })
          }
          return true;
        }
      })
    };

    if (self.namespaces().length) {
      whenLoaded();
    } else if (self.loading()) {
      var loadingSub = self.loading.subscribe(function () {
        loadingSub.dispose();
        whenLoaded();
      })
    } else {
      self.loadNamespaces().done(whenLoaded);
    }
  };

  AssistDbSource.prototype.triggerRefresh = function (data, event) {
    var self = this;
    self.loadNamespaces(true);
  };

  return AssistDbSource;
})();



var AssistDbNamespace = (function () {

  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {string} options.sourceType
   * @param {ContextNamespace} options.namespace
   * @param {boolean} options.nonSqlType - Optional, default false
   * @param {Object} options.navigationSettings
   * @constructor
   */
  function AssistDbNamespace (options) {
    var self = this;

    self.i18n = options.i18n;
    self.navigationSettings = options.navigationSettings;
    self.sourceType = options.sourceType;
    self.nonSqlType = options.nonSqlType;

    self.namespace = options.namespace;
    // TODO: Compute selection in assist?
    self.compute = ko.observable();
    if (self.namespace.computes.length) {
      self.compute(self.namespace.computes[0]);
    }
    self.name = options.namespace.name;

    self.dbIndex = {};
    self.databases = ko.observableArray();
    self.selectedDatabase = ko.observable();

    self.highlight = ko.observable(false);

    self.loadedPromise = $.Deferred();
    self.loadedDeferred = $.Deferred();
    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.reloading = ko.observable(false);
    self.hasErrors = ko.observable(false);
    self.invalidateOnRefresh = ko.observable('cache');

    self.loadingTables = ko.pureComputed(function() {
      return typeof self.selectedDatabase() !== 'undefined' && self.selectedDatabase() !== null && self.selectedDatabase().loading();
    });

    self.filter = {
      querySpec: ko.observable({}).extend({ rateLimit: 300 })
    };

    self.hasEntries = ko.pureComputed(function() {
      return self.databases().length > 0;
    });

    self.filteredEntries = ko.pureComputed(function () {
      if (!self.filter.querySpec() || typeof self.filter.querySpec().query === 'undefined' || !self.filter.querySpec().query) {
        return self.databases();
      }
      return self.databases().filter(function (database) {
        return database.catalogEntry.name.toLowerCase().indexOf(self.filter.querySpec().query.toLowerCase()) !== -1
      });
    });

    self.autocompleteFromEntries = function (nonPartial, partial) {
      var result = [];
      var partialLower = partial.toLowerCase();
      self.databases().forEach(function (db) {
        if (db.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + db.catalogEntry.name.substring(partial.length))
        }
      });
      return result;
    };

    self.selectedDatabase.subscribe(function () {
      var db = self.selectedDatabase();
      if (HAS_OPTIMIZER && db && !db.popularityIndexSet && !self.nonSqlType) {
        db.catalogEntry.loadNavOptPopularityForChildren({ silenceErrors: true }).done(function () {
          var applyPopularity = function () {
            db.entries().forEach(function (entry) {
              if (entry.catalogEntry.navOptPopularity && entry.catalogEntry.navOptPopularity.popularity >= 5) {
                entry.popularity(entry.catalogEntry.navOptPopularity.popularity )
              }
            });
          };

          if (db.loading()) {
            var subscription = db.loading.subscribe(function () {
              subscription.dispose();
              applyPopularity();
            });
          } else if (db.entries().length === 0) {
            var subscription = db.entries.subscribe(function (newEntries) {
              if (newEntries.length > 0) {
                subscription.dispose();
                applyPopularity();
              }
            });
          } else {
            applyPopularity();
          }
        });
      }
    });

    self.selectedDatabaseChanged = function () {
      if (self.selectedDatabase()) {
        if (!self.selectedDatabase().hasEntries() && !self.selectedDatabase().loading()) {
          self.selectedDatabase().loadEntries()
        }
        if (!self.navigationSettings.rightAssist) {
          ApiHelper.getInstance().setInTotalStorage('assist_' + self.sourceType + '_' + self.namespace.id, 'lastSelectedDb', self.selectedDatabase().catalogEntry.name);
          huePubSub.publish('assist.database.set', {
            sourceType: self.sourceType,
            namespace: self.namespace,
            name: self.selectedDatabase().catalogEntry.name
          })
        }
      }
    };

    var nestedFilter = {
      querySpec: ko.observable({}).extend({ rateLimit: 300 })
    };

    self.setDatabase = function (databaseName) {
      if (databaseName && self.selectedDatabase() && databaseName === self.selectedDatabase().catalogEntry.name) {
        return;
      }
      if (databaseName && self.dbIndex[databaseName]) {
        self.selectedDatabase(self.dbIndex[databaseName]);
        self.selectedDatabaseChanged();
        return;
      }
      var lastSelectedDb = ApiHelper.getInstance().getFromTotalStorage('assist_' + self.sourceType + '_' + self.namespace.id, 'lastSelectedDb', 'default');
      if (lastSelectedDb && self.dbIndex[lastSelectedDb]) {
        self.selectedDatabase(self.dbIndex[lastSelectedDb]);
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
      self.hasErrors(false);

      var lastSelectedDbName = self.selectedDatabase() ? self.selectedDatabase().catalogEntry.name : null;

      self.selectedDatabase(null);
      self.databases([]);

      DataCatalog.getEntry({ sourceType: self.sourceType, namespace: self.namespace, compute: self.compute(), path : [], definition: { type: 'source' } }).done(function (catalogEntry) {
        self.catalogEntry = catalogEntry;
        self.catalogEntry.getChildren({ silenceErrors: self.navigationSettings.rightAssist }).done(function (databaseEntries) {
          self.dbIndex = {};
          var hasNavMeta = false;
          var dbs = [];

          databaseEntries.forEach(function (catalogEntry) {
            hasNavMeta = hasNavMeta || !!catalogEntry.navigatorMeta;
            var database = new AssistDbEntry(catalogEntry, null, self, nestedFilter, self.i18n, self.navigationSettings);
            self.dbIndex[catalogEntry.name] = database;
            if (catalogEntry.name === lastSelectedDbName) {
              self.selectedDatabase(database);
              self.selectedDatabaseChanged();
            }
            dbs.push(database);
          });

          if (!hasNavMeta && !self.nonSqlType) {
            self.catalogEntry.loadNavigatorMetaForChildren({ silenceErrors: true });
          }
          self.databases(dbs);

          if (typeof callback === 'function') {
            callback();
          }
        }).fail(function () {
          self.hasErrors(true);
        }).always(function () {
          self.loaded(true);
          self.loadedDeferred.resolve();
          self.loading(false);
          self.reloading(false);
        });

      });
    };

    self.modalItem = ko.observable();

    if (!self.navigationSettings.rightAssist) {
      huePubSub.subscribe('data.catalog.entry.refreshed', function (details) {
        if (self.namespace.id !== details.entry.namespace.id || details.entry.getSourceType() !== self.sourceType) {
          return;
        }
        if (self.catalogEntry === details.entry) {
          self.initDatabases();
        } else {
          var findAndReloadInside = function (entries) {
            return entries.some(function (entry) {
              if (entry.catalogEntry.path.join('.') === details.entry.path.join('.')) {
                entry.catalogEntry = details.entry;
                entry.loadEntries();
                return true;
              }
              return findAndReloadInside(entry.entries());
            })
          };
          findAndReloadInside(self.databases());
        }
      });
    }
  }

  AssistDbNamespace.prototype.whenLoaded = function (callback) {
    var self = this;
    self.loadedDeferred.done(callback);
  };

  AssistDbNamespace.prototype.highlightInside = function (catalogEntry) {
    var self = this;
    var foundDb;
    var index;

    var findDatabase = function () {
      $.each(self.databases(), function (idx, db) {
        db.highlight(false);
        if (db.databaseName === catalogEntry.path[0]) {
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
            if (catalogEntry.path.length > 1) {
              foundDb.highlightInside(catalogEntry.path.slice(1));
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

  AssistDbNamespace.prototype.triggerRefresh = function (data, event) {
    var self = this;
    if (self.catalogEntry) {
      self.catalogEntry.clearCache({ invalidate: self.invalidateOnRefresh() });
    }
  };

  return AssistDbNamespace;
})();
