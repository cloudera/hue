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

import sqlAnalyzerRepository from 'catalog/analyzer/sqlAnalyzerRepository';
import $ from 'jquery';
import * as ko from 'knockout';

import { ASSIST_ACTIVE_DB_CHANGED_EVENT } from './events';
import dataCatalog from 'catalog/dataCatalog';
import AssistDbEntry from 'ko/components/assist/assistDbEntry';
import huePubSub from 'utils/huePubSub';
import { getFromLocalStorage, setInLocalStorage } from 'utils/storageUtils';

class AssistDbNamespace {
  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {string} options.sourceType
   * @param {Connector} options.connector
   * @param {ContextNamespace} options.namespace
   * @param {boolean} options.nonSqlType - Optional, default false
   * @param {Object} options.navigationSettings
   * @constructor
   */
  constructor(options) {
    const self = this;

    self.i18n = options.i18n;
    self.navigationSettings = options.navigationSettings;
    self.sourceType = options.sourceType;
    self.connector = options.connector;
    self.nonSqlType = options.nonSqlType;

    self.namespace = options.namespace;
    self.status = ko.observable(options.namespace.status);
    // TODO: Compute selection in assist?
    self.compute = ko.observable();
    if (self.namespace.computes.length) {
      self.compute(self.namespace.computes[0]);
    }
    self.name = options.namespace.name;

    self.dbIndex = {};
    self.databases = ko.observableArray();
    self.selectedDatabase = ko.observable();

    self.highlight = ko.observable(false);

    self.loadedPromise = $.Deferred();
    self.loadedDeferred = $.Deferred();
    self.loaded = ko.observable(false);
    self.loading = ko.observable(false);
    self.reloading = ko.observable(false);
    self.hasErrors = ko.observable(false);

    self.loadingTables = ko.pureComputed(
      () =>
        typeof self.selectedDatabase() !== 'undefined' &&
        self.selectedDatabase() !== null &&
        self.selectedDatabase().loading()
    );

    self.filter = {
      querySpec: ko.observable({}).extend({ rateLimit: 300 })
    };

    self.hasEntries = ko.pureComputed(() => self.databases().length > 0);

    self.filteredEntries = ko.pureComputed(() => {
      if (
        !self.filter.querySpec() ||
        typeof self.filter.querySpec().query === 'undefined' ||
        !self.filter.querySpec().query
      ) {
        return self.databases();
      }
      return self
        .databases()
        .filter(
          database =>
            database.catalogEntry.name
              .toLowerCase()
              .indexOf(self.filter.querySpec().query.toLowerCase()) !== -1
        );
    });

    self.autocompleteFromEntries = (nonPartial, partial) => {
      const result = [];
      const partialLower = partial.toLowerCase();
      self.databases().forEach(db => {
        if (db.catalogEntry.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + db.catalogEntry.name.substring(partial.length));
        }
      });
      return result;
    };

    self.selectedDatabase.subscribe(() => {
      const db = self.selectedDatabase();
      if (db) {
        huePubSub.publish(ASSIST_ACTIVE_DB_CHANGED_EVENT, {
          connector: this.connector,
          namespace: this.namespace,
          database: db.name
        });
      }

      if (window.HAS_SQL_ANALYZER && db && !db.popularityIndexSet && !self.nonSqlType) {
        const sqlAnalyzer = sqlAnalyzerRepository.getSqlAnalyzer(db.catalogEntry.getConnector());
        db.catalogEntry
          .loadSqlAnalyzerPopularityForChildren({ silenceErrors: true, sqlAnalyzer })
          .then(() => {
            const applyPopularity = () => {
              db.entries().forEach(entry => {
                if (
                  entry.catalogEntry.sqlAnalyzerPopularity &&
                  entry.catalogEntry.sqlAnalyzerPopularity.popularity >= 5
                ) {
                  entry.popularity(entry.catalogEntry.sqlAnalyzerPopularity.popularity);
                }
              });
            };

            if (db.loading()) {
              const subscription = db.loading.subscribe(() => {
                subscription.dispose();
                applyPopularity();
              });
            } else if (db.entries().length === 0) {
              const subscription = db.entries.subscribe(newEntries => {
                if (newEntries.length > 0) {
                  subscription.dispose();
                  applyPopularity();
                }
              });
            } else {
              applyPopularity();
            }
          });
      }
    });

    self.selectedDatabaseChanged = () => {
      if (self.selectedDatabase()) {
        if (!self.selectedDatabase().hasEntries() && !self.selectedDatabase().loading()) {
          self.selectedDatabase().loadEntries();
        }
        if (!self.navigationSettings.rightAssist) {
          const entry = self.selectedDatabase().catalogEntry;
          setInLocalStorage(
            'assist_' + entry.getConnector().id + '_' + entry.namespace.id + '.lastSelectedDb',
            entry.name
          );
          huePubSub.publish('assist.database.set', entry);
        }
      } else {
        setInLocalStorage(
          'assist_' + self.connector.id + '_' + self.namespace.id + '.lastSelectedDb',
          null
        );
      }
    };

    const nestedFilter = {
      querySpec: ko.observable({}).extend({ rateLimit: 300 })
    };

