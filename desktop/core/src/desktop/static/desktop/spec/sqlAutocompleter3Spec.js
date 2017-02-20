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
(function () {
  describe('sqlAutocompleter3.js', function () {

    describe('AutocompleteResults', function () {
      var subject = new AutocompleteResults({
        snippet: {
          type: function () {
            return 'hive';
          },
          database: function () {
            'default'
          }
        }
      });

      it('should handle parse results with keywords', function () {
        subject.entries([]);
        expect(subject.filtered().length).toBe(0);
        subject.update({
          lowerCase: true,
          suggestKeywords: [{ value: 'BAR', weight: 1 }, { value: 'FOO', weight: 2 }]
        });
        expect(subject.filtered().length).toBe(2);
        console.log(subject.filtered());
        // Sorted by weight, case adjusted
        expect(subject.filtered()[0].meta).toBe(AutocompleterGlobals.i18n.meta.keyword);
        expect(subject.filtered()[0].value).toBe('foo');
        expect(subject.filtered()[1].meta).toBe(AutocompleterGlobals.i18n.meta.keyword);
        expect(subject.filtered()[1].value).toBe('bar');
      });

      it('should handle parse results with identifiers', function () {
        subject.entries([]);
        expect(subject.filtered().length).toBe(0);
        subject.update({
          lowerCase: false,
          suggestIdentifiers: [{ name: 'foo', type: 'alias' }, { name: 'bar', type: 'table' }]
        });
        expect(subject.filtered().length).toBe(2);
        console.log(subject.filtered());
        // Sorted by name, no case adjust
        expect(subject.filtered()[0].meta).toBe('table');
        expect(subject.filtered()[0].value).toBe('bar');
        expect(subject.filtered()[1].meta).toBe('alias');
        expect(subject.filtered()[1].value).toBe('foo');
      });

      it('should handle parse results with functions', function () {
        subject.entries([]);
        expect(subject.filtered().length).toBe(0);
        subject.update({
          lowerCase: false,
          suggestFunctions: {}
        });
        expect(subject.filtered().length).toBeGreaterThan(0);
        expect(subject.filtered()[0].details.arguments).toBeDefined();
        expect(subject.filtered()[0].details.signature).toBeDefined();
        expect(subject.filtered()[0].details.description).toBeDefined();
      });
    });

    describe('SqlAutocomplete3', function () {

      var createSubject = function (dialect, textBeforeCursor, textAfterCursor) {
        return new SqlAutocompleter3({
          snippet: {
            type: function () {
              return dialect;
            },
            database: function () {
              'default'
            }
          },
          editor: function() {
            return {
              getTextBeforeCursor: function () {
                return textBeforeCursor;
              },
              getTextAfterCursor: function () {
                return textAfterCursor;
              }
            }
          }
        })
      };

      it('should create suggestions for Hive', function () {
        var subject = createSubject('hive', '', '');
        expect(subject.suggestions.filtered().length).toBe(0);
        subject.autocomplete();
        expect(subject.suggestions.filtered().length).toBeGreaterThan(0);
      });

      it('should create suggestions for Impala', function () {
        var subject = createSubject('impala', '', '');
        expect(subject.suggestions.filtered().length).toBe(0);
        subject.autocomplete();
        expect(subject.suggestions.filtered().length).toBeGreaterThan(0);
      });
    });
  });
})();