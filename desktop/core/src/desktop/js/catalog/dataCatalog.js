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
import localforage from 'localforage';

import CancellableJqPromise from 'api/cancellableJqPromise';
import catalogUtils from 'catalog/catalogUtils';
import DataCatalogEntry from 'catalog/dataCatalogEntry';
import GeneralDataCatalog from 'catalog/generalDataCatalog';
import MultiTableEntry from 'catalog/multiTableEntry';
import { getOptimizer, LOCAL_STRATEGY } from './optimizer/optimizer';

const STORAGE_POSTFIX = window.LOGGED_USERNAME;
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
      id += '_' + options.path.join('.');
    }
  } else if (options.paths && options.paths.length) {
    const pathSet = {};
    options.paths.forEach(path => {
      pathSet[path.join('.')] = true;
    });
    const uniquePaths = Object.keys(pathSet);
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
  const mergeAttribute = function (attributeName, ttl, promiseName) {
    if (
      storeEntry.version === DATA_CATALOG_VERSION &&
      storeEntry[attributeName] &&
      (!storeEntry[attributeName].hueTimestamp ||
        Date.now() - storeEntry[attributeName].hueTimestamp < ttl)
    ) {
      dataCatalogEntry[attributeName] = storeEntry[attributeName];
      if (promiseName) {
        dataCatalogEntry[promiseName] = $.Deferred()
          .resolve(dataCatalogEntry[attributeName])
          .promise();
      }
    }
  };

  mergeAttribute('definition', CACHEABLE_TTL.default);
  mergeAttribute('sourceMeta', CACHEABLE_TTL.default, 'sourceMetaPromise');
  mergeAttribute('analysis', CACHEABLE_TTL.default, 'analysisPromise');
  mergeAttribute('partitions', CACHEABLE_TTL.default, 'partitionsPromise');
  mergeAttribute('sample', CACHEABLE_TTL.default, 'samplePromise');
  mergeAttribute('navigatorMeta', CACHEABLE_TTL.default, 'navigatorMetaPromise');
  if (dataCatalogEntry.getConnector().optimizer !== LOCAL_STRATEGY) {
    mergeAttribute('optimizerMeta', CACHEABLE_TTL.optimizer, 'optimizerMetaPromise');
    mergeAttribute('optimizerPopularity', CACHEABLE_TTL.optimizer);
  }
};

/**
 * Helper function to fill a multi table catalog entry with cached metadata.
 *
 * @param {MultiTableEntry} multiTableCatalogEntry - The entry to fill
 * @param {Object} storeEntry - The cached version
 */
const mergeMultiTableEntry = function (multiTableCatalogEntry, storeEntry) {
  if (multiTableCatalogEntry.getConnector().optimizer === LOCAL_STRATEGY) {
    return;
  }
  const mergeAttribute = function (attributeName, ttl, promiseName) {
    if (
      storeEntry.version === DATA_CATALOG_VERSION &&
      storeEntry[attributeName] &&
      (!storeEntry[attributeName].hueTimestamp ||
        Date.now() - storeEntry[attributeName].hueTimestamp < ttl)
    ) {
      multiTableCatalogEntry[attributeName] = storeEntry[attributeName];
      if (promiseName) {
        multiTableCatalogEntry[promiseName] = $.Deferred()
          .resolve(multiTableCatalogEntry[attributeName])
          .promise();
      }
    }
  };

  mergeAttribute('topAggs', CACHEABLE_TTL.optimizer, 'topAggsPromise');
  mergeAttribute('topColumns', CACHEABLE_TTL.optimizer, 'topColumnsPromise');
  mergeAttribute('topFilters', CACHEABLE_TTL.optimizer, 'topFiltersPromise');
  mergeAttribute('topJoins', CACHEABLE_TTL.optimizer, 'topJoinsPromise');
};

