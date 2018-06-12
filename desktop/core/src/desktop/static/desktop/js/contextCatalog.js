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
 * @typedef {Object} ContextNamespace
 * @property {string} id
 * @property {string} name
 */

var ContextCatalog = (function () {

  var STORAGE_POSTFIX = LOGGED_USERNAME;
  var CONTEXT_CATALOG_VERSION = 2;
  var NAMESPACES_CONTEXT_TYPE = 'namespaces';
  var COMPUTES_CONTEXT_TYPE = 'computes';

  var ContextCatalog = (function () {

    function ContextCatalog() {
      var self = this;
      self.namespaces = {};
      self.namespacePromises = {};

      self.computes = {};
      self.computePromises = {};
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
            var namespaces = namespaces[options.sourceType];
            var dynamic = namespaces.hasMultiCluster;
            if (namespaces) {
              self.namespaces[self.sourceType] = { namespaces: namespaces, dynamic: dynamic };
              deferred.resolve(self.namespaces[self.sourceType]);
              self.saveLater(NAMESPACES_CONTEXT_TYPE, options.sourceType, self.namespaces[self.sourceType]);
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
     * @return {Promise}
     */
    ContextCatalog.prototype.getComputes = function (options) {
      var self = this;

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
            self.computes[self.sourceType] = computes;
            deferred.resolve(self.computes[self.sourceType])
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
      }
    }
  })();
})();