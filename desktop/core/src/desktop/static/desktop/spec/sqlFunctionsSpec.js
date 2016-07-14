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
define([
  'desktop/js/sqlFunctions'
], function (sqlFunctions) {
  describe('sqlFunctions.js', function () {
    it('should suggest only BOOLEAN functions when return type is set to BOOLEAN for Hive', function () {
      var completions = [];
      sqlFunctions.suggestFunctions('hive', ['BOOLEAN'], undefined, completions);

      expect(completions.length).not.toEqual(0);

      var completionsWithCorrectType = completions.filter(function (completion) {
        return completion.meta === 'BOOLEAN' || completion.meta === 'T';
      });

      expect(completionsWithCorrectType.length).toEqual(completions.length);
    });

    it('should suggest only STRING functions when return type is set to STRING for Hive', function () {
      var completions = [];
      sqlFunctions.suggestFunctions('hive', ['STRING'], undefined, completions);

      expect(completions.length).not.toEqual(0);

      var completionsWithCorrectType = completions.filter(function (completion) {
        return sqlFunctions.matchesType('hive', ['STRING'], [completion.meta]);
      });

      expect(completionsWithCorrectType.length).toEqual(completions.length);
    });

    it('should suggest only NUMBER functions when return type is set to NUMBER for Hive', function () {
      var completions = [];
      sqlFunctions.suggestFunctions('hive', ['NUMBER'], undefined, completions);

      expect(completions.length).not.toEqual(0);

      var atleastOneInt = false;
      var atleastOneString = false;
      var completionsWithCorrectType = completions.filter(function (completion) {
        atleastOneInt = atleastOneInt || completion.meta === 'INT';
        atleastOneString = atleastOneString || completion.meta === 'STRING';
        return sqlFunctions.matchesType('hive', ['NUMBER'], [completion.meta]);
      });

      expect(atleastOneInt).toBeTruthy();
      expect(atleastOneString).toBeTruthy();
      expect(completionsWithCorrectType.length).toEqual(completions.length);
    });

    it('should suggest only NUMBER functions when return type is set to NUMBER for Impala', function () {
      var completions = [];
      sqlFunctions.suggestFunctions('impala', ['NUMBER'], undefined, completions);

      expect(completions.length).not.toEqual(0);

      var atleastOneInt = false;
      var stringPresent = false;
      var completionsWithCorrectType = completions.filter(function (completion) {
        atleastOneInt = atleastOneInt || completion.meta === 'INT';
        stringPresent = stringPresent || completion.meta === 'STRING';
        return sqlFunctions.matchesType('hive', ['NUMBER'], [completion.meta]);
      });

      expect(atleastOneInt).toBeTruthy();
      expect(stringPresent).toBeFalsy();
      expect(completionsWithCorrectType.length).toEqual(completions.length);
    });

    it('should matchTypes for NUMBER', function () {
      expect(sqlFunctions.matchesType('hive', ['NUMBER'], ['INT'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['NUMBER'], ['BIGINT'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['NUMBER'], ['DOUBLE'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['NUMBER'], ['DECIMAL'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['NUMBER'], ['T'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['NUMBER'], ['STRING'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['INT'], ['NUMBER'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['BIGINT'], ['NUMBER'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['DOUBLE'], ['NUMBER'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['DECIMAL'], ['NUMBER'])).toBeTruthy();

      expect(sqlFunctions.matchesType('hive', ['STRING'], ['NUMBER'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['T'], ['NUMBER'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['NUMBER'], ['BOOLEAN'])).toBeFalsy();
      expect(sqlFunctions.matchesType('hive', ['BOOLEAN'], ['NUMBER'])).toBeFalsy();
    });

    it('should matchTypes for BIGINT', function () {
      expect(sqlFunctions.matchesType('hive', ['BIGINT'], ['BIGINT'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['BIGINT'], ['INT'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['BIGINT'], ['SMALLINT'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['BIGINT'], ['TINYINT'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['BIGINT'], ['T'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['BIGINT'], ['BOOLEAN'])).toBeFalsy();
      expect(sqlFunctions.matchesType('hive', ['BIGINT'], ['STRING'])).toBeFalsy();
      expect(sqlFunctions.matchesType('hive', ['INT'], ['BIGINT'])).toBeFalsy();
      expect(sqlFunctions.matchesType('hive', ['SMALLINT'], ['BIGINT'])).toBeFalsy();
      expect(sqlFunctions.matchesType('hive', ['TINYINT'], ['BIGINT'])).toBeFalsy();
      expect(sqlFunctions.matchesType('hive', ['DECIMAL'], ['BIGINT'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['T'], ['BIGINT'])).toBeTruthy();
      expect(sqlFunctions.matchesType('hive', ['BOOLEAN'], ['BIGINT'])).toBeFalsy();
      expect(sqlFunctions.matchesType('hive', ['STRING'], ['BIGINT'])).toBeTruthy();
    })
  });
});