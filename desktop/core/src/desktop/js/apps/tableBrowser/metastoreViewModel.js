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

import * as propsMappers from './propsMappers';
import MetastoreSource from 'apps/tableBrowser/metastoreSource';
import dataCatalog from 'catalog/dataCatalog';
import { GET_KNOWN_CONFIG_TOPIC } from 'config/events';
import { findEditorConnector } from 'config/hueConfig';
import huePubSub from 'utils/huePubSub';
import { getFromLocalStorage, withLocalStorage } from 'utils/storageUtils';
import waitForRendered from 'utils/timing/waitForRendered';
import changeURL from 'utils/url/changeURL';

class MetastoreViewModel {
  /**
   * @param {Object} options
   * @param {string} options.user
   * @param {Number} [options.partitionsLimit]
   * @param {boolean} [options.sqlAnalyzerEnabled]
   * @param {boolean} [options.navigatorEnabled]
   * @param {String} options.sourceType
   * @param {String} options.navigatorUrl
   * @constructor
   */
  constructor(options) {
    this.partitionsLimit = options.partitionsLimit;
    this.assistAvailable = ko.observable(true);
    this.isLeftPanelVisible = ko.observable();
    withLocalStorage('assist.assist_panel_visible', this.isLeftPanelVisible, true);
    this.isLeftPanelVisible.subscribe(() => {
      huePubSub.publish('assist.forceRender');
    });
    this.sqlAnalyzerEnabled = ko.observable(options.sqlAnalyzerEnabled || false);
    this.navigatorEnabled = ko.observable(options.navigatorEnabled || false);
    this.appConfig = ko.observable();

    this.propsMappers = propsMappers;

    this.source = ko.observable();
    this.sources = ko.observableArray();

    this.source.subscribe(newValue => {
      newValue.loadNamespaces().done(() => {
        if (newValue.namespace()) {
          newValue
            .namespace()
            .loadDatabases()
            .done(() => {
              this.loadUrl();
            });
        }
      });
    });

    // When manually changed through dropdown
    this.sourceChanged = () => {
      huePubSub.publish('metastore.url.change');
    };

    this.setDbAndTableByName = (dbName, tableName, callback) => {
      this.source()
        .namespace()
        .setDatabaseByName(dbName, () => {
          this.source()
            .namespace()
            .database()
            .setTableByName(tableName, () => {
              this.sourceChanged();
              callback();
            });
        });
    };

    this.loading = ko.pureComputed(() => !this.source() || this.source().loading());

    // TODO: Support dynamic config changes
    huePubSub.publish(GET_KNOWN_CONFIG_TOPIC, clusterConfig => {
      const initialSourceType = options.sourceType || 'hive';

      if (clusterConfig && clusterConfig.app_config && clusterConfig.app_config.catalogs) {
        const sources = [];
        if (clusterConfig.app_config.catalogs) {
          clusterConfig.app_config.catalogs.forEach(interpreter => {
            sources.push(
              new MetastoreSource({
                metastoreViewModel: this,
                displayName: interpreter.displayName,
                name: interpreter.name,
                type: interpreter.type
              })
            );
          });
        }
        if (!sources.length) {
          sources.push(
            new MetastoreSource({
              metastoreViewModel: this,
              displayName: initialSourceType,
              name: initialSourceType,
              type: initialSourceType
            })
          );
        }
        this.sources(sources);
        const found = sources.some(source => {
          if (source.type === initialSourceType) {
            this.source(source);
            return true;
          }
        });
        if (!found) {
          this.source(sources[0]);
        }
      }
    });

    this.navigatorEnabled.subscribe(newValue => {
      huePubSub.publish('meta.navigator.enabled', newValue);
    });

    this.navigatorUrl = ko.observable(options.navigatorUrl);

    this.currentTab = ko.observable('');

    huePubSub.subscribe('assist.database.selected', entry => {
      if (this.source().type !== entry.getConnector().id) {
        const found = this.sources().some(source => {
          if (source.type === entry.getConnector().id) {
            this.source(source);
            return true;
          }
        });
        if (!found) {
          return;
        }
      }

      if (this.source().namespace().id !== entry.namespace.id) {
        const found = this.source()
          .namespaces()
          .some(namespace => {
            if (namespace.id === entry.namespace.id) {
              this.source().namespace(namespace);
              return true;
            }
          });
        if (!found) {
          return;
        }
      }
      if (this.source().namespace().database()) {
        this.source().namespace().database().table(null);
      }
      this.source()
        .namespace()
        .setDatabaseByName(entry.name, () => {
          huePubSub.publish('metastore.url.change');
        });
    });

    huePubSub.subscribe('assist.table.selected', entry => {
      this.loadTableDef(entry, () => {
        huePubSub.publish('metastore.url.change');
      });
    });

    huePubSub.subscribe('metastore.url.change', () => {
      const prefix =
        window.HUE_BASE_URL && window.HUE_BASE_URL.length
          ? window.HUE_BASE_URL + '/metastore/'
          : '/hue/metastore/';
      if (this.source() && this.source().namespace()) {
        const params = {
          source_type: this.source().type
        };
        if (window.HAS_MULTI_CLUSTER) {
          params.namespace = this.source().namespace().id;
        }
        if (this.source().namespace().database() && this.source().namespace().database().table()) {
          changeURL(
            prefix +
              'table/' +
              this.source().namespace().database().table().catalogEntry.path.join('/'),
            params
          );
        } else if (this.source().namespace().database()) {
          changeURL(
            prefix + 'tables/' + this.source().namespace().database().catalogEntry.name,
            params
          );
        } else {
          changeURL(prefix + 'databases', params);
        }
      }
    });

    window.onpopstate = () => {
      if (window.location.pathname.indexOf('/metastore') > -1) {
        this.loadUrl();
      }
    };

    this.databasesBreadcrumb = () => {
      if (this.source().namespace().database()) {
        this.source().namespace().database().table(null);
      }
      this.source().namespace().database(null);
      huePubSub.publish('metastore.url.change');
    };

    this.tablesBreadcrumb = () => {
      this.source().namespace().database().table(null);
      huePubSub.publish('metastore.url.change');
    };

    this.scrollToColumn = col => {
      if (!col.table.samples.loading()) {
        $('.page-content').scrollTop(0);
        this.currentTab('sample');
        waitForRendered(
          '#sampleTable',
          el => el.parent().hasClass('dataTables_wrapper'),
          () => {
            const sampleTable = $('#sampleTable');
            const sampleCol = sampleTable.find('th').filter(function () {
              return $.trim($(this).text()).indexOf(col.catalogEntry.name) > -1;
            });
            sampleTable.find('.columnSelected').removeClass('columnSelected');
            sampleTable
              .find('tr td:nth-child(' + (sampleCol.index() + 1) + ')')
              .addClass('columnSelected');
            let scrollLeft = 0;
            sampleTable.find('th:lt(' + sampleCol.index() + ')').each(function () {
              scrollLeft += $(this).outerWidth();
            });
            scrollLeft = Math.max(0, scrollLeft - 40);
            sampleTable.parent().scrollLeft(scrollLeft);
            sampleTable.parent().trigger('scroll_update');
          }
        );
      }
    };
  }

