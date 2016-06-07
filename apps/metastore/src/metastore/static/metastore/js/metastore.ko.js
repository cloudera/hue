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
    define([
      'knockout',
      'desktop/js/apiHelper'
    ], factory);
  } else {
    root.EditorViewModel = factory(ko, apiHelper);
  }
}(this, function (ko, ApiHelper) {

  /**
   * @param {Object} options
   * @param {string} options.name
   * @param {ApiHelper} options.apiHelper
   * @param {string} [options.tableName]
   * @param {string} [options.tableComment]
   * @param {Object} options.i18n
   * @param {string} options.i18n.errorFetchingTableDetails
   * @param {string} options.i18n.errorFetchingTableFields
   * @param {string} options.i18n.errorFetchingTableSample
   * @param {string} options.i18n.errorRefreshingTableStats
   * @constructor
   */
  function MetastoreDatabase(options) {
    var self = this;
    self.apiHelper = options.apiHelper;
    self.i18n = options.i18n;
    self.name = options.name;

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.tables = ko.observableArray();
    self.stats = ko.observable();
    self.optimizerStats = ko.observableArray(); // TODO to plugify, duplicates similar MetastoreTable
    self.navigatorStats = ko.observable();

    self.showAddTagName = ko.observable(false);
    self.addTagName = ko.observable('');

    self.tableQuery = ko.observable('').extend({rateLimit: 150});

    self.filteredTables = ko.computed(function () {
      var returned = self.tables();
      if (self.tableQuery() !== '') {
        returned = $.grep(self.tables(), function (table) {
          return table.name.toLowerCase().indexOf(self.tableQuery()) > -1
            || (table.comment() && table.comment().toLowerCase().indexOf(self.tableQuery()) > -1);
        });
      }
      return returned.sort(function (a, b) {
    	if (options.optimizerEnabled()) {
          if (typeof a.optimizerStats() !== 'undefined' && a.optimizerStats() !== null) {
            if (typeof b.optimizerStats() !== 'undefined' && b.optimizerStats() !== null) {
              if (a.optimizerStats().popularity === b.optimizerStats().popularity) {
                return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
              }
              return  b.optimizerStats().popularity - a.optimizerStats().popularity;
            }
            return -1
          }
          if (typeof b.optimizerStats() !== 'undefined' && b.optimizerStats() !== null) {
            return 1;
          }
        }

        return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
      });
    });

    self.selectedTables = ko.observableArray();

    self.editingTable = ko.observable(false);
    self.table = ko.observable(null);
    
    self.addTags = function () {
      $.post('/metadata/api/navigator/add_tags', {
        id: ko.mapping.toJSON(self.navigatorStats().identity),
        tags: ko.mapping.toJSON([self.addTagName()])
      }, function(data) {
        if (data && data.status == 0) {
          self.navigatorStats().tags.push(self.addTagName());
          self.addTagName('');
          self.showAddTagName(false);
        } else {
          $(document).trigger("error", data.message);
        }
      });
    };
      
    self.deleteTags = function (tag) {
      $.post('/metadata/api/navigator/delete_tags', {
        id: ko.mapping.toJSON(self.navigatorStats().identity),
        tags: ko.mapping.toJSON([tag])
      }, function(data) {
        if (data && data.status == 0) {
          self.navigatorStats().tags.remove(tag);
        } else {
          $(document).trigger("error", data.message);
        }
      });
    };
  }

  MetastoreDatabase.prototype.load = function (callback, optimizerEnabled) {
    var self = this;
    if (self.loading()) {
      return;
    }

    self.loading(true);
    self.apiHelper.fetchTables({
      sourceType: 'hive',
      databaseName: self.name,
      successCallback: function (data) {
        self.tables($.map(data.tables_meta, function (tableMeta) {
          return new MetastoreTable({
            database: self,
            name: tableMeta.name,
            type: tableMeta.type,
            comment: tableMeta.comment,
            apiHelper: self.apiHelper,
            i18n: self.i18n,
            optimizerEnabled: optimizerEnabled
          })
        }));
        self.loaded(true);
        self.loading(false);
        if (optimizerEnabled) {
          $.get('/metadata/api/navigator/find_entity', {
            type: 'database',
            name: self.name
          }, function(data){
            if (data && data.status == 0) {
              self.navigatorStats(ko.mapping.fromJS(data.entity));
            } else {
              $(document).trigger("info", data.message);
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          });

          $.post('/metadata/api/optimizer_api/top_tables', {
            database: self.name
          }, function(data){
            if (data && data.status == 0) {
              var tableIndex = {};
              data.top_tables.forEach(function (topTable) {
                tableIndex[topTable.name] = topTable;
              });
              self.tables().forEach(function (table) {
                table.optimizerStats(tableIndex[table.name]);
              });
              self.optimizerStats(data.top_tables);
            } else {
              $(document).trigger("error", data.message);
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          }).always(function () {
            if (callback) {
              callback();
            }
          });
        } else if (callback) {
          callback();
        }
      },
      errorCallback: function (response) {
        self.loading(false);
        if (callback) {
          callback();
        }
      }
    });

    $.getJSON('/metastore/databases/' + self.name + '/metadata', function (data) {
      if (data && data.status == 0) {
        self.stats(data.data);
      }
    });


    $.totalStorage('hue.metastore.lastdb', self.name);
  };

  MetastoreDatabase.prototype.setTableByName = function (tableName) {
    var self = this;
    var foundTables = $.grep(self.tables(), function (metastoreTable) {
      return metastoreTable.name === tableName;
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
    window.setTimeout(function () {
      $('a[href="#overview"]').click();
    }, 200);
  };

  /**
   * @param {Object} options
   * @param {ApiHelper} options.apiHelper
   * @param {MetastoreTable} options.metastoreTable
   */
  function MetastoreTablePartitions(options) {
    var self = this;
    self.detailedKeys = ko.observableArray();
    self.keys = ko.observableArray();
    self.values = ko.observableArray();
    self.metastoreTable = options.metastoreTable;
    self.apiHelper = options.apiHelper;

    self.loaded = ko.observable(false);
    self.loading = ko.observable(true);

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
    self.apiHelper.fetchPartitions({
      databaseName: self.metastoreTable.database.name,
      tableName: self.metastoreTable.name,
      successCallback: function (data) {
        self.keys(data.partition_keys_json);
        self.values(data.partition_values_json);
        self.preview.values(self.values().slice(0, 5));
        self.preview.keys(self.keys());
        self.loading(false);
        self.loaded(true);
      },
      errorCallback: function (data) {
        self.loading(false);
        self.loaded(true);
      }
    })
  };

  /**
   * @param {Object} options
   * @param {ApiHelper} options.apiHelper
   * @param {MetastoreTable} options.metastoreTable
   * @param {Object} options.i18n
   * @param {string} options.i18n.errorFetchingTableSample
   */
  function MetastoreTableSamples(options) {
    var self = this;
    self.rows = ko.observableArray();
    self.headers = ko.observableArray();
    self.metastoreTable = options.metastoreTable;
    self.apiHelper = options.apiHelper;
    self.i18n = options.i18n;

    self.loaded = ko.observable(false);
    self.loading = ko.observable(true);

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
    self.apiHelper.fetchTableSample({
      sourceType: "hive",
      databaseName: self.metastoreTable.database.name,
      tableName: self.metastoreTable.name,
      successCallback: function (data) {
        self.rows(data.rows);
        self.headers(data.headers);
        self.preview.rows(self.rows().slice(0, 3));
        self.preview.headers(self.headers());
        self.loading(false);
        self.loaded(true);
      },
      errorCallback: function (data) {
        self.loading(false);
        self.loaded(true);
      }
    });
  };

  function MetastoreTableDetails(details) {
	var self = this;
  }
  
  /**
   * @param {Object} options
   * @param {MetastoreDatabase} options.database
   * @param {string} options.name
   * @param {string} options.type
   * @param {string} options.comment
   * @param {ApiHelper} options.apiHelper
   * @param {Object} options.i18n
   * @param {string} options.i18n.errorFetchingTableDetails
   * @param {string} options.i18n.errorFetchingTableFields
   * @param {string} options.i18n.errorFetchingTableSample
   * @param {string} options.i18n.errorRefreshingTableStats
   * @constructor
   */
  function MetastoreTable(options) {
    var self = this;
    self.database = options.database;
    self.apiHelper = options.apiHelper;
    self.i18n = options.i18n;
    self.optimizerEnabled = options.optimizerEnabled;
    self.name = options.name;
    self.type = options.type;

    self.optimizerStats = ko.observable();
    self.optimizerDetails = ko.observable();

    self.navigatorStats = ko.observable();
    self.relationshipsDetails = ko.observable();

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);

    self.loadingDetails = ko.observable(false);
    self.loadingColumns = ko.observable(false);
    self.columnQuery = ko.observable('').extend({rateLimit: 150});
    self.columns = ko.observableArray();
    self.filteredColumns = ko.computed(function () {
      var returned = self.columns();
      if (self.columnQuery() !== '') {
        returned = $.grep(self.columns(), function (column) {
          return column.name().toLowerCase().indexOf(self.columnQuery()) > -1
            || (column.comment() && column.comment().toLowerCase().indexOf(self.columnQuery()) > -1);
        });
      }
      return returned.sort(function (a, b) {
        return a.name().toLowerCase().localeCompare(b.name().toLowerCase());
      });
    });

    self.favouriteColumns = ko.observableArray();
    self.samples = new MetastoreTableSamples({
      apiHelper: self.apiHelper,
      i18n: self.i18n,
      metastoreTable: self
    });
    self.partitions = new MetastoreTablePartitions({
      apiHelper: self.apiHelper,
      metastoreTable: self
    });
    self.tableDetails = ko.observable();
    self.tableStats = ko.observable();
    self.refreshingTableStats = ko.observable(false);
    self.showAddTagName = ko.observable(false);
    self.addTagName = ko.observable('');
    self.loadingQueries = ko.observable(true);

    //TODO: Fetch table comment async and don't set it from python
    self.comment = ko.observable(options.comment);

    self.comment.subscribe(function (newValue) {
      $.post('/metastore/table/' + self.database.name + '/' + self.name + '/alter', {
        comment: newValue ? newValue : ""
      }, function () {
        huePubSub.publish('assist.clear.db.cache', {
          sourceType: 'hive',
          databaseName: self.database.name
        })
      });
    });

    self.refreshTableStats = function () {
      if (self.refreshingTableStats()) {
        return;
      }
      self.refreshingTableStats(true);
      self.apiHelper.refreshTableStats({
        tableName: self.name,
        databaseName: self.database.name,
        sourceType: "hive",
        successCallback: function (data) {
          self.fetchDetails();
        },
        errorCallback: function (data) {
          self.refreshingTableStats(false);
          $.jHueNotify.error(self.i18n.errorRefreshingTableStats);
          console.error('apiHelper.refreshTableStats error');
          console.error(data);
        }
      })
    };

    self.fetchFields = function () {
      var self = this;
      self.loadingColumns(true);
      self.apiHelper.fetchFields({
        sourceType: "hive",
        databaseName: self.database.name,
        tableName: self.name,
        fields: [],
        successCallback: function (data) {
          self.loadingColumns(false);
          self.columns($.map(data.extended_columns, function (column) {
            return new MetastoreColumn({
              extendedColumn: column,
              table: self
            })
          }));
          self.favouriteColumns(self.columns().slice(0, 5));
        },
        errorCallback: function () {
          self.loadingColumns(false);
        }
      })
    };

    self.fetchDetails = function () {
      var self = this;
      self.loadingDetails(true);
      self.apiHelper.fetchTableDetails({
        sourceType: "hive",
        databaseName: self.database.name,
        tableName: self.name,
        successCallback: function (data) {
          self.loadingDetails(false);
          if ((typeof data === 'object') && (data !== null)) {
            self.tableDetails(data);
            self.tableStats(data.details.stats);
            self.refreshingTableStats(false);
            self.samples.load();
            self.loaded(true);
            self.loading(false);
            if (data.partition_keys.length) {
              self.partitions.detailedKeys(data.partition_keys);
              self.partitions.load();
            } else {
              self.partitions.loading(false);
              self.partitions.loaded(true);
            }
            if (self.optimizerEnabled) {
              $.get('/metadata/api/navigator/find_entity', {
                type: 'table',
                database: self.database.name,
                name: self.name
              }, function(data) {
                if (data && data.status == 0) {
                  self.navigatorStats(ko.mapping.fromJS(data.entity));
                  self.getRelationships();
                } else {
                  $(document).trigger("info", data.message);
                }
              }).fail(function (xhr, textStatus, errorThrown) {
                $(document).trigger("error", xhr.responseText);
              });

              $.post('/metadata/api/optimizer_api/table_details', {
                tableName: self.name
              }, function(data){
                self.loadingQueries(false);
                if (data && data.status == 0) {
                  self.optimizerDetails(ko.mapping.fromJS(data.details));
                  
                  // Bump the most important columns first
                  var topCol = self.optimizerDetails().table_donut.topColumns().slice(0, 5);
                  if (topCol.length >= 3 && self.favouriteColumns().length > 0) { 
                    self.favouriteColumns($.grep(self.columns(), function(col) {
                        return topCol.indexOf(col.name()) != -1;
                      })
                    );
                  }
                  // Column popularity, stats
                  $.each(self.optimizerDetails().sortedTotal(), function(index, optimizerCol) {
                    var metastoreCol = $.grep(self.columns(), function(col) {
                      return col.name() == optimizerCol.columnName();
                    })
                    if (metastoreCol.length > 0) {
                      metastoreCol[0].popularity(optimizerCol.totalCount())
                    }
                  });
                } else {
                  $(document).trigger("info", data.message);
                }
              }).fail(function (xhr, textStatus, errorThrown) {
                $(document).trigger("error", xhr.responseText);
              });
            }
          }
          else {
            self.refreshingTableStats(false);
            self.loading(false);
          }
        },
        errorCallback: function (data) {
          self.refreshingTableStats(false);
          self.loadingDetails(false);
          self.loading(false);
        }
      })
    }

    self.addTags = function () {
      $.post('/metadata/api/navigator/add_tags', {
        id: ko.mapping.toJSON(self.navigatorStats().identity),
        tags: ko.mapping.toJSON([self.addTagName()])
      }, function(data) {
        if (data && data.status == 0) {
          self.navigatorStats().tags.push(self.addTagName());
          self.addTagName('');
          self.showAddTagName(false);
        } else {
          $(document).trigger("error", data.message);
        }
      });
    };
    
    self.deleteTags = function (tag) {console.log(tag);
      $.post('/metadata/api/navigator/delete_tags', {
        id: ko.mapping.toJSON(self.navigatorStats().identity),
        tags: ko.mapping.toJSON([tag])
      }, function(data) {
        if (data && data.status == 0) {
          self.navigatorStats().tags.remove(tag);
        } else {
          $(document).trigger("error", data.message);
        }
      });
    };
    
    self.getRelationships = function () {
      $.post('/metadata/api/navigator/lineage', {
        id: self.navigatorStats().identity
      }, function(data) {
        if (data && data.status == 0) {
          self.relationshipsDetails(ko.mapping.fromJS(data));
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("info", xhr.responseText);
      });
    };
  }

  MetastoreTable.prototype.showImportData = function () {
    var self = this;
    $.get('/metastore/table/' + self.database.name + '/' + self.name + '/load', function (data) {
      $("#import-data-modal").html(data['data']);
      $("#import-data-modal").modal("show");
    }).fail(function (xhr, textStatus, errorThrown) {
      $(document).trigger("error", xhr.responseText);
    });
  };

  MetastoreTable.prototype.load = function () {
    var self = this;
    if (self.loading()) {
      return;
    }
    self.loading(true);
    self.fetchFields();
    self.fetchDetails();
  };

  /**
   * @param {Object} options
   * @param {MetastoreTable} options.table
   * @param {object} options.extendedColumn
   * @constructor
   */
  function MetastoreColumn(options) {
    var self = this;
    self.table = options.table;
    ko.mapping.fromJS(options.extendedColumn, {}, self);

    self.favourite = ko.observable(false);
    self.popularity = ko.observable();

    self.comment.subscribe(function (newValue) {
      $.post('/metastore/table/' + self.table.database.name + '/' + self.table.name + '/alter_column', {
        column: self.name(),
        comment: newValue
      }, function (data) {
        if (data.status == 0) {
          huePubSub.publish('assist.clear.db.cache', {
            sourceType: 'hive',
            databaseName: self.table.database.name,
            tableName: self.table.name
          });
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr, textStatus, errorThrown) {
        $(document).trigger("error", xhr.responseText);
      });
    })
  }

  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {string} options.i18n.errorFetchingTableDetails
   * @param {string} options.i18n.errorFetchingTableFields
   * @param {string} options.i18n.errorFetchingTableSample
   * @param {string} options.i18n.errorLoadingDatabases
   * @param {string} options.i18n.errorLoadingTablePreview
   * @param {string} options.i18n.errorRefreshingTableStats
   * @param {string} options.user
   * @constructor
   */
  function MetastoreViewModel(options) {
    var self = this;
    self.assistAvailable = ko.observable(true);
    self.apiHelper = ApiHelper.getInstance(options);
    self.isLeftPanelVisible = ko.observable();
    self.apiHelper.withTotalStorage('assist', 'assist_panel_visible', self.isLeftPanelVisible, true);
    self.optimizerEnabled = ko.observable(options.optimizerEnabled || false);

    self.optimizerEnabled.subscribe(function (newValue) {
      huePubSub.publish('meta.optimizer.enabled', newValue);
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

    self.databaseQuery = ko.observable('').extend({rateLimit: 150});

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

    var loadDatabases = function (successCallback) {
      if (self.loading()) {
        return;
      }
      self.loading(true);
      self.apiHelper.loadDatabases({
        sourceType: 'hive',
        successCallback: function (databaseNames) {
          self.databases($.map(databaseNames, function (name) {
            return new MetastoreDatabase({
              name: name,
              apiHelper: self.apiHelper,
              i18n: self.i18n,
              optimizerEnabled: self.optimizerEnabled
            })
          }));
          self.loading(false);
          if (successCallback) {
            successCallback();
          }
        },
        errorCallback: function () {
          self.databases([]);
        }
      });
    };

    loadDatabases();

    var setDatabaseByName = function (databaseName, callback) {
      if (databaseName === '') {
        databaseName = $.totalStorage('hue.metastore.lastdb') || 'default';
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
      }
    };

    var loadTableDef = function (tableDef, callback) {
      setDatabaseByName(tableDef.database);
      if (self.database()) {
        if (self.database().table() && self.database().table().name == tableDef.name) {
          return;
        }
        var setTableAfterLoad = function () {
          var foundTables = $.grep(self.database().tables(), function (table) {
            return table.name === tableDef.name;
          });
          if (foundTables.length === 1) {
            self.database().setTable(foundTables[0], callback);
          }
          else {
            huePubSub.publish('assist.clear.db.cache', {
              sourceType: 'hive',
              clearAll: false,
              databaseName: self.database().name
            });
            self.database().load(setTableAfterLoad, self.optimizerEnabled());
          }
        };

        if (!self.database().loaded()) {
          var doOnce = self.database().loaded.subscribe(function () {
            setTableAfterLoad();
            doOnce.dispose();
          });
        } else {
          setTableAfterLoad();
        }
      }
    };

    huePubSub.subscribe('assist.db.refresh', function (type) {
      if (type !== 'hive') {
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
      loadDatabases(function () {
        if (currentDatabase) {
          setDatabaseByName(currentDatabase, function () {
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
      loadTableDef(tableDef, function () {
        huePubSub.publish('metastore.url.change')
      });
    });

    huePubSub.subscribe("assist.database.selected", function (databaseDef) {
      if (self.database()) {
        self.database().table(null);
      }
      setDatabaseByName(databaseDef.name, function () {
        huePubSub.publish('metastore.url.change')
      });
    });

    huePubSub.subscribe('metastore.url.change', function () {
      if (self.database() && self.database().table()) {
        hueUtils.changeURL('/metastore/table/' + self.database().name + '/' + self.database().table().name);
      }
      else if (self.database()) {
        hueUtils.changeURL('/metastore/tables/' + self.database().name);
      }
      else {
        hueUtils.changeURL('/metastore/databases');
      }
    });

    function loadURL() {
      var path = window.location.pathname.split('/');
      switch (path[2]) {
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
          setDatabaseByName(path[3]);
          break;
        case 'table':
          window.setTimeout(function() {
            loadTableDef({
              name: path[4],
              database: path[3]
            });
          }, 200);
          break;
      }
    }

    loadURL();

    window.onpopstate = loadURL;

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

  MetastoreViewModel.prototype.setDatabase = function (metastoreDatabase, callback) {
    var self = this;
    huePubSub.publish('metastore.scroll.to.top');
    self.database(metastoreDatabase);

    if (!metastoreDatabase.loaded()) {
      metastoreDatabase.load(callback, self.optimizerEnabled());
    } else if (callback) {
      callback();
    }
  };

  return MetastoreViewModel;
}));
