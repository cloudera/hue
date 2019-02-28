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

import solrQueryParser from '../solrQueryParser';

describe('solrQueryParser.js', () => {
  const testAutocomplete = function(beforeCursor, afterCursor, expectedResult) {
    const result = solrQueryParser.autocompleteSolrQuery(beforeCursor, afterCursor, true);
    if (!expectedResult.locations) {
      delete result.locations;
    }
    expect(result).toEqual(expectedResult);
  };

  it('should suggest fields for "|"', () => {
    testAutocomplete('', '', {
      suggestFields: { appendColon: true }
    });
  });

  it('should suggest values for "field|"', () => {
    testAutocomplete('field', '', {
      suggestFields: { appendColon: true }
    });
  });

  it('should suggest AND or OR for "field |"', () => {
    testAutocomplete('field ', '', {
      suggestKeywords: ['AND', 'OR', ':'],
      suggestValues: { field: 'field', prependColon: true }
    });
  });

  it('should suggest values for "field:|"', () => {
    testAutocomplete('field:', '', {
      suggestValues: { field: 'field' }
    });
  });

  it('should suggest values for "field:someVal|"', () => {
    testAutocomplete('field:someVal', '', {
      suggestValues: { field: 'field' }
    });
  });

  it('should suggest values for "field:"some Val|"', () => {
    testAutocomplete('field:"some Val', '', {
      suggestValues: { field: 'field', quotePresent: true, partial: 'some ' }
    });
  });

  it('should suggest values for "field:"a|"', () => {
    testAutocomplete('field:"a', '', {
      suggestValues: { field: 'field', quotePresent: true, partial: '' }
    });
  });

  it('should suggest values for "field:"Cabernet |"', () => {
    testAutocomplete('field:"Cabernet ', '', {
      suggestValues: { field: 'field', quotePresent: true, partial: 'Cabernet ' }
    });
  });

  it('should suggest values for "field:"some Val| foo"', () => {
    testAutocomplete('field:"some Val', ' foo"', {
      suggestValues: { field: 'field', quotePresent: true, partial: 'some ' }
    });
  });

  it('should suggest AND or OR for "field:value |"', () => {
    testAutocomplete('field:value ', '', {
      suggestKeywords: ['AND', 'OR']
    });
  });

  it('should suggest fields for "field:value AND |"', () => {
    testAutocomplete('field:value AND ', '', {
      suggestFields: { appendColon: true }
    });
  });

  it('should suggest fields for "(field:value OR foo) AND |"', () => {
    testAutocomplete('(field:value OR foo) AND ', '', {
      suggestFields: { appendColon: true }
    });
  });

  it('should suggest fields for "| field"', () => {
    testAutocomplete('', ' field', {
      suggestFields: { appendColon: true }
    });
  });

  it('should suggest fields for "| && field"', () => {
    testAutocomplete('', ' && field', {
      suggestFields: { appendColon: true }
    });
  });

  it('should suggest values for "foo AND b|"', () => {
    testAutocomplete('foo AND b', '', {
      suggestFields: { appendColon: true }
    });
  });

  it('should suggest values for "f| OR boo"', () => {
    testAutocomplete('f', ' OR boo', {
      suggestFields: { appendColon: true }
    });
  });

  it('should suggest AND or OR for "foo | field:value "', () => {
    testAutocomplete('foo ', ' field:value', {
      suggestKeywords: ['AND', 'OR', ':'],
      suggestValues: { field: 'foo', prependColon: true }
    });
  });
});
