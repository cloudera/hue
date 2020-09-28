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

import { SqlFunctions } from './sqlFunctions';
import { matchesType } from 'sql/reference/typeUtils';

describe('sqlFunctions.js', () => {
  it('should suggest only BOOLEAN functions when return type is set to BOOLEAN for Hive', () => {
    const completions = [];
    SqlFunctions.suggestFunctions('hive', ['BOOLEAN'], undefined, undefined, completions);

    expect(completions.length).not.toEqual(0);

    const completionsWithCorrectType = completions.filter(completion => {
      return (
        completion.meta === 'BOOLEAN' ||
        completion.meta === 'T' ||
        completion.meta === 'ARRAY' ||
        completion.meta === 'MAP' ||
        completion.meta === 'STRUCT' ||
        completion.meta === 'UNION' ||
        completion.meta === 'table'
      );
    });

    expect(completionsWithCorrectType.length).toEqual(completions.length);
  });

  it('should suggest only STRING functions when return type is set to STRING for Hive', () => {
    const completions = [];
    SqlFunctions.suggestFunctions('hive', ['STRING'], undefined, undefined, completions);

    expect(completions.length).not.toEqual(0);

    const completionsWithCorrectType = completions.filter(completion =>
      matchesType('hive', ['STRING'], [completion.meta])
    );

    expect(completionsWithCorrectType.length).toEqual(completions.length);
  });

  it('should suggest only NUMBER functions when return type is set to NUMBER for Hive', () => {
    const completions = [];
    SqlFunctions.suggestFunctions('hive', ['NUMBER'], undefined, undefined, completions);

    expect(completions.length).not.toEqual(0);

    let atleastOneInt = false;
    let atleastOneString = false;
    const completionsWithCorrectType = completions.filter(completion => {
      atleastOneInt = atleastOneInt || completion.meta === 'INT';
      atleastOneString = atleastOneString || completion.meta === 'STRING';
      return matchesType('hive', ['NUMBER'], [completion.meta]);
    });

    expect(atleastOneInt).toBeTruthy();
    expect(atleastOneString).toBeTruthy();
    expect(completionsWithCorrectType.length).toEqual(completions.length);
  });

  it('should suggest only NUMBER functions when return type is set to NUMBER for Impala', () => {
    const completions = [];
    SqlFunctions.suggestFunctions('impala', ['NUMBER'], undefined, undefined, completions);

    expect(completions.length).not.toEqual(0);

    let atleastOneInt = false;
    let stringPresent = false;
    const completionsWithCorrectType = completions.filter(completion => {
      atleastOneInt = atleastOneInt || completion.meta === 'INT';
      stringPresent = stringPresent || completion.meta === 'STRING';
      return matchesType('hive', ['NUMBER'], [completion.meta]);
    });

    expect(atleastOneInt).toBeTruthy();
    expect(stringPresent).toBeFalsy();
    expect(completionsWithCorrectType.length).toEqual(completions.length);
  });

  it('should give the expected argument types at a specific position', () => {
    expect(SqlFunctions.getArgumentTypes('hive', 'cos', 1)).toEqual(['DECIMAL', 'DOUBLE']);
    expect(SqlFunctions.getArgumentTypes('hive', 'cos', 2)).toEqual([]);
    expect(SqlFunctions.getArgumentTypes('impala', 'cos', 1)).toEqual(['DOUBLE']);
    expect(SqlFunctions.getArgumentTypes('impala', 'cos', 2)).toEqual([]);

    expect(SqlFunctions.getArgumentTypes('hive', 'greatest', 1)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'greatest', 200)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'greatest', 1)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'greatest', 200)).toEqual(['T']);

    expect(SqlFunctions.getArgumentTypes('hive', 'strleft', 1)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'strleft', 2)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'strleft', 3)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'strleft', 200)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'strleft', 1)).toEqual(['STRING']);
    expect(SqlFunctions.getArgumentTypes('impala', 'strleft', 2)).toEqual(['INT']);
    expect(SqlFunctions.getArgumentTypes('impala', 'strleft', 3)).toEqual([]);
    expect(SqlFunctions.getArgumentTypes('impala', 'strleft', 200)).toEqual([]);

    expect(SqlFunctions.getArgumentTypes('hive', 'concat', 10)).toEqual(['BINARY', 'STRING']);
    expect(SqlFunctions.getArgumentTypes('impala', 'concat', 10)).toEqual(['STRING']);

    expect(SqlFunctions.getArgumentTypes('hive', 'substring_index', 1)).toEqual(['STRING']);
    expect(SqlFunctions.getArgumentTypes('hive', 'substring_index', 2)).toEqual(['STRING']);
    expect(SqlFunctions.getArgumentTypes('hive', 'substring_index', 3)).toEqual(['INT']);
    expect(SqlFunctions.getArgumentTypes('hive', 'substring_index', 200)).toEqual([]);
    expect(SqlFunctions.getArgumentTypes('impala', 'substring_index', 1)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'substring_index', 2)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'substring_index', 3)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'substring_index', 200)).toEqual(['T']);

    expect(SqlFunctions.getArgumentTypes('hive', 'weeks_add', 1)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'weeks_add', 2)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'weeks_add', 3)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'weeks_add', 200)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'weeks_add', 1)).toEqual(['TIMESTAMP']);
    expect(SqlFunctions.getArgumentTypes('impala', 'weeks_add', 2)).toEqual(['BIGINT', 'INT']);
    expect(SqlFunctions.getArgumentTypes('impala', 'weeks_add', 3)).toEqual([]);
    expect(SqlFunctions.getArgumentTypes('impala', 'weeks_add', 200)).toEqual([]);

    expect(SqlFunctions.getArgumentTypes('hive', 'reflect', 1)).toEqual(['STRING']);
    expect(SqlFunctions.getArgumentTypes('hive', 'reflect', 2)).toEqual(['STRING']);
    expect(SqlFunctions.getArgumentTypes('hive', 'reflect', 3)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'reflect', 200)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'reflect', 1)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'reflect', 200)).toEqual(['T']);

    expect(SqlFunctions.getArgumentTypes('hive', 'blabla', 2)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('hive', 'blabla', 200)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'blabla', 2)).toEqual(['T']);
    expect(SqlFunctions.getArgumentTypes('impala', 'blabla', 200)).toEqual(['T']);
  });
});
