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

var MetastoreDatabase = (function () {
  /**
   * @param {Object} options
   * @param {string} options.name
   * @param {string} [options.tableName]
   * @param {string} [options.tableComment]
   * @constructor
   */
  function MetastoreDatabase(options) {
    var self = this;
    self.apiHelper = ApiHelper.getInstance();
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

  MetastoreDatabase.prototype.load = function (callback, optimizerEnabled, navigatorEnabled) {
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
            optimizerEnabled: optimizerEnabled,
            navigatorEnabled: navigatorEnabled
          })
        }));
        self.loaded(true);
        self.loading(false);
        if (optimizerEnabled && navigatorEnabled) {
          $.get('/metadata/api/navigator/find_entity', {
            type: 'database',
            name: self.name
          }, function(data){
            if (data && data.status == 0) {
              self.navigatorStats(ko.mapping.fromJS(data.entity));
            } else {
              //$(document).trigger("info", data.message);
            }
          }).fail(function (xhr, textStatus, errorThrown) {
            $(document).trigger("error", xhr.responseText);
          });

          $.post('/metadata/api/optimizer/top_tables', {
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


    self.apiHelper.setInTotalStorage('metastore', 'last.selected.database', self.name);
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
    self.metastoreTable = options.metastoreTable;
    self.apiHelper = ApiHelper.getInstance();

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
   * @param {MetastoreTable} options.metastoreTable
   */
  function MetastoreTableSamples(options) {
    var self = this;
    self.rows = ko.observableArray();
    self.headers = ko.observableArray();
    self.metastoreTable = options.metastoreTable;
    self.apiHelper = ApiHelper.getInstance();

    self.hasErrors = ko.observable(false);
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
    self.hasErrors(false);
    self.apiHelper.fetchTableSample({
      sourceType: "hive",
      databaseName: self.metastoreTable.database.name,
      tableName: self.metastoreTable.name,
      silenceErrors: true,
      successCallback: function (data) {
        self.rows(data.rows);
        self.headers(data.headers);
        self.preview.rows(self.rows().slice(0, 3));
        self.preview.headers(self.headers());
        self.loading(false);
        self.loaded(true);
      },
      errorCallback: function (data) {
        self.hasErrors(true);
        self.loading(false);
        self.loaded(true);
      }
    });
  };

  /**
   * @param {Object} options
   * @param {MetastoreDatabase} options.database
   * @param {string} options.name
   * @param {string} options.type
   * @param {string} options.comment
   * @constructor
   */
  function MetastoreTable(options) {
    var self = this;
    self.database = options.database;
    self.apiHelper = ApiHelper.getInstance();
    self.optimizerEnabled = options.optimizerEnabled;
    self.navigatorEnabled = options.navigatorEnabled;
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
            || (column.type() && column.type().toLowerCase().indexOf(self.columnQuery()) > -1)
            || (column.comment() && column.comment().toLowerCase().indexOf(self.columnQuery()) > -1);
        });
      }
      return returned;
    });

    self.favouriteColumns = ko.observableArray();
    self.samples = new MetastoreTableSamples({
      metastoreTable: self
    });
    self.partitions = new MetastoreTablePartitions({
      metastoreTable: self
    });

    self.partitionsCountLabel = ko.pureComputed(function () {
      if (self.partitions.values().length === MetastoreGlobals.partitionsLimit) {
        return self.partitions.values().length + '+'
      }
      return self.partitions.values().length;
    });
    self.tableDetails = ko.observable();
    self.tableStats = ko.observable();
    self.refreshingTableStats = ko.observable(false);
    self.showAddTagName = ko.observable(false);
    self.addTagName = ko.observable('');
    self.loadingQueries = ko.observable(true);

    //TODO: Fetch table comment async and don't set it from python
    self.comment = ko.observable(options.comment);
    self.commentWithoutNewLines = ko.pureComputed(function(){
      return self.comment() ? self.comment().replace(/<br\s*[\/]?>/gi, ' ').replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') : '';
    });

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
          $.jHueNotify.error(MetastoreGlobals.i18n.errorRefreshingTableStats);
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
            if (self.navigatorEnabled) {
              $.get('/metadata/api/navigator/find_entity', {
                type: 'table',
                database: self.database.name,
                name: self.name
              }, function(data) {
                if (data && data.status == 0) {
                  self.navigatorStats(ko.mapping.fromJS(data.entity));
                  self.getRelationships();
                } else {
                  //$(document).trigger("info", data.message);
                }
              }).fail(function (xhr, textStatus, errorThrown) {
                $(document).trigger("error", xhr.responseText);
              });
            }
            if (self.optimizerEnabled) {
              $.post('/metadata/api/optimizer/table_details', {
                databaseName: self.database.name,
                tableName: self.name
              }, function(data){
                self.loadingQueries(false);
                if (data && data.status == 0) {
                  self.optimizerDetails(ko.mapping.fromJS(data.details));

                  // Bump the most important columns first
                  var topCols = $.map(self.optimizerDetails().topCols().slice(0, 5), function(item) { return item.name(); });
                  if (topCols.length >= 3 && self.favouriteColumns().length > 0) {
                    self.favouriteColumns($.grep(self.columns(), function(col) {
                        return topCols.indexOf(col.name()) != -1;
                      })
                    );
                  }

                  // Column popularity, stats
                  $.each(self.optimizerDetails().topCols(), function(index, optimizerCol) {
                    var metastoreCol = $.grep(self.columns(), function(col) {
                      return col.name() == optimizerCol.name();
                    });
                    if (metastoreCol.length > 0) {
                      metastoreCol[0].popularity(optimizerCol.score())
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
    };

    self.drop = function () {
      $.post('/tables/drop/' + self.database.name, {
        table_selection: ko.mapping.toJSON([self.name]),
        skip_trash: 'off',
        is_embeddable: true
      }, function(resp) {
        if (resp.history_uuid) {
          huePubSub.publish('notebook.task.submitted', resp.history_uuid);
        } else {
          $(document).trigger("error", data.message);
        }
      });
    };

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
    $("#import-data-modal").empty().html('<div class="modal-header"><button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span></button><h2 class="modal-title"></h2></div><div class="modal-body"><i class="fa fa-spinner fa-spin fa-2x muted"></i></div>').modal("show");
    $.get('/metastore/table/' + self.database.name + '/' + self.name + '/load', function (data) {
      $("#import-data-modal").html(data['data']);
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

  MetastoreTable.prototype.showContextPopover = function (entry, event, orientation) {
    var $source = $(event.target);
    var offset = $source.offset();
    huePubSub.publish('sql.context.popover.show', {
      data: {
        type: 'table',
        identifierChain: [{ name: entry.name }]
      },
      orientation: orientation || 'right',
      sourceType: 'hive',
      defaultDatabase: entry.database.name,
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 2,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 2
      }
    });
  };

  return MetastoreTable;

})();

var MetastoreColumn = (function () {

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

  MetastoreColumn.prototype.showContextPopover = function (entry, event) {
    var $source = $(event.target);
    var offset = $source.offset();
    huePubSub.publish('sql.context.popover.show', {
      data: {
        type: 'column',
        identifierChain: [{ name: entry.table.name }, { name: entry.name() }]
      },
      orientation: 'right',
      sourceType: 'hive',
      defaultDatabase: entry.table.database.name,
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
