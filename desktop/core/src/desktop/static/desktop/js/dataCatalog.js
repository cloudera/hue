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

  var STORAGE_POSTFIX = LOGGED_USERNAME // TODO: Add flag for embedded mode

  var DATA_CATALOG_VERSION = 1;

  var cacheEnabled = true;

  /**
   * @param {string} sourceType
   *
   * @constructor
   */
  function DataCatalog(sourceType) {
    var self = this;
    self.sourceType = sourceType;
    self.entries = {};
    self.store = localforage.createInstance({
      name: 'HueDataCatalog_' + self.sourceType + '_' + STORAGE_POSTFIX
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
   * Clears the data catalog and cache for the given path and any children thereof.
   *
   * @param {string[]} rootPath - The path to clear
   */
  DataCatalog.prototype.clearStorageCascade = function (rootPath) {
    var self = this;
    var deferred = $.Deferred();
    if (rootPath.length === 0) {
      self.entries = {};
      self.store.clear().then(deferred.resolve).catch(deferred.reject);
      return deferred.promise();
    }

    var keyPrefix = rootPath.join('.');
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
   */
  DataCatalog.prototype.updateStore = function (dataCatalogEntry) {
    var self = this;
    if (!cacheEnabled) {
      return $.Deferred().resolve().promise();
    }
    var deferred = $.Deferred();
    self.store.setItem(dataCatalogEntry.getQualifiedPath(), {
      version: DATA_CATALOG_VERSION,
      definition: dataCatalogEntry.definition,
      sourceMeta: dataCatalogEntry.sourceMeta,
      analysis: dataCatalogEntry.analysis,
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
   * @param {string[][]} options.paths
   * @param {boolean} [options.silenceErrors] - Default true
   *
   * @return {CancellablePromise}
   */
  DataCatalog.prototype.loadNavOptPopularityForTables = function (options) {
    var self = this;
    var deferred = $.Deferred();
    var cancellablePromises = [];
    var popularEntries = [];
    var pathsToLoad = [];

    if (!options) {
      options = {};
    }
    if (typeof options.silenceErrors === 'undefined') {
      options.silenceErrors = true;
    }

    var existingPromises = [];
    options.paths.forEach(function (path) {
      var existingDeferred = $.Deferred();
      self.getEntry({ path: path }).done(function (tableEntry) {
        if (tableEntry.navOptPopularityForChildrenPromise) {
          tableEntry.navOptPopularityForChildrenPromise.done(function (existingPopularEntries) {
            popularEntries = popularEntries.concat(existingPopularEntries);
            existingDeferred.resolve();
          }).fail(existingDeferred.reject);
        } else if (tableEntry.definition && tableEntry.definition.navOptLoaded) {
          tableEntry.getChildren({silenceErrors: options.silenceErrors}).done(function (childEntries) {
            childEntries.forEach(function (childEntry) {
              if (childEntry.navOptPopularity) {
                popularEntries.push(childEntry);
              }
            });
            existingDeferred.resolve();
          });
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
            self.getEntry({ path: path }).done(function (entry) {
              entry.navOptPopularityForChildrenPromise = entry.applyNavOptResponseToChildren(perTable[path], options).done(function (entries) {
                popularEntries = popularEntries.concat(entries);
                tableDeferred.resolve();
              }).fail(tableDeferred.resolve);
              cancellablePromises.push(entry.navOptPopularityForChildrenPromise);
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

    return new CancellablePromise(deferred.promise(), cancellablePromises);
  };

  /**
   * Helper function to fill a catalog entry with cached metadata.
   *
   * @param {DataCatalogEntry} dataCatalogEntry - The entry to fill
   * @param {Object} storeEntry - The cached version
   */
  var mergeFromStoreEntry = function (dataCatalogEntry, storeEntry) {
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
    mergeAttribute('sample', CACHEABLE_TTL.default, 'samplePromise');
    mergeAttribute('navigatorMeta', CACHEABLE_TTL.default, 'navigatorMetaPromise');
    mergeAttribute('navOptMeta', CACHEABLE_TTL.optimizer, 'navOptMetaPromise');
    mergeAttribute('navOptPopularity', CACHEABLE_TTL.optimizer);
  };

  /**
   * @param {Object} options
   * @param {string|string[]} options.path
   * @param {Object} [options.definition] - The initial definition if not already set on the entry
   *
   * @return {Promise}
   */
  DataCatalog.prototype.getEntry = function (options) {
    var self = this;
    var deferred = $.Deferred();
    var identifier = typeof options.path === 'string' ? options.path : options.path.join('.');
    if (self.entries[identifier]) {
      deferred.resolve(self.entries[identifier]);
    } else {
      deferred.done(function (entry) {
        self.entries[identifier] = entry;
      });
      if (!cacheEnabled) {
        return deferred.resolve(new DataCatalogEntry(self, options.path, options.definition)).promise();
      }
      self.store.getItem(identifier).then(function (storeEntry) {
        var definition = storeEntry ? storeEntry.definition : options.definition;
        if (self.entries[identifier]) {
          deferred.resolve(self.entries[identifier]);
          return;
        }
        var entry = new DataCatalogEntry(self, options.path, definition);
        if (storeEntry) {
          mergeFromStoreEntry(entry, storeEntry);
        } else {
          entry.saveLater();
        }
        deferred.resolve(entry);
      }).catch(function (error) {
        console.warn(error);
        var entry = new DataCatalogEntry(self, options.path, options.definition);
        entry.saveLater();
        deferred.resolve(entry);
      })
    }
    return deferred.promise();
  };

  /**
   * Wrapper function around ApiHelper calls, it will also save the entry on success.
   *
   * @param {string} apiHelperFunction - The name of the ApiHelper function to call
   * @param {string} attributeName - The attribute to set
   * @param {DataCatalogEntry} dataCatalogEntry - The catalog entry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   */
  var fetchAndSave = function (apiHelperFunction, attributeName, dataCatalogEntry, apiOptions) {
    return ApiHelper.getInstance()[apiHelperFunction]({
      sourceType: dataCatalogEntry.getSourceType(),
      path: dataCatalogEntry.path,
      silenceErrors: apiOptions && apiOptions.silenceErrors
    }).done(function (data) {
      dataCatalogEntry[attributeName] = data;
      dataCatalogEntry.saveLater();
    }).fail(function () {
      dataCatalogEntry[attributeName] = {};
    })
  };

  /**
   * Helper function to reload the source meta for the given entry
   *
   * @param {DataCatalogEntry} dataCatalogEntry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   *
   * @return {CancellablePromise}
   */
  var reloadSourceMeta = function (dataCatalogEntry, apiOptions) {
    if (dataCatalogEntry.dataCatalog.invalidatePromise) {
      var deferred = $.Deferred();

      var cancellablePromises = [];
      dataCatalogEntry.dataCatalog.invalidatePromise.always(function () {
        cancellablePromises.push(fetchAndSave('fetchSourceMetadata', 'sourceMeta', dataCatalogEntry, apiOptions).done(deferred.resolve).fail(deferred.reject))
      });
      dataCatalogEntry.sourceMetaPromise = new CancellablePromise(deferred.promise(), undefined, cancellablePromises);
    } else {
      dataCatalogEntry.sourceMetaPromise = fetchAndSave('fetchSourceMetadata', 'sourceMeta', dataCatalogEntry, apiOptions);
    }
    return dataCatalogEntry.sourceMetaPromise;
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
      dataCatalogEntry.navigatorMetaPromise = fetchAndSave('fetchNavigatorMetadata', 'navigatorMeta', dataCatalogEntry, apiOptions);
    } else {
      dataCatalogEntry.navigatorMetaPromise =  $.Deferred.reject().promise();
    }
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
    dataCatalogEntry.analysisPromise = fetchAndSave(apiOptions && apiOptions.refreshAnalysis ? 'refreshAnalysis' : 'fetchAnalysis', 'analysis', dataCatalogEntry, apiOptions);
    return dataCatalogEntry.analysisPromise;
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
    dataCatalogEntry.samplePromise = fetchAndSave('fetchSample', 'sample', dataCatalogEntry, apiOptions);
    return dataCatalogEntry.samplePromise;
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
    if (HAS_OPTIMIZER && (dataCatalogEntry.getSourceType() === 'hive' || dataCatalogEntry.getSourceType() === 'impala')) {
      dataCatalogEntry.navOptMetaPromise = fetchAndSave('fetchNavOptMeta', 'navOptMeta', dataCatalogEntry, apiOptions);
    } else {
      dataCatalogEntry.navOptMetaPromise =  $.Deferred.reject().promise();
    }
    return dataCatalogEntry.navOptMetaPromise;
  };

  /**
   * @param {DataCatalog} dataCatalog
   * @param {string|string[]} path
   * @param {Object} definition - Initial known metadata on creation (normally comes from the parent entry)
   *
   * @constructor
   */
  function DataCatalogEntry(dataCatalog, path, definition) {
    var self = this;

    self.dataCatalog = dataCatalog;
    self.path = typeof path === 'string' && path ? path.split('.') : path || [];
    self.name = self.path.length ? self.path[self.path.length - 1] : dataCatalog.sourceType;

    self.definition = definition;

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

    self.samplePromise = undefined;
    self.sample = undefined;

    self.navOptPopularity = undefined;
    self.navOptMeta = undefined;
    self.navOptMetaPromise = undefined;

    self.navigatorMetaForChildrenPromise = undefined;
    self.navOptPopularityForChildrenPromise = undefined;

    self.childrenPromise = undefined;
  };

  /**
   * Resets the entry and clears the cache
   *
   * @param {string} [invalidate] - 'cache', 'invalidate' or 'invalidateAndFlush', default 'cache', only used for Impala
   * @param {boolean} [cascade] - Default false, only used when the entry is for the source
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.clear = function (invalidate, cascade) {
    var self = this;

    var invalidatePromise;

    if (!invalidate) {
      invalidate = 'cache';
    }

    if (invalidate !== 'cache' && self.getSourceType() === 'impala') {
      if (self.dataCatalog.invalidatePromise) {
        invalidatePromise = self.dataCatalog.invalidatePromise;
      } else {
        if (self.path.length) {
          invalidatePromise = ApiHelper.getInstance().invalidateSourceMetadata({
            sourceType: self.getSourceType(),
            invalidate: invalidate,
            database: self.path[0]
          });
        } else {
          invalidatePromise = ApiHelper.getInstance().invalidateSourceMetadata({
            sourceType: self.getSourceType(),
            invalidate: invalidate
          });
        }
        self.dataCatalog.invalidatePromise = invalidatePromise;
        invalidatePromise.always(function () {
          delete self.dataCatalog.invalidatePromise;
        });
      }
    } else {
      invalidatePromise = $.Deferred().resolve().promise();
    }

    self.reset();
    var saveDeferred = cascade ? self.dataCatalog.clearStorageCascade(self.path) : self.save();

    var clearPromise = $.when(invalidatePromise, saveDeferred);

    clearPromise.always(function () {
      huePubSub.publish('data.catalog.entry.refreshed', { entry: self, cascade: cascade });
    });

    return new CancellablePromise(clearPromise, undefined, [invalidatePromise]);
  };

  /**
   * Save the entry to cache
   *
   * @return {Promise}
   */
  DataCatalogEntry.prototype.save = function () {
    var self = this;
    window.clearTimeout(self.saveTimeout);
    return self.dataCatalog.updateStore(self);
  };

  /**
   * Save the entry at a later point of time
   */
  DataCatalogEntry.prototype.saveLater = function () {
    var self = this;
    window.clearTimeout(self.saveTimeout);
    self.saveTimeout = window.setTimeout(function () {
      self.save();
    }, 1000);
  };

  /**
   * Get the children of the catalog entry, columns for a table entry etc.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
   *
   * @return {Promise}
   */
  DataCatalogEntry.prototype.getChildren = function (options) {
    var self = this;
    if (self.childrenPromise && (!options || !options.refreshCache)) {
      return self.childrenPromise;
    }
    var deferred = $.Deferred();
    self.childrenPromise = deferred.promise();
    self.getSourceMeta(options).done(function (sourceMeta) {
      if (sourceMeta.notFound) {
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
            promises.push(self.dataCatalog.getEntry({ path: self.path.concat(path) }).done(function (catalogEntry) {
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
    return self.childrenPromise;
  };

  /**
   * Loads navigator metdata for children, only applicable to databases and tables
   *
   * @param {Object} [options]
   * @param {boolean} [options.refreshCache]
   * @param {boolean} [options.silenceErrors] - Default true
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.loadNavigatorMetaForChildren = function (options) {
    var self = this;

    if (!options) {
      options = {};
    }

    if (typeof options.silenceErrors === 'undefined') {
      options.silenceErrors = true;
    }

    if (!self.canHaveNavigatorMetadata() || self.isField()) {
      return $.Deferred().reject().promise();
    }

    if (self.navigatorMetaForChildrenPromise && (!options || !options.refreshCache)) {
      return self.navigatorMetaForChildrenPromise;
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

      cancellablePromises.push(ApiHelper.getInstance().searchEntities({
        query: query,
        rawQuery: true,
        limit: children.length,
        silenceErrors: options && options.silenceErrors
      }).done(function (result) {
        if (result && result.entities && result.entities.length > 0) {
          var entryPromises = [];
          result.entities.forEach(function (entity) {
            var entryPromise = self.dataCatalog.getEntry({ path: self.path.concat((entity.name || entity.originalName).toLowerCase())}).done(function(catalogEntry) {
              catalogEntry.navigatorMeta = entity;
              catalogEntry.navigatorMetaPromise = $.Deferred().resolve(catalogEntry.navigatorMeta).promise();
              catalogEntry.saveLater();
            });
            entryPromises.push(entryPromise);
            cancellablePromises.push(entryPromise);
          });
          $.when.apply($, entryPromises).done(function () {
            deferred.resolve(Array.prototype.slice.call(arguments));
          });
        } else {
          deferred.resolve([]);
        }
      }).fail(deferred.reject));
    }).fail(deferred.reject));

    self.navigatorMetaForChildrenPromise = new CancellablePromise(deferred.promise(), null, cancellablePromises);
    return self.navigatorMetaForChildrenPromise;
  };

  /**
   * Helper function used when loading navopt metdata for children
   *
   * @param {Object} response
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   */
  DataCatalogEntry.prototype.applyNavOptResponseToChildren = function (response, options) {
    var self = this;
    var deferred = $.Deferred();
    if (!self.definition) {
      self.definition = {};
    }
    self.definition.navOptLoaded = true;
    self.saveLater();


    var childPromise = self.getChildren({ silenceErrors: options && options.silenceErrors }).done(function (childEntries) {
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

    return new CancellablePromise(deferred.promise(), undefined, [ childPromise ]);
  };

  /**
   * Loads nav opt popularity for the children of this entry.
   *
   * @param {Object} [options]
   * @param {boolean} [options.refreshCache]
   * @param {boolean} [options.silenceErrors] - Default true
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.loadNavOptPopularityForChildren = function (options) {
    var self = this;
    if (!options) {
      options = {};
    }
    if (typeof options.silenceErrors === 'undefined') {
      options.silenceErrors = true;
    }

    if (!HAS_OPTIMIZER || (self.getSourceType() !== 'hive' && self.getSourceType() !== 'impala')) {
      return $.Deferred().reject().promise();
    }
    if (self.navOptPopularityForChildrenPromise && (!options || !options.refreshCache)) {
      return self.navOptPopularityForChildrenPromise;
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
    self.navOptPopularityForChildrenPromise = new CancellablePromise(deferred.promise(), undefined, cancellablePromises);
    return self.navOptPopularityForChildrenPromise;
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
      && self.isDatabase() || self.isTableOrView() || self.isColumn();
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
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.getComment = function (apiOptions) {
    var self = this;
    var deferred = $.Deferred();
    var cancellablePromises = [];

    var resolveWithSourceMeta = function () {
      if (self.sourceMeta) {
        deferred.resolve(self.sourceMeta && self.sourceMeta.comment || '');
      } else {
        cancellablePromises.push(self.getSourceMeta(apiOptions).done(function (sourceMeta) {
          deferred.resolve(sourceMeta && sourceMeta.comment || '');
        }).fail(deferred.reject));
      }
    };

    if (self.canHaveNavigatorMetadata()) {
      if (self.navigatorMeta) {
        deferred.resolve(self.navigatorMeta.description || self.navigatorMeta.originalDescription || '');
      } else {
        cancellablePromises.push(self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
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

    return new CancellablePromise(deferred.promise(), undefined, cancellablePromises);
  };

  /**
   * Sets the comment in the proper source
   *
   * @param {string} comment
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   *
   * @return {Promise}
   */
  DataCatalogEntry.prototype.setComment = function (comment, apiOptions) {
    var self = this;
    var deferred = $.Deferred();

    if (self.canHaveNavigatorMetadata()) {
      self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
        if (navigatorMeta) {
          ApiHelper.getInstance().updateNavigatorMetadata({
            identity: navigatorMeta.identity,
            properties: {
              description: comment
            }
          }).done(function () {
            reloadNavigatorMeta(self, {
              silenceErrors: apiOptions && apiOptions.silenceErrors,
              refreshCache: true
            }).done(function() {
              self.getComment(apiOptions).done(deferred.resolve);
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
        ApiHelper.getInstance().addNavTags(navMeta.identity, tags).done(function (response) {
          if (response && response.entity) {
            self.navigatorMeta = response.entity;
            self.navigatorMetaPromise = $.Deferred().resolve(self.navigatorMeta).promise();
            self.saveLater();
          } else {
            deferred.reject();
          }
          deferred.resolve(self.navigatorMeta);
        });
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
          ApiHelper.getInstance().deleteNavTags(navMeta.identity, tags).done(function (response) {
            if (response && response.entity) {
              self.navigatorMeta = response.entity;
              self.navigatorMetaPromise = $.Deferred().resolve(self.navigatorMeta).promise();
              self.saveLater();
            } else {
              deferred.reject();
            }
            deferred.resolve(self.navigatorMeta);
          });
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
   * Returns the default tooltip to use for the entry, either the comment if known or the qualified path.
   *
   * @return {string}
   */
  DataCatalogEntry.prototype.getTooltip = function () {
    var self = this;
    return self.getResolvedComment() || self.getTitle();
  };

  /**
   * Returns the default title used for the entry, the qualified path with type for fields.
   *
   * @return {string}
   */
  DataCatalogEntry.prototype.getTitle = function () {
    var self = this;
    var title = self.getQualifiedPath();
    if (self.isField()) {
      var type = self.getType();
      if (type) {
        title += ' (' + type + ')';
      }
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
   * For complex entries the type definition is stripped to either 'array', 'map' or 'struct'
   *
   * @return {string}
   */
  DataCatalogEntry.prototype.getType = function () {
    var self = this;
    var type = self.sourceMeta && self.sourceMeta.type || self.definition.type || '';
    if (type.indexOf('<') !== -1) {
      type = type.substring(0, type.indexOf('<'));
    }
    return type;
  };

  /**
   * Gets the source metadata for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.getSourceMeta = function (options) {
    var self = this;
    if (options && options.cachedOnly) {
      return self.sourceMetaPromise || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return reloadSourceMeta(self, options);
    }
    return self.sourceMetaPromise || reloadSourceMeta(self, options);
  };

  /**
   * Gets the analysis for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache] - Clears the browser cache
   * @param {boolean} [options.refreshAnalysis] - Performs a hard refresh on the source level
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.getAnalysis = function (options) {
    var self = this;
    if (options && options.cachedOnly) {
      return self.analysisPromise || $.Deferred().reject(false).promise();
    }
    if (options && (options.refreshCache || options.refreshAnalysis)) {
      return reloadAnalysis(self, options);
    }
    return self.analysisPromise || reloadAnalysis(self, options);
  };

  /**
   * Gets the Navigator metadata for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors] - Default true
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.getNavigatorMeta = function (options) {
    var self = this;

    if (!options) {
      options = {};
    }
    if (typeof options.silenceErrors === 'undefined') {
      options.silenceErrors = true;
    }
    if (!HAS_NAVIGATOR || (self.getSourceType() !== 'hive' && self.getSourceType() !== 'impala')) {
      return $.Deferred().reject().promise();
    }
    if (options && options.cachedOnly) {
      return self.navigatorMetaPromise || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return reloadNavigatorMeta(self, options);
    }
    return self.navigatorMetaPromise || reloadNavigatorMeta(self, options);
  };

  /**
   * Gets the Nav Opt metadata for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors] - Default true
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.getNavOptMeta = function (options) {
    var self = this;

    if (!options) {
      options = {};
    }
    if (typeof options.silenceErrors === 'undefined') {
      options.silenceErrors = true;
    }
    if (!self.isTableOrView() || !HAS_OPTIMIZER || (self.getSourceType() !== 'hive' && self.getSourceType() !== 'impala')) {
      return $.Deferred().reject().promise();
    }
    if (options && options.cachedOnly) {
      return self.navOptMetaPromise || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return reloadNavOptMeta(self, options);
    }
    return self.navOptMetaPromise || reloadNavOptMeta(self, options);
  };

  /**
   * Gets the sample for the entry. It will fetch it if not cached or if the refresh option is set.
   *
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.getSample = function (options) {
    var self = this;
    if (options && options.cachedOnly) {
      return self.samplePromise || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return reloadSample(self, options);
    }
    return self.samplePromise || reloadSample(self, options);
  };

  var instances = {};

  /**
   * Helepr function to get the DataCatalog instance for a given data source.
   *
   * @param {string} sourceType
   * @return {DataCatalog}
   */
  var getCatalog = function (sourceType) {
    return instances[sourceType] || (instances[sourceType] = new DataCatalog(sourceType));
  };

  if (typeof window.hueDebug === 'undefined') {
    window.hueDebug = {};
  }

  window.hueDebug.fillDataCatalog = function (sourceType, path) {
    if (!path) {
      path = [];
    }

    var options = { silenceErrors: true };

    var loadRecursive = function (entry) {
      var deferred = $.Deferred();
      var promises = [];
      promises.push(entry.getSourceMeta(options));
      promises.push(entry.getSample(options));
      if (entry.hasPossibleChildren()) {
        promises.push(entry.loadNavigatorMetaForChildren(options));
        promises.push(entry.getChildren(options).done(function (childEntries) {
          promises.push(childEntries.forEach(function (childEntry) {
            loadRecursive(childEntry);
          }));
        }));
      }
      $.when.apply($, promises).always(deferred.resolve);
      return deferred.promise();
    };

    var deferred = $.Deferred();
    getCatalog(sourceType).getEntry({ path: path }).done(function (startEntry) {
      startEntry.loadNavigatorMetaForChildren(options);
      loadRecursive(startEntry).always(deferred.resolve);
    });
    return deferred.promise();
  };

  huePubSub.subscribe('data.catalog.refresh.entry', function (options) {
    options.catalogEntry.clear(options.invalidate).always(function () {
      if (options.callback) {
        options.callback();
      }
    });
  });

  var allNavigatorTagsPromise = undefined;

  var sharedDataCalogStore = localforage.createInstance({
    name: 'HueDataCatalog_' + STORAGE_POSTFIX
  });

  return {
    /**
     * @param options
     *
     * @return {DataCatalogEntry}
     */
    getEntry: function (options) {
      return getCatalog(options.sourceType).getEntry(options);
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
     * @return {CancellablePromise}
     */
    getAllNavigatorTags: function (options) {
      if (allNavigatorTagsPromise && (!options || !options.refreshCache)) {
        return allNavigatorTagsPromise;
      }

      var deferred = $.Deferred();
      allNavigatorTagsPromise = deferred.promise();

      var reloadAllTags = function () {
        ApiHelper.getInstance().fetchAllNavigatorTags({
          silenceErrors: options && options.silenceErrors,
        }).done(deferred.resolve).fail(deferred.reject);

        deferred.done(function (allTags) {
          sharedDataCalogStore.setItem('hue.dataCatalog.allNavTags', { allTags: allTags, hueTimestamp: Date.now(), version: DATA_CATALOG_VERSION });
        })
      };

      if (!options || !options.refreshCache) {
        sharedDataCalogStore.getItem('hue.dataCatalog.allNavTags').then(function (storeEntry) {
          if (storeEntry && storeEntry.version === DATA_CATALOG_VERSION && (!storeEntry.hueTimestamp || (Date.now() - storeEntry.hueTimestamp) < CACHEABLE_TTL.default)) {
            deferred.resolve(storeEntry.allTags);
          } else {
            reloadAllTags();
          }
        }).catch(reloadAllTags);
      } else {
        reloadAllTags();
      }

      return allNavigatorTagsPromise;
    },

    updateAllNavigatorTags: function (tagsToAdd, tagsToRemove) {
      if (allNavigatorTagsPromise) {
        allNavigatorTagsPromise.done(function (allTags) {
          tagsToAdd.forEach(function (newTag) {
            if (!allTags[newTag]) {
              allTags[newTag] = 0;
            }
            allTags[newTag]++;
          });
          tagsToRemove.forEach(function (newTag) {
            if (!allTags[tagsToRemove]) {
              allTags[tagsToRemove]--;
              if (allTags[tagsToRemove] === 0) {
                delete allTags[tagsToRemove];
              }
            }
          });
          sharedDataCalogStore.setItem('hue.dataCatalog.allNavTags', { allTags: allTags, hueTimestamp: Date.now(), version: DATA_CATALOG_VERSION });
        });
      }
    },

    enableCache: function () {
      cacheEnabled = true
    },

    disableCache: function () {
      cacheEnabled = false;
    }
  };
})();