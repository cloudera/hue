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
  describe('solrFormulaParser.js', function () {

    describe('autocomplete', function () {
      var testAutocomplete = function (beforeCursor, afterCursor, expectedResult) {
        var result = solrFormulaParser.autocompleteSolrFormula(beforeCursor, afterCursor, true);
        if (!expectedResult.locations) {
          delete result.locations;
        }
        expect(result).toEqual(expectedResult);
      };

      it('should suggest aggregate functions for "|"', function () {
        testAutocomplete('', '', {
          suggestAggregateFunctions: true
        });
      });

      it('should suggest functions and fields for "min(|"', function () {
        testAutocomplete('min(', '', {
          suggestAggregateFunctions: true,
          suggestFunctions: true,
          suggestFields: true,
          locations: [
            {type: 'function', name: 'min', location: {first_line: 1, last_line: 1, first_column: 1, last_column: 4}}
          ]
        });
      });

      it('should suggest functions and fields for "min(boo + |"', function () {
        testAutocomplete('min(boo + ', '', {
          suggestAggregateFunctions: true,
          suggestFunctions: true,
          suggestFields: true
        });
      });

      it('should suggest functions and fields for "min(boo + | + baa)"', function () {
        testAutocomplete('min(boo + ', ' + baa)', {
          suggestAggregateFunctions: true,
          suggestFunctions: true,
          suggestFields: true
        });
      });

      it('should suggest functions and fields for "min(1- max(|"', function () {
        testAutocomplete('min(1- max(', '', {
          suggestAggregateFunctions: true,
          suggestFunctions: true,
          suggestFields: true
        });
      });

      it('should suggest operators for "min(boo + 1) - 4 + mul(10, baa)|"', function () {
        testAutocomplete('min(boo + 1) - 4 + mul(10, baa)', '', {
          suggestOperators: true,
          locations: [
            {type: 'function', name: 'min', location: {first_line: 1, last_line: 1, first_column: 1, last_column: 4}},
            {type: 'field', name: 'boo', location: {first_line: 1, last_line: 1, first_column: 5, last_column: 8}},
            {type: 'function', name: 'mul', location: {first_line: 1, last_line: 1, first_column: 20, last_column: 23}},
            {type: 'field', name: 'baa', location: {first_line: 1, last_line: 1, first_column: 28, last_column: 31}}
          ]
        });
      });

      it('should suggest operators for "min(boo |"', function () {
        testAutocomplete('min(boo ', '', {
          suggestOperators: true
        });
      });
    });

    describe('parse', function () {
      var testParse = function (expression, expectedResult) {
        var result = solrFormulaParser.parseSolrFormula(expression);
        expect(result).toBeTruthy();
        expect(result).toEqual(expectedResult);
      };

      it('should parse "min(boo)"', function () {
        testParse('min(boo)', {
          parsedValue: 'min(boo)'
        });
      });

      it('should fail parsing "min(boo"', function () {
        var result = solrFormulaParser.parseSolrFormula('min(boo');
        expect(result).toBeFalsy();
      });

      it('should convert + to sum for "min(boo + 1)"', function () {
        testParse('min(boo + 1)', {
          parsedValue: 'min(sum(boo,1))'
        });
      });

      it('should convert - to sub for "10 - min(boo + 1)"', function () {
        testParse('10 - min(boo + 1)', {
          parsedValue: 'sub(10,min(sum(boo,1)))'
        });
      });

      it('should convert - to sub for "-min(boo)"', function () {
        testParse('-min(boo)', {
          parsedValue: 'sub(0,min(boo))'
        });
      });

      it('should convert / to div for "min(boo)/10"', function () {
        testParse('min(boo)/10', {
          parsedValue: 'div(min(boo),10)'
        });
      });

      it('should convert * to mul for "1*2*3*4"', function () {
        testParse('1*2*3*4', {
          parsedValue: 'mul(mul(mul(1,2),3),4)'
        });
      });

      it('should handle precedence properly  "1*2+3*4"', function () {
        testParse('1*2+3*4', {
          parsedValue: 'sum(mul(1,2),mul(3,4))'
        });
      });

      it('should handle precedence properly with parentheses "1*(2+3)*4"', function () {
        testParse('1*(2+3)*4', {
          parsedValue: 'mul(mul(1,(sum(2,3))),4)'
        });
      });
    })
  });
})();