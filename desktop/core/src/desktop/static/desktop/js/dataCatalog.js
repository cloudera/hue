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


  function DataCatalog(sourceType) {
    var self = this;
    self.sourceType = sourceType;

  }

  DataCatalog.prototype.getEntry = function (options) {
    var self = this;
    return new DataCatalogEntry(self, options);
  };

  var reloadSourceMeta = function (dataCatalogEntry, refreshCache) {
    dataCatalogEntry.lastSourcePromise = $.Deferred();
    ApiHelper.getInstance().fetchSourceMetadata({
      sourceType: dataCatalogEntry.dataCatalog.sourceType,
      path: dataCatalogEntry.path,
      silenceErrors: dataCatalogEntry.silenceErrors,
      cachedOnly: dataCatalogEntry.cachedOnly,
      refreshCache: refreshCache
    }).done(function (data) {
      dataCatalogEntry.lastSourcePromise.resolve(data);
    }).fail(function (message) {
      dataCatalogEntry.lastSourcePromise.reject(message);
    });
    return dataCatalogEntry.lastSourcePromise.promise();
  };

  var reloadNavigatorMeta = function (dataCatalogEntry) {
    dataCatalogEntry.lastNavigatorPromise = $.Deferred();
    if (HAS_NAVIGATOR) {
      ApiHelper.getInstance().fetchNavigatorMetadata({
        path: dataCatalogEntry.path,
        silenceErrors: dataCatalogEntry.silenceErrors,
      }).done(function (data) {
        dataCatalogEntry.lastNavigatorPromise.resolve(data);
      }).fail(dataCatalogEntry.lastNavigatorPromise.reject);
    } else {
      dataCatalogEntry.lastNavigatorPromise.reject();
    }
    return dataCatalogEntry.lastNavigatorPromise.promise();
  };

  function DataCatalogEntry(dataCatalog, options) {
    var self = this;

    self.dataCatalog = dataCatalog;
    self.path = typeof options.path === 'string' && options.path ? options.path.split('.') : options.path || [];

    self.partialSourceMeta = options.partialSourceMeta;
    self.lastSourcePromise = undefined;
    self.lastNavigatorPromise = undefined;

    self.children = undefined;
    self.lastNavigatorChildrenPromise = undefined;

    self.silenceErrors = options.silenceErrors;
    self.cachedOnly = options.cachedOnly;
  }

  DataCatalogEntry.prototype.getChildren = function () {
    var self = this;
    var deferred = $.Deferred();
    if (self.children) {
      deferred.resolve(self.children);
    } else {
      self.getSourceMeta().done(function (sourceMeta) {
        if (self.children) {
          deferred.resolve(self.children);
        } else {
          self.children = [];
          var entities = sourceMeta.databases || sourceMeta.tables_meta || sourceMeta.extended_columns || sourceMeta.fields;
          if (entities) {
            entities.forEach(function (entity) {
              self.children.push(new DataCatalogEntry(self.dataCatalog, {
                path: self.path.concat(entity.name || entity),
                silenceErrors: self.silenceErrors,
                cachedOnly: self.cachedOnly,
                partialSourceMeta: typeof entity === 'object' ? entity : undefined
              }))
            });
          } else {
            (sourceMeta.type === 'map' ? ['key', 'value'] : ['item']).forEach(function (path) {
              if (sourceMeta[path]) {
                self.children.push(new DataCatalogEntry(self.dataCatalog, {
                  path: self.path.concat(path),
                  silenceErrors: self.silenceErrors,
                  cachedOnly: self.cachedOnly,
                  partialSourceMeta: sourceMeta[path]
                }));
              }
            })
          }
          deferred.resolve(self.children);
        }
      })
    }
    return deferred.promise();
  };

  DataCatalogEntry.prototype.loadNavigatorMetaForChildren = function () {
    var self = this;
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
        limit: children.length
      }).done(function (result) {
        if (result && result.entities && result.entities.length > 0) {
          var entityIndex = {};
          result.entities.forEach(function (entity) {
            entityIndex[entity.name || entity.originalName] = entity;
          });
          children.forEach(function (child) {
            var name = child.path[child.path.length - 1];
            if (entityIndex[name]) {
              child.lastNavigatorPromise = $.Deferred().resolve(entityIndex[name]).promise();
            }
          });
        }
      })
    })
  };

  DataCatalogEntry.prototype.getComment = function () {
    var self = this;
    var deferred = $.Deferred();

    var resolveWithSourceMeta = function () {
      self.getSourceMeta().done(function (sourceMeta) {
        deferred.resolve(sourceMeta && sourceMeta.comment || '');
      }).fail(deferred.reject);
    };

    if (HAS_NAVIGATOR) {
      self.getNavigatorMeta().done(function (navigatorMeta) {
        if (navigatorMeta && navigatorMeta.entity) {
          deferred.resolve(navigatorMeta.entity.description || navigatorMeta.entity.originalDescription || '');
        } else {
          resolveWithSourceMeta();
        }
      }).fail(resolveWithSourceMeta)
    } else {
      resolveWithSourceMeta();
    }

    return deferred.promise();
  };

  DataCatalogEntry.prototype.setComment = function (comment) {
    var self = this;
    var deferred = $.Deferred();

    if (HAS_NAVIGATOR) {
      self.getNavigatorMeta().done(function (navigatorMeta) {
        if (navigatorMeta && navigatorMeta.entity) {
          ApiHelper.getInstance().updateNavigatorMetadata({
            identity: navigatorMeta.entity.identity,
            properties: {
              description: comment
            }
          }).done(function () {
            reloadNavigatorMeta(self);
            self.getComment().done(deferred.resolve);
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
        reloadSourceMeta(self, true);
        self.getComment().done(deferred.resolve);
      }).fail(deferred.reject);
    }

    return deferred.promise();
  };

  DataCatalogEntry.prototype.getSourceMeta = function () {
    var self = this;
    return self.lastSourcePromise || reloadSourceMeta(self)
  };

  DataCatalogEntry.prototype.getNavigatorMeta = function () {
    var self = this;
    return self.lastNavigatorPromise || reloadNavigatorMeta(self)
  };


  var instances = {};

  var getCatalog = function (sourceType) {
    return instances[sourceType] || (instances[sourceType] = new DataCatalog(sourceType));
  };

  return {
    getCatalog: getCatalog,
    getEntry: function (options) {
      return getCatalog(options.sourceType).getEntry(options);
    }
  };
})();