  loadTableDef(entry, callback) {
    if (this.source().type !== entry.getConnector().id) {
      const found = this.sources().some(source => {
        if (source.type === entry.getConnector().id) {
          this.source(source);
          return true;
        }
      });
      if (!found) {
        return;
      }
    }
    if (this.source().namespace().id !== entry.namespace.id) {
      const found = this.source()
        .namespaces()
        .some(namespace => {
          if (namespace.id === entry.namespace.id) {
            this.source().namespace(namespace);
            return true;
          }
        });
      if (!found) {
        return;
      }
    }

    this.source()
      .namespace()
      .setDatabaseByName(entry.path[0], () => {
        if (this.source().namespace().database()) {
          if (
            this.source().namespace().database().table() &&
            this.source().namespace().database().table().catalogEntry.name === entry.name
          ) {
            if (callback) {
              callback();
            }
            return;
          }

          const setTableAfterLoad = clearDbCacheOnMissing => {
            const foundTables = this.source()
              .namespace()
              .database()
              .tables()
              .filter(table => table.catalogEntry.name === entry.name);
            if (foundTables.length === 1) {
              this.source().namespace().database().setTable(foundTables[0], callback);
            } else if (clearDbCacheOnMissing) {
              const dbEntry = this.source().namespace().database().catalogEntry;
              dbEntry
                .getChildren({ refreshCache: true, silenceErrors: true })
                .then(childEntries => {
                  if (childEntries.some(childEntry => childEntry.name === entry.name)) {
                    this.source()
                      .namespace()
                      .database()
                      .load(() => {
                        setTableAfterLoad(false);
                      });
                  } else {
                    dbEntry
                      .clearCache({
                        invalidate: 'invalidate',
                        silenceErrors: true,
                        targetChild: entry.name
                      })
                      .then(() => {
                        this.source()
                          .namespace()
                          .database()
                          .load(() => {
                            setTableAfterLoad(false);
                          });
                      });
                  }
                })
                .catch(() => {});
            }
          };

          if (!this.source().namespace().database().loaded()) {
            const doOnce = this.source()
              .namespace()
              .database()
              .loaded.subscribe(() => {
                setTableAfterLoad(true);
                doOnce.dispose();
              });
          } else {
            setTableAfterLoad(true);
          }
        }
      });
  }

