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

  /**
   * @param {String} sourceType
   * @constructor
   */
  function DataCatalog(sourceType) {
    var self = this;
    self.sourceType = sourceType;
    self.entries = {};
    self.store = localforage.createInstance({
      name: "HueDataCatalog_" + self.sourceType + '_' + LOGGED_USERNAME // TODO: Add flag for embedded mode
    });
  }

  DataCatalog.prototype.clearStorage = function () {
    var self = this;
    self.store.clear()
  };

  DataCatalog.prototype.updateStore = function (dataCatalogEntry) {
    var self = this;
    self.store.setItem(dataCatalogEntry.getQualifiedPath(), {
      definition: dataCatalogEntry.definition,
      sourceMeta: dataCatalogEntry.sourceMeta,
      sample: dataCatalogEntry.sample,
      navigatorMeta: dataCatalogEntry.navigatorMeta,
      navOptMeta: dataCatalogEntry.navOptMeta
    });
  };

  /**
   *
   * @param {object} options
   * @param {string[][]} options.paths
   * @param {boolean} [options.silenceErrors]
   *
   * @return {CancellablePromise}
   */
  DataCatalog.prototype.loadNavOptMetaForTables = function (options) {
    var self = this;
    var deferred = $.Deferred();
    var cancellablePromises = [];
    var entriesWithNavOptMeta = [];
    var pathsToLoad = [];

    var existingPromises = [];
    options.paths.forEach(function (path) {
      var existingDeferred = $.Deferred();
      self.getEntry({ path: path }).done(function (tableEntry) {
        if (tableEntry.navOptMetaForChildrenPromise) {
          tableEntry.navOptMetaForChildrenPromise.done(function (existingNavOptMetaEntries) {
            entriesWithNavOptMeta = entriesWithNavOptMeta.concat(existingNavOptMetaEntries);
            existingDeferred.resolve();
          }).fail(existingDeferred.reject);
        } else if (tableEntry.definition && tableEntry.definition.navOptLoaded) {
          tableEntry.getChildren({silenceErrors: options.silenceErrors}).done(function (childEntries) {
            childEntries.forEach(function (childEntry) {
              if (childEntry.navOptMeta) {
                entriesWithNavOptMeta.push(childEntry);
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
        cancellablePromises.push(ApiHelper.getInstance().fetchNavOptMetadata({
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
              entry.navOptMetaForChildrenPromise = entry.applyNavOptResponseToChildren(perTable[path], options).done(function (entries) {
                entriesWithNavOptMeta = entriesWithNavOptMeta.concat(entries);
                tableDeferred.resolve();
              }).fail(tableDeferred.resolve);
              cancellablePromises.push(entry.navOptMetaForChildrenPromise);
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
          deferred.resolve(entriesWithNavOptMeta);
        }).fail(deferred.reject);
      });
    });

    return new CancellablePromise(deferred.promise(), cancellablePromises);
  };

  var mergeFromStoreEntry = function (dataCatalogEntry, storeEntry) {
    var mergeAttribute = function (attributeName, ttl, promiseName) {
      if (storeEntry[attributeName] && (!storeEntry[attributeName].hueTimestamp || (Date.now() - storeEntry[attributeName].hueTimestamp) < ttl)) {
        dataCatalogEntry[attributeName] = storeEntry[attributeName];
        if (promiseName) {
          dataCatalogEntry[promiseName] = $.Deferred().resolve(dataCatalogEntry[attributeName]).promise();
        }
      }
    };

    mergeAttribute('definition', CACHEABLE_TTL.default);
    mergeAttribute('sourceMeta', CACHEABLE_TTL.default, 'sourceMetaPromise');
    mergeAttribute('sample', CACHEABLE_TTL.default, 'samplePromise');
    mergeAttribute('navigatorMeta', CACHEABLE_TTL.default, 'navigatorMetaPromise');
    mergeAttribute('navOptMeta', CACHEABLE_TTL.optimizer);
  };

  /**
   * @param {Object} options
   * @param {string|string[]} options.path
   * @param {Object} [options.definition] - The initial definition if not already set on the entry
   * @return {DataCatalogEntry}
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

  var fetchMeta = function (apiHelperFunction, dataCatalogEntry, apiOptions) {
    return ApiHelper.getInstance()[apiHelperFunction]({
      sourceType: dataCatalogEntry.dataCatalog.sourceType,
      path: dataCatalogEntry.path,
      silenceErrors: apiOptions && apiOptions.silenceErrors
    }).done(function () {
      dataCatalogEntry.saveLater();
    })
  };

  /**
   * @param {DataCatalogEntry} dataCatalogEntry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   *
   * @return {CancellablePromise}
   */
  var reloadSourceMeta = function (dataCatalogEntry, apiOptions) {
    dataCatalogEntry.sourceMetaPromise = fetchMeta('fetchSourceMetadata', dataCatalogEntry, apiOptions);
    dataCatalogEntry.sourceMetaPromise.done(function (sourceMeta) {
      dataCatalogEntry.sourceMeta = sourceMeta;
    });
    return dataCatalogEntry.sourceMetaPromise;
  };

  /**
   * @param {DataCatalogEntry} dataCatalogEntry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   *
   * @return {CancellablePromise}
   */
  var reloadNavigatorMeta = function (dataCatalogEntry, apiOptions) {
    if (HAS_NAVIGATOR && (dataCatalogEntry.dataCatalog.sourceType === 'hive' || dataCatalogEntry.dataCatalog.sourceType === 'impala')) {
      dataCatalogEntry.navigatorMetaPromise = fetchMeta('fetchNavigatorMetadata', dataCatalogEntry, apiOptions);
      dataCatalogEntry.navigatorMetaPromise.done(function (navigatorMeta) {
        dataCatalogEntry.navigatorMeta = navigatorMeta;
      });
    } else {
      dataCatalogEntry.navigatorMetaPromise =  $.Deferred.reject().promise();
    }
    return dataCatalogEntry.navigatorMetaPromise;
  };

  /**
   * @param {DataCatalogEntry} dataCatalogEntry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   *
   * @return {CancellablePromise}
   */
  var reloadSample = function (dataCatalogEntry, apiOptions) {
    dataCatalogEntry.samplePromise = fetchMeta('fetchSample', dataCatalogEntry, apiOptions);
    dataCatalogEntry.samplePromise.done(function (sample) {
      dataCatalogEntry.sample = sample;
    });
    return dataCatalogEntry.samplePromise;
  };

  /**
   * @param {DataCatalog} dataCatalog
   * @param {string|string[]} path
   * @param {Object} definition - Initial known metadata on creation
   * @constructor
   */
  function DataCatalogEntry(dataCatalog, path, definition) {
    var self = this;

    self.dataCatalog = dataCatalog;
    self.path = typeof path === 'string' && path ? path.split('.') : path || [];
    self.name = self.path.length ? self.path[self.path.length - 1] : dataCatalog.sourceType;

    self.definition = definition;

    self.sourceMetaPromise = undefined;
    self.sourceMeta = undefined;

    self.navigatorMetaPromise = undefined;
    self.navigatorMeta = undefined;

    self.samplePromise = undefined;
    self.sample = undefined;

    self.navOptMeta = undefined;

    self.navigatorMetaForChildrenPromise = undefined;
    self.navOptMetaForChildrenPromise = undefined;

    self.childrenPromise = undefined;
    self.saveTimeout = -1;
  }

  DataCatalogEntry.prototype.saveLater = function () {
    var self = this;
    window.clearTimeout(self.saveTimeout);
    self.saveTimeout = window.setTimeout(function () {
      self.dataCatalog.updateStore(self);
    }, 1000);
  };

  /**
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   *
   * @return {Promise}
   */
  DataCatalogEntry.prototype.getChildren = function (apiOptions) {
    var self = this;
    if (self.childrenPromise && (!apiOptions || !apiOptions.refreshCache)) {
      return self.childrenPromise;
    }
    var deferred = $.Deferred();
    self.childrenPromise = deferred.promise();
    self.getSourceMeta(apiOptions).done(function (sourceMeta) {
      var promises = [];
      var index = 0;
      var partitionKeys = {};
      if (sourceMeta.partition_keys) {
        sourceMeta.partition_keys.forEach(function (partitionKey) {
          partitionKeys[partitionKey.name] = true;
        })
      }

      var entities = sourceMeta.databases
        || sourceMeta.tables_meta || sourceMeta.extended_columns || sourceMeta.fields || sourceMeta.columns
        || (sourceMeta.value && sourceMeta.value.fields);
      if (entities) {
        entities.forEach(function (entity) {
          promises.push(self.dataCatalog.getEntry({ path: self.path.concat(entity.name || entity) }).done(function (catalogEntry) {
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
        });
      }
      if (self.dataCatalog.sourceType === 'impala' && self.isComplex()) {
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
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.refreshCache]
   * @param {boolean} [apiOptions.silenceErrors]
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.loadNavigatorMetaForChildren = function (apiOptions) {
    var self = this;

    if (self.dataCatalog.sourceType !== 'hive' && self.dataCatalog.sourceType !== 'impala') {
      return $.Deferred().reject().promise();
    }

    if (self.navigatorMetaForChildrenPromise && (!apiOptions || !apiOptions.refreshCache)) {
      return self.navigatorMetaForChildrenPromise;
    }

    var deferred = $.Deferred();

    var cancellablePromises = [];

    cancellablePromises.push(self.getChildren(apiOptions).done(function (children) {
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
        silenceErrors: apiOptions && apiOptions.silenceErrors
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

  DataCatalogEntry.prototype.applyNavOptResponseToChildren = function (response, options) {
    var self = this;
    var deferred = $.Deferred();
    if (!self.definition) {
      self.definition = {};
    }
    self.definition.navOptLoaded = true;
    self.saveLater();


    var childPromise = self.getChildren({ silenceErrors: options.silenceErrors }).done(function (childEntries) {
      var entriesByName = {};
      childEntries.forEach(function (childEntry) {
        entriesByName[childEntry.name.toLowerCase()] = childEntry;
      });
      var updatedIndex = {};

      if (self.isDatabase() && response.top_tables) {
        response.top_tables.forEach(function (topTable) {
          var matchingChild = entriesByName[topTable.name.toLowerCase()];
          if (matchingChild) {
            matchingChild.navOptMeta = topTable;
            matchingChild.saveLater();
            updatedIndex[matchingChild.getQualifiedPath()] = matchingChild;
          }
        });
      } else if (self.isTableOrView() && response.values) {
        var addNavOptMeta = function (columns, type) {
          if (columns) {
            columns.forEach(function (column) {
              var matchingChild = entriesByName[column.columnName.toLowerCase()];
              if (matchingChild) {
                if (!matchingChild.navOptMeta) {
                  matchingChild.navOptMeta = {};
                }
                matchingChild.navOptMeta[type] = column;
                matchingChild.saveLater();
                updatedIndex[matchingChild.getQualifiedPath()] = matchingChild;
              }
            });
          }
        };

        addNavOptMeta(response.values.filterColumns, 'filterColumn');
        addNavOptMeta(response.values.groupbyColumns, 'groupByColumn');
        addNavOptMeta(response.values.joinColumns, 'joinColumn');
        addNavOptMeta(response.values.orderbyColumns, 'orderByColumn');
        addNavOptMeta(response.values.selectColumns, 'selectColumn');
      }
      var entriesWithNavOptMeta = [];
      Object.keys(updatedIndex).forEach(function(path) {
        entriesWithNavOptMeta.push(updatedIndex[path]);
      });
      deferred.resolve(entriesWithNavOptMeta);
    }).fail(deferred.reject);

    return new CancellablePromise(deferred.promise(), undefined, [ childPromise ]);
  };

  /**
   * @param {Object} [options]
   * @param {boolean} [options.refreshCache]
   * @param {boolean} [options.silenceErrors]
   *
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.loadNavOptMetaForChildren = function (options) {
    var self = this;
    if (self.dataCatalog.sourceType !== 'hive' && self.dataCatalog.sourceType !== 'impala') {
      return $.Deferred().reject().promise();
    }
    if (self.navOptMetaForChildrenPromise && (!options || !options.refreshCache)) {
      return self.navOptMetaForChildrenPromise;
    }
    var deferred = $.Deferred();
    var cancellablePromises = [];
    if (self.definition && self.definition.navOptLoaded && (!options || !options.refreshCache)) {
      cancellablePromises.push(self.getChildren(options).done(function (childEntries) {
        deferred.resolve(childEntries.filter(function (entry) { return entry.navOptMeta }));
      }).fail(deferred.reject));
    } else if (self.isDatabase() || self.isTableOrView()) {
      cancellablePromises.push(ApiHelper.getInstance().fetchNavOptMetadata({
        silenceErrors: options && options.silenceErrors,
        refreshCache: options && options.refreshCache,
        paths: [ self.path ]
      }).done(function (data) {
        cancellablePromises.push(self.applyNavOptResponseToChildren(data, options).done(deferred.resolve).fail(deferred.reject));
      }).fail(deferred.reject));
    } else {
      deferred.resolve([]);
    }
    self.navOptMetaForChildrenPromise = new CancellablePromise(deferred.promise(), undefined, cancellablePromises);
    return self.navOptMetaForChildrenPromise;
  };

  DataCatalogEntry.prototype.getKnownComment = function () {
    var self = this;
    if (self.navigatorMeta && (self.dataCatalog.sourceType === 'hive' || self.dataCatalog.sourceType === 'impala')) {
      return self.navigatorMeta.description || self.navigatorMeta.originalDescription || ''
    }
    return self.sourceMeta && self.sourceMeta.comment || '';
  };

  /**
   * @param {Object|boolean} [apiOptions] -
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

    if (HAS_NAVIGATOR && (self.dataCatalog.sourceType === 'hive' || self.dataCatalog.sourceType === 'impala')) {
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

    if (HAS_NAVIGATOR && (self.dataCatalog.sourceType === 'hive' || self.dataCatalog.sourceType === 'impala')) {
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
        sourceType: self.dataCatalog.sourceType,
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

  DataCatalogEntry.prototype.addNavMetaTags = function (tags) {
    var self = this;
    var deferred = $.Deferred();
    if (HAS_NAVIGATOR) {
      self.getNavigatorMeta().done(function (navMeta) {
        if (navMeta && typeof navMeta.identity !== 'undefined') {
        ApiHelper.getInstance().addNavTags(navMeta.identity, tags).done(function (response) {
          if (response && response.entity) {
            self.navigatorMeta = response.entity;
            self.navigatorMetaPromise = $.Deferred().resolve(self.navigatorMeta).promise();
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

  DataCatalogEntry.prototype.deleteNavMetaTags = function (tags) {
    var self = this;
    var deferred = $.Deferred();
    if (HAS_NAVIGATOR) {
      self.getNavigatorMeta().done(function (navMeta) {
        if (navMeta && typeof navMeta.identity !== 'undefined') {
          ApiHelper.getInstance().deleteNavTags(navMeta.identity, tags).done(function (response) {
            if (response && response.entity) {
              self.navigatorMeta = response.entity;
              self.navigatorMetaPromise = $.Deferred().resolve(self.navigatorMeta).promise();
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

  DataCatalogEntry.prototype.hasPossibleChildren = function () {
    var self = this;
    return (!self.definition && !self.sourceMeta) ||
      (self.sourceMeta && /^(?:database|table|view|struct|array|map)/i.test(self.sourceMeta.type)) ||
      (self.definition && /^(?:database|table|view|struct|array|map)/i.test(self.definition.type));
  };

  DataCatalogEntry.prototype.getIndex = function () {
    var self = this;
    return self.definition && self.definition.index ? self.definition.index : 0;
  };

  DataCatalogEntry.prototype.isDatabase = function () {
    var self = this;
    return self.path.length === 1;
  };

  DataCatalogEntry.prototype.isTableOrView = function () {
    var self = this;
    return self.path.length === 2;
  };

  DataCatalogEntry.prototype.getTooltip = function () {
    var self = this;
    return self.getKnownComment() || self.getTitle();
  };

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

  DataCatalogEntry.prototype.getQualifiedPath = function () {
    var self = this;
    return self.path.join('.');
  }

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

  DataCatalogEntry.prototype.isPrimaryKey = function () {
    var self = this;
    return self.isColumn() && self.definition && /true/i.test(self.definition.primary_key);
  };

  DataCatalogEntry.prototype.isPartitionKey = function () {
    var self = this;
    return self.definition && !!self.definition.partitionKey;
  };

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

  DataCatalogEntry.prototype.isView = function () {
    var self = this;
    return self.path.length === 2 &&
      ((self.sourceMeta && self.sourceMeta.is_view) ||
      (self.definition && self.definition.type && self.definition.type.toLowerCase() === 'view'));
  };

  DataCatalogEntry.prototype.isColumn = function () {
    var self = this;
    return self.path.length === 3;
  };

  DataCatalogEntry.prototype.isComplex = function () {
    var self = this;
    return self.path.length > 2 && (
      (self.sourceMeta && /^(?:struct|array|map)/i.test(self.sourceMeta.type)) ||
      (self.definition && /^(?:struct|array|map)/i.test(self.definition.type)));
  };

  DataCatalogEntry.prototype.isField = function () {
    var self = this;
    return self.path.length > 2;
  };

  DataCatalogEntry.prototype.isArray = function () {
    var self = this;
    return (self.sourceMeta && /^array/i.test(self.sourceMeta.type)) ||
      (self.definition && /^array/i.test(self.definition.type));
  };

  DataCatalogEntry.prototype.isMap = function () {
    var self = this;
    return (self.sourceMeta && /^map/i.test(self.sourceMeta.type)) ||
      (self.definition && /^map/i.test(self.definition.type));
  };

  DataCatalogEntry.prototype.isMapValue = function () {
    var self = this;
    return self.definition && self.definition.isMapValue;
  };

  DataCatalogEntry.prototype.getType = function () {
    var self = this;
    var type = self.sourceMeta && self.sourceMeta.type || self.definition.type || '';
    if (type.indexOf('<') !== -1) {
      type = type.substring(0, type.indexOf('<'));
    }
    return type;
  };

  /**
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
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
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
   * @return {CancellablePromise}
   */
  DataCatalogEntry.prototype.getNavigatorMeta = function (options) {
    var self = this;
    if (self.dataCatalog.sourceType !== 'hive' && self.dataCatalog.sourceType !== 'impala') {
      return $.Deferred().reject().promise();
    }
    if (options && options.cachedOnly) {
      return self.navigatorMetaPromise || $.Deferred().reject(false).promise();
    }
    if (options && options.refreshCache) {
      return reloadNavigatorMeta(self, options);
    }
    return self.navigatorMetaPromise || reloadNavigatorMeta(self, options)
  };

  /**
   * @param {Object} [options]
   * @param {boolean} [options.silenceErrors]
   * @param {boolean} [options.cachedOnly]
   * @param {boolean} [options.refreshCache]
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
    return self.samplePromise || reloadSample(self, options)
  };

  var instances = {};

  /**
   * @param {string} sourceType
   * @return {DataCatalog}
   */
  var getCatalog = function (sourceType) {
    return instances[sourceType] || (instances[sourceType] = new DataCatalog(sourceType));
  };

  return {
    getEntry: function (options) {
      return getCatalog(options.sourceType).getEntry(options);
    },
    getCatalog : getCatalog
  };
})();