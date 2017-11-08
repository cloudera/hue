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
  fdescribe('solrQueryParser.js', function () {
    var testAutocomplete = function (beforeCursor, afterCursor, expectedResult) {
      var result = solrQueryParser.autocompleteSolrQuery(beforeCursor, afterCursor, true);
      if (!expectedResult.locations) {
        delete result.locations;
      }
      expect(result).toEqual(expectedResult);
    };


    it('should suggest fields for "|"', function () {
      testAutocomplete('', '', {
        suggestFields: {}
      });
    });

    it('should suggest values for "field|"', function () {
      testAutocomplete('field', '', {
        suggestFields: { startsWith: 'field' },
        suggestValues: { field: 'field', prependColon: true },
        suggestKeywords: [':']
      });
    });

    it('should suggest AND or OR for "field |"', function () {
      testAutocomplete('field ', '', {
        suggestKeywords: ['AND', 'OR', '&&', '||']
      });
    });

    it('should suggest values for "field:|"', function () {
      testAutocomplete('field:', '', {
        suggestValues: { field: 'field' }
      });
    });

    it('should suggest values for "field:someVal|"', function () {
      testAutocomplete('field:someVal', '', {
        suggestValues: { field: 'field', startsWith: 'someVal' }
      });
    });

    it('should suggest values for "field:"some Val|"', function () {
      testAutocomplete('field:"some Val', '', {
        suggestValues: { field: 'field', startsWith: 'some Val' }
      });
    });

    it('should suggest values for "field:"some Val| foo"', function () {
      testAutocomplete('field:"some Val', ' foo"', {
        suggestValues: { field: 'field', startsWith: 'some Val' }
      });
    });

    it('should suggest AND or OR for "field:value |"', function () {
      testAutocomplete('field:value ', '', {
        suggestKeywords: ['AND', 'OR', '&&', '||']
      });
    });

    it('should suggest fields for "field:value AND |"', function () {
      testAutocomplete('field:value AND ', '', {
        suggestFields: {}
      });
    });

    it('should suggest fields for "(field:value OR foo) AND |"', function () {
      testAutocomplete('(field:value OR foo) AND ', '', {
        suggestFields: {}
      });
    });

    it('should suggest fields for "| field"', function () {
      testAutocomplete('', ' field', {
        suggestFields: {}
      });
    });

    it('should suggest fields for "| && field"', function () {
      testAutocomplete('', ' && field', {
        suggestFields: {}
      });
    });

    it('should suggest values for "foo and b|"', function () {
      testAutocomplete('foo and b', '', {
        suggestFields: { startsWith: 'b' },
        suggestValues: { field: 'b', prependColon: true },
        suggestKeywords: [':']
      });
    });

    it('should suggest values for "f| or boo"', function () {
      testAutocomplete('f', ' or boo', {
        suggestFields: { startsWith: 'f' },
        suggestValues: { field: 'f', prependColon: true },
        suggestKeywords: [':']
      });
    });

    it('should suggest AND or OR for "foo | field:value "', function () {
      testAutocomplete('foo ', ' field:value', {
        suggestKeywords: ['AND', 'OR', '&&', '||']
      });
    });
  });
})();