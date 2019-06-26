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
import AssistDbSource from 'assist/assistDbSource';
import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';

class AssistDbPanel {
  /**
   * @param {Object} options
   * @param {Object} options.i18n
   * @param {Object[]} options.sourceTypes - All the available SQL source types
   * @param {string} options.sourceTypes[].name - Example: Hive SQL
   * @param {string} options.sourceTypes[].type - Example: hive
   * @param {string} [options.activeSourceType] - Example: hive
   * @param {Object} options.navigationSettings - enable/disable the links
   * @param {boolean} options.navigationSettings.openItem
   * @param {boolean} options.navigationSettings.showStats
   * @param {boolean} options.navigationSettings.pinEnabled
   * @param {boolean} [options.isSolr] - Default false;
   * @param {boolean} [options.isStreams] - Default false;
   * @constructor
   **/
  constructor(options) {
    const self = this;
    self.options = options;
    self.i18n = options.i18n;
    self.initialized = false;
    self.initalizing = false;

    self.isStreams = options.isStreams;
    self.isSolr = options.isSolr;
    self.nonSqlType = self.isSolr || self.isStreams;

    if (typeof options.sourceTypes === 'undefined') {
      options.sourceTypes = [];

      if (self.isSolr) {
        options.sourceTypes = [{ type: 'solr', name: 'solr' }];
      } else if (self.isStreams) {
        options.sourceTypes = [{ type: 'kafka', name: 'kafka' }];
      } else {
        window.ASSIST_SQL_INTERPRETERS.forEach(interpreter => {
          options.sourceTypes.push(interpreter);
        });
      }
    }

    self.sources = ko.observableArray();
    self.sourceIndex = {};
    self.selectedSource = ko.observable(null);

    options.sourceTypes.forEach(sourceType => {
      self.sourceIndex[sourceType.type] = new AssistDbSource({
        i18n: self.i18n,
        type: sourceType.type,
        name: sourceType.name,
        nonSqlType: sourceType.type === 'solr' || sourceType.type === 'kafka',
        navigationSettings: options.navigationSettings
      });
      self.sources.push(self.sourceIndex[sourceType.type]);
    });

    if (self.sources().length === 1) {
      self.selectedSource(self.sources()[0]);
    }

    if (self.sourceIndex['solr']) {
      huePubSub.subscribe('assist.collections.refresh', () => {
        const solrSource = self.sourceIndex['solr'];
        const doRefresh = () => {
          if (solrSource.selectedNamespace()) {
            const assistDbNamespace = solrSource.selectedNamespace();
            dataCatalog
              .getEntry({
                sourceType: 'solr',
                namespace: assistDbNamespace.namespace,
                compute: assistDbNamespace.compute(),
                path: []
              })
              .done(entry => {
                entry.clearCache({ cascade: true });
              });
          }
        };
        if (!solrSource.hasNamespaces()) {
          solrSource.loadNamespaces(true).done(doRefresh);
        } else {
          doRefresh();
        }
      });
    }

    huePubSub.subscribe('assist.db.highlight', catalogEntry => {
      huePubSub.publish('left.assist.show');
      if (catalogEntry.getSourceType() === 'solr') {
        huePubSub.publish('assist.show.solr');
      } else {
        huePubSub.publish('assist.show.sql');
      }
      huePubSub.publish('context.popover.hide');
      window.setTimeout(() => {
        let foundSource;
        self.sources().some(source => {
          if (source.sourceType === catalogEntry.getSourceType()) {
            foundSource = source;
            return true;
          }
        });
        if (foundSource) {
          if (self.selectedSource() !== foundSource) {
            self.selectedSource(foundSource);
          }
          foundSource.highlightInside(catalogEntry);
        }
      }, 0);
    });

    if (!self.isSolr && !self.isStreams) {
      huePubSub.subscribe('assist.set.database', databaseDef => {
        if (!databaseDef.source || !self.sourceIndex[databaseDef.source]) {
          return;
        }
        self.selectedSource(self.sourceIndex[databaseDef.source]);
        self.setDatabaseWhenLoaded(databaseDef.namespace, databaseDef.name);
      });

      const getSelectedDatabase = source => {
        const deferred = $.Deferred();
        const assistDbSource = self.sourceIndex[source];
        if (assistDbSource) {
          assistDbSource.loadedDeferred.done(() => {
            if (assistDbSource.selectedNamespace()) {
              assistDbSource.selectedNamespace().loadedDeferred.done(() => {
                if (assistDbSource.selectedNamespace().selectedDatabase()) {
                  deferred.resolve({
                    sourceType: source,
                    namespace: assistDbSource.selectedNamespace().namespace,
                    name: assistDbSource.selectedNamespace().selectedDatabase().name
                  });
                } else {
                  const lastSelectedDb = apiHelper.getFromTotalStorage(
                    'assist_' + source + '_' + assistDbSource.selectedNamespace().namespace.id,
                    'lastSelectedDb',
                    'default'
                  );
                  deferred.resolve({
                    sourceType: source,
                    namespace: assistDbSource.selectedNamespace().namespace,
                    name: lastSelectedDb
                  });
                }
              });
            } else {
              deferred.resolve({
                sourceType: source,
                namespace: { id: 'default' },
                name: 'default'
              });
            }
          });
        } else {
          deferred.reject();
        }

        return deferred;
      };

      huePubSub.subscribe('assist.get.database', source => {
        getSelectedDatabase(source).done(databaseDef => {
          huePubSub.publish('assist.database.set', databaseDef);
        });
      });

      huePubSub.subscribe('assist.get.database.callback', options => {
        getSelectedDatabase(options.source).done(options.callback);
      });

      huePubSub.subscribe('assist.get.source', () => {
        huePubSub.publish(
          'assist.source.set',
          self.selectedSource() ? self.selectedSource().sourceType : undefined
        );
      });

      huePubSub.subscribe('assist.set.source', source => {
        if (self.sourceIndex[source]) {
          self.selectedSource(self.sourceIndex[source]);
        }
      });

      huePubSub.publish('assist.db.panel.ready');

      huePubSub.subscribe('assist.is.db.panel.ready', () => {
        huePubSub.publish('assist.db.panel.ready');
      });

      self.selectedSource.subscribe(newSource => {
        if (newSource) {
          if (newSource.namespaces().length === 0) {
            newSource.loadNamespaces();
          }
          apiHelper.setInTotalStorage('assist', 'lastSelectedSource', newSource.sourceType);
        } else {
          apiHelper.setInTotalStorage('assist', 'lastSelectedSource');
        }
      });
    }

    if (self.isSolr || self.isStreams) {
      if (self.sources().length === 1) {
        self.selectedSource(self.sources()[0]);
        self
          .selectedSource()
          .loadNamespaces()
          .done(() => {
            const solrNamespace = self.selectedSource().selectedNamespace();
            if (solrNamespace) {
              solrNamespace.initDatabases();
              solrNamespace.whenLoaded(() => {
                solrNamespace.setDatabase('default');
              });
            }
          });
      }
    }

    self.breadcrumb = ko.pureComputed(() => {
      if (self.isStreams && self.selectedSource()) {
        return self.selectedSource().name;
      }
      if (!self.isSolr && self.selectedSource()) {
        if (self.selectedSource().selectedNamespace()) {
          if (
            self
              .selectedSource()
              .selectedNamespace()
              .selectedDatabase()
          ) {
            return self
              .selectedSource()
              .selectedNamespace()
              .selectedDatabase().catalogEntry.name;
          }
          if (window.HAS_MULTI_CLUSTER) {
            return self.selectedSource().selectedNamespace().name;
          }
        }
        return self.selectedSource().name;
      }
      return null;
    });
  }

