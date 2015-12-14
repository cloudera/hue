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
    define(['knockout'], factory);
  } else {
    root.AssistDbEntry = factory(ko);
  }
}(this, function (ko) {

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
  function AssistDbEntry (definition, parent, assistDbSource, filter, i18n, navigationSettings) {
    var self = this;
    self.i18n = i18n;
    self.definition = definition;

    self.assistDbSource = assistDbSource;
    self.parent = parent;
    self.filter = filter;
    self.isSearchVisible = ko.observable(false);
    self.editingSearch = ko.observable(false);

    self.expandable = typeof definition.type === "undefined" || /table|view|struct|array|map/i.test(definition.type);

    self.loaded = false;
    self.loading = ko.observable(false);
    self.open = ko.observable(false);
    self.entries = ko.observableArray([]);
    self.statsVisible = ko.observable(false);

    self.navigationSettings = navigationSettings;

    self.open.subscribe(function(newValue) {
      if (newValue && self.entries().length == 0) {
        self.loadEntries();
      }
    });

    self.hasEntries = ko.computed(function() {
      return self.entries().length > 0;
    });

    self.filteredEntries = ko.computed(function () {
      if (self.filter == null || (self.filter.showTables && self.filter.showTables() && self.filter.showViews() && self.filter.query().length === 0)) {
        return self.entries();
      }
      var result = [];
      $.each(self.entries(), function (index, entry) {
        if ((entry.definition.isTable && !self.filter.showTables()) || (entry.definition.isView && !self.filter.showViews()) ) {
          return;
        }
        if (entry.definition.name.toLowerCase().indexOf(self.filter.query()) > -1) {
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

    self.editorText = ko.computed(function () {
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
          if (self.assistDbSource.type === 'hive') {
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

  AssistDbEntry.prototype.toggleSearch = function() {
    var self = this;
    self.isSearchVisible(!self.isSearchVisible());
    self.editingSearch(self.isSearchVisible());
  };

  AssistDbEntry.prototype.loadEntries = function() {
    var self = this;
    if (!self.expandable || self.loading()) {
      return;
    }
    self.loading(true);

    var successCallback = function(data) {
      self.entries([]);
      if (typeof data.tables_meta !== "undefined") {
        self.entries($.map(data.tables_meta, function(table) {
          return self.createEntry({
            name: table.name,
            displayName: table.name,
            title: table.name + (table.comment ? ' - ' + table.comment : ''),
            type: table.type,
            isTable: /table/i.test(table.type),
            isView: /view/i.test(table.type)
          });
        }));
      } else if (typeof data.extended_columns !== "undefined" && data.extended_columns !== null) {
        self.entries($.map(data.extended_columns, function (columnDef) {
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
          return self.createEntry({
            name: columnDef.name,
            displayName: displayName,
            title: title,
            isColumn: true,
            type: shortType
          });
        }));
      } else if (typeof data.columns !== "undefined" && data.columns !== null) {
        self.entries($.map(data.columns, function(columnName) {
          return self.createEntry({
            name: columnName,
            displayName: columnName,
            title: columnName,
            isColumn: true
          });
        }));
      } else if (typeof data.type !== "undefined" && data.type !== null) {
        if (data.type === "map") {
          self.entries([
            self.createEntry({
              name: "key",
              displayName: "key (" + data.key.type + ")",
              title: "key (" + data.key.type + ")",
              type: data.key.type
            }),
            self.createEntry({
              name: "value",
              displayName: "value (" + data.value.type + ")",
              title: "value (" + data.value.type + ")",
              isMapValue: true,
              type: data.value.type
            })
          ]);
          self.entries()[1].open(true);
        } else if (data.type == "struct") {
          self.entries($.map(data.fields, function(field) {
            return self.createEntry({
              name: field.name,
              displayName: field.name + " (" + field.type + ")",
              title: field.name + " (" + field.type + ")",
              type: field.type
            });
          }));
        } else if (data.type == "array") {
          self.entries([
            self.createEntry({
              name: "item",
              displayName: "item (" + data.item.type + ")",
              title: "item (" + data.item.type + ")",
              isArray: true,
              type: data.item.type
            })
          ]);
          self.entries()[0].open(true);
        }
      }
      self.loading(false);
    };

    var errorCallback = function () {
      self.assistDbSource.hasErrors(true);
      self.loading(false);
    };

    self.assistDbSource.assistHelper.fetchPanelData({
      sourceType: self.assistDbSource.type,
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
    return new AssistDbEntry(definition, self, self.assistDbSource, null, self.i18n, self.navigationSettings)
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
        name: self.definition.name
      })
    }
  };

  AssistDbEntry.prototype.showPreview = function () {
    var self = this;
    var $assistQuickLook = $("#assistQuickLook");

    var hierarchy = self.getHierarchy();
    var databaseName = hierarchy[0];
    var tableName = hierarchy[1];

    $assistQuickLook.find(".tableName").text(self.definition.name);
    $assistQuickLook.find(".tableLink").attr("href", "/metastore/table/" + databaseName + "/" + tableName);
    self.assistDbSource.loadingSamples(true);
    self.assistDbSource.samples({});
    $assistQuickLook.attr("style", "width: " + ($(window).width() - 120) + "px;margin-left:-" + (($(window).width() - 80) / 2) + "px!important;");

    self.assistDbSource.assistHelper.fetchTableSample({
      sourceType: self.assistDbSource.type === "hive" ? "beeswax" : self.assistDbSource.type,
      databaseName: databaseName,
      tableName: tableName,
      dataType: "html",
      successCallback: function(data) {
        if (! data.rows) {
          data.rows = [];
        } else if (! data.headers) {
          data.headers = [];
        }
        self.assistDbSource.samples(data);
        self.assistDbSource.loadingSamples(false);
      },
      errorCallback: function(e) {
        if (e.status == 500) {
          $(document).trigger("error", self.i18n.errorLoadingTablePreview);
          $("#assistQuickLook").modal("hide");
        }
      }
    });

    $assistQuickLook.modal("show");
  };

  return AssistDbEntry;
}));
