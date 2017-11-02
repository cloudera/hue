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
  describe('solrExpressionParser.js', function () {

    var testParser = function (beforeCursor, afterCursor, expectedResult) {
      var result = solrExpressionParser.parseSolrExpression(beforeCursor, afterCursor, true);
      if (!expectedResult.locations) {
        delete result.locations;
      }
      expect(result).toEqual(expectedResult);
    };

    it('should suggest aggregate functions for "|"', function () {
      testParser('', '', {
        suggestAggregateFunctions: true
      });
    });

    it('should suggest functions and fields for "min(|"', function () {
      testParser('min(', '', {
        suggestFunctions: true,
        suggestFields: true,
        locations: [
          { type: 'function', name: 'min', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 4 }}
        ]
      });
    });

    it('should suggest functions and fields for "min(boo + |"', function () {
      testParser('min(boo + ', '', {
        suggestFunctions: true,
        suggestFields: true
      });
    });

    it('should suggest functions and fields for "min(boo + | + baa)"', function () {
      testParser('min(boo + ', ' + baa)', {
        suggestFunctions: true,
        suggestFields: true
      });
    });

    it('should suggest functions and fields for "min(1- max(|"', function () {
      testParser('min(1- max(', '', {
        suggestFunctions: true,
        suggestFields: true
      });
    });

    it('should suggest operators for "min(boo + 1) - 4 + mul(10, baa)|"', function () {
      testParser('min(boo + 1) - 4 + mul(10, baa)', '', {
        suggestOperators: true,
        locations: [
          { type: 'function', name: 'min', location: { first_line: 1, last_line: 1, first_column: 1, last_column: 4 } },
          { type: 'field', name: 'boo', location: { first_line: 1, last_line: 1, first_column: 5, last_column: 8 } },
          { type: 'function', name: 'mul', location: { first_line: 1, last_line: 1, first_column: 20, last_column: 23 } },
          { type: 'field', name: 'baa', location: { first_line: 1, last_line: 1, first_column: 28, last_column: 31 } }
        ]
      });
    });

    it('should suggest operators for "min(boo |"', function () {
      testParser('min(boo ', '', {
        suggestOperators: true
      });
    });
  });
})();