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

import ko from 'knockout';

import { sleep, UUID } from 'utils/hueUtils';

const isNumericColumn = type =>
  ['tinyint', 'smallint', 'int', 'bigint', 'float', 'double', 'decimal', 'real'].indexOf(type) !==
  -1;

const isDateTimeColumn = type => ['timestamp', 'date', 'datetime'].indexOf(type) !== -1;

const isComplexColumn = type => ['array', 'map', 'struct'].indexOf(type) !== -1;

const isStringColumn = type =>
  !isNumericColumn(type) && !isDateTimeColumn(type) && !isComplexColumn(type);

class Result {
  constructor(result, snippet) {
    this.id = ko.observable(result.id || UUID());
    this.type = ko.observable(result.type || 'table');
    this.hasResultset = ko.observable(result.hasResultset !== false).extend('throttle', 100);
    this.handle = ko.observable(result.handle || {});
    this.meta = ko.observableArray(result.meta || []);
    this.snippet = snippet;

    this.rows = ko.observable(result.rows);
    this.hasMore = ko.observable(!!result.hasMore);
    this.statement_id = ko.observable(result.statement_id || 0);
    this.statement_range = ko.observable(
      result.statement_range || {
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
    this.statements_count = ko.observable(1);
    this.previous_statement_hash = ko.observable(result.previous_statement_hash);
    this.cleanedMeta = ko.pureComputed(() => this.meta().filter(item => item.name !== ''));

    this.fetchedOnce = ko.observable(!!result.fetchedOnce);
    this.startTime = ko.observable(result.startTime ? new Date(result.startTime) : new Date());
    this.endTime = ko.observable(result.endTime ? new Date(result.endTime) : new Date());
    this.executionTime = ko.pureComputed(
      () => this.endTime().getTime() - this.startTime().getTime()
    );

    this.cleanedNumericMeta = ko.pureComputed(() =>
      this.meta().filter(item => item.name !== '' && isNumericColumn(item.type))
    );
    this.cleanedStringMeta = ko.pureComputed(() =>
      this.meta().filter(item => item.name !== '' && isStringColumn(item.type))
    );
    this.cleanedDateTimeMeta = ko.pureComputed(() =>
      this.meta().filter(item => item.name !== '' && isDateTimeColumn(item.type))
    );

    this.data = ko.observableArray(result.data || []).extend({ rateLimit: 50 });
    this.explanation = ko.observable(result.explanation || '');
    this.images = ko.observableArray(result.images || []).extend({ rateLimit: 50 });
    this.logs = ko.observable('');
    this.logLines = 0;
    this.hasSomeResults = ko.pureComputed(() => this.hasResultset() && this.data().length > 0);
  }


  cancelBatchExecution() {
    this.statements_count(1);
    this.hasMore(false);
    this.statement_range({
      start: {
        row: 0,
        column: 0
      },
      end: {
        row: 0,
        column: 0
      }
    });
    this.handle()['statement_id'] = 0;
    this.handle()['start'] = {
      row: 0,
      column: 0
    };
    this.handle()['end'] = {
      row: 0,
      column: 0
    };
    this.handle()['has_more_statements'] = false;
    this.handle()['previous_statement_hash'] = '';
  }

  clear() {
    this.fetchedOnce(false);
    this.hasMore(false);
    this.statement_range({
      start: {
        row: 0,
        column: 0
      },
      end: {
        row: 0,
        column: 0
      }
    });
    this.meta.removeAll();
    this.data.removeAll();
    this.images.removeAll();
    this.logs('');
    this.handle({
      // Keep multiquery indexing
      has_more_statements: this.handle()['has_more_statements'],
      statement_id: this.handle()['statement_id'],
      statements_count: this.handle()['statements_count'],
      previous_statement_hash: this.handle()['previous_statement_hash']
    });
    this.startTime(new Date());
    this.endTime(new Date());
    this.explanation('');
    this.logLines = 0;
    this.rows(null);
  }

  getContext() {
    return {
      id: this.id,
      type: this.type,
      handle: this.handle
    };
  }

  /**
   *
   * @param {ExecutionResult} executionResult
   * @return {Promise<*>}
   */
  async update(executionResult) {
    this.executionResult = executionResult;
    this.handle(this.executionResult.executable.handle);

    await this.fetchMoreRows(100, false);

    await sleep(2000);

    const resultSize = await this.executionResult.fetchResultSize();

    if (resultSize && resultSize.rows) {
      this.rows(resultSize.rows);
    }
  }

  async fetchMoreRows(rowCount, startOver) {
    if (!this.executionResult) {
      return Promise.reject();
    }

    const resultResponse = await this.executionResult.fetchRows({
      rows: rowCount,
      startOver: !!startOver
    });

    const initialIndex = this.data().length;
    const tempData = [];

    resultResponse.data.forEach((row, index) => {
      row.unshift(initialIndex + index + 1);
      this.data.push(row);
      tempData.push(row);
    });

    if (this.rows() == null || (this.rows() + '').indexOf('+') !== -1) {
      this.rows(this.data().length + (resultResponse.has_more ? '+' : ''));
    }

    this.images(resultResponse.images || []);

    if (!this.fetchedOnce()) {
      resultResponse.meta.unshift({ type: 'INT_TYPE', name: '', comment: null });
      this.meta(resultResponse.meta);
      this.type(resultResponse.type);
      this.fetchedOnce(true);
    }

    this.meta().forEach(meta => {
      switch (meta.type) {
        case 'TINYINT_TYPE':
        case 'SMALLINT_TYPE':
        case 'INT_TYPE':
        case 'BIGINT_TYPE':
        case 'FLOAT_TYPE':
        case 'DOUBLE_TYPE':
        case 'DECIMAL_TYPE':
          meta.cssClass = 'sort-numeric';
          break;
        case 'TIMESTAMP_TYPE':
        case 'DATE_TYPE':
        case 'DATETIME_TYPE':
          meta.cssClass = 'sort-date';
          break;
        default:
          meta.cssClass = 'sort-string';
      }
    });

    this.hasMore(resultResponse.has_more);
  }
}

export default Result;
