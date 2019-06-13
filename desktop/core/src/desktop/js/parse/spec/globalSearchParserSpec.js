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

import globalSearchParser from '../globalSearchParser';

describe('globalSearchParser.js', () => {
  const testParser = function(beforeCursor, afterCursor, expectedResult) {
    const result = globalSearchParser.parseGlobalSearch(beforeCursor, afterCursor, true);
    expect(result).toEqual(expectedResult);
  };

  it('should suggest facets for "|"', () => {
    testParser('', '', {
      suggestFacets: true,
      suggestResults: true,
      facets: {},
      text: []
    });
  });

  it('should suggest facets for "TAGS: asdf |"', () => {
    testParser('TAGS: asdf ', '', {
      suggestFacets: true,
      suggestResults: true,
      facets: {
        tags: { asdf: true }
      },
      text: []
    });
  });

  it('should suggest facet values for "type:table tags:"', () => {
    testParser('type:table tags: ', '', {
      suggestFacetValues: 'tags',
      facets: {
        type: { table: true }
      },
      text: []
    });
  });

  it('should suggest facet values for "type:table tags:a"', () => {
    testParser('type:table tags:a', '', {
      suggestFacetValues: 'tags',
      facets: {
        type: { table: true },
        tags: { a: true }
      },
      text: []
    });
  });

  it('should give correct facet values for "type:table type:column"', () => {
    testParser('type:table type:column ', '', {
      suggestFacets: true,
      suggestResults: true,
      facets: {
        type: { table: true, column: true }
      },
      text: []
    });
  });

  it('should give correct text values for "some text goes |here \'quoted value\'"', () => {
    testParser('some text goes ', "here 'quoted value'", {
      suggestFacets: true,
      suggestResults: true,
      facets: {},
      text: ['some', 'text', 'goes', 'here', 'quoted value']
    });
  });

  it("should give correct text and values for \"some boo:'asdfa adsf' text goes |here 'quoted value' foo:bar\"", () => {
    testParser("some boo:'asdfa adsf' text goes ", "here 'quoted value' foo:bar", {
      suggestFacets: true,
      suggestResults: true,
      facets: {
        boo: { 'asdfa adsf': true },
        foo: { bar: true }
      },
      text: ['some', 'text', 'goes', 'here', 'quoted value']
    });
  });

  it('should give correct text and values for "type:foo bar|"', () => {
    testParser('type:foo bar', '', {
      suggestFacets: true,
      suggestResults: true,
      facets: {
        type: { foo: true }
      },
      text: ['bar']
    });
  });

  it('should suggest facet values for "TAGS: |"', () => {
    testParser('TAGS: ', '', {
      suggestFacetValues: 'tags',
      facets: {},
      text: []
    });
  });
});
