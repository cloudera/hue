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

import $ from 'jquery'
import localforage from 'localforage'

import CancellablePromise from '../api/cancellablePromise'
import catalogUtils from './catalogUtils'
import DataCatalogEntry from './dataCatalogEntry'
import GeneralDataCatalog from './generalDataCatalog'
import MultiTableEntry from './multiTableEntry'

const STORAGE_POSTFIX = LOGGED_USERNAME;
const DATA_CATALOG_VERSION = 5;
let cacheEnabled = true;

/**
 * Creates a cache identifier given a namespace and path(s)
 *
 * @param {Object|DataCatalogEntry} options
 * @param {Object} options.namespace
 * @param {string} options.namespace.id
 * @param {string[]} [options.path]
 * @param {string[][]} [options.paths]
 * @return {string}
 */
const generateEntryCacheId = function (options) {
  let id = options.namespace.id;
  if (options.path) {
    if (typeof options.path === 'string') {
      id += '_' + options.path;
    } else if (options.path.length) {
      id +='_' + options.path.join('.');
    }
  } else if (options.paths && options.paths.length) {
    let pathSet = {};
    options.paths.forEach(function (path) {
      pathSet[path.join('.')] = true;
    });
    let uniquePaths = Object.keys(pathSet);
    uniquePaths.sort();
    id += '_' + uniquePaths.join(',');
  }
  return id;
};

/**
 * Helper function to fill a catalog entry with cached metadata.
 *
 * @param {DataCatalogEntry} dataCatalogEntry - The entry to fill
 * @param {Object} storeEntry - The cached version
 */
const mergeEntry = function (dataCatalogEntry, storeEntry) {
  let mergeAttribute = function (attributeName, ttl, promiseName) {
    if (storeEntry.version === DATA_CATALOG_VERSION && storeEntry[attributeName] && (!storeEntry[attributeName].hueTimestamp || (Date.now() - storeEntry[attributeName].hueTimestamp) < ttl)) {
      dataCatalogEntry[attributeName] = storeEntry[attributeName];
      if (promiseName) {
        dataCatalogEntry[promiseName] = $.Deferred().resolve(dataCatalogEntry[attributeName]).promise();
      }
    }
  };

  mergeAttribute('definition', CACHEABLE_TTL.default);
  mergeAttribute('sourceMeta', CACHEABLE_TTL.default, 'sourceMetaPromise');
  mergeAttribute('analysis', CACHEABLE_TTL.default, 'analysisPromise');
  mergeAttribute('partitions', CACHEABLE_TTL.default, 'partitionsPromise');
  mergeAttribute('sample', CACHEABLE_TTL.default, 'samplePromise');
  mergeAttribute('navigatorMeta', CACHEABLE_TTL.default, 'navigatorMetaPromise');
  mergeAttribute('navOptMeta', CACHEABLE_TTL.optimizer, 'navOptMetaPromise');
  mergeAttribute('navOptPopularity', CACHEABLE_TTL.optimizer);
};


/**
 * Helper function to fill a multi table catalog entry with cached metadata.
 *
 * @param {MultiTableEntry} multiTableCatalogEntry - The entry to fill
 * @param {Object} storeEntry - The cached version
 */
const mergeMultiTableEntry = function (multiTableCatalogEntry, storeEntry) {
  let mergeAttribute = function (attributeName, ttl, promiseName) {
    if (storeEntry.version === DATA_CATALOG_VERSION && storeEntry[attributeName] && (!storeEntry[attributeName].hueTimestamp || (Date.now() - storeEntry[attributeName].hueTimestamp) < ttl)) {
      multiTableCatalogEntry[attributeName] = storeEntry[attributeName];
      if (promiseName) {
        multiTableCatalogEntry[promiseName] = $.Deferred().resolve(multiTableCatalogEntry[attributeName]).promise();
      }
    }
  };

  mergeAttribute('topAggs', CACHEABLE_TTL.optimizer, 'topAggsPromise');
  mergeAttribute('topColumns', CACHEABLE_TTL.optimizer, 'topColumnsPromise');
  mergeAttribute('topFilters', CACHEABLE_TTL.optimizer, 'topFiltersPromise');
  mergeAttribute('topJoins', CACHEABLE_TTL.optimizer, 'topJoinsPromise');
};

