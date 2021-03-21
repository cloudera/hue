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
import * as ko from 'knockout';

import { ASSIST_SET_DATABASE_EVENT } from './assist/events';
import componentUtils from './componentUtils';
import contextCatalog, {
  CONTEXT_CATALOG_REFRESHED_EVENT,
  NAMESPACES_REFRESHED_EVENT
} from 'catalog/contextCatalog';
import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

export const CONTEXT_SELECTOR_COMPONENT = 'hue-context-selector';

const TEMPLATE = `
  <!-- ko if: loadingContext -->
  <i class="fa fa-spinner fa-spin muted"></i>
  <!-- /ko -->

  <div class="inline-block" style="display: none;" data-bind="visible: !loadingContext()">
    <!-- ko if: window.HAS_MULTI_CLUSTER -->
    <!-- ko if: availableClusters().length > 0 && !hideClusters -->
    <!-- ko ifnot: hideLabels --><span class="editor-header-title">${I18n(
      'Cluster'
    )}</span><!-- /ko -->
    <div data-bind="component: { name: 'hue-drop-down', params: { value: cluster, onSelect: onClusterSelect, entries: availableClusters, labelAttribute: 'name', searchable: true, linkTitle: '${I18n(
      'Active cluster'
    )}' } }" style="display: inline-block"></div>
    <!-- /ko -->
    <!-- ko if: availableClusters().length === 0 && !hideClusters -->
    <span class="editor-header-title"><i class="fa fa-warning"></i> ${I18n(
      'No clusters found'
    )}</span>
    <!-- /ko -->

    <!-- ko if: availableComputes().length > 0 && !hideComputes -->
    <!-- ko ifnot: hideLabels --><span class="editor-header-title">${I18n(
      'Compute'
    )}</span><!-- /ko -->
    <div data-bind="component: { name: 'hue-drop-down', params: { value: compute, onSelect: onComputeSelect, entries: availableComputes, labelAttribute: 'name', searchable: true, linkTitle: '${I18n(
      'Active compute'
    )}' } }" style="display: inline-block"></div>
    <!-- /ko -->
    <!-- ko if: availableComputes().length === 0 && !hideComputes -->
    <span class="editor-header-title"><i class="fa fa-warning"></i> ${I18n(
      'No computes found'
    )}</span>
    <!-- /ko -->

    <!-- ko if: availableNamespaces().length > 0 && !hideNamespaces -->
    <!-- ko ifnot: hideLabels --><span class="editor-header-title">${I18n(
      'Namespace'
    )}</span><!-- /ko -->
    <div data-bind="component: { name: 'hue-drop-down', params: { value: namespace, onSelect: onNamespaceSelect, entries: availableNamespaces, labelAttribute: 'name', searchable: true, linkTitle: '${I18n(
      'Active namespace'
    )}' } }" style="display: inline-block"></div>
    <!-- /ko -->
    <!-- ko if: availableNamespaces().length === 0 && !hideNamespaces -->
    <span class="editor-header-title"><i class="fa fa-warning"></i> ${I18n(
      'No namespaces found'
    )}</span>
    <!-- /ko -->
    <!-- /ko -->

    <!-- ko if: availableDatabases().length > 0 && !hideDatabases-->
    <div data-bind="component: { name: 'hue-drop-down', params: { titleName: 'Database', value: database, entries: availableDatabases, foreachVisible: true, searchable: true, linkTitle: '${I18n(
      'Active database'
    )}' } }" style="display: inline-block"></div>
    <!-- /ko -->
    <!-- ko if: availableDatabases().length === 0  && !hideDatabases -->
    <span class="editor-header-title"><i class="fa fa-warning"></i> ${I18n(
      'No databases found'
    )}</span>
    <!-- /ko -->
  </div>
`;

