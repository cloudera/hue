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
  describe('globalSearchParser.js', function () {

    var testParser = function (beforeCursor, afterCursor, expectedResult) {
      var result = globalSearchParser.parseGlobalSearch(beforeCursor, afterCursor, true);
      expect(result).toEqual(expectedResult);
    };

    it('should suggest facets for "|"', function () {
      testParser('', '', {
        suggestFacets: true,
        suggestResults: true,
        facets: {}
      });
    });

    it('should suggest facets for "TAGS: asdf |"', function () {
      testParser('TAGS: asdf ', '', {
        suggestFacets: true,
        suggestResults: true,
        facets: {
          'TAGS' : ['asdf']
        }
      });
    });

    it('should suggest facet values for "type:table tags:"', function() {
      testParser('type:table tags: ', '', {
        suggestFacetValues: 'tags',
        facets: {
          'type': ['table']
        }
      });
    });

    it('should give correct facet values for "type:table type:column"', function() {
      testParser('type:table type:column ', '', {
        suggestFacets: true,
        suggestResults: true,
        facets: {
          'type': ['table', 'column']
        }
      });
    });

    it('should suggest facet values for "tags: |"', function () {
      testParser('tags: ', '', {
        suggestFacetValues: 'tags',
        facets: {}
      });
    });
  });
})();