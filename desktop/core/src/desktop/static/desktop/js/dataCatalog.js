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

var DataCatalog = (function () {

  var STORAGE_POSTFIX = LOGGED_USERNAME;

  var DATA_CATALOG_VERSION = 5;

  var cacheEnabled = true;

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
  var generateEntryCacheId = function (options) {
    var id = options.namespace.id;
    if (options.path) {
      if (typeof options.path === 'string') {
        id += '_' + options.path;
      } else if (options.path.length) {
        id +='_' + options.path.join('.');
      }
    } else if (options.paths && options.paths.length) {
      var pathSet = {};
      options.paths.forEach(function (path) {
        pathSet[path.join('.')] = true;
      });
      var uniquePaths = Object.keys(pathSet);
      uniquePaths.sort();
      id += '_' + uniquePaths.join(',');
    }
    return id;
  };

  /**
   * Helper function that adds sets the silence errors option to true if not specified
   *
   * @param {Object} [options]
   * @return {Object}
   */
  var setSilencedErrors = function (options) {
    if (!options) {
      options = {};
    }
    if (typeof options.silenceErrors === 'undefined') {
      options.silenceErrors = true;
    }
    return options;
  };

  /**
   * Helper function to apply the cancellable option to an existing or new promise
   *
   * @param {CancellablePromise} [promise]
   * @param {Object} [options]
   * @param {boolean} [options.cancellable] - Default false
   *
   * @return {CancellablePromise}
   */
  var applyCancellable = function (promise, options) {
    if (promise && promise.preventCancel && (!options || !options.cancellable)) {
      promise.preventCancel();
    }
    return promise;
  };

  /**
   * Wrapper function around ApiHelper calls, it will also save the entry on success.
   *
   * @param {string} apiHelperFunction - The name of the ApiHelper function to call
   * @param {string} attributeName - The attribute to set
   * @param {DataCatalogEntry|MultiTableEntry} entry - The catalog entry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   */
  var fetchAndSave = function (apiHelperFunction, attributeName, entry, apiOptions) {
    return ApiHelper.getInstance()[apiHelperFunction]({
      sourceType: entry.dataCatalog.sourceType,
      compute: entry.compute,
      path: entry.path, // Set for DataCatalogEntry
      paths: entry.paths, // Set for MultiTableEntry
      silenceErrors: apiOptions && apiOptions.silenceErrors,
      isView: entry.isView && entry.isView() // MultiTable entries don't have this property
    }).done(function (data) {
      entry[attributeName] = data;
      entry.saveLater();
    })
  };

  var DataCatalog = (function () {
    /**
     * @param {string} sourceType
     *
     * @constructor
     */
    function DataCatalog(sourceType) {
      var self = this;
      self.sourceType = sourceType;
      self.entries = {};
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
    DataCatalog.prototype.disableCache = function () {
      cacheEnabled = false;
    };

    /**
     * Enables the cache for subsequent operations, mainly used for test purposes
     */
    DataCatalog.prototype.enableCache = function () {
      cacheEnabled = true;
    };

    /**
     * Returns true if the catalog can have NavOpt metadata
     *
     * @return {boolean}
     */
    DataCatalog.prototype.canHaveNavOptMetadata = function () {
      var self = this;
      return HAS_OPTIMIZER && (self.sourceType === 'hive' || self.sourceType === 'impala');
    };

    /**
     * Clears the data catalog and cache for the given path and any children thereof.
     *
     * @param {ContextNamespace} [namespace] - The context namespace
     * @param {ContextCompute} [compute] - The context compute
     * @param {string[]} rootPath - The path to clear
     */
    DataCatalog.prototype.clearStorageCascade = function (namespace, compute, rootPath) {
      var self = this;
      var deferred = $.Deferred();
      if (!namespace || !compute) {
        if (rootPath.length === 0) {
          self.entries = {};
          self.store.clear().then(deferred.resolve).catch(deferred.reject);
          return deferred.promise();
        }
        return deferred.reject().promise();
      }

      var keyPrefix = generateEntryCacheId({ namespace: namespace, path: rootPath });
      Object.keys(self.entries).forEach(function (key) {
        if (key.indexOf(keyPrefix) === 0) {
          delete self.entries[key];
        }
      });

      var deletePromises = [];
      var keysDeferred = $.Deferred();
      deletePromises.push(keysDeferred.promise());
      self.store.keys().then(function (keys) {
        keys.forEach(function (key) {
          if (key.indexOf(keyPrefix) === 0) {
            var deleteDeferred = $.Deferred();
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
    DataCatalog.prototype.persistCatalogEntry = function (dataCatalogEntry) {
      var self = this;
      if (!cacheEnabled || CACHEABLE_TTL.default <= 0) {
        return $.Deferred().resolve().promise();
      }
      var deferred = $.Deferred();

      var identifier = generateEntryCacheId(dataCatalogEntry);

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
    DataCatalog.prototype.loadNavOptPopularityForTables = function (options) {
      var self = this;
      var deferred = $.Deferred();
      var cancellablePromises = [];
      var popularEntries = [];
      var pathsToLoad = [];

      var options = setSilencedErrors(options);

      var existingPromises = [];
      options.paths.forEach(function (path) {
        var existingDeferred = $.Deferred();
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
        var loadDeferred = $.Deferred();
        if (pathsToLoad.length) {
          cancellablePromises.push(ApiHelper.getInstance().fetchNavOptPopularity({
            silenceErrors: options.silenceErrors,
            paths: pathsToLoad
          }).done(function (data) {
            var perTable = {};

            var splitNavOptValuesPerTable = function (listName) {
              if (data.values[listName]) {
                data.values[listName].forEach(function (column) {
                  var tableMeta = perTable[column.dbName + '.' + column.tableName];
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

            var tablePromises = [];

            Object.keys(perTable).forEach(function (path) {
              var tableDeferred = $.Deferred();
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

      return applyCancellable(new CancellablePromise(deferred, cancellablePromises), options);
    };

    /**
     * Helper function to fill a catalog entry with cached metadata.
     *
     * @param {DataCatalogEntry} dataCatalogEntry - The entry to fill
     * @param {Object} storeEntry - The cached version
     */
    var mergeEntry = function (dataCatalogEntry, storeEntry) {
      var mergeAttribute = function (attributeName, ttl, promiseName) {
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
     * @param {Object} options
     * @param {ContextNamespace} options.namespace - The context namespace
     * @param {ContextCompute} options.compute - The context compute
     * @param {string|string[]} options.path
     * @return {DataCatalogEntry}
     */
    DataCatalog.prototype.getKnownEntry = function (options) {
      var self = this;
      return self.entries[generateEntryCacheId(options)];
    };

    /**
     * @param {Object} options
     * @param {string|string[]} options.path
     * @param {ContextNamespace} options.namespace - The context namespace
     * @param {ContextCompute} options.compute - The context compute
     * @param {Object} [options.definition] - The initial definition if not already set on the entry
     * @param {boolean} [options.cachedOnly] - Default: false
     * @return {Promise}
     */
    DataCatalog.prototype.getEntry = function (options) {
      var self = this;
      var identifier = generateEntryCacheId(options);
      if (self.entries[identifier]) {
        return self.entries[identifier];
      }

      var deferred = $.Deferred();
      self.entries[identifier] = deferred.promise();

      if (!cacheEnabled) {
        deferred.resolve(new DataCatalogEntry({ dataCatalog: self, namespace: options.namespace, compute: options.compute, path: options.path, definition: options.definition })).promise();
      } else {
        self.store.getItem(identifier).then(function (storeEntry) {
          var definition = storeEntry ? storeEntry.definition : options.definition;
          var entry = new DataCatalogEntry({ dataCatalog: self, namespace: options.namespace, compute: options.compute, path: options.path, definition: definition });
          if (storeEntry) {
            mergeEntry(entry, storeEntry);
          } else if (!options.cachedOnly && options.definition) {
            entry.saveLater();
          }
          deferred.resolve(entry);
        }).catch(function (error) {
          console.warn(error);
          var entry = new DataCatalogEntry({ dataCatalog: self, namespace: options.namespace, compute: options.compute, path: options.path, definition: options.definition });
          if (!options.cachedOnly && options.definition) {
            entry.saveLater();
          }
          deferred.resolve(entry);
        })
      }

      return self.entries[identifier];
    };

    /**
     * Helper function to fill a multi table catalog entry with cached metadata.
     *
     * @param {MultiTableEntry} multiTableCatalogEntry - The entry to fill
     * @param {Object} storeEntry - The cached version
     */
    var mergeMultiTableEntry = function (multiTableCatalogEntry, storeEntry) {
      var mergeAttribute = function (attributeName, ttl, promiseName) {
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

    /**
     *
     * @param {Object} options
     * @param {ContextNamespace} options.namespace - The context namespace
     * @param {ContextCompute} options.compute - The context compute
     * @param {string[][]} options.paths
     *
     * @return {Promise}
     */
    DataCatalog.prototype.getMultiTableEntry = function (options) {
      var self = this;
      var identifier = generateEntryCacheId(options);
      if (self.multiTableEntries[identifier]) {
        return self.multiTableEntries[identifier];
      }

      var deferred = $.Deferred();
      self.multiTableEntries[identifier] = deferred.promise();

      if (!cacheEnabled) {
        deferred.resolve(new MultiTableEntry({ identifier: identifier, dataCatalog: self, paths: options.paths })).promise();
      } else {
        self.multiTableStore.getItem(identifier).then(function (storeEntry) {
          var entry = new MultiTableEntry({ identifier: identifier, dataCatalog: self, paths: options.paths });
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
    DataCatalog.prototype.persistMultiTableEntry = function (multiTableEntry) {
      var self = this;
      if (!cacheEnabled || CACHEABLE_TTL.default <= 0 || CACHEABLE_TTL.optimizer <= 0) {
        return $.Deferred().resolve().promise();
      }
      var deferred = $.Deferred();
      self.multiTableStore.setItem(multiTableEntry.identifier, {
        version: DATA_CATALOG_VERSION,
        topAggs: multiTableEntry.topAggs,
        topColumns: multiTableEntry.topColumns,
        topFilters: multiTableEntry.topFilters,
        topJoins: multiTableEntry.topJoins,
      }).then(deferred.resolve).catch(deferred.reject);
      return deferred.promise();
    };

    return DataCatalog;
  })();

  var DataCatalogEntry = (function () {

    /**
     * Helper function to reload the source meta for the given entry
     *
     * @param {DataCatalogEntry} dataCatalogEntry
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors]
     *
     * @return {CancellablePromise}
     */
    var reloadSourceMeta = function (dataCatalogEntry, options) {
      if (dataCatalogEntry.dataCatalog.invalidatePromise) {
        var deferred = $.Deferred();
        var cancellablePromises = [];
        dataCatalogEntry.dataCatalog.invalidatePromise.always(function () {
          cancellablePromises.push(fetchAndSave('fetchSourceMetadata', 'sourceMeta', dataCatalogEntry, options).done(deferred.resolve).fail(deferred.reject))
        });
        return dataCatalogEntry.trackedPromise('sourceMetaPromise', new CancellablePromise(deferred, undefined, cancellablePromises));
      }

      return dataCatalogEntry.trackedPromise('sourceMetaPromise', fetchAndSave('fetchSourceMetadata', 'sourceMeta', dataCatalogEntry, options));
    };

    /**
     * Helper function to reload the navigator meta for the given entry
     *
     * @param {DataCatalogEntry} dataCatalogEntry
     * @param {Object} [apiOptions]
     * @param {boolean} [apiOptions.silenceErrors] - Default true
     *
     * @return {CancellablePromise}
     */
    var reloadNavigatorMeta = function (dataCatalogEntry, apiOptions) {
      if (dataCatalogEntry.canHaveNavigatorMetadata()) {
        return dataCatalogEntry.trackedPromise('navigatorMetaPromise', fetchAndSave('fetchNavigatorMetadata', 'navigatorMeta', dataCatalogEntry, apiOptions)).done(function (navigatorMeta) {
          if (navigatorMeta && dataCatalogEntry.commentObservable) {
            dataCatalogEntry.commentObservable(dataCatalogEntry.getResolvedComment());
          }
        });
      }
      dataCatalogEntry.navigatorMetaPromise = $.Deferred().reject();
      return dataCatalogEntry.navigatorMetaPromise;
    };

    /**
     * Helper function to reload the analysis for the given entry
     *
     * @param {DataCatalogEntry} dataCatalogEntry
     * @param {Object} [apiOptions]
     * @param {boolean} [apiOptions.silenceErrors]
     * @param {boolean} [apiOptions.refreshAnalysis]
     *
     * @return {CancellablePromise}
     */
    var reloadAnalysis = function (dataCatalogEntry, apiOptions) {
      return dataCatalogEntry.trackedPromise('analysisPromise',
        fetchAndSave(apiOptions && apiOptions.refreshAnalysis ? 'refreshAnalysis' : 'fetchAnalysis', 'analysis', dataCatalogEntry, apiOptions));
    };

    /**
     * Helper function to reload the partitions for the given entry
     *
     * @param {DataCatalogEntry} dataCatalogEntry
     * @param {Object} [apiOptions]
     * @param {boolean} [apiOptions.silenceErrors]
     *
     * @return {CancellablePromise}
     */
    var reloadPartitions = function (dataCatalogEntry, apiOptions) {
      return dataCatalogEntry.trackedPromise('partitionsPromise', fetchAndSave('fetchPartitions', 'partitions', dataCatalogEntry, apiOptions));
    };

    /**
     * Helper function to reload the sample for the given entry
     *
     * @param {DataCatalogEntry} dataCatalogEntry
     * @param {Object} [apiOptions]
     * @param {boolean} [apiOptions.silenceErrors]
     *
     * @return {CancellablePromise}
     */
    var reloadSample = function (dataCatalogEntry, apiOptions) {
      return dataCatalogEntry.trackedPromise('samplePromise', fetchAndSave('fetchSample', 'sample', dataCatalogEntry, apiOptions));
    };

    /**
     * Helper function to reload the nav opt metadata for the given entry
     *
     * @param {DataCatalogEntry} dataCatalogEntry
     * @param {Object} [apiOptions]
     * @param {boolean} [apiOptions.silenceErrors] - Default true
     *
     * @return {CancellablePromise}
     */
    var reloadNavOptMeta = function (dataCatalogEntry, apiOptions) {
      if (dataCatalogEntry.dataCatalog.canHaveNavOptMetadata()) {
        return dataCatalogEntry.trackedPromise('navOptMetaPromise', fetchAndSave('fetchNavOptMeta', 'navOptMeta', dataCatalogEntry, apiOptions));
      }
      dataCatalogEntry.navOptMetaPromise =  $.Deferred.reject().promise();
      return dataCatalogEntry.navOptMetaPromise;
    };

    /**
     * @param {DataCatalog} options.dataCatalog
     * @param {string|string[]} options.path
     * @param {ContextNamespace} options.namespace - The context namespace
     * @param {ContextCompute} options.compute - The context compute
     * @param {Object} options.definition - Initial known metadata on creation (normally comes from the parent entry)
     *
     * @constructor
     */
    function DataCatalogEntry(options) {
      var self = this;

      self.namespace = options.namespace;
      self.compute = options.compute;
      self.dataCatalog = options.dataCatalog;
      self.path = typeof options.path === 'string' && options.path ? options.path.split('.') : options.path || [];
      self.name = self.path.length ? self.path[self.path.length - 1] : options.dataCatalog.sourceType;

      self.definition = options.definition;

      if (!self.definition) {
        if (self.path.length === 0) {
          self.definition = { type: 'source' }
        } else if (self.path.length === 1) {
          self.definition = { type: 'database' }
        } else if (self.path.length === 2) {
          self.definition = { type: 'table' }
        }
      }

      self.reset();
    }

    /**
     * Resets the entry to an empty state, it might still have some details cached
     */
    DataCatalogEntry.prototype.reset = function () {
      var self = this;
      self.saveTimeout = -1;
      self.sourceMetaPromise = undefined;
      self.sourceMeta = undefined;

      self.navigatorMeta = undefined;
      self.navigatorMetaPromise = undefined;

      self.analysis = undefined;
      self.analysisPromise = undefined;

      self.partitions = undefined;
      self.partitionsPromise = undefined;

      self.sample = undefined;
      self.samplePromise = undefined;

      self.navOptPopularity = undefined;
      self.navOptMeta = undefined;
      self.navOptMetaPromise = undefined;

      self.navigatorMetaForChildrenPromise = undefined;
      self.navOptPopularityForChildrenPromise = undefined;

      self.childrenPromise = undefined;
      
      if (self.path.length) {
        var parent = self.dataCatalog.getKnownEntry({ namespace: self.namespace, compute: self.compute, path: self.path.slice(0, self.path.length - 1) });
        if (parent) {
          parent.navigatorMetaForChildrenPromise = undefined;
          parent.navOptPopularityForChildrenPromise = undefined;
        }
      }
    };

    /**
     * Helper function that ensure that cancellable promises are not tracked anymore when cancelled
     *
     * @param {string} promiseName - The attribute name to use
     * @param {CancellablePromise} cancellablePromise
     */
    DataCatalogEntry.prototype.trackedPromise = function (promiseName, cancellablePromise) {
      var self = this;
      self[promiseName] = cancellablePromise;
      return cancellablePromise.fail(function () {
        if (cancellablePromise.cancelled) {
          delete self[promiseName];
        }
      })
    };

    /**
     * Resets the entry and clears the cache
     *
     * @param {Object} options
     * @param {string} [options.invalidate] - 'cache', 'invalidate' or 'invalidateAndFlush', default 'cache', only used for Impala
     * @param {boolean} [options.cascade] - Default false, only used when the entry is for the source
     * @param {boolean [options.silenceErrors] - Default false
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.clearCache = function (options) {
      var self = this;

      if (!options) {
        options = {}
      }

      var invalidatePromise;
      var invalidate = options.invalidate || 'cache';

      if (invalidate !== 'cache' && self.getSourceType() === 'impala') {
        if (self.dataCatalog.invalidatePromise) {
          invalidatePromise = self.dataCatalog.invalidatePromise;
        } else {
          invalidatePromise = ApiHelper.getInstance().invalidateSourceMetadata({
            sourceType: self.getSourceType(),
            compute: self.compute,
            invalidate: invalidate,
            path: self.path,
            silenceErrors: options.silenceErrors
          });
          self.dataCatalog.invalidatePromise = invalidatePromise;
          invalidatePromise.always(function () {
            delete self.dataCatalog.invalidatePromise;
          });
        }
      } else {
        invalidatePromise = $.Deferred().resolve().promise();
      }

      if (self.definition && self.definition.navOptLoaded) {
        delete self.definition.navOptLoaded;
      }

      self.reset();
      var saveDeferred = options.cascade ? self.dataCatalog.clearStorageCascade(self.namespace, self.compute, self.path) : self.save();

      var clearPromise = $.when(invalidatePromise, saveDeferred);

      clearPromise.always(function () {
        huePubSub.publish('data.catalog.entry.refreshed', { entry: self, cascade: !!options.cascade });
      });

      return new CancellablePromise(clearPromise, undefined, [ invalidatePromise ]);
    };

    /**
     * Save the entry to cache
     *
     * @return {Promise}
     */
    DataCatalogEntry.prototype.save = function () {
      var self = this;
      window.clearTimeout(self.saveTimeout);
      return self.dataCatalog.persistCatalogEntry(self);
    };

    /**
     * Save the entry at a later point of time
     */
    DataCatalogEntry.prototype.saveLater = function () {
      var self = this;
      if (CACHEABLE_TTL.default > 0) {
        window.clearTimeout(self.saveTimeout);
        self.saveTimeout = window.setTimeout(function () {
          self.save();
        }, 1000);
      }
    };

    /**
     * Get the children of the catalog entry, columns for a table entry etc.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors]
     * @param {boolean} [options.cachedOnly]
     * @param {boolean} [options.refreshCache]
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {Promise}
     */
    DataCatalogEntry.prototype.getChildren = function (options) {
      var self = this;
      if (self.childrenPromise && (!options || !options.refreshCache)) {
        return applyCancellable(self.childrenPromise, options);
      }
      var deferred = $.Deferred();

      if (options && options.cachedOnly && !self.sourceMeta && !self.sourceMetaPromise) {
        return deferred.reject(false).promise();
      }

      var sourceMetaPromise = self.getSourceMeta(options).done(function (sourceMeta) {
        if (!sourceMeta || sourceMeta.notFound) {
          deferred.reject();
          return;
        }
        var promises = [];
        var index = 0;
        var partitionKeys = {};
        if (sourceMeta.partition_keys) {
          sourceMeta.partition_keys.forEach(function (partitionKey) {
            partitionKeys[partitionKey.name] = true;
          })
        }

        var entities = sourceMeta.databases
          || sourceMeta.tables_meta || sourceMeta.extended_columns || sourceMeta.fields || sourceMeta.columns;

        if (entities) {
          entities.forEach(function (entity) {
            if (!sourceMeta.databases || ((entity.name || entity) !== '_impala_builtins')) {
              promises.push(self.dataCatalog.getEntry({
                namespace: self.namespace,
                compute: self.compute,
                path: self.path.concat(entity.name || entity)
              }).done(function (catalogEntry) {
                if (!catalogEntry.definition || typeof catalogEntry.definition.index === 'undefined') {
                  var definition = typeof entity === 'object' ? entity : {};
                  if (typeof entity !== 'object') {
                    if (self.path.length === 0) {
                      definition.type = 'database';
                    } else if (self.path.length === 1) {
                      definition.type = 'table';
                    } else if (self.path.length === 2) {
                      definition.type = 'column';
                    }
                  }
                  if (sourceMeta.partition_keys) {
                    definition.partitionKey = !!partitionKeys[entity.name];
                  }
                  definition.index = index++;
                  catalogEntry.definition = definition;
                  catalogEntry.saveLater();
                }
              }));
            }
          });
        }
        if ((self.getSourceType() === 'impala' || self.getSourceType() === 'hive') && self.isComplex()) {
          (sourceMeta.type === 'map' ? ['key', 'value'] : ['item']).forEach(function (path) {
            if (sourceMeta[path]) {
              promises.push(self.dataCatalog.getEntry({ namespace: self.namespace, compute: self.compute, path: self.path.concat(path) }).done(function (catalogEntry) {
                if (!catalogEntry.definition || typeof catalogEntry.definition.index === 'undefined') {
                  var definition = sourceMeta[path];
                  definition.index = index++;
                  definition.isMapValue = path === 'value';
                  catalogEntry.definition = definition;
                  catalogEntry.saveLater();
                }
              }));
            }
          })
        }
        $.when.apply($, promises).done(function () {
          deferred.resolve(Array.prototype.slice.call(arguments));
        });
      }).fail(deferred.reject);

      return applyCancellable(self.trackedPromise('childrenPromise', new CancellablePromise(deferred, undefined, [ sourceMetaPromise ])), options);
    };

    /**
     * Loads navigator metadata for children, only applicable to databases and tables
     *
     * @param {Object} [options]
     * @param {boolean} [options.refreshCache]
     * @param {boolean} [options.silenceErrors] - Default true
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.loadNavigatorMetaForChildren = function (options) {
      var self = this;

      options = setSilencedErrors(options);

      if (!self.canHaveNavigatorMetadata() || self.isField()) {
        return $.Deferred().reject().promise();
      }

      if (self.navigatorMetaForChildrenPromise && (!options || !options.refreshCache)) {
        return applyCancellable(self.navigatorMetaForChildrenPromise, options);
      }

      var deferred = $.Deferred();

      var cancellablePromises = [];

      cancellablePromises.push(self.getChildren(options).done(function (children) {
        var someHaveNavMeta = children.some(function (childEntry) { return childEntry.navigatorMeta });
        if (someHaveNavMeta && (!options || !options.refreshCache)) {
          deferred.resolve(children);
          return;
        }

        var query;
        // TODO: Add sourceType to nav search query
        if (self.path.length) {
          query = 'parentPath:"/' + self.path.join('/') + '" AND type:(table view field)';
        } else {
          query = 'type:database'
        }

        var rejectUnknown = function () {
          children.forEach(function (childEntry) {
            if (!childEntry.navigatorMeta) {
              childEntry.navigatorMeta = {};
              childEntry.navigatorMetaPromise = $.Deferred().reject().promise();
            }
          });
        };

        cancellablePromises.push(ApiHelper.getInstance().searchEntities({
          query: query,
          rawQuery: true,
          limit: children.length,
          silenceErrors: options && options.silenceErrors
        }).done(function (result) {
          if (result && result.entities) {
            var childEntryIndex = {};
            children.forEach(function (childEntry) {
              childEntryIndex[childEntry.name.toLowerCase()] = childEntry;
            });

            result.entities.forEach(function (entity) {
              var matchingChildEntry = childEntryIndex[(entity.original_name || entity.originalName).toLowerCase()];
              if (matchingChildEntry) {
                matchingChildEntry.navigatorMeta = entity;
                entity.hueTimestamp = Date.now();
                matchingChildEntry.navigatorMetaPromise = $.Deferred().resolve(matchingChildEntry.navigatorMeta).promise();
                if (entity && matchingChildEntry.commentObservable) {
                  matchingChildEntry.commentObservable(matchingChildEntry.getResolvedComment());
                }
                matchingChildEntry.saveLater();
              }
            });
          }
          rejectUnknown();
          deferred.resolve(children);
        }).fail(function () {
          rejectUnknown();
          deferred.reject();
        }));
      }).fail(deferred.reject));

      return applyCancellable(self.trackedPromise('navigatorMetaForChildrenPromise', new CancellablePromise(deferred, null, cancellablePromises)), options);
    };

    /**
     * Helper function used when loading navopt metdata for children
     *
     * @param {Object} response
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.applyNavOptResponseToChildren = function (response, options) {
      var self = this;
      var deferred = $.Deferred();
      if (!self.definition) {
        self.definition = {};
      }
      self.definition.navOptLoaded = true;
      self.saveLater();

      var childPromise = self.getChildren(options).done(function (childEntries) {
        var entriesByName = {};
        childEntries.forEach(function (childEntry) {
          entriesByName[childEntry.name.toLowerCase()] = childEntry;
        });
        var updatedIndex = {};

        if (self.isDatabase() && response.top_tables) {
          response.top_tables.forEach(function (topTable) {
            var matchingChild = entriesByName[topTable.name.toLowerCase()];
            if (matchingChild) {
              matchingChild.navOptPopularity = topTable;
              matchingChild.saveLater();
              updatedIndex[matchingChild.getQualifiedPath()] = matchingChild;
            }
          });
        } else if (self.isTableOrView() && response.values) {
          var addNavOptPopularity = function (columns, type) {
            if (columns) {
              columns.forEach(function (column) {
                var matchingChild = entriesByName[column.columnName.toLowerCase()];
                if (matchingChild) {
                  if (!matchingChild.navOptPopularity) {
                    matchingChild.navOptPopularity = {};
                  }
                  matchingChild.navOptPopularity[type] = column;
                  matchingChild.saveLater();
                  updatedIndex[matchingChild.getQualifiedPath()] = matchingChild;
                }
              });
            }
          };

          addNavOptPopularity(response.values.filterColumns, 'filterColumn');
          addNavOptPopularity(response.values.groupbyColumns, 'groupByColumn');
          addNavOptPopularity(response.values.joinColumns, 'joinColumn');
          addNavOptPopularity(response.values.orderbyColumns, 'orderByColumn');
          addNavOptPopularity(response.values.selectColumns, 'selectColumn');
        }
        var popularEntries = [];
        Object.keys(updatedIndex).forEach(function(path) {
          popularEntries.push(updatedIndex[path]);
        });
        deferred.resolve(popularEntries);
      }).fail(deferred.reject);

      return new CancellablePromise(deferred, undefined, [ childPromise ]);
    };

    /**
     * Loads nav opt popularity for the children of this entry.
     *
     * @param {Object} [options]
     * @param {boolean} [options.refreshCache]
     * @param {boolean} [options.silenceErrors] - Default true
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.loadNavOptPopularityForChildren = function (options) {
      var self = this;

      var options = setSilencedErrors(options);

      if (!self.dataCatalog.canHaveNavOptMetadata()) {
        return $.Deferred().reject().promise();
      }
      if (self.navOptPopularityForChildrenPromise && (!options || !options.refreshCache)) {
        return applyCancellable(self.navOptPopularityForChildrenPromise, options);
      }
      var deferred = $.Deferred();
      var cancellablePromises = [];
      if (self.definition && self.definition.navOptLoaded && (!options || !options.refreshCache)) {
        cancellablePromises.push(self.getChildren(options).done(function (childEntries) {
          deferred.resolve(childEntries.filter(function (entry) { return entry.navOptPopularity }));
        }).fail(deferred.reject));
      } else if (self.isDatabase() || self.isTableOrView()) {
        cancellablePromises.push(ApiHelper.getInstance().fetchNavOptPopularity({
          silenceErrors: options && options.silenceErrors,
          refreshCache: options && options.refreshCache,
          paths: [ self.path ]
        }).done(function (data) {
          cancellablePromises.push(self.applyNavOptResponseToChildren(data, options).done(deferred.resolve).fail(deferred.reject));
        }).fail(deferred.reject));
      } else {
        deferred.resolve([]);
      }

      return applyCancellable(self.trackedPromise('navOptPopularityForChildrenPromise', new CancellablePromise(deferred, undefined, cancellablePromises)), options);
    };

    /**
     * Returns true if the catalog entry can have navigator metadata
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.canHaveNavigatorMetadata = function () {
      var self = this;
      return HAS_NAVIGATOR
        && (self.getSourceType() === 'hive' || self.getSourceType() === 'impala')
        && (self.isDatabase() || self.isTableOrView() || self.isColumn());
    };

    /**
     * Returns the currently known comment without loading any additional metadata
     *
     * @return {string}
     */
    DataCatalogEntry.prototype.getResolvedComment = function () {
      var self = this;
      if (self.navigatorMeta && (self.getSourceType() === 'hive' || self.getSourceType() === 'impala')) {
        return self.navigatorMeta.description || self.navigatorMeta.originalDescription || ''
      }
      return self.sourceMeta && self.sourceMeta.comment || '';
    };

    /**
     * This can be used to get an observable for the comment which will be updated once a comment has been
     * resolved.
     *
     * @return {ko.observable}
     */
    DataCatalogEntry.prototype.getCommentObservable = function () {
      var self = this;
      if (!self.commentObservable) {
        self.commentObservable = ko.observable(self.getResolvedComment());
      }
      return self.commentObservable;
    };

    /**
     * Checks whether the comment is known and has been loaded from the proper source
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.hasResolvedComment = function () {
      var self = this;
      if (self.canHaveNavigatorMetadata()) {
        return typeof self.navigatorMeta !== 'undefined';
      }
      return typeof self.sourceMeta !== 'undefined';
    };

    /**
     * Gets the comment for this entry, fetching it if necessary from the proper source.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors]
     * @param {boolean} [options.cachedOnly]
     * @param {boolean} [options.refreshCache]
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getComment = function (options) {
      var self = this;
      var deferred = $.Deferred();
      var cancellablePromises = [];

      var resolveWithSourceMeta = function () {
        if (self.sourceMeta) {
          deferred.resolve(self.sourceMeta.comment || '');
        } else if (self.definition && typeof self.definition.comment !== 'undefined') {
          deferred.resolve(self.definition.comment)
        } else {
          cancellablePromises.push(self.getSourceMeta(options).done(function (sourceMeta) {
            deferred.resolve(sourceMeta && sourceMeta.comment || '');
          }).fail(deferred.reject));
        }
      };

      if (self.canHaveNavigatorMetadata()) {
        if (self.navigatorMetaPromise) {
          self.navigatorMetaPromise.done(function () {
            deferred.resolve(self.navigatorMeta.description || self.navigatorMeta.originalDescription || '');
          }).fail(resolveWithSourceMeta);
        } else if (self.navigatorMeta) {
          deferred.resolve(self.navigatorMeta.description || self.navigatorMeta.originalDescription || '');
        } else {
          cancellablePromises.push(self.getNavigatorMeta(options).done(function (navigatorMeta) {
            if (navigatorMeta) {
              deferred.resolve(navigatorMeta.description || navigatorMeta.originalDescription || '');
            } else {
              resolveWithSourceMeta();
            }
          }).fail(resolveWithSourceMeta))
        }
      } else {
        resolveWithSourceMeta();
      }

      return applyCancellable(new CancellablePromise(deferred, undefined, cancellablePromises), options);
    };

    /**
     * Updates custom navigator metadata for the catalog entry
     *
     * @param {Object} [modifiedCustomMetadata] - The custom metadata to update, only supply what has been changed
     * @param {string[]} [deletedCustomMetadataKeys] - The custom metadata to delete identifier by the keys
     * @param {Object} [apiOptions]
     * @param {boolean} [apiOptions.silenceErrors]
     *
     * @return {Promise}
     */
    DataCatalogEntry.prototype.updateNavigatorCustomMetadata = function (modifiedCustomMetadata, deletedCustomMetadataKeys, apiOptions) {
      var self = this;
      var deferred = $.Deferred();

      if (self.canHaveNavigatorMetadata()) {
        if (self.navigatorMeta === {} || (self.navigatorMeta && typeof self.navigatorMeta.identity === 'undefined')) {
          if (!apiOptions) {
            apiOptions = {};
          }
          apiOptions.refreshCache = true;
        }
        self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
          if (navigatorMeta) {
            ApiHelper.getInstance().updateNavigatorProperties({
              identity: navigatorMeta.identity,
              modifiedCustomMetadata: modifiedCustomMetadata,
              deletedCustomMetadataKeys: deletedCustomMetadataKeys
            }).done(function (entity) {
              if (entity) {
                self.navigatorMeta = entity;
                self.navigatorMetaPromise = $.Deferred().resolve(self.navigatorMeta).promise();
                self.saveLater();
                deferred.resolve(self.navigatorMeta);
              } else {
                deferred.reject();
              }
            }).fail(deferred.reject);
          }
        }).fail(deferred.reject);
      } else {
        deferred.reject();
      }

      return deferred.promise();
    };

    /**
     * Sets the comment in the proper source
     *
     * @param {string} comment
     * @param {Object} [apiOptions]
     * @param {boolean} [apiOptions.silenceErrors]
     * @param {boolean} [apiOptions.refreshCache]
     *
     * @return {Promise}
     */
    DataCatalogEntry.prototype.setComment = function (comment, apiOptions) {
      var self = this;
      var deferred = $.Deferred();

      if (self.canHaveNavigatorMetadata()) {
        if (self.navigatorMeta === {} || (self.navigatorMeta && typeof self.navigatorMeta.identity === 'undefined')) {
          if (!apiOptions) {
            apiOptions = {};
          }
          apiOptions.refreshCache = true;
        }
        self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
          if (navigatorMeta) {
            ApiHelper.getInstance().updateNavigatorProperties({
              identity: navigatorMeta.identity,
              properties: {
                description: comment
              }
            }).done(function (entity) {
              if (entity) {
                self.navigatorMeta = entity;
                self.navigatorMetaPromise = $.Deferred().resolve(self.navigatorMeta).promise();
                self.saveLater();
              }
              self.getComment(apiOptions).done(function (comment) {
                if (self.commentObservable && self.commentObservable() !== comment) {
                  self.commentObservable(comment);
                }
                deferred.resolve(comment);
              });
            }).fail(deferred.reject);
          }
        }).fail(deferred.reject);
      } else {
        ApiHelper.getInstance().updateSourceMetadata({
          sourceType: self.getSourceType(),
          path: self.path,
          properties: {
            comment: comment
          }
        }).done(function () {
          reloadSourceMeta(self, {
            silenceErrors: apiOptions && apiOptions.silenceErrors,
            refreshCache: true
          }).done(function () {
            self.getComment(apiOptions).done(deferred.resolve);
          });
        }).fail(deferred.reject);
      }

      return deferred.promise();
    };

    /**
     * Adds a list of tags and updates the navigator metadata of the entry
     *
     * @param {string[]} tags
     *
     * @return {Promise}
     */
    DataCatalogEntry.prototype.addNavigatorTags = function (tags) {
      var self = this;
      var deferred = $.Deferred();
      if (self.canHaveNavigatorMetadata()) {
        self.getNavigatorMeta().done(function (navMeta) {
          if (navMeta && typeof navMeta.identity !== 'undefined') {
            ApiHelper.getInstance().addNavTags(navMeta.identity, tags).done(function (entity) {
              if (entity) {
                self.navigatorMeta = entity;
                self.navigatorMetaPromise = $.Deferred().resolve(self.navigatorMeta).promise();
                self.saveLater();
              } else {
                deferred.reject();
              }
              deferred.resolve(self.navigatorMeta);
            }).fail(deferred.reject);
          } else {
            deferred.reject();
          }
        }).fail(deferred.reject);
      } else {
        deferred.reject();
      }
      return deferred.promise();
    };

    /**
     * Removes a list of tags and updates the navigator metadata of the entry
     *
     * @param {string[]} tags
     *
     * @return {Promise}
     */
    DataCatalogEntry.prototype.deleteNavigatorTags = function (tags) {
      var self = this;
      var deferred = $.Deferred();
      if (self.canHaveNavigatorMetadata()) {
        self.getNavigatorMeta().done(function (navMeta) {
          if (navMeta && typeof navMeta.identity !== 'undefined') {
            ApiHelper.getInstance().deleteNavTags(navMeta.identity, tags).done(function (entity) {
              if (entity) {
                self.navigatorMeta = entity;
                self.navigatorMetaPromise = $.Deferred().resolve(self.navigatorMeta).promise();
                self.saveLater();
              } else {
                deferred.reject();
              }
              deferred.resolve(self.navigatorMeta);
            }).fail(deferred.reject);
          } else {
            deferred.reject();
          }
        }).fail(deferred.reject);
      } else {
        deferred.reject();
      }
      return deferred.promise();
    };

    /**
     * Checks if the entry can have children or not without fetching additional metadata.
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.hasPossibleChildren = function () {
      var self = this;
      return (self.path.length < 3) ||
        (!self.definition && !self.sourceMeta) ||
        (self.sourceMeta && /^(?:struct|array|map)/i.test(self.sourceMeta.type)) ||
        (self.definition && /^(?:struct|array|map)/i.test(self.definition.type));
    };

    /**
     * Returns the index representing the order in which the backend returned this entry.
     *
     * @return {number}
     */
    DataCatalogEntry.prototype.getIndex = function () {
      var self = this;
      return self.definition && self.definition.index ? self.definition.index : 0;
    };

    /**
     * Returns the source type of this entry.
     *
     * @return {string} - 'impala', 'hive', 'solr', etc.
     */
    DataCatalogEntry.prototype.getSourceType = function () {
      var self = this;
      return self.dataCatalog.sourceType;
    };

    /**
     * Returns true if the entry represents a data source.
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isSource = function () {
      var self = this;
      return self.path.length === 0;
    };

    /**
     * Returns true if the entry is a database.
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isDatabase = function () {
      var self = this;
      return self.path.length === 1;
    };

    /**
     * Returns true if the entry is a table or a view.
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isTableOrView = function () {
      var self = this;
      return self.path.length === 2;
    };

    /**
     * Returns the default title used for the entry, the qualified path with type for fields. Optionally include
     * the comment after, if already resolved.
     *
     * @param {boolean} [includeComment] - Default false
     * @return {string}
     */
    DataCatalogEntry.prototype.getTitle = function (includeComment) {
      var self = this;
      var title = self.getQualifiedPath();
      if (self.isField()) {
        var type = self.getType();
        if (type) {
          title += ' (' + type + ')';
        }
      }
      if (includeComment && self.hasResolvedComment() && self.getResolvedComment()) {
        title += ' - ' + self.getResolvedComment();
      }
      return title;
    };

    /**
     * Returns the fully qualified path for this entry.
     *
     * @return {string}
     */
    DataCatalogEntry.prototype.getQualifiedPath = function () {
      var self = this;
      return self.path.join('.');
    };

    /**
     * Returns the display name for the entry, name or qualified path plus type for fields
     *
     * @param {boolean} qualified - Whether to use the qualified path or not, default false
     * @return {string}
     */
    DataCatalogEntry.prototype.getDisplayName = function (qualified) {
      var self = this;
      var displayName = qualified ? self.getQualifiedPath() : self.name;
      if (self.isField()) {
        var type = self.getType();
        if (type) {
          displayName += ' (' + type + ')';
        }
      }
      return displayName;
    };

    /**
     * Returns true for columns that are a primary key. Note that the definition has to come from a parent entry, i.e.
     * getChildren().
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isPrimaryKey = function () {
      var self = this;
      return self.isColumn() && self.definition && /true/i.test(self.definition.primary_key);
    };

    /**
     * Returns true if the entry is a partition key. Note that the definition has to come from a parent entry, i.e.
     * getChildren().
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isPartitionKey = function () {
      var self = this;
      return self.definition && !!self.definition.partitionKey;
    };

    /**
     * Returns true if the entry is a table. It will be accurate once the source meta has been loaded.
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isTable = function () {
      var self = this;
      if (self.path.length === 2) {
        if (self.sourceMeta) {
          return !self.sourceMeta.is_view;
        }
        if (self.definition && self.definition.type) {
          return self.definition.type.toLowerCase() === 'table';
        }
        return true;
      }
      return false;
    };

    /**
     * Returns true if the entry is a table. It will be accurate once the source meta has been loaded.
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isView = function () {
      var self = this;
      return self.path.length === 2 &&
        ((self.sourceMeta && self.sourceMeta.is_view) ||
          (self.definition && self.definition.type && self.definition.type.toLowerCase() === 'view'));
    };

    /**
     * Returns true if the entry is a column.
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isColumn = function () {
      var self = this;
      return self.path.length === 3;
    };

    /**
     * Returns true if the entry is a column. It will be accurate once the source meta has been loaded or if loaded from
     * a parent entry via getChildren().
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isComplex = function () {
      var self = this;
      return self.path.length > 2 && (
        (self.sourceMeta && /^(?:struct|array|map)/i.test(self.sourceMeta.type)) ||
        (self.definition && /^(?:struct|array|map)/i.test(self.definition.type)));
    };

    /**
     * Returns true if the entry is a field, i.e. column or child of a complex type.
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isField = function () {
      var self = this;
      return self.path.length > 2;
    };

    /**
     * Returns true if the entry is an array. It will be accurate once the source meta has been loaded or if loaded from
     * a parent entry via getChildren().
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isArray = function () {
      var self = this;
      return (self.sourceMeta && /^array/i.test(self.sourceMeta.type)) ||
        (self.definition && /^array/i.test(self.definition.type));
    };

    /**
     * Returns true if the entry is a map. It will be accurate once the source meta has been loaded or if loaded from
     * a parent entry via getChildren().
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isMap = function () {
      var self = this;
      return (self.sourceMeta && /^map/i.test(self.sourceMeta.type)) ||
        (self.definition && /^map/i.test(self.definition.type));
    };

    /**
     * Returns true if the entry is a map value. It will be accurate once the source meta has been loaded or if loaded
     * from a parent entry via getChildren().
     *
     * @return {boolean}
     */
    DataCatalogEntry.prototype.isMapValue = function () {
      var self = this;
      return self.definition && self.definition.isMapValue;
    };

    /**
     * Returns the type of the entry. It will be accurate once the source meta has been loaded or if loaded from
     * a parent entry via getChildren().
     *
     * The returned string is always lower case and for complex entries the type definition is stripped to
     * either 'array', 'map' or 'struct'.
     *
     * @return {string}
     */
    DataCatalogEntry.prototype.getType = function () {
      var self = this;
      var type = self.getRawType();
      if (type.indexOf('<') !== -1) {
        type = type.substring(0, type.indexOf('<'));
      }
      return type.toLowerCase();
    };

    /**
     * Returns the raw type of the entry. It will be accurate once the source meta has been loaded or if loaded from
     * a parent entry via getChildren().
     *
     * For complex entries the type definition is the full version.
     *
     * @return {string}
     */
    DataCatalogEntry.prototype.getRawType = function () {
      var self = this;
      return self.sourceMeta && self.sourceMeta.type || self.definition.type || '';
    };

    /**
     * Gets the source metadata for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors]
     * @param {boolean} [options.cachedOnly]
     * @param {boolean} [options.refreshCache]
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getSourceMeta = function (options) {
      var self = this;
      if (options && options.cachedOnly) {
        return applyCancellable(self.sourceMetaPromise, options) || $.Deferred().reject(false).promise();
      }
      if (options && options.refreshCache) {
        return applyCancellable(reloadSourceMeta(self, options));
      }
      return applyCancellable(self.sourceMetaPromise || reloadSourceMeta(self, options), options);
    };

    /**
     * Gets the analysis for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors]
     * @param {boolean} [options.cachedOnly]
     * @param {boolean} [options.refreshCache] - Clears the browser cache
     * @param {boolean} [options.refreshAnalysis] - Performs a hard refresh on the source level
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getAnalysis = function (options) {
      var self = this;
      if (options && options.cachedOnly) {
        return applyCancellable(self.analysisPromise, options) || $.Deferred().reject(false).promise();
      }
      if (options && (options.refreshCache || options.refreshAnalysis)) {
        return applyCancellable(reloadAnalysis(self, options), options);
      }
      return applyCancellable(self.analysisPromise || reloadAnalysis(self, options), options);
    };

    /**
     * Gets the partitions for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors]
     * @param {boolean} [options.cachedOnly]
     * @param {boolean} [options.refreshCache] - Clears the browser cache
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getPartitions = function (options) {
      var self = this;
      if (!self.isTableOrView()) {
        return $.Deferred().reject(false).promise();
      }
      if (options && options.cachedOnly) {
        return applyCancellable(self.partitionsPromise, options) || $.Deferred().reject(false).promise();
      }
      if (options && options.refreshCache) {
        return applyCancellable(reloadPartitions(self, options), options);
      }
      return applyCancellable(self.partitionsPromise || reloadPartitions(self, options), options);
    };

    /**
     * Gets the Navigator metadata for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default true
     * @param {boolean} [options.cachedOnly]
     * @param {boolean} [options.refreshCache]
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getNavigatorMeta = function (options) {
      var self = this;

      var options = setSilencedErrors(options);

      if (!self.canHaveNavigatorMetadata()) {
        return $.Deferred().reject().promise();
      }
      if (options && options.cachedOnly) {
        return applyCancellable(self.navigatorMetaPromise, options) || $.Deferred().reject(false).promise();
      }
      if (options && options.refreshCache) {
        return applyCancellable(reloadNavigatorMeta(self, options), options);
      }
      return applyCancellable(self.navigatorMetaPromise || reloadNavigatorMeta(self, options), options)
    };

    /**
     * Gets the Nav Opt metadata for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default true
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getNavOptMeta = function (options) {
      var self = this;

      var options = setSilencedErrors(options);

      if (!self.dataCatalog.canHaveNavOptMetadata() || !self.isTableOrView()) {
        return $.Deferred().reject().promise();
      }
      if (options && options.cachedOnly) {
        return applyCancellable(self.navOptMetaPromise, options) || $.Deferred().reject(false).promise();
      }
      if (options && options.refreshCache) {
        return applyCancellable(reloadNavOptMeta(self, options), options);
      }
      return applyCancellable(self.navOptMetaPromise || reloadNavOptMeta(self, options), options);
    };

    /**
     * Gets the sample for the entry, if unknown it will first check if any parent table already has the sample. It
     * will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     * @oaram {string} [options.operation]
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getSample = function (options) {
      var self = this;

      // This prevents caching of any non-standard sample queries, i.e. DISTINCT etc.
      if (options && options.operation && options.operation !== 'default') {
        return applyCancellable(ApiHelper.getInstance().fetchSample({
          sourceType: self.dataCatalog.sourceType,
          compute: self.compute,
          path: self.path,
          silenceErrors: options && options.silenceErrors,
          operation: options.operation
        }), options);
      }

      // Check if parent has a sample that we can reuse
      if (!self.samplePromise && self.isColumn()) {
        var deferred = $.Deferred();
        var cancellablePromises = [];

        var revertToSpecific = function () {
          if (options && options.cachedOnly) {
            deferred.reject();
          } else {
            cancellablePromises.push(applyCancellable(reloadSample(self, options), options).done(deferred.resolve).fail(deferred.reject));
          }
        };

        self.dataCatalog.getEntry({ namespace: self.namespace, compute: self.compute, path: self.path.slice(0, 2), definition: { type: 'table' } }).done(function (tableEntry) {
          if (tableEntry && tableEntry.samplePromise) {
            cancellablePromises.push(applyCancellable(tableEntry.samplePromise, options));

            tableEntry.samplePromise.done(function (parentSample) {
              var colSample = {
                hueTimestamp: parentSample.hueTimestamp,
                has_more: parentSample.has_more,
                type: parentSample.type,
                data: [],
                meta: []
              };
              if (parentSample.meta) {
                for (var i = 0; i < parentSample.meta.length; i++) {
                  if (parentSample.meta[i].name.toLowerCase() === self.name.toLowerCase()) {
                    colSample.meta[0] = parentSample.meta[i];
                    parentSample.data.forEach(function (parentRow) {
                      colSample.data.push([parentRow[i]]);
                    });
                    break;
                  }
                }
              }
              if (colSample.meta.length) {
                self.sample = colSample;
                deferred.resolve(self.sample);
              } else {
                revertToSpecific();
              }
            }).fail(revertToSpecific);
          } else {
            revertToSpecific();
          }
        }).fail(revertToSpecific);

        return applyCancellable(self.trackedPromise('samplePromise', new CancellablePromise(deferred, undefined, cancellablePromises)), options);
      }

      if (options && options.cachedOnly) {
        return applyCancellable(self.samplePromise, options) || $.Deferred().reject(false).promise();
      }
      if (options && options.refreshCache) {
        return applyCancellable(reloadSample(self, options), options);
      }
      return applyCancellable(self.samplePromise || reloadSample(self, options), options);
    };

    /**
     * Helper function to get details from the multi-table catalog for just this specific table
     *
     * @param {DataCatalogEntry} catalogEntry
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     * @param {string} functionName - The function to call, i.e. 'getTopAggs' etc.
     * @return {CancellablePromise}
     */
    var getFromMultiTableCatalog = function (catalogEntry, options, functionName) {
      var deferred = $.Deferred();
      if (!catalogEntry.isTableOrView()) {
        return deferred.reject();
      }
      var cancellablePromises = [];
      catalogEntry.dataCatalog.getMultiTableEntry({ namespace: catalogEntry.namespace, compute: catalogEntry.compute, paths: [ catalogEntry.path ] }).done(function (multiTableEntry) {
        cancellablePromises.push(multiTableEntry[functionName](options).done(deferred.resolve).fail(deferred.reject));
      }).fail(deferred.reject);
      return new CancellablePromise(deferred, undefined, cancellablePromises);
    };

    /**
     * Gets the top aggregate UDFs for the entry if it's a table or view. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getTopAggs = function (options) {
      var self = this;
      return getFromMultiTableCatalog(self, options, 'getTopAggs');
    };

    /**
     * Gets the top filters for the entry if it's a table or view. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getTopFilters = function (options) {
      var self = this;
      return getFromMultiTableCatalog(self, options, 'getTopFilters');
    };

    /**
     * Gets the top joins for the entry if it's a table or view. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    DataCatalogEntry.prototype.getTopJoins = function (options) {
      var self = this;
      return getFromMultiTableCatalog(self, options, 'getTopJoins');
    };

    return DataCatalogEntry;
  })();

  var MultiTableEntry = (function () {

    /**
     *
     * @param {Object} options
     * @param {string} options.identifier
     * @param {DataCatalog} options.dataCatalog
     * @param {string[][]} options.paths
     * @constructor
     */
    var MultiTableEntry = function (options) {
      var self = this;
      self.identifier = options.identifier;
      self.dataCatalog = options.dataCatalog;
      self.paths = options.paths;

      self.topAggs = undefined;
      self.topAggsPromise = undefined;

      self.topColumns = undefined;
      self.topColumnsPromise = undefined;

      self.topFilters = undefined;
      self.topFiltersPromise = undefined;

      self.topJoins = undefined;
      self.topJoinsPromise = undefined;
    };

    /**
     * Save the multi table entry to cache
     *
     * @return {Promise}
     */
    MultiTableEntry.prototype.save = function () {
      var self = this;
      window.clearTimeout(self.saveTimeout);
      return self.dataCatalog.persistMultiTableEntry(self);
    };

    /**
     * Save the multi table entry at a later point of time
     */
    MultiTableEntry.prototype.saveLater = function () {
      var self = this;
      if (CACHEABLE_TTL.default > 0) {
        window.clearTimeout(self.saveTimeout);
        self.saveTimeout = window.setTimeout(function () {
          self.save();
        }, 1000);
      }
    };
    /**
     * Helper function that ensure that cancellable promises are not tracked anymore when cancelled
     *
     * @param {string} promiseName - The attribute name to use
     * @param {CancellablePromise} cancellablePromise
     */
    MultiTableEntry.prototype.trackedPromise = function (promiseName, cancellablePromise) {
      var self = this;
      self[promiseName] = cancellablePromise;
      return cancellablePromise.fail(function () {
        if (cancellablePromise.cancelled) {
          delete self[promiseName];
        }
      })
    };

    /**
     * Helper function to reload a NavOpt multi table attribute, like topAggs or topFilters
     *
     * @param {MultiTableEntry} multiTableEntry
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default true
     * @param {string} promiseAttribute
     * @param {string} dataAttribute
     * @param {string} apiHelperFunction
     * @return {CancellablePromise}
     */
    var genericNavOptReload = function (multiTableEntry, options, promiseAttribute, dataAttribute, apiHelperFunction) {
      if (multiTableEntry.dataCatalog.canHaveNavOptMetadata()) {
        return multiTableEntry.trackedPromise(promiseAttribute, fetchAndSave(apiHelperFunction, dataAttribute, multiTableEntry, options));
      }
      multiTableEntry[promiseAttribute] = $.Deferred().reject();
      return multiTableEntry[promiseAttribute];
    };

    /**
     * Helper function to get a NavOpt multi table attribute, like topAggs or topFilters
     *
     * @param {MultiTableEntry} multiTableEntry
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.cancellable] - Default false
     * @param {string} promiseAttribute
     * @param {string} dataAttribute
     * @param {string} apiHelperFunction
     * @return {CancellablePromise}
     */
    var genericNavOptGet = function (multiTableEntry, options, promiseAttribute, dataAttribute, apiHelperFunction) {
      if (options && options.cachedOnly) {
        return applyCancellable(multiTableEntry[promiseAttribute], options) || $.Deferred().reject(false).promise();
      }
      if (options && options.refreshCache) {
        return applyCancellable(genericNavOptReload(multiTableEntry, options, promiseAttribute, dataAttribute, apiHelperFunction), options);
      }
      return applyCancellable(multiTableEntry[promiseAttribute] || genericNavOptReload(multiTableEntry, options, promiseAttribute, dataAttribute, apiHelperFunction), options);
    };

    /**
     * Gets the top aggregate UDFs for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    MultiTableEntry.prototype.getTopAggs = function (options) {
      var self = this;
      return genericNavOptGet(self, options, 'topAggsPromise', 'topAggs', 'fetchNavOptTopAggs');
    };

    /**
     * Gets the top columns for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    MultiTableEntry.prototype.getTopColumns = function (options) {
      var self = this;
      return genericNavOptGet(self, options, 'topColumnsPromise', 'topColumns', 'fetchNavOptTopColumns');
    };

    /**
     * Gets the top filters for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    MultiTableEntry.prototype.getTopFilters = function (options) {
      var self = this;
      return genericNavOptGet(self, options, 'topFiltersPromise', 'topFilters', 'fetchNavOptTopFilters');
    };

    /**
     * Gets the top joins for the entry. It will fetch it if not cached or if the refresh option is set.
     *
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors] - Default false
     * @param {boolean} [options.cachedOnly] - Default false
     * @param {boolean} [options.refreshCache] - Default false
     * @param {boolean} [options.cancellable] - Default false
     *
     * @return {CancellablePromise}
     */
    MultiTableEntry.prototype.getTopJoins = function (options) {
      var self = this;
      return genericNavOptGet(self, options, 'topJoinsPromise', 'topJoins', 'fetchNavOptTopJoins');
    };

    return MultiTableEntry;
  })();

  var GeneralDataCatalog = (function () {

    function GeneralDataCatalog() {
      var self = this;
      self.store = localforage.createInstance({
        name: 'HueDataCatalog_' + STORAGE_POSTFIX
      });

      self.allNavigatorTagsPromise = undefined;
    }

    /**
     * @param {Object} [options]
     * @param {boolean} [options.silenceErrors]
     * @param {boolean} [options.refreshCache]
     *
     * @return {Promise}
     */
    GeneralDataCatalog.prototype.getAllNavigatorTags = function (options) {
      var self = this;
      if (self.allNavigatorTagsPromise && (!options || !options.refreshCache)) {
        return self.allNavigatorTagsPromise;
      }

      var deferred = $.Deferred();

      if (!HAS_NAVIGATOR) {
        return deferred.reject().promise();
      }

      self.allNavigatorTagsPromise = deferred.promise();

      var reloadAllTags = function () {
        ApiHelper.getInstance().fetchAllNavigatorTags({
          silenceErrors: options && options.silenceErrors,
        }).done(deferred.resolve).fail(deferred.reject);

        if (CACHEABLE_TTL.default > 0) {
          deferred.done(function (allTags) {
            self.store.setItem('hue.dataCatalog.allNavTags', { allTags: allTags, hueTimestamp: Date.now(), version: DATA_CATALOG_VERSION });
          })
        }
      };

      if (CACHEABLE_TTL.default > 0 && (!options || !options.refreshCache)) {
        self.store.getItem('hue.dataCatalog.allNavTags').then(function (storeEntry) {
          if (storeEntry && storeEntry.version === DATA_CATALOG_VERSION && (!storeEntry.hueTimestamp || (Date.now() - storeEntry.hueTimestamp) < CACHEABLE_TTL.default)) {
            deferred.resolve(storeEntry.allTags);
          } else {
            reloadAllTags();
          }
        }).catch(reloadAllTags);
      } else {
        reloadAllTags();
      }

      return self.allNavigatorTagsPromise;
    };

    /**
     * @param {string[]} tagsToAdd
     * @param {string[]} tagsToRemove
     */
    GeneralDataCatalog.prototype.updateAllNavigatorTags = function (tagsToAdd, tagsToRemove) {
      var self = this;
      if (self.allNavigatorTagsPromise) {
        self.allNavigatorTagsPromise.done(function (allTags) {
          tagsToAdd.forEach(function (newTag) {
            if (!allTags[newTag]) {
              allTags[newTag] = 0;
            }
            allTags[newTag]++;
          });
          tagsToRemove.forEach(function (removedTag) {
            if (!allTags[removedTag]) {
              allTags[removedTag]--;
              if (allTags[removedTag] === 0) {
                delete allTags[removedTag];
              }
            }
          });
          self.store.setItem('hue.dataCatalog.allNavTags', { allTags: allTags, hueTimestamp: Date.now(), version: DATA_CATALOG_VERSION });
        });
      }
    };

    return GeneralDataCatalog;
  })();

  return (function () {
    var generalDataCatalog = new GeneralDataCatalog();
    var sourceBoundCatalogs = {};

    /**
     * Helper function to get the DataCatalog instance for a given data source.
     *
     * @param {string} sourceType
     * @return {DataCatalog}
     */
    var getCatalog = function (sourceType) {
      if (!sourceType) {
        throw new Error('getCatalog called without sourceType');
      }
      return sourceBoundCatalogs[sourceType] || (sourceBoundCatalogs[sourceType] = new DataCatalog(sourceType));
    };

    return {

      /**
       * @param {Object} options
       * @param {string} options.sourceType
       * @param {ContextNamespace} options.namespace - The context namespace
       * @param {ContextCompute} options.compute - The context compute
       * @param {string|string[]} options.path
       * @param {Object} [options.definition] - Optional initial definition
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
        var deferred = $.Deferred();
        var cancellablePromises = [];
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

      applyCancellable: applyCancellable
    };
  })();
})();