const TYPES_INDEX = {
  cluster: {
    name: 'cluster',
    loading: 'loadingClusters',
    available: 'availableClusters',
    hide: 'hideClusters',
    lastPromise: 'lastClustersPromise',
    contextCatalogFn: 'getClusters',
    localStorageId: 'lastSelectedCluster',
    onSelect: 'onClusterSelect'
  },
  compute: {
    name: 'compute',
    loading: 'loadingComputes',
    available: 'availableComputes',
    hide: 'hideComputes',
    lastPromise: 'lastComputesPromise',
    contextCatalogFn: 'getComputes',
    localStorageId: 'lastSelectedCompute',
    onSelect: 'onComputeSelect'
  },
  namespace: {
    name: 'namespace',
    loading: 'loadingNamespaces',
    available: 'availableNamespaces',
    hide: 'hideNamespaces',
    lastPromise: 'lastNamespacesPromise',
    contextCatalogFn: 'getNamespaces',
    localStorageId: 'lastSelectedNamespace',
    onSelect: 'onNamespaceSelect'
  }
};

const TYPES = Object.keys(TYPES_INDEX).map(key => {
  return TYPES_INDEX[key];
});

/**
 * This is a component for compute, namespace and database selection. All parameters are optional except the
 * connector, if for instance no database and namespace observables are provided it will only show compute
 * selection.
 *
 * If it's desired to just show namespaces for a given compute you can force hide the compute selection by
 * setting hideComputes to true and the value of the compute observable will be used.
 *
 * Example:
 *
 *   <!-- ko component: {
 *     name: 'hue-context-selector',
 *     params: {
 *       connector: myConnectorObservable,
 *       compute: myComputeObservable,
 *       namespace: myNamespaceObservable,
 *     }
 *   } --><!-- /ko -->
 *
 * @param {Object} params
 * @param {ko.observable} [params.cluster]
 * @param {ko.observable} [params.compute]
 * @param {ko.observable} [params.namespace]
 * @param {ko.observable} [params.connector]
 * @param {ko.observable} [params.database]
 * @param {ko.observableArray} [params.availableDatabases]
 * @param {boolean} [params.hideClusters] - Can be used to force hide cluster selection even if a cluster
 *                                          observable is provided.
 * @param {boolean} [params.hideComputes] - Can be used to force hide compute selection even if a compute
 *                                          observable is provided.
 * @param {boolean} [params.hideNamespaces] - Can be used to force hide namespace selection even if a namespace
 *                                            observable is provided.
 * @param {boolean} [params.hideDatabases] - Can be used to force hide database selection even if a database
 *                                           observable is provided.
 * @param {function} [params.onComputeSelect] - Callback when a new compute is selected (after initial set)
 * @param {function} [params.onClusterSelect] - Callback when a new cluster is selected (after initial set)
 * @param {function} [params.onNamespaceSelect] - Callback when a new namespace is selected (after initial set)
 * @constructor
 */
const HueContextSelector = function (params) {
  const self = this;
  if (!params.connector || !ko.unwrap(params.connector)) {
    throw new Error('No connector with type provided');
  }

  self.disposals = [];

  self.connector = params.connector;
  self.hideLabels = params.hideLabels;

  TYPES.forEach(type => {
    self[type.name] = params[type.name];
    self[type.loading] = ko.observable(false);
    self[type.available] = ko.observableArray();
    self[type.hide] = params[type.hide] || !self[type.name];
    self[type.lastPromise] = undefined;
    self[type.onSelect] = function (selectedVal, previousVal) {
      if (params[type.onSelect]) {
        params[type.onSelect](selectedVal, previousVal);
      }
      setInLocalStorage('contextSelector.' + type.localStorageId, selectedVal);

      if (selectedVal && type === TYPES_INDEX.compute) {
        self.setMatchingNamespace(selectedVal);
      } else if (selectedVal && type === TYPES_INDEX.namespace) {
        self.setMatchingCompute(selectedVal);
      }
    };
    if (self[type.name]) {
      huePubSub.subscribe('context.selector.set.' + type.name, id => {
        self[type.available]().some(instance => {
          if (instance.id === id) {
            self[type.name](instance);
            return true;
          }
        });
      });
    }
    self.reload(type);
  });

  let refreshThrottle = -1;

  const refresh = function (connectorId) {
    if (!connectorId || ko.unwrap(self.connector).id === connectorId) {
      window.clearTimeout(refreshThrottle);
      refreshThrottle = window.setTimeout(() => {
        TYPES.forEach(self.reload.bind(self));
      }, 100);
    }
  };

  const namespaceRefreshSub = huePubSub.subscribe(NAMESPACES_REFRESHED_EVENT, refresh);
  const contextCatalogRefreshSub = huePubSub.subscribe(CONTEXT_CATALOG_REFRESHED_EVENT, refresh);
  self.disposals.push(() => {
    window.clearTimeout(refreshThrottle);
    namespaceRefreshSub.remove();
    contextCatalogRefreshSub.remove();
  });

  self.loadingDatabases = ko.observable(false);
  self.availableDatabases = params.availableDatabases || ko.observableArray();
  self.database = params.database;
  self.hideDatabases = params.hideDatabases || !self.database;

  self.reloadDatabaseThrottle = -1;

  self.reloadDatabases();

  if (self.database) {
    huePubSub.subscribe('data.catalog.entry.refreshed', details => {
      if (details.entry.isSource()) {
        if (ko.unwrap(self.connector).id === details.entry.getConnector().id) {
          self.reloadDatabases();
        }
      }
    });
  }

  self.loadingContext = ko.pureComputed(() => {
    return (
      self[TYPES_INDEX.cluster.loading]() ||
      self[TYPES_INDEX.namespace.loading]() ||
      self[TYPES_INDEX.compute.loading]() ||
      self.loadingDatabases()
    );
  });
};

