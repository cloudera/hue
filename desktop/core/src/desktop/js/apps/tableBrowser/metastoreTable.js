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
import MetastoreColumn from 'apps/tableBrowser/metastoreColumn';
import MetastoreTableSamples from 'apps/tableBrowser/metastoreTableSamples';
import MetastoreTablePartitions from 'apps/tableBrowser/metastoreTablePartitions';
import I18n from 'utils/i18n';

let contextPopoverTimeout = -1;

class MetastoreTable {
  /**
   * @param {Object} options
   * @param {MetastoreDatabase} options.database
   * @param {DataCatalogEntry} options.catalogEntry
   * @param {observable} options.optimizerEnabled
   * @param {observable} options.navigatorEnabled
   * @constructor
   */
  constructor(options) {
    this.database = options.database;
    this.optimizerEnabled = options.optimizerEnabled;
    this.navigatorEnabled = options.navigatorEnabled;
    this.catalogEntry = options.catalogEntry;

    // TODO: Check if enough or if we need to fetch additional details
    this.isView = ko.observable(this.catalogEntry.isView());
    this.viewSql = ko.observable();

    this.optimizerStats = ko.observable();
    this.optimizerDetails = ko.observable();
    this.topJoins = ko.observableArray();
    this.navigatorMeta = ko.observable();
    this.relationshipsDetails = ko.observable();

    this.loaded = ko.observable(false);

    this.loadingDetails = ko.observable(false);
    this.loadingColumns = ko.observable(false);
    this.loadingQueries = ko.observable(false);
    this.loadingComment = ko.observable(false);
    this.loadingViewSql = ko.observable(false);
    this.loadingTopJoins = ko.observable(false);

    this.columns = ko.observableArray();

    this.samples = new MetastoreTableSamples({
      metastoreTable: this
    });

    this.partitions = new MetastoreTablePartitions({
      metastoreTable: this
    });

    this.loading = ko.pureComputed(() => this.loadingDetails() || this.loadingColumns());

    this.refreshing = ko.pureComputed(
      () =>
        this.loadingDetails() ||
        this.loadingColumns() ||
        this.loadingQueries() ||
        this.loadingComment() ||
        this.samples.loading() ||
        this.partitions.loading() ||
        this.loadingViewSql() ||
        this.loadingTopJoins()
    );

    this.partitionsCountLabel = ko.pureComputed(() => {
      if (this.partitions.values().length === window.METASTORE_PARTITION_LIMIT) {
        return this.partitions.values().length + '+';
      }
      return this.partitions.values().length;
    });
    this.tableDetails = ko.observable();
    this.tableStats = ko.observable();
    this.refreshingTableStats = ko.observable(false);
    this.showAddTagName = ko.observable(false);
    this.addTagName = ko.observable('');

    this.comment = ko.observable();
    this.editingComment = ko.observable();

    if (this.catalogEntry.hasResolvedComment()) {
      this.comment(this.catalogEntry.getResolvedComment());
    }

    this.commentWithoutNewLines = ko.pureComputed(() =>
      this.comment() ? hueUtils.deXSS(this.comment().replace(/[\n\r]+/gi, ' ')) : ''
    );

    this.comment.subscribe(newValue => {
      this.catalogEntry.getComment().done(comment => {
        if (comment !== newValue) {
          this.catalogEntry
            .setComment(newValue)
            .done(this.comment)
            .fail(() => {
              this.comment(comment);
            });
        }
      });
    });

    this.refreshTableStats = () => {
      if (this.refreshingTableStats()) {
        return;
      }
      this.refreshingTableStats(true);
      this.catalogEntry
        .getAnalysis({ refreshAnalysis: true, silenceErrors: true })
        .done(() => {
          this.fetchDetails();
        })
        .fail(data => {
          this.refreshingTableStats(false);
          $.jHueNotify.error(
            I18n('An error occurred refreshing the table stats. Please try again.')
          );
          console.error('apiHelper.refreshTableStats error');
          console.error(data);
        });
    };

    this.fetchFields = () => {
      this.loadingColumns(true);
      this.catalogEntry
        .getChildren()
        .done(columnEntries => {
          this.columns(
            columnEntries.map(
              columnEntry =>
                new MetastoreColumn({
                  catalogEntry: columnEntry,
                  table: this
                })
            )
          );

          this.catalogEntry
            .getOptimizerMeta()
            .done(optimizerMeta => {
              this.optimizerDetails(optimizerMeta);

              const topColIndex = {};
              optimizerMeta.topCols.forEach(topCol => {
                topColIndex[topCol.name] = topCol;
              });

              this.columns().forEach(column => {
                if (topColIndex[column.catalogEntry.name]) {
                  column.popularity(topColIndex[column.catalogEntry.name].score);
                }
              });
            })
            .always(() => {
              this.loadingQueries(false);
            });
        })
        .fail(() => {
          this.columns([]);
        })
        .always(() => {
          this.loadingColumns(false);
        });
    };

    this.fetchDetails = () => {
      this.loadingComment(true);
      this.database.catalogEntry
        .loadNavigatorMetaForChildren()
        .done(() => {
          this.catalogEntry.getComment().done(this.comment);
        })
        .always(() => {
          this.loadingComment(false);
        });

      if (this.catalogEntry.isView()) {
        this.loadingViewSql(true);
      }

      this.catalogEntry
        .getTopJoins({ silenceErrors: true })
        .done(topJoins => {
          if (topJoins && topJoins.values) {
            const joins = [];
            const ownQidLower = this.catalogEntry.path.join('.').toLowerCase();
            const ownNameLower = this.catalogEntry.name.toLowerCase();
            const ownDbNameLower = this.database.catalogEntry.name.toLowerCase();
            const joinIndex = {};
            const joinColsIndex = {};

            topJoins.values.forEach(topJoin => {
              if (topJoin.tables.length === 2) {
                topJoin.tables.forEach(table => {
                  const tableLower = table.toLowerCase();
                  if (tableLower !== ownQidLower && tableLower !== ownNameLower) {
                    const name =
                      tableLower.indexOf(ownDbNameLower + '.') === 0
                        ? table.substring(ownDbNameLower.length + 1)
                        : table;
                    if (!joinIndex[name]) {
                      joinIndex[name] = {
                        tableName: name,
                        tablePath: table.split('.'),
                        joinCols: [],
                        queryCount: 0
                      };
                    }
                    const join = joinIndex[name];
                    join.queryCount += topJoin.totalQueryCount;

                    topJoin.joinCols.forEach(joinCol => {
                      const cleanCols = {
                        queryCount: topJoin.totalQueryCount
                      };
                      if (joinCol.columns.length === 2) {
                        joinCol.columns.forEach(col => {
                          const colLower = col.toLowerCase();
                          if (colLower.indexOf(ownQidLower + '.') === 0) {
                            cleanCols.source = colLower.substring(ownDbNameLower.length + 1);
                            cleanCols.sourcePath = col.split('.');
                          } else if (colLower.indexOf(ownNameLower + '.') === 0) {
                            cleanCols.source = colLower;
                            cleanCols.sourcePath = col.split('.');
                            cleanCols.sourcePath.unshift(ownDbNameLower);
                          } else if (colLower.indexOf(ownDbNameLower + '.') === 0) {
                            cleanCols.target = colLower.substring(ownDbNameLower.length + 1);
                            cleanCols.targetPath = col.split('.');
                          } else {
                            cleanCols.target = col;
                            cleanCols.targetPath = col.split('.');
                          }
                        });
                      }
                      if (cleanCols.source && cleanCols.target) {
                        if (
                          joinColsIndex[
                            ownQidLower + join.tableName + cleanCols.source + cleanCols.target
                          ]
                        ) {
                          joinColsIndex[
                            ownQidLower + join.tableName + cleanCols.source + cleanCols.target
                          ].queryCount += topJoin.totalQueryCount;
                        } else {
                          joinColsIndex[
                            ownQidLower + join.tableName + cleanCols.source + cleanCols.target
                          ] = cleanCols;
                          join.joinCols.push(cleanCols);
                        }
                      }
                    });
                  }
                });
              }
            });

            Object.keys(joinIndex).forEach(key => {
              const join = joinIndex[key];
              if (join.joinCols.length) {
                join.joinCols.sort((a, b) => b.queryCount - a.queryCount);
                joins.push(join);
              }
            });
            joins.sort((a, b) => b.queryCount - a.queryCount);
            this.topJoins(joins);
          }
        })
        .always(() => {
          this.loadingTopJoins(false);
        });

      this.loadingDetails(true);
      this.catalogEntry
        .getAnalysis()
        .done(analysis => {
          this.tableDetails(analysis);
          this.tableStats(analysis.details.stats);
          this.loaded(true);
          if (analysis.partition_keys.length) {
            this.partitions.detailedKeys(analysis.partition_keys);
            this.partitions.load();
          } else {
            this.partitions.loading(false);
            this.partitions.loaded(true);
          }

          const found =
            analysis.properties &&
            analysis.properties.some(property => {
              if (property.col_name.toLowerCase() === 'view original text:') {
                apiHelper
                  .formatSql({ statements: property.data_type })
                  .done(formatResponse => {
                    this.viewSql(
                      formatResponse.status === 0
                        ? formatResponse.formatted_statements
                        : property.data_type
                    );
                  })
                  .fail(() => {
                    this.viewSql(property.data_type);
                  })
                  .always(() => {
                    this.loadingViewSql(false);
                  });
                return true;
              }
            });
          if (!found) {
            this.loadingViewSql(false);
          }
        })
        .fail(() => {
          this.partitions.loading(false);
          this.partitions.loaded(true);
          this.loadingViewSql(false);
        })
        .always(() => {
          this.refreshingTableStats(false);
          this.loadingDetails(false);
        });

      this.samples.load();
    };

    this.drop = () => {
      $.post('/tables/drop/' + this.database.catalogEntry.name, {
        table_selection: ko.mapping.toJSON([this.database.catalogEntry.name]),
        skip_trash: 'off',
        is_embeddable: true,
        cluster: JSON.stringify(this.database.catalogEntry.compute)
      }).done(resp => {
        if (resp.history_uuid) {
          huePubSub.publish('notebook.task.submitted', resp);
        } else {
          $(document).trigger('error', resp.message);
        }
      });
    };

    this.getRelationships = () => {
      $.post('/metadata/api/navigator/lineage', {
        id: this.navigatorMeta().identity
      })
        .done(data => {
          if (data && data.status === 0) {
            this.relationshipsDetails(ko.mapping.fromJS(data));
          } else {
            $(document).trigger('error', data.message);
          }
        })
        .fail(xhr => {
          $(document).trigger('info', xhr.responseText);
        });
    };
  }

