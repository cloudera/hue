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
import * as storageUtilsMock from './storageUtils';

import HdfsAutocompleter from './hdfsAutocompleter';
describe('hdfsAutocompleter.js', () => {
  let subject;

  const ajaxHelper = {
    responseForUrls: {}
  };

  const snippet = {
    type: ko.observable(),
    database: ko.observable('database_one'),
    isSqlDialect: function () {
      return true;
    },
    getContext: function () {
      return ko.mapping.fromJS(null);
    }
  };

  beforeAll(() => {
    jest.spyOn(storageUtilsMock, 'getFromLocalStorage').mockImplementation(() => null);
    jest.spyOn(storageUtilsMock, 'setInLocalStorage').mockImplementation(() => null);

    jest.spyOn($, 'ajax').mockImplementation(options => {
      const firstUrlPart = options.url.split('?')[0];

      expect(ajaxHelper.responseForUrls[firstUrlPart]).toBeDefined();
      const response = ajaxHelper.responseForUrls[firstUrlPart];
      response.called = true;
      response.status = 0;
      options.success(response);
      return {
        fail: function () {
          return {
            always: $.noop
          };
        }
      };
    });
  });

  afterEach(() => {
    $.each(ajaxHelper.responseForUrls, (key, value) => {
      expect(value.called).toEqual(true, key + ' was never called');
    });
  });

  beforeEach(() => {
    subject = new HdfsAutocompleter({
      user: 'testUser',
      snippet: snippet
    });
    ajaxHelper.responseForUrls = {};
  });

  const createCallbackSpyForValues = function (values) {
    const spy = {
      cb: value => {
        expect(value).toEqualAutocompleteValues(values);
      }
    };
    return jest.spyOn(spy, 'cb');
  };

  const assertAutoComplete = function (testDefinition) {
    ajaxHelper.responseForUrls = testDefinition.serverResponses;
    const callback = createCallbackSpyForValues(testDefinition.expectedSuggestions);
    subject.autocomplete(testDefinition.beforeCursor, testDefinition.afterCursor, callback);

    expect(callback).toHaveBeenCalled();
  };

  it('should return empty suggestions for empty statement', () => {
    assertAutoComplete({
      serverResponses: {},
      beforeCursor: '',
      afterCursor: '',
      expectedSuggestions: []
    });
  });

  it('should return empty suggestions for bogus statements', () => {
    assertAutoComplete({
      serverResponses: {},
      beforeCursor: "qwerqwer'asdf/",
      afterCursor: '',
      expectedSuggestions: []
    });
  });

  it('should return empty suggestions for URIs with schemes ', () => {
    assertAutoComplete({
      serverResponses: {},
      beforeCursor: '://blabla',
      afterCursor: '',
      expectedSuggestions: []
    });
  });

  it("should return suggestions for root with '", async () => {
    await assertAutoComplete({
      serverResponses: {
        '/filebrowser/view=%2F': {
          files: [
            { name: '.', type: 'dir' },
            { name: '..', type: 'dir' },
            { name: 'var', type: 'dir' },
            { name: 'tmp_file', type: 'file' }
          ]
        }
      },
      beforeCursor: "'/",
      afterCursor: '',
      expectedSuggestions: ['tmp_file', 'var']
    });
  });

  it('should return suggestions for root with "', () => {
    assertAutoComplete({
      serverResponses: {
        '/filebrowser/view=%2F': {
          files: [
            { name: '.', type: 'dir' },
            { name: '..', type: 'dir' },
            { name: 'var', type: 'dir' },
            { name: 'tmp_file', type: 'file' }
          ]
        }
      },
      beforeCursor: '"/',
      afterCursor: '',
      expectedSuggestions: ['tmp_file', 'var']
    });
  });

  it('should return suggestions for non-root', () => {
    assertAutoComplete({
      serverResponses: {
        '/filebrowser/view=%2Ffoo/bar': {
          files: [
            { name: '.', type: 'dir' },
            { name: '..', type: 'dir' },
            { name: 'var', type: 'dir' },
            { name: 'tmp_file', type: 'file' }
          ]
        }
      },
      beforeCursor: "'/foo/bar/",
      afterCursor: '',
      expectedSuggestions: ['tmp_file', 'var']
    });
  });
});
