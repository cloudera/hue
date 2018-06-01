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
 * @typedef {Object} SourceContext
 * @property {string} id
 * @property {string} name
 */

var ContextCatalog = (function () {

  var CONTEXT_CATALOG_VERSION = 1;

  var ContextCatalog = (function () {
    function ContextCatalog() {
      var self = this;
      self.entries = {};

      // TODO: Add caching
    }

    ContextCatalog.prototype.getContextCatalogEntry = function (app) {
      var self = this;
      if (!self.entries[app]) {
        self.entries[app] = new ContextCatalogEntry(app);
      }
      return self.entries[app];
    };

    return ContextCatalog;
  })();


  var ContextCatalogEntry = (function () {
    var ContextCatalogEntry = function (app) {
      var self = this;
      self.app = app;
      self.reset();
    };

    ContextCatalogEntry.prototype.reset = function () {
      var self = this;
      self.sourceContexts = {}; // TODO: Cache this
      self.sourceContextsPromises = {};
    };

    /**
     *
     * @param {Object} options
     * @param {string} options.sourceType
     * @param {boolean} [options.silenceErrors]
     * @return {Promise}
     */
    ContextCatalogEntry.prototype.getSourceContexts = function (options) {
      var self = this;

      if (self.sourceContextsPromises[options.sourceType]) {
        return self.sourceContextsPromises[options.sourceType];
      }

      var deferred = $.Deferred();
      self.sourceContextsPromises[options.sourceType] = deferred.promise();

      ApiHelper.getInstance().fetchSourceContexts(options).done(function (sourceContexts) {
        if (sourceContexts[self.app] && sourceContexts[self.app][options.sourceType]) {
          var context = sourceContexts[self.app][options.sourceType];
          // TODO: For now we only care about namespaces.
          if (context.namespaces) {
            self.sourceContexts[self.sourceType] = context.namespaces;
            deferred.resolve(self.sourceContexts[self.sourceType])
            // TODO: save
          } else {
            deferred.reject();
          }
        } else {
          deferred.reject();
        }
      });

      return deferred.promise({ name: 'foo' });
    };

    return ContextCatalogEntry;
  })();

  return (function () {
    var contextCatalog = new ContextCatalog();

    return {
      BROWSER_APP: 'browser',
      EDITOR_APP: 'editor',

      /**
       * @param {Object} options
       * @param {string} options.app
       * @param {string} options.sourceType
       * @param {boolean} [options.silenceErrors]
       * @return {Promise}
       */
      getSourceContexts: function (options) {
        return contextCatalog.getContextCatalogEntry(options.app).getSourceContexts(options);
      }
    }
  })();
})();