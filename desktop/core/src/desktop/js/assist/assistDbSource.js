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
import ko from 'knockout';

import apiHelper from 'api/apiHelper';
import AssistDbNamespace from 'assist/assistDbNamespace';
import contextCatalog from 'catalog/contextCatalog';
import huePubSub from 'utils/huePubSub';

class AssistDbSource {
  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {string} options.type
   * @param {ContextNamespace} [options.initialNamespace] - Optional initial namespace to use
   * @param {ContextCompute} [options.initialCompute] - Optional initial compute to use
   * @param {string} options.name
   * @param {boolean} options.nonSqlType - Optional, default false
   * @param {Object} options.navigationSettings
   * @constructor
   */
  constructor(options) {
    const self = this;

    self.sourceType = options.type;
    self.name = options.name;
    self.i18n = options.i18n;
    self.nonSqlType = options.nonSqlType;
    self.navigationSettings = options.navigationSettings;
    self.initialNamespace =
      options.initialNamespace ||
      apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedNamespace');
    self.initialCompute =
      options.initialCompute ||
      apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedCompute');

    self.selectedNamespace = ko.observable();
    self.namespaces = ko.observableArray();

    self.loadedDeferred = $.Deferred();
    self.loading = ko.observable(false);
    self.hasErrors = ko.observable(false);

    self.filter = {
      querySpec: ko.observable({}).extend({ rateLimit: 300 })
    };

    self.filteredNamespaces = ko.pureComputed(() => {
      if (
        !self.filter.querySpec() ||
        typeof self.filter.querySpec().query === 'undefined' ||
        !self.filter.querySpec().query
      ) {
        return self.namespaces();
      }
      return self
        .namespaces()
        .filter(
          namespace =>
            namespace.name.toLowerCase().indexOf(self.filter.querySpec().query.toLowerCase()) !== -1
        );
    });

    self.autocompleteFromNamespaces = (nonPartial, partial) => {
      const result = [];
      const partialLower = partial.toLowerCase();
      self.namespaces().forEach(namespace => {
        if (namespace.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + namespace.name.substring(partial.length));
        }
      });
      return result;
    };

    const ensureDbSet = () => {
      if (self.nonSqlType) {
        if (!self.selectedNamespace().selectedDatabase()) {
          self.selectedNamespace().selectedDatabase(self.selectedNamespace().databases()[0]);
          self.selectedNamespace().selectedDatabaseChanged();
        }
      }
    };

    self.selectedNamespace.subscribe(namespace => {
      if (namespace && !namespace.loaded() && !namespace.loading()) {
        namespace.initDatabases(ensureDbSet);
      } else {
        ensureDbSet();
      }
    });

    self.hasNamespaces = ko.pureComputed(() => self.namespaces().length > 0);

    huePubSub.subscribe('context.catalog.namespaces.refreshed', sourceType => {
      if (self.sourceType !== sourceType) {
        return;
      }

      self.loading(true);
      contextCatalog
        .getNamespaces({ sourceType: self.sourceType })
        .done(context => {
          const newNamespaces = [];
          const existingNamespaceIndex = {};
          self.namespaces().forEach(assistNamespace => {
            existingNamespaceIndex[assistNamespace.namespace.id] = assistNamespace;
          });
          context.namespaces.forEach(newNamespace => {
            if (existingNamespaceIndex[newNamespace.id]) {
              existingNamespaceIndex[newNamespace.id].namespace = newNamespace;
              existingNamespaceIndex[newNamespace.id].name = newNamespace.name;
              existingNamespaceIndex[newNamespace.id].status(newNamespace.status);
              newNamespaces.push(existingNamespaceIndex[newNamespace.id]);
            } else {
              newNamespaces.push(
                new AssistDbNamespace({
                  sourceType: self.sourceType,
                  namespace: newNamespace,
                  i18n: self.i18n,
                  nonSqlType: self.nonSqlType,
                  navigationSettings: self.navigationSettings
                })
              );
            }
          });
          self.namespaces(newNamespaces);
        })
        .always(() => {
          self.loading(false);
        });
    });
  }

  whenLoaded(callback) {
    const self = this;
    self.loadedDeferred.done(callback);
  }

  loadNamespaces(refresh) {
    const self = this;
    self.loading(true);

    if (refresh) {
      contextCatalog.getComputes({ sourceType: self.sourceType, clearCache: true });
    }

    return contextCatalog
      .getNamespaces({ sourceType: self.sourceType, clearCache: refresh })
      .done(context => {
        const assistNamespaces = [];
        let activeNamespace;
        let activeCompute;
        context.namespaces.forEach(namespace => {
          const assistNamespace = new AssistDbNamespace({
            sourceType: self.sourceType,
            namespace: namespace,
            i18n: self.i18n,
            nonSqlType: self.nonSqlType,
            navigationSettings: self.navigationSettings
          });

          if (self.initialNamespace && namespace.id === self.initialNamespace.id) {
            activeNamespace = assistNamespace;
            if (self.initialCompute) {
              activeNamespace.namespace.computes.some(compute => {
                if (compute.id === self.initialCompute.id) {
                  activeCompute = compute;
                }
              });
            }
          }
          assistNamespaces.push(assistNamespace);
        });
        self.namespaces(assistNamespaces);
        if (!refresh) {
          if (activeNamespace) {
            self.selectedNamespace(activeNamespace);
          } else if (assistNamespaces.length) {
            self.selectedNamespace(assistNamespaces[0]);
          }
          if (activeCompute) {
            self.selectedNamespace().compute(activeCompute);
          } else if (
            self.selectedNamespace() &&
            self.selectedNamespace().namespace &&
            self.selectedNamespace().namespace.computes &&
            self.selectedNamespace().namespace.computes.length
          ) {
            self.selectedNamespace().compute(self.selectedNamespace().namespace.computes[0]);
          }
        }
      })
      .fail(() => {
        self.hasErrors(true);
      })
      .always(() => {
        self.loadedDeferred.resolve();
        self.loading(false);
      });
  }

  highlightInside(catalogEntry) {
    const self = this;
    if (self.navigationSettings.rightAssist) {
      return;
    }

    const whenLoaded = () => {
      self.namespaces().some(namespace => {
        if (namespace.namespace.id === catalogEntry.namespace.id) {
          if (self.selectedNamespace() !== namespace) {
            self.selectedNamespace(namespace);
          }
          if (self.selectedNamespace().hasEntries()) {
            self.selectedNamespace().highlightInside(catalogEntry);
          } else {
            self.selectedNamespace().initDatabases(() => {
              self.selectedNamespace().highlightInside(catalogEntry);
            });
          }
          return true;
        }
      });
    };

    if (self.namespaces().length) {
      whenLoaded();
    } else if (self.loading()) {
      const loadingSub = self.loading.subscribe(() => {
        loadingSub.dispose();
        whenLoaded();
      });
    } else {
      self.loadNamespaces().done(whenLoaded);
    }
  }

  triggerRefresh() {
    const self = this;
    self.loadNamespaces(true);
  }
}

export default AssistDbSource;
