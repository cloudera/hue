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

var AssistDbEntry = (function () {
  /**
   * @param {Object} definition
   * @param {string} definition.type
   * @param {string} definition.name
   * @param {boolean} [definition.isColumn]
   * @param {boolean} [definition.isTable]
   * @param {boolean} [definition.isView]
   * @param {boolean} [definition.isDatabase]
   * @param {boolean} [definition.isMapValue]
   * @param {boolean} [definition.isArray]
   * @param {AssistDbEntry} parent
   * @param {AssistDbSource} assistDbSource
   * @param {Object} filter
   * @param {function} filter.query (observable)
   * @param {function} filter.showViews (observable)
   * @param {function} filter.showTables (observable)
   * @param {Object} i18n
   * @param {string} i18n.errorLoadingTablePreview
   * @param {Object} navigationSettings
   * @constructor
   */
  function AssistDbEntry (definition, parent, assistDbSource, filter, i18n, navigationSettings, sortFunctions) {
    var self = this;
    self.i18n = i18n;
    self.definition = definition;
    self.sortFunctions = sortFunctions;

    self.assistDbSource = assistDbSource;
    self.parent = parent;
    self.filter = filter;
    self.isSearchVisible = assistDbSource.isSearchVisible;
    self.editingSearch = ko.observable(false);
    self.sourceType = self.assistDbSource.sourceType;
    self.invalidateOnRefresh =  self.assistDbSource.invalidateOnRefresh;
    self.highlight = ko.observable(false);
    self.highlightParent = ko.observable(false);
    self.activeSort = self.assistDbSource.activeSort;
    self.popularity = ko.observable(0);

    self.expandable = typeof definition.type === "undefined" || /table|view|struct|array|map/i.test(definition.type);

    self.loaded = false;
    self.loading = ko.observable(false);
    self.open = ko.observable(false);
    self.entries = ko.observableArray([]);
    self.statsVisible = ko.observable(false);

    self.hasErrors = ko.observable(false);

    self.navigationSettings = navigationSettings;

    self.open.subscribe(function(newValue) {
      if (newValue && self.entries().length == 0) {
        self.loadEntries();
      }
    });

    self.hasEntries = ko.pureComputed(function() {
      return self.entries().length > 0;
    });

    self.assistDbSource.activeSort.subscribe(function (newSort) {
      self.entries.sort(self.sortFunctions[newSort]);
    });

    self.filteredEntries = ko.pureComputed(function () {
      if (self.filter == null || (self.filter.showTables && self.filter.showTables() && self.filter.showViews() && !self.filter.showActive() && self.filter.query().length === 0)) {
        return self.entries();
      }
      var result = [];
      $.each(self.entries(), function (index, entry) {
        if (self.filter.showActive()) {
          var found = false;
          for (var i = 0; i < self.filter.activeEditorTables().length; i++) {
            var activeTable = self.filter.activeEditorTables()[i];
            if (activeTable.db && self.definition.name !== activeTable.db) {
              continue;
            }
            if (activeTable.table === entry.definition.name) {
              found = true;
              break;
            }
          }
          if (!found) {
            return;
          }
        }
        if ((entry.definition.isTable && !self.filter.showTables()) || (entry.definition.isView && !self.filter.showViews()) ) {
          return;
        }
        if (entry.definition.name.toLowerCase().indexOf(self.filter.query().toLowerCase()) > -1) {
          result.push(entry);
        }
      });
      return result;
    });

    self.tableName = null;
    self.columnName = null;
    self.type = null;
    self.databaseName = self.getHierarchy()[0];
    if (self.definition.isTable || self.definition.isView) {
      self.tableName = self.definition.name;
      self.columnName = null;
      self.type = self.definition.type;
    } else if (self.definition.isColumn) {
      self.tableName = parent.definition.name;
      self.columnName = self.definition.name;
    }

    self.editorText = ko.pureComputed(function () {
      if (self.definition.isTable || self.definition.isView) {
        return self.definition.name;
      }
      if (self.definition.isColumn) {
        return self.definition.name + ", ";
      }
      var parts = [];
      var entry = self;
      while (entry != null) {
        if (entry.definition.isTable || self.definition.isView) {
          break;
        }
        if (entry.definition.isArray || entry.definition.isMapValue) {
          if (self.assistDbSource.sourceType === 'hive') {
            parts.push("[]");
          }
        } else {
          parts.push(entry.definition.name);
          parts.push(".");
        }
        entry = entry.parent;
      }
      parts.reverse();
      parts.push(", ");
      return parts.slice(1).join("");
    });
  }

  AssistDbEntry.prototype.showContextPopover = function (entry, event, positionAdjustment) {
    var self = this;
    var $source = $(event.target);
    var offset = $source.offset();
    if (positionAdjustment) {
      offset.left += positionAdjustment.left;
      offset.top += positionAdjustment.top;
    }

    var type;
    if (self.definition.isColumn) {
      type = 'column';
    } else if (self.definition.isComplex) {
      type = 'complex';
    } else if (self.definition.isTable) {
      type = 'table';
    } else if (self.definition.isView) {
      type = 'view';
    } else {
      type = 'database';
    }

    self.statsVisible(true);
    huePubSub.publish('sql.context.popover.show', {
      data: {
        type: type,
        identifierChain: $.map(self.getHierarchy(), function (name) { return { name: name }})
      },
      showInAssistEnabled: false,
      orientation: 'right',
      sourceType: self.sourceType,
      defaultDatabase: self.databaseName,
      pinEnabled: self.navigationSettings.pinEnabled,
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 3,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 3
      }
    });
    huePubSub.subscribeOnce('sql.context.popover.hidden', function () {
      self.statsVisible(false);
    });
  };

  AssistDbEntry.prototype.toggleSearch = function () {
    var self = this;
    self.isSearchVisible(!self.isSearchVisible());
    self.editingSearch(self.isSearchVisible());
  };

  AssistDbEntry.prototype.triggerRefresh = function (data, event) {
    var self = this;
    self.assistDbSource.triggerRefresh(data, event);
  };

  AssistDbEntry.prototype.highlightInside = function (path) {
    var self = this;

    var searchEntry = function () {
      var foundEntry;
      $.each(self.entries(), function (idx, entry) {
        if (entry.definition.name === path[0]) {
          foundEntry = entry;
          entry.open(true);
          return false;
        }
      });
      if (foundEntry) {
        if (path.length > 1) {
          foundEntry.highlightParent(true);
          huePubSub.publish('assist.db.scrollToHighlight');
          window.setTimeout(function () {
            foundEntry.highlightInside(path.slice(1));
          }, 0);
        } else {
          foundEntry.highlight(true);
          huePubSub.publish('assist.db.scrollToHighlight');
        }
      }
    };

    if (self.entries().length == 0) {
      self.loadEntries(searchEntry);
    } else {
      searchEntry();
    }
  };

  AssistDbEntry.prototype.loadEntries = function(callback) {
    var self = this;
    if (!self.expandable || self.loading()) {
      return;
    }
    self.loading(true);

    var loadEntriesDeferred = $.Deferred();

    var successCallback = function(data) {
      self.entries([]);
      self.hasErrors(false);
      self.loading(false);

      var newEntries = [];
      var index = 0;
      if (typeof data.tables_meta !== "undefined") {
        newEntries = $.map(data.tables_meta, function(table) {
          table.index = index++;
          table.title = table.name + (table.comment ? ' - ' + table.comment : '');
          table.displayName = table.name;
          table.isTable = /table/i.test(table.type);
          table.isView = /view/i.test(table.type);
          return self.createEntry(table);
        });
      } else if (typeof data.extended_columns !== "undefined" && data.extended_columns !== null) {
        newEntries = $.map(data.extended_columns, function (columnDef) {
          var displayName = columnDef.name;
          if (typeof columnDef.type !== "undefined" && columnDef.type !== null) {
            displayName += ' (' + columnDef.type + ')'
          }
          var title = displayName;
          if (typeof columnDef.comment !== "undefined" && columnDef.comment !== null) {
            title += ' ' + columnDef.comment;
          }
          var shortType = null;
          if (typeof columnDef.type !== "undefined" && columnDef.type !== null) {
            shortType = columnDef.type.match(/^[^<]*/g)[0]; // everything before '<'
          }
          columnDef.index = index++;
          columnDef.displayName = displayName;
          columnDef.title = title;
          columnDef.isColumn = true;
          columnDef.type = shortType;
          return self.createEntry(columnDef);
        });
      } else if (typeof data.columns !== "undefined" && data.columns !== null) {
        newEntries = $.map(data.columns, function(columnName) {
          return self.createEntry({
            name: columnName,
            index: index++,
            displayName: columnName,
            title: columnName,
            isColumn: true
          });
        });
      } else if (typeof data.type !== "undefined" && data.type !== null) {
        if (data.type === "map") {
          newEntries = [
            self.createEntry({
              name: "key",
              index: index++,
              displayName: "key (" + data.key.type + ")",
              title: "key (" + data.key.type + ")",
              type: data.key.type,
              isComplex: true
            }),
            self.createEntry({
              name: "value",
              index: index++,
              displayName: "value (" + data.value.type + ")",
              title: "value (" + data.value.type + ")",
              isMapValue: true,
              type: data.value.type,
              isComplex: true
            })
          ];
        } else if (data.type == "struct") {
          newEntries = $.map(data.fields, function(field) {
            return self.createEntry({
              name: field.name,
              index: index++,
              displayName: field.name + " (" + field.type + ")",
              title: field.name + " (" + field.type + ")",
              type: field.type,
              isComplex: true
            });
          });
        } else if (data.type == "array") {
          newEntries = [
            self.createEntry({
              name: "item",
              index: index++,
              displayName: "item (" + data.item.type + ")",
              title: "item (" + data.item.type + ")",
              isArray: true,
              type: data.item.type,
              isComplex: true
            })
          ];
        }
      }


      if (data.type === 'array' || data.type === 'map') {
        self.entries(newEntries);
        self.entries()[0].open(true);
      } else {
        newEntries.sort(self.sortFunctions[self.assistDbSource.activeSort()]);
        self.entries(newEntries);
      }
      loadEntriesDeferred.resolve(newEntries);
      if (typeof callback === 'function') {
        callback();
      }
    };

    var errorCallback = function () {
      self.hasErrors(true);
      self.loading(false);
      loadEntriesDeferred.resolve([]);
    };

    if (HAS_OPTIMIZER && self.definition.isTable) {
      self.assistDbSource.apiHelper.fetchNavOptTopColumns({
        sourceType: self.assistDbSource.sourceType,
        successCallback: function (data) {
          if (data.status === 0 && data.values && data.values.selectColumns && data.values.selectColumns.length > 0) {
            var colIndex = {};
            data.values.selectColumns.forEach(function (col) {
              colIndex[col.columnName] = col;
            });
            $.when(loadEntriesDeferred).done(function () {
              if (!self.hasErrors()) {
                self.entries().forEach(function (entry) {
                  if (colIndex[entry.definition.name]) {
                    entry.popularity(colIndex[entry.definition.name].columnCount);
                  }
                });

                if (self.assistDbSource.activeSort() === 'popular') {
                  self.entries.sort(self.sortFunctions.popular);
                }
              }
            })
          }
        },
        silenceErrors: true,
        tables: [{ identifierChain: [{ name: self.definition.name }] }],
        defaultDatabase: self.parent.definition.name
      })
    }

    self.assistDbSource.apiHelper.fetchPanelData({
      sourceType: self.assistDbSource.sourceType,
      hierarchy: self.getHierarchy(),
      successCallback: successCallback,
      errorCallback: errorCallback
    });
  };

  /**
   * @param {Object} definition
   * @param {string} definition.type
   * @param {string} definition.name
   * @param {boolean} [definition.isDatabase]
   * @param {boolean} [definition.isColumn]
   * @param {boolean} [definition.isTable]
   * @param {boolean} [definition.isView]
   * @param {boolean} [definition.isMapValue]
   * @param {boolean} [definition.isArray]
   */
  AssistDbEntry.prototype.createEntry = function (definition) {
    var self = this;
    return new AssistDbEntry(definition, self, self.assistDbSource, null, self.i18n, self.navigationSettings, self.sortFunctions)
  };

  AssistDbEntry.prototype.getHierarchy = function () {
    var self = this;
    var parts = [];
    var entry = self;
    while (entry != null) {
      parts.push(entry.definition.name);
      entry = entry.parent;
    }
    parts.reverse();
    return parts;
  };

  AssistDbEntry.prototype.dblClick = function () {
    var self = this;
    huePubSub.publish('assist.dblClickDbItem', self);
  };

  AssistDbEntry.prototype.toggleOpen = function () {
    var self = this;
    self.open(!self.open());
  };

  AssistDbEntry.prototype.openItem = function () {
    var self = this;
    if (self.definition.isTable || self.definition.isView) {
      huePubSub.publish("assist.table.selected", {
        database: self.databaseName,
        name: self.definition.name
      })
    } else if (self.definition.isDatabase) {
      huePubSub.publish("assist.database.selected", {
        source: self.assistDbSource.sourceType,
        name: self.definition.name
      })
    }
  };

  return AssistDbEntry;
})();