HueContextSelector.prototype.setMatchingNamespace = function (compute) {
  const self = this;
  if (self[TYPES_INDEX.namespace.name]) {
    // Select the first corresponding namespace when a compute is selected (unless selected)
    self[TYPES_INDEX.namespace.lastPromise].done(() => {
      if (
        !self[TYPES_INDEX.namespace.name]() ||
        self[TYPES_INDEX.namespace.name]().id !== compute.namespace
      ) {
        const found = self[TYPES_INDEX.namespace.available]().some(namespace => {
          if (compute.namespace === namespace.id) {
            self[TYPES_INDEX.namespace.name](namespace);
            setInLocalStorage('contextSelector.' + TYPES_INDEX.namespace.localStorageId, namespace);
            return true;
          }
        });

        if (!found) {
          // This can happen when a compute refers to a namespace that isn't returned by the namespaces call
          // TODO: What should we do?
          self[TYPES_INDEX.namespace.name](undefined);
        }
      }
    });
  }
};

HueContextSelector.prototype.setMatchingCompute = function (namespace) {
  const self = this;
  if (self[TYPES_INDEX.compute.name]) {
    // Select the first corresponding compute when a namespace is selected (unless selected)
    self[TYPES_INDEX.compute.lastPromise].done(() => {
      if (
        !self[TYPES_INDEX.compute.name]() ||
        (self[TYPES_INDEX.compute.name]().namespace &&
          self[TYPES_INDEX.compute.name]().namespace !== namespace.id)
      ) {
        const found = self[TYPES_INDEX.compute.available]().some(compute => {
          if (namespace.id === compute.namespace) {
            self[TYPES_INDEX.compute.name](compute);
            setInLocalStorage('contextSelector.' + TYPES_INDEX.compute.localStorageId, namespace);
            return true;
          }
        });

        if (!found) {
          // This can happen when a namespace refers to a compute that isn't returned by the computes call
          // TODO: What should we do?
          self[TYPES_INDEX.compute.name](undefined);
        }
      }
    });
  }
};