  setDatabaseWhenLoaded(namespace, databaseName) {
    const self = this;
    self.selectedSource().whenLoaded(() => {
      if (
        self.selectedSource().selectedNamespace() &&
        self.selectedSource().selectedNamespace().namespace.id !== namespace.id
      ) {
        self
          .selectedSource()
          .namespaces()
          .some(otherNamespace => {
            if (otherNamespace.namespace.id === namespace.id) {
              self.selectedSource().selectedNamespace(otherNamespace);
              return true;
            }
          });
      }

      if (self.selectedSource().selectedNamespace()) {
        self
          .selectedSource()
          .selectedNamespace()
          .whenLoaded(() => {
            self
              .selectedSource()
              .selectedNamespace()
              .setDatabase(databaseName);
          });
      }
    });
  }

  back() {
    if (this.isStreams) {
      this.selectedSource(null);
      return;
    }
    if (this.selectedSource()) {
      if (this.selectedSource() && this.selectedSource().selectedNamespace()) {
        if (
          this.selectedSource()
            .selectedNamespace()
            .selectedDatabase()
        ) {
          this.selectedSource()
            .selectedNamespace()
            .selectedDatabase(null);
        } else if (window.HAS_MULTI_CLUSTER) {
          this.selectedSource().selectedNamespace(null);
        } else {
          this.selectedSource(null);
        }
      } else {
        this.selectedSource(null);
      }
    }
  }

  init() {
    if (this.initialized) {
      return;
    }
    if (this.isSolr) {
      this.selectedSource(this.sourceIndex['solr']);
    } else if (this.isStreams) {
      this.selectedSource(this.sourceIndex['kafka']);
    } else {
      const storageSourceType = apiHelper.getFromTotalStorage('assist', 'lastSelectedSource');
      if (!this.selectedSource()) {
        if (this.options.activeSourceType) {
          this.selectedSource(this.sourceIndex[this.options.activeSourceType]);
        } else if (storageSourceType && this.sourceIndex[storageSourceType]) {
          this.selectedSource(this.sourceIndex[storageSourceType]);
        }
      }
    }
    this.initialized = true;
  }
}

export default AssistDbPanel;