  loadUrl() {
    const path = window.location.pathname.startsWith(window.HUE_BASE_URL)
      ? window.location.pathname.substr(window.HUE_BASE_URL.length)
      : window.location.pathname.substr(4) || '/metastore/tables';
    const pathParts = path.split('/');
    if (pathParts[0] === '') {
      pathParts.shift();
    }
    while (pathParts[0] === 'hue') {
      pathParts.shift();
    }
    if (pathParts[0] === 'metastore') {
      pathParts.shift();
    }
    const loadedDeferred = $.Deferred();

    if (!this.loading()) {
      loadedDeferred.resolve();
    } else {
      const loadSub = this.loading.subscribe(() => {
        loadSub.dispose();
        loadedDeferred.resolve();
      });
    }

    const sourceAndNamespaceDeferred = $.Deferred();

    loadedDeferred.done(() => {
      let search = location.search;
      let namespaceId;
      let connectorId;
      let sourceType;
      if (search) {
        search = search.replace('?', '');
        search.split('&').forEach(param => {
          if (param.indexOf('namespace=') === 0) {
            namespaceId = param.replace('namespace=', '');
          } else if (param.indexOf('source_type=') === 0) {
            sourceType = param.replace('source_type=', ''); // Keep old links working
          } else if (param.indexOf('source=') === 0) {
            sourceType = param.replace('source=', ''); // Keep old links working
          } else if (param.indexOf('connector_id=') === 0) {
            connectorId = param.replace('connector_id=', '');
          }
        });
      }

      if (!connectorId && sourceType) {
        connectorId = sourceType;
      }

      if (connectorId && connectorId !== this.source().connector().id) {
        const found = this.sources().some(source => {
          if (connectorId === source.connector().id) {
            this.source(source);
            return true;
          }
        });
        if (!found) {
          sourceAndNamespaceDeferred.reject();
          return;
        }
      }

      if (!namespaceId && getFromLocalStorage('contextSelector.lastSelectedNamespace')) {
        namespaceId = getFromLocalStorage('contextSelector.lastSelectedNamespace').id;
      }

      this.source().lastLoadNamespacesDeferred.done(() => {
        if (namespaceId && namespaceId !== this.source().namespace().id) {
          const found = this.source()
            .namespaces()
            .some(namespace => {
              if (namespace.id === namespaceId) {
                this.source().namespace(namespace);
                return true;
              }
            });
          if (!found) {
            sourceAndNamespaceDeferred.reject();
            return;
          } else {
            sourceAndNamespaceDeferred.resolve();
          }
        } else {
          sourceAndNamespaceDeferred.resolve();
        }
      });
    });

    sourceAndNamespaceDeferred.done(() => {
      const namespace = this.source().namespace();
      switch (pathParts[0]) {
        case 'databases':
          if (namespace.database()) {
            namespace.database().table(null);
            namespace.database(null);
          }
          break;
        case 'tables':
          if (namespace.database()) {
            namespace.database().table(null);
          }
          namespace.setDatabaseByName(pathParts[1]);
          break;
        case 'table':
          huePubSub.subscribe(
            'metastore.loaded.table',
            () => {
              this.currentTab('overview');
            },
            'metastore'
          );

          dataCatalog
            .getEntry({
              connector: findEditorConnector(connector => connector.id === this.source().type),
              namespace: namespace.namespace,
              compute: namespace.compute,
              path: [pathParts[1], pathParts[2]]
            })
            .then(entry => {
              this.loadTableDef(entry, () => {
                if (pathParts.length > 3 && pathParts[3] === 'partitions') {
                  huePubSub.subscribe(
                    'metastore.loaded.partitions',
                    () => {
                      this.currentTab('partitions');
                    },
                    'metastore'
                  );
                }
              });
            });
      }
    });
  }
}

export default MetastoreViewModel;