export class DataCatalog {
  /**
   * @param {Connector} connector
   *
   * @constructor
   */
  constructor(connector) {
    const self = this;
    if (!connector || !connector.id) {
      throw new Error('DataCatalog created without connector or id');
    }
    self.connector = connector;

    self.entries = {};
    self.temporaryEntries = {};
    self.multiTableEntries = {};
    self.store = localforage.createInstance({
      name: 'HueDataCatalog_' + self.connector.id + '_' + STORAGE_POSTFIX
    });
    self.multiTableStore = localforage.createInstance({
      name: 'HueDataCatalog_' + self.connector.id + '_multiTable_' + STORAGE_POSTFIX
    });
  }

  /**
   * Disables the caching for subsequent operations, mainly used for test purposes
   */
  static disableCache() {
    cacheEnabled = false;
  }

  /**
   * Enables the cache for subsequent operations, mainly used for test purposes
   */
  static enableCache() {
    cacheEnabled = true;
  }

  static cacheEnabled() {
    return cacheEnabled;
  }

  /**
   * Returns true if the catalog can have Optimizer metadata
   *
   * @return {boolean}
   */
  canHaveOptimizerMeta() {
    return (
      HAS_OPTIMIZER &&
      this.connector &&
      this.connector.optimizer &&
      this.connector.optimizer !== 'off'
    );
  }

  /**
   * Clears the data catalog and cache for the given path and any children thereof.
   *
   * @param {ContextNamespace} [namespace] - The context namespace
   * @param {ContextCompute} [compute] - The context compute
   * @param {string[]} rootPath - The path to clear
   */
  clearStorageCascade(namespace, compute, rootPath) {
    const self = this;
    const deferred = $.Deferred();
    if (!namespace || !compute) {
      if (rootPath.length === 0) {
        self.entries = {};
        self.store.clear().then(deferred.resolve).catch(deferred.reject);
        return deferred.promise();
      }
      return deferred.reject().promise();
    }

    const keyPrefix = generateEntryCacheId({ namespace: namespace, path: rootPath });
    Object.keys(self.entries).forEach(key => {
      if (key.indexOf(keyPrefix) === 0) {
        delete self.entries[key];
      }
    });

    const deletePromises = [];
    const keysDeferred = $.Deferred();
    deletePromises.push(keysDeferred.promise());
    self.store
      .keys()
      .then(keys => {
        keys.forEach(key => {
          if (key.indexOf(keyPrefix) === 0) {
            const deleteDeferred = $.Deferred();
            deletePromises.push(deleteDeferred.promise());
            self.store.removeItem(key).then(deleteDeferred.resolve).catch(deleteDeferred.reject);
          }
        });
        keysDeferred.resolve();
      })
      .catch(keysDeferred.reject);

    return $.when.apply($, deletePromises);
  }

  /**
   * Updates the cache for the given entry
   *
   * @param {DataCatalogEntry} dataCatalogEntry
   * @return {Promise}
   */
  persistCatalogEntry(dataCatalogEntry) {
    const self = this;
    if (!cacheEnabled || CACHEABLE_TTL.default <= 0) {
      return $.Deferred().resolve().promise();
    }
    const deferred = $.Deferred();

    const identifier = generateEntryCacheId(dataCatalogEntry);

    self.store
      .setItem(identifier, {
        version: DATA_CATALOG_VERSION,
        definition: dataCatalogEntry.definition,
        sourceMeta: dataCatalogEntry.sourceMeta,
        analysis: dataCatalogEntry.analysis,
        partitions: dataCatalogEntry.partitions,
        sample: dataCatalogEntry.sample,
        navigatorMeta: dataCatalogEntry.navigatorMeta,
        optimizerMeta:
          this.connector.optimizer !== LOCAL_STRATEGY ? dataCatalogEntry.optimizerMeta : undefined,
        optimizerPopularity:
          this.connector.optimizer !== LOCAL_STRATEGY
            ? dataCatalogEntry.optimizerPopularity
            : undefined
      })
      .then(deferred.resolve)
      .catch(deferred.reject);

    return deferred.promise();
  }

