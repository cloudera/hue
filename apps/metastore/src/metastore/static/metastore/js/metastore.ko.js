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
    self.apiHelper = window.apiHelper;
    self.isLeftPanelVisible = ko.observable();
    self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);
    self.optimizerEnabled = ko.observable(options.optimizerEnabled || false);
    self.navigatorEnabled = ko.observable(options.navigatorEnabled || false);
    self.appConfig = ko.observable();

    self.source = ko.observable();
    self.sources = ko.observableArray();

    self.source.subscribe(function (newValue) {
      newValue.loadNamespaces().done(function () {
        if (newValue.namespace()) {
          newValue.namespace().loadDatabases().done(function () {
            self.loadUrl();
          });
        }
      });
    });

    // When manually changed through dropdown
    self.sourceChanged = function () {
      huePubSub.publish('metastore.url.change')
    };

    self.loading = ko.pureComputed(function () {
      if (!self.source()) {
        return true;
      }
      if (self.source().loading()) {
        return true;
      }
      return false;
    });

    huePubSub.publish('cluster.config.get.config', function (clusterConfig) {
      var initialSourceType = options.sourceType || 'hive';
      if (clusterConfig && clusterConfig.app_config && (
          (clusterConfig.app_config.editor && clusterConfig.app_config.editor.interpreters) || clusterConfig.app_config.catalogs)) {
        var sources = [];
        clusterConfig.app_config.editor.interpreters.forEach(function (interpreter) {
          if (interpreter.is_sql) {
            sources.push(new MetastoreSource({
              metastoreViewModel: self,
              name: interpreter.name,
              type: interpreter.type
            }))
          }
        });
        if (clusterConfig.app_config.catalogs) {
          clusterConfig.app_config.catalogs.forEach(function (interpreter) {
            sources.push(new MetastoreSource({
              metastoreViewModel: self,
              name: interpreter.name,
              type: interpreter.type
            }))
          });
        }
        if (!sources.length) {
          sources.push(new MetastoreSource({
            metastoreViewModel: self,
            name: initialSourceType,
            type: initialSourceType
          }));
        }
        self.sources(sources);
        var found = sources.some(function (source) {
          if (source.type === initialSourceType) {
            self.source(source);
            return true;
          }
        });
        if (!found) {
          self.source(sources[0]);
        }
      }
    });

    self.navigatorEnabled.subscribe(function (newValue) {
      huePubSub.publish('meta.navigator.enabled', newValue);
    });

    self.optimizerUrl = ko.observable(options.optimizerUrl);
    self.navigatorUrl = ko.observable(options.navigatorUrl);

    self.currentTab = ko.observable('');

    huePubSub.subscribe('assist.database.selected', function (databaseDef) {
      if (self.source().type !== databaseDef.sourceType) {
        var found = self.sources().some(function (source) {
          if (source.type === databaseDef.sourceType) {
            self.source(source);
            return true;
          }
        });
        if (!found) {
          return;
        }
      }

      if (self.source().namespace().id !== databaseDef.namespace.id) {
        var found = self.source().namespaces().some(function (namespace) {
          if (namespace.id === databaseDef.namespace.id) {
            self.source().namespace(namespace);
            return true;
          }
        });
        if (!found) {
          return;
        }
      }
      if (self.source().namespace().database()) {
        self.source().namespace().database().table(null);
      }
      self.source().namespace().setDatabaseByName(databaseDef.name, function () {
        huePubSub.publish('metastore.url.change')
      });
    });

    huePubSub.subscribe("assist.table.selected", function (tableDef) {
      self.loadTableDef(tableDef, function () {
        huePubSub.publish('metastore.url.change')
      });
    });

    huePubSub.subscribe('metastore.url.change', function () {
      var prefix = '/hue/metastore/';
      if (self.source() && self.source().namespace()) {
        var params = {
          source_type: self.source().type
        };
        if (window.HAS_MULTI_CLUSTER) {
          params.namespace = self.source().namespace().id
        }
        if (self.source().namespace().database() && self.source().namespace().database().table()) {
          hueUtils.changeURL(prefix + 'table/' + self.source().namespace().database().table().catalogEntry.path.join('/'), params);
        } else if (self.source().namespace().database()) {
          hueUtils.changeURL(prefix + 'tables/' + self.source().namespace().database().catalogEntry.name, params);
        } else {
          hueUtils.changeURL(prefix + 'databases', params);
        }
      }
    });

    window.onpopstate = function () {
      if (window.location.pathname.indexOf('/metastore') > -1) {
        self.loadUrl();
      }
    };

    self.databasesBreadcrumb = function () {
      if (self.source().namespace().database()) {
        self.source().namespace().database().table(null);
      }
      self.source().namespace().database(null);
      huePubSub.publish('metastore.url.change');
    };

    self.tablesBreadcrumb = function () {
      self.source().namespace().database().table(null);
      huePubSub.publish('metastore.url.change')
    }
  }

  MetastoreViewModel.prototype.loadTableDef = function (tableDef, callback) {
    var self = this;
    if (self.source().type !== tableDef.sourceType) {
      var found = self.sources().some(function (source) {
        if (source.type === tableDef.sourceType) {
          self.source(source);
          return true;
        }
      });
      if (!found) {
        return;
      }
    }
    if (self.source().namespace().id !== tableDef.namespace.id) {
      var found = self.source().namespaces().some(function (namespace) {
        if (namespace.id === tableDef.namespace.id) {
          self.source().namespace(namespace);
          return true;
        }
      });
      if (!found) {
        return;
      }
    }
    self.source().namespace().setDatabaseByName(tableDef.database, function () {
      if (self.source().namespace().database()) {
        if (self.source().namespace().database().table() && self.source().namespace().database().table().catalogEntry.name === tableDef.name) {
          if (callback) {
            callback();
          }
          return;
        }

        var setTableAfterLoad = function (clearDbCacheOnMissing) {
          var foundTables = self.source().namespace().database().tables().filter(function (table) {
            return table.catalogEntry.name === tableDef.name;
          });
          if (foundTables.length === 1) {
            self.source().namespace().database().setTable(foundTables[0], callback);
          } else if (clearDbCacheOnMissing) {
            self.source().namespace().database().catalogEntry.clearCache({ invalidate: 'invalidate', silenceErrors: true }).then(function () {
              self.source().namespace().database().load(function () {
                setTableAfterLoad(false);
              });
            });
          }
        };

        if (!self.source().namespace().database().loaded()) {
          var doOnce = self.source().namespace().database().loaded.subscribe(function () {
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

    var path = window.location.pathname.substr(4);
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
    var loadedDeferred = $.Deferred();

    if (!self.loading()) {
      loadedDeferred.resolve();
    } else {
      var loadSub = self.loading.subscribe(function () {
        loadSub.dispose();
        loadedDeferred.resolve();
      })
    }

    var sourceAndNamespaceDeferred = $.Deferred();

    loadedDeferred.done(function () {
      var search = location.search;
      var namespaceId;
      var sourceType;
      if (search) {
        search = search.replace('?', '');
        search.split('&').forEach(function (param) {
          if (param.indexOf('namespace=') === 0) {
            namespaceId = param.replace('namespace=', '');
          }
          if (param.indexOf('source_type=') === 0) {
            sourceType = param.replace('source_type=', '');
          }
        });
      }

      if (sourceType && sourceType !== self.source().type) {
        var found = self.sources().some(function (source) {
          if (source.type === sourceType) {
            self.source(source);
            return true;
          }
        });
        if (!found) {
          sourceAndNamespaceDeferred.reject();
          return;
        }
      }

      if (!namespaceId && window.apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedNamespace')) {
        namespaceId = window.apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedNamespace').id;
      }

      self.source().lastLoadNamespacesDeferred.done(function () {
        if (namespaceId && namespaceId !== self.source().namespace().id) {
          var found = self.source().namespaces().some(function (namespace) {
            if (namespace.id === namespaceId) {
              self.source().namespace(namespace);
              return true;
            }
          });
          if (!found) {
            sourceAndNamespaceDeferred.reject();
            return;
          } else {
            sourceAndNamespaceDeferred.resolve();
          }
        } else {
          sourceAndNamespaceDeferred.resolve();
        }
      });
    });


    sourceAndNamespaceDeferred.done(function () {
      var namespace = self.source().namespace();
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
            sourceType: self.source().type,
            namespace: namespace
          }, function(){
            if (path.length > 3 && path[3] === 'partitions'){
              huePubSub.subscribe('metastore.loaded.partitions', function() {
                self.currentTab('partitions');
              }, 'metastore');
            }
          });
      }
    })
  };

  return MetastoreViewModel;
})();
