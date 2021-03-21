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

import * as ko from 'knockout';

import AssistDbEntry from 'ko/components/assist/assistDbEntry';
import AssistDbSource from 'ko/components/assist/assistDbSource';
import componentUtils from 'ko/components/componentUtils';
import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import { TEMPLATE, AssistantUtils } from 'ko/components/assist/ko.assistEditorContextPanel';
import { findDashboardConnector } from 'config/hueConfig';

class AssistDashboardPanel {
  constructor() {
    this.isSolr = ko.observable(true);

    this.showRisks = ko.observable(false);

    this.filter = {
      querySpec: ko
        .observable({
          query: '',
          facets: {},
          text: []
        })
        .extend({ rateLimit: 300 })
    };

    this.sourceType = ko.observable('solr');

    this.activeTables = ko.observableArray();

    this.filteredTables = AssistantUtils.getFilteredTablesPureComputed(this);

    this.someLoading = ko.pureComputed(() => {
      return this.activeTables().some(table => {
        return table.loading() || (!table.hasEntries() && !table.hasErrors());
      });
    });

    const navigationSettings = {
      showStats: true,
      rightAssist: true
    };
    const i18n = {};

    huePubSub.subscribe('set.active.dashboard.collection', collection => {
      const collectionName = collection.name();

      if (!collectionName) {
        return;
      }

      this.sourceType = ko.observable(collection.engine());

      const connector = findDashboardConnector(connector => connector.id === collection.engine());

      const assistDbSource = new AssistDbSource({
        i18n: i18n,
        initialNamespace: collection.activeNamespace,
        initialCompute: collection.activeCompute,
        type: collection.engine(),
        name: collection.engine(),
        connector: connector,
        nonSqlType: true,
        navigationSettings: navigationSettings
      });

      const fakeParentName =
        collectionName.indexOf('.') > -1 ? collectionName.split('.')[0] : 'default';

      const sourceType =
        collection.source() === 'query' ? collection.engine() + '-query' : collection.engine();

      dataCatalog
        .getEntry({
          namespace: collection.activeNamespace,
          compute: collection.activeCompute,
          connector: { id: sourceType }, // TODO: Use connectors in assist dashboard panel
          path: [fakeParentName],
          definition: { type: 'database' }
        })
        .then(fakeDbCatalogEntry => {
          const assistFakeDb = new AssistDbEntry(
            fakeDbCatalogEntry,
            null,
            assistDbSource,
            this.filter,
            i18n,
            navigationSettings
          );
          dataCatalog
            .getEntry({
              namespace: collection.activeNamespace,
              compute: collection.activeCompute,
              connector: { id: sourceType }, // TODO: Use connectors in assist dashboard panel
              path: [
                fakeParentName,
                collectionName.indexOf('.') > -1 ? collectionName.split('.')[1] : collectionName
              ],
              definition: { type: 'table' }
            })
            .then(collectionCatalogEntry => {
              const collectionEntry = new AssistDbEntry(
                collectionCatalogEntry,
                assistFakeDb,
                assistDbSource,
                this.filter,
                i18n,
                navigationSettings
              );
              this.activeTables([collectionEntry]);

              if (
                !collectionEntry.loaded &&
                !collectionEntry.hasErrors() &&
                !collectionEntry.loading()
              ) {
                collectionEntry.loadEntries(() => {
                  collectionEntry.toggleOpen();
                });
              }
            });
        });

      this.autocompleteFromEntries = function (nonPartial, partial) {
        const added = {};
        const result = [];
        const partialLower = partial.toLowerCase();
        this.activeTables().forEach(table => {
          if (
            !added[table.catalogEntry.name] &&
            table.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0
          ) {
            added[table.catalogEntry.name] = true;
            result.push(nonPartial + partial + table.catalogEntry.name.substring(partial.length));
          }
          table.entries().forEach(col => {
            if (
              !added[col.catalogEntry.name] &&
              col.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0
            ) {
              added[col.catalogEntry.name] = true;
              result.push(nonPartial + partial + col.catalogEntry.name.substring(partial.length));
            }
          });
        });
        return result;
      };
    });
  }
}

componentUtils.registerStaticComponent('assist-dashboard-panel', AssistDashboardPanel, TEMPLATE);
