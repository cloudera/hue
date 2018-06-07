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
        namespace: self.namespace(),
        name: null
      });
    });

    self.reloading = ko.observable(false);
    self.loading = ko.observable(false);

    self.currentTab = ko.observable('');

    self.lastLoadNamespacesDeferred = $.Deferred();
    self.namespace = ko.observable();
    self.namespaces = ko.observableArray();

    self.namespace.subscribe(function () {
      if (self.namespace() && self.namespace().databases().length === 0) {
        self.namespace().loadDatabases();
      }
    });

    huePubSub.subscribe('data.catalog.entry.refreshed', function (details) {
      var refreshedEntry = details.entry;

      if (refreshedEntry.getSourceType() !== self.sourceType()) {
        return;
      }

      var prevNamespaceId = null;
      var prevDbName = null;
      var prevTableName = null;
      if (self.namespace()) {
        prevNamespaceId = self.namespace().namespace.id;
        if (self.namespace().database()) {
          prevDbName = self.namespace().database().catalogEntry.name;
          if (self.namespace().database().table()) {
            prevTableName = self.namespace().database().table().catalogEntry.name;
          }

        }
      }

      var setPrevious = function () {
        if (prevNamespaceId) {
          self.setNamespaceById(prevNamespaceId).done(function () {
            if (prevDbName) {
              self.namespace().setDatabaseByName(prevDbName, function () {
                if (self.namespace().database() && prevTableName) {
                  self.namespace().database().setTableByName(prevTableName);
                }
              });
            }
          });
        }
      };

      var completeRefresh = function () {
        self.reloading(true);
        if (self.namespace() && self.namespace().database() && self.namespace().database().table()) {
          self.namespace().database().table(null);
        }
        if (self.namespace() && self.namespace().database()) {
          self.namespace().database(null);
        }
        if (self.namespace()) {
          self.namespace(null);
        }
        self.loadNamespaces().done(setPrevious).always(function () {
          self.reloading(false);
        });
      };

      if (refreshedEntry.isSource()) {
        completeRefresh();
      } else if (refreshedEntry.isDatabase() && self.namespace()) {
        self.namespace().databases().some(function (database) {
          if (database.catalogEntry === refreshedEntry) {
            database.load(setPrevious, self.optimizerEnabled(), self.navigatorEnabled());
            return true;
          }
        })
      } else if (refreshedEntry.isTableOrView()) {
        self.namespace().databases().some(function (database) {
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

    huePubSub.subscribe('assist.database.selected', function (databaseDef) {
      if (self.sourceType() !== databaseDef.sourceType) {
        self.sourceType(databaseDef.sourceType);
      }
      if (self.namespace() !== databaseDef.namespace) {
        self.namespace(databaseDef.namespace);
      }
      // TODO: Handle namespaces + sourceType
      if (self.namespace() && self.database()) {
        self.namespace().database().table(null);
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
      if (self.namespace()) {
        if (self.namespace().database() && self.namespace().database().table()) {
          hueUtils.changeURL(prefix + 'table/' + self.namespace().database().table().catalogEntry.path.join('/'));
        }
        else if (self.namespace().database()) {
          hueUtils.changeURL(prefix + 'tables/' + self.namespace().database().catalogEntry.name);
        }
        else {
          hueUtils.changeURL(prefix + 'databases');
        }
      }
    });

    self.loadNamespaces().done(function () {
      self.loadUrl();
    });

    window.onpopstate = function () {
      if (window.location.pathname.indexOf('/metastore') > -1) {
        self.loadUrl();
      }
    };

    self.namespacesBreadcrumb = function () {
      if (self.namespace() && self.namespace().database()) {
        self.namespace().database().table(null);
      }
      if (self.namespace()) {
        self.namespace().database(null)
      }
      self.namespace(null);
      huePubSub.publish('metastore.url.change');
    };

    self.databasesBreadcrumb = function () {
      if (self.namespace().database()) {
        self.namespace().database().table(null);
      }
      self.namespace().database(null);
      huePubSub.publish('metastore.url.change');
    };

    self.tablesBreadcrumb = function () {
      self.namespace().database().table(null);
      huePubSub.publish('metastore.url.change')
    }
  }

  MetastoreViewModel.prototype.loadNamespaces = function () {
    var self = this;
    self.lastLoadNamespacesDeferred = $.Deferred();
    ContextCatalog.getNamespaces({ sourceType: self.sourceType() }).done(function (namespaces) {
      self.namespaces($.map(namespaces, function (namespace) {
        return new MetastoreNamespace({
          metastoreViewModel: self,
          sourceType: self.sourceType,
          navigatorEnabled: self.navigatorEnabled,
          optimizerEnabled: self.optimizerEnabled,
          namespace: namespace
        });
      }));
      self.namespace(self.namespaces()[0]);
      self.lastLoadNamespacesDeferred.resolve();
    }).fail(self.lastLoadNamespacesDeferred.reject);
    return self.lastLoadNamespacesDeferred;
  };

  MetastoreViewModel.prototype.setNamespaceById = function (namespaceId) {
    var self = this;
    var deferred = $.Deferred();
    self.lastLoadNamespacesDeferred.done(function () {
      var found = self.namespaces().some(function (namespace) {
        if (namespace.namespace.id === namespaceId) {
          self.namespace(namespace);
          return true;
          deferred.resolve();
        }
      });
      if (!found) {
        deferred.reject();
      }
    }).fail(deferred.reject);
    return deferred.promise();
  }


  MetastoreViewModel.prototype.loadTableDef = function (tableDef, callback) {
    var self = this;
    if (self.sourceType() !== tableDef.sourceType) {
      self.sourceType(tableDef.sourceType);
    }
    if (self.namespace() !== tableDef.namespace) {
      self.namespace(tableDef.namespace);
    }
    self.namespace().setDatabaseByName(tableDef.database, function () {
      if (self.namespace() && self.namespace().database()) {
        if (self.namespace().database().table() && self.namespace().database().table().catalogEntry.name === tableDef.name) {
          if (callback) {
            callback();
          }
          return;
        }

        var setTableAfterLoad = function (clearDbCacheOnMissing) {
          var foundTables = self.namespace().database().tables().filter(function (table) {
            return table.catalogEntry.name === tableDef.name;
          });
          if (foundTables.length === 1) {
            self.namespace().database().setTable(foundTables[0], callback);
          } else if (clearDbCacheOnMissing) {
            self.namespace().database().catalogEntry.clearCache({ invalidate: 'invalidate', silenceErrors: true }).done(function () {
              self.namespace().database().load(function () {
                setTableAfterLoad(false);
              });
            });
          } else {
            self.loadingTable(false);
          }
        };

        if (!self.namespace().database().loaded()) {
          var doOnce = self.namespace().database().loaded.subscribe(function () {
            setTableAfterLoad(true);
            doOnce.dispose();
          });
        } else {
          setTableAfterLoad(true);
        }
      }
    });
  };

  MetastoreViewModel.prototype.loadUrl = function () {
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
    var namespace = self.namespace();
    switch (path[0]) {
      case 'databases':
        if (namespace.database()) {
          namespace.database().table(null);
          namespace.database(null);
        }
        break;
      case 'tables':
        if (namespace.database()) {
          namespace.database().table(null);
        }
        namespace.setDatabaseByName(path[1]);
        break;
      case 'table':
        huePubSub.subscribe('metastore.loaded.table', function() {
          self.currentTab('overview');
        }, 'metastore');
        self.loadTableDef({
          name: path[2],
          database: path[1],
          sourceType: self.sourceType(),
          namespace: namespace
        }, function(){
          if (path.length > 3 && path[3] === 'partitions'){
            huePubSub.subscribe('metastore.loaded.partitions', function() {
              self.currentTab('partitions');
            }, 'metastore');
          }
        });
    }
  };

  return MetastoreViewModel;
})();
