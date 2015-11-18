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
    root.AssistEntry = factory(ko);
  }
}(this, function (ko) {

  function AssistEntry (definition, parent, assistSource, filter, i18n) {
    var self = this;
    self.i18n = i18n;
    self.definition = definition;

    self.assistSource = assistSource;
    self.parent = parent;
    self.filter = filter;

    self.expandable = typeof definition.type === "undefined" || definition.type === "struct" || definition.type === "array" || definition.type === "map";

    self.loaded = false;
    self.loading = ko.observable(false);
    self.open = ko.observable(false);
    self.entries = ko.observableArray([]);
    self.statsVisible = ko.observable(false);

    self.open.subscribe(function(newValue) {
      if (newValue && self.entries().length == 0) {
        self.loadEntries();
      }
    });

    self.hasEntries = ko.computed(function() {
      return self.entries().length > 0;
    });

    self.filteredEntries = ko.computed(function () {
      if (self.filter == null || self.filter().length === 0) {
        return self.entries();
      }
      var result = [];
      $.each(self.entries(), function (index, entry) {
        if (entry.definition.name.toLowerCase().indexOf(self.filter()) > -1) {
          result.push(entry);
        }
      });
      return result;
    });

    self.tableName = null;
    self.columnName = null;
    self.databaseName = self.getHierarchy()[0];
    if (self.definition.isTable) {
      self.tableName = self.definition.name;
      self.columnName = null;
    } else if (self.definition.isColumn) {
      self.tableName = parent.definition.name;
      self.columnName = self.definition.name;
    }

    self.editorText = ko.computed(function () {
      if (self.definition.isTable) {
        return self.definition.name;
      }
      if (self.definition.isColumn) {
        return self.definition.name + ", ";
      }
      var parts = [];
      var entry = self;
      while (entry != null) {
        if (entry.definition.isTable) {
          break;
        }
        if (entry.definition.isArray || entry.definition.isMapValue) {
          if (self.assistSource.assistHelper.type === 'hive') {
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

  AssistEntry.prototype.loadEntries = function() {
    var self = this;
    if (!self.expandable || self.loading()) {
      return;
    }
    self.loading(true);
    self.entries([]);

    // Defer this part to allow ko to react on empty entries and loading
    window.setTimeout(function() {
      self.assistSource.assistHelper.fetchPanelData(self.assistSource.snippet, self.getHierarchy(), function(data) {
        if (typeof data.tables !== "undefined") {
          self.entries($.map(data.tables, function(tableName) {
            return self.createEntry({
              name: tableName,
              displayName: tableName,
              title: tableName,
              isTable: true
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
      }, function() {
        self.assistSource.hasErrors(true);
        self.loading(false);
      });
    }, 10);
  };

  AssistEntry.prototype.createEntry = function(definition) {
    var self = this;
    return new AssistEntry(definition, self, self.assistSource, null)
  };

  AssistEntry.prototype.getHierarchy = function () {
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

  AssistEntry.prototype.dblClick = function (data, event) {
    var self = this;
    huePubSub.publish('assist.dblClickItem', self);
  };

  AssistEntry.prototype.toggleOpen = function () {
    var self = this;
    self.open(!self.open());
  };

  AssistEntry.prototype.showPreview = function () {
    var self = this;
    var $assistQuickLook = $("#assistQuickLook");

    var hierarchy = self.getHierarchy();
    var databaseName = hierarchy[0];
    var tableName = hierarchy[1];

    $assistQuickLook.find(".tableName").text(self.definition.name);
    $assistQuickLook.find(".tableLink").attr("href", "/metastore/table/" + self.assistSource.assistHelper.activeDatabase() + "/" + tableName);
    $assistQuickLook.find(".sample").empty("");
    $assistQuickLook.attr("style", "width: " + ($(window).width() - 120) + "px;margin-left:-" + (($(window).width() - 80) / 2) + "px!important;");

    self.assistSource.assistHelper.fetchTableHtmlPreview(self.assistSource.snippet, tableName, function(data) {
      $assistQuickLook.find(".loader").hide();
      $assistQuickLook.find(".sample").html(data);
    }, function(e) {
      if (e.status == 500) {
        $(document).trigger("error", self.i18n.errorLoadingTablePreview);
        $("#assistQuickLook").modal("hide");
      }
    });

    $assistQuickLook.modal("show");
  };

  return AssistEntry;
}));