  /**
   * Loads Navigator Optimizer popularity for multiple tables in one go.
   *
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {Connector} options.connector
   * @param {string[][]} options.paths
   * @param {boolean} [options.silenceErrors] - Default true
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellableJqPromise}
   */
  loadOptimizerPopularityForTables(options) {
    const deferred = $.Deferred();
    const cancellablePromises = [];
    let popularEntries = [];
    const pathsToLoad = [];

    options = catalogUtils.setSilencedErrors(options);

    const existingPromises = [];
    options.paths.forEach(path => {
      const existingDeferred = $.Deferred();
      this.getEntry({ namespace: options.namespace, compute: options.compute, path: path })
        .done(tableEntry => {
          if (tableEntry.optimizerPopularityForChildrenPromise) {
            tableEntry.optimizerPopularityForChildrenPromise
              .done(existingPopularEntries => {
                popularEntries = popularEntries.concat(existingPopularEntries);
                existingDeferred.resolve();
              })
              .fail(existingDeferred.reject);
          } else if (tableEntry.definition && tableEntry.definition.optimizerLoaded) {
            cancellablePromises.push(
              tableEntry
                .getChildren(options)
                .done(childEntries => {
                  childEntries.forEach(childEntry => {
                    if (childEntry.optimizerPopularity) {
                      popularEntries.push(childEntry);
                    }
                  });
                  existingDeferred.resolve();
                })
                .fail(existingDeferred.reject)
            );
          } else {
            pathsToLoad.push(path);
            existingDeferred.resolve();
          }
        })
        .fail(existingDeferred.reject);
      existingPromises.push(existingDeferred.promise());
    });

    $.when.apply($, existingPromises).always(() => {
      const loadDeferred = $.Deferred();
      if (pathsToLoad.length) {
        cancellablePromises.push(
          getOptimizer(this.connector)
            .fetchPopularity({
              silenceErrors: options.silenceErrors,
              paths: pathsToLoad
            })
            .done(data => {
              const perTable = {};

              const splitOptimizerValuesPerTable = function (listName) {
                if (data.values[listName]) {
                  data.values[listName].forEach(column => {
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
                splitOptimizerValuesPerTable('filterColumns');
                splitOptimizerValuesPerTable('groupbyColumns');
                splitOptimizerValuesPerTable('joinColumns');
                splitOptimizerValuesPerTable('orderbyColumns');
                splitOptimizerValuesPerTable('selectColumns');
              }

              const tablePromises = [];

              Object.keys(perTable).forEach(path => {
                const tableDeferred = $.Deferred();
                this.getEntry({
                  namespace: options.namespace,
                  compute: options.compute,
                  path: path
                })
                  .done(entry => {
                    cancellablePromises.push(
                      entry.trackedPromise(
                        'optimizerPopularityForChildrenPromise',
                        entry
                          .applyOptimizerResponseToChildren(perTable[path], options)
                          .done(entries => {
                            popularEntries = popularEntries.concat(entries);
                            tableDeferred.resolve();
                          })
                          .fail(tableDeferred.resolve)
                      )
                    );
                  })
                  .fail(tableDeferred.reject);
                tablePromises.push(tableDeferred.promise());
              });

              $.when.apply($, tablePromises).always(() => {
                loadDeferred.resolve();
              });
            })
            .fail(loadDeferred.reject)
        );
      } else {
        loadDeferred.resolve();
      }
      loadDeferred.always(() => {
        $.when
          .apply($, cancellablePromises)
          .done(() => {
            deferred.resolve(popularEntries);
          })
          .fail(deferred.reject);
      });
    });

    return catalogUtils.applyCancellable(
      new CancellableJqPromise(deferred, cancellablePromises),
      options
    );
  }

  /**
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {string|string[]} options.path
   * @return {DataCatalogEntry}
   */
  getKnownEntry(options) {
    const self = this;
    return self.entries[generateEntryCacheId(options)];
  }

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
   * @param {Connector} options.connector
   *
   * @param {Object[]} options.columns
   * @param {string} options.columns[].name
   * @param {string} options.columns[].type
   * @param {Object[][]} options.sample
   *
   * @return {Object}
   */
  addTemporaryTable(options) {
    const self = this;
    const tableDeferred = $.Deferred();
    const path = ['default', options.name];

    const identifiersToClean = [];

    const addEntryMeta = function (entry, sourceMeta) {
      entry.sourceMeta = sourceMeta || entry.definition;
      entry.sourceMetaPromise = $.Deferred().resolve(entry.sourceMeta).promise();
      entry.navigatorMeta = { comment: '' };
      entry.navigatorMetaPromise = $.Deferred().resolve(entry.navigatorMeta).promise();
      entry.analysis = { is_view: false };
      entry.analysisPromise = $.Deferred().resolve(entry.analysis).promise();
    };

    let removeTable = function () {}; // noop until actually added

    const sourceIdentifier = generateEntryCacheId({
      namespace: options.namespace,
      path: []
    });

    if (!self.temporaryEntries[sourceIdentifier]) {
      const sourceDeferred = $.Deferred();
      self.temporaryEntries[sourceIdentifier] = sourceDeferred.promise();
      const sourceEntry = new DataCatalogEntry({
        isTemporary: true,
        dataCatalog: self,
        namespace: options.namespace,
        compute: options.compute,
        path: [],
        definition: {
          index: 0,
          optimizerLoaded: true,
          type: 'source'
        }
      });
      addEntryMeta(sourceEntry);
      identifiersToClean.push(sourceIdentifier);
      sourceEntry.childrenPromise = $.Deferred().resolve([]).promise();
      sourceDeferred.resolve(sourceEntry);
    }

    self.temporaryEntries[sourceIdentifier].done(sourceEntry => {
      sourceEntry.getChildren().done(existingTemporaryDatabases => {
        const databaseIdentifier = generateEntryCacheId({
          namespace: options.namespace,
          path: ['default']
        });

        if (!self.temporaryEntries[databaseIdentifier]) {
          const databaseDeferred = $.Deferred();
          self.temporaryEntries[databaseIdentifier] = databaseDeferred.promise();
          const databaseEntry = new DataCatalogEntry({
            isTemporary: true,
            dataCatalog: self,
            namespace: options.namespace,
            compute: options.compute,
            path: ['default'],
            definition: {
              index: 0,
              optimizerLoaded: true,
              type: 'database'
            }
          });
          addEntryMeta(databaseEntry);
          identifiersToClean.push(databaseIdentifier);
          databaseEntry.childrenPromise = $.Deferred().resolve([]).promise();
          databaseDeferred.resolve(databaseEntry);
          existingTemporaryDatabases.push(databaseEntry);
        }

        self.temporaryEntries[databaseIdentifier].done(databaseEntry => {
          databaseEntry.getChildren().done(existingTemporaryTables => {
            const tableIdentifier = generateEntryCacheId({
              namespace: options.namespace,
              path: path
            });
            self.temporaryEntries[tableIdentifier] = tableDeferred.promise();
            identifiersToClean.push(tableIdentifier);

            const tableEntry = new DataCatalogEntry({
              isTemporary: true,
              dataCatalog: self,
              namespace: options.namespace,
              compute: options.compute,
              path: path,
              definition: {
                comment: '',
                index: 0,
                name: options.name,
                optimizerLoaded: true,
                type: 'table'
              }
            });
            existingTemporaryTables.push(tableEntry);
            const indexToDelete = existingTemporaryTables.length - 1;
            removeTable = function () {
              existingTemporaryTables.splice(indexToDelete, 1);
            };

            const childrenDeferred = $.Deferred();
            tableEntry.childrenPromise = childrenDeferred.promise();

            if (options.columns) {
              const childEntries = [];

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
              options.columns.forEach(column => {
                const columnPath = path.concat(column.name);
                const columnIdentifier = generateEntryCacheId({
                  namespace: options.namespace,
                  path: columnPath
                });

                const columnDeferred = $.Deferred();
                self.temporaryEntries[columnIdentifier] = columnDeferred.promise();
                identifiersToClean.push(columnIdentifier);

                const columnEntry = new DataCatalogEntry({
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
                  options.sample.forEach(sampleRow => {
                    columnEntry.sample.data.push([sampleRow[index - 1]]);
                  });
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

                childEntries.push(columnEntry);
              });
              childrenDeferred.resolve(childEntries);
            } else {
              childrenDeferred.resolve([]);
            }

            tableDeferred.resolve(tableEntry);
          });
        });
      });
    });

    return {
      delete: function () {
        removeTable();
        while (identifiersToClean.length) {
          delete self.entries[identifiersToClean.pop()];
        }
      }
    };
  }

  /**
   * @param {Object} options
   * @param {string|string[]} options.path
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {Object} [options.definition] - The initial definition if not already set on the entry
   * @param {boolean} [options.cachedOnly] - Default: false
   * @param {boolean} [options.temporaryOnly] - Default: false
   * // @param {Session} [options.session]
   * @return {Promise}
   */
  getEntry(options) {
    const self = this;
    const identifier = generateEntryCacheId(options);
    if (options.temporaryOnly) {
      return self.temporaryEntries[identifier] || $.Deferred().reject().promise();
    }
    if (self.entries[identifier]) {
      return self.entries[identifier];
    }

    const deferred = $.Deferred();
    self.entries[identifier] = deferred.promise();

    if (!cacheEnabled) {
      deferred
        .resolve(
          new DataCatalogEntry({
            dataCatalog: self,
            namespace: options.namespace,
            compute: options.compute,
            path: options.path,
            definition: options.definition
          })
        )
        .promise();
    } else {
      self.store
        .getItem(identifier)
        .then(storeEntry => {
          const definition = storeEntry ? storeEntry.definition : options.definition;
          const entry = new DataCatalogEntry({
            dataCatalog: self,
            namespace: options.namespace,
            compute: options.compute,
            path: options.path,
            definition: definition
          });
          if (storeEntry) {
            mergeEntry(entry, storeEntry);
          } else if (!options.cachedOnly && options.definition) {
            entry.saveLater();
          }
          deferred.resolve(entry);
        })
        .catch(error => {
          console.warn(error);
          const entry = new DataCatalogEntry({
            dataCatalog: self,
            namespace: options.namespace,
            compute: options.compute,
            path: options.path,
            definition: options.definition
          });
          if (!options.cachedOnly && options.definition) {
            entry.saveLater();
          }
          deferred.resolve(entry);
        });
    }

    return self.entries[identifier];
  }

  /**
   *
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {Connector} options.connector
   * @param {string[][]} options.paths
   *
   * @return {Promise}
   */
  getMultiTableEntry(options) {
    const self = this;
    const identifier = generateEntryCacheId(options);
    if (self.multiTableEntries[identifier]) {
      return self.multiTableEntries[identifier];
    }

    const deferred = $.Deferred();
    self.multiTableEntries[identifier] = deferred.promise();

    if (!cacheEnabled) {
      deferred
        .resolve(
          new MultiTableEntry({
            identifier: identifier,
            dataCatalog: self,
            paths: options.paths
          })
        )
        .promise();
    } else {
      self.multiTableStore
        .getItem(identifier)
        .then(storeEntry => {
          const entry = new MultiTableEntry({
            identifier: identifier,
            dataCatalog: self,
            paths: options.paths
          });
          if (storeEntry) {
            mergeMultiTableEntry(entry, storeEntry);
          }
          deferred.resolve(entry);
        })
        .catch(error => {
          console.warn(error);
          deferred.resolve(
            new MultiTableEntry({
              identifier: identifier,
              dataCatalog: self,
              paths: options.paths
            })
          );
        });
    }

    return self.multiTableEntries[identifier];
  }

  /**
   * Updates the cache for the given multi tableentry
   *
   * @param {MultiTableEntry} multiTableEntry
   * @return {Promise}
   */
  persistMultiTableEntry(multiTableEntry) {
    const self = this;
    if (
      !cacheEnabled ||
      CACHEABLE_TTL.default <= 0 ||
      CACHEABLE_TTL.optimizer <= 0 ||
      multiTableEntry.getConnector().optimizer === LOCAL_STRATEGY
    ) {
      return $.Deferred().resolve().promise();
    }
    const deferred = $.Deferred();
    self.multiTableStore
      .setItem(multiTableEntry.identifier, {
        version: DATA_CATALOG_VERSION,
        topAggs: multiTableEntry.topAggs,
        topColumns: multiTableEntry.topColumns,
        topFilters: multiTableEntry.topFilters,
        topJoins: multiTableEntry.topJoins
      })
      .then(deferred.resolve)
      .catch(deferred.reject);
    return deferred.promise();
  }
}

const generalDataCatalog = new GeneralDataCatalog();
const sourceBoundCatalogs = {};

/**
 * Helper function to get the DataCatalog instance for a given data source.
 *
 * @param {Connector} connector
 *
 * @return {DataCatalog}
 */
const getCatalog = function (connector) {
  if (!connector || !connector.id) {
    throw new Error('getCatalog called without connector with id');
  }
  return (
    sourceBoundCatalogs[connector.id] ||
    (sourceBoundCatalogs[connector.id] = new DataCatalog(connector))
  );
};

export default {
  /**
   * Adds a detached (temporary) entry to the data catalog. This would allow autocomplete etc. of tables that haven't
   * been created yet.
   *
   * Calling this returns a handle that allows deletion of any created entries by calling delete() on the handle.
   *
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {Connector} options.connector
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
    return getCatalog(options.connector).addTemporaryTable(options);
  },

  /**
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {Connector} options.connector
   * @param {string|string[]} options.path
   * @param {Object} [options.definition] - Optional initial definition
   * @param {boolean} [options.cachedOnly] - Default: false
   * @param {boolean} [options.temporaryOnly] - Default: false
   *
   * @return {JQuery.Promise<DataCatalogEntry>}
   */
  getEntry: function (options) {
    return getCatalog(options.connector).getEntry(options);
  },

  /**
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {Connector} options.connector
   * @param {string[][]} options.paths
   *
   * @return {Promise}
   */
  getMultiTableEntry: function (options) {
    return getCatalog(options.connector).getMultiTableEntry(options);
  },

  /**
   * This can be used as a shorthand function to get the child entries of the given path. Same as first calling
   * getEntry then getChildren.
   *
   * @param {Object} options
   * @param {ContextNamespace} options.namespace - The context namespace
   * @param {ContextCompute} options.compute - The context compute
   * @param {Connector} options.connector
   * @param {string|string[]} options.path
   * @param {Object} [options.definition] - Optional initial definition of the parent entry
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.temporaryOnly]
   * @param {boolean} [options.refreshCache]
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellableJqPromise}
   */
  getChildren: function (options) {
    const deferred = $.Deferred();
    const cancellablePromises = [];
    getCatalog(options.connector)
      .getEntry(options)
      .done(entry => {
        cancellablePromises.push(
          entry.getChildren(options).done(deferred.resolve).fail(deferred.reject)
        );
      })
      .fail(deferred.reject);
    return new CancellableJqPromise(deferred, undefined, cancellablePromises);
  },

  /**
   * @param {Connector} connector
   *
   * @return {DataCatalog}
   */
  getCatalog: getCatalog,

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
    cacheEnabled = true;
  },

  disableCache: function () {
    cacheEnabled = false;
  },

  applyCancellable: catalogUtils.applyCancellable
};