HueContextSelector.prototype.reload = function (type) {
  const self = this;
  if (self[type.name]) {
    self[type.loading](true);
    self[type.lastPromise] = contextCatalog[type.contextCatalogFn]({
      connector: ko.unwrap(self.connector)
    })
      .done(available => {
        // Namespaces response differs slightly from the others
        if (type === TYPES_INDEX.namespace) {
          available = available.namespaces;
        }
        self[type.available](available);

        // If we only get one and hue is not configured for multi-cluster we always fallback to the returned
        // compute or namespace from the backend. This also guarantees a compute and namespace is always set.
        if (available.length === 1 && !window.HAS_MULTI_CLUSTER) {
          if (!self[type.name]() || self[type.name]().id !== available[0].id) {
            self[type.name](available[0]);
          }
          return;
        }

        // In some cases we could have a namespace or compute without the name attribute, or the name might have changed.
        if (self[type.name]() && !self[type.name]().name) {
          available.some(other => {
            if (other !== self[type.name]() && other.id === self[type.name]().id) {
              self[type.name](other);
              return true;
            }
          });
        }

        if (!self[type.name]() && getFromLocalStorage('contextSelector.' + type.localStorageId)) {
          const lastSelected = getFromLocalStorage('contextSelector.' + type.localStorageId);
          const found = available.some(other => {
            if (other.id === lastSelected.id) {
              self[type.name](other);
              return true;
            }
          });

          // If we can't find the last selected cluster or compute we try to find by type
          if (
            !found &&
            lastSelected &&
            (type === TYPES_INDEX.cluster || type === TYPES_INDEX.compute)
          ) {
            available.some(other => {
              if (lastSelected && other.type === lastSelected.type) {
                self[type.name](other);
                return true;
              }
            });
          }
        }

        if (!self[type.name]() && available.length) {
          self[type.name](available[0]);
        }

        // Namespace is leading, update compute to match once/if available
        if (self[type.name]() && type === TYPES_INDEX.namespace) {
          self.setMatchingCompute(self[type.name]());
        }
      })
      .always(() => {
        self[type.loading](false);
      });
  } else {
    self[type.lastPromise] = $.Deferred().resolve().promise();
  }
};

HueContextSelector.prototype.reloadDatabases = function () {
  const self = this;
  if (self.database && !self.hideDatabases) {
    self.loadingDatabases(true);
    $.when(self[TYPES_INDEX.namespace.lastPromise], self[TYPES_INDEX.compute.lastPromise]).done(
      () => {
        window.clearTimeout(self.reloadDatabaseThrottle);
        self.reloadDatabaseThrottle = window.setTimeout(() => {
          const connector = ko.unwrap(self.connector);
          if (!self[TYPES_INDEX.namespace.name]()) {
            self.availableDatabases([]);
            self.loadingDatabases(false);
            return;
          }
          dataCatalog
            .getEntry({
              namespace: self[TYPES_INDEX.namespace.name](),
              compute: self[TYPES_INDEX.compute.name](),
              connector: connector,
              path: [],
              definition: { type: 'source' }
            })
            .then(sourceEntry => {
              sourceEntry
                .getChildren({ silenceErrors: true })
                .then(databaseEntries => {
                  const databaseNames = [];
                  databaseEntries.forEach(databaseEntry => {
                    databaseNames.push(databaseEntry.name);
                  });
                  self.availableDatabases(databaseNames);
                })
                .catch(() => {
                  self.availableDatabases([]);
                })
                .finally(() => {
                  let lastSelectedDb = getFromLocalStorage(
                    'assist_' +
                      ko.unwrap(self.connector).id +
                      '_' +
                      self[TYPES_INDEX.namespace.name]().id +
                      '.lastSelectedDb'
                  );

                  const updateAssist = lastSelectedDb !== '';

                  if (
                    !self.database() ||
                    self.availableDatabases().indexOf(self.database()) === -1
                  ) {
                    if (!lastSelectedDb) {
                      lastSelectedDb = 'default';
                    }

                    if (
                      self.availableDatabases().length === 0 ||
                      self.availableDatabases().indexOf(lastSelectedDb) !== -1
                    ) {
                      self.database(lastSelectedDb);
                    } else {
                      self.database(self.availableDatabases()[0]);
                    }
                  }
                  self.loadingDatabases(false);

                  if (updateAssist) {
                    huePubSub.publish(ASSIST_SET_DATABASE_EVENT, {
                      connector: connector,
                      namespace: self[TYPES_INDEX.namespace.name](),
                      name: self.database()
                    });
                  }
                });
            });
        }, 10);
      }
    );
  } else if (self.database) {
    self.availableDatabases([]);
    self.database(undefined);
  }
};

HueContextSelector.prototype.dispose = function () {
  const self = this;
  while (self.disposals.length) {
    self.disposals.pop()();
  }
};

componentUtils.registerComponent(CONTEXT_SELECTOR_COMPONENT, HueContextSelector, TEMPLATE);
