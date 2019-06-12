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

import hueUtils from 'utils/hueUtils';

class Result {
  constructor(snippet, result) {
    const self = this;

    $.extend(
      snippet,
      snippet.chartType == 'lines' && {
        // Retire line chart
        chartType: 'bars',
        chartTimelineType: 'line'
      }
    );
    self.id = ko.observable(
      typeof result.id != 'undefined' && result.id != null ? result.id : hueUtils.UUID()
    );
    self.type = ko.observable(
      typeof result.type != 'undefined' && result.type != null ? result.type : 'table'
    );
    self.hasResultset = ko
      .observable(
        typeof result.hasResultset != 'undefined' && result.hasResultset != null
          ? result.hasResultset
          : true
      )
      .extend('throttle', 100);
    self.handle = ko.observable(
      typeof result.handle != 'undefined' && result.handle != null ? result.handle : {}
    );
    self.meta = ko.observableArray(
      typeof result.meta != 'undefined' && result.meta != null ? result.meta : []
    );

    const adaptMeta = function() {
      let i = 0;
      self.meta().forEach(item => {
        if (typeof item.checked === 'undefined') {
          item.checked = ko.observable(true);
          item.checked.subscribe(() => {
            self.filteredMetaChecked(
              self.filteredMeta().some(item => {
                return item.checked();
              })
            );
          });
        }
        item.type = item.type.replace(/_type/i, '').toLowerCase();
        if (typeof item.originalIndex === 'undefined') {
          item.originalIndex = i;
        }
        i++;
      });
    };

    adaptMeta();
    self.meta.subscribe(adaptMeta);

    self.rows = ko.observable(
      typeof result.rows != 'undefined' && result.rows != null ? result.rows : null
    );
    self.hasMore = ko.observable(
      typeof result.hasMore != 'undefined' && result.hasMore != null ? result.hasMore : false
    );
    self.statement_id = ko.observable(
      typeof result.statement_id != 'undefined' && result.statement_id != null
        ? result.statement_id
        : 0
    );
    self.statement_range = ko.observable(
      typeof result.statement_range != 'undefined' && result.statement_range != null
        ? result.statement_range
        : {
            start: {
              row: 0,
              column: 0
            },
            end: {
              row: 0,
              column: 0
            }
          }
    );
    // We don't keep track of any previous selection so prevent entering into batch execution mode after load by setting
    // statements_count to 1. For the case when a selection is not starting at row 0.
    self.statements_count = ko.observable(1);
    self.previous_statement_hash = ko.observable(
      typeof result.previous_statement_hash != 'undefined' && result.previous_statement_hash != null
        ? result.previous_statement_hash
        : null
    );
    self.cleanedMeta = ko.computed(() => {
      return ko.utils.arrayFilter(self.meta(), item => {
        return item.name != '';
      });
    });
    self.metaFilter = ko.observable();

    self.isMetaFilterVisible = ko.observable(false);
    self.filteredMetaChecked = ko.observable(true);

    self.filteredColumnCount = ko.pureComputed(() => {
      if (!self.metaFilter() || self.metaFilter().query === '') {
        return self.meta().length - 1;
      }
      return self.filteredMeta().length;
    });

    self.filteredMeta = ko.pureComputed(() => {
      if (!self.metaFilter() || self.metaFilter().query === '') {
        return self.meta();
      }

      return self.meta().filter(item => {
        const facets = self.metaFilter().facets;
        const isFacetMatch = !facets || Object.keys(facets).length === 0 || !facets['type']; // So far only type facet is used for SQL
        const isTextMatch = !self.metaFilter().text || self.metaFilter().text.length === 0;
        let match = true;

        if (!isFacetMatch) {
          match = !!facets['type'][item.type];
        }

        if (match && !isTextMatch) {
          match = self.metaFilter().text.every(text => {
            return item.name.toLowerCase().indexOf(text.toLowerCase()) !== -1;
          });
        }
        return match;
      });
    });

    self.autocompleteFromEntries = function(nonPartial, partial) {
      const result = [];
      const partialLower = partial.toLowerCase();
      self.meta().forEach(column => {
        if (column.name.toLowerCase().indexOf(partialLower) === 0) {
          result.push(nonPartial + partial + column.name.substring(partial.length));
        } else if (column.name.toLowerCase().indexOf('.' + partialLower) !== -1) {
          result.push(
            nonPartial +
              partial +
              column.name.substring(
                partial.length + column.name.toLowerCase().indexOf('.' + partialLower) + 1
              )
          );
        }
      });

      return result;
    };
    self.clickFilteredMetaCheck = function() {
      self.filteredMeta().forEach(item => {
        item.checked(self.filteredMetaChecked());
      });
    };

    self.fetchedOnce = ko.observable(
      typeof result.fetchedOnce != 'undefined' && result.fetchedOnce != null
        ? result.fetchedOnce
        : false
    );
    self.startTime = ko.observable(
      typeof result.startTime != 'undefined' && result.startTime != null
        ? new Date(result.startTime)
        : new Date()
    );
    self.endTime = ko.observable(
      typeof result.endTime != 'undefined' && result.endTime != null
        ? new Date(result.endTime)
        : new Date()
    );
    self.executionTime = ko.computed(() => {
      return self.endTime().getTime() - self.startTime().getTime();
    });

    function isNumericColumn(type) {
      return (
        $.inArray(type, [
          'tinyint',
          'smallint',
          'int',
          'bigint',
          'float',
          'double',
          'decimal',
          'real'
        ]) > -1
      );
    }

    function isDateTimeColumn(type) {
      return $.inArray(type, ['timestamp', 'date', 'datetime']) > -1;
    }

    function isComplexColumn(type) {
      return $.inArray(type, ['array', 'map', 'struct']) > -1;
    }

    function isStringColumn(type) {
      return !isNumericColumn(type) && !isDateTimeColumn(type) && !isComplexColumn(type);
    }

    self.cleanedNumericMeta = ko.computed(() => {
      return ko.utils.arrayFilter(self.meta(), item => {
        return item.name != '' && isNumericColumn(item.type);
      });
    });

    self.cleanedStringMeta = ko.computed(() => {
      return ko.utils.arrayFilter(self.meta(), item => {
        return item.name != '' && isStringColumn(item.type);
      });
    });

    self.cleanedDateTimeMeta = ko.computed(() => {
      return ko.utils.arrayFilter(self.meta(), item => {
        return item.name != '' && isDateTimeColumn(item.type);
      });
    });

    self.data = ko.observableArray(
      typeof result.data != 'undefined' && result.data != null ? result.data : []
    );
    self.data.extend({ rateLimit: 50 });
    self.explanation = ko.observable(
      typeof result.explanation != 'undefined' && result.explanation != null
        ? result.explanation
        : ''
    );
    self.images = ko.observableArray(
      typeof result.images != 'undefined' && result.images != null ? result.images : []
    );
    self.images.extend({ rateLimit: 50 });
    self.logs = ko.observable('');
    self.logLines = 0;
    self.hasSomeResults = ko.computed(() => {
      return self.hasResultset() && self.data().length > 0; // status() == 'available'
    });

    self.getContext = function() {
      return {
        id: self.id,
        type: self.type,
        handle: self.handle
      };
    };

    self.clear = function() {
      self.fetchedOnce(false);
      self.hasMore(false);
      self.statement_range({
        start: {
          row: 0,
          column: 0
        },
        end: {
          row: 0,
          column: 0
        }
      });
      self.meta.removeAll();
      self.data.removeAll();
      self.images.removeAll();
      self.logs('');
      self.handle({
        // Keep multiquery indexing
        has_more_statements: self.handle()['has_more_statements'],
        statement_id: self.handle()['statement_id'],
        statements_count: self.handle()['statements_count'],
        previous_statement_hash: self.handle()['previous_statement_hash']
      });
      self.startTime(new Date());
      self.endTime(new Date());
      self.explanation('');
      self.logLines = 0;
      self.rows(null);
    };
  }

  cancelBatchExecution() {
    const self = this;
    self.statements_count(1);
    self.hasMore(false);
    self.statement_range({
      start: {
        row: 0,
        column: 0
      },
      end: {
        row: 0,
        column: 0
      }
    });
    self.handle()['statement_id'] = 0;
    self.handle()['start'] = {
      row: 0,
      column: 0
    };
    self.handle()['end'] = {
      row: 0,
      column: 0
    };
    self.handle()['has_more_statements'] = false;
    self.handle()['previous_statement_hash'] = '';
  }
}

export default Result;
