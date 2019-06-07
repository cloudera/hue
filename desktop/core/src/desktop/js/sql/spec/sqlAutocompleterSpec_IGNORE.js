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

import dataCatalog from 'catalog/dataCatalog';
import SqlAutocompleter from '../sqlAutocompleter';

// TODO: Ignore until ace is in webpack

describe('sqlAutocomplete.js', () => {
  let subject;

  beforeEach(() => {
    dataCatalog.disableCache();
    window.AUTOCOMPLETE_TIMEOUT = 1;
    jasmine.Ajax.install();

    jasmine.Ajax.stubRequest(/.*\/notebook\/api\/autocomplete\/$/).andReturn({
      status: 200,
      statusText: 'HTTP/1.1 200 OK',
      contentType: 'application/json',
      responseText: '{"status": 0, "databases": ["default"]}'
    });

    jasmine.Ajax.stubRequest(/.*\/notebook\/api\/autocomplete\/[^/]+$/).andReturn({
      status: 200,
      statusText: 'HTTP/1.1 200 OK',
      contentType: 'application/json',
      responseText:
        '{"status": 0, "tables_meta": [' +
        '{"comment": "comment", "type": "Table", "name": "foo"}, ' +
        '{"comment": null, "type": "View", "name": "bar_view"}, ' +
        '{"comment": null, "type": "Table", "name": "bar"}]}'
    });

    jasmine.Ajax.stubRequest(/.*\/notebook\/api\/autocomplete\/[^/]+\/[^/]+$/).andReturn({
      status: 200,
      statusText: 'HTTP/1.1 200 OK',
      contentType: 'application/json',
      responseText:
        '{"status": 0, "support_updates": false, "hdfs_link": "/filebrowser/view=/user/hive/warehouse/customers", "extended_columns": [{"comment": "", "type": "int", "name": "id"}, {"comment": "", "type": "string", "name": "name"}, {"comment": "", "type": "struct<email_format:string,frequency:string,categories:struct<promos:boolean,surveys:boolean>>", "name": "email_preferences"}, {"comment": "", "type": "map<string,struct<street_1:string,street_2:string,city:string,state:string,zip_code:string>>", "name": "addresses"}, {"comment": "", "type": "array<struct<order_id:string,order_date:string,items:array<struct<product_id:int,sku:string,name:string,price:double,qty:int>>>>", "name": "orders"}], "columns": ["id", "name", "email_preferences", "addresses", "orders"], "partition_keys": []}'
    });
  });

  afterEach(() => {
    if (subject.suggestions.loading()) {
      for (let i = 0; i < jasmine.Ajax.requests.count(); i++) {
        console.log(jasmine.Ajax.requests.at(i));
      }
      fail('Still loading, missing ajax spec?');
    }
    AUTOCOMPLETE_TIMEOUT = 0;
    dataCatalog.enableCache();
    jasmine.Ajax.uninstall();
  });

  const createSubject = function(dialect, textBeforeCursor, textAfterCursor, positionStatement) {
    const editor = ace.edit();
    editor.setValue(textBeforeCursor);
    const actualCursorPosition = editor.getCursorPosition();
    editor.setValue(textBeforeCursor + textAfterCursor);
    editor.moveCursorToPosition(actualCursorPosition);

    return new SqlAutocompleter({
      snippet: {
        autocompleteSettings: {
          temporaryOnly: false
        },
        type: function() {
          return dialect;
        },
        database: function() {
          return 'default';
        },
        namespace: function() {
          return { id: 'defaultNamespace' };
        },
        compute: function() {
          return { id: 'defaultCompute' };
        },
        whenContextSet: function() {
          return $.Deferred().resolve();
        },
        positionStatement: ko.observable(positionStatement)
      },
      editor: function() {
        return {};
      }
    });
  };

  it('should create suggestions for Hive', () => {
    subject = createSubject('hive', '', '');
    expect(subject.suggestions.filtered().length).toBe(0);
    subject.autocomplete();
    expect(subject.suggestions.filtered().length).toBeGreaterThan(0);
  });

  it('should create suggestions for Impala', () => {
    subject = createSubject('impala', '', '');
    expect(subject.suggestions.filtered().length).toBe(0);
    subject.autocomplete();
    expect(subject.suggestions.filtered().length).toBeGreaterThan(0);
  });

  it('should fallback to the active query when there are surrounding errors', () => {
    subject = createSubject('hive', 'SELECT FROMzzz bla LIMIT 1; SELECT ', ' FROM bla', {
      location: { first_line: 1, last_line: 1, first_column: 27, last_column: 52 }
    });
    expect(subject.suggestions.filtered().length).toBe(0);
    subject.autocomplete();
    expect(subject.suggestions.filtered().length).toBeGreaterThan(0);
  });

  it("should only fallback to the active query when there are surrounding errors if there's an active query", () => {
    subject = createSubject('hive', 'SELECT FROMzzz bla LIMIT 1; SELECT ', ' FROM bla');
    expect(subject.suggestions.filtered().length).toBe(0);
    subject.autocomplete();
    expect(subject.suggestions.filtered().length).toBe(0);
  });

  it('should suggest columns from subqueries', () => {
    subject = createSubject(
      'hive',
      'SELECT ',
      ' FROM customers, (SELECT app FROM web_logs) AS subQ;'
    );
    expect(subject.suggestions.filtered().length).toBe(0);
    subject.autocomplete();
    expect(subject.suggestions.filtered().length).toBeGreaterThan(0);

    const appFound = subject.suggestions.filtered().some(suggestion => {
      return suggestion.category.id === 'column' && suggestion.value === 'app';
    });

    expect(appFound).toBeTruthy();
  });
});
