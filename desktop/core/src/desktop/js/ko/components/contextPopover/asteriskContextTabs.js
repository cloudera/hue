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

import dataCatalog from 'catalog/dataCatalog';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import sqlUtils from 'sql/sqlUtils';

class AsteriskData {
  constructor(data, connector, namespace, compute, defaultDatabase) {
    const self = this;
    self.loading = ko.observable(true);
    self.hasErrors = ko.observable(false);
    self.columns = [];

    self.selectedColumns = ko.pureComputed(
      () => (!self.loading() && self.columns.filter(column => column.selected())) || []
    );

    self.expand = function () {
      const colsToExpand =
        self.selectedColumns().length === 0 ? self.columns : self.selectedColumns();
      const colIndex = {};
      const colsTableMap = {};
      self.columns.forEach(col => {
        if (colsTableMap[col.name]) {
          colsTableMap[col.name].push(col.table);
        } else {
          colsTableMap[col.name] = [col.table];
        }
      });
      colsToExpand.forEach(col => {
        if (colIndex[col.name]) {
          colIndex[col.name]++;
        } else {
          colIndex[col.name] = 1;
        }
      });
      Object.keys(colIndex).forEach(name => {
        if (colIndex[name] === 1 && colsTableMap[name].length === 1) {
          delete colIndex[name];
        }
      });

      Promise.all(
        colsToExpand.map(async column => {
          if (column.tableAlias) {
            return (
              (await sqlUtils.backTickIfNeeded(connector, column.tableAlias)) +
              '.' +
              (await sqlUtils.backTickIfNeeded(connector, column.name))
            );
          }
          if (colIndex[column.name]) {
            return (
              (await sqlUtils.backTickIfNeeded(connector, column.table)) +
              '.' +
              (await sqlUtils.backTickIfNeeded(connector, column.name))
            );
          }
          return await sqlUtils.backTickIfNeeded(connector, column.name);
        })
      ).then(backtickedCols => {
        huePubSub.publish('ace.replace', {
          location: data.location,
          text: backtickedCols.join(', ')
        });
      });

      huePubSub.publish('context.popover.hide');
    };

    const deferrals = [];
    data.tables.forEach(table => {
      if (table.identifierChain) {
        const fetchDeferred = $.Deferred();
        deferrals.push(fetchDeferred);
        const path = $.map(table.identifierChain, identifier => {
          return identifier.name;
        });
        if (path.length === 1) {
          path.unshift(defaultDatabase);
        }
        dataCatalog
          .getEntry({
            namespace: namespace,
            compute: compute,
            connector: connector,
            path: path
          })
          .then(entry => {
            entry
              .getSourceMeta({ silenceErrors: true })
              .then(sourceMeta => {
                if (typeof sourceMeta.extended_columns !== 'undefined') {
                  const newColumns = [];
                  sourceMeta.extended_columns.forEach(column => {
                    const clonedColumn = $.extend({}, column);
                    clonedColumn.extendedType = clonedColumn.type
                      .replace(/</g, '&lt;')
                      .replace(/>/g, '&lt;');
                    if (clonedColumn.type.indexOf('<') !== -1) {
                      clonedColumn.type = clonedColumn.type.substring(
                        0,
                        clonedColumn.type.indexOf('<')
                      );
                    }
                    clonedColumn.selected = ko.observable(false);
                    clonedColumn.table =
                      table.identifierChain[table.identifierChain.length - 1].name;
                    if (table.alias) {
                      clonedColumn.tableAlias = table.alias;
                    }
                    newColumns.push(clonedColumn);
                  });
                  self.columns = self.columns.concat(newColumns);
                }
                fetchDeferred.resolve();
              })
              .catch(fetchDeferred.reject);
          })
          .catch(fetchDeferred.reject);
      }
    });

    if (deferrals.length === 0) {
      self.loading(false);
    }
    $.when.apply($, deferrals).done(
      () => {
        self.loading(false);
      },
      () => {
        if (self.columns.length === 0) {
          self.hasErrors(true);
        }
      }
    );
  }
}

class AsteriskContextTabs {
  constructor(data, connector, namespace, compute, defaultDatabase) {
    const self = this;
    self.data = new AsteriskData(data, connector, namespace, compute, defaultDatabase);

    self.tabs = [
      {
        id: 'details',
        label: I18n('Details'),
        template: 'context-popover-asterisk-details',
        templateData: self.data
      }
    ];
    self.activeTab = ko.observable('details');
  }
}

export default AsteriskContextTabs;
