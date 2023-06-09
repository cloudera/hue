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

import { getNamespaces } from 'catalog/contextCatalog';
import { NAMESPACES_REFRESHED_TOPIC } from 'catalog/events';
import huePubSub from 'utils/huePubSub';
import MetastoreNamespace from 'apps/tableBrowser/metastoreNamespace';
import {
  ASSIST_DB_PANEL_IS_READY_EVENT,
  ASSIST_IS_DB_PANEL_READY_EVENT,
  ASSIST_SET_DATABASE_EVENT
} from 'ko/components/assist/events';
import { findEditorConnector } from 'config/hueConfig';
import { getFromLocalStorage } from 'utils/storageUtils';

class MetastoreSource {
  constructor(options) {
    this.type = options.type;
    this.name = options.name;
    this.displayName = options.displayName;
    this.metastoreViewModel = options.metastoreViewModel;

    this.reloading = ko.observable(false);
    this.loading = ko.observable(false);

    this.lastLoadNamespacesDeferred = $.Deferred();
    this.namespace = ko.observable();
    this.namespaces = ko.observableArray();

    this.namespace.subscribe(() => {
      if (this.namespace() && this.namespace().databases().length === 0) {
        this.namespace().loadDatabases();
      }
    });

    // When manually changed through dropdown
    this.namespaceChanged = (newNamespace, previousNamespace) => {
      if (previousNamespace.database() && !this.namespace().database()) {
        // Try to set the same database by name, if not there it will revert to 'default'
        this.namespace().setDatabaseByName(previousNamespace.database().catalogEntry.name, () => {
          huePubSub.publish('metastore.url.change');
        });
      } else {
        huePubSub.publish('metastore.url.change');
      }
    };

    this.connector = ko.observable(findEditorConnector(connector => connector.id === this.type));

    huePubSub.subscribe(ASSIST_DB_PANEL_IS_READY_EVENT, () => {
      this.lastLoadNamespacesDeferred.done(() => {
        const namespaceId = _this.namespace().namespace.id;
        const localStorageKey = `assist_${this.type}_${namespaceId}.lastSelectedDb`;
        let lastSelectedDb = getFromLocalStorage(localStorageKey);
        if (!lastSelectedDb && lastSelectedDb !== '') {
          lastSelectedDb = 'default';
        }
        huePubSub.publish(ASSIST_SET_DATABASE_EVENT, {
          connector: this.connector(),
          namespace: this.namespace().namespace,
          name: lastSelectedDb
        });
      });
    });

    huePubSub.publish(ASSIST_IS_DB_PANEL_READY_EVENT);

    const getCurrentState = () => {
      const result = {
        namespaceId: null,
        database: null,
        table: null
      };
      if (this.namespace()) {
        result.namespaceId = this.namespace().id;
        if (this.namespace().database()) {
          result.database = this.namespace().database().catalogEntry.name;
          if (this.namespace().database().table()) {
            result.table = this.namespace().database().table().catalogEntry.name;
          }
        }
      }
      return result;
    };

    const setState = state => {
      if (state.namespaceId) {
        this.setNamespaceById(state.namespaceId).done(() => {
          if (state.database) {
            this.namespace().setDatabaseByName(state.database, () => {
              if (this.namespace().database() && state.table) {
                this.namespace().database().setTableByName(state.table);
              }
            });
          }
        });
      }
    };

    const completeRefresh = previousState => {
      this.reloading(true);
      if (this.namespace() && this.namespace().database() && this.namespace().database().table()) {
        this.namespace().database().table(null);
      }
      if (this.namespace() && this.namespace().database()) {
        this.namespace().database(null);
      }
      if (this.namespace()) {
        this.namespace(null);
      }
      this.loadNamespaces()
        .done(() => {
          setState(previousState);
        })
        .always(() => {
          this.reloading(false);
        });
    };

    huePubSub.subscribe(NAMESPACES_REFRESHED_TOPIC, connectorId => {
      if (this.type !== connectorId) {
        return;
      }
      const previousState = getCurrentState();
      completeRefresh(previousState);
    });

    huePubSub.subscribe('data.catalog.entry.refreshed', details => {
      const refreshedEntry = details.entry;

      if (refreshedEntry.getConnector().id !== this.type) {
        return;
      }

      const previousState = getCurrentState();

      if (refreshedEntry.isSource()) {
        completeRefresh(previousState);
      } else if (refreshedEntry.isDatabase() && this.namespace()) {
        this.namespace()
          .databases()
          .some(database => {
            if (database.catalogEntry === refreshedEntry) {
              database.load(
                () => {
                  setState(previousState);
                },
                this.metastoreViewModel.sqlAnalyzerEnabled(),
                this.metastoreViewModel.navigatorEnabled()
              );
              return true;
            }
          });
      } else if (refreshedEntry.isTableOrView()) {
        this.namespace()
          .databases()
          .some(database => {
            if (database.catalogEntry.name === refreshedEntry.path[0]) {
              database.tables().some(table => {
                if (table.catalogEntry.name === refreshedEntry.name) {
                  table.load();
                  return true;
                }
              });
              return true;
            }
          });
      }
    });
  }

  loadNamespaces() {
    this.loading(true);
    getNamespaces({ connector: this.connector() })
      .then(context => {
        const namespacesWithComputes = context.namespaces.filter(
          namespace => namespace.computes.length
        );
        this.namespaces(
          namespacesWithComputes.map(
            namespace =>
              new MetastoreNamespace({
                metastoreViewModel: this.metastoreViewModel,
                sourceType: this.type,
                navigatorEnabled: this.metastoreViewModel.navigatorEnabled,
                sqlAnalyzerEnabled: this.metastoreViewModel.sqlAnalyzerEnabled,
                namespace: namespace
              })
          )
        );
        this.namespace(this.namespaces()[0]);
        this.lastLoadNamespacesDeferred.resolve();
      })
      .catch(this.lastLoadNamespacesDeferred.reject)
      .finally(() => {
        this.loading(false);
      });
    return this.lastLoadNamespacesDeferred;
  }

  setNamespaceById(namespaceId) {
    const deferred = $.Deferred();
    this.lastLoadNamespacesDeferred
      .done(() => {
        const found = this.namespaces().some(namespace => {
          if (namespace.namespace.id === namespaceId) {
            this.namespace(namespace);
            deferred.resolve();
            return true;
          }
        });
        if (!found) {
          deferred.reject();
        }
      })
      .fail(deferred.reject);
    return deferred.promise();
  }
}

export default MetastoreSource;
