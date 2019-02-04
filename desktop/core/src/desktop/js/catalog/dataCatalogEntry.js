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

import apiHelper from '../api/apiHelper'
import CancellablePromise from '../api/cancellablePromise'
import catalogUtils from './catalogUtils'
import huePubSub from '../utils/huePubSub'


/**
 * Helper function to reload the source meta for the given entry
 *
 * @param {DataCatalogEntry} dataCatalogEntry
 * @param {Object} [options]
 * @param {boolean} [options.silenceErrors]
 *
 * @return {CancellablePromise}
 */
const reloadSourceMeta = function (dataCatalogEntry, options) {
  if (dataCatalogEntry.dataCatalog.invalidatePromise) {
    let deferred = $.Deferred();
    let cancellablePromises = [];
    dataCatalogEntry.dataCatalog.invalidatePromise.always(function () {
      cancellablePromises.push(catalogUtils.fetchAndSave('fetchSourceMetadata', 'sourceMeta', dataCatalogEntry, options).done(deferred.resolve).fail(deferred.reject))
    });
    return dataCatalogEntry.trackedPromise('sourceMetaPromise', new CancellablePromise(deferred, undefined, cancellablePromises));
  }

  return dataCatalogEntry.trackedPromise('sourceMetaPromise', catalogUtils.fetchAndSave('fetchSourceMetadata', 'sourceMeta', dataCatalogEntry, options));
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
const reloadNavigatorMeta = function (dataCatalogEntry, apiOptions) {
  if (dataCatalogEntry.canHaveNavigatorMetadata()) {
    return dataCatalogEntry.trackedPromise('navigatorMetaPromise', catalogUtils.fetchAndSave('fetchNavigatorMetadata', 'navigatorMeta', dataCatalogEntry, apiOptions)).done(function (navigatorMeta) {
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
const reloadAnalysis = function (dataCatalogEntry, apiOptions) {
  return dataCatalogEntry.trackedPromise('analysisPromise',
    catalogUtils.fetchAndSave(apiOptions && apiOptions.refreshAnalysis ? 'refreshAnalysis' : 'fetchAnalysis', 'analysis', dataCatalogEntry, apiOptions));
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
const reloadPartitions = function (dataCatalogEntry, apiOptions) {
  return dataCatalogEntry.trackedPromise('partitionsPromise', catalogUtils.fetchAndSave('fetchPartitions', 'partitions', dataCatalogEntry, apiOptions));
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
const reloadSample = function (dataCatalogEntry, apiOptions) {
  return dataCatalogEntry.trackedPromise('samplePromise', catalogUtils.fetchAndSave('fetchSample', 'sample', dataCatalogEntry, apiOptions));
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
const reloadNavOptMeta = function (dataCatalogEntry, apiOptions) {
  if (dataCatalogEntry.dataCatalog.canHaveNavOptMetadata()) {
    return dataCatalogEntry.trackedPromise('navOptMetaPromise', catalogUtils.fetchAndSave('fetchNavOptMeta', 'navOptMeta', dataCatalogEntry, apiOptions));
  }
  dataCatalogEntry.navOptMetaPromise =  $.Deferred.reject().promise();
  return dataCatalogEntry.navOptMetaPromise;
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
const getFromMultiTableCatalog = function (catalogEntry, options, functionName) {
  let deferred = $.Deferred();
  if (!catalogEntry.isTableOrView()) {
    return deferred.reject();
  }
  let cancellablePromises = [];
  catalogEntry.dataCatalog.getMultiTableEntry({ namespace: catalogEntry.namespace, compute: catalogEntry.compute, paths: [ catalogEntry.path ] }).done(function (multiTableEntry) {
    cancellablePromises.push(multiTableEntry[functionName](options).done(deferred.resolve).fail(deferred.reject));
  }).fail(deferred.reject);
  return new CancellablePromise(deferred, undefined, cancellablePromises);
};

/**
 * @param {DataCatalog} options.dataCatalog
 * @param {string|string[]} options.path
 * @param {ContextNamespace} options.namespace - The context namespace
 * @param {ContextCompute} options.compute - The context compute
 * @param {Object} options.definition - Initial known metadata on creation (normally comes from the parent entry)
 * @param {boolean} [options.isTemporary] - Default false
 *
 * @constructor
 */
class DataCatalogEntry {
  
  constructor(options) {
    let self = this;

    self.namespace = options.namespace;
    self.compute = options.compute;
    self.dataCatalog = options.dataCatalog;
    self.path = typeof options.path === 'string' && options.path ? options.path.split('.') : options.path || [];
    self.name = self.path.length ? self.path[self.path.length - 1] : options.dataCatalog.sourceType;
    self.isTemporary = options.isTemporary;

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
  reset() {
    let self = this;
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
      let parent = self.dataCatalog.getKnownEntry({ namespace: self.namespace, compute: self.compute, path: self.path.slice(0, self.path.length - 1) });
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
  trackedPromise(promiseName, cancellablePromise) {
    let self = this;
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
   * @param {boolean} [options.silenceErrors] - Default false
   * @return {CancellablePromise}
   */
  clearCache(options) {
    let self = this;

    if (!options) {
      options = {}
    }

    let invalidatePromise;
    let invalidate = options.invalidate || 'cache';

    if (invalidate !== 'cache' && self.getSourceType() === 'impala') {
      if (window.IS_K8S_ONLY) {
        invalidate = 'invalidateAndFlush';
      }
      if (self.dataCatalog.invalidatePromise) {
        invalidatePromise = self.dataCatalog.invalidatePromise;
      } else {
        invalidatePromise = apiHelper.invalidateSourceMetadata({
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
    let saveDeferred = options.cascade ? self.dataCatalog.clearStorageCascade(self.namespace, self.compute, self.path) : self.save();

    let clearPromise = $.when(invalidatePromise, saveDeferred);

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
  save() {
    let self = this;
    window.clearTimeout(self.saveTimeout);
    return self.dataCatalog.persistCatalogEntry(self);
  };

  /**
   * Save the entry at a later point of time
   */
  saveLater() {
    let self = this;
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
   * @return {CancellablePromise}
   */
  getChildren(options) {
    let self = this;
    if (self.childrenPromise && (!options || !options.refreshCache)) {
      return catalogUtils.applyCancellable(self.childrenPromise, options);
    }
    let deferred = $.Deferred();

    if (options && options.cachedOnly && !self.sourceMeta && !self.sourceMetaPromise) {
      return deferred.reject(false).promise();
    }

    let sourceMetaPromise = self.getSourceMeta(options).done(function (sourceMeta) {
      if (!sourceMeta || sourceMeta.notFound) {
        deferred.reject();
        return;
      }
      let promises = [];
      let index = 0;
      let partitionKeys = {};
      if (sourceMeta.partition_keys) {
        sourceMeta.partition_keys.forEach(function (partitionKey) {
          partitionKeys[partitionKey.name] = true;
        })
      }

      let entities = sourceMeta.databases
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
                let definition = typeof entity === 'object' ? entity : {};
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
                let definition = sourceMeta[path];
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

    return catalogUtils.applyCancellable(self.trackedPromise('childrenPromise', new CancellablePromise(deferred, undefined, [ sourceMetaPromise ])), options);
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
  loadNavigatorMetaForChildren(options) {
    let self = this;

    options = catalogUtils.setSilencedErrors(options);

    if (!self.canHaveNavigatorMetadata() || self.isField()) {
      return $.Deferred().reject().promise();
    }

    if (self.navigatorMetaForChildrenPromise && (!options || !options.refreshCache)) {
      return catalogUtils.applyCancellable(self.navigatorMetaForChildrenPromise, options);
    }

    let deferred = $.Deferred();

    let cancellablePromises = [];

    cancellablePromises.push(self.getChildren(options).done(function (children) {
      let someHaveNavMeta = children.some(function (childEntry) { return childEntry.navigatorMeta });
      if (someHaveNavMeta && (!options || !options.refreshCache)) {
        deferred.resolve(children);
        return;
      }

      let query;
      // TODO: Add sourceType to nav search query
      if (self.path.length) {
        query = 'parentPath:"/' + self.path.join('/') + '" AND type:(table view field)';
      } else {
        query = 'type:database'
      }

      let rejectUnknown = () => {
        children.forEach(function (childEntry) {
          if (!childEntry.navigatorMeta) {
            childEntry.navigatorMeta = {};
            childEntry.navigatorMetaPromise = $.Deferred().reject().promise();
          }
        });
      };

      cancellablePromises.push(apiHelper.searchEntities({
        query: query,
        rawQuery: true,
        limit: children.length,
        silenceErrors: options && options.silenceErrors
      }).done(function (result) {
        if (result && result.entities) {
          let childEntryIndex = {};
          children.forEach(function (childEntry) {
            childEntryIndex[childEntry.name.toLowerCase()] = childEntry;
          });

          result.entities.forEach(function (entity) {
            let matchingChildEntry = childEntryIndex[(entity.original_name || entity.originalName).toLowerCase()];
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

    return catalogUtils.applyCancellable(self.trackedPromise('navigatorMetaForChildrenPromise', new CancellablePromise(deferred, null, cancellablePromises)), options);
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
  applyNavOptResponseToChildren(response, options) {
    let self = this;
    let deferred = $.Deferred();
    if (!self.definition) {
      self.definition = {};
    }
    self.definition.navOptLoaded = true;
    self.saveLater();

    let childPromise = self.getChildren(options).done(function (childEntries) {
      let entriesByName = {};
      childEntries.forEach(function (childEntry) {
        entriesByName[childEntry.name.toLowerCase()] = childEntry;
      });
      let updatedIndex = {};

      if (self.isDatabase() && response.top_tables) {
        response.top_tables.forEach(function (topTable) {
          let matchingChild = entriesByName[topTable.name.toLowerCase()];
          if (matchingChild) {
            matchingChild.navOptPopularity = topTable;
            matchingChild.saveLater();
            updatedIndex[matchingChild.getQualifiedPath()] = matchingChild;
          }
        });
      } else if (self.isTableOrView() && response.values) {
        let addNavOptPopularity = function (columns, type) {
          if (columns) {
            columns.forEach(function (column) {
              let matchingChild = entriesByName[column.columnName.toLowerCase()];
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
      let popularEntries = [];
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
  loadNavOptPopularityForChildren(options) {
    let self = this;

    options = catalogUtils.setSilencedErrors(options);

    if (!self.dataCatalog.canHaveNavOptMetadata()) {
      return $.Deferred().reject().promise();
    }
    if (self.navOptPopularityForChildrenPromise && (!options || !options.refreshCache)) {
      return catalogUtils.applyCancellable(self.navOptPopularityForChildrenPromise, options);
    }
    let deferred = $.Deferred();
    let cancellablePromises = [];
    if (self.definition && self.definition.navOptLoaded && (!options || !options.refreshCache)) {
      cancellablePromises.push(self.getChildren(options).done(function (childEntries) {
        deferred.resolve(childEntries.filter(function (entry) { return entry.navOptPopularity }));
      }).fail(deferred.reject));
    } else if (self.isDatabase() || self.isTableOrView()) {
      cancellablePromises.push(apiHelper.fetchNavOptPopularity({
        silenceErrors: options && options.silenceErrors,
        refreshCache: options && options.refreshCache,
        paths: [ self.path ]
      }).done(function (data) {
        cancellablePromises.push(self.applyNavOptResponseToChildren(data, options).done(deferred.resolve).fail(deferred.reject));
      }).fail(deferred.reject));
    } else {
      deferred.resolve([]);
    }

    return catalogUtils.applyCancellable(self.trackedPromise('navOptPopularityForChildrenPromise', new CancellablePromise(deferred, undefined, cancellablePromises)), options);
  };

  /**
   * Returns true if the catalog entry can have navigator metadata
   *
   * @return {boolean}
   */
  canHaveNavigatorMetadata() {
    let self = this;
    return window.HAS_NAVIGATOR
      && (self.getSourceType() === 'hive' || self.getSourceType() === 'impala')
      && (self.isDatabase() || self.isTableOrView() || self.isColumn());
  };

  /**
   * Returns the currently known comment without loading any additional metadata
   *
   * @return {string}
   */
  getResolvedComment() {
    let self = this;
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
  getCommentObservable() {
    let self = this;
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
  hasResolvedComment() {
    let self = this;
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
  getComment(options) {
    let self = this;
    let deferred = $.Deferred();
    let cancellablePromises = [];

    let resolveWithSourceMeta = function () {
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

    return catalogUtils.applyCancellable(new CancellablePromise(deferred, undefined, cancellablePromises), options);
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
  updateNavigatorCustomMetadata(modifiedCustomMetadata, deletedCustomMetadataKeys, apiOptions) {
    let self = this;
    let deferred = $.Deferred();

    if (self.canHaveNavigatorMetadata()) {
      if (self.navigatorMeta === {} || (self.navigatorMeta && typeof self.navigatorMeta.identity === 'undefined')) {
        if (!apiOptions) {
          apiOptions = {};
        }
        apiOptions.refreshCache = true;
      }
      self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
        if (navigatorMeta) {
          apiHelper.updateNavigatorProperties({
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
  setComment(comment, apiOptions) {
    let self = this;
    let deferred = $.Deferred();

    if (self.canHaveNavigatorMetadata()) {
      if (self.navigatorMeta === {} || (self.navigatorMeta && typeof self.navigatorMeta.identity === 'undefined')) {
        if (!apiOptions) {
          apiOptions = {};
        }
        apiOptions.refreshCache = true;
      }
      self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
        if (navigatorMeta) {
          apiHelper.updateNavigatorProperties({
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
      apiHelper.updateSourceMetadata({
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
  addNavigatorTags(tags) {
    let self = this;
    let deferred = $.Deferred();
    if (self.canHaveNavigatorMetadata()) {
      self.getNavigatorMeta().done(function (navMeta) {
        if (navMeta && typeof navMeta.identity !== 'undefined') {
          apiHelper.addNavTags(navMeta.identity, tags).done(function (entity) {
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
  deleteNavigatorTags(tags) {
    let self = this;
    let deferred = $.Deferred();
    if (self.canHaveNavigatorMetadata()) {
      self.getNavigatorMeta().done(function (navMeta) {
        if (navMeta && typeof navMeta.identity !== 'undefined') {
          apiHelper.deleteNavTags(navMeta.identity, tags).done(function (entity) {
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
  hasPossibleChildren() {
    let self = this;
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
  getIndex() {
    let self = this;
    return self.definition && self.definition.index ? self.definition.index : 0;
  };

  /**
   * Returns the source type of this entry.
   *
   * @return {string} - 'impala', 'hive', 'solr', etc.
   */
  getSourceType() {
    let self = this;
    return self.dataCatalog.sourceType;
  };

  /**
   * Returns true if the entry represents a data source.
   *
   * @return {boolean}
   */
  isSource() {
    let self = this;
    return self.path.length === 0;
  };

  /**
   * Returns true if the entry is a database.
   *
   * @return {boolean}
   */
  isDatabase() {
    let self = this;
    return self.path.length === 1;
  };

  /**
   * Returns true if the entry is a table or a view.
   *
   * @return {boolean}
   */
  isTableOrView() {
    let self = this;
    return self.path.length === 2;
  };

  /**
   * Returns the default title used for the entry, the qualified path with type for fields. Optionally include
   * the comment after, if already resolved.
   *
   * @param {boolean} [includeComment] - Default false
   * @return {string}
   */
  getTitle(includeComment) {
    let self = this;
    let title = self.getQualifiedPath();
    if (self.isField()) {
      let type = self.getType();
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
  getQualifiedPath() {
    let self = this;
    return self.path.join('.');
  };

  /**
   * Returns the display name for the entry, name or qualified path plus type for fields
   *
   * @param {boolean} qualified - Whether to use the qualified path or not, default false
   * @return {string}
   */
  getDisplayName(qualified) {
    let self = this;
    let displayName = qualified ? self.getQualifiedPath() : self.name;
    if (self.isField()) {
      let type = self.getType();
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
  isPrimaryKey() {
    let self = this;
    return self.isColumn() && self.definition && /true/i.test(self.definition.primary_key);
  };

  /**
   * Returns true if the entry is a partition key. Note that the definition has to come from a parent entry, i.e.
   * getChildren().
   *
   * @return {boolean}
   */
  isPartitionKey() {
    let self = this;
    return self.definition && !!self.definition.partitionKey;
  };

  /**
   * Returns true if the entry is a table. It will be accurate once the source meta has been loaded.
   *
   * @return {boolean}
   */
  isTable() {
    let self = this;
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
  isView() {
    let self = this;
    return self.path.length === 2 &&
      ((self.sourceMeta && self.sourceMeta.is_view) ||
        (self.definition && self.definition.type && self.definition.type.toLowerCase() === 'view'));
  };

  /**
   * Returns true if the entry is a column.
   *
   * @return {boolean}
   */
  isColumn() {
    let self = this;
    return self.path.length === 3;
  };

  /**
   * Returns true if the entry is a column. It will be accurate once the source meta has been loaded or if loaded from
   * a parent entry via getChildren().
   *
   * @return {boolean}
   */
  isComplex() {
    let self = this;
    return self.path.length > 2 && (
      (self.sourceMeta && /^(?:struct|array|map)/i.test(self.sourceMeta.type)) ||
      (self.definition && /^(?:struct|array|map)/i.test(self.definition.type)));
  };

  /**
   * Returns true if the entry is a field, i.e. column or child of a complex type.
   *
   * @return {boolean}
   */
  isField() {
    let self = this;
    return self.path.length > 2;
  };

  /**
   * Returns true if the entry is an array. It will be accurate once the source meta has been loaded or if loaded from
   * a parent entry via getChildren().
   *
   * @return {boolean}
   */
  isArray() {
    let self = this;
    return (self.sourceMeta && /^array/i.test(self.sourceMeta.type)) ||
      (self.definition && /^array/i.test(self.definition.type));
  };

  /**
   * Returns true if the entry is a map. It will be accurate once the source meta has been loaded or if loaded from
   * a parent entry via getChildren().
   *
   * @return {boolean}
   */
  isMap() {
    let self = this;
    return (self.sourceMeta && /^map/i.test(self.sourceMeta.type)) ||
      (self.definition && /^map/i.test(self.definition.type));
  };

  /**
   * Returns true if the entry is a map value. It will be accurate once the source meta has been loaded or if loaded
   * from a parent entry via getChildren().
   *
   * @return {boolean}
   */
  isMapValue() {
    let self = this;
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
  getType() {
    let self = this;
    let type = self.getRawType();
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
  getRawType() {
    let self = this;
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
  getSourceMeta(options) {
    let self = this;
    if (options && options.cachedOnly) {
      return catalogUtils.applyCancellable(self.sourceMetaPromise, options) || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return catalogUtils.applyCancellable(reloadSourceMeta(self, options));
    }
    return catalogUtils.applyCancellable(self.sourceMetaPromise || reloadSourceMeta(self, options), options);
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
  getAnalysis(options) {
    let self = this;
    if (options && options.cachedOnly) {
      return catalogUtils.applyCancellable(self.analysisPromise, options) || $.Deferred().reject(false).promise();
    }
    if (options && (options.refreshCache || options.refreshAnalysis)) {
      return catalogUtils.applyCancellable(reloadAnalysis(self, options), options);
    }
    return catalogUtils.applyCancellable(self.analysisPromise || reloadAnalysis(self, options), options);
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
  getPartitions(options) {
    let self = this;
    if (!self.isTableOrView()) {
      return $.Deferred().reject(false).promise();
    }
    if (options && options.cachedOnly) {
      return catalogUtils.applyCancellable(self.partitionsPromise, options) || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return catalogUtils.applyCancellable(reloadPartitions(self, options), options);
    }
    return catalogUtils.applyCancellable(self.partitionsPromise || reloadPartitions(self, options), options);
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
  getNavigatorMeta(options) {
    let self = this;

    options = catalogUtils.setSilencedErrors(options);

    if (!self.canHaveNavigatorMetadata()) {
      return $.Deferred().reject().promise();
    }
    if (options && options.cachedOnly) {
      return catalogUtils.applyCancellable(self.navigatorMetaPromise, options) || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return catalogUtils.applyCancellable(reloadNavigatorMeta(self, options), options);
    }
    return catalogUtils.applyCancellable(self.navigatorMetaPromise || reloadNavigatorMeta(self, options), options)
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
  getNavOptMeta(options) {
    let self = this;

    options = catalogUtils.setSilencedErrors(options);

    if (!self.dataCatalog.canHaveNavOptMetadata() || !self.isTableOrView()) {
      return $.Deferred().reject().promise();
    }
    if (options && options.cachedOnly) {
      return catalogUtils.applyCancellable(self.navOptMetaPromise, options) || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return catalogUtils.applyCancellable(reloadNavOptMeta(self, options), options);
    }
    return catalogUtils.applyCancellable(self.navOptMetaPromise || reloadNavOptMeta(self, options), options);
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
  getSample(options) {
    let self = this;

    // This prevents caching of any non-standard sample queries, i.e. DISTINCT etc.
    if (options && options.operation && options.operation !== 'default') {
      return catalogUtils.applyCancellable(apiHelper.fetchSample({
        sourceType: self.dataCatalog.sourceType,
        compute: self.compute,
        path: self.path,
        silenceErrors: options && options.silenceErrors,
        operation: options.operation
      }), options);
    }

    // Check if parent has a sample that we can reuse
    if (!self.samplePromise && self.isColumn()) {
      let deferred = $.Deferred();
      let cancellablePromises = [];

      let revertToSpecific = function () {
        if (options && options.cachedOnly) {
          deferred.reject();
        } else {
          cancellablePromises.push(catalogUtils.applyCancellable(reloadSample(self, options), options).done(deferred.resolve).fail(deferred.reject));
        }
      };

      self.dataCatalog.getEntry({ namespace: self.namespace, compute: self.compute, path: self.path.slice(0, 2), definition: { type: 'table' } }).done(function (tableEntry) {
        if (tableEntry && tableEntry.samplePromise) {
          cancellablePromises.push(catalogUtils.applyCancellable(tableEntry.samplePromise, options));

          tableEntry.samplePromise.done(function (parentSample) {
            let colSample = {
              hueTimestamp: parentSample.hueTimestamp,
              has_more: parentSample.has_more,
              type: parentSample.type,
              data: [],
              meta: []
            };
            if (parentSample.meta) {
              for (let i = 0; i < parentSample.meta.length; i++) {
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

      return catalogUtils.applyCancellable(self.trackedPromise('samplePromise', new CancellablePromise(deferred, undefined, cancellablePromises)), options);
    }

    if (options && options.cachedOnly) {
      return catalogUtils.applyCancellable(self.samplePromise, options) || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return catalogUtils.applyCancellable(reloadSample(self, options), options);
    }
    return catalogUtils.applyCancellable(self.samplePromise || reloadSample(self, options), options);
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
  getTopAggs(options) {
    let self = this;
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
  getTopFilters(options) {
    let self = this;
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
  getTopJoins(options) {
    let self = this;
    return getFromMultiTableCatalog(self, options, 'getTopJoins');
  };
}


export default DataCatalogEntry;