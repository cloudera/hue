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

import AceAutocompleteWrapper from '../aceAutocompleteWrapper';

describe('aceAutocompleteWrapper.js', () => {
  it('should not throw exceptions', done => {
    const subject = new AceAutocompleteWrapper({
      snippet: {
        isSqlDialect: function() {
          return true;
        },
        type: ko.observable('hive'),
        database: function() {
          return 'default';
        }
      }
    });

    try {
      subject.getCompletions(
        {
          getTextBeforeCursor: function() {
            return 'SELECT * FROM (SELECT * FROM tbl) a JOIN (SELECT * FROM tbl) b ON a.c=';
          },
          getTextAfterCursor: function() {
            return '';
          },
          hideSpinner: function() {
            expect(true).toBeTruthy(); // Prevent jasmine warning
            done();
          },
          showSpinner: function() {}
        },
        undefined,
        undefined,
        undefined,
        () => {
          expect(true).toBeTruthy(); // Prevent jasmine warning
          done();
        }
      );
    } catch (e) {
      expect(false).toBeTruthy('Got unexpected exception');
      done();
    }
  });
});