class DataCatalog {

  /**
   * @param {string} sourceType
   *
   * @constructor
   */
  constructor(sourceType) {
    let self = this;
    self.sourceType = sourceType;
    self.entries = {};
    self.temporaryEntries = {};
    self.multiTableEntries = {};
    self.store = localforage.createInstance({
      name: 'HueDataCatalog_' + self.sourceType + '_' + STORAGE_POSTFIX
    });
    self.multiTableStore = localforage.createInstance({
      name: 'HueDataCatalog_' + self.sourceType + '_multiTable_' + STORAGE_POSTFIX
    });
  }

  /**
   * Disables the caching for subsequent operations, mainly used for test purposes
   */
  static disableCache() {
    cacheEnabled = false;
  };

  /**
   * Enables the cache for subsequent operations, mainly used for test purposes
   */
  static enableCache() {
    cacheEnabled = true;
  };

  /**
   * Returns true if the catalog can have NavOpt metadata
   *
   * @return {boolean}
   */
  canHaveNavOptMetadata() {
    let self = this;
    return HAS_OPTIMIZER && (self.sourceType === 'hive' || self.sourceType === 'impala');
  };

  /**
   * Clears the data catalog and cache for the given path and any children thereof.
   *
   * @param {ContextNamespace} [namespace] - The context namespace
   * @param {ContextCompute} [compute] - The context compute
   * @param {string[]} rootPath - The path to clear
   */
  clearStorageCascade(namespace, compute, rootPath) {
    let self = this;
    let deferred = $.Deferred();
    if (!namespace || !compute) {
      if (rootPath.length === 0) {
        self.entries = {};
        self.store.clear().then(deferred.resolve).catch(deferred.reject);
        return deferred.promise();
      }
      return deferred.reject().promise();
    }

    let keyPrefix = generateEntryCacheId({ namespace: namespace, path: rootPath });
    Object.keys(self.entries).forEach(function (key) {
      if (key.indexOf(keyPrefix) === 0) {
        delete self.entries[key];
      }
    });

    let deletePromises = [];
    let keysDeferred = $.Deferred();
    deletePromises.push(keysDeferred.promise());
    self.store.keys().then(function (keys) {
      keys.forEach(function (key) {
        if (key.indexOf(keyPrefix) === 0) {
          let deleteDeferred = $.Deferred();
          deletePromises.push(deleteDeferred.promise());
          self.store.removeItem(key).then(deleteDeferred.resolve).catch(deleteDeferred.reject);
        }
      });
      keysDeferred.resolve();
    }).catch(keysDeferred.reject);

    return $.when.apply($, deletePromises);
  };

  /**
   * Updates the cache for the given entry
   *
   * @param {DataCatalogEntry} dataCatalogEntry
   * @return {Promise}
   */
  persistCatalogEntry(dataCatalogEntry) {
    let self = this;
    if (!cacheEnabled || CACHEABLE_TTL.default <= 0) {
      return $.Deferred().resolve().promise();
    }
    let deferred = $.Deferred();

    let identifier = generateEntryCacheId(dataCatalogEntry);

    self.store.setItem(identifier, {
      version: DATA_CATALOG_VERSION,
      definition: dataCatalogEntry.definition,
      sourceMeta: dataCatalogEntry.sourceMeta,
      analysis: dataCatalogEntry.analysis,
      partitions: dataCatalogEntry.partitions,
      sample: dataCatalogEntry.sample,
      navigatorMeta: dataCatalogEntry.navigatorMeta,
      navOptMeta:  dataCatalogEntry.navOptMeta,
      navOptPopularity: dataCatalogEntry.navOptPopularity,
    }).then(deferred.resolve).catch(deferred.reject);

    return deferred.promise();
  };

