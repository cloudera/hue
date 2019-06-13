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

var MetastoreSource = (function () {

  var MetastoreSource = function (options) {
    var self = this;
    self.type = options.type;
    self.name = options.name;
    self.metastoreViewModel = options.metastoreViewModel;

    self.reloading = ko.observable(false);
    self.loading = ko.observable(false);

    self.lastLoadNamespacesDeferred = $.Deferred();
    self.namespace = ko.observable();
    self.namespaces = ko.observableArray();

    self.namespace.subscribe(function () {
      if (self.namespace() && self.namespace().databases().length === 0) {
        self.namespace().loadDatabases();
      }
    });

    // When manually changed through dropdown
    self.namespaceChanged = function (newNamespace, previousNamespace) {
      if (previousNamespace.database() && !self.namespace().database()) {
        // Try to set the same database by name, if not there it will revert to 'default'
        self.namespace().setDatabaseByName(previousNamespace.database().catalogEntry.name, function () {
          huePubSub.publish('metastore.url.change');
        });
      } else {
        huePubSub.publish('metastore.url.change');
      }
    };

    huePubSub.subscribe("assist.db.panel.ready", function () {
      self.lastLoadNamespacesDeferred.done(function () {
        var lastSelectedDb = window.apiHelper.getFromTotalStorage('assist_' + self.sourceType + '_' + self.namespace.id, 'lastSelectedDb', 'default');
        huePubSub.publish('assist.set.database', {
          source: self.type,
          namespace: self.namespace().namespace,
          name: lastSelectedDb
        });
      });
    });

    var getCurrentState = function () {
      var result = {
        namespaceId: null,
        database: null,
        table: null
      };
      var prevNamespaceId = null;
      var prevDbName = null;
      var prevTableName = null;
      if (self.namespace()) {
        result.namespaceId = self.namespace().id;
        if (self.namespace().database()) {
          result.database = self.namespace().database().catalogEntry.name;
          if (self.namespace().database().table()) {
            result.table = self.namespace().database().table().catalogEntry.name;
          }
        }
      }
      return result;
    };

    var setState = function (state) {
      if (state.namespaceId) {
        self.setNamespaceById(state.namespaceId).done(function () {
          if (state.database) {
            self.namespace().setDatabaseByName(state.database, function () {
              if (self.namespace().database() && state.table) {
                self.namespace().database().setTableByName(state.table);
              }
            });
          }
        });
      }
    };

    var completeRefresh = function (previousState) {
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
      self.loadNamespaces().done(function () {
        setState(previousState);
      }).always(function () {
        self.reloading(false);
      });
    };

    huePubSub.subscribe('context.catalog.namespaces.refreshed', function (sourceType) {
      if (self.type !== sourceType) {
        return;
      }
      var previousState = getCurrentState();
      completeRefresh(previousState);
    });

    huePubSub.subscribe('data.catalog.entry.refreshed', function (details) {
      var refreshedEntry = details.entry;

      if (refreshedEntry.getSourceType() !== self.type) {
        return;
      }

      var previousState = getCurrentState();

      if (refreshedEntry.isSource()) {
        completeRefresh(previousState);
      } else if (refreshedEntry.isDatabase() && self.namespace()) {
        self.namespace().databases().some(function (database) {
          if (database.catalogEntry === refreshedEntry) {
            database.load(function () {
              setState(previousState);
            }, self.metastoreViewModel.optimizerEnabled(), self.metastoreViewModel.navigatorEnabled());
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
  };

  MetastoreSource.prototype.loadNamespaces = function () {
    var self = this;
    self.loading(true);
    contextCatalog.getNamespaces({ sourceType: self.type }).done(function (context) {
      var namespacesWithComputes = context.namespaces.filter(function (namespace) { return namespace.computes.length });
      self.namespaces($.map(namespacesWithComputes, function (namespace) {
        return new MetastoreNamespace({
          metastoreViewModel: self.metastoreViewModel,
          sourceType: self.type,
          navigatorEnabled: self.metastoreViewModel.navigatorEnabled,
          optimizerEnabled: self.metastoreViewModel.optimizerEnabled,
          namespace: namespace
        });
      }));
      self.namespace(self.namespaces()[0]);
      self.lastLoadNamespacesDeferred.resolve();
    }).fail(self.lastLoadNamespacesDeferred.reject).always(function () {
      self.loading(false);
    });
    return self.lastLoadNamespacesDeferred;
  };


  MetastoreSource.prototype.setNamespaceById = function (namespaceId) {
    var self = this;
    var deferred = $.Deferred();
    self.lastLoadNamespacesDeferred.done(function () {
      var found = self.namespaces().some(function (namespace) {
        if (namespace.namespace.id === namespaceId) {
          self.namespace(namespace);
          deferred.resolve();
          return true;
        }
      });
      if (!found) {
        deferred.reject();
      }
    }).fail(deferred.reject);
    return deferred.promise();
  }

  return MetastoreSource;
})();

var MetastoreNamespace = (function () {

  var MetastoreNamespace = function (options) {
    var self = this;
    self.apiHelper = window.apiHelper;
    self.namespace = options.namespace;

    // TODO: Compute selection in the metastore?
    self.compute = options.namespace.computes[0];
    self.id = options.namespace.id;
    self.name = options.namespace.name;
    self.metastoreViewModel = options.metastoreViewModel;
    self.sourceType = options.sourceType;
    self.navigatorEnabled = options.navigatorEnabled;
    self.optimizerEnabled = options.optimizerEnabled;

    self.catalogEntry = ko.observable();

    self.database = ko.observable();
    self.databases = ko.observableArray();
    self.selectedDatabases = ko.observableArray();
    self.loadingDatabases = ko.observable(false);
    self.lastLoadDatabasesPromise = undefined;
  };

  MetastoreNamespace.prototype.loadDatabases = function () {
    var self = this;
    if (self.loadingDatabases() && self.lastLoadDatabasesPromise) {
      return self.lastLoadDatabasesPromise;
    }

    self.loadingDatabases(true);
    var deferred = $.Deferred();
    self.lastLoadDatabasesPromise = deferred.promise();

    deferred.fail(function () {
      self.databases([]);
    }).always(function () {
      self.loadingDatabases(false);
    });

    dataCatalog.getEntry({ namespace: self.namespace, compute: self.compute, sourceType: self.sourceType, path: [], definition: { type: 'source' } }).done(function (entry) {
      self.catalogEntry(entry);
      entry.getChildren().done(function (databaseEntries) {
        self.databases($.map(databaseEntries, function (databaseEntry) {
          return new MetastoreDatabase({ catalogEntry: databaseEntry, optimizerEnabled: self.optimizerEnabled, metastoreViewModel: self.metastoreViewModel });
        }));
        deferred.resolve();
      }).fail(deferred.reject);
    });

    return self.lastLoadDatabasesPromise;
  };

  MetastoreNamespace.prototype.reload = function () {
    var self = this;
    if (!self.loadingDatabases() && self.catalogEntry()) {
      self.loadingDatabases(true);
      // Clear will publish when done
      self.catalogEntry().clearCache({ invalidate: self.sourceType === 'impala' ? 'invalidate' : 'cache' });
    }
  };

  MetastoreNamespace.prototype.setDatabase = function (metastoreDatabase, callback) {
    var self = this;
    huePubSub.publish('metastore.scroll.to.top');
    self.database(metastoreDatabase);

    if (!metastoreDatabase.loaded()) {
      metastoreDatabase.load(callback, self.optimizerEnabled(), self.navigatorEnabled(), self.sourceType);
    } else if (callback) {
      callback();
    }
  };

  MetastoreNamespace.prototype.onDatabaseClick = function (catalogEntry) {
    var self = this;

    self.databases().some(function (database) {
      if (database.catalogEntry === catalogEntry) {
        self.setDatabase(database, function() { huePubSub.publish('metastore.url.change') });
        return true;
      }
    });
  };

  MetastoreNamespace.prototype.setDatabaseByName = function (databaseName, callback) {
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
        self.catalogEntry().clearCache({ invalidate: 'invalidate', silenceErrors: true }).then(function () {
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

    window.setTimeout(function () {
      if (self.loadingDatabases() && self.lastLoadDatabasesPromise !== null) {
        self.lastLoadDatabasesPromise.done(function () {
          whenLoaded(true);
        });
      } else {
        if (self.databases().length) {
          whenLoaded(true);
        } else {
          self.loadDatabases().done(function () {
            whenLoaded(true);
          })
        }
      }
    }, 0);
  };

  return MetastoreNamespace;
})();

var MetastoreDatabase = (function () {
  /**
   * @param {object} options
   * @param {DataCatalogEntry} options.catalogEntry
   * @param {observable} options.optimizerEnabled
   * @param {MetastoreViewModel} options.metastoreViewModel;
   * @constructor
   */
  function MetastoreDatabase(options) {
    var self = this;
    self.apiHelper = window.apiHelper;
    self.catalogEntry = options.catalogEntry;
    self.metastoreViewModel = options.metastoreViewModel;

    self.loaded = ko.observable(false);
    self.loadingTables = ko.observable(false);
    self.loadingAnalysis = ko.observable(false);
    self.loadingComment = ko.observable(false);
    self.loadingTableComments = ko.observable(false);
    self.loadingTablePopularity = ko.observable(false);

    self.tables = ko.observableArray();

    self.loading = ko.pureComputed(function () {
      return self.loadingTables() || self.loadingAnalysis();
    });

    self.refreshing = ko.pureComputed(function () {
      return self.loadingTables() || self.loadingAnalysis() || self.loadingComment() || self.loadingTableComments() ||
        self.loadingTablePopularity();
    });

    self.comment = ko.observable();

    self.comment.subscribe(function (newValue) {
      self.catalogEntry.getComment().done(function (comment) {
        if (comment !== newValue) {
          self.catalogEntry.setComment(newValue).done(self.comment).fail(function () {
            self.comment(comment);
          })
        }
      });
    });

    self.stats = ko.observable();
    self.navigatorMeta = ko.observable();

    self.showAddTagName = ko.observable(false);
    self.addTagName = ko.observable('');

    self.selectedTables = ko.observableArray();

    self.editingTable = ko.observable(false);
    self.table = ko.observable(null);
  }

  MetastoreDatabase.prototype.onTableClick = function (catalogEntry) {
    var self = this;
    self.tables().some(function (table) {
      if (table.catalogEntry === catalogEntry) {
        self.setTable(table, function() { huePubSub.publish('metastore.url.change'); });
        return true;
      }
    })
  };

  MetastoreDatabase.prototype.reload = function () {
    var self = this;
    // Clear will publish when done
    self.catalogEntry.clearCache({ invalidate: self.catalogEntry.getSourceType() === 'impala' ? 'invalidate' : 'cache' });
  };

  MetastoreDatabase.prototype.load = function (callback, optimizerEnabled, navigatorEnabled) {
    var self = this;


    if (navigatorEnabled) {
      self.loadingComment(true);
      self.catalogEntry.getNavigatorMeta().done(self.navigatorMeta).always(function () {
        self.loadingComment(false);
      });
    }

    self.catalogEntry.getComment().done(self.comment);

    self.loadingTables(true);
    self.catalogEntry.getChildren().done(function (tableEntries) {
      self.tables($.map(tableEntries, function (tableEntry) {
        return new MetastoreTable({
          database: self,
          catalogEntry: tableEntry,
          optimizerEnabled: optimizerEnabled,
          navigatorEnabled: navigatorEnabled
        });
      }));
      if (navigatorEnabled) {
        self.loadingTableComments(true);
        self.catalogEntry.loadNavigatorMetaForChildren().done(function () {
          self.tables().forEach(function (table) {
            table.navigatorMeta(table.catalogEntry.navigatorMeta);
          })
        }).always(function () {
          self.loadingTableComments(false);
        })
      }
      if (optimizerEnabled) {
        self.loadingTablePopularity(true);
        self.catalogEntry.loadNavOptPopularityForChildren().done(function () {
          self.tables().forEach(function (table) {
            table.optimizerStats(table.catalogEntry.navOptPopularity);
          })
        }).always(function () {
          self.loadingTablePopularity(false);
        })
      }
      self.loaded(true);
    }).fail(function () {
      self.tables([]);
    }).always(function () {
      self.loadingTables(false);
      if (callback) {
        callback();
      }
    });

    self.loadingAnalysis(true);
    self.catalogEntry.getAnalysis().done(self.stats).always(function () {
      self.loadingAnalysis(false);
    });

    self.apiHelper.setInTotalStorage('metastore', 'last.selected.database', self.name);
  };

  MetastoreDatabase.prototype.setTableByName = function (tableName) {
    var self = this;

    if (self.table() && self.table().catalogEntry.name === tableName) {
      return;
    }

    var foundTables = self.tables().filter(function (metastoreTable) {
      return metastoreTable.catalogEntry.name === tableName;
    });

    if (foundTables.length === 1) {
      self.setTable(foundTables[0]);
    }
  };

  MetastoreDatabase.prototype.setTable = function (metastoreTable, callback) {
    var self = this;
    huePubSub.publish('metastore.scroll.to.top');
    self.table(metastoreTable);
    if (!metastoreTable.loaded()) {
      metastoreTable.load();
    }
    if (callback) {
      callback();
    }
    self.metastoreViewModel.currentTab('overview');
  };

  MetastoreDatabase.prototype.showContextPopover = function (entry, event, orientation) {
    var $source = $(event.currentTarget || event.target);
    var offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: entry.catalogEntry
      },
      orientation: orientation || 'right',
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 2,
        right: offset.left + (orientation === 'left' ? 0 : $source.width() + 1),
        bottom: offset.top + $source.height() - 2
      }
    });
  };

  return MetastoreDatabase;
})();

var MetastoreTable = (function () {

  /**
   * @param {Object} options
   * @param {MetastoreTable} options.metastoreTable
   */
  function MetastoreTablePartitions(options) {
    var self = this;
    self.detailedKeys = ko.observableArray();
    self.keys = ko.observableArray();
    self.values = ko.observableArray();
    self.selectedValues = ko.observableArray();

    self.valuesFlat = ko.pureComputed(function(){
      return self.values().map(function(item){
        return item.partitionSpec
      });
    });

    self.selectedValuesFlat = ko.pureComputed(function(){
      return self.selectedValues().map(function(item){
        return item.partitionSpec
      });
    });

    self.metastoreTable = options.metastoreTable;
    self.apiHelper = window.apiHelper;

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);

    self.sortDesc = ko.observable(true);
    self.filters = ko.observableArray([]);

    self.typeaheadValues = function (column) {
      var values = [];
      self.values().forEach(function (row) {
        var cell = row.columns[self.keys().indexOf(column())];
        if (values.indexOf(cell) !== -1) {
          values.push(cell);
        }
      });
      return values
    };

    self.addFilter = function () {
      self.filters.push(ko.mapping.fromJS({'column': '', 'value': ''}));
    };

    self.removeFilter = function (data) {
      self.filters.remove(data);
      if (self.filters().length === 0) {
        self.sortDesc(true);
        self.filter();
      }
    };

    self.filter = function () {
      self.loading(true);
      self.loaded(false);
      var filters = JSON.parse(ko.toJSON(self.filters));
      var postData = {};
      filters.forEach(function (filter) {
        postData[filter.column] = filter.value;
      });
      postData['sort'] = self.sortDesc() ? 'desc' : 'asc';

      $.ajax({
        type: 'POST',
        url: '/metastore/table/' + self.metastoreTable.catalogEntry.path.join('/') + '/partitions',
        data: postData,
        success: function (data) {
          self.values(data.partition_values_json);
          self.loading(false);
          self.loaded(true);
        },
        dataType: 'json'
      });
    };

    self.preview = {
      keys: ko.observableArray(),
      values: ko.observableArray()
    }
  }

  MetastoreTablePartitions.prototype.load = function () {
    var self = this;
    if (self.loaded()) {
      return;
    }

    self.loading(true);

    self.metastoreTable.catalogEntry.getPartitions().done(function (partitions) {
      self.keys(partitions.partition_keys_json);
      self.values(partitions.partition_values_json);
      self.preview.values(self.values().slice(0, 5));
      self.preview.keys(self.keys());
      huePubSub.publish('metastore.loaded.partitions');
    }).always(function () {
      self.loading(false);
      self.loaded(true);
    });
  };

  /**
   * @param {Object} options
   * @param {MetastoreTable} options.metastoreTable
   */
  function MetastoreTableSamples(options) {
    var self = this;
    self.rows = ko.observableArray();
    self.headers = ko.observableArray();
    self.metastoreTable = options.metastoreTable;

    self.hasErrors = ko.observable(false);
    self.errorMessage = ko.observable();
    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);

    self.preview = {
      headers: ko.observableArray(),
      rows: ko.observableArray()
    }
  }

  MetastoreTableSamples.prototype.load = function () {
    var self = this;
    if (self.loaded()) {
      return;
    }
    self.hasErrors(false);
    self.loading(true);
    self.metastoreTable.catalogEntry.getSample().done(function (sample) {
      self.rows(sample.data);
      self.headers($.map(sample.meta, function (meta) { return meta.name }));
      self.preview.rows(self.rows().slice(0, 3));
      self.preview.headers(self.headers());
    }).fail(function (message) {
      self.errorMessage(message);
      self.hasErrors(true);
    }).always(function () {
      self.loading(false);
      self.loaded(true);
    });
  };

  /**
   * @param {Object} options
   * @param {MetastoreDatabase} options.database
   * @param {DataCatalogEntry} options.catalogEntry
   * @param {boolean} options.optimizerEnabled
   * @param {boolean} options.navigatorEnabled
   * @constructor
   */
  function MetastoreTable(options) {
    var self = this;
    self.database = options.database;
    self.optimizerEnabled = options.optimizerEnabled;
    self.navigatorEnabled = options.navigatorEnabled;
    self.catalogEntry = options.catalogEntry;

    self.apiHelper = window.apiHelper;

    // TODO: Check if enough or if we need to fetch additional details
    self.isView = ko.observable(self.catalogEntry.isView());
    self.viewSql = ko.observable();

    self.optimizerStats = ko.observable();
    self.optimizerDetails = ko.observable();
    self.topJoins = ko.observableArray();
    self.navigatorMeta = ko.observable();
    self.relationshipsDetails = ko.observable();

    self.loaded = ko.observable(false);

    self.loadingDetails = ko.observable(false);
    self.loadingColumns = ko.observable(false);
    self.loadingQueries = ko.observable(false);
    self.loadingComment = ko.observable(false);
    self.loadingViewSql = ko.observable(false);
    self.loadingTopJoins = ko.observable(false);

    self.columns = ko.observableArray();

    self.samples = new MetastoreTableSamples({
      metastoreTable: self
    });

    self.partitions = new MetastoreTablePartitions({
      metastoreTable: self
    });

    self.loading = ko.pureComputed(function () {
      return self.loadingDetails() || self.loadingColumns();
    });

    self.refreshing = ko.pureComputed(function () {
      return self.loadingDetails() || self.loadingColumns() || self.loadingQueries() || self.loadingComment() ||
        self.samples.loading() || self.partitions.loading() || self.loadingViewSql() || self.loadingTopJoins();
    });

    self.partitionsCountLabel = ko.pureComputed(function () {
      if (self.partitions.values().length === METASTORE_PARTITION_LIMIT) {
        return self.partitions.values().length + '+'
      }
      return self.partitions.values().length;
    });
    self.tableDetails = ko.observable();
    self.tableStats = ko.observable();
    self.refreshingTableStats = ko.observable(false);
    self.showAddTagName = ko.observable(false);
    self.addTagName = ko.observable('');

    self.comment = ko.observable();
    self.editingComment = ko.observable();

    if (self.catalogEntry.hasResolvedComment()) {
      self.comment(self.catalogEntry.getResolvedComment());
    }

    self.commentWithoutNewLines = ko.pureComputed(function(){
      return self.comment() ? hueUtils.deXSS(self.comment().replace(/[\n\r]+/gi, ' ')) : '';
    });

    self.comment.subscribe(function (newValue) {
      self.catalogEntry.getComment().done(function (comment) {
        if (comment !== newValue) {
          self.catalogEntry.setComment(newValue).done(self.comment).fail(function () {
            self.comment(comment);
          })
        }
      });
    });

    self.refreshTableStats = function () {
      if (self.refreshingTableStats()) {
        return;
      }
      self.refreshingTableStats(true);
      self.catalogEntry.getAnalysis({ refreshAnalysis: true, silenceErrors: true }).done(function () {
        self.fetchDetails();
      }).fail(function () {
        self.refreshingTableStats(false);
        $.jHueNotify.error(window.I18n('An error occurred refreshing the table stats. Please try again.'));
        console.error('apiHelper.refreshTableStats error');
        console.error(data);
      });
    };

    self.fetchFields = function () {
      self.loadingColumns(true);
      self.catalogEntry.getChildren().done(function (columnEntries) {
        self.columns($.map(columnEntries, function (columnEntry) {
          return new MetastoreColumn({
            catalogEntry: columnEntry,
            table: self
          })
        }));

        self.catalogEntry.getNavOptMeta().done(function (navOptMeta) {
          self.optimizerDetails(navOptMeta);

          var topColIndex = {};
          navOptMeta.topCols.forEach(function (topCol) {
            topColIndex[topCol.name] = topCol;
          });

          self.columns().forEach(function (column) {
            if (topColIndex[column.catalogEntry.name]) {
              column.popularity(topColIndex[column.catalogEntry.name].score);
            }
          });
        }).always(function () {
          self.loadingQueries(false);
        });
      }).fail(function () {
        self.columns([]);
      }).always(function () {
        self.loadingColumns(false);
      });
    };

    self.fetchDetails = function () {
      self.loadingComment(true);
      self.database.catalogEntry.loadNavigatorMetaForChildren().done(function () {
        self.catalogEntry.getComment().done(self.comment);
      }).always(function () {
        self.loadingComment(false);
      });

      if (self.catalogEntry.isView()) {
        self.loadingViewSql(true);
      }

      self.catalogEntry.getTopJoins({ silenceErrors: true }).done(function (topJoins) {
        if (topJoins && topJoins.values) {
          var joins = [];
          var ownQidLower = self.catalogEntry.path.join('.').toLowerCase();
          var ownNameLower = self.catalogEntry.name.toLowerCase();
          var ownDbNameLower = self.database.catalogEntry.name.toLowerCase();

          var joinIndex = {};
          var joinColsIndex = {};
          topJoins.values.forEach(function (topJoin) {
            if (topJoin.tables.length === 2) {
              topJoin.tables.forEach(function (table) {
                var tableLower = table.toLowerCase();
                if (tableLower !== ownQidLower && tableLower !== ownNameLower) {
                  var name = tableLower.indexOf(ownDbNameLower + '.') === 0 ? table.substring(ownDbNameLower.length + 1) : table;
                  if (!joinIndex[name]) {
                    joinIndex[name] = {
                      tableName: name,
                      tablePath: table.split('.'),
                      joinCols: [],
                      queryCount: 0
                    }
                  }
                  var join = joinIndex[name];
                  join.queryCount += topJoin.totalQueryCount;

                  topJoin.joinCols.forEach(function (joinCol) {
                    var cleanCols = {
                      queryCount: topJoin.totalQueryCount
                    };
                    if (joinCol.columns.length === 2) {
                      joinCol.columns.forEach(function (col) {
                        var colLower = col.toLowerCase();
                        if (colLower.indexOf(ownQidLower + '.') === 0) {
                          cleanCols.source = colLower.substring(ownDbNameLower.length + 1);
                          cleanCols.sourcePath = col.split('.');
                        } else if (colLower.indexOf(ownNameLower + '.') === 0) {
                          cleanCols.source = colLower;
                          cleanCols.sourcePath = col.split('.');
                          cleanCols.sourcePath.unshift(ownDbNameLower);
                        } else if (colLower.indexOf(ownDbNameLower + '.') === 0) {
                          cleanCols.target = colLower.substring(ownDbNameLower.length + 1);
                          cleanCols.targetPath = col.split('.');
                        } else {
                          cleanCols.target = col;
                          cleanCols.targetPath = col.split('.');
                        }
                      })
                    }
                    if (cleanCols.source && cleanCols.target) {
                      if (joinColsIndex[ownQidLower + join.tableName + cleanCols.source + cleanCols.target]) {
                        joinColsIndex[ownQidLower + join.tableName + cleanCols.source + cleanCols.target].queryCount += topJoin.totalQueryCount;
                      } else {
                        joinColsIndex[ownQidLower + join.tableName + cleanCols.source + cleanCols.target] = cleanCols;
                        join.joinCols.push(cleanCols);
                      }
                    }
                  })
                }
              });
            }
          });

          Object.keys(joinIndex).forEach(function (key) {
            var join = joinIndex[key];
            if (join.joinCols.length) {
              join.joinCols.sort(function (a, b) {
                return b.queryCount - a.queryCount;
              });
              joins.push(join);
            }
          });
          joins.sort(function (a, b) {
            return b.queryCount - a.queryCount;
          });
          self.topJoins(joins);
        }
      }).always(function () {
        self.loadingTopJoins(false);
      });

      self.loadingDetails(true);
      self.catalogEntry.getAnalysis().done(function (analysis) {
        self.tableDetails(analysis);
        self.tableStats(analysis.details.stats);
        self.loaded(true);
        if (analysis.partition_keys.length) {
          self.partitions.detailedKeys(analysis.partition_keys);
          self.partitions.load();
        } else {
          self.partitions.loading(false);
          self.partitions.loaded(true);
        }

        var found = analysis.properties && analysis.properties.some(function (property) {
          if (property.col_name.toLowerCase() === 'view original text:') {
            window.apiHelper.formatSql({ statements: property.data_type }).done(function (formatResponse) {
              self.viewSql(formatResponse.status === 0 ? formatResponse.formatted_statements : property.data_type)
            }).fail(function () {
              self.viewSql(property.data_type)
            }).always(function () {
              self.loadingViewSql(false);
            });
            return true;
          }
        });
        if (!found) {
          self.loadingViewSql(false);
        }
      }).fail(function () {
        self.partitions.loading(false);
        self.partitions.loaded(true);
        self.loadingViewSql(false);
      }).always(function () {
        self.refreshingTableStats(false);
        self.loadingDetails(false)
      });

      self.samples.load();
    };

    self.drop = function () {
      $.post('/tables/drop/' + self.database.catalogEntry.name, {
        table_selection: ko.mapping.toJSON([self.name]),
        skip_trash: 'off',
        is_embeddable: true,
        cluster: JSON.stringify(self.database.catalogEntry.compute)
      }, function(resp) {
        if (resp.history_uuid) {
          huePubSub.publish('notebook.task.submitted', resp.history_uuid);
        } else {
          $(document).trigger("error", data.message);
        }
      });
    };

    self.getRelationships = function () {
      $.post('/metadata/api/navigator/lineage', {
        id: self.navigatorMeta().identity
      }, function(data) {
        if (data && data.status === 0) {
          self.relationshipsDetails(ko.mapping.fromJS(data));
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr) {
        $(document).trigger("info", xhr.responseText);
      });
    };
  }

  MetastoreTable.prototype.reload = function () {
    var self = this;
    self.samples.loaded(false);
    self.partitions.loaded(false);
    // Clear will publish when done
    self.catalogEntry.clearCache({ invalidate: self.catalogEntry.getSourceType() === 'impala' ? 'invalidate' : 'cache' });
  };

  MetastoreTable.prototype.showImportData = function () {
    var self = this;
    $("#import-data-modal").empty().html('<div class="modal-header"><button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span></button><h2 class="modal-title"></h2></div><div class="modal-body"><i class="fa fa-spinner fa-spin fa-2x muted"></i></div>').modal("show");
    $.get('/metastore/table/' + self.catalogEntry.path.join('/') + '/load?source_type=' + self.catalogEntry.getSourceType(), function (data) {
      $("#import-data-modal").html(data['data']);
    }).fail(function (xhr) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  MetastoreTable.prototype.load = function () {
    var self = this;
    self.fetchFields();
    self.fetchDetails();
    huePubSub.publish('metastore.loaded.table');
  };


  var contextPopoverTimeout = -1;

  MetastoreTable.prototype.showContextPopover = function (entry, event, orientation) {
    window.clearTimeout(contextPopoverTimeout);
    var $source = $(event.currentTarget || event.target);
    var offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: entry.catalogEntry
      },
      orientation: orientation || 'right',
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 2,
        right: offset.left + (orientation === 'left' ? 0 : $source.width() + 1),
        bottom: offset.top + $source.height() - 2
      }
    });
  };

  MetastoreTable.prototype.showContextPopoverDelayed = function (entry, event, orientation) {
    var self = this;
    window.clearTimeout(contextPopoverTimeout);
    contextPopoverTimeout = window.setTimeout(function () {
      self.showContextPopover(entry, event, orientation);
    }, 500);
  };

  MetastoreTable.prototype.clearContextPopoverDelay = function () {
    window.clearInterval(contextPopoverTimeout);
  };

  return MetastoreTable;

})();

var MetastoreColumn = (function () {

  /**
   * @param {Object} options
   * @param {MetastoreTable} options.table
   * @param {DataCatalogEntry} options.catalogEntry
   * @constructor
   */
  function MetastoreColumn(options) {
    var self = this;
    self.table = options.table;
    self.catalogEntry = options.catalogEntry;

    self.favourite = ko.observable(false);
    self.popularity = ko.observable();
    self.comment = ko.observable();

    self.comment.subscribe(function (newValue) {
      self.catalogEntry.getComment().done(function (comment) {
        if (comment !== newValue) {
          self.catalogEntry.setComment(newValue).done(self.comment).fail(function () {
            self.comment(comment);
          })
        }
      });
    });

    self.table.catalogEntry.loadNavigatorMetaForChildren().done(function () {
      self.catalogEntry.getComment().done(self.comment);
    });
  }

  MetastoreColumn.prototype.showContextPopover = function (entry, event) {
    var $source = $(event.target);
    var offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: entry.catalogEntry
      },
      orientation: 'right',
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 2,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 2
      }
    });
  };

  return MetastoreColumn;
})();
