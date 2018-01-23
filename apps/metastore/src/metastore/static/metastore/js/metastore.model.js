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
   * @param {object} options
   * @param {DataCatalogEntry} options.catalogEntry
   * @param {observable} options.optimizerEnabled
   * @constructor
   */
  function MetastoreDatabase(options) {
    var self = this;
    self.apiHelper = ApiHelper.getInstance();
    self.catalogEntry = options.catalogEntry;

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.tables = ko.observableArray();

    self.comment = ko.observable();

    self.stats = ko.observable(); // TODO: add to DataCatalogEntry
    self.navigatorMeta = ko.observable();

    self.showAddTagName = ko.observable(false);
    self.addTagName = ko.observable('');
    self.tableQuery = ko.observable('').extend({rateLimit: 150});

    self.filteredTables = ko.computed(function () {
      var returned = self.tables();
      if (self.tableQuery() !== '') {
        returned = self.tables().filter(function (table) {
          return table.catalogEntry.name.toLowerCase().indexOf(self.tableQuery()) > -1
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

        return a.catalogEntry.name.toLowerCase().localeCompare(b.catalogEntry.name.toLowerCase());
      });
    });

    self.selectedTables = ko.observableArray();

    self.editingTable = ko.observable(false);
    self.table = ko.observable(null);
  }

  MetastoreDatabase.prototype.load = function (callback, optimizerEnabled, navigatorEnabled) {
    var self = this;
    if (self.loading()) {
      return;
    }

    self.loading(true);

    if (navigatorEnabled) {
      self.catalogEntry.getNavigatorMeta().done(self.navigatorMeta);
    }

    self.catalogEntry.getComment().done(self.comment);

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
        self.catalogEntry.loadNavigatorMetaForChildren().done(function () {
          self.tables().forEach(function (table) {
            table.navigatorMeta(table.catalogEntry.navigatorMeta);
          })
        })
      }
      if (optimizerEnabled) {
        self.catalogEntry.loadNavOptPopularityForChildren().done(function () {
          self.tables().forEach(function (table) {
            table.optimizerStats(table.catalogEntry.navOptPopularity);
          })
        });
      }
      self.loaded(true);
    }).fail(function () {
      self.tables([]);
    }).always(function () {
      self.loading(false);
      if (callback) {
        callback();
      }
    });

    // TODO: Move to ApiHelper (via DataCatalogEntry)
    $.getJSON('/metastore/databases/' + self.catalogEntry.name + '/metadata', function (data) {
      if (data && data.status == 0) {
        self.stats(data.data);
      }
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
    hueUtils.waitForRendered('a[href="#overview"]', function(el){ return el.is(':visible') }, function(){
      window.setTimeout(function(){
        $('a[href="#overview"]').click();
      }, 0);
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
    self.apiHelper = ApiHelper.getInstance();

    self.loaded = ko.observable(false);
    self.loading = ko.observable(true);

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
    // TODO: Add to DataCatalogEntry
    self.apiHelper.fetchPartitions({
      databaseName: self.metastoreTable.catalogEntry.path[0],
      tableName: self.metastoreTable.catalogEntry.name,
      successCallback: function (data) {
        self.keys(data.partition_keys_json);
        self.values(data.partition_values_json);
        self.preview.values(self.values().slice(0, 5));
        self.preview.keys(self.keys());
        self.loading(false);
        self.loaded(true);
        huePubSub.publish('metastore.loaded.partitions');
      },
      errorCallback: function () {
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

    self.hasErrors = ko.observable(false);
    self.errorMessage = ko.observable();
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
    self.loading(true);
    self.metastoreTable.catalogEntry.getSample().done(function (sample) {
      self.rows(sample.rows);
      self.headers(sample.headers);
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

    self.apiHelper = ApiHelper.getInstance();

    // TODO: Check if enough or if we need to fetch additional details
    self.isView = ko.observable(self.catalogEntry.isView());

    self.optimizerStats = ko.observable();
    self.optimizerDetails = ko.observable();
    self.navigatorMeta = ko.observable();
    self.relationshipsDetails = ko.observable();

    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);

    self.loadingDetails = ko.observable(false);
    self.loadingColumns = ko.observable(false);

    self.columnQuery = ko.observable('').extend({ rateLimit: 150 });
    self.columns = ko.observableArray();
    self.filteredColumns = ko.computed(function () {
      var returned = self.columns();
      if (self.columnQuery() !== '') {
        returned = self.columns().filter(function (column) {
          var entry = column.catalogEntry;
          return entry.name.toLowerCase().indexOf(self.columnQuery().toLowerCase()) !== -1
            || (entry.getType().toLowerCase().indexOf(self.columnQuery().toLowerCase()) !== -1)
            || (column.comment() && column.comment().toLowerCase().indexOf(self.columnQuery().toLowerCase()) !== -1);
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
    self.loadingQueries = ko.observable(true);

    self.comment = ko.observable();

    self.commentWithoutNewLines = ko.pureComputed(function(){
      return self.comment() ? hueUtils.deXSS(self.comment().replace(/<br\s*[\/]?>/gi, ' ')) : '';
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

    // TODO: Move stats to DataCatalogEntry
    self.refreshTableStats = function () {
      if (self.refreshingTableStats()) {
        return;
      }
      self.refreshingTableStats(true);
      self.apiHelper.refreshTableStats({
        tableName: self.catalogEntry.name,
        databaseName: self.database.catalogEntry.name,
        sourceType: self.catalogEntry.getSourceType(),
        successCallback: function () {
          self.fetchDetails();
        },
        errorCallback: function (data) {
          self.refreshingTableStats(false);
          $.jHueNotify.error(HUE_I18n.metastore.errorRefreshingTableStats);
          console.error('apiHelper.refreshTableStats error');
          console.error(data);
        }
      })
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
        self.favouriteColumns(self.columns().slice(0, 5));
      }).fail(function () {
        self.columns([]);
        self.favouriteColumns([]);
      }).always(function () {
        self.loadingColumns(false);
      });
    };

    self.fetchDetails = function () {
      self.loadingDetails(true);

      // TODO: Load in parallel
      self.catalogEntry.getAnalysis().done(function (analysis) {
        self.loadingDetails(false);
        if ((typeof analysis === 'object') && (analysis !== null)) {
          self.tableDetails(analysis);
          self.tableStats(analysis.details.stats);
          self.refreshingTableStats(false);
          self.samples.load();
          self.loaded(true);
          self.loading(false);
          if (analysis.partition_keys.length) {
            self.partitions.detailedKeys(analysis.partition_keys);
            self.partitions.load();
          } else {
            self.partitions.loading(false);
            self.partitions.loaded(true);
          }

          self.catalogEntry.getComment().done(self.comment);

          // TODO: Move to DataCatalogEntry
          if (self.optimizerEnabled) {
            $.post('/metadata/api/optimizer/table_details', {
              databaseName: self.database.catalogEntry.name,
              tableName: self.catalogEntry.name
            }, function(data){
              self.loadingQueries(false);
              if (data && data.status == 0) {
                self.optimizerDetails(ko.mapping.fromJS(data.details));

                // Bump the most important columns first
                var topCols = $.map(self.optimizerDetails().topCols().slice(0, 5), function(item) { return item.name(); });
                if (topCols.length >= 3 && self.favouriteColumns().length > 0) {
                  self.favouriteColumns(self.columns().filter(function(col) {
                    return topCols.indexOf(col.catalogEntry.name) !== -1;
                  }));
                }

                // Column popularity, stats
                $.each(self.optimizerDetails().topCols(), function(index, optimizerCol) {
                  var metastoreCol = $.grep(self.columns(), function(col) {
                    return col.catalogEntry.name == optimizerCol.name();
                  });
                  if (metastoreCol.length > 0) {
                    metastoreCol[0].popularity(optimizerCol.score())
                  }
                });
              } else {
                $(document).trigger("info", data.message);
              }
            });
          }
        } else {
          self.refreshingTableStats(false);
          self.loading(false);
        }
      }).fail(function () {
        self.refreshingTableStats(false);
        self.loading(false);
      }).always(function () {
        self.loadingDetails(false)
      });
    };

    self.drop = function () {
      $.post('/tables/drop/' + self.database.catalogEntry.name, {
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

    self.getRelationships = function () {
      $.post('/metadata/api/navigator/lineage', {
        id: self.navigatorMeta().identity
      }, function(data) {
        if (data && data.status == 0) {
          self.relationshipsDetails(ko.mapping.fromJS(data));
        } else {
          $(document).trigger("error", data.message);
        }
      }).fail(function (xhr) {
        $(document).trigger("info", xhr.responseText);
      });
    };
  }

  MetastoreTable.prototype.showImportData = function () {
    var self = this;
    $("#import-data-modal").empty().html('<div class="modal-header"><button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span></button><h2 class="modal-title"></h2></div><div class="modal-body"><i class="fa fa-spinner fa-spin fa-2x muted"></i></div>').modal("show");
    $.get('/metastore/table/' + self.catalogEntry.path.join('/') + '/load', function (data) {
      $("#import-data-modal").html(data['data']);
    }).fail(function (xhr) {
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
    self.refreshTableStats();
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
        type: 'table',
        identifierChain: [{ name: entry.catalogEntry.name }]
      },
      orientation: orientation || 'right',
      sourceType: entry.catalogEntry.getSourceType(),
      defaultDatabase: entry.database.catalogEntry.name,
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
  }

  MetastoreColumn.prototype.showContextPopover = function (entry, event) {
    var $source = $(event.target);
    var offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'column',
        identifierChain: [{ name: entry.table.catalogEntry.name }, { name: entry.catalogEntry.name }]
      },
      orientation: 'right',
      sourceType: entry.catalogEntry.getSourceType(),
      defaultDatabase: entry.table.database.catalogEntry.name,
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