    self.setDatabase = databaseName => {
      if (
        databaseName &&
        self.selectedDatabase() &&
        databaseName === self.selectedDatabase().catalogEntry.name
      ) {
        return;
      }
      if (databaseName && self.dbIndex[databaseName]) {
        self.selectedDatabase(self.dbIndex[databaseName]);
        self.selectedDatabaseChanged();
        return;
      }
      let lastSelectedDb = getFromLocalStorage(
        'assist_' + self.sourceType + '_' + self.namespace.id + '.lastSelectedDb'
      );

      if (!lastSelectedDb && lastSelectedDb !== '') {
        lastSelectedDb = 'default';
      }
      if (lastSelectedDb && self.dbIndex[lastSelectedDb]) {
        self.selectedDatabase(self.dbIndex[lastSelectedDb]);
        self.selectedDatabaseChanged();
      } else if (lastSelectedDb && self.databases().length > 0) {
        self.selectedDatabase(self.databases()[0]);
        self.selectedDatabaseChanged();
      }
    };

    self.initDatabases = callback => {
      if (self.loading()) {
        return;
      }
      self.loading(true);
      self.hasErrors(false);

      const lastSelectedDbName = self.selectedDatabase()
        ? self.selectedDatabase().catalogEntry.name
        : null;

      self.selectedDatabase(null);
      self.databases([]);

      dataCatalog
        .getEntry({
          namespace: self.namespace,
          compute: self.compute(),
          connector: self.connector,
          path: [],
          definition: { type: 'source' }
        })
        .then(catalogEntry => {
          self.catalogEntry = catalogEntry;
          self.catalogEntry
            .getChildren({ silenceErrors: self.navigationSettings.rightAssist })
            .then(databaseEntries => {
              self.dbIndex = {};
              let hasNavMeta = false;
              const dbs = [];

              databaseEntries.forEach(catalogEntry => {
                hasNavMeta = hasNavMeta || !!catalogEntry.navigatorMeta;
                const database = new AssistDbEntry(
                  catalogEntry,
                  null,
                  self,
                  nestedFilter,
                  self.i18n,
                  self.navigationSettings
                );
                self.dbIndex[catalogEntry.name] = database;
                if (catalogEntry.name === lastSelectedDbName) {
                  self.selectedDatabase(database);
                  self.selectedDatabaseChanged();
                }
                dbs.push(database);
              });

              if (!hasNavMeta && !self.nonSqlType) {
                try {
                  self.catalogEntry.loadNavigatorMetaForChildren({ silenceErrors: true });
                } catch (err) {}
              }
              self.databases(dbs);

              if (typeof callback === 'function') {
                callback();
              }
            })
            .catch(() => {
              self.hasErrors(true);
            })
            .finally(() => {
              self.loaded(true);
              self.loadedDeferred.resolve();
              self.loading(false);
              self.reloading(false);
            });
        });
    };

    self.modalItem = ko.observable();

    if (!self.navigationSettings.rightAssist) {
      huePubSub.subscribe('data.catalog.entry.refreshed', details => {
        if (
          self.namespace.id !== details.entry.namespace.id ||
          details.entry.getConnector().id !== self.sourceType
        ) {
          return;
        }
        if (self.catalogEntry === details.entry) {
          self.initDatabases();
        } else {
          const targetPath = details.entry.path.join('.');
          const findAndReloadInside = entries => {
            return entries.some(entry => {
              if (entry.catalogEntry.path.join('.') === targetPath) {
                entry.catalogEntry = details.entry;
                entry.loadEntries();
                return true;
              }
              return findAndReloadInside(entry.entries());
            });
          };
          findAndReloadInside(self.databases());
        }
      });
    }
  }

  whenLoaded(callback) {
    const self = this;
    self.loadedDeferred.done(callback);
  }

  highlightInside(catalogEntry) {
    const self = this;
    let foundDb;

    const findDatabase = () => {
      self.databases().forEach(db => {
        db.highlight(false);
        if (db.databaseName === catalogEntry.path[0]) {
          foundDb = db;
        }
      });

      if (foundDb) {
        const whenLoaded = () => {
          if (self.selectedDatabase() !== foundDb) {
            self.selectedDatabase(foundDb);
          }
          if (!foundDb.open()) {
            foundDb.open(true);
          }
          window.setTimeout(() => {
            huePubSub.subscribeOnce('assist.db.scrollToComplete', () => {
              foundDb.highlight(true);
              // Timeout is for animation effect
              window.setTimeout(() => {
                foundDb.highlight(false);
              }, 1800);
            });
            if (catalogEntry.path.length > 1) {
              foundDb.highlightInside(catalogEntry.path.slice(1));
            } else {
              huePubSub.publish('assist.db.scrollTo', foundDb);
            }
          }, 0);
        };

        if (foundDb.hasEntries()) {
          whenLoaded();
        } else {
          foundDb.loadEntries(whenLoaded);
        }
      }
    };

    if (!self.loaded()) {
      self.initDatabases(findDatabase);
    } else {
      findDatabase();
    }
  }

  triggerRefresh() {
    const self = this;
    if (self.catalogEntry) {
      self.catalogEntry.clearCache();
    }
  }
}

export default AssistDbNamespace;
