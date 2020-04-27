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

import apiHelper from 'api/apiHelper';
import huePubSub from 'utils/huePubSub';
import hueUtils from 'utils/hueUtils';
import MetastoreSource from 'apps/table_browser/metastoreSource';
import { GET_KNOWN_CONFIG_EVENT } from 'utils/hueConfig';

class MetastoreViewModel {
  /**
   * @param {Object} options
   * @param {string} options.user
   * @param {Number} [options.partitionsLimit]
   * @param {boolean} [options.optimizerEnabled]
   * @param {boolean} [options.navigatorEnabled]
   * @param {String} options.sourceType
   * @param {String} options.optimizerUrl
   * @param {String} options.navigatorUrl
   * @constructor
   */
  constructor(options) {
    this.partitionsLimit = options.partitionsLimit;
    this.assistAvailable = ko.observable(true);
    this.isLeftPanelVisible = ko.observable();
    apiHelper.withTotalStorage('assist', 'assist_panel_visible', this.isLeftPanelVisible, true);
    this.optimizerEnabled = ko.observable(options.optimizerEnabled || false);
    this.navigatorEnabled = ko.observable(options.navigatorEnabled || false);
    this.appConfig = ko.observable();

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

    this.loading = ko.pureComputed(() => !this.source() || this.source().loading());

    // TODO: Support dynamic config changes
    huePubSub.publish(GET_KNOWN_CONFIG_EVENT, clusterConfig => {
      const initialSourceType = options.sourceType || 'hive';

      if (clusterConfig && clusterConfig.app_config && clusterConfig.app_config.catalogs) {
        const sources = [];
        if (clusterConfig.app_config.catalogs) {
          clusterConfig.app_config.catalogs.forEach(interpreter => {
            sources.push(
              new MetastoreSource({
                metastoreViewModel: this,
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

    this.optimizerUrl = ko.observable(options.optimizerUrl);
    this.navigatorUrl = ko.observable(options.navigatorUrl);

    this.currentTab = ko.observable('');

    huePubSub.subscribe('assist.database.selected', databaseDef => {
      if (this.source().type !== databaseDef.sourceType) {
        const found = this.sources().some(source => {
          if (source.type === databaseDef.sourceType) {
            this.source(source);
            return true;
          }
        });
        if (!found) {
          return;
        }
      }

      if (this.source().namespace().id !== databaseDef.namespace.id) {
        const found = this.source()
          .namespaces()
          .some(namespace => {
            if (namespace.id === databaseDef.namespace.id) {
              this.source().namespace(namespace);
              return true;
            }
          });
        if (!found) {
          return;
        }
      }
      if (
        this.source()
          .namespace()
          .database()
      ) {
        this.source()
          .namespace()
          .database()
          .table(null);
      }
      this.source()
        .namespace()
        .setDatabaseByName(databaseDef.name, () => {
          huePubSub.publish('metastore.url.change');
        });
    });

    huePubSub.subscribe('assist.table.selected', tableDef => {
      this.loadTableDef(tableDef, () => {
        huePubSub.publish('metastore.url.change');
      });
    });

    huePubSub.subscribe('metastore.url.change', () => {
      const prefix = '/hue/metastore/';
      if (this.source() && this.source().namespace()) {
        const params = {
          source_type: this.source().type
        };
        if (window.HAS_MULTI_CLUSTER) {
          params.namespace = this.source().namespace().id;
        }
        if (
          this.source()
            .namespace()
            .database() &&
          this.source()
            .namespace()
            .database()
            .table()
        ) {
          hueUtils.changeURL(
            prefix +
              'table/' +
              this.source()
                .namespace()
                .database()
                .table()
                .catalogEntry.path.join('/'),
            params
          );
        } else if (
          this.source()
            .namespace()
            .database()
        ) {
          hueUtils.changeURL(
            prefix +
              'tables/' +
              this.source()
                .namespace()
                .database().catalogEntry.name,
            params
          );
        } else {
          hueUtils.changeURL(prefix + 'databases', params);
        }
      }
    });

    window.onpopstate = () => {
      if (window.location.pathname.indexOf('/metastore') > -1) {
        this.loadUrl();
      }
    };

    this.databasesBreadcrumb = () => {
      if (
        this.source()
          .namespace()
          .database()
      ) {
        this.source()
          .namespace()
          .database()
          .table(null);
      }
      this.source()
        .namespace()
        .database(null);
      huePubSub.publish('metastore.url.change');
    };

    this.tablesBreadcrumb = () => {
      this.source()
        .namespace()
        .database()
        .table(null);
      huePubSub.publish('metastore.url.change');
    };

    this.scrollToColumn = col => {
      if (!col.table.samples.loading()) {
        $('.page-content').scrollTop(0);
        this.currentTab('sample');
        hueUtils.waitForRendered(
          '#sampleTable',
          el => el.parent().hasClass('dataTables_wrapper'),
          () => {
            const sampleTable = $('#sampleTable');
            const sampleCol = sampleTable.find('th').filter(function() {
              return $.trim($(this).text()).indexOf(col.catalogEntry.name) > -1;
            });
            sampleTable.find('.columnSelected').removeClass('columnSelected');
            sampleTable
              .find('tr td:nth-child(' + (sampleCol.index() + 1) + ')')
              .addClass('columnSelected');
            let scrollLeft = 0;
            sampleTable.find('th:lt(' + sampleCol.index() + ')').each(function() {
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

  loadTableDef(tableDef, callback) {
    if (this.source().type !== tableDef.sourceType) {
      const found = this.sources().some(source => {
        if (source.type === tableDef.sourceType) {
          this.source(source);
          return true;
        }
      });
      if (!found) {
        return;
      }
    }
    if (this.source().namespace().id !== tableDef.namespace.id) {
      const found = this.source()
        .namespaces()
        .some(namespace => {
          if (namespace.id === tableDef.namespace.id) {
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
      .setDatabaseByName(tableDef.database, () => {
        if (
          this.source()
            .namespace()
            .database()
        ) {
          if (
            this.source()
              .namespace()
              .database()
              .table() &&
            this.source()
              .namespace()
              .database()
              .table().catalogEntry.name === tableDef.name
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
              .filter(table => table.catalogEntry.name === tableDef.name);
            if (foundTables.length === 1) {
              this.source()
                .namespace()
                .database()
                .setTable(foundTables[0], callback);
            } else if (clearDbCacheOnMissing) {
              const dbEntry = this.source()
                .namespace()
                .database().catalogEntry;
              dbEntry
                .getChildren({ refreshCache: true, silenceErrors: true })
                .then(childEntries => {
                  if (childEntries.some(childEntry => childEntry.name === tableDef.name)) {
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
                        targetChild: tableDef.name
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
                });
            }
          };

          if (
            !this.source()
              .namespace()
              .database()
              .loaded()
          ) {
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
    const path = window.location.pathname.substr(4) || '/metastore/tables';
    const pathParts = path.split('/');
    if (pathParts[0] === '') {
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
      let sourceType;
      if (search) {
        search = search.replace('?', '');
        search.split('&').forEach(param => {
          if (param.indexOf('namespace=') === 0) {
            namespaceId = param.replace('namespace=', '');
          }
          if (param.indexOf('source_type=') === 0) {
            sourceType = param.replace('source_type=', '');
          }
        });
      }

      if (sourceType && sourceType !== this.source().type) {
        const found = this.sources().some(source => {
          if (source.type === sourceType) {
            this.source(source);
            return true;
          }
        });
        if (!found) {
          sourceAndNamespaceDeferred.reject();
          return;
        }
      }

      if (
        !namespaceId &&
        apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedNamespace')
      ) {
        namespaceId = apiHelper.getFromTotalStorage('contextSelector', 'lastSelectedNamespace').id;
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
          this.loadTableDef(
            {
              name: pathParts[2],
              database: pathParts[1],
              sourceType: this.source().type,
              namespace: namespace
            },
            () => {
              if (pathParts.length > 3 && pathParts[3] === 'partitions') {
                huePubSub.subscribe(
                  'metastore.loaded.partitions',
                  () => {
                    this.currentTab('partitions');
                  },
                  'metastore'
                );
              }
            }
          );
      }
    });
  }
}

export default MetastoreViewModel;
