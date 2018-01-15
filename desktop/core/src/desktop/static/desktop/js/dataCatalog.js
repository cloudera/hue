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
   * @param {Object} options
   * @param {string|string[]} options.path
   * @param {Object} [options.definition] - The initial definition if not already set on the entry
   * @return {DataCatalogEntry}
   */
  DataCatalog.prototype.getEntry = function (options) {
    var self = this;
    var identifier = typeof options.path === 'string' ? options.path : (typeof options.path === 'string' ? options.path : options.path.join('.'));
    return self.entries[identifier] || (self.entries[identifier] = new DataCatalogEntry(self, options.path, options.definition));
  };

  var fetchMeta = function (apiHelperFunction, dataCatalogEntry, apiOptions) {
    return ApiHelper.getInstance()[apiHelperFunction]({
      sourceType: dataCatalogEntry.dataCatalog.sourceType,
      path: dataCatalogEntry.path,
      silenceErrors: apiOptions && apiOptions.silenceErrors,
      cachedOnly: apiOptions && apiOptions.cachedOnly,
      refreshCache: apiOptions && apiOptions.refreshCache
    })
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
    dataCatalogEntry.lastSourceMetaPromise = fetchMeta('fetchSourceMetadata', dataCatalogEntry, apiOptions);
    dataCatalogEntry.lastSourceMetaPromise.done(function (sourceMeta) {
      dataCatalogEntry.sourceMeta = sourceMeta;
    });
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
    if (HAS_NAVIGATOR) {
      dataCatalogEntry.lastNavigatorMetaPromise = fetchMeta('fetchNavigatorMetadata', dataCatalogEntry, apiOptions);
      dataCatalogEntry.lastNavigatorMetaPromise.done(function (navigatorMeta) {
        dataCatalogEntry.navigatorMeta = navigatorMeta;
      });
    } else {
      dataCatalogEntry.lastNavigatorMetaPromise =  $.Deferred.reject().promise();
    }
    return dataCatalogEntry.lastNavigatorMetaPromise;
  };

  /**
   * @param {DataCatalogEntry} dataCatalogEntry
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  var reloadSample = function (dataCatalogEntry, apiOptions) {
    dataCatalogEntry.lastSamplePromise = fetchMeta('fetchSample', dataCatalogEntry, apiOptions);
    dataCatalogEntry.lastSamplePromise.done(function (sample) {
      dataCatalogEntry.sample = sample;
    });
    return dataCatalogEntry.lastSamplePromise;
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

    self.lastSourceMetaPromise = undefined;
    self.sourceMeta = undefined;

    self.lastNavigatorMetaPromise = undefined;
    self.navigatorMeta = undefined;

    self.lastSamplePromise = undefined;
    self.sample = undefined;

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
              var definition = typeof entity === 'object' ? entity : {};
              definition.index = index++;
              var catalogEntry = self.dataCatalog.getEntry({ path: self.path.concat(entity.name || entity), definition: definition });
              self.children.push(catalogEntry);
            });
          } else {
            (sourceMeta.type === 'map' ? ['key', 'value'] : ['item']).forEach(function (path) {
              if (sourceMeta[path]) {
                var definition = sourceMeta[path];
                definition.index = index++;
                definition.isMapValue = path === 'value'
                var catalogEntry = self.dataCatalog.getEntry({ path: self.path.concat(path), definition: definition.isMapValue = path === 'value' });
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
            entityIndex[(entity.name || entity.originalName).toLowerCase()] = entity;
          });
          children.forEach(function (child) {
            var name = child.name.toLowerCase();
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

  DataCatalogEntry.prototype.getKnownComment = function () {
    var self = this;
    if (self.navigatorMeta) {
      return self.navigatorMeta.description || self.navigatorMeta.originalDescription || ''
    }
    return self.sourceMeta && self.sourceMeta.comment || '';
  };

  /**
   * @param {Object|boolean} [apiOptions] -
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
      if (self.navigatorMeta) {
        deferred.resolve(self.navigatorMeta.description || self.navigatorMeta.originalDescription || '');
      } else {
        self.getNavigatorMeta(apiOptions).done(function (navigatorMeta) {
          if (navigatorMeta) {
            deferred.resolve(navigatorMeta.description || navigatorMeta.originalDescription || '');
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
    var title = self.path.join('.');
    if (self.isField()) {
      var type = self.getType();
      if (type) {
        title += ' (' + type + ')';
      }
    }
    return title;
  };

  DataCatalogEntry.prototype.getDisplayName = function (qualified) {
    var self = this;
    var displayName = qualified ? self.path.join('.') : self.name;
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
    var type = self.sourceMeta && self.sourceMeta.type || self.definition.type || '';
    if (~type.indexOf('<')) {
      type = type.substring(0, type.indexOf('<'));
    }
    return type;
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

  /**
   * @param {Object} [apiOptions]
   * @param {boolean} [apiOptions.silenceErrors]
   * @param {boolean} [apiOptions.cachedOnly]
   * @param {boolean} [apiOptions.refreshCache]
   * @return {Promise}
   */
  DataCatalogEntry.prototype.getSample = function () {
    var self = this;
    return self.lastSamplePromise || reloadSample(self, options)
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
    }
  };
})();