  reload() {
    this.samples.loaded(false);
    this.partitions.loaded(false);
    // Clear will publish when done
    this.catalogEntry.clearCache();
  }

  showImportData() {
    $('#import-data-modal')
      .empty()
      .html(
        '<div class="modal-header"><button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span></button><h2 class="modal-title"></h2></div><div class="modal-body"><i class="fa fa-spinner fa-spin fa-2x muted"></i></div>'
      )
      .modal('show');
    $.get(
      '/metastore/table/' +
        this.catalogEntry.path.join('/') +
        '/load?source_type=' +
        this.catalogEntry.getConnector().id
    )
      .done(data => {
        $('#import-data-modal').html(data['data']);
      })
      .fail(xhr => {
        $(document).trigger('error', xhr.responseText);
      });
  }

  load() {
    this.fetchFields();
    this.fetchDetails();
    huePubSub.publish('metastore.loaded.table');
  }

  showContextPopover(entry, event, orientation) {
    window.clearTimeout(contextPopoverTimeout);
    const $source = $(event.currentTarget || event.target);
    const offset = $source.offset();
    huePubSub.publish('context.popover.show', {
      data: {
        type: 'catalogEntry',
        catalogEntry: entry.catalogEntry
      },
      orientation: orientation || 'right',
      source: {
        element: event.target,
        left: offset.left,
        top: offset.top - 2,
        right: offset.left + (orientation === 'left' ? 0 : $source.width() + 1),
        bottom: offset.top + $source.height() - 2
      }
    });
  }

  showContextPopoverDelayed(entry, event, orientation) {
    window.clearTimeout(contextPopoverTimeout);
    contextPopoverTimeout = window.setTimeout(() => {
      this.showContextPopover(entry, event, orientation);
    }, 500);
  }

  clearContextPopoverDelay() {
    window.clearInterval(contextPopoverTimeout);
  }
}

export default MetastoreTable;
