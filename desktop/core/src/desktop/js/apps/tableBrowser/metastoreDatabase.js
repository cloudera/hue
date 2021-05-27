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

import huePubSub from 'utils/huePubSub';
import MetastoreTable from 'apps/tableBrowser/metastoreTable';
import { setInLocalStorage } from 'utils/storageUtils';

class MetastoreDatabase {
  /**
   * @param {object} options
   * @param {DataCatalogEntry} options.catalogEntry
   * @param {observable} options.sqlAnalyzerEnabled
   * @param {MetastoreViewModel} options.metastoreViewModel;
   * @constructor
   */
  constructor(options) {
    this.catalogEntry = options.catalogEntry;
    this.metastoreViewModel = options.metastoreViewModel;

    this.loaded = ko.observable(false);
    this.loadingTables = ko.observable(false);
    this.loadingAnalysis = ko.observable(false);
    this.loadingComment = ko.observable(false);
    this.loadingTableComments = ko.observable(false);
    this.loadingTablePopularity = ko.observable(false);

    this.tables = ko.observableArray();

    this.loading = ko.pureComputed(() => this.loadingTables() || this.loadingAnalysis());

    this.refreshing = ko.pureComputed(
      () =>
        this.loadingTables() ||
        this.loadingAnalysis() ||
        this.loadingComment() ||
        this.loadingTableComments() ||
        this.loadingTablePopularity()
    );

    this.comment = ko.observable();

    this.comment.subscribe(newValue => {
      this.catalogEntry.getComment().then(comment => {
        if (comment !== newValue) {
          this.catalogEntry
            .setComment(newValue)
            .then(this.comment)
            .catch(() => {
              this.comment(comment);
            });
        }
      });
    });

    this.stats = ko.observable();
    this.navigatorMeta = ko.observable();

    this.showAddTagName = ko.observable(false);
    this.addTagName = ko.observable('');

    this.selectedTables = ko.observableArray();

    this.editingTable = ko.observable(false);
    this.table = ko.observable(null);
  }

  onTableClick(catalogEntry) {
    this.tables().some(table => {
      if (table.catalogEntry === catalogEntry) {
        this.setTable(table, () => {
          huePubSub.publish('metastore.url.change');
        });
        return true;
      }
    });
  }

  reload() {
    if (this.loading()) {
      return;
    }
    // Clear will publish when done
    this.catalogEntry.clearCache().then(() => {
      this.load(
        () => {},
        this.metastoreViewModel.sqlAnalyzerEnabled(),
        this.metastoreViewModel.navigatorEnabled()
      );
    });
  }

  load(callback, sqlAnalyzerEnabled, navigatorEnabled) {
    if (navigatorEnabled) {
      this.loadingComment(true);
      this.catalogEntry
        .getNavigatorMeta()
        .then(this.navigatorMeta)
        .finally(() => {
          this.loadingComment(false);
        });
    }

    this.catalogEntry.getComment().then(this.comment);

    this.loadingTables(true);
    this.catalogEntry
      .getChildren()
      .then(tableEntries => {
        this.tables(
          tableEntries.map(
            tableEntry =>
              new MetastoreTable({
                database: this,
                catalogEntry: tableEntry,
                sqlAnalyzerEnabled,
                navigatorEnabled
              })
          )
        );
        if (navigatorEnabled) {
          this.loadingTableComments(true);
          this.catalogEntry
            .loadNavigatorMetaForChildren()
            .then(() => {
              this.tables().forEach(table => {
                table.navigatorMeta(table.catalogEntry.navigatorMeta);
              });
            })
            .finally(() => {
              this.loadingTableComments(false);
            });
        }
        if (sqlAnalyzerEnabled) {
          this.loadingTablePopularity(true);
          const sqlAnalyzer = sqlAnalyzerRepository.getSqlAnalyzer(
            this.catalogEntry.getConnector()
          );
          this.catalogEntry
            .loadSqlAnalyzerPopularityForChildren({ sqlAnalyzer })
            .then(() => {
              this.tables().forEach(table => {
                table.sqlAnalyzerStats(table.catalogEntry.sqlAnalyzerPopularity);
              });
            })
            .finally(() => {
              this.loadingTablePopularity(false);
            });
        }
        this.loaded(true);
      })
      .catch(() => {
        this.tables([]);
      })
      .finally(() => {
        this.loadingTables(false);
        if (callback) {
          callback();
        }
      });

    this.loadingAnalysis(true);
    this.catalogEntry
      .getAnalysis()
      .then(this.stats)
      .catch(() => {})
      .finally(() => {
        this.loadingAnalysis(false);
      });

    setInLocalStorage('metastore.last.selected.database', this.name);
  }

  setTableByName(tableName, callback) {
    if (this.table() && this.table().catalogEntry.name === tableName) {
      return;
    }

    this.tables().some(metastoreTable => {
      if (metastoreTable.catalogEntry.name === tableName) {
        this.setTable(metastoreTable, callback);
        return true;
      }
    });
  }

  setTable(metastoreTable, callback) {
    huePubSub.publish('metastore.scroll.to.top');
    this.table(metastoreTable);
    if (!metastoreTable.loaded()) {
      metastoreTable.load();
    }
    this.metastoreViewModel.currentTab('overview');
    if (callback) {
      callback();
    }
  }

  showContextPopover(entry, event, orientation) {
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
}

export default MetastoreDatabase;
