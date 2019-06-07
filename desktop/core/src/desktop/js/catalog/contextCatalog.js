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

import $ from 'jquery';
import localforage from 'localforage';

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';

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

const STORAGE_POSTFIX = window.LOGGED_USERNAME;
const CONTEXT_CATALOG_VERSION = 4;
const NAMESPACES_CONTEXT_TYPE = 'namespaces';
const DISABLE_CACHE = true;

class ContextCatalog {
  constructor() {
    const self = this;
    self.namespaces = {};
    self.namespacePromises = {};

    self.computes = {};
    self.computePromises = {};

    self.clusters = {};
    self.clusterPromises = {};

    const addPubSubs = () => {
      if (typeof huePubSub !== 'undefined') {
        huePubSub.subscribe('context.catalog.refresh', () => {
          const namespacesToRefresh = Object.keys(self.namespaces);
          self.namespaces = {};
          self.namespacePromises = {};

          self.computes = {};
          self.computePromises = {};

          self.clusters = {};
          self.clusterPromises = {};
          huePubSub.publish('context.catalog.refreshed');
          namespacesToRefresh.forEach(sourceType => {
            huePubSub.publish('context.catalog.namespaces.refreshed', sourceType);
          });
        });
      } else {
        window.setTimeout(addPubSubs, 100);
      }
    };

    addPubSubs();
  }

  getStore() {
    if (!self.store) {
      self.store = localforage.createInstance({
        name: 'HueContextCatalog_' + STORAGE_POSTFIX
      });
    }
    return self.store;
  }

  saveLater(contextType, sourceType, entry) {
    const self = this;
    window.setTimeout(() => {
      self.getStore().setItem(sourceType + '_' + contextType, {
        version: CONTEXT_CATALOG_VERSION,
        entry: entry
      });
    }, 1000);
  }