  /**
   * Loads Navigator Optimizer popularity for multiple tables in one go.
   *
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {string[][]} options.paths
   * @param {boolean} [options.silenceErrors] - Default true
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellablePromise}
   */
  loadNavOptPopularityForTables(options) {
    let self = this;
    let deferred = $.Deferred();
    let cancellablePromises = [];
    let popularEntries = [];
    let pathsToLoad = [];

    options = catalogUtils.setSilencedErrors(options);

    let existingPromises = [];
    options.paths.forEach(function (path) {
      let existingDeferred = $.Deferred();
      self.getEntry({ namespace: options.namespace, compute: options.compute, path: path }).done(function (tableEntry) {
        if (tableEntry.navOptPopularityForChildrenPromise) {
          tableEntry.navOptPopularityForChildrenPromise.done(function (existingPopularEntries) {
            popularEntries = popularEntries.concat(existingPopularEntries);
            existingDeferred.resolve();
          }).fail(existingDeferred.reject);
        } else if (tableEntry.definition && tableEntry.definition.navOptLoaded) {
          cancellablePromises.push(tableEntry.getChildren(options).done(function (childEntries) {
            childEntries.forEach(function (childEntry) {
              if (childEntry.navOptPopularity) {
                popularEntries.push(childEntry);
              }
            });
            existingDeferred.resolve();
          }).fail(existingDeferred.reject));
        } else {
          pathsToLoad.push(path);
          existingDeferred.resolve();
        }
      }).fail(existingDeferred.reject);
      existingPromises.push(existingDeferred.promise());
    });

    $.when.apply($, existingPromises).always(function () {
      let loadDeferred = $.Deferred();
      if (pathsToLoad.length) {
        cancellablePromises.push(window.apiHelper.fetchNavOptPopularity({
          silenceErrors: options.silenceErrors,
          paths: pathsToLoad
        }).done(function (data) {
          let perTable = {};

          let splitNavOptValuesPerTable = function (listName) {
            if (data.values[listName]) {
              data.values[listName].forEach(function (column) {
                let tableMeta = perTable[column.dbName + '.' + column.tableName];
                if (!tableMeta) {
                  tableMeta = { values: [] };
                  perTable[column.dbName + '.' + column.tableName] = tableMeta;
                }
                if (!tableMeta.values[listName]) {
                  tableMeta.values[listName] = [];
                }
                tableMeta.values[listName].push(column);
              });
            }
          };

          if (data.values) {
            splitNavOptValuesPerTable('filterColumns');
            splitNavOptValuesPerTable('groupbyColumns');
            splitNavOptValuesPerTable('joinColumns');
            splitNavOptValuesPerTable('orderbyColumns');
            splitNavOptValuesPerTable('selectColumns');
          }

          let tablePromises = [];

          Object.keys(perTable).forEach(function (path) {
            let tableDeferred = $.Deferred();
            self.getEntry({ namespace: options.namespace, compute: options.compute, path: path }).done(function (entry) {
              cancellablePromises.push(entry.trackedPromise('navOptPopularityForChildrenPromise', entry.applyNavOptResponseToChildren(perTable[path], options).done(function (entries) {
                popularEntries = popularEntries.concat(entries);
                tableDeferred.resolve();
              }).fail(tableDeferred.resolve)));
            }).fail(tableDeferred.reject);
            tablePromises.push(tableDeferred.promise());
          });

          $.when.apply($, tablePromises).always(function () {
            loadDeferred.resolve();
          });
        }).fail(loadDeferred.reject));
      } else {
        loadDeferred.resolve();
      }
      loadDeferred.always(function () {
        $.when.apply($, cancellablePromises).done(function () {
          deferred.resolve(popularEntries);
        }).fail(deferred.reject);
      });
    });

    return catalogUtils.applyCancellable(new CancellablePromise(deferred, cancellablePromises), options);
  };

  /**
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {string|string[]} options.path
   * @return {DataCatalogEntry}
   */
  getKnownEntry(options) {
    let self = this;
    return self.entries[generateEntryCacheId(options)];
  };

