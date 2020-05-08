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
    const connectorType = options.connector.type;

    const notifyForRefresh = self.namespacePromises[connectorType] && options.clearCache;
    if (options.clearCache) {
      self.namespacePromises[connectorType] = undefined;
      self.namespaces[connectorType] = undefined;
    }

    if (self.namespacePromises[connectorType]) {
      return self.namespacePromises[connectorType];
    }

    if (self.namespaces[connectorType]) {
      self.namespacePromises[connectorType] = $.Deferred()
        .resolve(self.namespaces[connectorType])
        .promise();
      return self.namespacePromises[connectorType];
    }

    const deferred = $.Deferred();

    self.namespacePromises[connectorType] = deferred.promise();

    const startingNamespaces = {};
    const pollTimeout = -1;

    const pollForStarted = () => {
      window.clearTimeout(pollTimeout);
      window.setTimeout(() => {
        if (Object.keys(startingNamespaces).length) {
          apiHelper.fetchContextNamespaces(options).done(namespaces => {
            if (namespaces[connectorType]) {
              const namespaces = namespaces[connectorType];
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
                  huePubSub.publish(NAMESPACES_REFRESHED_EVENT, connectorType);
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
        if (namespaces[connectorType]) {
          const dynamic = namespaces.dynamicClusters;
          namespaces = namespaces[connectorType];
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
            self.namespaces[connectorType] = {
              namespaces: namespaces.filter(namespace => namespace.name),
              dynamic: dynamic,
              hueTimestamp: Date.now()
            };
            deferred.resolve(self.namespaces[connectorType]);
            if (notifyForRefresh) {
              huePubSub.publish(NAMESPACES_REFRESHED_EVENT, connectorType);
            }

            if (self.namespaces[connectorType].namespaces.length) {
              self.saveLater(
                NAMESPACES_CONTEXT_TYPE,
                connectorType,
                self.namespaces[connectorType]
              );
            } else {
              self.getStore().removeItem(connectorType + '_' + NAMESPACES_CONTEXT_TYPE);
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
        .getSaved(NAMESPACES_CONTEXT_TYPE, connectorType)
        .done(namespaces => {
          self.namespaces[connectorType] = namespaces;
          deferred.resolve(self.namespaces[connectorType]);
        })
        .fail(fetchNamespaces);
    } else {
      fetchNamespaces();
    }

    return self.namespacePromises[connectorType];
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

    const connectorType = options.connector.type;

    if (options.clearCache) {
      self.computePromises[connectorType] = undefined;
      self.computes[connectorType] = undefined;
    }

    if (self.computePromises[connectorType]) {
      return self.computePromises[connectorType];
    }

    if (self.computes[connectorType]) {
      self.computePromises[connectorType] = $.Deferred()
        .resolve(self.computes[connectorType])
        .promise();
      return self.computePromises[connectorType];
    }

    const deferred = $.Deferred();
    self.computePromises[connectorType] = deferred.promise();

    apiHelper.fetchContextComputes(options).done(computes => {
      if (computes[connectorType]) {
        computes = computes[connectorType];
        if (computes) {
          self.computes[connectorType] = computes;
          deferred.resolve(self.computes[connectorType]);
          // TODO: save
        } else {
          deferred.reject();
        }
      } else {
        deferred.reject();
      }
    });

    return self.computePromises[connectorType];
  }

  /**
   * @param {Object} options
   * @param {Connector} options.connector
   * @param {boolean} [options.silenceErrors] - Default False
   * @return {Promise}
   */
  getClusters(options) {
    const self = this;

    const connectorType = options.connector.type;

    if (self.clusterPromises[connectorType]) {
      return self.clusterPromises[connectorType];
    }

    if (self.clusters[connectorType]) {
      self.clusterPromises[connectorType] = $.Deferred()
        .resolve(self.clusters[connectorType])
        .promise();
      return self.clusterPromises[connectorType];
    }

    const deferred = $.Deferred();
    self.clusterPromises[connectorType] = deferred.promise();

    apiHelper.fetchContextClusters(options).done(clusters => {
      if (clusters && clusters[connectorType]) {
        self.clusters[connectorType] = clusters[connectorType];
        deferred.resolve(self.clusters[connectorType]);
      } else {
        deferred.reject();
      }
    });

    return self.clusterPromises[connectorType];
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
