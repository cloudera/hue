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

/**
 * @typedef {Object} ContextCompute
 * @property {string} id
 * @property {string} name
 */

/**
 * @typedef {Object} ContextNamespace
 * @property {string} id
 * @property {string} name
 * @property {ContextCompute} computes
 */

var ContextCatalog = (function () {

  var STORAGE_POSTFIX = LOGGED_USERNAME;
  var CONTEXT_CATALOG_VERSION = 4;
  var NAMESPACES_CONTEXT_TYPE = 'namespaces';
  var COMPUTES_CONTEXT_TYPE = 'computes';
  var DISABLE_CACHE = true;

  var ContextCatalog = (function () {

    function ContextCatalog() {
      var self = this;
      self.namespaces = {};
      self.namespacePromises = {};

      self.computes = {};
      self.computePromises = {};

      self.clusters = {};
      self.clusterPromises = {};

      var addPubSubs = function () {
        if (typeof huePubSub !== 'undefined') {
          huePubSub.subscribe('context.catalog.refresh', function () {
            self.namespaces = {};
            self.namespacePromises = {};

            self.computes = {};
            self.computePromises = {};

            self.clusters = {};
            self.clusterPromises = {};
            huePubSub.publish('context.catalog.refreshed');
          })
        } else {
          window.setTimeout(addPubSubs, 100);
        }
      };

      addPubSubs();
    }

    ContextCatalog.prototype.getStore = function () {
      if (!self.store) {
        self.store = localforage.createInstance({
          name: 'HueContextCatalog_' + STORAGE_POSTFIX
        });
      }
      return self.store;
    };

    ContextCatalog.prototype.saveLater = function (contextType, sourceType, entry) {
      var self = this;
      window.setTimeout(function () {
        self.getStore().setItem(sourceType + '_' + contextType, { version: CONTEXT_CATALOG_VERSION, entry: entry });
      }, 1000);
    };

    ContextCatalog.prototype.getSaved = function (contextType, sourceType) {
      var self = this;
      var deferred = $.Deferred();

      if (DISABLE_CACHE) {
        return deferred.reject().promise();
      }

      self.getStore().getItem(sourceType + '_' + contextType).then(function (saved) {
        if (saved && saved.version === CONTEXT_CATALOG_VERSION) {
          deferred.resolve(saved.entry);
        } else {
          deferred.reject();
        }
      }).catch(function (error) {
        console.warn(error);
        deferred.reject();
      });

      return deferred.promise();
    };

    /**
     * @param {Object} options
     * @param {string} options.sourceType
     * @param {boolean} [options.clearCache] - Default False
     * @param {boolean} [options.silenceErrors] - Default False
     * @return {Promise}
     */
    ContextCatalog.prototype.getNamespaces = function (options) {
      var self = this;

      var notifyForRefresh = self.namespacePromises[options.sourceType] && options.clearCache;
      if (options.clearCache) {
        self.namespacePromises[options.sourceType] = undefined;
        self.namespaces[options.sourceType] = undefined;
      }

      if (self.namespacePromises[options.sourceType]) {
        return self.namespacePromises[options.sourceType];
      }

      if (self.namespaces[options.sourceType]) {
        self.namespacePromises[options.sourceType] = $.Deferred().resolve(self.namespaces[options.sourceType]).promise();
        return self.namespacePromises[options.sourceType];
      }

      var deferred = $.Deferred();

      self.namespacePromises[options.sourceType] = deferred.promise();

      var fetchNamespaces = function () {
        ApiHelper.getInstance().fetchContextNamespaces(options).done(function (namespaces) {
          if (namespaces[options.sourceType]) {
            var dynamic = namespaces.dynamicClusters;
            var namespaces = namespaces[options.sourceType];
            if (namespaces) {
              namespaces.forEach(function (namespace) {
                namespace.computes.forEach(function (compute) {
                  if (!compute.id && compute.crn) {
                    compute.id = compute.crn;
                  }
                  if (!compute.name && compute.clusterName) {
                    compute.name = compute.clusterName;
                  }
                })
              });
              self.namespaces[options.sourceType] = { namespaces: namespaces.filter(function (namespace) {
                return namespace.name; // Only include namespaces with a name.
              }), dynamic: dynamic, hueTimestamp: Date.now() };
              deferred.resolve(self.namespaces[options.sourceType]);
              if (notifyForRefresh) {
                huePubSub.publish('context.catalog.namespaces.refreshed', options.sourceType);
              }

              if (self.namespaces[options.sourceType].namespaces.length) {
                self.saveLater(NAMESPACES_CONTEXT_TYPE, options.sourceType, self.namespaces[options.sourceType]);
              } else {
                self.getStore().removeItem(options.sourceType + '_' + NAMESPACES_CONTEXT_TYPE);
              }
            } else {
              deferred.reject();
            }
          } else {
            deferred.reject();
          }
        });
      };

      if (!options.clearCache) {
        self.getSaved(NAMESPACES_CONTEXT_TYPE, options.sourceType).done(function (namespaces) {
          self.namespaces[options.sourceType] = namespaces;
          deferred.resolve(self.namespaces[options.sourceType]);
        }).fail(fetchNamespaces);
      } else {
        fetchNamespaces();
      }

      return self.namespacePromises[options.sourceType];
    };

    /**
     * @param {Object} options
     * @param {string} options.sourceType
     * @param {boolean} [options.silenceErrors] - Default False
     * @param {boolean} [options.clearCache] - Default False
     * @return {Promise}
     */
    ContextCatalog.prototype.getComputes = function (options) {
      var self = this;

      if (options.clearCache) {
        self.computePromises[options.sourceType] = undefined;
        self.computes[options.sourceType] = undefined;
      }

      if (self.computePromises[options.sourceType]) {
        return self.computePromises[options.sourceType];
      }

      if (self.computes[options.sourceType]) {
        self.computePromises[options.sourceType] = $.Deferred().resolve(self.computes[options.sourceType]).promise();
        return self.computePromises[options.sourceType];
      }

      var deferred = $.Deferred();
      self.computePromises[options.sourceType] = deferred.promise();

      ApiHelper.getInstance().fetchContextComputes(options).done(function (computes) {
        if (computes[options.sourceType]) {
          var computes = computes[options.sourceType];
          if (computes) {
            self.computes[options.sourceType] = computes;
            deferred.resolve(self.computes[options.sourceType])
            // TODO: save
          } else {
            deferred.reject();
          }
        } else {
          deferred.reject();
        }
      });

      return self.computePromises[options.sourceType];
    };

    /**
     * @param {Object} options
     * @param {string} options.sourceType
     * @param {boolean} [options.silenceErrors] - Default False
     * @return {Promise}
     */
    ContextCatalog.prototype.getClusters = function (options) {
      var self = this;

      if (self.clusterPromises[options.sourceType]) {
        return self.clusterPromises[options.sourceType];
      }

      if (self.clusters[options.sourceType]) {
        self.clusterPromises[options.sourceType] = $.Deferred().resolve(self.clusters[options.sourceType]).promise();
        return self.clusterPromises[options.sourceType];
      }

      var deferred = $.Deferred();
      self.clusterPromises[options.sourceType] = deferred.promise();

      ApiHelper.getInstance().fetchContextClusters(options).done(function (clusters) {
        if (clusters && clusters[options.sourceType]) {
          self.clusters[options.sourceType] = clusters[options.sourceType];
          deferred.resolve(self.clusters[options.sourceType])
        } else {
          deferred.reject();
        }
      });

      return self.clusterPromises[options.sourceType];
    };

    return ContextCatalog;
  })();

  return (function () {
    var contextCatalog = new ContextCatalog();

    return {

      /**
       * @param {Object} options
       * @param {string} options.sourceType
       * @param {boolean} [options.clearCache] - Default False
       * @param {boolean} [options.silenceErrors] - Default False
       * @return {Promise}
       */
      getNamespaces: function (options) {
        return contextCatalog.getNamespaces(options);
      },

      /**
       * @param {Object} options
       * @param {string} options.sourceType
       * @param {boolean} [options.silenceErrors] - Default False
       * @return {Promise}
       */
      getComputes: function (options) {
        return contextCatalog.getComputes(options);
      },

      /**
       * @param {Object} options
       * @param {string} options.sourceType // TODO: rename?
       * @param {boolean} [options.silenceErrors] - Default False
       * @return {Promise}
       */
      getClusters: function (options) {
        return contextCatalog.getClusters(options);
      }
    }
  })();
})();