  /**
   * Adds a temporary table to the data catalog. This would allow autocomplete etc. of tables that haven't
   * been created yet.
   *
   * Calling this returns a handle that allows deletion of any created entries by calling delete() on the handle.
   *
   * @param {Object} options
   * @param {string} options.name
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   *
   * @param {Object[]} options.columns
   * @param {string} options.columns[].name
   * @param {string} options.columns[].type
   * @param {Object[][]} options.sample
   *
   * @return {Object}
   */
  addTemporaryTable(options) {
    let self = this;
    let tableDeferred = $.Deferred();
    let path = ['default', options.name];

    let identifiersToClean = [];

    let addEntryMeta = function (entry, sourceMeta) {
      entry.sourceMeta = sourceMeta || entry.definition;
      entry.sourceMetaPromise = $.Deferred().resolve(entry.sourceMeta).promise();
      entry.navigatorMeta = { comment: '' };
      entry.navigatorMetaPromise = $.Deferred().resolve(entry.navigatorMeta).promise();
      entry.analysis = { is_view: false };
      entry.analysisPromise = $.Deferred().resolve(entry.analysis).promise();
    };

    let removeTable = function () {}; // noop until actually added

    let sourceIdentifier = generateEntryCacheId({
      namespace: options.namespace,
      path: []
    });

    if (!self.temporaryEntries[sourceIdentifier]) {
      let sourceDeferred = $.Deferred();
      self.temporaryEntries[sourceIdentifier] = sourceDeferred.promise();
      let sourceEntry = new DataCatalogEntry({
        isTemporary: true,
        dataCatalog: self,
        namespace: options.namespace,
        compute: options.compute,
        path: [],
        definition: {
          index: 0,
          navOptLoaded: true,
          type: 'source'
        }
      });
      addEntryMeta(sourceEntry);
      identifiersToClean.push(sourceIdentifier);
      sourceEntry.childrenPromise = $.Deferred().resolve([]).promise();
      sourceDeferred.resolve(sourceEntry);
    }

    self.temporaryEntries[sourceIdentifier].done(function (sourceEntry) {
      sourceEntry.getChildren().done(function (existingTemporaryDatabases) {
        let databaseIdentifier = generateEntryCacheId({
          namespace: options.namespace,
          path: ['default']
        });

        if (!self.temporaryEntries[databaseIdentifier]) {
          let databaseDeferred = $.Deferred();
          self.temporaryEntries[databaseIdentifier] = databaseDeferred.promise();
          let databaseEntry = new DataCatalogEntry({
            isTemporary: true,
            dataCatalog: self,
            namespace: options.namespace,
            compute: options.compute,
            path: ['default'],
            definition: {
              index: 0,
              navOptLoaded: true,
              type: 'database'
            }
          });
          addEntryMeta(databaseEntry);
          identifiersToClean.push(databaseIdentifier);
          databaseEntry.childrenPromise = $.Deferred().resolve([]).promise();
          databaseDeferred.resolve(databaseEntry);
          existingTemporaryDatabases.push(databaseEntry);
        }

        self.temporaryEntries[databaseIdentifier].done(function (databaseEntry) {
          databaseEntry.getChildren().done(function (existingTemporaryTables) {
            let tableIdentifier = generateEntryCacheId({
              namespace: options.namespace,
              path: path
            });
            self.temporaryEntries[tableIdentifier] = tableDeferred.promise();
            identifiersToClean.push(tableIdentifier);

            let tableEntry = new DataCatalogEntry({
              isTemporary: true,
              dataCatalog: self,
              namespace: options.namespace,
              compute: options.compute,
              path: path,
              definition: {
                comment: '',
                index: 0,
                name: options.name,
                navOptLoaded: true,
                type: 'table'
              }
            });
            existingTemporaryTables.push(tableEntry);
            let indexToDelete = existingTemporaryTables.length - 1;
            removeTable = function () { existingTemporaryTables.splice(indexToDelete, 1); };

            let childrenDeferred = $.Deferred();
            tableEntry.childrenPromise = childrenDeferred.promise();

            if (options.columns) {
              let childEntries = [];

              addEntryMeta(tableEntry, {
                columns: [],
                extended_columns: [],
                comment: '',
                notFound: false,
                is_view: false
              });

              tableEntry.sample = {
                data: options.sample || [],
                meta: tableEntry.sourceMeta.extended_columns
              };
              tableEntry.samplePromise = $.Deferred().resolve(tableEntry.sample).promise();

              let index = 0;
              options.columns.forEach(function (column) {
                let columnPath = path.concat(column.name);
                let columnIdentifier = generateEntryCacheId({
                  namespace: options.namespace,
                  path: columnPath
                });

                let columnDeferred = $.Deferred();
                self.temporaryEntries[columnIdentifier] = columnDeferred.promise();
                identifiersToClean.push(columnIdentifier);

                let columnEntry = new DataCatalogEntry({
                  isTemporary: true,
                  dataCatalog: self,
                  namespace: options.namespace,
                  compute: options.compute,
                  path: columnPath,
                  definition: {
                    comment: '',
                    index: index++,
                    name: column.name,
                    partitionKey: false,
                    type: column.type
                  }
                });

                columnEntry.sample = {
                  data: [],
                  meta: column
                };
                if (options.sample) {
                  options.sample.forEach(function (sampleRow) {
                    columnEntry.sample.data.push([sampleRow[index - 1]]);
                  })
                }
                columnEntry.samplePromise = $.Deferred().resolve(columnEntry.sample).promise();

                tableEntry.sourceMeta.columns.push(column.name);
                tableEntry.sourceMeta.extended_columns.push(columnEntry.definition);
                columnDeferred.resolve(columnEntry);
                addEntryMeta(columnEntry, {
                  comment: '',
                  name: column.name,
                  notFount: false,
                  sample: [],
                  type: column.type
                });

                childEntries.push(columnEntry)
              });
              childrenDeferred.resolve(childEntries);
            } else {
              childrenDeferred.resolve([]);
            }

            tableDeferred.resolve(tableEntry);
          });
        });
      })


    });

    return {
      delete: function () {
        removeTable();
        while (identifiersToClean.length) {
          delete self.entries[identifiersToClean.pop()];
        }
      }
    }
  };

