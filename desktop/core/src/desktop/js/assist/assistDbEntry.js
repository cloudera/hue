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

import $ from 'jquery';
import ko from 'knockout';

import huePubSub from 'utils/huePubSub';
import sqlUtils from 'sql/sqlUtils';

const findNameInHierarchy = (entry, searchCondition) => {
  const sourceType = entry.sourceType;
  while (entry && !searchCondition(entry)) {
    entry = entry.parent;
  }
  if (entry) {
    return sqlUtils.backTickIfNeeded(sourceType, entry.catalogEntry.name);
  }
};

class AssistDbEntry {
  /**
   * @param {DataCatalogEntry} catalogEntry
   * @param {AssistDbEntry} parent
   * @param {AssistDbNamespace} assistDbNamespace
   * @param {Object} filter
   * @param {function} filter.querySpec (observable)
   * @param {Object} i18n
   * @param {string} i18n.errorLoadingTablePreview
   * @param {Object} navigationSettings
   * @constructor
   */
  constructor(catalogEntry, parent, assistDbNamespace, filter, i18n, navigationSettings) {
    const self = this;
    self.catalogEntry = catalogEntry;
    self.parent = parent;
    self.assistDbNamespace = assistDbNamespace;
    self.filter = filter;
    self.i18n = i18n;
    self.navigationSettings = navigationSettings;

    self.sourceType = assistDbNamespace.sourceType;
    self.invalidateOnRefresh = assistDbNamespace.invalidateOnRefresh;

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

    self.iconClass = '';
    if (!self.navigationSettings.rightAssist) {
      if (self.sourceType === 'solr') {
        self.iconClass = 'fa-search';
      } else if (self.sourceType === 'kafka') {
        self.iconClass = 'fa-sitemap';
      } else if (self.catalogEntry.isView()) {
        self.iconClass = 'fa-eye';
      } else {
        self.iconClass = 'fa-table';
      }
    }

    self.open.subscribe(newValue => {
      if (newValue && self.entries().length === 0) {
        self.loadEntries();
      }
    });

    self.hasEntries = ko.pureComputed(() => self.entries().length > 0);

    self.filteredEntries = ko.pureComputed(() => {
      const facets = self.filter.querySpec().facets;
      const facetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
      // Only text match on tables/views or columns if flag is set
      const textMatch =
        (!self.catalogEntry.isDatabase() && !self.filterColumnNames()) ||
        (!self.filter.querySpec().text || self.filter.querySpec().text.length === 0);

      if (facetMatch && textMatch) {
        return self.entries();
      }

      return self.entries().filter(entry => {
        let match = true;

        if (match && !facetMatch) {
          if (entry.catalogEntry.isField()) {
            match =
              (Object.keys(facets['type']).length === 2 &&
                facets['type']['table'] &&
                facets['type']['view']) ||
              (Object.keys(facets['type']).length === 1 &&
                (facets['type']['table'] || facets['type']['view'])) ||
              facets['type'][entry.catalogEntry.getType()];
          } else if (entry.catalogEntry.isTableOrView()) {
            match =
              (!facets['type']['table'] && !facets['type']['view']) ||
              (facets['type']['table'] && entry.catalogEntry.isTable()) ||
              (facets['type']['view'] && entry.catalogEntry.isView());
          }
        }

        if (match && !textMatch) {
          const nameLower = entry.catalogEntry.name.toLowerCase();
          match = self.filter
            .querySpec()
            .text.every(text => nameLower.indexOf(text.toLowerCase()) !== -1);
        }

        return match;
      });
    });

    self.autocompleteFromEntries = (nonPartial, partial) => {
      const result = [];
      const partialLower = partial.toLowerCase();
      self.entries().forEach(entry => {
        if (entry.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + entry.catalogEntry.name.substring(partial.length));
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

    self.editorText = ko.pureComputed(() => {
      if (self.catalogEntry.isTableOrView()) {
        return self.getTableName();
      }
      if (self.catalogEntry.isColumn()) {
        return self.getColumnName() + ', ';
      }
      return self.getComplexName() + ', ';
    });
  }

  knownFacetValues() {
    const self = this;
    const types = {};
    if (self.parent === null) {
      // Only find facets on the DB level
      self.entries().forEach(tableEntry => {
        if (!self.assistDbNamespace.nonSqlType) {
          if (tableEntry.catalogEntry.isTable()) {
            types.table = types.table ? types.table + 1 : 1;
          } else if (tableEntry.catalogEntry.isView()) {
            types.view = types.view ? types.view + 1 : 1;
          }
        }
        if (tableEntry.open()) {
          tableEntry.entries().forEach(colEntry => {
            if (!types[colEntry.catalogEntry.getType()]) {
              types[colEntry.catalogEntry.getType()] = 1;
            } else {
              types[colEntry.catalogEntry.getType()]++;
            }
          });
        }
      });
    }
    if (Object.keys(types).length) {
      return { type: types };
    }
    return {};
  }

  getDatabaseName() {
    return findNameInHierarchy(this, entry => entry.catalogEntry.isDatabase());
  }

  getTableName() {
    return findNameInHierarchy(this, entry => entry.catalogEntry.isTableOrView());
  }

  getColumnName() {
    return findNameInHierarchy(this, entry => entry.catalogEntry.isColumn());
  }

  getComplexName() {
    let entry = this;
    const sourceType = entry.sourceType;
    const parts = [];
    while (entry != null) {
      if (entry.catalogEntry.isTableOrView()) {
        break;
      }
      if (entry.catalogEntry.isArray() || entry.catalogEntry.isMapValue()) {
        if (sourceType === 'hive') {
          parts.push('[]');
        }
      } else {
        parts.push(sqlUtils.backTickIfNeeded(sourceType, entry.catalogEntry.name));
        parts.push('.');
      }
      entry = entry.parent;
    }
    parts.reverse();
    return parts.slice(1).join('');
  }

  showContextPopover(entry, event, positionAdjustment) {
    const self = this;
    const $source = $(event.target);
    const offset = $source.offset();
    if (positionAdjustment) {
      offset.left += positionAdjustment.left;
      offset.top += positionAdjustment.top;
    }

    self.statsVisible(true);
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: self.catalogEntry
      },
      showInAssistEnabled: !!self.navigationSettings.rightAssist,
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
    huePubSub.subscribeOnce('context.popover.hidden', () => {
      self.statsVisible(false);
    });
  }

  triggerRefresh() {
    const self = this;
    self.catalogEntry.clearCache({ invalidate: self.invalidateOnRefresh(), cascade: true });
  }

  highlightInside(path) {
    const self = this;

    const searchEntry = () => {
      let foundEntry;
      self.entries().forEach(entry => {
        entry.highlight(false);
        if (entry.catalogEntry.name === path[0]) {
          foundEntry = entry;
        }
      });
      if (foundEntry) {
        if (foundEntry.expandable && !foundEntry.open()) {
          foundEntry.open(true);
        }

        window.setTimeout(() => {
          if (path.length > 1) {
            foundEntry.highlightInside(path.slice(1));
          } else {
            huePubSub.subscribeOnce('assist.db.scrollToComplete', () => {
              foundEntry.highlight(true);
              // Timeout is for animation effect
              window.setTimeout(() => {
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
        const subscription = self.loading.subscribe(newVal => {
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
  }

  loadEntries(callback) {
    const self = this;
    if (!self.expandable || self.loading()) {
      return;
    }
    self.loading(true);

    const loadEntriesDeferred = $.Deferred();

    const successCallback = sourceMeta => {
      self.entries([]);
      if (!sourceMeta.notFound) {
        self.catalogEntry
          .getChildren({ silenceErrors: self.navigationSettings.rightAssist })
          .done(catalogEntries => {
            self.hasErrors(false);
            self.loading(false);
            self.loaded = true;
            if (catalogEntries.length === 0) {
              self.entries([]);
              return;
            }
            const newEntries = [];
            catalogEntries.forEach(catalogEntry => {
              newEntries.push(self.createEntry(catalogEntry));
            });
            if (sourceMeta.type === 'array') {
              self.entries(newEntries);
              self.entries()[0].open(true);
            } else {
              self.entries(newEntries);
            }

            loadEntriesDeferred.resolve(newEntries);
            if (typeof callback === 'function') {
              callback();
            }
          })
          .fail(() => {
            self.loading(false);
            self.loaded = true;
            self.hasErrors(true);
          });

        if (!self.assistDbNamespace.nonSqlType) {
          self.catalogEntry.loadNavigatorMetaForChildren({
            silenceErrors: self.navigationSettings.rightAssist
          });
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

    const errorCallback = () => {
      self.hasErrors(true);
      self.loading(false);
      self.loaded = true;
      loadEntriesDeferred.resolve([]);
    };

    if (
      !self.navigationSettings.rightAssist &&
      HAS_OPTIMIZER &&
      (self.catalogEntry.isTable() || self.catalogEntry.isDatabase()) &&
      !self.assistDbNamespace.nonSqlType
    ) {
      self.catalogEntry.loadNavOptPopularityForChildren({ silenceErrors: true }).done(() => {
        loadEntriesDeferred.done(() => {
          if (!self.hasErrors()) {
            self.entries().forEach(entry => {
              if (entry.catalogEntry.navOptPopularity) {
                if (entry.catalogEntry.navOptPopularity.popularity) {
                  entry.popularity(entry.catalogEntry.navOptPopularity.popularity);
                } else if (entry.catalogEntry.navOptPopularity.column_count) {
                  entry.popularity(entry.catalogEntry.navOptPopularity.column_count);
                } else if (entry.catalogEntry.navOptPopularity.selectColumn) {
                  entry.popularity(entry.catalogEntry.navOptPopularity.selectColumn.columnCount);
                }
              }
            });
          }
        });
      });
    }

    self.catalogEntry
      .getSourceMeta({ silenceErrors: self.navigationSettings.rightAssist })
      .done(successCallback)
      .fail(errorCallback);
  }

  /**
   * @param {DataCatalogEntry} catalogEntry
   */
  createEntry(catalogEntry) {
    const self = this;
    return new AssistDbEntry(
      catalogEntry,
      self,
      self.assistDbNamespace,
      self.filter,
      self.i18n,
      self.navigationSettings
    );
  }

  getHierarchy() {
    const self = this;
    return self.catalogEntry.path.concat();
  }

  dblClick() {
    const self = this;
    if (self.catalogEntry.isTableOrView()) {
      huePubSub.publish('editor.insert.table.at.cursor', {
        name: self.getTableName(),
        database: self.getDatabaseName()
      });
    } else if (self.catalogEntry.isColumn()) {
      huePubSub.publish('editor.insert.column.at.cursor', {
        name: self.getColumnName(),
        table: self.getTableName(),
        database: self.getDatabaseName()
      });
    } else {
      huePubSub.publish('editor.insert.column.at.cursor', {
        name: self.getComplexName(),
        table: self.getTableName(),
        database: self.getDatabaseName()
      });
    }
  }

  explore(isSolr) {
    const self = this;
    if (isSolr) {
      huePubSub.publish('open.link', '/hue/dashboard/browse/' + self.catalogEntry.name);
    } else {
      huePubSub.publish(
        'open.link',
        '/hue/dashboard/browse/' +
          self.getDatabaseName() +
          '.' +
          self.getTableName() +
          '?engine=' +
          self.assistDbNamespace.sourceType
      );
    }
  }

  openInMetastore() {
    const self = this;
    let url;
    if (self.catalogEntry.isDatabase()) {
      url =
        '/metastore/tables/' +
        self.catalogEntry.name +
        '?source=' +
        self.catalogEntry.getSourceType() +
        '&namespace=' +
        self.catalogEntry.namespace.id;
    } else if (self.catalogEntry.isTableOrView()) {
      url =
        '/metastore/table/' +
        self.parent.catalogEntry.name +
        '/' +
        self.catalogEntry.name +
        '?source=' +
        self.catalogEntry.getSourceType() +
        '&namespace=' +
        self.catalogEntry.namespace.id;
    } else {
      return;
    }

    huePubSub.publish('open.link', url);
  }

  openInIndexer() {
    const self = this;
    const definitionName = self.catalogEntry.name;
    if (window.IS_NEW_INDEXER_ENABLED) {
      huePubSub.publish('open.link', '/indexer/indexes/' + definitionName);
    } else {
      const hash = '#edit/' + definitionName;
      if (
        window.location.pathname.startsWith('/hue/indexer') &&
        !window.location.pathname.startsWith('/hue/indexer/importer')
      ) {
        window.location.hash = hash;
      } else {
        huePubSub.subscribeOnce('app.gained.focus', app => {
          if (app === 'indexes') {
            window.setTimeout(() => {
              window.location.hash = hash;
            }, 0);
          }
        });
        huePubSub.publish('open.link', '/indexer');
      }
    }
  }

  toggleOpen() {
    const self = this;
    self.open(!self.open());
  }

  openItem() {
    const self = this;
    if (self.catalogEntry.isTableOrView()) {
      huePubSub.publish('assist.table.selected', {
        sourceType: self.assistDbNamespace.sourceType,
        namespace: self.assistDbNamespace.namespace,
        database: self.databaseName,
        name: self.catalogEntry.name
      });
    } else if (self.catalogEntry.isDatabase()) {
      huePubSub.publish('assist.database.selected', {
        sourceType: self.assistDbNamespace.sourceType,
        namespace: self.assistDbNamespace.namespace,
        name: self.catalogEntry.name
      });
    }
  }
}

export default AssistDbEntry;
