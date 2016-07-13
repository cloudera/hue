// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// 'License'); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an 'AS IS' BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
define([
  'knockout',
  'desktop/js/autocomplete/sql',
  'desktop/spec/autocompleterTestUtils'
], function(ko, sql, testUtils) {

  describe('sql.js LOAD statements', function() {

    beforeAll(function () {
      sql.yy.parseError = function (msg) {
        throw Error(msg);
      };
      jasmine.addMatchers(testUtils.testDefinitionMatcher);
    });

    var assertAutoComplete = testUtils.assertAutocomplete;

    describe('Impala specific', function () {
      it('should suggest keywords for "|"', function() {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'impala',
          containsKeywords: ['LOAD'],
          expectedResult: {
            lowerCase: false
          }
        });
      });

      it('should suggest keywords for "LOAD |"', function () {
        assertAutoComplete({
          beforeCursor: 'LOAD ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['DATA']
          }
        });
      });

      it('should suggest keywords for "LOAD DATA |"', function () {
        assertAutoComplete({
          beforeCursor: 'LOAD DATA ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INPATH']
          }
        });
      });

      it('should suggest keywords for "LOAD DATA INPATH \'/some/path\' |"', function () {
        assertAutoComplete({
          beforeCursor: 'LOAD DATA INPATH \'/some/path\' ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['INTO']
          }
        });
      });

      it('should suggest keywords for "LOAD DATA INPATH \'some/path\' INTO |"', function () {
        assertAutoComplete({
          beforeCursor: 'LOAD DATA INPATH \'some/path\' INTO ',
          afterCursor: '',
          dialect: 'impala',
          expectedResult: {
            lowerCase: false,
            suggestKeywords: ['TABLE']
          }
        });
      });
    });

    describe('Hive specific', function () {
      it('should suggest keywords for "|"', function () {
        assertAutoComplete({
          beforeCursor: '',
          afterCursor: '',
          dialect: 'hive',
          containsKeywords: ['LOAD'],
          expectedResult: {
            lowerCase: false
          }
        });
      });
    });

    it('should suggest hdfs paths for "LOAD DATA INPATH \'|\'"', function () {
      assertAutoComplete({
        beforeCursor: 'LOAD DATA INPATH \'',
        afterCursor: '\'',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: ''}
        }
      });
    });

    it('should suggest hdfs paths for "LOAD DATA INPATH \'/|\'"', function () {
      assertAutoComplete({
        beforeCursor: 'LOAD DATA INPATH \'/',
        afterCursor: '\'',
        dialect: 'hive',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/'}
        }
      });
    });

    it('should suggest hdfs paths for "LOAD DATA INPATH \'/|"', function () {
      assertAutoComplete({
        beforeCursor: 'LOAD DATA INPATH \'/',
        afterCursor: '',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/'}
        }
      });
    });

    it('should suggest hdfs paths for "LOAD DATA INPATH \'/|/bar\' INTO TABLE foo"', function () {
      assertAutoComplete({
        serverResponses: {},
        beforeCursor: 'LOAD DATA INPATH \'/',
        afterCursor: '/bar\' INTO TABLE foo',
        dialect: 'impala',
        expectedResult: {
          lowerCase: false,
          suggestHdfs: { path: '/'}
        }
      });
    });
  });
});