  /**
   * @param {Object} options
   * @param {string|string[]} options.path
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {Object} [options.definition] - The initial definition if not already set on the entry
   * @param {boolean} [options.cachedOnly] - Default: false
   * @param {boolean} [options.temporaryOnly] - Default: false
   * @return {Promise}
   */
  getEntry(options) {
    let self = this;
    let identifier = generateEntryCacheId(options);
    if (options.temporaryOnly) {
      return self.temporaryEntries[identifier] || $.Deferred().reject().promise();
    }
    if (self.entries[identifier]) {
      return self.entries[identifier];
    }

    let deferred = $.Deferred();
    self.entries[identifier] = deferred.promise();

    if (!cacheEnabled) {
      deferred.resolve(new DataCatalogEntry({ dataCatalog: self, namespace: options.namespace, compute: options.compute, path: options.path, definition: options.definition })).promise();
    } else {
      self.store.getItem(identifier).then(function (storeEntry) {
        let definition = storeEntry ? storeEntry.definition : options.definition;
        let entry = new DataCatalogEntry({ dataCatalog: self, namespace: options.namespace, compute: options.compute, path: options.path, definition: definition });
        if (storeEntry) {
          mergeEntry(entry, storeEntry);
        } else if (!options.cachedOnly && options.definition) {
          entry.saveLater();
        }
        deferred.resolve(entry);
      }).catch(function (error) {
        console.warn(error);
        let entry = new DataCatalogEntry({ dataCatalog: self, namespace: options.namespace, compute: options.compute, path: options.path, definition: options.definition });
        if (!options.cachedOnly && options.definition) {
          entry.saveLater();
        }
        deferred.resolve(entry);
      })
    }

    return self.entries[identifier];
  };

  /**
   *
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {string[][]} options.paths
   *
   * @return {Promise}
   */
  getMultiTableEntry(options) {
    let self = this;
    let identifier = generateEntryCacheId(options);
    if (self.multiTableEntries[identifier]) {
      return self.multiTableEntries[identifier];
    }

    let deferred = $.Deferred();
    self.multiTableEntries[identifier] = deferred.promise();

    if (!cacheEnabled) {
      deferred.resolve(new MultiTableEntry({ identifier: identifier, dataCatalog: self, paths: options.paths })).promise();
    } else {
      self.multiTableStore.getItem(identifier).then(function (storeEntry) {
        let entry = new MultiTableEntry({ identifier: identifier, dataCatalog: self, paths: options.paths });
        if (storeEntry) {
          mergeMultiTableEntry(entry, storeEntry);
        }
        deferred.resolve(entry);
      }).catch(function (error) {
        console.warn(error);
        deferred.resolve(new MultiTableEntry({ identifier: identifier, dataCatalog: self, paths: options.paths }));
      })
    }

    return self.multiTableEntries[identifier];
  };

