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
      sqlFunctions.suggestFunctions('hive', ['BOOLEAN'], undefined, undefined, completions);

      expect(completions.length).not.toEqual(0);

      var completionsWithCorrectType = completions.filter(function (completion) {
        return completion.meta === 'BOOLEAN' || completion.meta === 'T' || completion.meta === 'ARRAY' || completion.meta === 'MAP' || completion.meta === 'STRUCT';
      });

      expect(completionsWithCorrectType.length).toEqual(completions.length);
    });

    it('should suggest only STRING functions when return type is set to STRING for Hive', function () {
      var completions = [];
      sqlFunctions.suggestFunctions('hive', ['STRING'], undefined, undefined, completions);

      expect(completions.length).not.toEqual(0);

      var completionsWithCorrectType = completions.filter(function (completion) {
        return sqlFunctions.matchesType('hive', ['STRING'], [completion.meta]);
      });

      expect(completionsWithCorrectType.length).toEqual(completions.length);
    });

    it('should suggest only NUMBER functions when return type is set to NUMBER for Hive', function () {
      var completions = [];
      sqlFunctions.suggestFunctions('hive', ['NUMBER'], undefined, undefined, completions);

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
      sqlFunctions.suggestFunctions('impala', ['NUMBER'], undefined, undefined, completions);

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
    });

    it('should give the expected argument types at a specific position', function () {
      expect(sqlFunctions.getArgumentTypes('hive', 'cos', 1)).toEqual(['DECIMAL', 'DOUBLE']);
      expect(sqlFunctions.getArgumentTypes('hive', 'cos', 2)).toEqual([]);
      expect(sqlFunctions.getArgumentTypes('impala', 'cos', 1)).toEqual(['DOUBLE']);
      expect(sqlFunctions.getArgumentTypes('impala', 'cos', 2)).toEqual([]);

      expect(sqlFunctions.getArgumentTypes('hive', 'greatest', 1)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'greatest', 200)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'greatest', 1)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'greatest', 200)).toEqual(['T']);

      expect(sqlFunctions.getArgumentTypes('hive', 'strleft', 1)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'strleft', 2)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'strleft', 3)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'strleft', 200)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'strleft', 1)).toEqual(['STRING']);
      expect(sqlFunctions.getArgumentTypes('impala', 'strleft', 2)).toEqual(['INT']);
      expect(sqlFunctions.getArgumentTypes('impala', 'strleft', 3)).toEqual([]);
      expect(sqlFunctions.getArgumentTypes('impala', 'strleft', 200)).toEqual([]);

      expect(sqlFunctions.getArgumentTypes('hive', 'substring_index', 1)).toEqual(['STRING']);
      expect(sqlFunctions.getArgumentTypes('hive', 'substring_index', 2)).toEqual(['STRING']);
      expect(sqlFunctions.getArgumentTypes('hive', 'substring_index', 3)).toEqual(['INT']);
      expect(sqlFunctions.getArgumentTypes('hive', 'substring_index', 200)).toEqual([]);
      expect(sqlFunctions.getArgumentTypes('impala', 'substring_index', 1)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'substring_index', 2)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'substring_index', 3)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'substring_index', 200)).toEqual(['T']);

      expect(sqlFunctions.getArgumentTypes('hive', 'weeks_add', 1)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'weeks_add', 2)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'weeks_add', 3)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'weeks_add', 200)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'weeks_add', 1)).toEqual(['TIMESTAMP']);
      expect(sqlFunctions.getArgumentTypes('impala', 'weeks_add', 2)).toEqual(['BIGINT', 'INT']);
      expect(sqlFunctions.getArgumentTypes('impala', 'weeks_add', 3)).toEqual([]);
      expect(sqlFunctions.getArgumentTypes('impala', 'weeks_add', 200)).toEqual([]);

      expect(sqlFunctions.getArgumentTypes('hive', 'reflect', 1)).toEqual(['STRING']);
      expect(sqlFunctions.getArgumentTypes('hive', 'reflect', 2)).toEqual(['STRING']);
      expect(sqlFunctions.getArgumentTypes('hive', 'reflect', 3)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'reflect', 200)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'reflect', 1)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'reflect', 200)).toEqual(['T']);

      expect(sqlFunctions.getArgumentTypes('hive', 'blabla', 2)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('hive', 'blabla', 200)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'blabla', 2)).toEqual(['T']);
      expect(sqlFunctions.getArgumentTypes('impala', 'blabla', 200)).toEqual(['T']);
    });
  });
});