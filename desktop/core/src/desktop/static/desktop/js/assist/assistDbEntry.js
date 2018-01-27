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
   * @param {DataCatalogEntry} catalogEntry
   * @param {AssistDbEntry} parent
   * @param {AssistDbSource} assistDbSource
   * @param {Object} filter
   * @param {function} filter.querySpec (observable)
   * @param {function} filter.showViews (observable)
   * @param {function} filter.showTables (observable)
   * @param {Object} i18n
   * @param {string} i18n.errorLoadingTablePreview
   * @param {Object} navigationSettings
   * @constructor
   */
  function AssistDbEntry (catalogEntry, parent, assistDbSource, filter, i18n, navigationSettings) {
    var self = this;
    self.catalogEntry = catalogEntry;
    self.parent = parent;
    self.assistDbSource = assistDbSource;
    self.filter = filter;
    self.i18n = i18n;
    self.navigationSettings = navigationSettings;

    self.sourceType = assistDbSource.sourceType;
    self.invalidateOnRefresh =  assistDbSource.invalidateOnRefresh;
    self.sortFunctions = assistDbSource.sortFunctions;
    self.isSearchVisible = assistDbSource.isSearchVisible;
    self.activeSort = assistDbSource.activeSort;

    self.expandable = self.catalogEntry.hasPossibleChildren();

    self.filterColumnNames = ko.observable(false);
    self.highlight = ko.observable(false);
    self.popularity = ko.observable(0);

    self.loaded = false;
    self.loading = ko.observable(false);
    self.open = ko.observable(false);
    self.entries = ko.observableArray([]);
    self.statsVisible = ko.observable(false);

    self.hasErrors = ko.observable(false);

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
      var facets = self.filter.querySpec().facets;
      var tableAndViewFilterMatch = !self.catalogEntry.isDatabase() || (self.filter.showTables && self.filter.showTables() && self.filter.showViews && self.filter.showViews());
      var facetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
      // Only text match on tables/views or columns if flag is set
      var textMatch = (!self.catalogEntry.isDatabase() && !self.filterColumnNames()) || (!self.filter.querySpec().text || self.filter.querySpec().text.length === 0);

      if (tableAndViewFilterMatch && facetMatch && textMatch) {
        return self.entries();
      }

      return self.entries().filter(function (entry) {
        var match = true;
        if (!tableAndViewFilterMatch) {
          match = entry.catalogEntry.isTable() && self.filter.showTables() || entry.catalogEntry.isView() && self.filter.showViews();
        }

        if (match && !facetMatch) {
          if (entry.catalogEntry.isField()) {
            match = (Object.keys(facets['type']).length === 2 && facets['type']['table'] && facets['type']['view'])
              || (Object.keys(facets['type']).length === 1 && (facets['type']['table'] || facets['type']['view']))
              || facets['type'][entry.catalogEntry.getType()];
          } else if (entry.catalogEntry.isTableOrView()) {
            match = (!facets['type']['table'] && !facets['type']['view']) || (facets['type']['table'] && entry.catalogEntry.isTable()) || (facets['type']['view'] && entry.catalogEntry.isView());
          }
        }

        if (match && !textMatch) {
          var nameLower = entry.catalogEntry.name.toLowerCase();
          match = self.filter.querySpec().text.every(function (text) {
            return nameLower.indexOf(text.toLowerCase()) !== -1
          });
        }

        return match;
      });
    });

    self.autocompleteFromEntries = function (nonPartial, partial) {
      var result = [];
      var partialLower = partial.toLowerCase();
      self.entries().forEach(function (entry) {
        if (entry.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + entry.catalogEntry.name.substring(partial.length))
        }
      });
      return result;
    };

    self.tableName = null;
    self.columnName = null;
    self.type = null;
    self.databaseName = self.getHierarchy()[0];
    if (self.catalogEntry.isTableOrView()) {
      self.tableName = self.catalogEntry.name;
      self.columnName = null;
      self.type = self.catalogEntry.getType();
    } else if (self.catalogEntry.isColumn()) {
      self.tableName = parent.catalogEntry.name;
      self.columnName = self.catalogEntry.name;
    }

    self.editorText = ko.pureComputed(function () {
      if (self.catalogEntry.isTableOrView()) {
        return self.getTableName();
      }
      if (self.catalogEntry.isColumn()) {
        return self.getColumnName() + ', ';
      }
      return self.getComplexName() + ', ';
    });
  }

  var findNameInHierarchy = function (entry, searchCondition) {
    var sourceType = entry.sourceType;
    while (entry && !searchCondition(entry)) {
      entry = entry.parent;
    }
    if (entry) {
      return SqlUtils.backTickIfNeeded(sourceType, entry.catalogEntry.name);
    }
  };

  AssistDbEntry.prototype.getDatabaseName = function () {
    return findNameInHierarchy(this, function (entry) { return entry.catalogEntry.isDatabase() });
  };

  AssistDbEntry.prototype.getTableName = function () {
    return findNameInHierarchy(this, function (entry) { return entry.catalogEntry.isTableOrView() });
  };

  AssistDbEntry.prototype.getColumnName = function () {
    return findNameInHierarchy(this, function (entry) { return entry.catalogEntry.isColumn() });
  };

  AssistDbEntry.prototype.getComplexName = function () {
    var entry = this;
    var sourceType = entry.sourceType;
    var parts = [];
    while (entry != null) {
      if (entry.catalogEntry.isTableOrView()) {
        break;
      }
      if (entry.catalogEntry.isArray() || entry.catalogEntry.isMapValue()) {
        if (sourceType === 'hive') {
          parts.push("[]");
        }
      } else {
        parts.push(SqlUtils.backTickIfNeeded(sourceType, entry.catalogEntry.name));
        parts.push(".");
      }
      entry = entry.parent;
    }
    parts.reverse();
    return parts.slice(1).join("");
  };

  AssistDbEntry.prototype.showContextPopover = function (entry, event, positionAdjustment) {
    var self = this;
    var $source = $(event.target);
    var offset = $source.offset();
    if (positionAdjustment) {
      offset.left += positionAdjustment.left;
      offset.top += positionAdjustment.top;
    }

    var type;
    if (self.catalogEntry.isColumn() && self.sourceType === 'solr') {
      type = 'collection';
    } else if (self.catalogEntry.isColumn()) {
      type = 'column';
    } else if (self.catalogEntry.isDatabase()) {
      type = 'database';
    } else if (self.catalogEntry.isTable()) {
      type = 'table';
    } else if (self.catalogEntry.isView()) {
      type = 'view';
    } else {
      type = 'complex';
    }

    self.statsVisible(true);
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: self.catalogEntry
      },
      showInAssistEnabled: self.navigationSettings.rightAssist,
      orientation: self.navigationSettings.rightAssist ? 'left' : 'right',
      pinEnabled: self.navigationSettings.pinEnabled,
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 3,
        right: offset.left + $source.width() + 1,
        bottom: offset.top + $source.height() - 3
      }
    });
    huePubSub.subscribeOnce('context.popover.hidden', function () {
      self.statsVisible(false);
    });
  };

  AssistDbEntry.prototype.toggleSearch = function () {
    var self = this;
    self.isSearchVisible(!self.isSearchVisible());
  };

  AssistDbEntry.prototype.triggerRefresh = function () {
    var self = this;
    self.catalogEntry.clear(self.invalidateOnRefresh(), true);
  };

  AssistDbEntry.prototype.highlightInside = function (path) {
    var self = this;

    var searchEntry = function () {
      var foundEntry;
      $.each(self.entries(), function (idx, entry) {
        entry.highlight(false);
        if (entry.catalogEntry.name === path[0]) {
          foundEntry = entry;
        }
      });
      if (foundEntry) {
        if (foundEntry.expandable && !foundEntry.open()) {
          foundEntry.open(true);
        }

        window.setTimeout(function () {
          if (path.length > 1) {
            foundEntry.highlightInside(path.slice(1));
          } else {
            huePubSub.subscribeOnce('assist.db.scrollToComplete', function () {
              foundEntry.highlight(true);
              // Timeout is for animation effect
              window.setTimeout(function () {
                foundEntry.highlight(false);
              }, 1800);
            });
            huePubSub.publish('assist.db.scrollTo', foundEntry);
          }
        }, 0);
      }
    };

    if (self.entries().length === 0) {
      if (self.loading()) {
        var subscription = self.loading.subscribe(function (newVal) {
          if (!newVal) {
            subscription.dispose();
            searchEntry();
          }
        });
      } else {
        self.loadEntries(searchEntry);
      }
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

    var successCallback = function(sourceMeta) {
      self.entries([]);
      if (!sourceMeta.notFound) {
        self.catalogEntry.getChildren({ silenceErrors: self.navigationSettings.rightAssist }).done(function (catalogEntries) {
          self.hasErrors(false);
          self.loading(false);
          self.loaded = true;
          if (catalogEntries.length === 0) {
            self.entries([]);
            return;
          }
          var newEntries = [];
          catalogEntries.forEach(function (catalogEntry) {
            newEntries.push(self.createEntry(catalogEntry));
          });
          if (sourceMeta.type === 'array') {
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
        }).fail(function () {
          self.loading(false);
          self.loaded = true;
          self.hasErrors(true);
        });

        if (self.assistDbSource.sourceType !== 'solr') {
          self.catalogEntry.loadNavigatorMetaForChildren({ silenceErrors: self.navigationSettings.rightAssist });
        }
      } else {
        self.hasErrors(true);
        self.loading(false);
        self.loaded = true;
        if (typeof callback === 'function') {
          callback();
        }
      }
    };

    var errorCallback = function () {
      self.hasErrors(true);
      self.loading(false);
      self.loaded = true;
      loadEntriesDeferred.resolve([]);
    };

    if (!self.navigationSettings.rightAssist && HAS_OPTIMIZER && self.catalogEntry.isTable() && self.assistDbSource.sourceType !== 'solr') {
      self.catalogEntry.loadNavOptPopularityForChildren({ silenceErrors: true }).done(function () {
        loadEntriesDeferred.done(function () {
          if (!self.hasErrors()) {
            self.entries().forEach(function (entry) {
              if (entry.catalogEntry.navOptPopularity) {
                entry.popularity(entry.catalogEntry.navOptPopularity.columnCount)
              }
            });

            if (self.assistDbSource.activeSort() === 'popular') {
              self.entries.sort(self.sortFunctions.popular);
            }
          }
        })
      });
    }

    self.catalogEntry.getSourceMeta({ silenceErrors: self.navigationSettings.rightAssist }).done(successCallback).fail(errorCallback);
  };

  /**
   * @param {DataCatalogEntry} catalogEntry
   */
  AssistDbEntry.prototype.createEntry = function (catalogEntry) {
    var self = this;
    return new AssistDbEntry(catalogEntry, self, self.assistDbSource, self.filter, self.i18n, self.navigationSettings)
  };

  AssistDbEntry.prototype.getHierarchy = function () {
    var self = this;
    return self.catalogEntry.path.concat();
  };

  AssistDbEntry.prototype.dblClick = function () {
    var self = this;
    if (self.catalogEntry.isTableOrView()) {
      huePubSub.publish('editor.insert.table.at.cursor', { name: self.getTableName(), database: self.getDatabaseName() });
    } else if (self.catalogEntry.isColumn()) {
      huePubSub.publish('editor.insert.column.at.cursor', { name: self.getColumnName(), table: self.getTableName(), database: self.getDatabaseName() });
    } else {
      huePubSub.publish('editor.insert.column.at.cursor', { name: self.getComplexName(), table: self.getTableName(), database: self.getDatabaseName() });
    }
  };

  AssistDbEntry.prototype.explore = function (isSolr) {
    var self = this;
    if (isSolr) {
      huePubSub.publish('open.link', '/hue/dashboard/browse/' + self.catalogEntry.name);
    }
    else {
      huePubSub.publish('open.link', '/hue/dashboard/browse/' + self.getDatabaseName() + '.' + self.getTableName() + '?engine=' + self.assistDbSource.sourceType);
    }
  };

  AssistDbEntry.prototype.openInMetastore = function () {
    var self = this;
    var url;
    if (self.catalogEntry.isDatabase()) {
      url = '/metastore/tables/' + self.catalogEntry.name;
    } else if (self.catalogEntry.isTableOrView()) {
      url = '/metastore/table/' + self.parent.catalogEntry.name + '/' + self.catalogEntry.name;
    } else {
      return;
    }

    if (IS_HUE_4) {
      huePubSub.publish('open.link', url);
    } else {
      window.open(url, '_blank');
    }
  };

  AssistDbEntry.prototype.openInIndexer = function () {
    var self = this;
    var definitionName = self.catalogEntry.name;
    if (IS_NEW_INDEXER_ENABLED) {
      if (IS_HUE_4) {
        huePubSub.publish('open.link', '/indexer/indexes/' + definitionName);
      }
      else {
        window.open('/indexer/indexes/' + definitionName);
      }
    }
    else {
      var hash = '#edit/' + definitionName;
      if (IS_HUE_4) {
        if (window.location.pathname.startsWith('/hue/indexer') && !window.location.pathname.startsWith('/hue/indexer/importer')) {
          window.location.hash = hash;
        }
        else {
          huePubSub.subscribeOnce('app.gained.focus', function (app) {
            if (app === 'indexes') {
              window.setTimeout(function () {
                window.location.hash = hash;
              }, 0)
            }
          });
          huePubSub.publish('open.link', '/indexer');
        }
      }
      else {
        window.open('/indexer/' + hash);
      }
    }
  };

  AssistDbEntry.prototype.toggleOpen = function () {
    var self = this;
    self.open(!self.open());
  };

  AssistDbEntry.prototype.openItem = function () {
    var self = this;
    if (self.catalogEntry.isTableOrView()) {
      huePubSub.publish("assist.table.selected", {
        database: self.databaseName,
        name: self.catalogEntry.name
      })
    } else if (self.catalogEntry.isDatabase()) {
      huePubSub.publish("assist.database.selected", {
        source: self.assistDbSource.sourceType,
        name: self.catalogEntry.name
      })
    }
  };

  return AssistDbEntry;
})();