  /**
   * Updates the cache for the given multi tableentry
   *
   * @param {MultiTableEntry} multiTableEntry
   * @return {Promise}
   */
  persistMultiTableEntry(multiTableEntry) {
    let self = this;
    if (!cacheEnabled || CACHEABLE_TTL.default <= 0 || CACHEABLE_TTL.optimizer <= 0) {
      return $.Deferred().resolve().promise();
    }
    let deferred = $.Deferred();
    self.multiTableStore.setItem(multiTableEntry.identifier, {
      version: DATA_CATALOG_VERSION,
      topAggs: multiTableEntry.topAggs,
      topColumns: multiTableEntry.topColumns,
      topFilters: multiTableEntry.topFilters,
      topJoins: multiTableEntry.topJoins,
    }).then(deferred.resolve).catch(deferred.reject);
    return deferred.promise();
  };
}

let generalDataCatalog = new GeneralDataCatalog();
let sourceBoundCatalogs = {};

/**
 * Helper function to get the DataCatalog instance for a given data source.
 *
 * @param {string} sourceType
 * @return {DataCatalog}
 */
const getCatalog = function (sourceType) {
  if (!sourceType) {
    throw new Error('getCatalog called without sourceType');
  }
  return sourceBoundCatalogs[sourceType] || (sourceBoundCatalogs[sourceType] = new DataCatalog(sourceType));
};

export default {

  /**
   * Adds a detached (temporary) entry to the data catalog. This would allow autocomplete etc. of tables that haven't
   * been created yet.
   *
   * Calling this returns a handle that allows deletion of any created entries by calling delete() on the handle.
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {string} options.name
   *
   * @param {Object[]} options.columns
   * @param {string} options.columns[].name
   * @param {string} options.columns[].type
   * @param {Object[][]} options.sample
   *
   * @return {Object}
   */
  addTemporaryTable: function (options) {
    return getCatalog(options.sourceType).addTemporaryTable(options);
  },

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {string|string[]} options.path
   * @param {Object} [options.definition] - Optional initial definition
   * @param {boolean} [options.temporaryOnly] - Default: false
   *
   * @return {Promise}
   */
  getEntry: function (options) {
    return getCatalog(options.sourceType).getEntry(options);
  },

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {string[][]} options.paths
   *
   * @return {Promise}
   */
  getMultiTableEntry: function (options) {
    return getCatalog(options.sourceType).getMultiTableEntry(options);
  },

  /**
   * This can be used as a shorthand function to get the child entries of the given path. Same as first calling
   * getEntry then getChildren.
   *
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {string|string[]} options.path
   * @param {Object} [options.definition] - Optional initial definition of the parent entry
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellablePromise}
   */
  getChildren:  function(options) {
    let deferred = $.Deferred();
    let cancellablePromises = [];
    getCatalog(options.sourceType).getEntry(options).done(function (entry) {
      cancellablePromises.push(entry.getChildren(options).done(deferred.resolve).fail(deferred.reject));
    }).fail(deferred.reject);
    return new CancellablePromise(deferred, undefined, cancellablePromises);
  },

  /**
   * @param {string} sourceType
   *
   * @return {DataCatalog}
   */
  getCatalog : getCatalog,

  /**
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.refreshCache]
   *
   * @return {Promise}
   */
  getAllNavigatorTags: generalDataCatalog.getAllNavigatorTags.bind(generalDataCatalog),

  /**
   * @param {string[]} tagsToAdd
   * @param {string[]} tagsToRemove
   */
  updateAllNavigatorTags: generalDataCatalog.updateAllNavigatorTags.bind(generalDataCatalog),

  enableCache: function () {
    cacheEnabled = true
  },

  disableCache: function () {
    cacheEnabled = false;
  },

  applyCancellable: catalogUtils.applyCancellable
};