  getSaved(contextType, sourceType) {
    const self = this;
    const deferred = $.Deferred();

    if (DISABLE_CACHE) {
      return deferred.reject().promise();
    }

    self
      .getStore()
      .getItem(sourceType + '_' + contextType)
      .then(saved => {
        if (saved && saved.version === CONTEXT_CATALOG_VERSION) {
          deferred.resolve(saved.entry);
        } else {
          deferred.reject();
        }
      })
      .catch(error => {
        console.warn(error);
        deferred.reject();
      });

    return deferred.promise();
  }

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {boolean} [options.clearCache] - Default False
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getNamespaces(options) {
    const self = this;

    const notifyForRefresh = self.namespacePromises[options.sourceType] && options.clearCache;
    if (options.clearCache) {
      self.namespacePromises[options.sourceType] = undefined;
      self.namespaces[options.sourceType] = undefined;
    }

    if (self.namespacePromises[options.sourceType]) {
      return self.namespacePromises[options.sourceType];
    }

    if (self.namespaces[options.sourceType]) {
      self.namespacePromises[options.sourceType] = $.Deferred()
        .resolve(self.namespaces[options.sourceType])
        .promise();
      return self.namespacePromises[options.sourceType];
    }

    const deferred = $.Deferred();

    self.namespacePromises[options.sourceType] = deferred.promise();

    const startingNamespaces = {};
    const pollTimeout = -1;

    const pollForStarted = () => {
      window.clearTimeout(pollTimeout);
      window.setTimeout(() => {
        if (Object.keys(startingNamespaces).length) {
          apiHelper.fetchContextNamespaces(options).done(namespaces => {
            if (namespaces[options.sourceType]) {
              const namespaces = namespaces[options.sourceType];
              if (namespaces) {
                let statusChanged = false;
                namespaces.forEach(namespace => {
                  if (startingNamespaces[namespace.id] && namespace.status !== 'STARTING') {
                    startingNamespaces[namespace.id].status = namespace.status;
                    delete startingNamespaces[namespace.id];
                    statusChanged = true;
                  }
                });
                if (statusChanged) {
                  huePubSub.publish('context.catalog.namespaces.refreshed', options.sourceType);
                }
                if (Object.keys(startingNamespaces).length) {
                  pollForStarted();
                }
              }
            }
          });
        }
      }, 2000);
    };

    deferred.done(context => {
      context.namespaces.forEach(namespace => {
        if (namespace.status === 'STARTING') {
          startingNamespaces[namespace.id] = namespace;
        }
      });
      if (Object.keys(startingNamespaces).length) {
        pollForStarted();
      }
    });

    const fetchNamespaces = () => {
      apiHelper.fetchContextNamespaces(options).done(namespaces => {
        if (namespaces[options.sourceType]) {
          const dynamic = namespaces.dynamicClusters;
          namespaces = namespaces[options.sourceType];
          if (namespaces) {
            namespaces.forEach(namespace => {
              namespace.computes.forEach(compute => {
                if (!compute.id && compute.crn) {
                  compute.id = compute.crn;
                }
                if (!compute.name && compute.clusterName) {
                  compute.name = compute.clusterName;
                }
              });
            });
            self.namespaces[options.sourceType] = {
              namespaces: namespaces.filter(namespace => namespace.name),
              dynamic: dynamic,
              hueTimestamp: Date.now()
            };
            deferred.resolve(self.namespaces[options.sourceType]);
            if (notifyForRefresh) {
              huePubSub.publish('context.catalog.namespaces.refreshed', options.sourceType);
            }

            if (self.namespaces[options.sourceType].namespaces.length) {
              self.saveLater(
                NAMESPACES_CONTEXT_TYPE,
                options.sourceType,
                self.namespaces[options.sourceType]
              );
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
      self
        .getSaved(NAMESPACES_CONTEXT_TYPE, options.sourceType)
        .done(namespaces => {
          self.namespaces[options.sourceType] = namespaces;
          deferred.resolve(self.namespaces[options.sourceType]);
        })
        .fail(fetchNamespaces);
    } else {
      fetchNamespaces();
    }

    return self.namespacePromises[options.sourceType];
  }

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {boolean} [options.silenceErrors] - Default False
   * @param {boolean} [options.clearCache] - Default False
   * @return {Promise}
   */
  getComputes(options) {
    const self = this;

    if (options.clearCache) {
      self.computePromises[options.sourceType] = undefined;
      self.computes[options.sourceType] = undefined;
    }

    if (self.computePromises[options.sourceType]) {
      return self.computePromises[options.sourceType];
    }

    if (self.computes[options.sourceType]) {
      self.computePromises[options.sourceType] = $.Deferred()
        .resolve(self.computes[options.sourceType])
        .promise();
      return self.computePromises[options.sourceType];
    }

    const deferred = $.Deferred();
    self.computePromises[options.sourceType] = deferred.promise();

    apiHelper.fetchContextComputes(options).done(computes => {
      if (computes[options.sourceType]) {
        computes = computes[options.sourceType];
        if (computes) {
          self.computes[options.sourceType] = computes;
          deferred.resolve(self.computes[options.sourceType]);
          // TODO: save
        } else {
          deferred.reject();
        }
      } else {
        deferred.reject();
      }
    });

    return self.computePromises[options.sourceType];
  }

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getClusters(options) {
    const self = this;

    if (self.clusterPromises[options.sourceType]) {
      return self.clusterPromises[options.sourceType];
    }

    if (self.clusters[options.sourceType]) {
      self.clusterPromises[options.sourceType] = $.Deferred()
        .resolve(self.clusters[options.sourceType])
        .promise();
      return self.clusterPromises[options.sourceType];
    }

    const deferred = $.Deferred();
    self.clusterPromises[options.sourceType] = deferred.promise();

    apiHelper.fetchContextClusters(options).done(clusters => {
      if (clusters && clusters[options.sourceType]) {
        self.clusters[options.sourceType] = clusters[options.sourceType];
        deferred.resolve(self.clusters[options.sourceType]);
      } else {
        deferred.reject();
      }
    });

    return self.clusterPromises[options.sourceType];
  }
}

const contextCatalog = new ContextCatalog();

export default {
  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {boolean} [options.clearCache] - Default False
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getNamespaces: options => contextCatalog.getNamespaces(options),

  /**
   * @param {Object} options
   * @param {string} options.sourceType
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getComputes: options => contextCatalog.getComputes(options),

  /**
   * @param {Object} options
   * @param {string} options.sourceType // TODO: rename?
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getClusters: options => contextCatalog.getClusters(options)
};
