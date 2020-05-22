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

export const REFRESH_CONTEXT_CATALOG_EVENT = 'context.catalog.refresh';
export const CONTEXT_CATALOG_REFRESHED_EVENT = 'context.catalog.refreshed';
export const NAMESPACES_REFRESHED_EVENT = 'context.catalog.namespaces.refreshed';

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
        huePubSub.subscribe(REFRESH_CONTEXT_CATALOG_EVENT, () => {
          const namespacesToRefresh = Object.keys(self.namespaces);
          self.namespaces = {};
          self.namespacePromises = {};

          self.computes = {};
          self.computePromises = {};

          self.clusters = {};
          self.clusterPromises = {};
          huePubSub.publish(CONTEXT_CATALOG_REFRESHED_EVENT);
          namespacesToRefresh.forEach(connectorType => {
            huePubSub.publish(NAMESPACES_REFRESHED_EVENT, connectorType);
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

  saveLater(contextType, connectorType, entry) {
    const self = this;
    window.setTimeout(() => {
      self.getStore().setItem(connectorType + '_' + contextType, {
        version: CONTEXT_CATALOG_VERSION,
        entry: entry
      });
    }, 1000);
  }

  getSaved(contextType, connectorType) {
    const self = this;
    const deferred = $.Deferred();

    if (DISABLE_CACHE) {
      return deferred.reject().promise();
    }

    self
      .getStore()
      .getItem(connectorType + '_' + contextType)
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
   * @param {Connector} options.connector
   * @param {boolean} [options.clearCache] - Default False
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getNamespaces(options) {
    const self = this;
    const connectorId = options.connector.id;

    const notifyForRefresh = self.namespacePromises[connectorId] && options.clearCache;
    if (options.clearCache) {
      self.namespacePromises[connectorId] = undefined;
      self.namespaces[connectorId] = undefined;
    }

    if (self.namespacePromises[connectorId]) {
      return self.namespacePromises[connectorId];
    }

    if (self.namespaces[connectorId]) {
      self.namespacePromises[connectorId] = $.Deferred()
        .resolve(self.namespaces[connectorId])
        .promise();
      return self.namespacePromises[connectorId];
    }

    const deferred = $.Deferred();

    self.namespacePromises[connectorId] = deferred.promise();

    const startingNamespaces = {};
    const pollTimeout = -1;

    const pollForStarted = () => {
      window.clearTimeout(pollTimeout);
      window.setTimeout(() => {
        if (Object.keys(startingNamespaces).length) {
          apiHelper.fetchContextNamespaces(options).done(namespaces => {
            if (namespaces[connectorId]) {
              const namespaces = namespaces[connectorId];
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
                  huePubSub.publish(NAMESPACES_REFRESHED_EVENT, connectorId);
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
        if (namespaces[connectorId]) {
          const dynamic = namespaces.dynamicClusters;
          namespaces = namespaces[connectorId];
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
            self.namespaces[connectorId] = {
              namespaces: namespaces.filter(namespace => namespace.name),
              dynamic: dynamic,
              hueTimestamp: Date.now()
            };
            deferred.resolve(self.namespaces[connectorId]);
            if (notifyForRefresh) {
              huePubSub.publish(NAMESPACES_REFRESHED_EVENT, connectorId);
            }

            if (self.namespaces[connectorId].namespaces.length) {
              self.saveLater(NAMESPACES_CONTEXT_TYPE, connectorId, self.namespaces[connectorId]);
            } else {
              self.getStore().removeItem(connectorId + '_' + NAMESPACES_CONTEXT_TYPE);
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
        .getSaved(NAMESPACES_CONTEXT_TYPE, connectorId)
        .done(namespaces => {
          self.namespaces[connectorId] = namespaces;
          deferred.resolve(self.namespaces[connectorId]);
        })
        .fail(fetchNamespaces);
    } else {
      fetchNamespaces();
    }

    return self.namespacePromises[connectorId];
  }

  /**
   * @param {Object} options
   * @param {Connector} options.connector
   * @param {boolean} [options.silenceErrors] - Default False
   * @param {boolean} [options.clearCache] - Default False
   * @return {Promise}
   */
  getComputes(options) {
    const self = this;

    const connectorId = options.connector.id;

    if (options.clearCache) {
      self.computePromises[connectorId] = undefined;
      self.computes[connectorId] = undefined;
    }

    if (self.computePromises[connectorId]) {
      return self.computePromises[connectorId];
    }

    if (self.computes[connectorId]) {
      self.computePromises[connectorId] = $.Deferred()
        .resolve(self.computes[connectorId])
        .promise();
      return self.computePromises[connectorId];
    }

    const deferred = $.Deferred();
    self.computePromises[connectorId] = deferred.promise();

    apiHelper.fetchContextComputes(options).done(computes => {
      if (computes[connectorId]) {
        computes = computes[connectorId];
        if (computes) {
          self.computes[connectorId] = computes;
          deferred.resolve(self.computes[connectorId]);
          // TODO: save
        } else {
          deferred.reject();
        }
      } else {
        deferred.reject();
      }
    });

    return self.computePromises[connectorId];
  }

  /**
   * @param {Object} options
   * @param {Connector} options.connector
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getClusters(options) {
    const self = this;

    const connectorId = options.connector.id;

    if (self.clusterPromises[connectorId]) {
      return self.clusterPromises[connectorId];
    }

    if (self.clusters[connectorId]) {
      self.clusterPromises[connectorId] = $.Deferred()
        .resolve(self.clusters[connectorId])
        .promise();
      return self.clusterPromises[connectorId];
    }

    const deferred = $.Deferred();
    self.clusterPromises[connectorId] = deferred.promise();

    apiHelper.fetchContextClusters(options).done(clusters => {
      if (clusters && clusters[connectorId]) {
        self.clusters[connectorId] = clusters[connectorId];
        deferred.resolve(self.clusters[connectorId]);
      } else {
        deferred.reject();
      }
    });

    return self.clusterPromises[connectorId];
  }
}

const contextCatalog = new ContextCatalog();

export default {
  /**
   * @param {Object} options
   * @param {Connector} options.connector
   * @param {boolean} [options.clearCache] - Default False
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getNamespaces: options => contextCatalog.getNamespaces(options),

  /**
   * @param {Object} options
   * @param {Connector} options.connector
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getComputes: options => contextCatalog.getComputes(options),

  /**
   * @param {Object} options
   * @param {Connector} options.connector
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getClusters: options => contextCatalog.getClusters(options)
};
