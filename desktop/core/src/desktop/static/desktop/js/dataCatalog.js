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
  }

  /**
   * @param {string|string[]} path
   * @return {DataCatalogEntry}
   */
  DataCatalog.prototype.getEntry = function (path) {
    var self = this;
    var identifier = typeof path === 'string' ? path : (typeof path === 'string' ? path : path.join('.'));
    return self.entries[identifier] || (self.entries[identifier] = new DataCatalogEntry(self, path));
  };

  /**
   * @param {DataCatalogEntry} dataCatalogEntry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  var reloadSourceMeta = function (dataCatalogEntry, apiOptions) {
    var deferred = $.Deferred();
    ApiHelper.getInstance().fetchSourceMetadata({
      sourceType: dataCatalogEntry.dataCatalog.sourceType,
      path: dataCatalogEntry.path,
      silenceErrors: apiOptions && apiOptions.silenceErrors,
      cachedOnly: apiOptions && apiOptions.cachedOnly,
      refreshCache: apiOptions && apiOptions.refreshCache
    }).done(function (data) {
      dataCatalogEntry.sourceMeta = data;
      deferred.resolve(data);
    }).fail(deferred.reject);
    dataCatalogEntry.lastSourceMetaPromise = deferred.promise();
    return dataCatalogEntry.lastSourceMetaPromise;
  };

  /**
   * @param {DataCatalogEntry} dataCatalogEntry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  var reloadNavigatorMeta = function (dataCatalogEntry, apiOptions) {
    var deferred = $.Deferred();
    if (HAS_NAVIGATOR) {
      ApiHelper.getInstance().fetchNavigatorMetadata({
        path: dataCatalogEntry.path,
        silenceErrors: apiOptions && apiOptions.silenceErrors,
        cachedOnly: apiOptions && apiOptions.cachedOnly,
        refreshCache: apiOptions && apiOptions.refreshCache
      }).done(function (data) {
        dataCatalogEntry.navigatorMeta = data;
        deferred.resolve(data);
      }).fail(deferred.reject);
    } else {
      deferred.reject();
    }
    dataCatalogEntry.lastNavigatorMetaPromise = deferred.promise();
    return dataCatalogEntry.lastNavigatorMetaPromise;
  };

  /**
   * @param {DataCatalog} dataCatalog
   * @param {string|string[]} path
   * @constructor
   */
  function DataCatalogEntry(dataCatalog, path) {
    var self = this;

    self.dataCatalog = dataCatalog;
    self.path = typeof path === 'string' && path ? path.split('.') : path || [];
    self.name = self.path.length ? self.path[self.path.length - 1] : dataCatalog.sourceType;

    self.definition = undefined;
    self.lastSourceMetaPromise = undefined;
    self.sourceMeta = undefined;
    self.lastNavigatorMetaPromise = undefined;
    self.navigatorMeta = undefined;

    self.children = undefined;
  }

  /**
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  DataCatalogEntry.prototype.getChildren = function (apiOptions) {
    var self = this;
    var deferred = $.Deferred();
    if (self.children) {
      deferred.resolve(self.children);
    } else {
      self.getSourceMeta(apiOptions).done(function (sourceMeta) {
        if (self.children) {
          deferred.resolve(self.children);
        } else {
          self.children = [];
          var index = 0;
          var entities = sourceMeta.databases || sourceMeta.tables_meta || sourceMeta.extended_columns || sourceMeta.fields;
          if (entities) {
            entities.forEach(function (entity) {
              var catalogEntry = self.dataCatalog.getEntry(self.path.concat(entity.name || entity));
              if (!catalogEntry.definition && typeof entity === 'object') {
                catalogEntry.definition = entity;
                catalogEntry.definition.index = index++;
              }
              self.children.push(catalogEntry);
            });
          } else {
            (sourceMeta.type === 'map' ? ['key', 'value'] : ['item']).forEach(function (path) {
              if (sourceMeta[path]) {
                var catalogEntry = self.dataCatalog.getEntry(self.path.concat(path));
                if (!catalogEntry.definition) {
                  catalogEntry.definition = sourceMeta[path];
                  catalogEntry.definition.index = index++;
                  catalogEntry.definition.isMapValue = path === 'value'
                }
                self.children.push(catalogEntry);
              }
            })
          }
          deferred.resolve(self.children);
        }
      })
    }
    return deferred.promise();
  };

  /**
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @return {Promise}
   */
  DataCatalogEntry.prototype.loadNavigatorMetaForChildren = function (apiOptions) {
    var self = this;
    var deferred = $.Deferred();
    self.getChildren().done(function (children) {
      var query;

      // TODO: Add sourceType to nav search query
      if (self.path.length) {
        query = 'parentPath:"/' + self.path.join('/') + '" AND type:(table view field)';
      } else {
        query = 'type:database'
      }

      ApiHelper.getInstance().searchEntities({
        query: query,
        rawQuery: true,
        limit: children.length,
        silenceErrors: apiOptions && apiOptions.silenceErrors
      }).done(function (result) {
        if (result && result.entities && result.entities.length > 0) {
          var entityIndex = {};
          result.entities.forEach(function (entity) {
            entityIndex[entity.name || entity.originalName] = entity;
          });
          children.forEach(function (child) {
            var name = child.path[child.path.length - 1];
            if (entityIndex[name]) {
              child.navigatorMeta = entityIndex[name];
              child.lastNavigatorMetaPromise = $.Deferred().resolve(child.navigatorMeta).promise();
            }
          });
          deferred.resolve(children);
        }
      }).fail(deferred.reject);
    });
    return deferred.promise();
  };

  /**
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  DataCatalogEntry.prototype.getComment = function (apiOptions) {
    var self = this;
    var deferred = $.Deferred();

    var resolveWithSourceMeta = function () {
      if (self.sourceMeta) {
        deferred.resolve(self.sourceMeta && self.sourceMeta.comment || '');
      } else {
        self.getSourceMeta(apiOptions).done(function (sourceMeta) {
          deferred.resolve(sourceMeta && sourceMeta.comment || '');
        }).fail(deferred.reject);
      }
    };

    if (HAS_NAVIGATOR) {
      if (self.navigatorMeta && self.navigatorMeta.entity) {
        deferred.resolve(self.navigatorMeta.entity.description || self.navigatorMeta.entity.originalDescription || '');
      } else {
        self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
          if (navigatorMeta && navigatorMeta.entity) {
            deferred.resolve(navigatorMeta.entity.description || navigatorMeta.entity.originalDescription || '');
          } else {
            resolveWithSourceMeta();
          }
        }).fail(resolveWithSourceMeta)
      }
    } else {
      resolveWithSourceMeta();
    }

    return deferred.promise();
  };

  /**
   * @param {string} comment
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  DataCatalogEntry.prototype.setComment = function (comment, apiOptions) {
    var self = this;
    var deferred = $.Deferred();

    if (HAS_NAVIGATOR) {
      self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
        if (navigatorMeta && navigatorMeta.entity) {
          ApiHelper.getInstance().updateNavigatorMetadata({
            identity: navigatorMeta.entity.identity,
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

  DataCatalogEntry.prototype.hasPossibleChildren = function () {
    var self = this;
    return (!self.definition && !self.sourceMeta) ||
      (self.sourceMeta && /^(?:table|view|struct|array|map)/i.test(self.sourceMeta.type)) ||
      (self.definition && /^(?:table|view|struct|array|map)/i.test(self.definition.type));
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


  DataCatalogEntry.prototype.getTitle = function () {
    var self = this;
    var title = self.path.join('.');
    if (self.isField()) {
      var type = self.getType();
      if (type) {
        if (~type.indexOf('<')) {
          type = type.substring(0, type.indexOf('<'));
        }
        title += ' (' + type + ')';
      }
    }
    return title;
  };

  DataCatalogEntry.prototype.getDisplayName = function () {
    var self = this;
    var displayName = self.name;
    if (self.isField()) {
      var type = self.getType();
      if (type) {
        if (~type.indexOf('<')) {
          type = type.substring(0, type.indexOf('<'));
        }
        displayName += ' (' + type + ')';
      }
    }
    return displayName;
  };

  DataCatalogEntry.prototype.isPrimaryKey = function () {
    var self = this;
    return self.isColumn() && self.definition && /true/i.test(self.definition.primary_key);
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
    return (self.definition && self.definition.type && self.definition.type.toLowerCase() === 'array') ||
      (self.sourceMeta && self.sourceMeta.type && self.sourceMeta.type.toLowerCase() === 'array');
  };

  DataCatalogEntry.prototype.isMapValue = function () {
    var self = this;
    return self.definition && self.definition.isMapValue;
  };

  DataCatalogEntry.prototype.getType = function () {
    var self = this;
    if (self.sourceMeta) {
      return self.sourceMeta.type;
    }
    if (self.definition) {
      return self.definition.type;
    }
  };

  /**
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  DataCatalogEntry.prototype.getSourceMeta = function (apiOptions) {
    var self = this;
    return self.lastSourceMetaPromise || reloadSourceMeta(self, apiOptions);
  };

  /**
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  DataCatalogEntry.prototype.getNavigatorMeta = function (apiOptions) {
    var self = this;
    return self.lastNavigatorMetaPromise || reloadNavigatorMeta(self, apiOptions)
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
      return getCatalog(options.sourceType).getEntry(options.path);
    }
  };
})();